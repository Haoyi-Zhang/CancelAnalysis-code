"""Rebuild and independently check the finite evidence.

Supported runner environment: Linux, Python >= 3.10, standard library only.
The bounded child runner relies on POSIX ``resource`` limits and process-group
termination; native Windows is therefore intentionally rejected (WSL is Linux).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import platform
import re
import signal
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def platform_preflight() -> dict[str, str]:
    errors = []
    if sys.version_info < (3, 10):
        errors.append("Python 3.10 or newer is required")
    if platform.system() != "Linux":
        errors.append("the bounded runner is supported on Linux only (native Windows lacks resource/killpg semantics)")
    if importlib.util.find_spec("resource") is None:
        errors.append("the Python resource module is unavailable")
    if not hasattr(os, "killpg"):
        errors.append("os.killpg is unavailable")
    if errors:
        raise SystemExit("unsupported reproduction environment: " + "; ".join(errors))
    return {
        "operating_system": platform.system(),
        "kernel_release": platform.release(),
        "python_implementation": platform.python_implementation(),
        "python_version": platform.python_version(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "reproduction")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="skip completed successful jobs in this output; use only an unchanged source tree",
    )
    args = parser.parse_args()
    environment = platform_preflight()
    out = args.output.resolve()
    if out == ROOT or out in ROOT.parents or out in [ROOT / "cases", ROOT / "results", ROOT / "src", ROOT / "tests", ROOT / "proofs"]:
        parser.error("output must not overwrite repository evidence or source")
    if out.exists() and any(out.iterdir()) and not args.resume:
        parser.error("output is not empty; use a new directory or --resume")
    out.mkdir(parents=True, exist_ok=True)
    results = out / "results"
    results.mkdir(exist_ok=True)
    logs = out / "logs"
    logs.mkdir(exist_ok=True)
    jobs = [
        ("construct", "src/construct.py", [str(out / "cases")]),
        ("campaign", "src/campaign.py", [str(out / "cases"), str(results)]),
        ("closure-candidates", "src/closure_search.py", [str(results / "closure_candidates.json")]),
        ("closure-check", "src/closure_checker.py", [str(results / "closure_candidates.json"), str(results / "closure_verification.json")]),
        ("probe-candidates", "src/probe_search.py", [str(results / "probe_candidates.json")]),
        ("probe-check", "src/probe_checker.py", [str(results / "probe_candidates.json"), str(results / "probe_verification.json")]),
        ("reversible", "src/reversible_oracle.py", [str(results / "reversible_verification.json")]),
        ("transport", "src/transport_oracle.py", [str(results / "transport_verification.json")]),
        ("tests", "tests/test_checker.py", []),
    ]
    measured = []
    for name, script, jobargs in jobs:
        metric = logs / (name + ".json")
        if args.resume and metric.exists() and json.loads(metric.read_text()).get("exit_code") == 0:
            record = json.loads(metric.read_text())
            record.update(job=name, resumed=True)
            measured.append(record)
            continue
        with (logs / (name + ".stdout.txt")).open("w") as stdout, (logs / (name + ".stderr.txt")).open("w") as stderr:
            proc = subprocess.Popen(
                [sys.executable, str(ROOT / "src/bounded_worker.py"), str(metric), str(ROOT / script), *jobargs],
                cwd=ROOT,
                stdout=stdout,
                stderr=stderr,
                start_new_session=True,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0"},
            )
            try:
                code = proc.wait(timeout=120)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
                code = 124
        if not metric.exists():
            metric.write_text(json.dumps({"exit_code": code, "measurement_complete": False}) + "\n")
        record = json.loads(metric.read_text())
        record.update(job=name, resumed=False)
        measured.append(record)
        print(name, code, flush=True)
        if code != 0 or record.get("exit_code") != 0:
            (out / "run.json").write_text(
                json.dumps(
                    {"success": False, "environment": environment, "jobs": measured},
                    indent=2,
                    sort_keys=True,
                )
                + "\n"
            )
            return 1

    # Scientific JSON and CSV are compared directly, never by a generated hash manifest.
    pairs = []
    for reference in sorted((ROOT / "cases").glob("*.json")):
        pairs.append((reference, out / "cases" / reference.name))
    names = [
        "case_verification.json",
        "campaign_summary.json",
        "case_summary.csv",
        "closure_candidates.json",
        "closure_verification.json",
        "probe_candidates.json",
        "probe_verification.json",
        "reversible_verification.json",
        "transport_verification.json",
    ]
    pairs += [(ROOT / "results" / name, results / name) for name in names]
    for reference, actual in pairs:
        if not actual.exists():
            raise RuntimeError("missing reproduced evidence: " + actual.name)
        same = (
            json.loads(reference.read_text()) == json.loads(actual.read_text())
            if reference.suffix == ".json"
            else reference.read_bytes() == actual.read_bytes()
        )
        if not same:
            raise RuntimeError("scientific evidence mismatch: " + reference.name)

    test_text = (logs / "tests.stderr.txt").read_text()
    test_match = re.search(r"Ran\s+(\d+)\s+tests?\b", test_text)
    if not test_match:
        raise RuntimeError("could not read the executed regression-test count")
    regression_tests = int(test_match.group(1))

    report = {
        "success": True,
        "environment": environment,
        "scientific_jobs": len(jobs),
        "regression_tests": regression_tests,
        "jobs": measured,
        "directly_compared_files": len(pairs),
        "cumulative_job_cpu_seconds": sum(x.get("cpu_seconds", 0) for x in measured),
        "maximum_job_peak_rss_kib": max(x.get("peak_rss_kib", 0) for x in measured),
        "timing_results_excluded_from_equality": True,
        "resume_used": args.resume,
        "note": "CPU covers these measured jobs, not all earlier interactive prototypes; clean runs must not use --resume.",
    }
    (out / "run.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "jobs"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
