"""One owned, bounded Linux Python job; writes measurements, never a fingerprint."""
from __future__ import annotations

import json
import runpy
import sys
import time
import traceback
from pathlib import Path

try:
    import resource
except ImportError:  # pragma: no cover - reproduce.py rejects this platform first.
    resource = None


def main() -> int:
    report = Path(sys.argv[1])
    script = Path(sys.argv[2]).resolve()
    args = sys.argv[3:]
    if sys.version_info < (3, 10) or not sys.platform.startswith("linux") or resource is None:
        report.write_text(json.dumps({"exit_code": 2, "measurement_complete": False}, sort_keys=True) + "\n")
        print("bounded_worker requires Linux and Python >= 3.10", file=sys.stderr)
        return 2
    resource.setrlimit(resource.RLIMIT_AS, (3 * 1024**3, 3 * 1024**3))
    resource.setrlimit(resource.RLIMIT_CPU, (115, 118))
    resource.setrlimit(resource.RLIMIT_FSIZE, (8 * 1024**2, 8 * 1024**2))
    before = time.perf_counter()
    code = 0
    sys.argv = [str(script), *args]
    sys.path.insert(0, str(script.parent))
    try:
        runpy.run_path(str(script), run_name="__main__")
    except SystemExit as exc:
        code = 0 if exc.code is None else exc.code if isinstance(exc.code, int) else 1
    except BaseException:
        traceback.print_exc()
        code = 1
    usage = resource.getrusage(resource.RUSAGE_SELF)
    report.write_text(
        json.dumps(
            {
                "exit_code": code,
                "wall_seconds": time.perf_counter() - before,
                "cpu_seconds": usage.ru_utime + usage.ru_stime,
                "peak_rss_kib": usage.ru_maxrss,
            },
            sort_keys=True,
            indent=2,
        )
        + "\n"
    )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
