"""Chapter 59: the three country appendices summarised by the ch 55 engine
(status, approval plan, open items, top risks).

Run from the project root:   python -m companion.ch59.cases5
"""
from __future__ import annotations

import importlib

from companion.ch59 import common  # noqa: F401  (path)
from companion.ch59.common import emit


def country(name: str, n: int) -> dict:
    from companion.ch55 import engine as en
    src = importlib.import_module(f"companion.ch{n}.sources")
    more = importlib.import_module(f"companion.ch{n}.more")
    quiet = lambda *a, **k: None
    st = en.status_table(src, quiet)
    ap = en.approvals(src, quiet)
    iss = en.issues(src, quiet)
    g = en.grid_gaps(src, quiet)
    tot = st["tot"]
    nf = len(src.FACTS)
    top = sorted(more.RISKS, key=lambda r: -(r[3] * r[4]))
    big = [r for r in top if r[3] * r[4] >= 16]
    lines = [f"{name} appendix (ch {n}): {nf} statements, {tot['verified']} verified"
             f" ({tot['verified'] / nf:.0%}), {tot['project-dependent']} project-dependent,"
             f" {tot['to-confirm']} to-confirm",
             f"  approval plan {ap['total']:.1f} months (teaching); critical path"
             f" {' > '.join(ap['crit'])}",
             f"  unverified on the critical path: {', '.join(ap['tcc']) or 'none'}",
             f"  grid-study inputs from public sources: {g['complete']:.0%}",
             f"  open items: {sum(iss.values())} to {len(iss)} addressees",
             "  risks scored 16 or more:"]
    lines += [f"    {r[0]} {r[1][:58]}" for r in big]
    emit(f"y_{name.lower()}", lines)
    return dict(n=nf, ver=tot["verified"], months=ap["total"], open=sum(iss.values()),
                big=[r[0] for r in big])


def main() -> dict:
    return {nm: country(nm, n) for nm, n in (("Iran", 55), ("Afghanistan", 56),
                                              ("Tajikistan", 57))}


if __name__ == "__main__":
    main()
