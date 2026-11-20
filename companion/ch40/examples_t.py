"""Chapter 40, further lessons on quality statistics and problem solving:
agreement of visual inspectors (Cohen's kappa), an uncertainty budget for
joint resistance, a p-chart of FAT first-pass failures, a confidence
interval for Cpk, the average outgoing quality of rectifying inspection,
a Pareto chart of FAT findings, the 8D record of the torque event, a
warranty-cost forecast from the field Weibull, and an MTBF interval from
fleet hours.

Run from the project root:   python -m companion.ch40.examples_t
Writes companion/ch40/expected/t_*.txt and diagrams/data/ch40-*.csv.
Teaching values (A-436 to A-440); a fictional integrator.
"""
from __future__ import annotations

import math

from scipy import stats

from companion.ch40 import sources as src  # noqa: F401  (plantp on path)
from companion.ch40.common import csv, emit
from plantp import quality as qa


# ----------------------------------------------- inspectors' agreement
# [start: kappa]
def kappa(a, b) -> float:
    """Cohen's kappa of two raters' pass/fail calls."""
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return (po - pe) / (1 - pe)
# [end: kappa]


def agreement() -> dict[str, float]:
    # 40 crimp samples, 1 = pass; inspector B is lenient on borderline ones
    ref = [1] * 28 + [0] * 12
    a = ref[:]
    b = ref[:]
    for k in (28, 29, 30, 31):              # four borderline fails passed by B
        b[k] = 1
    a[5] = 0                                 # A fails one good crimp
    ka, kb = kappa(a, ref), kappa(b, ref)
    kab = kappa(a, b)
    lines = ["visual inspection of crimps: do the inspectors agree?",
             "  40 crimps, 12 bad by the cross-section reference",
             f"  inspector A vs reference: kappa {ka:.2f}",
             f"  inspector B vs reference: kappa {kb:.2f} (passes 4 bad ones)",
             f"  A vs B: kappa {kab:.2f}",
             "  a common guide reads kappa above 0.75 as good agreement;",
             "  B's misses are all borderline crimps - the boundary",
             "  samples and the reference photos go to the workstation"]
    emit("t_kappa", lines)
    return dict(a=ka, b=kb, ab=kab)


# ------------------------------------------------ uncertainty budget
BUDGET = [  # contribution, standard uncertainty (micro-ohm), basis (A-436)
    ("meter calibration", 0.10, "certificate, k = 2 halved"),
    ("resolution", 0.03, "0.1 / sqrt(12)"),
    ("probe placement", 0.11, "GRR with fixture, repeatability"),
    ("inspectors", 0.16, "GRR with fixture, reproducibility"),
    ("temperature of joint", 0.08, "+/- 5 C, copper coefficient"),
]


def uncertainty() -> dict[str, float]:
    uc = math.sqrt(sum(u * u for _, u, _ in BUDGET))
    U = 2 * uc
    lines = ["uncertainty budget of a joint-resistance reading (micro-ohm)",
             "  contribution            u      basis"]
    for name, u, basis in BUDGET:
        lines.append(f"  {name:22s} {u:5.2f}   {basis}")
    big = max(BUDGET, key=lambda r: r[1])
    lines += [f"  combined {uc:.2f}; expanded (k = 2) {U:.2f}",
              f"  largest: {big[0]} - the next improvement is training,",
              "  not a better meter; the mean joint (12.4) sits",
              f"  {(20 - 12.4) / U:.0f} times U below the limit of 20, so readings",
              "  near the limit, not typical ones, need the guard band"]
    emit("t_budget", lines)
    return dict(uc=uc, U=U)


# ------------------------------------------------------- p-chart
WEEKS = [(12, 1), (14, 1), (13, 1), (12, 0), (15, 2), (13, 1), (12, 1),
         (14, 1), (13, 6), (12, 1)]          # (tests, first-pass failures)


