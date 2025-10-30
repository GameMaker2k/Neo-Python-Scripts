import json
import argparse
import os
from datetime import datetime

def load_json_file(path):
    """
    Load a single benchmark JSON file produced by time_script.py --json.
    We'll augment with inferred timestamp from filename if possible.
    """
    with open(path, "r") as f:
        data = json.load(f)

    # try to infer timestamp from filename, e.g. bench-2025-10-29T21-43-37.json
    # we'll store that on 'timestamp' if it's not already there
    inferred_ts = infer_timestamp_from_filename(os.path.basename(path))
    if inferred_ts and "timestamp" not in data:
        data["timestamp"] = inferred_ts

    # normalize numeric fields that we expect
    def grab_float(key):
        val = data.get(key, None)
        if isinstance(val, (int, float)):
            return float(val)
        try:
            return float(val)
        except (TypeError, ValueError):
            return None

    norm = {}
    norm["timestamp"]     = data.get("timestamp")  # may be None
    norm["script"]        = data.get("script")
    norm["args"]          = data.get("args")
    norm["runs"]          = data.get("runs")
    norm["warmup"]        = data.get("warmup")
    norm["real_avg_s"]    = grab_float("real_avg_s")
    norm["real_sd_s"]     = grab_float("real_sd_s")
    norm["user_avg_s"]    = grab_float("user_avg_s")
    norm["user_sd_s"]     = grab_float("user_sd_s")
    norm["sys_avg_s"]     = grab_float("sys_avg_s")
    norm["sys_sd_s"]      = grab_float("sys_sd_s")
    norm["peak_mem_mb"]   = grab_float("peak_mem_mb")
    norm["worst_exit"]    = data.get("worst_exit")

    return norm

def infer_timestamp_from_filename(fname):
    """
    Heuristic:
    If filename has something like 2025-10-29T21-43-37 in it,
    we'll convert that to 2025-10-29T21:43:37 and use that.
    Otherwise return None.
    """
    # look for a chunk like YYYY-MM-DDThh-mm-ss
    # super rough pattern, but good enough
    import re
    m = re.search(r"(\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2})", fname)
    if not m:
        return None
    raw = m.group(1)  # e.g. 2025-10-29T21-43-37
    # swap '-' in the time part with ':'
    date_part, time_part = raw.split("T", 1)
    time_part_clean = time_part.replace("-", ":")
    return f"{date_part}T{time_part_clean}"

def fmt_secs(sec):
    if sec is None:
        return "N/A"
    return f"{sec:.3f}s"

def fmt_pair(a, b):
    # show "cur (a), prev (b)"
    return f"{fmt_secs(a)} vs {fmt_secs(b)}"

def pct_diff(curr, base):
    # percent slower (+) or faster (-)
    if curr is None or base is None or base == 0:
        return None
    return (curr - base) / base * 100.0

def fmt_pct(p):
    if p is None:
        return "N/A"
    sign = "+" if p >= 0 else ""
    return f"{sign}{p:.2f}%"

def print_single_report(data, label="Run"):
    """
    Pretty print one benchmark JSON's stats.
    """
    print(f"=== {label} ===")
    print(f"timestamp      : {data.get('timestamp','N/A')}")
    print(f"script         : {data.get('script','N/A')} {join_args(data.get('args'))}")
    print(f"runs (warmup)  : {data.get('runs','?')} ({data.get('warmup','?')})")
    print(f"avg real time  : {fmt_secs(data.get('real_avg_s'))} ± {fmt_secs(data.get('real_sd_s'))}")
    print(f"user avg time  : {fmt_secs(data.get('user_avg_s'))} ± {fmt_secs(data.get('user_sd_s'))}")
    print(f"sys  avg time  : {fmt_secs(data.get('sys_avg_s'))} ± {fmt_secs(data.get('sys_sd_s'))}")
    print(f"peak mem       : {data.get('peak_mem_mb','N/A')} MB")
    print(f"worst exit     : {data.get('worst_exit','N/A')}")
    print()

def join_args(args_field):
    if args_field is None:
        return ""
    if isinstance(args_field, list):
        return " ".join(str(x) for x in args_field)
    return str(args_field)

def print_comparison(a, b, label_a="A", label_b="B"):
    """
    Show a regression/speedup report comparing two JSON runs:
    B vs A.
    """
    slow_real = pct_diff(b["real_avg_s"], a["real_avg_s"])
    slow_user = pct_diff(b["user_avg_s"], a["user_avg_s"])
    slow_sys  = pct_diff(b["sys_avg_s"],  a["sys_avg_s"])

    print("=== Comparison (B vs A) ===")
    print(f"A timestamp     : {a.get('timestamp','N/A')}")
    print(f"B timestamp     : {b.get('timestamp','N/A')}")
    print()
    print("real avg time   : " +
          fmt_pair(b["real_avg_s"], a["real_avg_s"]) +
          f"   slowdown {fmt_pct(slow_real)}")
    print("user avg time   : " +
          fmt_pair(b["user_avg_s"], a["user_avg_s"]) +
          f"   slowdown {fmt_pct(slow_user)}")
    print("sys avg time    : " +
          fmt_pair(b["sys_avg_s"], a["sys_avg_s"]) +
          f"   slowdown {fmt_pct(slow_sys)}")
    print()
    print("peak mem (MB)   : " +
          f"{b.get('peak_mem_mb','N/A')} vs {a.get('peak_mem_mb','N/A')}")
    print(f"runs (warmup)   : {b.get('runs','?')} ({b.get('warmup','?')})  vs  "
          f"{a.get('runs','?')} ({a.get('warmup','?')})")
    print(f"worst exit      : {b.get('worst_exit','N/A')} vs {a.get('worst_exit','N/A')}")
    print()

def main():
    parser = argparse.ArgumentParser(
        description="Read one or two JSON benchmark summaries and report performance."
    )
    parser.add_argument(
        "json_files",
        nargs="+",
        help="One JSON file (summary), or two JSON files to compare."
    )
    args = parser.parse_args()

    if len(args.json_files) == 0:
        print("Need at least one JSON file.")
        return

    if len(args.json_files) > 2:
        print("Please pass one file (show stats) or two files (compare).")
        return

    # Load runs
    run_a = load_json_file(args.json_files[0])
    if len(args.json_files) == 1:
        # Just print single
        print_single_report(run_a, label="Run")
        return

    # Two runs: compare
    run_b = load_json_file(args.json_files[1])

    # We’ll show both individually first:
    print_single_report(run_a, label="A")
    print_single_report(run_b, label="B")

    # Then show diff B vs A:
    print_comparison(run_a, run_b, label_a="A", label_b="B")

if __name__ == "__main__":
    main()
