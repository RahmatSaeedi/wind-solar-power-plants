"""Chapter 59: rebuild the whole capstone dossier in one run - verify the
data pack, run every chapter-59 script in order, and report what was
produced. The dossier is reproducible when this run gives the same files.

Run from the project root:   python -m companion.ch59.run_all
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import time

from companion.ch59 import common  # noqa: F401  (path)
from companion.ch59.common import EXPECTED, emit

# [start: order]
ORDER = ["index", "dossier", "defense", "cases", "cases2", "cases3", "cases4",
         "cases5", "cases6", "cases7", "cases8", "cases9", "integrated",
         "sheets"]
# [end: order]


def digest() -> str:
    h = hashlib.sha256()
    for f in sorted(EXPECTED.glob("*.txt")):
        if f.name == "x_run.txt":
            continue
        h.update(f.name.encode())
        h.update(f.read_bytes())
    return h.hexdigest()[:12]


def main() -> dict:
    from plantp import datapack
    import importlib
    problems = datapack.verify()
    t0 = time.time()
    with contextlib.redirect_stdout(io.StringIO()):
        for name in ORDER:
            importlib.import_module(f"companion.ch59.{name}").main()
    first = digest()
    with contextlib.redirect_stdout(io.StringIO()):
        for name in ("index", "dossier", "defense"):
            importlib.import_module(f"companion.ch59.{name}").main()
    second = digest()
    n = len([f for f in EXPECTED.glob("*.txt") if f.name != "x_run.txt"])
    lines = ["rebuilding the capstone dossier in one run",
             f"  data pack {datapack.DATA_RELEASE}: {len(problems)} checksum problems",
             f"  scripts run in order: {', '.join(ORDER)}",
             f"  outputs: {n} text files; digest {first}",
             f"  second run of the core scripts: digest {second}"
             f" ({'same' if first == second else 'DIFFERENT'})",
             "  same inputs, same seeds, same files: the dossier is reproducible;",
             "  a changed digest names a changed input or model"]
    emit("x_run", lines)
    return dict(problems=len(problems), n=n, same=first == second, secs=time.time() - t0)


if __name__ == "__main__":
    main()
