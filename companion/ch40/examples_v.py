"""Chapter 40, a fourth round: reviewing calibration certificates, the
capability of crimp pull force with its histogram, variables sampling
against attribute sampling, a two-level factorial experiment on the
crimp, where yield improvement pays most, the first-article package of
the bought frames, and stress-strength interference of a lifting lug.

Run from the project root:   python -m companion.ch40.examples_v
Writes companion/ch40/expected/v_*.txt and diagrams/data/ch40-*.csv.
Teaching values (A-435 to A-441); a fictional integrator; the crimp
factors are named generically, never as machine settings.
"""
from __future__ import annotations

import math
import random
from statistics import mean, stdev

from companion.ch40 import sources as src
from companion.ch40.common import csv, emit
from plantp import quality as qa

# ---------------------------------------------- calibration certificates
CERTS = [  # instrument, valid to day, range covers use?, uncertainty given?,
    #        traceable to a national standard?, conformity rule stated?
    ("TW-11 torque wrench", 60, True, True, True, True),
    ("TW-14 torque wrench", 30, True, True, True, True),
    ("IR-03 insulation tester", 17, True, True, True, False),
    ("MO-01 micro-ohmmeter", 90, False, True, True, True),
    ("SI-02 relay test set", 40, True, False, True, True),
    ("DFT-02 coating gauge", 45, True, True, False, True),
]


def certificates(today: int = 20) -> dict[str, list[str]]:
    lines = [f"calibration certificates reviewed on day {today}"]
    out = {}
    for name, valid, rng, unc, trace, rule in CERTS:
        f = []
        if valid < today:
            f.append("expired")
        if not rng:
            f.append("range does not cover the use")
        if not unc:
            f.append("no uncertainty")
        if not trace:
            f.append("no traceability")
        if not rule:
            f.append("no conformity rule")
        out[name] = f
        lines.append(f"  {name:24s} {'ok' if not f else '; '.join(f)}")
    bad = [k for k, v in out.items() if v]
    lines += [f"  certificates with a finding: {len(bad)} of {len(CERTS)}",
              "  a certificate is evidence only if it covers the range used,",
              "  states its uncertainty and traceability, and says how the",
              "  pass was decided; 'calibrated' alone is a declaration"]
    emit("v_certs", lines)
    return out


# ------------------------------------------- crimp pull-force capability
def pull_force(seed: int = 401) -> list[float]:
    rng = random.Random(seed)
    return [round(rng.gauss(5.2, 0.28), 2) for _ in range(60)]   # kN


def crimp_capability() -> dict[str, float]:
    f = pull_force()
    lsl = 4.4                                   # kN, lug maker's minimum
    m, s, _, cpk = qa.cp_cpk(f, lsl, None)
    ppm = qa.ppm_out(m, s, lsl, None)
    edges = [round(4.4 + 0.1 * k, 1) for k in range(0, 17)]
    counts = [sum(edges[k] <= x < edges[k + 1] for x in f)
              for k in range(len(edges) - 1)]
    csv("ch40-pull.csv", "lo,count", list(zip(edges[:-1], counts)))
    lines = [f"crimp pull force of 60 lugs (lower limit {lsl} kN)",
             f"  mean {m:.2f} kN, sd {s:.2f} kN; Cpk {cpk:.2f}; "
             f"{ppm:,.0f} ppm under",
             f"  Cpk {cpk:.2f} is below 1.33: about {ppm / 1000:.1f} crimps in 1,000",
             "  under the minimum - the mean must rise (the factorial below",
             "  shows how); one-sided, since a stronger crimp is no defect;",
             "  the pull test is destructive, so it runs on samples at each",
             "  die change and shift, and the die check guards the rest"]
    emit("v_pull", lines)
    return dict(mean=m, sd=s, cpk=cpk, ppm=ppm)


# ------------------------------------- variables vs attributes sampling
def variables_plan(aql: float, ltpd: float, alpha: float = 0.05,
                   beta: float = 0.10) -> tuple[int, float]:
    """Sample size and acceptance constant k of a variables plan with
    known-sigma style approximation (textbook formula)."""
    z = lambda p: -_ppf(p)                      # noqa: E731
    za, zb = _ppf(1 - alpha), _ppf(1 - beta)
    z1, z2 = z(aql), z(ltpd)
    k = (z2 * za + z1 * zb) / (za + zb)
    n = math.ceil(((za + zb) / (z1 - z2)) ** 2 * (1 + k * k / 2))
    return n, k


def _ppf(q: float) -> float:
    lo, hi = -10.0, 10.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if qa.phi(mid) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def sampling_compare() -> dict[str, float]:
    n_attr, c = qa.find_plan(0.01, 0.05)
    n_var, k = variables_plan(0.01, 0.05)
    lines = ["frame width: variables plan against the attribute plan",
             "  (AQL 1 %, LTPD 5 %, producer's risk 5 %, consumer's 10 %)",
             f"  attribute plan: n = {n_attr}, accept if <= {c} out of limits",
             f"  variables plan: n = {n_var}, accept if (limit - mean)/s >= "
             f"{k:.2f}",
             "  measuring the width, not only judging in/out, carries more",
             f"  information per frame: the same protection with {n_var / n_attr:.0%}",
             "  of the samples - if the width is normal and well measured"]
    emit("v_varsample", lines)
    return dict(n_attr=n_attr, n_var=n_var, k=k)


