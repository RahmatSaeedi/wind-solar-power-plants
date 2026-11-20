"""Chapter 22, section B - option appraisal: criteria and their scores,
weights from three stakeholders, dominance, how stable the ranking is
when the weights are uncertain, the weight at which the ranking flips,
and scores shrunk toward the middle when their evidence is weak.

Run from the project root:   python -m companion.ch22.lab_b
Writes companion/ch22/expected/b_*.txt and diagrams/data/ch22-*.csv.
Teaching values A-312.
"""
from __future__ import annotations

import numpy as np

from companion.ch22 import sources as src
from companion.ch22.common import csv, emit
from plantp import appraisal as ap

NAMES = list(src.SITES)

# [start: criteria]
CRITERIA = [  # (label, value function, higher is better, evidence key)
    ("energy", lambda f: f["energy"], True, "energy_q"),
    ("cost incl. grid", lambda f: f["capex"] + f["reinforce"], False, None),
    ("time to COD", lambda f: f["schedule"], False, None),
    ("grid readiness", lambda f: f["grid_free_mw"] - f["grid_km"], True, None),
    ("environment", lambda f: (-f["bird_overlap"] - 0.1 * f["heritage"]
                               - 0.2 * f["water_scarce"]), True, None),
    ("social", lambda f: -(f["households"] + 5 * f["displaced"]
                           + 0.5 * f["seasonal"]), True, None),
    ("constructability", lambda f: -(f["slope_pct"] + 0.3 * f["road_km"]),
     True, None),
]
WEIGHTS = {   # three stakeholder views (A-312, teaching)
    "developer": [0.30, 0.25, 0.15, 0.10, 0.05, 0.05, 0.10],
    "lender":    [0.20, 0.20, 0.15, 0.15, 0.10, 0.10, 0.10],
    "community": [0.10, 0.05, 0.05, 0.05, 0.30, 0.40, 0.05],
}
# [end: criteria]


def score_matrix() -> np.ndarray:
    cols = []
    for _, fn_, hib, _ in CRITERIA:
        cols.append(ap.normalise([fn_(src.SITES[n]) for n in NAMES], hib))
    return np.array(cols).T                  # sites x criteria


def scores() -> None:
    s = score_matrix()
    lines = ["normalised scores (1 = best of the three):",
             "  criterion          " + "".join(f"{n:>11s}" for n in NAMES)]
    for k, (lab, *_rest) in enumerate(CRITERIA):
        lines.append(f"  {lab:18s} " + "".join(f"{s[i, k]:11.2f}" for i in range(len(NAMES))))
    lines.append("  weighted totals by stakeholder:")
    rows = []
    for who, w in WEIGHTS.items():
        tot = ap.weighted(s, w)
        lines.append(f"  {who:18s} " + "".join(f"{t:11.2f}" for t in tot))
        rows.append((who, *[f"{t:.3f}" for t in tot]))
    dom = ap.dominated(s)
    lines += [f"  dominated options: {', '.join(NAMES[i] for i in dom) or 'none'}",
              "  min-max scores exaggerate small differences between three",
              "  options and depend on which options are in the set: the",
              "  total is a summary for discussion, not a measurement"]
    emit("b_scores", lines)
    csv("ch22-scores.csv", "who,north,central,south", rows)


def flip_weight(who: str = "developer") -> float | None:
    """Energy weight at which P-North ranks first (the other weights
    keep their proportions)."""
    s = score_matrix()
    w0 = np.array(WEIGHTS[who], float)
    for we in np.arange(0.30, 0.95, 0.01):
        w = w0.copy()
        w[0] = we
        w[1:] = w0[1:] / w0[1:].sum() * (1 - we)
        if NAMES[int(np.argmax(ap.weighted(s, w)))] == "P-North":
            return float(we)
    return None


def stability() -> None:
    s = score_matrix()
    lines = ["how often each site ranks first when the weights are uncertain",
             "(5,000 random weight sets around each stakeholder's view):",
             "  stakeholder        " + "".join(f"{n:>11s}" for n in NAMES)]
    for who, w in WEIGHTS.items():
        share = ap.rank_stability(s, w)
        lines.append(f"  {who:18s} " + "".join(f"{x * 100:10.0f}%" for x in share))
    flip = flip_weight()
    lines += [f"  the developer's ranking turns to P-North only when energy weighs"
              f" {flip * 100:.0f} %" if flip else "  P-North never ranks first",
              "  a ranking that survives most plausible weights is robust;",
              "  one that needs a single extreme weight is an argument"]
    emit("b_stability", lines)


def evidence() -> None:
    s = score_matrix().copy()
    q = np.array([src.SITES[n]["energy_q"] for n in NAMES])
    s_adj = s.copy()
    s_adj[:, 0] = ap.quality_adjusted(s[:, 0], q)
    w = WEIGHTS["developer"]
    lines = ["the energy score shrunk toward 0.5 by the quality of its evidence:",
             "  site        quality   energy score   adjusted   developer total"]
    tot0, tot1 = ap.weighted(s, w), ap.weighted(s_adj, w)
    for i, n in enumerate(NAMES):
        lines.append(f"  {n:10s} {q[i]:8.1f}   {s[i, 0]:12.2f}   {s_adj[i, 0]:8.2f}"
                     f"   {tot0[i]:.2f} -> {tot1[i]:.2f}")
    lines += ["  P-North's energy lead rests on reanalysis and four months",
              "  of mast data: until a full campaign (ch 13) confirms it, it",
              "  counts for less; quality is recorded beside every score"]
    emit("b_evidence", lines)


if __name__ == "__main__":
    scores()
    stability()
    evidence()
