#!/bin/bash

import io
import os
import re
import hmac
import json
import stat
import shutil
import hashlib
import inspect
import tempfile
from io import open

def get_importing_script_path():
    """Best-effort path of the importing (caller) script, or None."""
    for frame_info in inspect.stack():
        filename = frame_info.filename
        if filename != __file__:  # Ignore current module's file
            return os.path.abspath(filename)
    return None

def add_format(reg, key, magic, ext, name=None, ver="001",
               new_style=True, use_advanced_list=True, use_alt_inode=False, delim="\x00"):
    if key in reg:
        return
    magic_bytes = magic.encode("utf-8")
    reg[key] = {
        "format_name": name or key,
        "format_magic": magic,
        "format_len": len(magic_bytes),
        "format_hex": magic_bytes.hex(),
        "format_delimiter": delim,
        "format_ver": ver,
        "new_style": new_style,
        "use_advanced_list": use_advanced_list,
        "use_alt_inode": use_alt_inode,
        "format_extension": ext,
    }

__file_format_multi_dict__ = {}
__file_format_default__ = "ArchiveFile"
__include_defaults__ = True
__use_inmem__ = True
__use_memfd__ = True
__use_spoolfile__ = False
__use_spooldir__ = tempfile.gettempdir()
__use_new_style__ = True
__use_advanced_list__ = True
__use_alt_inode__ = False
BYTES_PER_KiB = 1024
BYTES_PER_MiB = 1024 * BYTES_PER_KiB
# Spool: not tiny, but won’t blow up RAM if many are in use
DEFAULT_SPOOL_MAX = 4 * BYTES_PER_MiB      # 4 MiB per spooled temp file
__spoolfile_size__ = DEFAULT_SPOOL_MAX
# Buffer: bigger than stdlib default (16 KiB), but still modest
DEFAULT_BUFFER_MAX = 256 * BYTES_PER_KiB   # 256 KiB copy buffer
__filebuff_size__ = DEFAULT_BUFFER_MAX
__program_name__ = "Py"+__file_format_default__
__use_env_file__ = True
__use_ini_file__ = True
__use_ini_name__ = "archivefile.ini"
__use_json_file__ = False
__use_json_name__ = "archivefile.json"
if(__use_ini_file__ and __use_json_file__):
    __use_json_file__ = False
if('PYARCHIVEFILE_CONFIG_FILE' in os.environ and os.path.exists(os.environ['PYARCHIVEFILE_CONFIG_FILE']) and __use_env_file__):
    scriptconf = os.environ['PYARCHIVEFILE_CONFIG_FILE']
else:
    prescriptpath = get_importing_script_path()
    if(prescriptpath is not None):
        if(__use_ini_file__ and not __use_json_file__):
            scriptconf = os.path.join(os.path.dirname(prescriptpath), __use_ini_name__)
        elif(__use_json_file__ and not __use_ini_file__):
            scriptconf = os.path.join(os.path.dirname(prescriptpath), __use_json_name__)
        else:
            scriptconf = ""
            prescriptpath = None
    else:
        scriptconf = ""
if os.path.exists(scriptconf):
    __config_file__ = scriptconf
elif(__use_ini_file__ and not __use_json_file__):
    __config_file__ = os.path.join(os.path.dirname(os.path.realpath(__file__)), __use_ini_name__)
elif(not __use_ini_file__ and __use_json_file__):
    __config_file__ = os.path.join(os.path.dirname(os.path.realpath(__file__)), __use_json_name__)
else:
    __config_file__ = os.path.join(os.path.dirname(os.path.realpath(__file__)), __use_ini_name__)
if __use_ini_file__ and os.path.exists(__config_file__):
    config = configparser.ConfigParser()
    config.read(__config_file__)
    def decode_unicode_escape(value):
        """Decode INI/JSON escape sequences (Py3)."""
        if value is None:
            return ""
        if isinstance(value, (bytes, bytearray, memoryview)):
            value = bytes(value).decode('utf-8', 'replace')
        if not isinstance(value, str):
            value = str(value)
        return value.encode('utf-8').decode('unicode_escape')

    __file_format_default__ = decode_unicode_escape(config.get('config', 'default'))
    __program_name__ = decode_unicode_escape(config.get('config', 'proname'))
    __include_defaults__ = config.getboolean('config', 'includedef')
    __use_inmem__ = config.getboolean('config', 'useinmem')
    __use_memfd__ = config.getboolean('config', 'usememfd')
    __use_spoolfile__ = config.getboolean('config', 'usespoolfile')
    __spoolfile_size__ = config.getint('config', 'spoolfilesize')
    __use_new_style__ = config.getboolean('config', 'newstyle')
    __use_advanced_list__ = config.getboolean('config', 'advancedlist')
    __use_alt_inode__ = config.getboolean('config', 'altinode')
    # Loop through all sections
    for section in config.sections():
        if section == "config":
            continue

        required_keys = [
            "len", "hex", "ver", "name",
            "magic", "delimiter", "extension"
        ]

        # Py2+Py3 compatible key presence check
        has_all_required = all(config.has_option(section, key) for key in required_keys)
        if not has_all_required:
            continue

        delim = decode_unicode_escape(config.get(section, 'delimiter'))
        if (not is_only_nonprintable(delim)):
            delim = "\x00" * len("\x00")

        __file_format_multi_dict__.update({
            decode_unicode_escape(config.get(section, 'magic')): {
                'format_name':        decode_unicode_escape(config.get(section, 'name')),
                'format_magic':       decode_unicode_escape(config.get(section, 'magic')),
                'format_len':         config.getint(section, 'len'),
                'format_hex':         config.get(section, 'hex'),
                'format_delimiter':   delim,
                'format_ver':         config.get(section, 'ver'),
                'format_extension':   decode_unicode_escape(config.get(section, 'extension')),
            }
        })
        if not __file_format_multi_dict__ and not __include_defaults__:
            __include_defaults__ = True
