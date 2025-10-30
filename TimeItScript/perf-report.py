import csv
import sys
import argparse
from datetime import datetime

def parse_float(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None

def pct_diff(curr, base):
    # percent slower (+) or faster (-)
    if curr is None or base is None or base == 0:
        return None
    return (curr - base) / base * 100.0

def load_rows(csv_path):
    rows = []
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            ts = r.get("timestamp")
            # try to parse timestamp into datetime if possible
            r["_timestamp_dt"] = None
            if ts:
                try:
                    r["_timestamp_dt"] = datetime.fromisoformat(ts)
                except Exception:
                    pass

            r["_real_avg_s"] = parse_float(r.get("real_avg_s"))
            r["_real_sd_s"] = parse_float(r.get("real_sd_s"))
            r["_peak_mem_mb"] = parse_float(r.get("peak_mem_mb"))
            r["_worst_exit"] = r.get("worst_exit")

            rows.append(r)

    # sort chronologically if we could parse timestamps
    if all(r["_timestamp_dt"] is not None for r in rows):
        rows.sort(key=lambda x: x["_timestamp_dt"])

    return rows

def format_secs(sec):
    if sec is None:
        return "N/A"
    return f"{sec:.3f}s"

def format_pct(p):
    if p is None:
        return "N/A"
    sign = "+" if p >= 0 else ""
    return f"{sign}{p:.2f}%"

def pick_by_timestamp_prefix(rows, prefix):
    """
    Allow the user to pass e.g. '2025-10-29T21:43'
    and we'll pick the first row whose timestamp starts with that.
    If multiple match, we take the first match.
    """
    for r in rows:
        ts = r.get("timestamp", "")
        if ts.startswith(prefix):
            return r
    return None

def print_main_report(rows, last_n):
    latest = rows[-1]

    # best run = row with minimum avg real time
    best = min(
        rows,
        key=lambda r: (r["_real_avg_s"] if r["_real_avg_s"] is not None else float("inf"))
    )

    slowdown_pct = pct_diff(latest["_real_avg_s"], best["_real_avg_s"])

    print("=== Performance Report ===\n")
    print("Most recent run:")
    print(f"  timestamp      : {latest.get('timestamp','N/A')}")
    print(f"  script         : {latest.get('script','N/A')} {latest.get('args','')}")
    print(f"  runs (warmup)  : {latest.get('runs','?')} ({latest.get('warmup','?')})")
    print(f"  avg real time  : {format_secs(latest['_real_avg_s'])} ± {format_secs(latest['_real_sd_s'])}")
    print(f"  peak mem       : {latest.get('peak_mem_mb','N/A')} MB")
    print(f"  worst exit     : {latest.get('worst_exit','N/A')}")
    print()

    print("Best (fastest) run so far:")
    print(f"  timestamp      : {best.get('timestamp','N/A')}")
    print(f"  script         : {best.get('script','N/A')} {best.get('args','')}")
    print(f"  avg real time  : {format_secs(best['_real_avg_s'])} ± {format_secs(best['_real_sd_s'])}")
    print(f"  peak mem       : {best.get('peak_mem_mb','N/A')} MB")
    print()

    print("Change vs best:")
    print(f"  slowdown       : {format_pct(slowdown_pct)} "
          f"(current {format_secs(latest['_real_avg_s'])}, best {format_secs(best['_real_avg_s'])})")
    print()

    tail = rows[-last_n:]
    print(f"Last {len(tail)} runs:")
    header = [
        "timestamp",
        "real_avg_s",
        "sd",
        "peak_mem_mb",
        "runs",
        "exit",
    ]
    print("  " + " | ".join(h.ljust(20) for h in header))
    print("  " + "-+-".join("-"*20 for _ in header))

    for r in tail:
        ts = r.get("timestamp","")[:19]
        real_avg = r.get("real_avg_s","N/A")
        sd = r.get("real_sd_s","N/A")
        mem = r.get("peak_mem_mb","N/A")
        rn = r.get("runs","?")
        ex = r.get("worst_exit","?")
        line = [
            ts,
            str(real_avg),
            str(sd),
            str(mem),
            str(rn),
            str(ex),
        ]
        print("  " + " | ".join(val.ljust(20) for val in line))

def print_compare_block(a, b, label_a="A", label_b="B"):
    slowdown = pct_diff(b["_real_avg_s"], a["_real_avg_s"])

    print("\n=== Direct Comparison ===")
    print(f"{label_a}: {a.get('timestamp','N/A')}")
    print(f"  avg real       : {format_secs(a['_real_avg_s'])} ± {format_secs(a['_real_sd_s'])}")
    print(f"  peak mem       : {a.get('peak_mem_mb','N/A')} MB")
    print(f"  runs (warmup)  : {a.get('runs','?')} ({a.get('warmup','?')})")
    print()
    print(f"{label_b}: {b.get('timestamp','N/A')}")
    print(f"  avg real       : {format_secs(b['_real_avg_s'])} ± {format_secs(b['_real_sd_s'])}")
    print(f"  peak mem       : {b.get('peak_mem_mb','N/A')} MB")
    print(f"  runs (warmup)  : {b.get('runs','?')} ({b.get('warmup','?')})")
    print()
    print("Change B vs A:")
    print(f"  slowdown       : {format_pct(slowdown)} "
          f"(B {format_secs(b['_real_avg_s'])}, A {format_secs(a['_real_avg_s'])})")

def main():
    parser = argparse.ArgumentParser(
        description="Show performance summary / compare historical runs"
    )
    parser.add_argument("csv_path", help="Path to perf-log.csv")
    parser.add_argument(
        "--last",
        type=int,
        default=5,
        help="How many most recent rows to show in the history table (default 5)."
    )
    parser.add_argument(
        "--compare",
        nargs=2,
        metavar=("TSTAMP_A", "TSTAMP_B"),
        help="Compare two specific timestamps (prefix match). "
             "Example: --compare 2025-10-29T21:43 2025-10-30T00:12"
    )
    args = parser.parse_args()

    rows = load_rows(args.csv_path)
    if not rows:
        print("No rows in CSV yet.")
        sys.exit(0)

    # Always show the main report
    print_main_report(rows, args.last)

    # If the user asked for a comparison, do that too
    if args.compare:
        ts_a, ts_b = args.compare
        row_a = pick_by_timestamp_prefix(rows, ts_a)
        row_b = pick_by_timestamp_prefix(rows, ts_b)

        if row_a is None:
            print(f"\nCould not find any row starting with timestamp '{ts_a}'")
        elif row_b is None:
            print(f"\nCould not find any row starting with timestamp '{ts_b}'")
        else:
            print_compare_block(row_a, row_b, label_a="A", label_b="B")

if __name__ == "__main__":
    main()
