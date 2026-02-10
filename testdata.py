#!/usr/bin/env python3
"""
archive_tool.py — merged ArchiveFile extractor/list tool

Best of:
- data.py: detection by magic hex, NUL-delimited token parsing, resilient scanning, safe extraction, lzma/bzip2/zlib
- test.py: INI/JSON configuration loading, env override, checksum helpers pattern

Usage:
  python archive_tool.py list   path/to/archive.arc --fmt archivefile.json
  python archive_tool.py extract path/to/archive.arc --fmt archivefile.ini --out output_dir
"""

from __future__ import annotations

import os
import re
import json
import bz2
import lzma
import zlib
import hmac
import argparse
import hashlib
import configparser
from dataclasses import dataclass
from typing import Dict, Tuple, List, Optional, Iterable, Any, Callable

HEXBYTES = b"0123456789abcdefABCDEF"


# ----------------------------
# Utilities
# ----------------------------

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


def is_hex_str(s: str) -> bool:
    return bool(s) and all(c in "0123456789abcdefABCDEF" for c in s)


def decode_unicode_escape(value: Any) -> str:
    """Decode INI/JSON escape sequences (compatible with test.py style)."""
    if value is None:
        return ""
    if isinstance(value, (bytes, bytearray, memoryview)):
        value = bytes(value).decode("utf-8", "replace")
    if not isinstance(value, str):
        value = str(value)
    return value.encode("utf-8").decode("unicode_escape")


def is_only_nonprintable(s: str) -> bool:
    """True if every character is non-printable."""
    if s is None:
        return True
    return all(not ch.isprintable() for ch in s)


# ----------------------------
# Checksums (lightweight + extensible)
# ----------------------------

def checksum_supported(algo_key: str) -> bool:
    try:
        return algo_key.lower() in hashlib.algorithms_available
    except Exception:
        return False


def file_checksum(data_or_file, algo: str = "md5", salt: Optional[bytes] = None, chunk_size: int = 256 * 1024) -> str:
    """Compute checksum for bytes/str/file-like."""
    algo_key = (algo or "md5").lower()

    def _new_hasher():
        if salt:
            return hmac.new(salt, digestmod=algo_key)
        return hashlib.new(algo_key)

    if not checksum_supported(algo_key):
        return "0"

    h = _new_hasher()

    if hasattr(data_or_file, "read"):
        while True:
            chunk = data_or_file.read(chunk_size)
            if not chunk:
                break
            if not isinstance(chunk, (bytes, bytearray, memoryview)):
                chunk = bytes(chunk)
            h.update(chunk)
        return h.hexdigest().lower()

    data = data_or_file
    if isinstance(data, str):
        data = data.encode("utf-8")
    if not isinstance(data, (bytes, bytearray, memoryview)):
        data = str(data).encode("utf-8")

    h.update(bytes(data))
    return h.hexdigest().lower()


def checksums_equal(a: str, b: str) -> bool:
    """Constant-time compare of hex strings (accepts 0x prefix)."""
    a = (a or "0").strip().lower()
    b = (b or "0").strip().lower()
    if a.startswith("0x"):
        a = a[2:]
    if b.startswith("0x"):
        b = b[2:]
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


# ----------------------------
# Format config loading (INI or JSON)
# ----------------------------

@dataclass(frozen=True)
class FormatSpec:
    key: str
    name: str
    magic_str: str             # human-readable magic (e.g. "ArchiveFile")
    magic_hex: str             # hex bytes for file detection
    delimiter: bytes           # usually b"\x00"
    extension: str = ""
    version: str = ""          # optional
    # Optional layout indices for tokenized records (default matches data.py)
    idx_type: int = 0
    idx_name: int = 3
    idx_usize: int = 5
    idx_comp: int = 15
    idx_csize: int = 16


def load_formats(fmt_path: str) -> Tuple[Optional[str], Dict[str, FormatSpec]]:
    """
    Load formats from either:
      - JSON like data.py
      - INI like test.py
    Returns (default_key, registry)
    """
    if not os.path.exists(fmt_path):
        raise FileNotFoundError(f"Format config not found: {fmt_path}")

    _, ext = os.path.splitext(fmt_path.lower())

    if ext in (".ini", ".cfg"):
        return _load_formats_ini(fmt_path)
    if ext in (".json",):
        return _load_formats_json(fmt_path)

    # Heuristic: try INI first, then JSON
    try:
        return _load_formats_ini(fmt_path)
    except Exception:
        return _load_formats_json(fmt_path)


