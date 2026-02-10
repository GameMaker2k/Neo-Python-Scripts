import os
import json
import argparse
import bz2
import lzma
import zlib

HEXBYTES = b"0123456789abcdefABCDEF"

# ----------------------------
# Format detection (from *.json)
# ----------------------------

def load_formats(json_path: str):
    with open(json_path, "r", encoding="utf-8") as jf:
        spec = json.load(jf)

    cfg = spec.get("config", {})
    default_name = cfg.get("default")

    formats = []
    for name, meta in spec.items():
        if name == "config":
            continue

        hx = meta.get("hex", "")
        try:
            magic_bytes = bytes.fromhex(hx)
        except Exception:
            continue

        formats.append((name, meta, magic_bytes))

    if not formats:
        raise ValueError(f"No formats found in {json_path}")

    return default_name, formats

def detect_format(file_path: str, json_path: str):
    default_name, formats = load_formats(json_path)

    max_len = max((len(mb) for _, _, mb in formats), default=64)
    with open(file_path, "rb") as f:
        head = f.read(max_len)

    # prefer longest match first
    formats_sorted = sorted(formats, key=lambda x: len(x[2]), reverse=True)
    for name, meta, magic_bytes in formats_sorted:
        if head.startswith(magic_bytes):
            return name, meta, magic_bytes

    # fallback to config.default
    if default_name:
        for name, meta, magic_bytes in formats:
            if name == default_name:
                return name, meta, magic_bytes

    raise ValueError("No matching format and no default in JSON.")

def parse_delimiter(delim_value) -> bytes:
    """
    JSON uses literal NUL often (shown as \u0000).
    If it's a string, encode it. If it's already something else, fallback to NUL.
    """
    if isinstance(delim_value, str) and delim_value != "":
        return delim_value.encode("utf-8")
    return b"\x00"

def make_token_reader(delim: bytes):
    """
    Token reader that preserves empty fields (important for this format).
    Delimiter is exactly one byte for your files (NUL), but this works for any single-byte delim.
    """
    if len(delim) != 1:
        # If someone ever sets a multi-byte delimiter, we can add support;
        # for now keep it strict to avoid subtle bugs.
        raise ValueError("Delimiter must be exactly 1 byte for this extractor.")
    d = delim

    def read_token(f):
        buf = bytearray()
        while True:
            b = f.read(1)
            if not b:
                return buf.decode("utf-8", errors="ignore")
            if b == d:
                return buf.decode("utf-8", errors="ignore")
            buf += b

    return read_token

# ----------------------------
# Archive helpers
# ----------------------------

def is_hex_str(s: str) -> bool:
    return bool(s) and all(c in "0123456789abcdefABCDEF" for c in s)

def scan_to_next_header(f, max_scan=2_000_000):
    """Skip padding/garbage until we find an ASCII hex digit that can start a header token."""
    scanned = 0
    while scanned < max_scan:
        b = f.read(1)
        if not b:
            return False
        scanned += 1
        if b in HEXBYTES:
            f.seek(-1, 1)
            return True
    raise RuntimeError("Could not find next header within scan limit")

def find_content_start(f, compression, max_scan=4096):
    """
    After a record header there may be padding. Find the start of compressed payload.
    - lzma (alone) commonly starts with 0x5D
    - bzip2 starts with 'BZh'
    - zlib usually starts with 0x78
    """
    start = f.tell()
    data = f.read(max_scan)
    if not data:
        return None

    if compression == "lzma":
        i = data.find(b"\x5d")
    elif compression == "bzip2":
        i = data.find(b"BZh")
    elif compression == "zlib":
        i = data.find(b"\x78")
    else:
        return None

    if i == -1:
        return None
    return start + i

def decompress_payload(comp, payload: bytes) -> bytes:
    if comp == "lzma":
        return lzma.decompress(payload)
    if comp == "bzip2":
        return bz2.decompress(payload)
    if comp == "zlib":
        return zlib.decompress(payload)
    return payload

def safe_join(base_dir: str, arc_path: str) -> str:
    """Prevent path traversal; always extract under base_dir."""
    arc_path = arc_path.lstrip("./").replace("\\", "/")
    while arc_path.startswith("/"):
        arc_path = arc_path[1:]

    full = os.path.abspath(os.path.join(base_dir, arc_path))
    base = os.path.abspath(base_dir)

    if os.path.commonpath([full, base]) != base:
        raise ValueError(f"Unsafe path (traversal blocked): {arc_path}")

    return full

# ----------------------------
# Record iterator (layout-based)
# ----------------------------

