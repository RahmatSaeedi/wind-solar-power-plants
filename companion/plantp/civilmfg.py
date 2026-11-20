"""Civil, structural, tower and tracker manufacture checks (chapter 47):
mill certificates against the order, carbon equivalent, welder
qualifications against their expiry, NDT coverage against the plan, a
bar bending schedule validator, batching tickets against the time and
temperature rules, straightness of a tube from survey points, and the
ageing of a nonconformance register.

Teaching relations and rules. Nothing here is a welding procedure, a
heat-treatment schedule, a cure schedule or a concrete mix; limits come
from the designers, the specifications and the standards.
"""
from __future__ import annotations

from datetime import date


# ------------------------------------------------------------ steel
# [start: cev]
def cev(c: float, mn: float, cr: float = 0.0, mo: float = 0.0, v: float = 0.0,
        ni: float = 0.0, cu: float = 0.0) -> float:
    """Carbon equivalent (IIW form): C + Mn/6 + (Cr+Mo+V)/5 + (Ni+Cu)/15."""
    return c + mn / 6 + (cr + mo + v) / 5 + (ni + cu) / 15
# [end: cev]


# [start: millcert]
def check_cert(cert: dict, order: dict) -> list[str]:
    """Compare one mill certificate with the purchase order: grade,
    thickness range, impact-test temperature and energy, CEV limit."""
    out = []
    if cert["grade"] != order["grade"]:
        out.append(f"grade {cert['grade']} (ordered {order['grade']})")
    lo, hi = order["t_range"]
    if not lo <= cert["t_mm"] <= hi:
        out.append(f"thickness {cert['t_mm']} mm outside {lo}-{hi}")
    if cert["impact_c"] > order["impact_c"]:
        out.append(f"impact tested at {cert['impact_c']} C (ordered "
                   f"{order['impact_c']} C)")
    if min(cert["impact_j"]) < order["impact_j"]:
        out.append(f"impact energy {min(cert['impact_j'])} J below "
                   f"{order['impact_j']} J")
    e = cev(**cert["chem"])
    if e > order["cev_max"]:
        out.append(f"CEV {e:.2f} above {order['cev_max']:.2f}")
    return out
# [end: millcert]


# ------------------------------------------------------------ welders
def qualified(welder: dict, process: str, position: str, on: date) -> str:
    """'ok', or why a welder may not weld this joint on this date."""
    q = welder["quals"].get(process)
    if q is None:
        return f"not qualified for {process}"
    if position not in q["positions"]:
        return f"not qualified in position {position}"
    if q["expires"] < on:
        return f"expired {q['expires']}"
    return "ok"


# ------------------------------------------------------------ NDT coverage
def coverage(plan: dict[str, float], done: dict[str, tuple[float, float]]) -> dict:
    """plan: category -> required share; done: category -> (inspected m,
    total m). Return category -> (share done, short of plan?)."""
    return {k: (done[k][0] / done[k][1], done[k][0] / done[k][1] < plan[k] - 1e-9)
            for k in plan}


# ------------------------------------------------------------ reinforcement
def bar_mass(d_mm: float) -> float:
    """Mass of a steel bar per metre, kg/m: d^2 / 162 (d in mm)."""
    return d_mm ** 2 / 162.0


# [start: bbs]
REQUIRED = ["mark", "dia", "shape", "length_mm", "number"]


def check_bbs(rows: list[dict], dias: set[int], shapes: set[str]) -> list:
    """Return (mark, problem) for a bar bending schedule: missing fields,
    duplicate marks, sizes or shape codes not allowed, lengths that look
    like metres."""
    out, seen = [], set()
    for r in rows:
        m = r.get("mark") or "?"
        for f in REQUIRED:
            if r.get(f) in (None, ""):
                out.append((m, f"missing {f}"))
        if m in seen:
            out.append((m, "duplicate mark"))
        seen.add(m)
        if r.get("dia") not in (None, "") and r["dia"] not in dias:
            out.append((m, f"diameter {r['dia']} not allowed"))
        if r.get("shape") not in (None, "") and r["shape"] not in shapes:
            out.append((m, f"shape code {r['shape']} unknown"))
        ln = r.get("length_mm")
        if isinstance(ln, (int, float)) and 0 < ln < 50:
            out.append((m, "length looks like metres, not mm"))
    return out
# [end: bbs]


def bbs_mass(rows: list[dict]) -> float:
    """Total mass of the schedule's bars, kg (valid rows only)."""
    tot = 0.0
    for r in rows:
        try:
            tot += bar_mass(r["dia"]) * r["length_mm"] / 1000 * r["number"]
        except (TypeError, KeyError):
            pass
    return tot


# ------------------------------------------------------------ concrete
# [start: tickets]
def check_ticket(t: dict, max_min: float, max_temp: float,
                 max_water_l: float) -> list[str]:
    """Batching ticket and delivery record: time from batching to the end
    of discharge, concrete temperature, water added at site."""
    out = []
    age = t["discharged_min"]
    if age > max_min:
        out.append(f"{age:.0f} min from batching (limit {max_min:.0f})")
    if t["temp_c"] > max_temp:
        out.append(f"concrete at {t['temp_c']:.0f} C (limit {max_temp:.0f})")
    if t["water_added_l"] > max_water_l:
        out.append(f"{t['water_added_l']:.0f} L water added on site")
    return out
# [end: tickets]


def conformity(results: list[float], fck: float, margin: float = 4.0,
               low: float = 4.0) -> dict:
    """Teaching conformity rule for a group of strength results: mean of the
    group >= fck + margin and every result >= fck - low."""
    m = sum(results) / len(results)
    return dict(mean=m, ok_mean=m >= fck + margin,
                ok_each=min(results) >= fck - low, lowest=min(results))


# ------------------------------------------------------------ geometry
def straightness(xs: list[float], ys: list[float]) -> tuple[float, float]:
    """Largest offset of survey points from the chord between the ends,
    and where it is (x)."""
    x0, y0, x1, y1 = xs[0], ys[0], xs[-1], ys[-1]
    best = (0.0, x0)
    for x, y in zip(xs, ys):
        yc = y0 + (y1 - y0) * (x - x0) / (x1 - x0)
        if abs(y - yc) > abs(best[0]):
            best = (y - yc, x)
    return best


# ------------------------------------------------------------ NCRs
def ageing(ncrs: list[dict], on: date) -> dict:
    """Open nonconformance reports by age band (days)."""
    bands = {"<30": 0, "30-90": 0, ">90": 0}
    for n in ncrs:
        if n.get("closed"):
            continue
        d = (on - n["raised"]).days
        bands["<30" if d < 30 else "30-90" if d <= 90 else ">90"] += 1
    return bands