elif __use_json_file__ and os.path.exists(__config_file__):
    # Prefer ujson/simplejson if available (you already have this import block above)
    with open(__config_file__, 'rb') as f:
        raw = f.read()

    # Ensure we get a text string for json.loads (Py3-only)
    text = raw.decode('utf-8', 'replace')
    cfg = json.loads(text)

    # --- helpers: coerce + decode like your INI path ---
    def decode_unicode_escape(value):
        """Decode INI/JSON escape sequences (Py3)."""
        if value is None:
            return ""
        if isinstance(value, (bytes, bytearray, memoryview)):
            value = bytes(value).decode('utf-8', 'replace')
        if not isinstance(value, str):
            value = str(value)
        return value.encode('utf-8').decode('unicode_escape')

    def _to_bool(v):
        # handle true/false, 1/0, and "true"/"false"/"1"/"0"
        if isinstance(v, bool):
            return v
        if isinstance(v, (int, float)):
            return bool(v)
        if isinstance(v, (str,)):
            lv = v.strip().lower()
            if lv in ('true', 'yes', '1'):
                return True
            if lv in ('false', 'no', '0'):
                return False
        return bool(v)

    def _to_int(v, default=0):
        try:
            return int(v)
        except Exception:
            return default

    def _get(section_dict, key, default=None):
        return section_dict.get(key, default)

    # --- read global config (like INI's [config]) ---
    cfg_config = cfg.get('config', {}) or {}
    __file_format_default__ = decode_unicode_escape(_get(cfg_config, 'default', ''))
    __program_name__        = decode_unicode_escape(_get(cfg_config, 'proname', ''))
    __include_defaults__    = _to_bool(_get(cfg_config, 'includedef', True))
    __use_inmem__       = _to_bool(_get(cfg_config, 'useinmem', True))
    __use_memfd__       = _to_bool(_get(cfg_config, 'usememfd', True))
    __use_spoolfile__       = _to_bool(_get(cfg_config, 'usespoolfile', False))
    __spoolfile_size__       = _to_int(_get(cfg_config, 'spoolfilesize', DEFAULT_SPOOL_MAX))
    __use_new_style__       = _to_bool(_get(cfg_config, 'usespoolfile', True))
    __use_advanced_list__       = _to_bool(_get(cfg_config, 'usespoolfile', True))
    __use_alt_inode__       = _to_bool(_get(cfg_config, 'usespoolfile', False))

    # --- iterate format sections (everything except "config") ---
    required_keys = [
        "len", "hex", "ver", "name",
        "magic", "delimiter", "extension"
    ]

    for section_name, section in cfg.items():
        if section_name == 'config' or not isinstance(section, dict):
            continue

        # check required keys present
        if not all(k in section for k in required_keys):
            continue

        # pull + coerce values
        magic      = decode_unicode_escape(_get(section, 'magic', ''))
        name       = decode_unicode_escape(_get(section, 'name', ''))
        fmt_len    = _to_int(_get(section, 'len', 0))
        fmt_hex    = decode_unicode_escape(_get(section, 'hex', ''))
        fmt_ver    = decode_unicode_escape(_get(section, 'ver', ''))
        delim      = decode_unicode_escape(_get(section, 'delimiter', ''))
        extension  = decode_unicode_escape(_get(section, 'extension', ''))

        # keep your delimiter validation semantics
        if not is_only_nonprintable(delim):
            delim = "\x00" * len("\x00")  # same as your INI branch

        __file_format_multi_dict__.update({
            magic: {
                'format_name':        name,
                'format_magic':       magic,
                'format_len':         fmt_len,
                'format_hex':         fmt_hex,
                'format_delimiter':   delim,
                'format_ver':         fmt_ver,
                'format_extension':   extension,
            }
        })

    # mirror your INI logic
    if not __file_format_multi_dict__ and not __include_defaults__:
        __include_defaults__ = True
elif __use_ini_file__ and not os.path.exists(__config_file__):
    __use_ini_file__ = False
    __use_json_file__ = False
    __include_defaults__ = True
elif __use_json_file__ and not os.path.exists(__config_file__):
    __use_json_file__ = False
    __use_ini_file__ = False
    __include_defaults__ = True
if not __use_ini_file__ and not __include_defaults__:
    __include_defaults__ = True
if __include_defaults__:
    # Arc / Neo
    add_format(__file_format_multi_dict__, "ArchiveFile", "ArchiveFile", ".arc", "ArchiveFile")
    add_format(__file_format_multi_dict__, "NeoFile",     "NeoFile",     ".neo", "NeoFile")

# Pick a default if current default key is not present
if __file_format_default__ not in __file_format_multi_dict__:
    __file_format_default__ = next(iter(__file_format_multi_dict__))
__file_format_name__ = __file_format_multi_dict__[__file_format_default__]['format_name']
__file_format_magic__ = __file_format_multi_dict__[__file_format_default__]['format_magic']
__file_format_len__ = __file_format_multi_dict__[__file_format_default__]['format_len']
__file_format_hex__ = __file_format_multi_dict__[__file_format_default__]['format_hex']
__file_format_delimiter__ = __file_format_multi_dict__[__file_format_default__]['format_delimiter']
__file_format_ver__ = __file_format_multi_dict__[__file_format_default__]['format_ver']
__file_format_extension__ = __file_format_multi_dict__[__file_format_default__]['format_extension']
__file_format_dict__ = __file_format_multi_dict__[__file_format_default__]

hashlib_guaranteed = False

def CheckSumSupport(checkfor, guaranteed=True):
    if(guaranteed):
        try:
            hash_list = sorted(list(hashlib.algorithms_guaranteed))
        except AttributeError:
            try:
                hash_list = sorted(list(hashlib.algorithms))
            except AttributeError:
                hash_list = sorted(list(a.lower() for a in hashlib.algorithms_available))
    else:
        try:
            hash_list = sorted(list(hashlib.algorithms_available))
        except AttributeError:
            try:
                hash_list = sorted(list(hashlib.algorithms))
            except AttributeError:
                hash_list = sorted(list(a.lower() for a in hashlib.algorithms_available))
    checklistout = hash_list
    if(checkfor in checklistout):
        return True
    else:
        return False

def GetHeaderChecksum(inlist=None, checksumtype="md5", formatspecs=None, saltkey=None):
    """
    Serialize header fields (list/tuple => joined with delimiter + trailing delimiter;
    or a single field) and compute the requested checksum. Returns lowercase hex.
    """
    algo_key = (checksumtype or "md5").lower()

    delim = formatspecs.get('format_delimiter', "\x00")
    hdr_bytes = AppendNullBytes(inlist, delim).encode("UTF-8")
    if not isinstance(hdr_bytes, (bytes, )):
        hdr_bytes = hdr_bytes.encode("UTF-8")
    saltkeyval = None
    if(hasattr(saltkey, "read")):
        saltkeyval = skfp.read()
        if(not isinstance(saltkeyval, bytes)):
            saltkeyval = saltkeyval.encode("UTF-8")
    elif(isinstance(saltkey, bytes)):
        saltkeyval = saltkey
    elif(saltkey is not None and os.path.exists(saltkey)):
        with open(saltkey, "rb") as skfp:
            saltkeyval = skfp.read()
    else:
        saltkey = None
    if(saltkeyval is None):
        saltkey = None
    if CheckSumSupport(algo_key, hashlib_guaranteed):
        if(saltkey is None or saltkeyval is None):
            h = hashlib.new(algo_key, hdr_bytes)
        else:
            h = hmac.new(saltkeyval, hdr_bytes, digestmod=algo_key)
        return h.hexdigest().lower()

    return "0"