def iter_records(f, read_token, fmt_name: str, fmt_meta: dict, fmt_magic_str: str):
    """
    Yields dicts:
      {type, name, usize, comp, csize, header_pos}
    Uses the field layout that worked for your ArchiveFile1 .arc.
    If future formats change indices, we can extend the JSON schema to include them.
    """

    # Signature token in file (often "ArchiveFile1"), allow prefix match with fmt_magic_str ("ArchiveFile")
    sig = read_token(f)
    if not sig.startswith(fmt_magic_str):
        raise ValueError(f"Signature mismatch: got {sig!r}, expected prefix {fmt_magic_str!r}")
    print(f"Archive Signature: {sig}")

    # Global header
    global_len_hex = read_token(f)
    global_count_raw = read_token(f)
    if not is_hex_str(global_count_raw):
        raise ValueError(f"Bad global field_count: {global_count_raw!r}")
    global_count = int(global_count_raw, 16)

    _global_fields = [read_token(f) for _ in range(global_count)]
    print(f"Global header: len={global_len_hex}, fields={global_count} (consumed)")

    rec = 0
    while True:
        if not scan_to_next_header(f):
            break

        header_pos = f.tell()
        header_len_hex = read_token(f)
        if not is_hex_str(header_len_hex):
            break

        field_count_hex = read_token(f)
        if not is_hex_str(field_count_hex):
            continue

        field_count = int(field_count_hex, 16)
        fields = [read_token(f) for _ in range(field_count)]

        # Layout (works for your provided format doc / files):
        # fields[0] = ftype ("0" file, "5" dir)
        # fields[3] = fname
        # fields[5] = fsize_hex (uncompressed)
        # fields[15] = compression ("lzma"/"bzip2"/"zlib")
        # fields[16] = fcsize_hex (compressed)
        ftype = fields[0] if len(fields) > 0 else ""
        fname = fields[3] if len(fields) > 3 else ""
        fsize_hex = fields[5] if len(fields) > 5 else "0"
        comp = fields[15] if len(fields) > 15 else ""
        csize_hex = fields[16] if len(fields) > 16 else "0"

        try:
            usize = int(fsize_hex, 16) if is_hex_str(fsize_hex) else 0
        except Exception:
            usize = 0

        try:
            csize = int(csize_hex, 16) if is_hex_str(csize_hex) else 0
        except Exception:
            csize = 0

        if rec < 4:
            print(f"RECORD {rec} @ {header_pos}: hlen={header_len_hex} fcount={field_count_hex} type={ftype} name={fname}")
        rec += 1

        yield {
            "type": ftype,
            "name": fname,
            "usize": usize,
            "comp": comp,
            "csize": csize,
            "header_pos": header_pos,
        }

# ----------------------------
# Main extract/list
# ----------------------------

def process_archive(arc_path: str, fmt_json: str, out_dir: str, list_only: bool):
    fmt_name, fmt_meta, _magic_bytes = detect_format(arc_path, fmt_json)
    delim = parse_delimiter(fmt_meta.get("delimiter", "\u0000"))
    fmt_magic_str = fmt_meta.get("magic", fmt_name)  # e.g. "ArchiveFile"

    read_token = make_token_reader(delim)

    print(f"Detected format: {fmt_name} (magic='{fmt_magic_str}', delimiter={delim!r})")

    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)

    extracted = 0
    listed = 0

    with open(arc_path, "rb") as f:
        for r in iter_records(f, read_token, fmt_name, fmt_meta, fmt_magic_str):
            if r["name"]:
                listed += 1

            if list_only:
                kind = "DIR " if r["type"] != "0" else "FILE"
                print(f"{kind} {r['name']}  usize={r['usize']}  comp={r['comp']}  csize={r['csize']}")
                continue

            # extract only files with known compression and positive compressed size
            if r["type"] != "0":
                continue
            if not r["name"] or r["csize"] <= 0 or r["comp"] not in ("lzma", "bzip2", "zlib"):
                continue

            payload_start = find_content_start(f, r["comp"])
            if payload_start is None:
                print(f"Could not locate content start for {r['name']} ({r['comp']}) after offset {f.tell()}")
                continue

            f.seek(payload_start, 0)
            payload = f.read(r["csize"])
            if len(payload) != r["csize"]:
                print(f"Short read for {r['name']}: wanted {r['csize']}, got {len(payload)}")
                break

            try:
                data = decompress_payload(r["comp"], payload)
            except Exception as e:
                print(f"Decompress failed for {r['name']} ({r['comp']}): {e}")
                f.seek(payload_start + r["csize"], 0)
                continue

            out_path = safe_join(out_dir, r["name"])
            out_subdir = os.path.dirname(out_path)
            if out_subdir:
                os.makedirs(out_subdir, exist_ok=True)

            with open(out_path, "wb") as w:
                w.write(data)

            status = "OK" if (r["usize"] == 0 or len(data) == r["usize"]) else f"SIZE MISMATCH (got {len(data)}, expected {r['usize']})"
            print(f"Extracted {os.path.relpath(out_path, out_dir)} [{r['comp']}] {status}")
            extracted += 1

            # jump to end of payload for next scan
            f.seek(payload_start + r["csize"], 0)

    if list_only:
        print(f"Done. Listed {listed} records.")
    else:
        print(f"Done. Extracted {extracted} files into: {out_dir}")

def main():
    ap = argparse.ArgumentParser(description="Extract ArchiveFile/CatFile/FoxFile-style archives using a format JSON (e.g. archivefile.json).")
    ap.add_argument("archive", help="Path to archive file (e.g. data.arc)")
    ap.add_argument("--fmt", default="archivefile.json", help="Format JSON definition (default: archivefile.json)")
    ap.add_argument("--out", default="output", help="Output directory (default: output)")
    ap.add_argument("--list", action="store_true", help="List archive contents only (no extraction)")
    args = ap.parse_args()

    process_archive(args.archive, args.fmt, args.out, args.list)

if __name__ == "__main__":
    main()