def _normalize_delimiter(raw: str) -> bytes:
    raw = decode_unicode_escape(raw)
    # test.py enforces delimiter be non-printable; otherwise forces NUL
    if raw and not is_only_nonprintable(raw):
        raw = "\x00"
    if raw == "":
        raw = "\x00"
    return raw.encode("utf-8")


def _load_formats_ini(path: str) -> Tuple[Optional[str], Dict[str, FormatSpec]]:
    cp = configparser.ConfigParser()
    cp.read(path)

    default_key = None
    if cp.has_section("config"):
        default_key = decode_unicode_escape(cp.get("config", "default", fallback="")) or None

    registry: Dict[str, FormatSpec] = {}

    for section in cp.sections():
        if section == "config":
            continue

        required = ["hex", "magic", "delimiter"]
        if not all(cp.has_option(section, k) for k in required):
            continue

        magic = decode_unicode_escape(cp.get(section, "magic"))
        name = decode_unicode_escape(cp.get(section, "name", fallback=section)) or section
        magic_hex = decode_unicode_escape(cp.get(section, "hex"))
        delimiter = _normalize_delimiter(cp.get(section, "delimiter", fallback="\\x00"))
        extension = decode_unicode_escape(cp.get(section, "extension", fallback=""))
        version = decode_unicode_escape(cp.get(section, "ver", fallback=""))

        # Optional indices (nice "best of": make data.py layout configurable)
        idx_type = int(cp.get(section, "idx_type", fallback="0"))
        idx_name = int(cp.get(section, "idx_name", fallback="3"))
        idx_usize = int(cp.get(section, "idx_usize", fallback="5"))
        idx_comp = int(cp.get(section, "idx_comp", fallback="15"))
        idx_csize = int(cp.get(section, "idx_csize", fallback="16"))

        registry[section] = FormatSpec(
            key=section,
            name=name,
            magic_str=magic,
            magic_hex=magic_hex,
            delimiter=delimiter,
            extension=extension,
            version=version,
            idx_type=idx_type,
            idx_name=idx_name,
            idx_usize=idx_usize,
            idx_comp=idx_comp,
            idx_csize=idx_csize,
        )

    if not registry:
        raise ValueError(f"No formats found in INI: {path}")

    # If default_key isn't a section name, allow matching by magic_str
    if default_key and default_key not in registry:
        for k, spec in registry.items():
            if spec.magic_str == default_key or spec.name == default_key:
                default_key = k
                break
        else:
            default_key = next(iter(registry.keys()))

    if not default_key:
        default_key = next(iter(registry.keys()))

    return default_key, registry


def _load_formats_json(path: str) -> Tuple[Optional[str], Dict[str, FormatSpec]]:
    with open(path, "r", encoding="utf-8") as jf:
        spec = json.load(jf)

    cfg = spec.get("config", {}) or {}
    default_key = cfg.get("default") or None

    registry: Dict[str, FormatSpec] = {}

    for key, meta in spec.items():
        if key == "config" or not isinstance(meta, dict):
            continue

        magic_str = decode_unicode_escape(meta.get("magic", key))
        name = decode_unicode_escape(meta.get("name", key))
        magic_hex = decode_unicode_escape(meta.get("hex", ""))

        # delimiter may be "\u0000" in JSON
        delim_value = meta.get("delimiter", "\u0000")
        delimiter = _normalize_delimiter(delim_value)

        extension = decode_unicode_escape(meta.get("extension", ""))
        version = decode_unicode_escape(meta.get("ver", ""))

        idx_type = int(meta.get("idx_type", 0))
        idx_name = int(meta.get("idx_name", 3))
        idx_usize = int(meta.get("idx_usize", 5))
        idx_comp = int(meta.get("idx_comp", 15))
        idx_csize = int(meta.get("idx_csize", 16))

        registry[key] = FormatSpec(
            key=key,
            name=name,
            magic_str=magic_str,
            magic_hex=magic_hex,
            delimiter=delimiter,
            extension=extension,
            version=version,
            idx_type=idx_type,
            idx_name=idx_name,
            idx_usize=idx_usize,
            idx_comp=idx_comp,
            idx_csize=idx_csize,
        )

    if not registry:
        raise ValueError(f"No formats found in JSON: {path}")

    if default_key and default_key not in registry:
        # allow default to name/magic match
        for k, s in registry.items():
            if s.magic_str == default_key or s.name == default_key:
                default_key = k
                break
        else:
            default_key = next(iter(registry.keys()))

    if not default_key:
        default_key = next(iter(registry.keys()))

    return default_key, registry


