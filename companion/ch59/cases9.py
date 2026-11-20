"""Chapter 59: the dossier's documents by discipline and type, and the
documents, unknowns and decisions of each Part of the book.

Run from the project root:   python -m companion.ch59.cases9
"""
from __future__ import annotations

from collections import Counter

from companion.ch59 import common  # noqa: F401  (path)
from companion.ch59.common import emit
from companion.ch59 import sources as src

PARTS = [("I", 1, 5), ("II", 6, 11), ("III", 12, 16), ("IV", 17, 22), ("V", 23, 28),
         ("VI", 29, 33), ("VII", 34, 37), ("VIII", 38, 50), ("IX", 51, 53), ("X", 54, 59)]
DISC = ["PRJ", "GEN", "ELE", "CTL", "CIV", "MEC"]
TYPES = ["REP", "REG", "SPC", "CAL", "PRO", "DWG", "LST"]


def all_docs() -> list[str]:
    docs = set()
    for n in range(1, 60):
        docs.update(src.records(n)["docs"])
    return sorted(docs)


def j_docs() -> dict:
    docs = all_docs()
    c = Counter((d.split("-")[1], d.split("-")[2]) for d in docs)
    lines = [f"documents of the dossier by discipline and type ({len(docs)} documents)",
             "  " + "disc".ljust(5) + "".join(f"{t:>5s}" for t in TYPES) + "  total"]
    tot_t = Counter()
    by_d = {}
    for d in DISC:
        row = [c[(d, t)] for t in TYPES]
        by_d[d] = sum(row)
        for t, v in zip(TYPES, row):
            tot_t[t] += v
        lines.append("  " + d.ljust(5) + "".join(f"{v:5d}" for v in row) + f"  {sum(row):5d}")
    lines.append("  " + "all".ljust(5) + "".join(f"{tot_t[t]:5d}" for t in TYPES)
                 + f"  {sum(tot_t.values()):5d}")
    other = len(docs) - sum(tot_t.values())
    top_d = max(by_d, key=by_d.get)
    top_t = max(tot_t, key=tot_t.get)
    lines += [f"  other kinds: {other}",
              f"  most documents: discipline {top_d} ({by_d[top_d]}), type {top_t}"
              f" ({tot_t[top_t]}); registers and",
              f"  reports together {tot_t['REG'] + tot_t['REP']} of {len(docs)}"
              f" ({(tot_t['REG'] + tot_t['REP']) / len(docs):.0%})"]
    emit("j_docs", lines)
    return dict(n=len(docs), by_d=by_d, by_t=dict(tot_t), other=other)


def a_parts() -> dict:
    lines = ["documents, unknowns and decisions by Part of the book",
             f"  {'Part':5s} {'chapters':>9s} {'docs':>5s} {'unknowns':>8s} {'decisions':>9s}"]
    rows = []
    for name, a, b in PARTS:
        chs = list(range(a, b + 1))
        docs, unk = set(), set()
        for n in chs:
            r = src.records(n)
            docs.update(r["docs"])
            unk.update(r["unknowns"])
        dec = src.decisions_of(chs)
        rows.append((name, len(chs), len(docs), len(unk), len(dec)))
        lines.append(f"  {name:5s} {f'{a}-{b}':>9s} {len(docs):5d} {len(unk):8d} {len(dec):9d}")
    per = [(r[0], r[2] / r[1]) for r in rows]
    top = max(per, key=lambda x: x[1])
    lines += [f"  documents per chapter highest in Part {top[0]} ({top[1]:.1f});",
              "  a document named in two Parts is counted in each"]
    emit("a_parts", lines)
    return dict(rows=rows, top=top)


def main() -> dict:
    return dict(j_docs=j_docs(), a_parts=a_parts())


if __name__ == "__main__":
    main()