def GetFileChecksum(inbytes, checksumtype="md5", formatspecs=None, saltkey=None):
    """
    Accepts bytes/str/file-like.
      - Hashlib algos: streamed in 1 MiB chunks.
      - CRC algos (crc16_ansi/ccitt/x25/kermit, crc64_iso/ecma): streamed via CRCContext for file-like.
      - Falls back to one-shot for non-file-like inputs.
    """
    algo_key = (checksumtype or "md5").lower()
    saltkeyval = None
    if(hasattr(saltkey, "read")):
        saltkeyval = skfp.read()
        saltkeyval = saltkeyval.encode("UTF-8")
    elif(isinstance(saltkey, (bytes, ))):
        saltkeyval = saltkey
    elif(saltkey is not None and os.path.exists(saltkey)):
        with open(saltkey, "rb") as skfp:
            saltkeyval = skfp.read()
    else:
        saltkey = None
    if(saltkeyval is None):
        saltkey = None
    # file-like streaming
    if hasattr(inbytes, "read"):
        # hashlib

        if CheckSumSupport(algo_key, hashlib_guaranteed):
            if(saltkey is None or saltkeyval is None):
                h = hashlib.new(algo_key)
            else:
                h = hmac.new(saltkeyval, digestmod=algo_key)
            while True:
                chunk = inbytes.read(__filebuff_size__)
                if not chunk:
                    break
                if not isinstance(chunk, (bytes, bytearray, memoryview)):
                    chunk = bytes(bytearray(chunk))
                h.update(chunk)
            return h.hexdigest().lower()

        # not known streaming algo: fallback to one-shot bytes
        data = inbytes.read()
        if not isinstance(data, (bytes,)):
            data = data.encode("UTF-8")
    else:
        data = inbytes
        if not isinstance(data, (bytes, )):
            data = data.encode("UTF-8")

    # one-shot

    if CheckSumSupport(algo_key, hashlib_guaranteed):
        if(saltkey is None or saltkeyval is None):
            h = hashlib.new(algo_key, data)
        else:
            h = hmac.new(saltkeyval, data, digestmod=algo_key)
        return h.hexdigest().lower()

    return "0"

def ValidateHeaderChecksum(inlist=None, checksumtype="md5", inchecksum="0", formatspecs=None, saltkey=None):
    calc = GetHeaderChecksum(inlist, checksumtype, formatspecs, saltkey)
    want = (inchecksum or "0").strip().lower()
    if want.startswith("0x"):
        want = want[2:]
    return CheckChecksums(want, calc)

def ValidateFileChecksum(infile, checksumtype="md5", inchecksum="0", formatspecs=None, saltkey=None):
    calc = GetFileChecksum(infile, checksumtype, formatspecs, saltkey)
    want = (inchecksum or "0").strip().lower()
    if want.startswith("0x"):
        want = want[2:]
    return CheckChecksums(want, calc)

def CheckChecksums(inchecksum, outchecksum):
    # Normalize as text first
    calc = (inchecksum or "0").strip().lower()
    want = (outchecksum or "0").strip().lower()

    if want.startswith("0x"):
        want = want[2:]

    if not isinstance(calc, (bytes, )):
        calc = calc.encode("UTF-8")
    if not isinstance(want, (bytes, )):
        want = want.encode("UTF-8")

    return hmac.compare_digest(want, calc)

def AppendNullByte(indata, delimiter=None):
    if(delimiter is None):
        return False
    return indata + delimiter


def AppendNullBytes(indata=None, delimiter=None):
    if(delimiter is None):
        return False
    parts = [x for x in indata]
    return delimiter.join(parts) + delimiter

def ReadFileHeaderDataBySize(fp, delimiter="\x00"):
    bytesize = 0
    oldseek = fp.tell()
    while True:
        if(not fp.read(1).decode("UTF-8").isprintable()):
            break;
        bytesize += 1
    fp.seek(oldseek, 0)
    numhex = fp.read(bytesize).decode("UTF-8")
    numdec = int(numhex, 16)
    fp.seek(len(delimiter), 1)
    headerdata = fp.read(numdec).decode("UTF-8")
    headerdatasplit = headerdata.split(delimiter)
    headerdatasplit.insert(0, numhex)
    fp.seek(len(delimiter), 1)
    return headerdatasplit

def ReadFileHeaderData(fp, skipchecksum=False, formatspecs=None, saltkey=None):
    if(formatspecs is None):
        formatspecs = __file_format_multi_dict__
    filespec = None
    delimiter = None
    for key, value in formatspecs.items():
        oldseek = fp.tell()
        filetype = fp.read(value['format_len'])
        formatver = str(int(value['format_ver']))
        filever = fp.read(len(formatver)).decode("UTF-8")
        if(filetype.hex()==value['format_hex'] and formatver==filever):
            filespec = formatspecs[key]
            delimiter = filespec['format_delimiter']
            filetypefull = filetype.decode("UTF-8")+filever
            break
        fp.seek(oldseek, 1)
    if(filespec is None or delimiter is None):
        return False
    fp.seek(len(delimiter), 1)
    outlist = ReadFileHeaderDataBySize(fp, delimiter)
    outlist.insert(0, filetypefull)
    if(not ValidateHeaderChecksum(outlist[:-1], outlist[-2], outlist[-1], filespec, saltkey) and not skipchecksum):
        return False
    fp.seek(len(delimiter), 1)
    return outlist