def detect_format(file_path: str, fmt_registry: Dict[str, FormatSpec], default_key: Optional[str]) -> FormatSpec:
    """Detect by matching the longest magic hex prefix; fallback to default."""
    candidates: List[Tuple[int, FormatSpec, bytes]] = []
    for spec in fmt_registry.values():
        hx = spec.magic_hex or ""
        try:
            mb = bytes.fromhex(hx)
        except Exception:
            continue
        candidates.append((len(mb), spec, mb))

    if not candidates:
        if default_key and default_key in fmt_registry:
            return fmt_registry[default_key]
        raise ValueError("No valid magic hex entries in config.")

    max_len = max(n for n, _, _ in candidates)
    with open(file_path, "rb") as f:
        head = f.read(max_len)

    # longest match first
    candidates.sort(key=lambda t: t[0], reverse=True)
    for _, spec, mb in candidates:
        if mb and head.startswith(mb):
            return spec

    if default_key and default_key in fmt_registry:
        return fmt_registry[default_key]

    # last resort
    return next(iter(fmt_registry.values()))


# ----------------------------
# Token reader + record scanning (data.py best bits)
# ----------------------------

def make_token_reader(delim: bytes) -> Callable:
    """Read UTF-8 tokens separated by exactly one byte delimiter (commonly NUL)."""
    if len(delim) != 1:
        raise ValueError("Delimiter must be exactly 1 byte for this tool.")
    d = delim

    def read_token(f) -> str:
        buf = bytearray()
        while True:
            b = f.read(1)
            if not b:
                return buf.decode("utf-8", errors="ignore")
            if b == d:
                return buf.decode("utf-8", errors="ignore")
            buf += b

    return read_token


def scan_to_next_header(f, max_scan: int = 2_000_000) -> bool:
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


