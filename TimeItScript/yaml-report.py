import sys
import math
import argparse
from datetime import datetime

########################
# YAML mini-parser
########################

def parse_simple_yaml(path):
    """
    Parse the restricted YAML format emitted by time_script.py --yaml.
    Supports:
      key: value
      key:
        - item
        - item
    Values become str / float / int / None (null).
    Returns dict.
    """
    data = {}
    current_list_key = None

    def coerce_scalar(token):
        # trim whitespace
        token = token.strip()
        # null
        if token == "null":
            return None
        # bools
        if token == "true":
            return True
        if token == "false":
            return False
        # int?
        try:
            if token.isdigit() or (token.startswith("-") and token[1:].isdigit()):
                return int(token)
        except Exception:
            pass
        # float?
        try:
            # reject pure ints here to avoid double parsing
            if "." in token or "e" in token or "E" in token:
                return float(token)
            # also handle things like 0.436 without 'e'
            if "." in token:
                return float(token)
        except Exception:
            pass
        # quoted strings like "foo bar"
        if (token.startswith('"') and token.endswith('"')) or (
            token.startswith("'") and token.endswith("'")
        ):
            return token[1:-1]
        # fallback raw string
        return token

    with open(path, "r") as f:
        for raw_line in f:
            line = raw_line.rstrip("\n")

            # skip totally empty lines
            if not line.strip():
                continue

            # list entry?
            if line.lstrip().startswith("- "):
                # must currently be inside a list key
                if current_list_key is None:
                    raise ValueError(f"YAML parse error: list item outside list in {path}: {line}")
                # get whatever comes after '- '
                after_dash = line.lstrip()[2:]
                data[current_list_key].append(coerce_scalar(after_dash))
                continue

            # Otherwise it's either "key:" or "key: value"
            if ":" in line:
                # figure indent level
                # For our format we don't actually need indent for logic,
                # but we'll be strict: only top-level keys are supported.
                before_colon, after_colon = line.split(":", 1)
                key = before_colon.strip()
                value_part = after_colon.strip()

                if value_part == "":
                    # This starts a list (like "args:")
                    current_list_key = key
                    data[current_list_key] = []
                else:
                    # scalar "key: value"
                    current_list_key = None
                    data[key] = coerce_scalar(value_part)

            else:
                # unrecognized line style
                raise ValueError(f"YAML parse error in {path}: {line}")

    return data


########################
# Helpers for math/formatting
########################

def pct_diff(curr, base):
    """
    Percent slowdown (+) or speedup (-) from 'base' to 'curr'.
    """
    if curr is None or base is None:
        return None
    if base == 0:
        return None
    return (curr - base) / base * 100.0

def fmt_pct(p):
    if p is None:
        return "N/A"
    sign = "+" if p >= 0 else ""
    return f"{sign}{p:.2f}%"

def fmt_secs(sec):
    if sec is None:
        return "N/A"
    return f"{sec:.3f}s"

def join_args(args_field):
    if args_field is None:
        return ""
    if isinstance(args_field, list):
        return " ".join(str(x) for x in args_field)
    return str(args_field)

def pick_timestamp_from_filename_or_field(path, data):
    """
    Try to get a timestamp for display:
    - If YAML already has 'timestamp', use that.
    - Otherwise attempt to infer from filename like bench-2025-10-29T21-43-37.yaml.
    """
    if "timestamp" in data and data["timestamp"]:
        return data["timestamp"]

    import os, re
    base = os.path.basename(path)
    m = re.search(r"(\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2})", base)
    if not m:
        return None
    raw = m.group(1)  # like 2025-10-29T21-43-37
    date_part, time_part = raw.split("T", 1)
    time_part_clean = time_part.replace("-", ":")
    return f"{date_part}T{time_part_clean}"


########################
# Reporting helpers
########################

def normalize_record(data, path_for_ts=None):
    """
    Take the parsed YAML dict and return a normalized record
    with numeric fields and fallback timestamp.
    """
    def grab_float(k):
        v = data.get(k)
        if isinstance(v, (int, float)):
            return float(v)
        try:
            return float(v)
        except Exception:
            return None

    rec = {}
    rec["timestamp"]    = pick_timestamp_from_filename_or_field(path_for_ts, data)
    rec["script"]       = data.get("script")
    rec["args"]         = data.get("args")
    rec["runs"]         = data.get("runs")
    rec["warmup"]       = data.get("warmup")
    rec["real_avg_s"]   = grab_float("real_avg_s")
    rec["real_sd_s"]    = grab_float("real_sd_s")
    rec["user_avg_s"]   = grab_float("user_avg_s")
    rec["user_sd_s"]    = grab_float("user_sd_s")
    rec["sys_avg_s"]    = grab_float("sys_avg_s")
    rec["sys_sd_s"]     = grab_float("sys_sd_s")
    rec["peak_mem_mb"]  = grab_float("peak_mem_mb")
    rec["worst_exit"]   = data.get("worst_exit")

    return rec