def p_chart() -> dict:
    n_tot = sum(n for n, _ in WEEKS)
    pbar = sum(f for _, f in WEEKS) / n_tot
    rows, out = [], []
    for k, (n, f) in enumerate(WEEKS, 1):
        sig = math.sqrt(pbar * (1 - pbar) / n)
        ucl = pbar + 3 * sig
        p = f / n
        rows.append((k, round(p, 4), round(ucl, 4)))
        if p > ucl:
            out.append(k)
    csv("ch40-pchart.csv", "week,p,ucl", rows)
    rest = [(n, f) for k, (n, f) in enumerate(WEEKS, 1) if k not in out]
    p_rest = sum(f for _, f in rest) / sum(n for n, _ in rest)
    lines = ["p-chart of FAT first-pass failures (skid line and panels)",
             f"  {n_tot} tests in 10 weeks; mean failure share {pbar:.3f}",
             f"  weeks above the upper limit: {', '.join(map(str, out))}",
             "  the limits move with each week's number of tests; week 9",
             "  (6 of 13) is a signal - a new panel supplier started that",
             f"  week; without it the share is {p_rest:.1%}, the 92 % FAT",
             "  yield of lesson A; limits are recomputed once the cause is",
             "  removed, not before"]
    emit("t_pchart", lines)
    return dict(pbar=pbar, out=out)


# ------------------------------------------- confidence interval of Cpk
def cpk_interval() -> dict[str, float]:
    good = [x for s in src.SERIALS if s not in ("S-05", "S-06", "S-07")
            for x in src.RESIST[s]]
    _, _, _, cpk = qa.cp_cpk(good, None, 20.0)
    n = len(good)
    z = 1.645
    half = z * math.sqrt(1 / (9 * n) + cpk ** 2 / (2 * (n - 1)))
    ten = cpk - z * math.sqrt(1 / 90 + cpk ** 2 / 18)
    lines = [f"how sure is Cpk {cpk:.2f} from {n} joints? (normal approximation)",
             f"  95 % lower bound: {cpk - half:.2f}",
             "  with 35 joints the lower bound is still above 1.33; with",
             f"  ten joints it would be {ten:.2f} - a capability claim",
             "  needs its sample size"]
    emit("t_cpkci", lines)
    return dict(cpk=cpk, lower=cpk - half)


# ------------------------------------------ average outgoing quality
def aoq() -> dict[str, float]:
    n, c, N = 132, 3, 2000
    rows, peak = [], (0.0, 0.0)
    for k in range(0, 101):
        p = k / 1000
        a = qa.p_accept(n, c, p)
        q = a * p * (N - n) / N
        rows.append((round(p * 100, 1), round(q * 100, 4)))
        peak = max(peak, (q, p))
    csv("ch40-aoq.csv", "p,aoq", rows)
    lines = ["average outgoing quality of rectifying inspection",
             "  (n = 132, c = 3; a rejected lot of 2,000 is sorted 100 %)",
             f"  worst average outgoing quality: {peak[0]:.2%} at "
             f"{peak[1]:.1%} incoming",
             "  good lots pass; bad lots are sorted clean; in between the",
             "  plan lets through at most this share on average - the",
             "  limit is a property of the plan, not of the supplier"]
    emit("t_aoq", lines)
    return dict(aoql=peak[0], at=peak[1])


# --------------------------------------------------- Pareto of findings
FINDINGS = {  # FAT findings over the ten skids by category (A-438)
    "control wiring": 9, "labels and documents": 6, "LV terminations": 5,
    "earth bonds": 2, "paint damage": 2, "relay settings": 1, "other": 1}