def find_content_start(f, compression: str, max_scan: int = 4096) -> Optional[int]:
    """
    After a record header there may be padding. Find the start of compressed payload.
    - lzma often starts with 0x5D
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


def decompress_payload(comp: str, payload: bytes) -> bytes:
    if comp == "lzma":
        return lzma.decompress(payload)
    if comp == "bzip2":
        return bz2.decompress(payload)
    if comp == "zlib":
        return zlib.decompress(payload)
    return payload


@dataclass
class Record:
    ftype: str
    name: str
    usize: int
    comp: str
    csize: int
    header_pos: int


def iter_records(f, read_token, fmt: FormatSpec) -> Iterable[Record]:
    """
    Tokenized ArchiveFile-style iterator (resilient).
    Assumes:
      signature token first (e.g. 'ArchiveFile1') then global header then records.
    Field indices are configurable in FormatSpec, default matches data.py.
    """
    sig = read_token(f)
    # allow prefix match (data.py style)
    if not sig.startswith(fmt.magic_str):
        raise ValueError(f"Signature mismatch: got {sig!r}, expected prefix {fmt.magic_str!r}")

    # Global header (best-effort consume)
    global_len_hex = read_token(f)
    global_count_raw = read_token(f)
    if is_hex_str(global_count_raw):
        global_count = int(global_count_raw, 16)
        _ = [read_token(f) for _ in range(global_count)]
    # If not hex, continue anyway—some variants exist.

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

        def _get(idx: int) -> str:
            return fields[idx] if 0 <= idx < len(fields) else ""

        ftype = _get(fmt.idx_type)
        fname = _get(fmt.idx_name)
        fsize_hex = _get(fmt.idx_usize) or "0"
        comp = _get(fmt.idx_comp)
        csize_hex = _get(fmt.idx_csize) or "0"

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

        yield Record(ftype=ftype, name=fname, usize=usize, comp=comp, csize=csize, header_pos=header_pos)


# ----------------------------
# High-level operations
# ----------------------------

def list_archive(arc_path: str, fmt_path: str) -> int:
    default_key, registry = load_formats(fmt_path)
    fmt = detect_format(arc_path, registry, default_key)

    print(f"Detected format: {fmt.key} (magic='{fmt.magic_str}', delimiter={fmt.delimiter!r})")

    read_token = make_token_reader(fmt.delimiter)

    listed = 0
    with open(arc_path, "rb") as f:
        for r in iter_records(f, read_token, fmt):
            if r.name:
                listed += 1
            kind = "DIR " if r.ftype != "0" else "FILE"
            print(f"{kind} {r.name}  usize={r.usize}  comp={r.comp}  csize={r.csize}")

    print(f"Done. Listed {listed} records.")
    return 0


def extract_archive(arc_path: str, fmt_path: str, out_dir: str, verify_sizes: bool = True) -> int:
    default_key, registry = load_formats(fmt_path)
    fmt = detect_format(arc_path, registry, default_key)

    print(f"Detected format: {fmt.key} (magic='{fmt.magic_str}', delimiter={fmt.delimiter!r})")

    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)

    read_token = make_token_reader(fmt.delimiter)

    extracted = 0
    with open(arc_path, "rb") as f:
        for r in iter_records(f, read_token, fmt):
            # extract only files with known compression and positive compressed size
            if r.ftype != "0":
                continue
            if not r.name or r.csize <= 0 or r.comp not in ("lzma", "bzip2", "zlib"):
                continue

            payload_start = find_content_start(f, r.comp)
            if payload_start is None:
                print(f"Could not locate content start for {r.name} ({r.comp}) after offset {f.tell()}")
                continue

            f.seek(payload_start, 0)
            payload = f.read(r.csize)
            if len(payload) != r.csize:
                print(f"Short read for {r.name}: wanted {r.csize}, got {len(payload)}")
                break

            try:
                data = decompress_payload(r.comp, payload)
            except Exception as e:
                print(f"Decompress failed for {r.name} ({r.comp}): {e}")
                f.seek(payload_start + r.csize, 0)
                continue

            out_path = safe_join(out_dir, r.name)
            os.makedirs(os.path.dirname(out_path), exist_ok=True)

            with open(out_path, "wb") as w:
                w.write(data)

            if verify_sizes and r.usize and len(data) != r.usize:
                status = f"SIZE MISMATCH (got {len(data)}, expected {r.usize})"
            else:
                status = "OK"

            print(f"Extracted {os.path.relpath(out_path, out_dir)} [{r.comp}] {status}")
            extracted += 1

            # jump to end of payload for next scan
            f.seek(payload_start + r.csize, 0)

    print(f"Done. Extracted {extracted} files into: {out_dir}")
    return 0


# ----------------------------
# CLI
# ----------------------------

def main() -> int:
    ap = argparse.ArgumentParser(
        description="List/extract ArchiveFile-style archives using INI or JSON format definitions."
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    ap_list = sub.add_parser("list", help="List archive contents")
    ap_list.add_argument("archive", help="Path to archive file (e.g. data.arc)")
    ap_list.add_argument("--fmt", required=True, help="Format config file (.ini or .json)")

    ap_ext = sub.add_parser("extract", help="Extract archive contents")
    ap_ext.add_argument("archive", help="Path to archive file (e.g. data.arc)")
    ap_ext.add_argument("--fmt", required=True, help="Format config file (.ini or .json)")
    ap_ext.add_argument("--out", default="output", help="Output directory (default: output)")
    ap_ext.add_argument("--no-size-check", action="store_true", help="Disable uncompressed size verification")

    args = ap.parse_args()

    if args.cmd == "list":
        return list_archive(args.archive, args.fmt)
    if args.cmd == "extract":
        return extract_archive(args.archive, args.fmt, args.out, verify_sizes=not args.no_size_check)

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
