import sys
import time
import os
import io
import math
import argparse
import json
import gc
import csv
from datetime import datetime
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr, contextmanager

# Some platforms (Windows, Termux variants) might not have resource
try:
    import resource
except Exception:
    resource = None


# --- Utility: ANSI colors for pretty summary ---

class Color:
    GREEN = "\033[32m"
    RED = "\033[31m"
    RESET = "\033[0m"

def color_ok(text, ok=True):
    if ok:
        return f"{Color.GREEN}{text}{Color.RESET}"
    else:
        return f"{Color.RED}{text}{Color.RESET}"


# --- Formatting helpers ---

def format_time_human(seconds: float) -> str:
    """
    Format float seconds as XmY.YYYs to mimic /usr/bin/time.
    """
    minutes = int(seconds // 60)
    rem_seconds = seconds - minutes * 60
    return f"{minutes}m{rem_seconds:.3f}s"


def mean_std(values):
    vals = [v for v in values if v is not None]
    if not vals:
        return (None, None)
    m = sum(vals) / len(vals)
    if len(vals) > 1:
        var = sum((x - m) ** 2 for x in vals) / (len(vals) - 1)
        sd = math.sqrt(var)
    else:
        sd = 0.0
    return (m, sd)


# --- Resource snapshotting / memory accounting ---

def get_usage_snapshot():
    """
    Return a tuple (user_time, sys_time, peak_kb_raw)
    - user_time/sys_time include this process + children
    - peak_kb_raw is ru_maxrss (platform-dependent peak RSS, usually KB)
    If we can't measure (no resource module), all are None.
    """
    if resource is None:
        return None, None, None

    try:
        usage_self = resource.getrusage(resource.RUSAGE_SELF)
        usage_children = resource.getrusage(resource.RUSAGE_CHILDREN)

        user_time = usage_self.ru_utime + usage_children.ru_utime
        sys_time = usage_self.ru_stime + usage_children.ru_stime

        # ru_maxrss is KB on Linux, historically bytes on some BSDs/macOS.
        # We'll treat it as KB-ish and scale to MB best-effort.
        peak_kb_raw = max(usage_self.ru_maxrss, usage_children.ru_maxrss)

        return user_time, sys_time, peak_kb_raw
    except Exception:
        return None, None, None


def kb_to_mb(kb_val):
    if kb_val is None:
        return None
    return kb_val / 1024.0


# --- Context managers for cwd/env/gc tweaks ---

@contextmanager
def push_cwd(new_cwd: str | None):
    """
    Temporarily chdir into new_cwd if provided.
    """
    if not new_cwd:
        yield
        return
    old = os.getcwd()
    os.chdir(new_cwd)
    try:
        yield
    finally:
        os.chdir(old)


@contextmanager
def push_env(env_overrides):
    """
    Temporarily override os.environ with the given KEY=VALUE pairs.
    env_overrides: dict[str,str]
    """
    if not env_overrides:
        yield
        return

    old_values = {}
    for k, v in env_overrides.items():
        old_values[k] = os.environ.get(k, None)
        os.environ[k] = v

    try:
        yield
    finally:
        for k, old in old_values.items():
            if old is None:
                # key didn't exist before
                del os.environ[k]
            else:
                os.environ[k] = old


@contextmanager
def maybe_disable_gc(disable: bool):
    """
    If disable=True: disable GC for the duration, then restore.
    """
    if not disable:
        yield
        return
    was_enabled = gc.isenabled()
    if was_enabled:
        gc.disable()
    try:
        yield
    finally:
        if was_enabled:
            gc.enable()


# --- Core run logic ---

def run_target_once(script_path: Path, script_args, quiet: bool):
    """
    Run the target script exactly once under controlled conditions.
    Returns dict with:
      real, user, sys, rss_mb_after, rss_delta_mb, exit_code, error
    """
    # Prepare argv for the target
    sys.argv = [str(script_path)] + list(script_args)

    # Fresh global namespace so each run is isolated
    globals_dict = {"__name__": "__main__"}

    # Read & compile target script
    code = compile(script_path.read_text(), script_path.name, "exec")

    # Snapshot before
    wall_start = time.perf_counter()
    user_start, sys_start, peak_kb_before = get_usage_snapshot()

    # Handle quiet I/O
    if quiet:
        f_stdout = io.StringIO()
        f_stderr = io.StringIO()
        ctx_stdout = redirect_stdout(f_stdout)
        ctx_stderr = redirect_stderr(f_stderr)
    else:
        class _NullCtx:
            def __enter__(self): return None
            def __exit__(self, *a): return False
        ctx_stdout = _NullCtx()
        ctx_stderr = _NullCtx()

    exit_code = 0
    err = None

    with ctx_stdout, ctx_stderr:
        try:
            exec(code, globals_dict)
        except SystemExit as e:
            # Target called sys.exit(...)
            if isinstance(e.code, int):
                exit_code = e.code
            else:
                exit_code = 1
                err = f"SystemExit: {e.code}"
        except Exception as e:
            # Uncaught exception
            exit_code = 1
            err = f"Uncaught exception: {e}"

    # Snapshot after
    wall_end = time.perf_counter()
    user_end, sys_end, peak_kb_after = get_usage_snapshot()

    # Compute elapsed times
    real_elapsed = wall_end - wall_start

    if user_start is not None and user_end is not None:
        user_elapsed = user_end - user_start
    else:
        user_elapsed = None

    if sys_start is not None and sys_end is not None:
        sys_elapsed = sys_end - sys_start
    else:
        sys_elapsed = None

    # Memory:
    # peak_kb_* is "peak so far in the process". To approximate per-run
    # growth we take after-before (clamped at 0). Also record absolute peak.
    if peak_kb_before is not None and peak_kb_after is not None:
        delta_kb = peak_kb_after - peak_kb_before
        if delta_kb < 0:
            delta_kb = 0
        rss_delta_mb = kb_to_mb(delta_kb)
        rss_after_mb = kb_to_mb(peak_kb_after)
    else:
        rss_delta_mb = None
        rss_after_mb = None

    return {
        "real": real_elapsed,
        "user": user_elapsed,
        "sys": sys_elapsed,
        "rss_mb_after": rss_after_mb,     # approx absolute peak after run
        "rss_delta_mb": rss_delta_mb,     # approx growth during this run
        "exit_code": exit_code,
        "error": err,
    }


# --- Progress bar helpers ---

def build_progress_bar(done, total, width=10):
    """
    Return a string like [####------] for done/total.
    width = total slots in the bar.
    """
    if total <= 0:
        total = 1
    frac = done / total
    if frac < 0:
        frac = 0
    if frac > 1:
        frac = 1
    filled = int(round(frac * width))
    if filled > width:
        filled = width
    return "[" + "#" * filled + "-" * (width - filled) + "]"

def print_progress_line(run_idx, total_runs, status_text):
    """
    Overwrite the same console line with carriage return.
    status_text is appended after the bar and run info.
    """
    bar = build_progress_bar(run_idx, total_runs, width=10)
    line = f"{bar} Run {run_idx}/{total_runs} {status_text}"
    # \r moves cursor to start of line, no newline so we can update in place
    print("\r" + line, end="", flush=True)


# --- Printing helpers ---

def print_single_run(run, run_index: int | None = None):
    """
    Print time-style info for one run, including memory + exit code.
    """
    if run_index is not None:
        print(f"\n--- run {run_index} ---")

    real_str = format_time_human(run["real"])
    user_str = format_time_human(run["user"]) if run["user"] is not None else "N/A"
    sys_str  = format_time_human(run["sys"])  if run["sys"]  is not None else "N/A"

    print(f"real\t{real_str}")
    print(f"user\t{user_str}")
    print(f"sys \t{sys_str}")

    if run["rss_mb_after"] is not None:
        mem_line = f"{run['rss_mb_after']:.1f}MB peak RSS"
        if run["rss_delta_mb"] is not None:
            mem_line += f" (+{run['rss_delta_mb']:.1f}MB this run)"
        print(f"mem \t{mem_line}")
    else:
        print("mem \tN/A")

    print(f"exit\t{run['exit_code']}")
    if run["error"]:
        print(f"note\t{run['error']}")


def summarize_runs(runs):
    """
    Build aggregate statistics across all runs.
    Returns dict with means/sd, peak mem, worst exit, etc.
    """
    real_mean, real_sd = mean_std([r["real"] for r in runs])
    user_mean, user_sd = mean_std([r["user"] for r in runs])
    sys_mean,  sys_sd  = mean_std([r["sys"]  for r in runs])

    # Peak memory across runs
    rss_after_vals = [r["rss_mb_after"] for r in runs if r["rss_mb_after"] is not None]
    peak_rss = max(rss_after_vals) if rss_after_vals else None

    # Worst (nonzero) exit code from any run
    worst_exit = 0
    for r in runs:
        if r["exit_code"] != 0:
            worst_exit = r["exit_code"]

    return {
        "real_mean": real_mean,
        "real_sd": real_sd,
        "user_mean": user_mean,
        "user_sd": user_sd,
        "sys_mean": sys_mean,
        "sys_sd": sys_sd,
        "peak_rss": peak_rss,          # MB
        "worst_exit": worst_exit,
    }


def print_summary(stats, num_runs, max_real_threshold=None, max_mem_threshold=None):
    """
    Pretty summary with alignment and color.
    Returns a tuple:
      (passed_exit_ok, passed_perf_ok, passed_mem_ok)
    """
    def fmt_mean_sd(mean, sd):
        if mean is None:
            return "N/A"
        return f"{format_time_human(mean)} ± {sd:.3f}s"

    print(f"\n=== summary over {num_runs} runs ===")

    # line up labels to width 14
    print(f"{'real avg ± sd:'.ljust(14)} {fmt_mean_sd(stats['real_mean'], stats['real_sd'])}")
    print(f"{'user avg ± sd:'.ljust(14)} {fmt_mean_sd(stats['user_mean'], stats['user_sd'])}")
    print(f"{'sys  avg ± sd:'.ljust(14)} {fmt_mean_sd(stats['sys_mean'],  stats['sys_sd'])}")

    if stats["peak_rss"] is not None:
        print(f"{'peak mem:'.ljust(14)} {stats['peak_rss']:.1f}MB RSS")
    else:
        print(f"{'peak mem:'.ljust(14)} N/A")

    ok_exit = (stats["worst_exit"] == 0)
    worst_exit_line = "0" if ok_exit else str(stats["worst_exit"])
    print(f"{'worst exit:'.ljust(14)} {color_ok(worst_exit_line, ok_exit)}")

    # Performance gate
    passed_perf = True
    if max_real_threshold is not None and stats["real_mean"] is not None:
        passed_perf = stats["real_mean"] <= max_real_threshold
        perf_line = (
            f"{stats['real_mean']:.6f}s avg <= {max_real_threshold:.6f}s ? "
            + ("PASS" if passed_perf else "FAIL")
        )
        print(f"{'perf gate:'.ljust(14)} {color_ok(perf_line, passed_perf)}")

    # Memory gate
    passed_mem = True
    if max_mem_threshold is not None and stats["peak_rss"] is not None:
        passed_mem = stats["peak_rss"] <= max_mem_threshold
        mem_line = (
            f"{stats['peak_rss']:.1f}MB peak <= {max_mem_threshold:.1f}MB ? "
            + ("PASS" if passed_mem else "FAIL")
        )
        print(f"{'mem gate:'.ljust(14)} {color_ok(mem_line, passed_mem)}")

    return ok_exit, passed_perf, passed_mem


def write_csv(csv_path, stats, target_script, target_args, runs, warmup):
    """
    Append benchmark summary to a CSV.
    If file doesn't exist, write header first.
    """
    file_exists = os.path.exists(csv_path)

    row = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "script": str(target_script),
        "args": " ".join(target_args),
        "runs": runs,
        "warmup": warmup,
        "real_avg_s": stats["real_mean"],
        "real_sd_s": stats["real_sd"],
        "user_avg_s": stats["user_mean"],
        "user_sd_s": stats["user_sd"],
        "sys_avg_s": stats["sys_mean"],
        "sys_sd_s": stats["sys_sd"],
        "peak_mem_mb": stats["peak_rss"],
        "worst_exit": stats["worst_exit"],
    }

    fieldnames = list(row.keys())

    with open(csv_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def print_json_summary(stats, target_script, target_args, runs, warmup):
    """
    Print a machine-readable JSON summary to stdout.
    """
    out = {
        "script": str(target_script),
        "args": target_args,
        "runs": runs,
        "warmup": warmup,
        "real_avg_s": stats["real_mean"],
        "real_sd_s": stats["real_sd"],
        "user_avg_s": stats["user_mean"],
        "user_sd_s": stats["user_sd"],
        "sys_avg_s": stats["sys_mean"],
        "sys_sd_s": stats["sys_sd"],
        "peak_mem_mb": stats["peak_rss"],
        "worst_exit": stats["worst_exit"],
    }
    print("\nJSON summary:")
    print(json.dumps(out, indent=2, sort_keys=True))

def dump_yaml(obj, indent=0):
    """
    Minimal YAML dumper (no external deps).
    Handles dicts, lists, numbers, strings, None.
    Returns a string.
    """
    sp = "  " * indent
    if isinstance(obj, dict):
        lines = []
        for k, v in obj.items():
            # keys will be simple strings in our usage
            if isinstance(v, (dict, list)):
                lines.append(f"{sp}{k}:")
                lines.append(dump_yaml(v, indent + 1))
            else:
                lines.append(f"{sp}{k}: {scalar_to_yaml(v)}")
        return "\n".join(lines)
    elif isinstance(obj, list):
        lines = []
        for item in obj:
            if isinstance(item, (dict, list)):
                lines.append(f"{sp}-")
                lines.append(dump_yaml(item, indent + 1))
            else:
                lines.append(f"{sp}- {scalar_to_yaml(item)}")
        return "\n".join(lines)
    else:
        # scalar at top level
        return f"{sp}{scalar_to_yaml(obj)}"

def scalar_to_yaml(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    # string fallback
    s = str(v)
    # Quote only if we see something YAML might parse weird.
    # We'll keep it simple: if it has colon, newline, or starts with '-' or '#', quote.
    if (":" in s or "\n" in s or s.startswith("-") or s.startswith("#")):
        return json.dumps(s)  # reuse JSON quoting as valid YAML string
    return s

def print_yaml_summary(stats, target_script, target_args, runs, warmup):
    """
    Print a machine-readable YAML summary to stdout (no PyYAML required).
    """
    out = {
        "script": str(target_script),
        "args": target_args,
        "runs": runs,
        "warmup": warmup,
        "real_avg_s": stats["real_mean"],
        "real_sd_s": stats["real_sd"],
        "user_avg_s": stats["user_mean"],
        "user_sd_s": stats["user_sd"],
        "sys_avg_s": stats["sys_mean"],
        "sys_sd_s": stats["sys_sd"],
        "peak_mem_mb": stats["peak_rss"],
        "worst_exit": stats["worst_exit"],
    }
    print("\nYAML summary:")
    print(dump_yaml(out))


# --- arg parsing ---

def split_timer_vs_target(argv):
    """
    Support:
      python time_script.py [timer flags...] -- target.py [target args...]
    OR (no --):
      python time_script.py [timer flags...] target.py [target args...]

    Returns (timer_argv, target_argv).
    """
    if "--" in argv:
        sep_index = argv.index("--")
        our_argv = argv[1:sep_index]
        target_argv = argv[sep_index + 1:]
        return our_argv, target_argv

    # no explicit "--"
    if len(argv) <= 1:
        return [], []

    # find first non-dash arg after program name -> treat that as start of target
    split_at = None
    for i, a in enumerate(argv[1:], start=1):
        if not a.startswith("-"):
            split_at = i
            break

    if split_at is None:
        # all were flags, no script provided
        return argv[1:], []
    else:
        return argv[1:split_at], argv[split_at:]


def parse_args(argv):
    """
    Parse benchmarker flags AND separate target script + its args.
    """
    timer_argv, target_argv = split_timer_vs_target(argv)

    parser = argparse.ArgumentParser(
        prog="time_script.py",
        description="Benchmark a Python script (like `time`, with extra stats)."
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="How many measured runs to perform (default 1)."
    )
    parser.add_argument(
        "--warmup",
        type=int,
        default=0,
        help="How many warmup runs to execute before timing."
    )
    parser.add_argument(
        "--quiet-target",
        action="store_true",
        dest="quiet_target",
        help="Suppress target's stdout/stderr during runs."
    )
    parser.add_argument(
        "--show-each",
        action="store_true",
        dest="show_each",
        help="Print per-run stats even when --runs > 1."
    )
    parser.add_argument(
        "--cwd",
        dest="cwd",
        default=None,
        help="Run the target in this working directory."
    )
    parser.add_argument(
        "--env",
        dest="env_pairs",
        action="append",
        default=[],
        help="KEY=VALUE to inject into target's environment. Repeatable."
    )
    parser.add_argument(
        "--no-gc",
        dest="no_gc",
        action="store_true",
        help="Disable Python GC during measured runs (re-enabled after)."
    )
    parser.add_argument(
        "--max-real",
        dest="max_real",
        type=float,
        default=None,
        help="Fail (nonzero exit) if avg real time exceeds this many seconds."
    )
    parser.add_argument(
        "--max-mem",
        dest="max_mem",
        type=float,
        default=None,
        help="Fail (nonzero exit) if peak memory exceeds this many MB."
    )
    parser.add_argument(
        "--csv",
        dest="csv_path",
        default=None,
        help="Append summary row to this CSV file."
    )
    parser.add_argument(
        "--json",
        dest="emit_json",
        action="store_true",
        help="Also print machine-readable JSON summary."
    )
    parser.add_argument(
        "--yaml",
        dest="emit_yaml",
        action="store_true",
        help="Also print machine-readable YAML summary."
    )

    opts = parser.parse_args(timer_argv)
    return opts, target_argv


def parse_env_pairs(pairs_list):
    """
    Convert ["KEY=VALUE", "FOO=BAR"] -> {"KEY":"VALUE", "FOO":"BAR"}
    Silently ignore malformed entries without '='.
    """
    env_map = {}
    for item in pairs_list:
        if "=" in item:
            k, v = item.split("=", 1)
            env_map[k] = v
    return env_map


# --- main ---

def main():
    opts, target_argv = parse_args(sys.argv)

    if not target_argv:
        print("Usage:")
        print("  python time_script.py "
              "[--runs N] [--warmup M] [--quiet-target] [--show-each] "
              "[--cwd DIR] [--env KEY=VAL ...] [--no-gc] "
              "[--max-real SEC] [--max-mem MB] "
              "[--csv FILE] [--json] [--yaml] "
              "-- <script> [args...]")
        sys.exit(1)

    script_path = Path(target_argv[0])
    script_args = target_argv[1:]

    # Prepare environment overrides
    env_overrides = parse_env_pairs(opts.env_pairs)

    # Warmup runs (not recorded in stats)
    with push_cwd(opts.cwd), push_env(env_overrides), maybe_disable_gc(opts.no_gc):
        for _ in range(opts.warmup):
            run_target_once(script_path, script_args, quiet=opts.quiet_target)

    # Measured runs with progress bar
    results = []
    with push_cwd(opts.cwd), push_env(env_overrides), maybe_disable_gc(opts.no_gc):
        for i in range(opts.runs):
            run_number = i + 1

            # show starting state for this run
            print_progress_line(run_number, opts.runs, status_text="starting...")

            run_res = run_target_once(script_path, script_args, quiet=opts.quiet_target)
            results.append(run_res)

            # after run finishes, update progress with result summary
            short_real = f"{run_res['real']:.3f}s" if run_res['real'] is not None else "N/A"
            short_mem = (
                f"{run_res['rss_mb_after']:.1f}MB"
                if run_res['rss_mb_after'] is not None
                else "N/A"
            )

            # only show exit if it's nonzero
            if run_res["exit_code"] != 0:
                exit_fragment = f" exit={run_res['exit_code']}"
            else:
                exit_fragment = ""

            print_progress_line(
                run_number,
                opts.runs,
                status_text=f"done real={short_real} mem={short_mem}{exit_fragment}",
            )

            # Detailed per-run block (optional)
            if opts.runs == 1 or opts.show_each:
                # newline so block doesn't collide with bar text
                print()
                print_single_run(run_res, run_index=run_number)

        # after loop, newline so summary prints on its own line
        print()

    # Summary / post-processing
    stats = summarize_runs(results)

    ok_exit, passed_perf, passed_mem = print_summary(
        stats,
        num_runs=opts.runs,
        max_real_threshold=opts.max_real,
        max_mem_threshold=opts.max_mem,
    )

    # Optional CSV logging
    if opts.csv_path:
        write_csv(
            opts.csv_path,
            stats,
            target_script=script_path,
            target_args=script_args,
            runs=opts.runs,
            warmup=opts.warmup,
        )

    # Optional JSON/YAML output
    if opts.emit_json:
        print_json_summary(
            stats,
            target_script=str(script_path),
            target_args=script_args,
            runs=opts.runs,
            warmup=opts.warmup,
        )

    if opts.emit_yaml:
        print_yaml_summary(
            stats,
            target_script=str(script_path),
            target_args=script_args,
            runs=opts.runs,
            warmup=opts.warmup,
        )

    # Final exit code logic (including gates)
    final_exit = 0
    if stats["worst_exit"] != 0:
        final_exit = stats["worst_exit"]

    if not passed_perf:
        if final_exit == 0:
            final_exit = 1

    if not passed_mem:
        if final_exit == 0:
            final_exit = 1

    sys.exit(final_exit)


if __name__ == "__main__":
    main()
