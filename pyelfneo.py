#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ELF summary similar to GNU `file` + ldd-like dependency listing (Py2.7+/Py3.x)

Default: print `file`-style one-liner.
Options:
  --ldd         print ldd-like "NEEDED => resolved-path" lines
  --recursive   recurse dependencies (static; does not execute anything)
  --tree        show a dependency tree (implies --recursive)
  -v            verbose details
  --show-dynamic (with -v) show SONAME/NEEDED/RPATH/RUNPATH
"""

from __future__ import print_function

import os
import sys
import struct
import argparse
import glob


# ---------- Py2/Py3 helpers ----------

def _b1(x):
    if x is None:
        return 0
    if isinstance(x, int):  # Py3
        return x
    return ord(x)           # Py2


def _read_exact(f, n):
    data = f.read(n)
    if not data or len(data) != n:
        return None
    return data


def _align4(n):
    return (n + 3) & ~3


def _hex_bytes(b):
    if b is None:
        return ""
    if sys.version_info[0] >= 3:
        return b.hex()
    return "".join("{:02x}".format(ord(ch)) for ch in b)


def _safe_ascii(b):
    if b is None:
        return ""
    if isinstance(b, str) and sys.version_info[0] < 3:
        try:
            return b.decode("utf-8", "replace")
        except Exception:
            return b.decode("latin-1", "replace")
    try:
        return b.decode("utf-8", "replace")
    except Exception:
        try:
            return b.decode("latin-1", "replace")
        except Exception:
            return repr(b)


def _split_paths(s):
    if not s:
        return []
    # allow ':' separated paths
    return [p for p in s.split(":") if p]


def _uniq(seq):
    out = []
    seen = set()
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


# ---------- Lookups (subset, tuned for file-like output) ----------

OSABI = {
    0x00: "SYSV",
    0x01: "HPUX",
    0x02: "NetBSD",
    0x03: "Linux",
    0x04: "GNU",
    0x06: "Solaris",
    0x07: "AIX",
    0x08: "IRIX",
    0x09: "FreeBSD",
    0x0C: "OpenBSD",
}

ETYPES = {
    0x0000: "none",
    0x0001: "relocatable",
    0x0002: "executable",
    0x0003: "shared object",
    0x0004: "core file",
}

EMACH = {
    0x0000: "no machine",
    0x0002: "SPARC",
    0x0003: "Intel 80386",
    0x0008: "MIPS",
    0x0014: "PowerPC",
    0x0016: "IBM S/390",
    0x0028: "ARM",
    0x0032: "IA-64",
    0x003E: "x86-64",
    0x00B7: "AArch64",
    0x00F3: "RISC-V",
}

# Program header types
PT_LOAD    = 1
PT_DYNAMIC = 2
PT_INTERP  = 3
PT_NOTE    = 4

# Section header types
SHT_SYMTAB = 2

# GNU note types
NT_GNU_ABI_TAG  = 1
NT_GNU_BUILD_ID = 3

GNU_ABI_OS = {
    0: "Linux",
    1: "Hurd",
    2: "Solaris",
    3: "FreeBSD",
}

# ARM EABI flags
EF_ARM_EABIMASK = 0xFF000000

# MIPS ISA flags
EF_MIPS_ARCH    = 0xF0000000
EF_MIPS_ARCH_32    = 0x50000000
EF_MIPS_ARCH_64    = 0x60000000
EF_MIPS_ARCH_32R2  = 0x70000000
EF_MIPS_ARCH_64R2  = 0x80000000
EF_MIPS_ARCH_32R6  = 0x90000000
EF_MIPS_ARCH_64R6  = 0xA0000000

MIPS_ARCH_STR = {
    EF_MIPS_ARCH_32:   "MIPS32",
    EF_MIPS_ARCH_64:   "MIPS64",
    EF_MIPS_ARCH_32R2: "MIPS32 rel2",
    EF_MIPS_ARCH_64R2: "MIPS64 rel2",
    EF_MIPS_ARCH_32R6: "MIPS32 rel6",
    EF_MIPS_ARCH_64R6: "MIPS64 rel6",
}

# Dynamic tags we care about
DT_NULL    = 0
DT_NEEDED  = 1
DT_STRTAB  = 5
DT_STRSZ   = 10
DT_SONAME  = 14
DT_RPATH   = 15
DT_RUNPATH = 29


def _vaddr_to_offset(load_segs, vaddr):
    for seg in load_segs:
        start = seg["p_vaddr"]
        end = start + seg["p_filesz"]
        if vaddr >= start and vaddr < end:
            return (vaddr - start) + seg["p_offset"]
    return None


def _expand_origin(path_entry, origin_dir):
    # Expand $ORIGIN and ${ORIGIN}
    if not path_entry:
        return path_entry
    out = path_entry.replace("${ORIGIN}", origin_dir).replace("$ORIGIN", origin_dir)
    return out


def _parse_ld_so_conf(conf_path, dirs_out, visited):
    """
    Parse /etc/ld.so.conf with support for 'include' globs.
    Best-effort; matches typical Linux behavior well enough for resolution.
    """
    if not conf_path or conf_path in visited:
        return
    visited.add(conf_path)
    try:
        with open(conf_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("include "):
                    pat = line.split(None, 1)[1].strip()
                    for fn in glob.glob(pat):
                        _parse_ld_so_conf(fn, dirs_out, visited)
                else:
                    dirs_out.append(line)
    except Exception:
        return


def _system_library_paths():
    """
    Build a reasonable "system" library search path list:
    - /etc/ld.so.conf (+ includes)
    - common default dirs
    - common multiarch dirs
    """
    paths = []
    visited = set()
    _parse_ld_so_conf("/etc/ld.so.conf", paths, visited)

    # common defaults
    paths += [
        "/lib", "/usr/lib",
        "/lib64", "/usr/lib64",
    ]

    # common multiarch layouts
    paths += glob.glob("/lib/*-linux-gnu")
    paths += glob.glob("/usr/lib/*-linux-gnu")
    paths += glob.glob("/lib/*-gnu")          # e.g., some non-linux-gnu layouts
    paths += glob.glob("/usr/lib/*-gnu")

    # normalize + dedupe, keep only existing dirs
    out = []
    for p in paths:
        if p and os.path.isdir(p):
            out.append(p)
    return _uniq(out)


def _resolve_library(name, search_dirs):
    """
    Resolve 'libfoo.so.X' using search_dirs. Returns full path or None.
    """
    if not name:
        return None

    # If the NEEDED entry is already a path, honor it.
    if "/" in name:
        return name if os.path.isfile(name) else None

    for d in search_dirs:
        cand = os.path.join(d, name)
        if os.path.isfile(cand):
            return cand
    return None


def parse_elf(path, want_dynamic=True):
    """
    Parse enough ELF info for file-like summary + DT_NEEDED resolution.
    Returns dict or False.
    """
    if not path or (not os.path.exists(path)) or (not os.path.isfile(path)):
        return False

    with open(path, "rb") as f:
        ident = _read_exact(f, 16)
        if not ident or ident[:4] != b"\x7fELF":
            return False

        ei_class = _b1(ident[4:5])
        ei_data  = _b1(ident[5:6])
        ei_osabi = _b1(ident[7:8])

        if ei_data == 1:
            endian = "<"
            endian_name = "LSB"
        elif ei_data == 2:
            endian = ">"
            endian_name = "MSB"
        else:
            return False

        if ei_class == 1:
            bits = 32
            ehdr = _read_exact(f, 36)
            if not ehdr:
                return False
            (e_type, e_machine, e_version, e_entry, e_phoff, e_shoff,
             e_flags, e_ehsize, e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx) = \
                struct.unpack(endian + "HHIIIIIHHHHHH", ehdr)
        elif ei_class == 2:
            bits = 64
            ehdr = _read_exact(f, 48)
            if not ehdr:
                return False
            (e_type, e_machine, e_version, e_entry, e_phoff, e_shoff,
             e_flags, e_ehsize, e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx) = \
                struct.unpack(endian + "HHIQQQIHHHHHH", ehdr)
        else:
            return False

        info = {
            "path": path,
            "bits": bits,
            "endian": endian,
            "endian_name": endian_name,
            "osabi": OSABI.get(ei_osabi, "UNKNOWN"),
            "e_type": e_type,
            "e_type_name": ETYPES.get(e_type, "unknown"),
            "arch": EMACH.get(e_machine, "unknown"),
            "e_machine": e_machine,
            "e_version": e_version,
            "e_entry": e_entry,
            "e_flags": e_flags,

            "e_phoff": e_phoff,
            "e_phentsize": e_phentsize,
            "e_phnum": e_phnum,

            "e_shoff": e_shoff,
            "e_shentsize": e_shentsize,
            "e_shnum": e_shnum,
            "e_shstrndx": e_shstrndx,

            "has_dynamic": False,
            "interpreter": None,
            "buildid": None,
            "gnu_abi": None,

            "has_symtab": None,
            "has_debug": None,

            "abi_parts": [],

            # dynamic extras
            "soname": None,
            "needed": [],
            "rpath": None,
            "runpath": None,
        }

        # ABI extras from e_flags
        if e_machine == 0x0028:  # ARM
            ver = (e_flags & EF_ARM_EABIMASK) >> 24
            if ver:
                info["abi_parts"].append("EABI{0}".format(ver))
        if e_machine == 0x0008:  # MIPS
            mips_arch = (e_flags & EF_MIPS_ARCH)
            s = MIPS_ARCH_STR.get(mips_arch)
            if s:
                info["abi_parts"].append(s)

        # Program headers
        load_segs = []
        dynamic_seg = None
        phdrs = []

        if e_phoff and e_phnum and e_phentsize:
            try:
                f.seek(e_phoff, 0)
            except Exception:
                e_phnum = 0

            if bits == 32:
                ph_fmt = "IIIIIIII"
                ph_need = struct.calcsize(endian + ph_fmt)
                for _ in range(e_phnum):
                    raw = _read_exact(f, e_phentsize)
                    if not raw or len(raw) < ph_need:
                        break
                    (p_type, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_flags, p_align) = \
                        struct.unpack(endian + ph_fmt, raw[:ph_need])
                    phdrs.append((p_type, p_offset, p_filesz, p_vaddr))
                    if p_type == PT_LOAD:
                        load_segs.append({"p_vaddr": p_vaddr, "p_offset": p_offset, "p_filesz": p_filesz})
                    if p_type == PT_DYNAMIC:
                        dynamic_seg = {"p_offset": p_offset, "p_filesz": p_filesz}
            else:
                ph_fmt = "IIQQQQQQ"
                ph_need = struct.calcsize(endian + ph_fmt)
                for _ in range(e_phnum):
                    raw = _read_exact(f, e_phentsize)
                    if not raw or len(raw) < ph_need:
                        break
                    (p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align) = \
                        struct.unpack(endian + ph_fmt, raw[:ph_need])
                    phdrs.append((p_type, p_offset, p_filesz, p_vaddr))
                    if p_type == PT_LOAD:
                        load_segs.append({"p_vaddr": p_vaddr, "p_offset": p_offset, "p_filesz": p_filesz})
                    if p_type == PT_DYNAMIC:
                        dynamic_seg = {"p_offset": p_offset, "p_filesz": p_filesz}

        # dynamic?
        for (p_type, p_offset, p_filesz, p_vaddr) in phdrs:
            if p_type == PT_DYNAMIC:
                info["has_dynamic"] = True
                break

        # interpreter
        for (p_type, p_offset, p_filesz, p_vaddr) in phdrs:
            if p_type == PT_INTERP and p_filesz > 0:
                try:
                    f.seek(p_offset, 0)
                    raw = f.read(p_filesz)
                    if raw:
                        raw = raw.split(b"\x00", 1)[0]
                        info["interpreter"] = _safe_ascii(raw)
                except Exception:
                    pass
                break

        # GNU notes
        for (p_type, p_offset, p_filesz, p_vaddr) in phdrs:
            if p_type != PT_NOTE or p_filesz <= 0:
                continue
            try:
                f.seek(p_offset, 0)
                blob = f.read(p_filesz)
            except Exception:
                continue
            if not blob:
                continue

            off = 0
            while off + 12 <= len(blob):
                namesz, descsz, ntype = struct.unpack(endian + "III", blob[off:off+12])
                off += 12
                name = blob[off:off+namesz] if namesz else b""
                off += _align4(namesz)
                desc = blob[off:off+descsz] if descsz else b""
                off += _align4(descsz)

                name = name.split(b"\x00", 1)[0]

                if name == b"GNU" and ntype == NT_GNU_BUILD_ID and info["buildid"] is None:
                    algo = "sha1" if len(desc) == 20 else ("md5" if len(desc) == 16 else "hex")
                    info["buildid"] = (algo, _hex_bytes(desc))

                if name == b"GNU" and ntype == NT_GNU_ABI_TAG and info["gnu_abi"] is None:
                    if len(desc) >= 16:
                        os_id, maj, mi, sub = struct.unpack(endian + "IIII", desc[:16])
                        info["gnu_abi"] = (GNU_ABI_OS.get(os_id, "Unknown"), maj, mi, sub)

        # PIE heuristic
        if info["e_type"] == 0x0003 and info["interpreter"]:
            info["e_type_name"] = "pie executable"

        # Dynamic section parsing (NEEDED + string table + rpath/runpath/soname)
        if want_dynamic and dynamic_seg and load_segs:
            try:
                f.seek(dynamic_seg["p_offset"], 0)
                dyn_blob = f.read(dynamic_seg["p_filesz"]) or b""

                if bits == 32:
                    dyn_fmt = "II"
                    dyn_entsz = 8
                else:
                    dyn_fmt = "QQ"
                    dyn_entsz = 16

                dyn = []
                strtab_vaddr = None
                strsz = None

                for i in range(0, len(dyn_blob) - dyn_entsz + 1, dyn_entsz):
                    d_tag, d_val = struct.unpack(endian + dyn_fmt, dyn_blob[i:i+dyn_entsz])
                    dyn.append((d_tag, d_val))
                    if d_tag == DT_NULL:
                        break
                    if d_tag == DT_STRTAB:
                        strtab_vaddr = d_val
                    if d_tag == DT_STRSZ:
                        strsz = d_val

                if strtab_vaddr is not None and strsz:
                    strtab_off = _vaddr_to_offset(load_segs, strtab_vaddr)
                    if strtab_off is not None and strsz > 0:
                        f.seek(strtab_off, 0)
                        strtab = f.read(int(strsz)) or b""

                        def get_cstr(off):
                            off = int(off)
                            if off < 0 or off >= len(strtab):
                                return None
                            end = strtab.find(b"\x00", off)
                            if end == -1:
                                end = len(strtab)
                            return _safe_ascii(strtab[off:end])

                        for d_tag, d_val in dyn:
                            if d_tag == DT_SONAME and info["soname"] is None:
                                info["soname"] = get_cstr(d_val)
                            elif d_tag == DT_RPATH and info["rpath"] is None:
                                info["rpath"] = get_cstr(d_val)
                            elif d_tag == DT_RUNPATH and info["runpath"] is None:
                                info["runpath"] = get_cstr(d_val)
                            elif d_tag == DT_NEEDED:
                                s = get_cstr(d_val)
                                if s:
                                    info["needed"].append(s)
            except Exception:
                pass

        # Section headers: symtab + debug_info
        has_symtab = False
        has_debug = False
        if info["e_shoff"] and info["e_shnum"] and info["e_shentsize"]:
            try:
                f.seek(info["e_shoff"], 0)
                sh_list = []
                if bits == 32:
                    sh_fmt = "IIIIIIIIII"
                else:
                    sh_fmt = "IIQQQQIIQQ"
                sh_need = struct.calcsize(endian + sh_fmt)

                for _ in range(info["e_shnum"]):
                    raw = _read_exact(f, info["e_shentsize"])
                    if not raw or len(raw) < sh_need:
                        break
                    fields = struct.unpack(endian + sh_fmt, raw[:sh_need])
                    sh_name = fields[0]
                    sh_type = fields[1]
                    sh_offset = fields[4] if bits == 32 else fields[4]
                    sh_size = fields[5] if bits == 32 else fields[5]
                    sh_list.append({"sh_name": sh_name, "sh_type": sh_type, "sh_offset": sh_offset, "sh_size": sh_size})
                    if sh_type == SHT_SYMTAB:
                        has_symtab = True

                shstrtab = b""
                shstrndx = info["e_shstrndx"]
                if 0 <= shstrndx < len(sh_list):
                    shstr = sh_list[shstrndx]
                    if shstr["sh_offset"] and shstr["sh_size"]:
                        f.seek(shstr["sh_offset"], 0)
                        shstrtab = f.read(shstr["sh_size"]) or b""

                if shstrtab:
                    for sh in sh_list:
                        n = sh.get("sh_name", 0)
                        if n >= len(shstrtab):
                            continue
                        end = shstrtab.find(b"\x00", n)
                        if end == -1:
                            continue
                        name = shstrtab[n:end]
                        if (name.startswith(b".debug") or
                            name.startswith(b".zdebug") or
                            name in (b".gnu_debuglink", b".gnu_debugdata") or
                            name.endswith(b".dwo")):
                            has_debug = True
                            break

                info["has_symtab"] = has_symtab
                info["has_debug"] = has_debug
            except Exception:
                info["has_symtab"] = None
                info["has_debug"] = None

        return info


def format_like_file(info):
    parts = []
    parts.append("{0}: ELF {1}-bit {2} {3}".format(
        info["path"], info["bits"], info["endian_name"], info["e_type_name"]
    ))
    parts.append(info["arch"])

    for x in info.get("abi_parts", []):
        parts.append(x)

    parts.append("version {0} ({1})".format(info["e_version"], info["osabi"]))

    if info["has_dynamic"]:
        parts.append("dynamically linked")
    else:
        if info["e_type"] == 0x0002:
            parts.append("statically linked")

    if info["interpreter"]:
        parts.append("interpreter {0}".format(info["interpreter"]))

    if info["buildid"]:
        algo, hexid = info["buildid"]
        parts.append("BuildID[{0}]={1}".format(algo, hexid))

    if info["gnu_abi"] and info["gnu_abi"][0] == "Linux":
        _, maj, mi, sub = info["gnu_abi"]
        parts.append("for GNU/Linux {0}.{1}.{2}".format(maj, mi, sub))

    if info["has_debug"] is True:
        parts.append("with debug_info")

    if info["has_symtab"] is True:
        parts.append("not stripped")
    elif info["has_symtab"] is False:
        parts.append("stripped")

    return ", ".join(parts)


# ---------- ldd-like resolution ----------

def _build_search_dirs(elf_info):
    """
    Approximate loader search dirs for this object.
    We do a loader-ish order that matches common behavior:
      - if RUNPATH: LD_LIBRARY_PATH then RUNPATH
      - else if RPATH: RPATH then LD_LIBRARY_PATH
      - then system dirs (ld.so.conf + defaults)
    """
    origin = os.path.dirname(os.path.realpath(elf_info["path"]))
    rpath = elf_info.get("rpath")
    runpath = elf_info.get("runpath")

    rpath_dirs = [_expand_origin(p, origin) for p in _split_paths(rpath)]
    runpath_dirs = [_expand_origin(p, origin) for p in _split_paths(runpath)]

    ld_lib = _split_paths(os.environ.get("LD_LIBRARY_PATH", ""))

    sys_dirs = _system_library_paths()

    out = []
    if runpath_dirs:
        out += ld_lib
        out += runpath_dirs
    elif rpath_dirs:
        out += rpath_dirs
        out += ld_lib
    else:
        out += ld_lib

    out += sys_dirs
    # keep only existing dirs
    out2 = []
    for d in out:
        if d and os.path.isdir(d):
            out2.append(d)
    return _uniq(out2)


def ldd_like(path, recursive=False, tree=False, _seen=None, _indent=""):
    """
    Print ldd-like deps:
      libX.so => /path/libX.so
      libY.so => not found

    recursive/tree mode parses each found lib to list its DT_NEEDED too.
    """
    if _seen is None:
        _seen = set()

    info = parse_elf(path, want_dynamic=True)
    if not info:
        print("{0}: not an ELF file".format(path))
        return

    search_dirs = _build_search_dirs(info)

    # print interpreter like ldd does (roughly)
    if info.get("interpreter"):
        interp = info["interpreter"]
        interp_disp = os.path.basename(interp)
        print("{0}{1} => {2}".format(_indent, interp_disp, interp))

    needed = info.get("needed", []) or []
    for lib in needed:
        resolved = _resolve_library(lib, search_dirs)
        if resolved:
            print("{0}{1} => {2}".format(_indent, lib, resolved))
        else:
            print("{0}{1} => not found".format(_indent, lib))

    if tree:
        recursive = True

    if not recursive:
        return

    # recurse
    for lib in needed:
        resolved = _resolve_library(lib, search_dirs)
        if not resolved:
            continue
        rp = os.path.realpath(resolved)
        key = (rp,)
        if key in _seen:
            continue
        _seen.add(key)
        # In tree mode, indent child deps
        if tree:
            ldd_like(resolved, recursive=True, tree=True, _seen=_seen, _indent=_indent + "  ")
        else:
            ldd_like(resolved, recursive=True, tree=False, _seen=_seen, _indent=_indent)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    ap = argparse.ArgumentParser(description="GNU `file`-like ELF summary + static ldd-like deps (Python 2/3).")
    ap.add_argument("infile", help="Path to an ELF file")
    ap.add_argument("-v", "--verbose", action="store_true", help="Print extra parsed details")
    ap.add_argument("--show-dynamic", action="store_true", help="(with -v) show SONAME/NEEDED/RPATH/RUNPATH")
    ap.add_argument("--ldd", action="store_true", help="Print ldd-like linked libraries (static; no execution)")
    ap.add_argument("--recursive", action="store_true", help="(with --ldd) recursively list dependencies")
    ap.add_argument("--tree", action="store_true", help="(with --ldd) show dependency tree (implies --recursive)")
    args = ap.parse_args(argv)

    if args.ldd:
        # ldd-like mode
        ldd_like(args.infile, recursive=args.recursive or args.tree, tree=args.tree)
        return 0

    # file-like default
    info = parse_elf(args.infile, want_dynamic=True)
    if not info:
        print("{0}: cannot open or not an ELF file".format(args.infile))
        return 1

    print(format_like_file(info))

    if args.verbose:
        print("  bits:        {0}".format(info["bits"]))
        print("  endian:      {0}".format("little" if info["endian"] == "<" else "big"))
        print("  osabi:       {0}".format(info["osabi"]))
        print("  type:        0x{0:04x} ({1})".format(info["e_type"], info["e_type_name"]))
        print("  arch:        {0}".format(info["arch"]))
        if info.get("abi_parts"):
            print("  abi_parts:   {0}".format(", ".join(info["abi_parts"])))
        print("  entry:       0x{0:x}".format(int(info["e_entry"])))
        print("  flags:       0x{0:x}".format(int(info["e_flags"])))
        print("  dynamic:     {0}".format(bool(info["has_dynamic"])))
        print("  interpreter: {0}".format(info["interpreter"]))
        print("  buildid:     {0}".format(info["buildid"]))
        print("  gnu_abi:     {0}".format(info["gnu_abi"]))
        print("  has_debug:   {0}".format(info["has_debug"]))
        print("  has_symtab:  {0}".format(info["has_symtab"]))

        if args.show_dynamic:
            print("  soname:      {0}".format(info.get("soname")))
            print("  rpath:       {0}".format(info.get("rpath")))
            print("  runpath:     {0}".format(info.get("runpath")))
            print("  needed:      {0}".format(", ".join(info.get("needed", []))))

    return 0


if __name__ == "__main__":
    sys.exit(main())
