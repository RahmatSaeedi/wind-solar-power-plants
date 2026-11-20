"""Shared helpers for the chapter 7 scripts: wrapped text outputs and plot-data CSVs."""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPECTED = HERE / "expected"
DATA = HERE.parents[1] / "diagrams" / "data"
sys.path.insert(0, str(HERE.parents[0]))


def emit(name: str, lines: list[str]) -> None:
    EXPECTED.mkdir(exist_ok=True)
    wrapped = []
    for line in lines:
        wrapped += textwrap.wrap(line, 78, subsequent_indent="    ") or [""]
    text = "\n".join(wrapped) + "\n"
    (EXPECTED / f"{name}.txt").write_text(text, encoding="utf-8", newline="\n")
    print(f"== {name}\n{text}")


def csv(name: str, header: str, rows) -> None:
    with open(DATA / name, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(header + "\n")
        for row in rows:
            fh.write(",".join(str(x) for x in row) + "\n")