def ReadFileHeaderDataWithContent(fp, listonly=False, contentasfile=False, uncompress=True, skipchecksum=False, formatspecs=__file_format_dict__, saltkey=None):
    if(not hasattr(fp, "read")):
        return False
    delimiter = formatspecs['format_delimiter']
    fheaderstart = fp.tell()
    HeaderOut = ReadFileHeaderDataBySize(fp, delimiter)
    if(len(HeaderOut) == 0):
        return False
    if(re.findall("^[.|/]", HeaderOut[5])):
        fname = HeaderOut[5]
    else:
        fname = "./"+HeaderOut[5]
    fcs = HeaderOut[-2].lower()
    fccs = HeaderOut[-1].lower()
    fsize = int(HeaderOut[7], 16)
    fcompression = HeaderOut[17]
    fcsize = int(HeaderOut[18], 16)
    fseeknextfile = HeaderOut[28]
    fjsontype = HeaderOut[29]
    fjsonlen = int(HeaderOut[30], 16)
    fjsonsize = int(HeaderOut[31], 16)
    fjsonchecksumtype = HeaderOut[32]
    fjsonchecksum = HeaderOut[33]
    fextrasize = int(HeaderOut[34], 16)
    fextrafields = int(HeaderOut[35], 16)
    fextrafieldslist = []
    extrastart = 36
    extraend = extrastart + fextrafields
    while(extrastart < extraend):
        fextrafieldslist.append(HeaderOut[extrastart])
        extrastart = extrastart + 1
    fvendorfieldslist = []
    fvendorfields = 0;
    if((len(HeaderOut) - 4)>extraend):
        extrastart = extraend
        extraend = len(HeaderOut) - 4
        while(extrastart < extraend):
            fvendorfieldslist.append(HeaderOut[extrastart])
            extrastart = extrastart + 1
            fvendorfields = fvendorfields + 1
    if(fextrafields==1):
        try:
            fextrafieldslist = json.loads(base64.b64decode(fextrafieldslist[0]).decode("UTF-8"))
            fextrafields = len(fextrafieldslist)
        except (binascii.Error, json.decoder.JSONDecodeError, UnicodeDecodeError):
            try:
                fextrafieldslist = json.loads(fextrafieldslist[0])
            except (binascii.Error, json.decoder.JSONDecodeError, UnicodeDecodeError):
                pass
    fjstart = fp.tell()
    if(fjsontype=="json"):
        fjsoncontent = {}
        fprejsoncontent = fp.read(fjsonsize).decode("UTF-8")
        if(fjsonsize > 0):
            try:
                fjsonrawcontent = base64.b64decode(fprejsoncontent.encode("UTF-8")).decode("UTF-8")
                fjsoncontent = json.loads(base64.b64decode(fprejsoncontent.encode("UTF-8")).decode("UTF-8"))
            except (binascii.Error, json.decoder.JSONDecodeError, UnicodeDecodeError):
                try:
                    fjsonrawcontent = fprejsoncontent
                    fjsoncontent = json.loads(fprejsoncontent)
                except (binascii.Error, json.decoder.JSONDecodeError, UnicodeDecodeError):
                    fprejsoncontent = ""
                    fjsonrawcontent = fprejsoncontent 
                    fjsoncontent = {}
        else:
            fprejsoncontent = ""
            fjsonrawcontent = fprejsoncontent 
            fjsoncontent = {}
    elif(testyaml and fjsontype == "yaml"):
        fjsoncontent = {}
        fprejsoncontent = fp.read(fjsonsize).decode("UTF-8")
        if (fjsonsize > 0):
            try:
                # try base64 → utf-8 → YAML
                fjsonrawcontent = base64.b64decode(fprejsoncontent.encode("UTF-8")).decode("UTF-8")
                fjsoncontent = yaml.safe_load(fjsonrawcontent) or {}
            except (binascii.Error, UnicodeDecodeError, yaml.YAMLError):
                try:
                    # fall back to treating the bytes as plain text YAML
                    fjsonrawcontent = fprejsoncontent
                    fjsoncontent = yaml.safe_load(fjsonrawcontent) or {}
                except (UnicodeDecodeError, yaml.YAMLError):
                    # final fallback: empty
                    fprejsoncontent = ""
                    fjsonrawcontent = fprejsoncontent
                    fjsoncontent = {}
        else:
            fprejsoncontent = ""
            fjsonrawcontent = fprejsoncontent
            fjsoncontent = {}
    elif(not testyaml and fjsontype == "yaml"):
        fjsoncontent = {}
        fprejsoncontent = fp.read(fjsonsize).decode("UTF-8")
        fprejsoncontent = ""
        fjsonrawcontent = fprejsoncontent
    elif(fjsontype=="list"):
        fprejsoncontent = fp.read(fjsonsize).decode("UTF-8")
        flisttmp = io.BytesIO()
        flisttmp.write(fprejsoncontent.encode())
        flisttmp.seek(0)
        fjsoncontent = ReadFileHeaderData(flisttmp, fjsonlen, delimiter)
        flisttmp.close()
        fjsonrawcontent = fjsoncontent
        if(fjsonlen==1):
            try:
                fjsonrawcontent = base64.b64decode(fjsoncontent[0]).decode("UTF-8")
                fjsoncontent = json.loads(base64.b64decode(fjsoncontent[0]).decode("UTF-8"))
                fjsonlen = len(fjsoncontent)
            except (binascii.Error, json.decoder.JSONDecodeError, UnicodeDecodeError):
                try:
                    fjsonrawcontent = fjsoncontent[0]
                    fjsoncontent = json.loads(fjsoncontent[0])
                except (binascii.Error, json.decoder.JSONDecodeError, UnicodeDecodeError):
                    pass
    fp.seek(len(delimiter), 1)
    fjend = fp.tell() - 1
    jsonfcs = GetFileChecksum(fprejsoncontent, fjsonchecksumtype, formatspecs, saltkey)
    if(not CheckChecksums(fjsonchecksum, jsonfcs) and not skipchecksum):
        VerbosePrintOut("File JSON Data Checksum Error with file " +
                        fname + " at offset " + str(fheaderstart))
        VerbosePrintOut("'" + fjsonchecksum + "' != " + "'" + jsonfcs + "'")
        return False
    fcs = HeaderOut[-2].lower()
    fccs = HeaderOut[-1].lower()
    newfcs = GetHeaderChecksum(HeaderOut[:-2], HeaderOut[-4].lower(), formatspecs, saltkey)
    if(fcs != newfcs and not skipchecksum):
        VerbosePrintOut("File Header Checksum Error with file " +
                        fname + " at offset " + str(fheaderstart))
        VerbosePrintOut("'" + fcs + "' != " + "'" + newfcs + "'")
        return False
    fhend = fp.tell() - 1
    fcontentstart = fp.tell()
    fcontents = io.BytesIO()
    pyhascontents = False
    if(fsize > 0 and not listonly):
        if(fcompression == "none" or fcompression == "" or fcompression == "auto"):
            fcontents.write(fp.read(fsize))
        else:
            fcontents.write(fp.read(fcsize))
        pyhascontents = True
    elif(fsize > 0 and listonly):
        if(fcompression == "none" or fcompression == "" or fcompression == "auto"):
            fp.seek(fsize, 1)
        else:
            fp.seek(fcsize, 1)
        pyhascontents = False
    fcontents.seek(0, 0)
    newfccs = GetFileChecksum(fcontents, HeaderOut[-3].lower(), formatspecs, saltkey)
    fcontents.seek(0, 0)
    if(not CheckChecksums(fccs, newfccs) and not skipchecksum and not listonly):
        VerbosePrintOut("File Content Checksum Error with file " +
                        fname + " at offset " + str(fcontentstart))
        VerbosePrintOut("'" + fccs + "' != " + "'" + newfccs + "'")
        return False
    if(fcompression == "none" or fcompression == "" or fcompression == "auto"):
        pass
    else:
        fcontents.seek(0, 0)
        if(uncompress):
            cfcontents = UncompressFileAlt(
                fcontents, formatspecs)
            cfcontents.seek(0, 0)
            fcontents = io.BytesIO()
            shutil.copyfileobj(cfcontents, fcontents, length=__filebuff_size__)
            cfcontents.close()
            fcontents.seek(0, 0)
            fccs = GetFileChecksum(fcontents, HeaderOut[-3].lower(), formatspecs, saltkey)
    fcontentend = fp.tell()
    if(re.findall("^\\+([0-9]+)", fseeknextfile)):
        fseeknextasnum = int(fseeknextfile.replace("+", ""))
        if(abs(fseeknextasnum) == 0):
            pass
        fp.seek(fseeknextasnum, 1)
    elif(re.findall("^\\-([0-9]+)", fseeknextfile)):
        fseeknextasnum = int(fseeknextfile)
        if(abs(fseeknextasnum) == 0):
            pass
        fp.seek(fseeknextasnum, 1)
    elif(re.findall("^([0-9]+)", fseeknextfile)):
        fseeknextasnum = int(fseeknextfile)
        if(abs(fseeknextasnum) == 0):
            pass
        fp.seek(fseeknextasnum, 0)
    else:
        return False
    fcontents.seek(0, 0)
    if(not contentasfile):
        fcontents = fcontents.read()
    HeaderOut.append(fcontents)
    return HeaderOut