# ------------------------------------------- two-level factorial on the crimp
# [start: doe]
RUNS = {  # (factor A, factor B): pull force kN, two repeats - A-436
    (-1, -1): [4.71, 4.79], (+1, -1): [5.12, 5.20],
    (-1, +1): [4.98, 5.04], (+1, +1): [5.86, 5.78],
}
# A: die closing force low/high; B: wire insertion depth short/full
# [end: doe]


def factorial() -> dict[str, float]:
    m = {k: mean(v) for k, v in RUNS.items()}
    a = (m[(1, -1)] + m[(1, 1)] - m[(-1, -1)] - m[(-1, 1)]) / 2
    b = (m[(-1, 1)] + m[(1, 1)] - m[(-1, -1)] - m[(1, -1)]) / 2
    ab = (m[(1, 1)] + m[(-1, -1)] - m[(1, -1)] - m[(-1, 1)]) / 2
    rep_sd = math.sqrt(mean(stdev(v) ** 2 for v in RUNS.values()))
    se = rep_sd / math.sqrt(2)                  # effect of 8 runs: 2s/sqrt(8)
    csv("ch40-doe.csv", "b,a_low,a_high",
        [(-1, m[(-1, -1)], m[(1, -1)]), (1, m[(-1, 1)], m[(1, 1)])])
    lines = ["2 x 2 factorial on crimp pull force (two repeats a run)",
             "  factor A: die closing force; factor B: insertion depth",
             f"  effect of A {a:+.2f} kN; of B {b:+.2f} kN; interaction AB "
             f"{ab:+.2f} kN",
             f"  repeat sd {rep_sd:.3f} kN; standard error of an effect "
             f"{se:.3f} kN",
             "  all three effects are many standard errors from zero: the",
             "  interaction says depth matters most when the force is high -",
             "  one factor at a time would have missed it; the result sets",
             "  the control-plan check, not a machine recipe"]
    emit("v_doe", lines)
    return dict(a=a, b=b, ab=ab, se=se)


# ------------------------------------------- where yield improvement pays
def yield_priority() -> list[tuple[str, float]]:
    base = qa.rty([r[4] for r in src.ROUTE])
    gains = []
    for k, (op, work, *_r) in enumerate(src.ROUTE):
        ys = [r[4] for r in src.ROUTE]
        if ys[k] >= 1.0:
            continue
        ys[k] = min(1.0, ys[k] + 0.02)
        gains.append((f"{op} {work}", qa.rty(ys) - base))
    gains.sort(key=lambda t: -t[1])
    lines = [f"rolled throughput yield {base:.3f}: two points more at one step",
             "  step                                        RTY gain"]
    for name, g in gains[:5]:
        lines.append(f"  {name:43s} {g:+.4f}")
    lines += ["  every step gives about the same gain per point (yields",
              "  multiply), so the choice is made on cost and on what the",
              "  failures are: FAT finds faults made earlier, so the line",
              "  steps that make them (OP60, OP40) come first"]
    emit("v_yield", lines)
    return gains


# ------------------------------------------- first-article package of frames
FAI = {  # item: delivered with the first frame?
    "dimensional report against the drawing": True,
    "material certificates (steel grade)": True,
    "weld procedure and welder qualifications": True,
    "coating thickness report": True,
    "process flow and control plan": False,
    "capability of key dimensions": False,
    "measurement-system study of the gauge": False,
    "lift-lug load test": True,
}


def first_article() -> dict[str, int]:
    missing = [k for k, v in FAI.items() if not v]
    lines = ["first-article package of the bought frames"]
    for k, v in FAI.items():
        lines.append(f"  {'[x]' if v else '[ ]'} {k}")
    lines += [f"  {len(missing)} of {len(FAI)} missing - the first frame passes,",
              "  but the process behind it is not yet shown: release for",
              "  the order waits for the control plan and the capability"]
    emit("v_fai", lines)
    return dict(missing=len(missing))


# --------------------------------------- stress-strength of a lifting lug
def stress_strength() -> dict[str, float]:
    load_m, load_s = 148.0, 15.0            # kN a leg (lesson F, scatter)
    rows, out = [], {}
    lines = ["lifting lug: chance that load exceeds strength (both normal)",
             f"  load a leg {load_m:.0f} kN (sd {load_s:.0f})",
             "  strength mean  sd   safety factor  chance of failure"]
    for s_m, s_s in ((250.0, 25.0), (300.0, 25.0), (300.0, 50.0)):
        z = (s_m - load_m) / math.sqrt(s_s ** 2 + load_s ** 2)
        p = 1 - qa.phi(z)
        out[(s_m, s_s)] = p
        lines.append(f"  {s_m:13.0f}  {s_s:3.0f}  {s_m / load_m:13.2f}  "
                     f"{p:17.2e}")
    for x in range(100, 401, 5):
        f_load = math.exp(-0.5 * ((x - load_m) / load_s) ** 2) / (load_s * 2.5066)
        f_str = math.exp(-0.5 * ((x - 300) / 50.0) ** 2) / (50.0 * 2.5066)
        rows.append((x, round(f_load * 1000, 4), round(f_str * 1000, 4)))
    csv("ch40-stress.csv", "x,load,strength", rows)
    ratio = out[(300.0, 50.0)] / out[(300.0, 25.0)]
    lines += [f"  the same safety factor (2.0) gives {ratio:,.0f} times the",
              "  risk when the strength scatters twice as much: a safety",
              "  factor without the scatter says little - the lift lug's",
              "  load test in the first-article package measures it"]
    emit("v_stress", lines)
    return out


if __name__ == "__main__":
    certificates()
    crimp_capability()
    sampling_compare()
    factorial()
    yield_priority()
    first_article()
    stress_strength()
