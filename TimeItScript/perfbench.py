import time
import math
import gc
import sys
from contextlib import contextmanager
from statistics import mean
from datetime import datetime

try:
    import resource
except Exception:
    resource = None


# ---------- low-level helpers ----------

def _usage_snapshot():
    """
    Snapshot resource usage for self + children.
    Returns (user_time, sys_time, peak_kb_raw).
    On platforms without resource, returns (None, None, None).
    """
    if resource is None:
        return None, None, None
    try:
        r_self = resource.getrusage(resource.RUSAGE_SELF)
        r_child = resource.getrusage(resource.RUSAGE_CHILDREN)
        user_t = r_self.ru_utime + r_child.ru_utime
        sys_t = r_self.ru_stime + r_child.ru_stime
        peak_kb = max(r_self.ru_maxrss, r_child.ru_maxrss)
        return user_t, sys_t, peak_kb
    except Exception:
        return None, None, None


def _kb_to_mb(kb_val):
    if kb_val is None:
        return None
    return kb_val / 1024.0


def _mean_std(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return (None, None)
    m = mean(vals)
    if len(vals) == 1:
        return (m, 0.0)
    var = sum((x - m) ** 2 for x in vals) / (len(vals) - 1)
    return (m, math.sqrt(var))


def _median_p90(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return (None, None)
    vals.sort()
    n = len(vals)
    # median
    if n % 2:
        med = vals[n // 2]
    else:
        med = 0.5 * (vals[n // 2 - 1] + vals[n // 2])
    # p90
    if n == 1:
        p90 = vals[0]
    else:
        idx = int(math.ceil(0.9 * n)) - 1
        if idx < 0:
            idx = 0
        if idx >= n:
            idx = n - 1
        p90 = vals[idx]
    return med, p90


def _format_time_human(seconds):
    if seconds is None:
        return "N/A"
    minutes = int(seconds // 60)
    rem = seconds - minutes * 60
    return f"{minutes}m{rem:.3f}s"


@contextmanager
def _maybe_disable_gc(disable):
    """
    Temporarily disable GC if disable=True.
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


def _run_once_callable(fn, args, kwargs, quiet=False):
    """
    Run fn(*args, **kwargs) once, capture timing + RSS delta.
    Returns dict with run stats.
    """
    # silence?
    if quiet:
        class DevNull:
            def write(self, _): pass
            def flush(self): pass
        old_out, old_err = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = DevNull(), DevNull()
    else:
        old_out = old_err = None

    wall_start = time.perf_counter()
    user_start, sys_start, kb_before = _usage_snapshot()

    err = None
    exit_code = 0
    try:
        fn(*args, **kwargs)
    except SystemExit as e:
        if isinstance(e.code, int):
            exit_code = e.code
        else:
            exit_code = 1
            err = f"SystemExit: {e.code}"
    except Exception as e:
        exit_code = 1
        err = f"Uncaught exception: {e}"

    wall_end = time.perf_counter()
    user_end, sys_end, kb_after = _usage_snapshot()

    if old_out is not None:
        sys.stdout, sys.stderr = old_out, old_err

    real_elapsed = wall_end - wall_start
    user_elapsed = None if user_start is None or user_end is None else (user_end - user_start)
    sys_elapsed  = None if sys_start  is None or sys_end  is None else (sys_end  - sys_start)

    if kb_before is not None and kb_after is not None:
        delta_kb = kb_after - kb_before
        if delta_kb < 0:
            delta_kb = 0
        rss_after_mb = _kb_to_mb(kb_after)
        rss_delta_mb = _kb_to_mb(delta_kb)
    else:
        rss_after_mb = None
        rss_delta_mb = None

    return {
        "real": real_elapsed,
        "user": user_elapsed,
        "sys": sys_elapsed,
        "rss_mb_after": rss_after_mb,
        "rss_delta_mb": rss_delta_mb,
        "exit_code": exit_code,
        "error": err,
    }


def _run_once_snippet(code_str, glb, quiet=False):
    """
    Execute code_str in given globals dict once, capture timing+RSS.
    Similar to _run_once_callable but for arbitrary code text.
    """
    if quiet:
        class DevNull:
            def write(self, _): pass
            def flush(self): pass
        old_out, old_err = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = DevNull(), DevNull()
    else:
        old_out = old_err = None

    wall_start = time.perf_counter()
    user_start, sys_start, kb_before = _usage_snapshot()

    err = None
    exit_code = 0
    try:
        exec(code_str, glb)
    except SystemExit as e:
        if isinstance(e.code, int):
            exit_code = e.code
        else:
            exit_code = 1
            err = f"SystemExit: {e.code}"
    except Exception as e:
        exit_code = 1
        err = f"Uncaught exception: {e}"

    wall_end = time.perf_counter()
    user_end, sys_end, kb_after = _usage_snapshot()

    if old_out is not None:
        sys.stdout, sys.stderr = old_out, old_err

    real_elapsed = wall_end - wall_start
    user_elapsed = None if user_start is None or user_end is None else (user_end - user_start)
    sys_elapsed  = None if sys_start  is None or sys_end  is None else (sys_end  - sys_start)

    if kb_before is not None and kb_after is not None:
        delta_kb = kb_after - kb_before
        if delta_kb < 0:
            delta_kb = 0
        rss_after_mb = _kb_to_mb(kb_after)
        rss_delta_mb = _kb_to_mb(delta_kb)
    else:
        rss_after_mb = None
        rss_delta_mb = None

    return {
        "real": real_elapsed,
        "user": user_elapsed,
        "sys": sys_elapsed,
        "rss_mb_after": rss_after_mb,
        "rss_delta_mb": rss_delta_mb,
        "exit_code": exit_code,
        "error": err,
    }


def _summarize_runs(runs):
    """
    Compute aggregate stats + fastest/slowest runs.
    """
    real_list = [r["real"] for r in runs]
    user_list = [r["user"] for r in runs]
    sys_list  = [r["sys"]  for r in runs]

    real_mean, real_sd = _mean_std(real_list)
    user_mean, user_sd = _mean_std(user_list)
    sys_mean,  sys_sd  = _mean_std(sys_list)

    real_med, real_p90 = _median_p90(real_list)

    # peak RSS
    rss_vals = [r["rss_mb_after"] for r in runs if r["rss_mb_after"] is not None]
    peak_rss = max(rss_vals) if rss_vals else None

    # worst exit code
    worst_exit = 0
    for r in runs:
        if r["exit_code"] != 0:
            worst_exit = r["exit_code"]

    # cpu util % and io share %
    if real_mean and user_mean is not None and sys_mean is not None and real_mean > 0:
        total_cpu = user_mean + sys_mean
        cpu_util = (total_cpu / real_mean) * 100.0
    else:
        cpu_util = None

    if user_mean is not None and sys_mean is not None and (user_mean + sys_mean) > 0:
        io_share = (sys_mean / (user_mean + sys_mean)) * 100.0
    else:
        io_share = None

    # slowest/fastest runs by real
    slow_i = None
    slow_val = None
    fast_i = None
    fast_val = None
    for i, r in enumerate(runs):
        rv = r["real"]
        if rv is None:
            continue
        if slow_val is None or rv > slow_val:
            slow_val = rv
            slow_i = i
        if fast_val is None or rv < fast_val:
            fast_val = rv
            fast_i = i

    slowest = (slow_i + 1, runs[slow_i]) if slow_i is not None else (None, None)
    fastest = (fast_i + 1, runs[fast_i]) if fast_i is not None else (None, None)

    return {
        "timestamp": datetime.now().isoformat(timespec="seconds"),

        "real_mean_s": real_mean,
        "real_sd_s": real_sd,
        "real_med_s": real_med,
        "real_p90_s": real_p90,

        "user_mean_s": user_mean,
        "user_sd_s": user_sd,
        "sys_mean_s": sys_mean,
        "sys_sd_s": sys_sd,

        "cpu_util_pct": cpu_util,
        "io_share_pct": io_share,

        "peak_mem_mb": peak_rss,
        "worst_exit": worst_exit,

        "fastest_index": fastest[0],
        "fastest_run": fastest[1],
        "slowest_index": slowest[0],
        "slowest_run": slowest[1],

        "all_runs": runs,
    }


def _print_summary(stats, note=None, max_real=None, max_mem=None):
    """
    Human-readable pretty print of stats, similar to your CLI script.
    Also returns a final status dict about pass/fail gates.
    """

    def _fmt_ms(val):
        return _format_time_human(val)

    def _fmt_pct(val):
        return "N/A" if val is None else f"{val:.1f}%"

    print("=== benchmark summary ===")
    print(f"real avg ± sd: {_fmt_ms(stats['real_mean_s'])} ± {stats['real_sd_s']:.3f}s"
          if stats['real_mean_s'] is not None else
          "real avg ± sd: N/A")
    print(f"real median:   {_fmt_ms(stats['real_med_s'])}")
    print(f"real p90:      {_fmt_ms(stats['real_p90_s'])}")

    print(f"user avg ± sd: {_fmt_ms(stats['user_mean_s'])} ± {stats['user_sd_s']:.3f}s"
          if stats['user_mean_s'] is not None else
          "user avg ± sd: N/A")
    print(f"sys  avg ± sd: {_fmt_ms(stats['sys_mean_s'])} ± {stats['sys_sd_s']:.3f}s"
          if stats['sys_mean_s'] is not None else
          "sys  avg ± sd: N/A")

    print(f"cpu util avg:  {_fmt_pct(stats['cpu_util_pct'])}")
    print(f"io share:     {_fmt_pct(stats['io_share_pct'])} kernel time")

    if stats["peak_mem_mb"] is not None:
        print(f"peak mem:      {stats['peak_mem_mb']:.1f}MB RSS")
    else:
        print("peak mem:      N/A")

    print(f"worst exit:    {stats['worst_exit']}")

    # Gates
    passed_perf = True
    passed_mem = True
    if max_real is not None and stats["real_mean_s"] is not None:
        passed_perf = (stats["real_mean_s"] <= max_real)
        state = "PASS" if passed_perf else "FAIL"
        print(f"perf gate:     {stats['real_mean_s']:.6f}s avg <= {max_real:.6f}s ? {state}")
    if max_mem is not None and stats["peak_mem_mb"] is not None:
        passed_mem = (stats["peak_mem_mb"] <= max_mem)
        state = "PASS" if passed_mem else "FAIL"
        print(f"mem gate:      {stats['peak_mem_mb']:.1f}MB peak <= {max_mem:.1f}MB ? {state}")

    # Fastest/slowest
    if stats["fastest_run"] is not None:
        fr = stats["fastest_run"]
        fi = stats["fastest_index"]
        print(f"\nfastest run (#{fi}):")
        print(f"  real={fr['real']:.3f}s user={fr['user']:.3f}s sys={fr['sys']:.3f}s "
              f"mem={fr['rss_mb_after']:.1f}MB exit={fr['exit_code']}")

    if stats["slowest_run"] is not None:
        sr = stats["slowest_run"]
        si = stats["slowest_index"]
        print(f"\nslowest run (#{si}):")
        print(f"  real={sr['real']:.3f}s user={sr['user']:.3f}s sys={sr['sys']:.3f}s "
              f"mem={sr['rss_mb_after']:.1f}MB exit={sr['exit_code']}")

    if note:
        print(f"\nnote: {note}")

    return {
        "passed_perf_gate": passed_perf,
        "passed_mem_gate": passed_mem,
        "worst_exit_zero": (stats["worst_exit"] == 0),
    }


# ---------- public API ----------

def benchmark_fn(
    fn,
    *args,
    runs=5,
    warmup=2,
    quiet=True,
    no_gc=False,
    note=None,
    max_real=None,
    max_mem=None,
    **kwargs,
):
    """
    Benchmark a callable in the current interpreter.

    Example:
        def f():
            do_work()
        benchmark_fn(f, runs=5, warmup=2, quiet=True)

    Params:
        fn        : function or callable to run each iteration
        *args/**kwargs : args passed to fn
        runs      : how many recorded iterations
        warmup    : how many pre-runs (not recorded)
        quiet     : suppress stdout/stderr from fn
        no_gc     : disable gc during timing runs
        note      : label stored in the result dict / printed
        max_real  : perf gate in seconds for average real time
        max_mem   : mem gate in MB for peak RSS

    Returns:
        stats dict (same fields printed)
    """
    # warmup
    with _maybe_disable_gc(no_gc):
        for _ in range(warmup):
            _run_once_callable(fn, args, kwargs, quiet=quiet)

    # measured
    results = []
    with _maybe_disable_gc(no_gc):
        for _ in range(runs):
            results.append(_run_once_callable(fn, args, kwargs, quiet=quiet))

    stats = _summarize_runs(results)
    _print_summary(stats, note=note, max_real=max_real, max_mem=max_mem)
    return stats


def benchmark_snippet(
    code_body,
    setup=None,
    runs=5,
    warmup=2,
    quiet=True,
    no_gc=False,
    note=None,
    max_real=None,
    max_mem=None,
):
    """
    Benchmark arbitrary code text, like timeit but with memory + cpu stats.

    Example:
        benchmark_snippet(
            "digest = hasher.update(data)",
            setup="import hashlib; hasher = hashlib.sha256(); data=b'x'*1024",
            runs=10,
            warmup=5,
        )

    Params:
        code_body : code string to exec each iteration
        setup     : optional code string run ONCE up front to build globals
        runs      : how many recorded iterations
        warmup    : how many pre-runs (not recorded)
        quiet     : suppress stdout/stderr
        no_gc     : disable gc during timing
        note      : label stored in the result dict / printed
        max_real  : perf gate in seconds
        max_mem   : mem gate in MB

    Returns:
        stats dict (same fields printed)
    """
    glb = {"__name__": "__perfbench__"}
    if setup:
        exec(setup, glb)

    with _maybe_disable_gc(no_gc):
        for _ in range(warmup):
            _run_once_snippet(code_body, glb, quiet=quiet)

    results = []
    with _maybe_disable_gc(no_gc):
        for _ in range(runs):
            results.append(_run_once_snippet(code_body, glb, quiet=quiet))

    stats = _summarize_runs(results)
    _print_summary(stats, note=note, max_real=max_real, max_mem=max_mem)
    return stats