def ReadFileHeaderDataWithContentToArray(fp, listonly=False, contentasfile=True, uncompress=True, skipchecksum=False, formatspecs=__file_format_dict__, saltkey=None):
    if(not hasattr(fp, "read")):
        return False
    delimiter = formatspecs['format_delimiter']
    fheaderstart = fp.tell()
    HeaderOut = ReadFileHeaderDataBySize(fp, delimiter)
    if(len(HeaderOut) == 0):
        return False
    fheadsize = int(HeaderOut[0], 16)
    fnumfields = int(HeaderOut[1], 16)
    ftype = int(HeaderOut[2], 16)
    fencoding = HeaderOut[3]
    fcencoding = HeaderOut[4]
    if(re.findall("^[.|/]", HeaderOut[5])):
        fname = HeaderOut[5]
    else:
        fname = "./"+HeaderOut[5]
    fbasedir = os.path.dirname(fname)
    flinkname = HeaderOut[6]
    fsize = int(HeaderOut[7], 16)
    fblksize = int(HeaderOut[8], 16)
    fblocks = int(HeaderOut[9], 16)
    fflags = int(HeaderOut[10], 16)
    fatime = int(HeaderOut[11], 16)
    fmtime = int(HeaderOut[12], 16)
    fctime = int(HeaderOut[13], 16)
    fbtime = int(HeaderOut[14], 16)
    fmode = int(HeaderOut[15], 16)
    fchmode = stat.S_IMODE(fmode)
    ftypemod = stat.S_IFMT(fmode)
    fwinattributes = int(HeaderOut[16], 16)
    fcompression = HeaderOut[17]
    fcsize = int(HeaderOut[18], 16)
    fuid = int(HeaderOut[19], 16)
    funame = HeaderOut[20]
    fgid = int(HeaderOut[21], 16)
    fgname = HeaderOut[22]
    fid = int(HeaderOut[23], 16)
    finode = int(HeaderOut[24], 16)
    flinkcount = int(HeaderOut[25], 16)
    fdev = int(HeaderOut[26], 16)
    frdev = int(HeaderOut[27], 16)
    fseeknextfile = HeaderOut[28]
    fjsontype = HeaderOut[29]
    fjsonlen = int(HeaderOut[30], 16)
    fjsonsize = int(HeaderOut[31], 16)
    fjsonchecksumtype = HeaderOut[32]
    fjsonchecksum = HeaderOut[33]
    fextrasize = int(HeaderOut[34], 16)
    fextrafields = int(HeaderOut[35], 16)
    fextrafieldslist = []
    extrastart = 36
    extraend = extrastart + fextrafields
    while(extrastart < extraend):
        fextrafieldslist.append(HeaderOut[extrastart])
        extrastart = extrastart + 1
    fvendorfieldslist = []
    fvendorfields = 0;
    if((len(HeaderOut) - 4)>extraend):
        extrastart = extraend
        extraend = len(HeaderOut) - 4
        while(extrastart < extraend):
            fvendorfieldslist.append(HeaderOut[extrastart])
            extrastart = extrastart + 1
            fvendorfields = fvendorfields + 1
    if(fextrafields==1):
        try:
            fextrafieldslist = json.loads(base64.b64decode(fextrafieldslist[0]).decode("UTF-8"))
            fextrafields = len(fextrafieldslist)
        except (binascii.Error, json.decoder.JSONDecodeError, UnicodeDecodeError):
            try:
                fextrafieldslist = json.loads(fextrafieldslist[0])
            except (binascii.Error, json.decoder.JSONDecodeError, UnicodeDecodeError):
                pass
    fjstart = fp.tell()
    if(fjsontype=="json"):
        fjsoncontent = {}
        fprejsoncontent = fp.read(fjsonsize).decode("UTF-8")
        if(fjsonsize > 0):
            try:
                fjsonrawcontent = base64.b64decode(fprejsoncontent.encode("UTF-8")).decode("UTF-8")
                fjsoncontent = json.loads(base64.b64decode(fprejsoncontent.encode("UTF-8")).decode("UTF-8"))
            except (binascii.Error, json.decoder.JSONDecodeError, UnicodeDecodeError):
                try:
                    fjsonrawcontent = fprejsoncontent
                    fjsoncontent = json.loads(fprejsoncontent)
                except (binascii.Error, json.decoder.JSONDecodeError, UnicodeDecodeError):
                    fprejsoncontent = ""
                    fjsonrawcontent = fprejsoncontent 
                    fjsoncontent = {}
        else:
            fprejsoncontent = ""
            fjsonrawcontent = fprejsoncontent 
            fjsoncontent = {}
    elif(testyaml and fjsontype == "yaml"):
        fjsoncontent = {}
        fprejsoncontent = fp.read(fjsonsize).decode("UTF-8")
        if (fjsonsize > 0):
            try:
                # try base64 → utf-8 → YAML
                fjsonrawcontent = base64.b64decode(fprejsoncontent.encode("UTF-8")).decode("UTF-8")
                fjsoncontent = yaml.safe_load(fjsonrawcontent) or {}
            except (binascii.Error, UnicodeDecodeError, yaml.YAMLError):
                try:
                    # fall back to treating the bytes as plain text YAML
                    fjsonrawcontent = fprejsoncontent
                    fjsoncontent = yaml.safe_load(fjsonrawcontent) or {}
                except (UnicodeDecodeError, yaml.YAMLError):
                    # final fallback: empty
                    fprejsoncontent = ""
                    fjsonrawcontent = fprejsoncontent
                    fjsoncontent = {}
        else:
            fprejsoncontent = ""
            fjsonrawcontent = fprejsoncontent
            fjsoncontent = {}
    elif(not testyaml and fjsontype == "yaml"):
        fjsoncontent = {}
        fprejsoncontent = fp.read(fjsonsize).decode("UTF-8")
        fprejsoncontent = ""
        fjsonrawcontent = fprejsoncontent
    elif(fjsontype=="list"):
        fprejsoncontent = fp.read(fjsonsize).decode("UTF-8")
        flisttmp = io.BytesIO()
        flisttmp.write(fprejsoncontent.encode())
        flisttmp.seek(0)
        fjsoncontent = ReadFileHeaderData(flisttmp, fjsonlen, delimiter)
        flisttmp.close()
        fjsonrawcontent = fjsoncontent
        if(fjsonlen==1):
            try:
                fjsonrawcontent = base64.b64decode(fjsoncontent[0]).decode("UTF-8")
                fjsoncontent = json.loads(base64.b64decode(fjsoncontent[0]).decode("UTF-8"))
                fjsonlen = len(fjsoncontent)
            except (binascii.Error, json.decoder.JSONDecodeError, UnicodeDecodeError):
                try:
                    fjsonrawcontent = fjsoncontent[0]
                    fjsoncontent = json.loads(fjsoncontent[0])
                except (binascii.Error, json.decoder.JSONDecodeError, UnicodeDecodeError):
                    pass
    fp.seek(len(delimiter), 1)
    fjend = fp.tell() - 1
    jsonfcs = GetFileChecksum(fprejsoncontent, fjsonchecksumtype, formatspecs, saltkey)
    if(not CheckChecksums(fjsonchecksum, jsonfcs) and not skipchecksum):
        VerbosePrintOut("File JSON Data Checksum Error with file " +
                        fname + " at offset " + str(fheaderstart))
        VerbosePrintOut("'" + fjsonchecksum + "' != " + "'" + jsonfcs + "'")
        return False
    fcs = HeaderOut[-2].lower()
    fccs = HeaderOut[-1].lower()
    newfcs = GetHeaderChecksum(HeaderOut[:-2], HeaderOut[-4].lower(), formatspecs, saltkey)
    if(fcs != newfcs and not skipchecksum):
        VerbosePrintOut("File Header Checksum Error with file " +
                        fname + " at offset " + str(fheaderstart))
        VerbosePrintOut("'" + fcs + "' != " + "'" + newfcs + "'")
        return False
    fhend = fp.tell() - 1
    fcontentstart = fp.tell()
    fcontents = io.BytesIO()
    pyhascontents = False
    if(fsize > 0 and not listonly):
        if(fcompression == "none" or fcompression == "" or fcompression == "auto"):
            fcontents.write(fp.read(fsize))
        else:
            fcontents.write(fp.read(fcsize))
        pyhascontents = True
    elif(fsize > 0 and listonly):
        if(fcompression == "none" or fcompression == "" or fcompression == "auto"):
            fp.seek(fsize, 1)
        else:
            fp.seek(fcsize, 1)
        pyhascontents = False
    fcontents.seek(0, 0)
    newfccs = GetFileChecksum(fcontents, HeaderOut[-3].lower(), formatspecs, saltkey)
    fcontents.seek(0, 0)
    if(not CheckChecksums(fccs, newfccs) and not skipchecksum and not listonly):
        VerbosePrintOut("File Content Checksum Error with file " +
                        fname + " at offset " + str(fcontentstart))
        VerbosePrintOut("'" + fccs + "' != " + "'" + newfccs + "'")
        return False
    if(fcompression == "none" or fcompression == "" or fcompression == "auto"):
        pass
    else:
        fcontents.seek(0, 0)
        if(uncompress):
            cfcontents = UncompressFileAlt(
                fcontents, formatspecs)
            cfcontents.seek(0, 0)
            fcontents = io.BytesIO()
            shutil.copyfileobj(cfcontents, fcontents, length=__filebuff_size__)
            cfcontents.close()
            fcontents.seek(0, 0)
            fccs = GetFileChecksum(fcontents, HeaderOut[-3].lower(), formatspecs, saltkey)
    fcontentend = fp.tell()
    if(re.findall("^\\+([0-9]+)", fseeknextfile)):
        fseeknextasnum = int(fseeknextfile.replace("+", ""))
        if(abs(fseeknextasnum) == 0):
            pass
        fp.seek(fseeknextasnum, 1)
    elif(re.findall("^\\-([0-9]+)", fseeknextfile)):
        fseeknextasnum = int(fseeknextfile)
        if(abs(fseeknextasnum) == 0):
            pass
        fp.seek(fseeknextasnum, 1)
    elif(re.findall("^([0-9]+)", fseeknextfile)):
        fseeknextasnum = int(fseeknextfile)
        if(abs(fseeknextasnum) == 0):
            pass
        fp.seek(fseeknextasnum, 0)
    else:
        return False
    fcontents.seek(0, 0)
    if(not contentasfile):
        fcontents = fcontents.read()
    outlist = {'fheadersize': fheadsize, 'fhstart': fheaderstart, 'fhend': fhend, 'ftype': ftype, 'fencoding': fencoding, 'fcencoding': fcencoding, 'fname': fname, 'fbasedir': fbasedir, 'flinkname': flinkname, 'fsize': fsize, 'fblksize': fblksize, 'fblocks': fblocks, 'fflags': fflags, 'fatime': fatime, 'fmtime': fmtime, 'fctime': fctime, 'fbtime': fbtime, 'fmode': fmode, 'fchmode': fchmode, 'ftypemod': ftypemod, 'fwinattributes': fwinattributes, 'fcompression': fcompression, 'fcsize': fcsize, 'fuid': fuid, 'funame': funame, 'fgid': fgid, 'fgname': fgname, 'finode': finode, 'flinkcount': flinkcount,
               'fdev': fdev, 'frdev': frdev, 'fseeknextfile': fseeknextfile, 'fheaderchecksumtype': HeaderOut[-4], 'fjsonchecksumtype': fjsonchecksumtype, 'fcontentchecksumtype': HeaderOut[-3], 'fnumfields': fnumfields + 2, 'frawheader': HeaderOut, 'fvendorfields': fvendorfields, 'fvendordata': fvendorfieldslist, 'fextrafields': fextrafields, 'fextrafieldsize': fextrasize, 'fextradata': fextrafieldslist, 'fjsontype': fjsontype, 'fjsonlen': fjsonlen, 'fjsonsize': fjsonsize, 'fjsonrawdata': fjsonrawcontent, 'fjsondata': fjsoncontent, 'fjstart': fjstart, 'fjend': fjend, 'fheaderchecksum': fcs, 'fjsonchecksum': fjsonchecksum, 'fcontentchecksum': fccs, 'fhascontents': pyhascontents, 'fcontentstart': fcontentstart, 'fcontentend': fcontentend, 'fcontentasfile': contentasfile, 'fcontents': fcontents}
    return outlist

