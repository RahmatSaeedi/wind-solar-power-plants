"""Chapter 40, lesson E (reliability in production): critical
characteristics drawn from the FMEA, reliability growth of the pilot run
(Crow-AMSAA) and the test time to reach the MTBF target, the burn-in
trade-off for a latent-defect sub-population, the escape chain before and
after the corrective actions, and early field returns read with a
Weibull fit (ch 37).

Run from the project root:   python -m companion.ch40.examples_e
Writes companion/ch40/expected/e_*.txt and diagrams/data/ch40-growth.csv.
Teaching values (A-437, A-439); a fictional integrator.
"""
from __future__ import annotations

import math

from companion.ch40 import sources as src
from companion.ch40.common import csv, emit
from plantp import performance as pf
from plantp import quality as qa


def critical() -> list[dict]:
    cc = [r for r in src.FMEA if qa.severity_class(r["s"]) == 2
          or (r["s"] >= 7 and r["o"] >= 3)]
    lines = ["critical characteristics drawn from the FMEA",
             "  (severity 9-10, or 7-8 with occurrence 3 or more)"]
    for r in cc:
        lines.append(f"  {r['op']}  {r['mode']}: {r['effect']}")
    lines += [f"  {len(cc)} of {len(src.FMEA)} modes become critical: each gets"
              " a",
              "  control-plan row, a record in the traveler and a place in",
              "  the FAT, because each leads to a field failure mechanism",
              "  (heat, insulation breakdown, touch voltage)"]
    emit("e_critical", lines)
    return cc


def target_time(fit: dict, target: float) -> float:
    """Test hours at which the instantaneous MTBF reaches the target,
    if the same growth continues."""
    b, lam = fit["beta"], fit["lam"]
    return (1.0 / (target * lam * b)) ** (1.0 / (b - 1.0))


def growth() -> dict[str, float]:
    fit = qa.crow_amsaa(src.PILOT, src.PILOT_T)
    t_need = target_time(fit, src.TARGET_MTBF)
    lines = ["reliability growth in the pilot extended-run test",
             f"  failures {fit['n']} in {src.PILOT_T:,.0f} h; beta "
             f"{fit['beta']:.2f} (below 1: improving)",
             f"  cumulative MTBF {fit['mtbf_cum']:.0f} h; MTBF now "
             f"{fit['mtbf_now']:.0f} h",
             f"  target {src.TARGET_MTBF:,.0f} h is reached at about "
             f"{t_need:,.0f} h of test",
             "  if the corrective actions keep coming at the same pace;",
             f"  five skids on test share it: {t_need / 5:,.0f} h each "
             f"(about {t_need / 5 / 730:.0f} months)",
             "  growth is not time passing - it is failures found, their",
             "  causes removed and the fixes built into later skids"]
    rows = [(k, t) for k, t in enumerate(src.PILOT, 1)]
    model = [(round(t, 0), round(fit["lam"] * t ** fit["beta"], 3))
             for t in (20, 50, 100, 200, 500, 1000, 2000)]
    csv("ch40-growth.csv", "n,t", rows)
    csv("ch40-growth-model.csv", "t,n", model)
    emit("e_growth", lines)
    return dict(fit=fit, t_need=t_need)


def weibull_cdf(t: float, beta: float, eta: float) -> float:
    return 1 - math.exp(-((t / eta) ** beta))


def burn_in() -> dict[float, dict[float, float]]:
    L = src.LATENT
    latent = L["share"] * L["boards"]
    rack = 0.001                            # k u a board-hour (shared rack)
    lines = [f"burn-in of control boards: {L['boards']} boards, "
             f"{L['share']:.0%} latent ({latent:.1f} expected)",
             f"  latent ones fail as Weibull beta {L['beta']}, eta "
             f"{L['eta_h']:.0f} h; rack {rack * 1000:.0f} u a board-hour",
             "  hours  caught  left   cost if a field failure costs",
             "                          6 k u (swap)   40 k u (block trips)"]
    out: dict[float, dict[float, float]] = {6.0: {}, 40.0: {}}
    for h in (0.0, 24.0, 48.0, 168.0, 336.0):
        caught = latent * weibull_cdf(h, L["beta"], L["eta_h"])
        left = latent - caught
        for field in out:
            out[field][h] = L["boards"] * h * rack + left * field
        lines.append(f"  {h:5.0f}  {caught:6.2f}  {left:5.2f}   "
                     f"{out[6.0][h]:12.2f}   {out[40.0][h]:12.2f}")
    best = {f: min(c, key=c.get) for f, c in out.items()}
    lines += [f"  cheapest: {best[6.0]:.0f} h if a failure is a board swap, "
              f"{best[40.0]:.0f} h",
              "  if it trips a block: the field cost decides, not a habit",
              "  burn-in removes weak units; it does not remove the cause -",
              "  the supplier's corrective action does (lesson C)"]
    emit("e_burnin", lines)
    return out


def escapes() -> dict[str, float]:
    before = qa.escape(1.0, [0.0, 0.3, 0.0])
    after = qa.escape(1.0, [0.5, 0.3, 0.95])
    joints = 10 * 24
    bad = 0.30 * 3 * 24                     # 30 % of joints on 3 skids
    lines = ["escape chain of an under-torqued joint (share that leaves)",
             "  stage                 before   after",
             "  paint mark at OP40      0.0     0.5",
             "  visual in process       0.3     0.3",
             "  resistance at FAT       0.0     0.95",
             f"  escape                {before:5.2f}   {after:6.4f}",
             f"  with {bad:.0f} bad joints of {joints}: {bad * before:.1f} reach "
             f"site before, {bad * after:.2f} after",
             "  detection is multiplied, not added: three modest checks",
             "  in a row beat one perfect check that is sometimes skipped"]
    emit("e_escape", lines)
    return dict(before=before, after=after, bad=bad)


RETURNS = [40.0, 75.0, 130.0, 210.0, 420.0, 900.0, 1600.0]   # h (A-439)
RUNNING = [4380.0] * 53                                       # survivors


def field_returns() -> tuple[float, float]:
    k, lam = pf.weibull_mle(RETURNS, RUNNING)
    ratio = (100.0 / 4000.0) ** (k - 1)
    lines = ["early field returns of skid components (first half year)",
             f"  failures {len(RETURNS)}, survivors {len(RUNNING)} at 4,380 h",
             f"  Weibull shape {k:.2f} (ch 37 method); the failure rate at",
             f"  100 h is {ratio:.1f} times the rate at 4,000 h",
             "  shape below 1: the failure rate falls with age - the mark",
             "  of manufacturing escapes, not of wear-out; the response is",
             "  in the factory (genealogy, root cause, supplier action),",
             "  not a shorter maintenance interval"]
    emit("e_returns", lines)
    return k, lam


if __name__ == "__main__":
    critical()
    growth()
    burn_in()
    escapes()
    field_returns()
