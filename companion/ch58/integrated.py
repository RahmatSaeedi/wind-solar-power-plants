"""Chapter 58, three integrated examples for Plant P: numbers by hand, the
register readiness review and the basis D-062.

Run from the project root:   python -m companion.ch58.integrated
Writes companion/ch58/expected/int_*.txt.
"""
from __future__ import annotations

import contextlib
import io

from companion.ch58 import run
from companion.ch58 import sources as src
from companion.ch58.common import emit


def main() -> None:
    with contextlib.redirect_stdout(io.StringIO()):
        r = run.main()
    from companion.ch43 import sources as s43
    from plantp import xfmrdesign as xd
    T = s43.TESTS
    r0 = xd.cooling_curve(T["cool_t_min"], T["cool_r_hv"])["r0"]
    n = r["register"]["n"]
    op = r["open_items"]["n"]
    v = r["verbal"]
    emit("int_hand", [
        "three numbers by hand",
        f"  open items: {op} / {n} = {op / n:.0%}",
        f"  requirements that cannot be verified: {v['vague']} / {v['req']}",
        f"  winding rise: {r0:.4f} / {T['r_hv_ohm']} x (235 + {T['r_temp_c']:.0f})"
        f" - 235 - {T['ambient_c']:.0f} = "
        f"{r0 / T['r_hv_ohm'] * (235 + T['r_temp_c']) - 235 - T['ambient_c']:.1f} K"])
    checks = [
        ("every row has the nine required fields", True),
        ("every row has an official catalogue source", True),
        ("duplicates merged", False),
        ("open items (confirm) closed", False),
        ("national adoption checked for the project country", False),
        ("editions in the specification dated on purpose", True),
        ("requirements free of vague words", False),
        ("certificates checked against edition and lab scope", True),
        ("one clause traced to approval, register and trigger", True),
        ("edition-change impact links kept for every requirement", False),
        ("watch plan with intervals and an owner", True),
        ("standard texts bought for the clauses the project uses", False),
    ]
    ok = sum(x for _, x in checks)
    emit("int_review", ["Plant P standards register: readiness for a project on " + str(src.TODAY)]
         + [f"  [{'x' if x else ' '}] {t}" for t, x in checks]
         + [f"  {ok} of {len(checks)}: the register is complete as a list; as a",
            "  project tool it still needs merged duplicates, closed open",
            "  items, country adoption and the texts themselves"])
    emit("int_basis", [
        "standards basis of Plant P (D-062):",
        f"  1 one register ({n} rows), nine required fields, an official",
        "    catalogue source and a verification date on every row",
        "  2 no standard is cited as law: legal force comes from a law, a",
        "    grid code or the contract that names it (ch 54-57)",
        "  3 specifications cite dated editions; an undated reference only",
        "    where the latest edition is wanted on purpose",
        "  4 requirements use 'shall' with a value and a test; vague words",
        "    are removed before issue",
        "  5 a certificate counts only for the same model, edition and an",
        "    accredited scope; an older edition triggers a gap analysis",
        "  6 every requirement keeps its trace to approval, register entry",
        "    and change trigger; an edition change runs the impact list",
        "  7 watch: open items monthly, linked or hub rows twice a year,",
        "    the rest yearly",
        "  8 clause texts are bought and read for the project; the book's",
        "    register gives titles and editions, not content"])


if __name__ == "__main__":
    main()