def ReadFileDataWithContent(fp, filestart=0, listonly=False, contentasfile=False, uncompress=True, skipchecksum=False, formatspecs=None, saltkey=None):
    if(not hasattr(fp, "read")):
        return False
    delimiter = formatspecs['format_delimiter']
    curloc = filestart
    try:
        fp.seek(0, 2)
    except (OSError, ValueError):
        SeekToEndOfFile(fp)
    CatSize = fp.tell()
    CatSizeEnd = CatSize
    fp.seek(curloc, 0)
    inheaderver = str(int(formatspecs['format_ver'].replace(".", "")))
    headeroffset = fp.tell()
    formstring = fp.read(formatspecs['format_len'] + len(inheaderver)).decode("UTF-8")
    formdelszie = len(formatspecs['format_delimiter'])
    formdel = fp.read(formdelszie).decode("UTF-8")
    if(formstring != formatspecs['format_magic']+inheaderver):
        return False
    if(formdel != formatspecs['format_delimiter']):
        return False
    inheader = ReadFileHeaderDataBySize(fp, delimiter)
    fprechecksumtype = inheader[-2]
    fprechecksum = inheader[-1]
    headercheck = ValidateHeaderChecksum([formstring] + inheader[:-1], fprechecksumtype, fprechecksum, formatspecs, saltkey)
    newfcs = GetHeaderChecksum([formstring] + inheader[:-1], fprechecksumtype, formatspecs, saltkey)
    if(not headercheck and not skipchecksum):
        VerbosePrintOut(
            "File Header Checksum Error with file at offset " + str(headeroffset))
        VerbosePrintOut("'" + fprechecksum + "' != " +
                        "'" + newfcs + "'")
        return False
    fnumfiles = int(inheader[8], 16)
    outfseeknextfile = inheader[9]
    fjsonsize = int(inheader[12], 16)
    fjsonchecksumtype = inheader[13]
    fjsonchecksum = inheader[14]
    fp.read(fjsonsize)
    # Next seek directive
    if(re.findall(r"^\+([0-9]+)", outfseeknextfile)):
        fseeknextasnum = int(outfseeknextfile.replace("+", ""))
        if(abs(fseeknextasnum) == 0):
            pass
        fp.seek(fseeknextasnum, 1)
    elif(re.findall(r"^\-([0-9]+)", outfseeknextfile)):
        fseeknextasnum = int(outfseeknextfile)
        if(abs(fseeknextasnum) == 0):
            pass
        fp.seek(fseeknextasnum, 1)
    elif(re.findall(r"^([0-9]+)", outfseeknextfile)):
        fseeknextasnum = int(outfseeknextfile)
        if(abs(fseeknextasnum) == 0):
            pass
        fp.seek(fseeknextasnum, 0)
    else:
        return False
    countnum = 0
    flist = []
    while(countnum < fnumfiles):
        HeaderOut = ReadFileHeaderDataWithContent(fp, listonly, contentasfile, uncompress, skipchecksum, formatspecs, saltkey)
        if(len(HeaderOut) == 0):
            break
        flist.append(HeaderOut)
        countnum = countnum + 1
    return flist

