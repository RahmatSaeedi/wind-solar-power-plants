"""A simple build-and-test pipeline for the chapter 5 tools: run it before
every release, and let a machine run it on every change.

    python -m companion.ch05.check_all

Stages (each must pass before the next): data integrity, generator
reproducibility, automated tests, regression against the stored reference.
Exit code 0 only when everything passes.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / "companion" / "ch05" / "reference_S0.json"


# [start: pipeline]
def stage(name, ok, detail=""):
    tail = f" - {detail}" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{tail}")
    return ok


def main():
    from plantp import datapack
    from companion.ch05.resource_tool import run
    ok = stage("data pack checksums",
               not datapack.verify("1.0.0") and not datapack.verify("1.1.0"))
    for rel in ("1.0.0", "1.1.0") if ok else ():
        p = subprocess.run([sys.executable, "companion/plantp_data/"
                            "generate_release.py", "--release", rel,
                            "--check"],
                           cwd=ROOT, capture_output=True, text=True)
        ok = stage(f"generator reproduces {rel}", p.returncode == 0,
                   p.stdout.strip()) and ok
    if ok:
        p = subprocess.run([sys.executable, "-m", "pytest", "-p",
                            "no:cacheprovider",
                            "companion/tests/test_ch05_tool.py",
                            "companion/tests/test_ch05_modules.py"],
                           cwd=ROOT, capture_output=True, text=True)
        m = re.search(r"(\d+) passed", p.stdout)
        ok = stage("unit and property tests", p.returncode == 0,
                   f"{m.group(1) if m else 0} passed")
    if ok:
        res, _ = run.run(run.load_config(
            ROOT / "companion/ch05/config/run_S0.yml"))
        ref = json.loads(REFERENCE.read_text(encoding="utf-8"))
        diff = {k: (ref[k], res[k]) for k in ref if res.get(k) != ref[k]}
        ok = stage("regression against reference_S0.json", not diff,
                   f"differences {diff}" if diff else f"{len(ref)} values")
    print("RESULT:", "release may proceed" if ok else "STOP - fix first")
    return 0 if ok else 1
# [end: pipeline]


if __name__ == "__main__":
    sys.exit(main())
