"""Chapter 49, lesson A (construction readiness) and lesson L (emergency
and site-security readiness): approvals against the fronts that need
them, method statements, crew competence, design release, welfare at the
workforce peak, response time to each work front, and inductions against
the gate log.

Run from the project root:   python -m companion.ch49.examples_a
Writes companion/ch49/expected/a_*.txt and l_*.txt.
"""
from __future__ import annotations

import math
from datetime import timedelta

import numpy as np

from companion.ch49 import sources as src
from companion.ch49.common import emit


# [start: permits]
def permits() -> list:
    rows = []
    for name, front, need, got in src.PERMITS:
        late = None if got is None else got - need
        rows.append((name, front, need, got, late))
    return rows
# [end: permits]


def show_permits() -> list:
    rows = permits()
    lines = ["approvals register against the day each front needs them",
             "  approval                                 needed  granted  late days"]
    for name, front, need, got, late in rows:
        g = "open" if got is None else str(got)
        l_ = "-" if late is None else (f"{late:+d}" if late > 0 else "0")
        lines.append(f"  {name[:40]:40s} {need:6d}  {g:>7s}  {l_:>9s}")
    blocked = [r for r in rows if r[3] is None or r[4] > 0]
    lines += [f"  {len(blocked)} of {len(rows)} late or open: the wadi consent held the "
              "access road",
              "  15 days; the road crossing and the ruin-buffer works have",
              "  no approval yet - their fronts are planned around them, not",
              "  started in hope (ch 22 permit register, ch 33 ruin buffer)"]
    emit("a_permits", lines)
    return blocked


def methods() -> list:
    bad = [(a, ms, st) for a, (ms, st) in src.METHODS.items() if st != "approved"]
    lines = ["method statements by activity: work starts only on an approved one"]
    lines += [f"  {a:28s} {ms or 'none':6s} {st or 'not written'}"
              for a, (ms, st) in src.METHODS.items()]
    lines += [f"  {len(bad)} activities cannot start: string wiring has none, MV",
              "  terminations went back with comments, earthing waits for",
              "  review - each is on the block's critical path (lesson D)"]
    emit("a_methods", lines)
    return bad


def competence(warn_days: int = 45) -> dict:
    expired, soon, missing = [], [], []
    for crew, roles in src.ROSTER.items():
        for role, person, until in roles:
            if person is None:
                missing.append((crew, role))
            elif until is not None and until < src.TODAY:
                expired.append((crew, role, person, until))
            elif until is not None and until < src.TODAY + timedelta(days=warn_days):
                soon.append((crew, role, person, until))
    lines = [f"crew competence on {src.TODAY} (certificates and named roles)"]
    lines += [f"  expired: {c} - {r} ({p}, {u})" for c, r, p, u in expired]
    lines += [f"  expires within {warn_days} days: {c} - {r} ({p}, {u})"
              for c, r, p, u in soon]
    lines += [f"  role not filled: {c} - {r}" for c, r in missing]
    lines += ["  the jointing crew cannot terminate MV cables until the",
              "  jointer's maker training is renewed; the crane crew has no",
              "  lift supervisor, so no planned lift goes ahead; the module",
              "  crew works without a named first aider - each is a stop,",
              "  not a note (ch 32 competency)"]
    emit("a_competence", lines)
    return dict(expired=expired, soon=soon, missing=missing)


def release() -> list:
    bad = [(wp, d, r, s) for wp, docs in src.DRAWINGS.items() for d, r, s in docs
           if s != "IFC"]
    lines = ["drawings each package needs, by status (ch 38 statuses)"]
    for wp, docs in src.DRAWINGS.items():
        for d, r, s in docs:
            lines.append(f"  {wp:22s} {d} {r}  {s}"
                         + ("" if s == "IFC" else "  - not for construction"))
    lines += [f"  {len(bad)} packages wait for a drawing issued for construction:",
              "  building from a drawing 'issued for approval' is building a",
              "  revision that may still change"]
    emit("a_release", lines)
    return bad


def welfare(per_toilet: int = 15, l_day: float = 70.0, outside: float = 0.6) -> dict:
    months = np.arange(1, 19)
    curve = np.sin(np.pi * (months - 0.5) / 18) ** 1.5
    workers = 450 * curve / curve.max()                 # ch 22 curve
    peak = int(round(workers.max()))
    lines = ["welfare at the workforce peak (ch 22 curve, ch 32 70 L a day)",
             f"  peak {peak} workers in month {int(months[workers.argmax()])}; "
             f"worker-months {workers.sum():,.0f}",
             f"  toilets at 1 per {per_toilet}: {math.ceil(peak / per_toilet)}; water "
             f"{peak * l_day / 1000:.1f} m3 a day",
             f"  beds for workers from outside ({outside:.0%}): {math.ceil(peak * outside)}",
             "  temporary facilities are sized for the peak and built before",
             "  it: a camp that fills in month 9 is planned in month 2"]
    emit("a_welfare", lines)
    return dict(peak=peak, toilets=math.ceil(peak / per_toilet),
                water=peak * l_day / 1000, beds=math.ceil(peak * outside))


# ------------------------------------------------ L. emergency readiness
def response() -> dict:
    t = src.SITE_TEAM
    out = {f: t["mobilise_min"] + km / t["road_kmh"] * 60 for f, km in src.FRONTS.items()}
    lines = [f"site first-aid team to each front: {t['mobilise_min']:.0f} min to mobilise, "
             f"{t['road_kmh']:.0f} km/h on site roads",
             f"  target {t['target_min']:.0f} min (teaching; the approved emergency plan sets it)",
             "  front                        km    minutes"]
    lines += [f"  {f:28s} {src.FRONTS[f]:4.1f}  {m:7.1f}"
              + ("" if m <= t["target_min"] else "  OVER")
              for f, m in out.items()]
    over = [f for f, m in out.items() if m > t["target_min"]]
    lines += [f"  over the target: {', '.join(over)}",
              "  the line works sit beyond the reach of one medical point: a",
              "  second equipped vehicle stays with the line crew, and the",
              "  work does not start until it is there"]
    emit("l_response", lines)
    return dict(minutes=out, over=over)


def inductions() -> list:
    bad = []
    for w in src.GATE:
        d = src.INDUCT.get(w, "absent")
        if d == "absent":
            bad.append((w, "not in the induction register"))
        elif d is None:
            bad.append((w, "registered, never inducted"))
        elif (src.TODAY - d).days > src.INDUCT_VALID_DAYS:
            bad.append((w, f"induction of {d} expired"))
    lines = [f"gate log of {src.TODAY} against the induction register "
             f"({src.INDUCT_VALID_DAYS}-day validity)"]
    lines += [f"  {w}: {why}" for w, why in bad]
    lines += [f"  {len(bad)} of {len(src.GATE)} people inside without a valid induction:",
              "  the gate is where the induction register is enforced, and",
              "  the muster count (ch 32) is only as good as the gate log"]
    emit("l_induction", lines)
    return bad


if __name__ == "__main__":
    show_permits()
    methods()
    competence()
    release()
    welfare()
    response()
    inductions()