def print_single_report(rec, label="Run"):
    """
    Pretty-print stats for one YAML record.
    """
    print(f"=== {label} ===")
    print(f"timestamp      : {rec.get('timestamp','N/A')}")
    print(f"script         : {rec.get('script','N/A')} {join_args(rec.get('args'))}")
    print(f"runs (warmup)  : {rec.get('runs','?')} ({rec.get('warmup','?')})")
    print(f"avg real time  : {fmt_secs(rec.get('real_avg_s'))} ± {fmt_secs(rec.get('real_sd_s'))}")
    print(f"user avg time  : {fmt_secs(rec.get('user_avg_s'))} ± {fmt_secs(rec.get('user_sd_s'))}")
    print(f"sys  avg time  : {fmt_secs(rec.get('sys_avg_s'))} ± {fmt_secs(rec.get('sys_sd_s'))}")
    print(f"peak mem       : {rec.get('peak_mem_mb','N/A')} MB")
    print(f"worst exit     : {rec.get('worst_exit','N/A')}")
    print()

def print_comparison(a, b, label_a="A", label_b="B"):
    """
    Compare two YAML-derived records.
    We'll report slowdown of B vs A.
    """
    slow_real = pct_diff(b["real_avg_s"], a["real_avg_s"])
    slow_user = pct_diff(b["user_avg_s"], a["user_avg_s"])
    slow_sys  = pct_diff(b["sys_avg_s"],  a["sys_avg_s"])

    print("=== Comparison (B vs A) ===")
    print(f"A timestamp     : {a.get('timestamp','N/A')}")
    print(f"B timestamp     : {b.get('timestamp','N/A')}")
    print()
    print("real avg time   : "
          + f"{fmt_secs(b['real_avg_s'])} vs {fmt_secs(a['real_avg_s'])}   "
          + f"slowdown {fmt_pct(slow_real)}")
    print("user avg time   : "
          + f"{fmt_secs(b['user_avg_s'])} vs {fmt_secs(a['user_avg_s'])}   "
          + f"slowdown {fmt_pct(slow_user)}")
    print("sys avg time    : "
          + f"{fmt_secs(b['sys_avg_s'])} vs {fmt_secs(a['sys_avg_s'])}   "
          + f"slowdown {fmt_pct(slow_sys)}")
    print()
    print("peak mem (MB)   : "
          + f"{b.get('peak_mem_mb','N/A')} vs {a.get('peak_mem_mb','N/A')}")
    print(f"runs (warmup)   : {b.get('runs','?')} ({b.get('warmup','?')})  vs  "
          f"{a.get('runs','?')} ({a.get('warmup','?')})")
    print(f"worst exit      : {b.get('worst_exit','N/A')} vs {a.get('worst_exit','N/A')}")
    print()


########################
# Main CLI
########################

def main():
    parser = argparse.ArgumentParser(
        description="Show performance summary / compare YAML benchmark snapshots"
    )
    parser.add_argument(
        "yaml_files",
        nargs="+",
        help="One YAML file to summarize, or two YAML files to compare."
    )
    args = parser.parse_args()

    if len(args.yaml_files) == 0:
        print("Need at least one YAML file.")
        sys.exit(1)

    if len(args.yaml_files) > 2:
        print("Please pass one file (show stats) or two files (compare).")
        sys.exit(1)

    # Load first file
    raw_a = parse_simple_yaml(args.yaml_files[0])
    rec_a = normalize_record(raw_a, path_for_ts=args.yaml_files[0])

    if len(args.yaml_files) == 1:
        # Single report mode
        print_single_report(rec_a, label="Run")
        return

    # Two-file compare mode
    raw_b = parse_simple_yaml(args.yaml_files[1])
    rec_b = normalize_record(raw_b, path_for_ts=args.yaml_files[1])

    print_single_report(rec_a, label="A")
    print_single_report(rec_b, label="B")
    print_comparison(rec_a, rec_b, label_a="A", label_b="B")


if __name__ == "__main__":
    main()