def ReadFileDataWithContentToArray(fp, filestart=0, seekstart=0, seekend=0, listonly=False, contentasfile=True, uncompress=True, skipchecksum=False, formatspecs=__file_format_dict__, saltkey=None, seektoend=False):
    if(not hasattr(fp, "read")):
        return False
    delimiter = formatspecs['format_delimiter']
    curloc = filestart
    try:
        fp.seek(0, 2)
    except (OSError, ValueError):
        SeekToEndOfFile(fp)
    CatSize = fp.tell()
    CatSizeEnd = CatSize
    fp.seek(curloc, 0)
    inheaderver = str(int(formatspecs['format_ver'].replace(".", "")))
    headeroffset = fp.tell()
    formstring = fp.read(formatspecs['format_len'] + len(inheaderver)).decode("UTF-8")
    formdelszie = len(formatspecs['format_delimiter'])
    formdel = fp.read(formdelszie).decode("UTF-8")
    if(formstring != formatspecs['format_magic']+inheaderver):
        return False
    if(formdel != formatspecs['format_delimiter']):
        return False
    inheader = ReadFileHeaderDataBySize(
            fp, formatspecs['format_delimiter'])
    fnumextrafieldsize = int(inheader[15], 16)
    fnumextrafields = int(inheader[16], 16)
    fextrafieldslist = []
    extrastart = 17
    extraend = extrastart + fnumextrafields
    while(extrastart < extraend):
        fextrafieldslist.append(inheader[extrastart])
        extrastart = extrastart + 1
    if(fnumextrafields==1):
        try:
            fextrafieldslist = json.loads(base64.b64decode(fextrafieldslist[0]).decode("UTF-8"))
            fnumextrafields = len(fextrafieldslist)
        except (binascii.Error, json.decoder.JSONDecodeError, UnicodeDecodeError):
            try:
                fextrafieldslist = json.loads(fextrafieldslist[0])
            except (binascii.Error, json.decoder.JSONDecodeError, UnicodeDecodeError):
                pass
    fvendorfieldslist = []
    fvendorfields = 0;
    if((len(inheader) - 2)>extraend):
        extrastart = extraend
        extraend = len(inheader) - 2
        while(extrastart < extraend):
            fvendorfieldslist.append(HeaderOut[extrastart])
            extrastart = extrastart + 1
            fvendorfields = fvendorfields + 1
    formversion = re.findall("([\\d]+)", formstring)
    fheadsize = int(inheader[0], 16)
    fnumfields = int(inheader[1], 16)
    fheadctime = int(inheader[2], 16)
    fheadmtime = int(inheader[3], 16)
    fhencoding = inheader[4]
    fostype = inheader[5]
    fpythontype = inheader[6]
    fprojectname = inheader[7]
    fnumfiles = int(inheader[8], 16)
    fseeknextfile = inheader[9]
    fjsontype = inheader[10]
    fjsonlen = int(inheader[11], 16)
    fjsonsize = int(inheader[12], 16)
    fjsonchecksumtype = inheader[13]
    fjsonchecksum = inheader[14]
    fjsoncontent = {}
    fjstart = fp.tell()
    if(fjsontype=="json"):
        fjsoncontent = {}
        fprejsoncontent = fp.read(fjsonsize).decode("UTF-8")
        if(fjsonsize > 0):
            try:
                fjsonrawcontent = base64.b64decode(fprejsoncontent.encode("UTF-8")).decode("UTF-8")
                fjsoncontent = json.loads(base64.b64decode(fprejsoncontent.encode("UTF-8")).decode("UTF-8"))
            except (binascii.Error, json.decoder.JSONDecodeError, UnicodeDecodeError):
                try:
                    fjsonrawcontent = fprejsoncontent
                    fjsoncontent = json.loads(fprejsoncontent)
                except (binascii.Error, json.decoder.JSONDecodeError, UnicodeDecodeError):
                    fprejsoncontent = ""
                    fjsonrawcontent = fprejsoncontent 
                    fjsoncontent = {}
        else:
            fprejsoncontent = ""
            fjsonrawcontent = fprejsoncontent 
            fjsoncontent = {}
    elif(testyaml and fjsontype == "yaml"):
        fjsoncontent = {}
        fprejsoncontent = fp.read(fjsonsize).decode("UTF-8")
        if (fjsonsize > 0):
            try:
                # try base64 → utf-8 → YAML
                fjsonrawcontent = base64.b64decode(fprejsoncontent.encode("UTF-8")).decode("UTF-8")
                fjsoncontent = yaml.safe_load(fjsonrawcontent) or {}
            except (binascii.Error, UnicodeDecodeError, yaml.YAMLError):
                try:
                    # fall back to treating the bytes as plain text YAML
                    fjsonrawcontent = fprejsoncontent
                    fjsoncontent = yaml.safe_load(fjsonrawcontent) or {}
                except (UnicodeDecodeError, yaml.YAMLError):
                    # final fallback: empty
                    fprejsoncontent = ""
                    fjsonrawcontent = fprejsoncontent
                    fjsoncontent = {}
        else:
            fprejsoncontent = ""
            fjsonrawcontent = fprejsoncontent
            fjsoncontent = {}
    elif(not testyaml and fjsontype == "yaml"):
        fjsoncontent = {}
        fprejsoncontent = fp.read(fjsonsize).decode("UTF-8")
        fprejsoncontent = ""
        fjsonrawcontent = fprejsoncontent
    elif(fjsontype=="list"):
        fprejsoncontent = fp.read(fjsonsize).decode("UTF-8")
        flisttmp = io.BytesIO()
        flisttmp.write(fprejsoncontent.encode())
        flisttmp.seek(0)
        fjsoncontent = ReadFileHeaderData(flisttmp, fjsonlen, delimiter)
        flisttmp.close()
        fjsonrawcontent = fjsoncontent
        if(fjsonlen==1):
            try:
                fjsonrawcontent = base64.b64decode(fjsoncontent[0]).decode("UTF-8")
                fjsoncontent = json.loads(base64.b64decode(fjsoncontent[0]).decode("UTF-8"))
                fjsonlen = len(fjsoncontent)
            except (binascii.Error, json.decoder.JSONDecodeError, UnicodeDecodeError):
                try:
                    fjsonrawcontent = fjsoncontent[0]
                    fjsoncontent = json.loads(fjsoncontent[0])
                except (binascii.Error, json.decoder.JSONDecodeError, UnicodeDecodeError):
                    pass
    fjend = fp.tell()
    if(re.findall("^\\+([0-9]+)", fseeknextfile)):
        fseeknextasnum = int(fseeknextfile.replace("+", ""))
        if(abs(fseeknextasnum) == 0):
            pass
        fp.seek(fseeknextasnum, 1)
    elif(re.findall("^\\-([0-9]+)", fseeknextfile)):
        fseeknextasnum = int(fseeknextfile)
        if(abs(fseeknextasnum) == 0):
            pass
        fp.seek(fseeknextasnum, 1)
    elif(re.findall("^([0-9]+)", fseeknextfile)):
        fseeknextasnum = int(fseeknextfile)
        if(abs(fseeknextasnum) == 0):
            pass
        fp.seek(fseeknextasnum, 0)
    else:
        return False
    jsonfcs = GetFileChecksum(fprejsoncontent, fjsonchecksumtype, formatspecs, saltkey)
    if(not CheckChecksums(fjsonchecksum, jsonfcs) and not skipchecksum):
        VerbosePrintOut("File JSON Data Checksum Error with file " +
                        fname + " at offset " + str(fheaderstart))
        VerbosePrintOut("'" + fjsonchecksum + "' != " + "'" + jsonfcs + "'")
        return False
    fprechecksumtype = inheader[-2]
    fprechecksum = inheader[-1]
    headercheck = ValidateHeaderChecksum([formstring] + inheader[:-1], fprechecksumtype, fprechecksum, formatspecs, saltkey)
    newfcs = GetHeaderChecksum([formstring] + inheader[:-1], fprechecksumtype, formatspecs, saltkey)
    if(not headercheck and not skipchecksum):
        VerbosePrintOut(
            "File Header Checksum Error with file at offset " + str(headeroffset))
        VerbosePrintOut("'" + fprechecksum + "' != " +
                        "'" + newfcs + "'")
        return False
    formversions = re.search('(.*?)(\\d+)', formstring).groups()
    fcompresstype = ""
    outlist = {'fnumfiles': fnumfiles, 'ffilestart': filestart, 'fformat': formversions[0], 'fcompression': fcompresstype, 'fencoding': fhencoding, 'fmtime': fheadmtime, 'fctime': fheadctime, 'fversion': formversions[1], 'fostype': fostype, 'fprojectname': fprojectname, 'fimptype': fpythontype, 'fheadersize': fheadsize, 'fsize': CatSizeEnd, 'fnumfields': fnumfields + 2, 'fformatspecs': formatspecs, 'fseeknextfile': fseeknextfile, 'fchecksumtype': fprechecksumtype, 'fheaderchecksum': fprechecksum, 'fjsonchecksumtype': fjsonchecksumtype, 'fjsontype': fjsontype, 'fjsonlen': fjsonlen, 'fjsonsize': fjsonsize, 'fjsonrawdata': fjsonrawcontent, 'fjsondata': fjsoncontent, 'fjstart': fjstart, 'fjend': fjend, 'fjsonchecksum': fjsonchecksum, 'frawheader': [formstring] + inheader, 'fextrafields': fnumextrafields, 'fextrafieldsize': fnumextrafieldsize, 'fextradata': fextrafieldslist, 'fvendorfields': fvendorfields, 'fvendordata': fvendorfieldslist, 'ffilelist': []}
    if (seekstart < 0) or (seekstart > fnumfiles):
        seekstart = 0
    if (seekend == 0) or (seekend > fnumfiles) or (seekend < seekstart):
        seekend = fnumfiles
    elif (seekend < 0) and (abs(seekend) <= fnumfiles) and (abs(seekend) >= seekstart):
        seekend = fnumfiles - abs(seekend)
    if(seekstart > 0):
        il = 0
        while(il < seekstart):
            prefhstart = fp.tell()
            preheaderdata = ReadFileHeaderDataBySize(
                fp, formatspecs['format_delimiter'])
            if(len(preheaderdata) == 0):
                break
            prefsize = int(preheaderdata[5], 16)
            if(re.findall("^[.|/]", preheaderdata[5])):
                prefname = preheaderdata[5]
            else:
                prefname = "./"+preheaderdata[5]
            prefseeknextfile = preheaderdata[26]
            prefjsonlen = int(preheaderdata[28], 16)
            prefjsonsize = int(preheaderdata[29], 16)
            prefjsonchecksumtype = preheaderdata[30]
            prefjsonchecksum = preheaderdata[31]
            prejsoncontent = fp.read(prefjsonsize).decode("UTF-8")
            fp.seek(len(delimiter), 1)
            prejsonfcs = GetFileChecksum(prejsoncontent, prefjsonchecksumtype, formatspecs, saltkey)
            if(not CheckChecksums(prefjsonchecksum, prejsonfcs) and not skipchecksum):
                VerbosePrintOut("File JSON Data Checksum Error with file " +
                                prefname + " at offset " + str(prefhstart))
                VerbosePrintOut("'" + prefjsonchecksum + "' != " + "'" + prejsonfcs + "'")
                return False
            prenewfcs = GetHeaderChecksum(preheaderdata[:-2], preheaderdata[-4].lower(), formatspecs, saltkey)
            prefcs = preheaderdata[-2]
            if(not CheckChecksums(prefcs, prenewfcs) and not skipchecksum):
                VerbosePrintOut("File Header Checksum Error with file " +
                                 prefname + " at offset " + str(prefhstart))
                VerbosePrintOut("'" + prefcs + "' != " +
                                "'" + prenewfcs + "'")
                return False
                valid_archive = False
                invalid_archive = True
            prefhend = fp.tell() - 1
            prefcontentstart = fp.tell()
            prefcontents = io.BytesIO()
            pyhascontents = False
            if(prefsize > 0):
                prefcontents.write(fp.read(prefsize))
                prefcontents.seek(0, 0)
                prenewfccs = GetFileChecksum(prefcontents, preheaderdata[-3].lower(), formatspecs, saltkey)
                prefccs = preheaderdata[-1]
                pyhascontents = True
                if(not CheckChecksums(prefccs, prenewfccs) and not skipchecksum):
                    VerbosePrintOut("File Content Checksum Error with file " +
                                    prefname + " at offset " + str(prefcontentstart))
                    VerbosePrintOut("'" + prefccs +
                                    "' != " + "'" + prenewfccs + "'")
                    return False
            if(re.findall("^\\+([0-9]+)", prefseeknextfile)):
                fseeknextasnum = int(prefseeknextfile.replace("+", ""))
                if(abs(fseeknextasnum) == 0):
                    pass
                fp.seek(fseeknextasnum, 1)
            elif(re.findall("^\\-([0-9]+)", prefseeknextfile)):
                fseeknextasnum = int(prefseeknextfile)
                if(abs(fseeknextasnum) == 0):
                    pass
                fp.seek(fseeknextasnum, 1)
            elif(re.findall("^([0-9]+)", prefseeknextfile)):
                fseeknextasnum = int(prefseeknextfile)
                if(abs(fseeknextasnum) == 0):
                    pass
                fp.seek(fseeknextasnum, 0)
            else:
                return False
            il = il + 1
    realidnum = 0
    countnum = seekstart
    while (fp.tell() < CatSizeEnd) if seektoend else (countnum < seekend):
        HeaderOut = ReadFileHeaderDataWithContentToArray(fp, listonly, contentasfile, uncompress, skipchecksum, formatspecs, saltkey)
        if(len(HeaderOut) == 0):
            break
        HeaderOut.update({'fid': realidnum, 'fidalt': realidnum})
        outlist['ffilelist'].append(HeaderOut)
        countnum = countnum + 1
        realidnum = realidnum + 1
    outlist.update({'fp': fp})
    return outlist

test = open("./test.arc", "rb")
headerdata = ReadFileDataWithContentToArray(test, formatspecs=__file_format_dict__, uncompress=False)
print(headerdata)
test.close()