def pareto() -> dict[str, float]:
    total = sum(FINDINGS.values())
    cum, rows, lines = 0, [], [f"Pareto of {total} FAT findings on ten skids"]
    for k, (name, v) in enumerate(sorted(FINDINGS.items(),
                                         key=lambda t: -t[1]), 1):
        cum += v
        rows.append((k, v, round(100 * cum / total, 1)))
        lines.append(f"  {name:22s} {v:3d}  cumulative {cum / total:4.0%}")
    csv("ch40-pareto.csv", "k,count,cum", rows)
    lines += ["  three categories hold 77 % of findings; control wiring is",
              "  first - the drawing-revision cause of the FMEA (ch 38) - but",
              "  the costliest finding was one LV termination: count and",
              "  consequence are ranked apart"]
    emit("t_pareto", lines)
    return dict(total=total)


# ------------------------------------------------------------ 8D record
EIGHT_D = [
    ("D1 team", "quality lead, line supervisor, test engineer, owner's QA"),
    ("D2 problem", "LV busbar joint overheated on S-06 in July"),
    ("D3 containment", "S-05 and S-07 measured and re-torqued on site"),
    ("D4 root cause", "dropped wrench; missed checks had no hold; no"
     " resistance at FAT"),
    ("D5 actions chosen", "shift check with hold; paint marks; resistance"
     " at FAT"),
    ("D6 actions done", "procedure rev C; meters bought; ITP updated"),
    ("D7 prevent recurrence", "FMEA detection re-rated; same rule for all"
     " torque tools and crimp dies"),
    ("D8 close", "three months of checks logged; team recognised"),
]


def eight_d() -> dict[str, int]:
    lines = ["the 8D record of the torque event"]
    for k, v in EIGHT_D:
        lines += [f"  {k}", f"      {v}"]
    lines += ["  D7 is the step most often skipped: the fix for TW-14 is",
              "  extended to every tool and die that could fail the same",
              "  way, so the next event does not need an 8D of its own"]
    emit("t_8d", lines)
    return dict(steps=len(EIGHT_D))


# ------------------------------------ warranty cost from the field Weibull
def warranty_cost() -> dict[str, float]:
    from companion.ch40.examples_e import RETURNS, RUNNING
    from plantp import performance as pf
    k_shape, lam = pf.weibull_mle(RETURNS, RUNNING)   # the fit of lesson E
    units, months, cost = 60, 24, 3.5     # parts in the fleet; k u a claim
    h = months * 730.0
    p_fail = 1 - math.exp(-((h / lam) ** k_shape))
    exp_claims = units * p_fail
    lines = ["warranty cost forecast from the field Weibull (lesson E)",
             f"  {units} parts, {months}-month workmanship warranty, "
             f"{cost} k u a claim",
             f"  chance a part fails in the warranty: {p_fail:.1%}",
             f"  expected claims {exp_claims:.1f}; expected cost "
             f"{exp_claims * cost:.1f} k u",
             "  with shape below 1 most of these claims come early; the",
             "  forecast is redone as returns arrive, and each return is",
             "  traced to its lot before it is paid"]
    emit("t_warranty", lines)
    return dict(p=p_fail, claims=exp_claims)


# ------------------------------------------------ MTBF interval from fleet
def mtbf_interval() -> dict[str, float]:
    failures, hours = 4, 10 * 4380.0       # ten skids, half a year
    mtbf = hours / failures
    lo = 2 * hours / stats.chi2.ppf(0.95, 2 * failures + 2)
    lines = ["MTBF of the skid auxiliary systems from fleet hours",
             f"  {failures} failures in {hours:,.0f} skid-hours: point estimate "
             f"{mtbf:,.0f} h",
             f"  one-sided 95 % lower bound (chi-square): {lo:,.0f} h",
             "  with four failures the bound is far below the point value;",
             "  a supplier quoting the point value as 'demonstrated' is",
             "  quoting a hope - the lower bound is what the data prove"]
    emit("t_mtbf", lines)
    return dict(mtbf=mtbf, lower=lo)


if __name__ == "__main__":
    agreement()
    uncertainty()
    p_chart()
    cpk_interval()
    aoq()
    pareto()
    eight_d()
    warranty_cost()
    mtbf_interval()
