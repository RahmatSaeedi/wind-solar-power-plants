"""Chapter 44, round v: test-point access and in-circuit test coverage,
checking the maker's failure-rate claim against two years of field
record, what an X-ray station is worth at the plant's and the factory's
volume, the learning curve of the ten inverters, and sampling of coating
coverage.

Run from the project root:   python -m companion.ch44.examples_v
Writes companion/ch44/expected/v_*.txt.
Teaching values (A-469, A-472).
"""
from __future__ import annotations

import math

from companion.ch44 import sources as src
from companion.ch44.common import emit
from plantp import convmfg as cm
from plantp import performance as pf


# ------------------------------------------------ 1. test-point access
def access(opens_ppm: float = 500.0, joints: int = 1800) -> dict:
    """In-circuit test finds an open joint only on a net it can touch."""
    lines = [f"open joints {opens_ppm:.0f} ppm a board; in-circuit test finds "
             "an open on a reachable net",
             "  with 0.97 (teaching); other stations as in lesson C",
             "  nets with a test point   ICT finds   open joints out ppm"]
    out = {}
    base = dict(src.LINE["detect"])
    for acc in (0.60, 0.80, 0.92, 1.00):
        det = dict(base)
        det["in-circuit test"] = dict(base["in-circuit test"])
        det["in-circuit test"]["open joint"] = 0.97 * acc
        esc = cm.escapes({"open joint": opens_ppm}, det)["open joint"]
        out[acc] = esc
        lines.append(f"  {acc:22.0%}   {0.97 * acc:9.2f}   {esc:19.2f}")
    lines += [f"  from 60 % to 100 % access the escaping opens fall by "
              f"{1 - out[1.00] / out[0.60]:.0%}: test points are",
              "  placed in the layout (design for test, lesson B) - the",
              "  factory cannot test a net the board gives it no way to touch"]
    emit("v_access", lines)
    return out


# ------------------------------------------------ 2. the maker's FIT claim
def fit_claim(claim_fit: float = 56400.0, units: int = 10, years: float = 2.0,
              observed: int = 14) -> dict:
    hours = units * years * 8760
    expected = claim_fit * hours / 1e9
    lo, hi = pf.rate_interval(observed, hours, 0.90)
    lines = [f"field record of {units} inverters for {years:.0f} years "
             f"({hours:,.0f} unit-hours)",
             f"  claimed {claim_fit:,.0f} FIT: {expected:.1f} failures expected; "
             f"observed {observed}",
             f"  90 % interval of the true rate: {lo * 1e9:,.0f} - "
             f"{hi * 1e9:,.0f} FIT",
             f"  the claim lies {'inside' if lo * 1e9 <= claim_fit <= hi * 1e9 else 'outside'}"
             " the interval: two years of ten units cannot",
             "  tell 56,400 FIT from 90,000 - a fleet this small judges a",
             "  claim only when the record is far off; the maker's wider",
             "  fleet record is the evidence (ch 37)"]
    emit("v_fit", lines)
    return dict(expected=expected, lo=lo * 1e9, hi=hi * 1e9)


# ------------------------------------------------ 3. what an X-ray station is worth
def xray_value(field_cost: float = 3.0, station_cost: float = 60.0) -> dict:
    """Escapes removed by the X-ray station times a field failure cost."""
    with_x = sum(cm.escapes(src.LINE["defects_ppm"], src.LINE["detect"]).values())
    det = {k: v for k, v in src.LINE["detect"].items() if not k.startswith("X-ray")}
    without = sum(cm.escapes(src.LINE["defects_ppm"], det).values())
    removed = (without - with_x) / 1e6                      # per board
    lines = [f"X-ray station: escaping defects {without:.1f} ppm without, "
             f"{with_x:.1f} ppm with",
             f"  field failure {field_cost:.0f} k u, station {station_cost:.0f} k u a "
             "year (teaching)",
             "  boards a year   field cost saved k u   verdict"]
    out = {}
    for boards in (520, 10000, 100000, 1000000):
        saved = boards * removed * field_cost
        out[boards] = saved
        lines.append(f"  {boards:13,d}   {saved:21.2f}   "
                     f"{'pays' if saved > station_cost else 'does not pay'}")
    be = station_cost / (removed * field_cost)
    lines += [f"  break-even near {be:,.0f} boards a year: by escapes alone the",
              "  station does not pay for one plant's 520 boards, nor for a",
              "  converter factory's few tens of thousands; it is kept for",
              "  what it shows - hidden opens and voids under parts that",
              "  crack later (lesson B) - which a functional test cannot",
              "  see: the buyer asks that it exists and its findings feed",
              "  the process, not that one order pays for it"]
    emit("v_xray", lines)
    return dict(without=without, with_x=with_x, breakeven=be)


# ------------------------------------------------ 4. learning curve
def learning(first_h: float = 60.0, rate: float = 0.85, units: int = 10) -> dict:
    b = math.log(rate, 2)
    hours = [first_h * (k + 1) ** b for k in range(units)]
    lines = [f"cabinet integration hours, first unit {first_h:.0f} h, learning "
             f"{rate:.0%} (teaching)",
             "  unit:  " + " ".join(f"{k + 1:5d}" for k in range(units)),
             "  hours: " + " ".join(f"{h:5.1f}" for h in hours),
             f"  total {sum(hours):.0f} h against {units * first_h:.0f} h at the "
             f"first unit's pace; unit 10 takes {hours[-1] / hours[0]:.0%}",
             "  of unit 1 - a plan that prices every unit like the first",
             "  is too slow, one that prices them like the tenth is too",
             "  fast; and a design change at unit 6 starts part of the",
             "  curve again (ch 40)"]
    emit("v_learning", lines)
    return dict(total=sum(hours), last=hours[-1])


# ------------------------------------------------ 5. coating coverage sampling
def coverage_sampling(spots: int = 40, p_miss: float = 0.002) -> dict:
    """Critical spots a board under the coating; each missed with p."""
    p_board = 1 - (1 - p_miss) ** spots
    lines = [f"coating on {spots} critical spots a board (spacings that rely on "
             "it, lesson B);",
             f"  each spot left bare with chance {p_miss:.1%} (teaching)",
             f"  chance a board has a bare critical spot: {p_board:.1%}",
             "  boards inspected   chance to see at least one bare board"]
    out = {}
    for n in (5, 20, 52, 100):
        q = 1 - (1 - p_board) ** n
        out[n] = q
        lines.append(f"  {n:15d}   {q:35.0%}")
    lines += ["  a sample shows the process is working; it does not make",
              "  each board safe - where the spacing depends on the coating,",
              "  every board's critical spots are inspected under UV light",
              "  and the result goes into the board's record"]
    emit("v_coat", lines)
    return dict(p_board=p_board, n52=out[52])


# ------------------------------------------------ 6. interface ageing
def tim_ageing(years: int = 25, n0: float = 20000.0) -> dict:
    """Daily power cycles; the interface resistance grows with cycles
    (teaching rates), the swing grows with it, and so does the damage
    per year (Miner sum against a reference life n0 at the design swing)."""
    from plantp import pe
    from companion.ch44.examples_b import S as ST, I as IN
    r0 = cm.tim_r(ST["tim_um"], ST["tim_k"], ST["tim_area_cm2"])
    base = ST["p_module_w"] * (ST["r_jc"] + r0 + ST["r_hs"])
    rows = {}
    for name, grow in (("paste (3 % a 1,000 cycles)", 0.03),
                       ("phase-change pad (0.5 %)", 0.005)):
        damage, swings = 0.0, []
        for y in range(years):
            r = r0 * (1 + grow) ** (y * 365 / 1000)
            sw = ST["p_module_w"] * (ST["r_jc"] + r + ST["r_hs"])
            swings.append(sw)
            damage += 365 / (n0 * pe.relative_cycle_life(sw, base))
        rows[name] = (swings[-1], damage)
    lines = [f"interface ageing over {years} years of daily cycles; life "
             f"{n0:,.0f} cycles at the",
             f"  design swing {base:.1f} K (teaching); damage = sum of cycles / "
             "life (Miner)",
             "  interface material              swing in year 25 K   damage"]
    for name, (sw, d) in rows.items():
        lines.append(f"  {name:31s} {sw:18.1f}   {d:6.2f}")
    ratio = rows["paste (3 % a 1,000 cycles)"][1] / rows["phase-change pad (0.5 %)"][1]
    lines += [f"  the ageing paste uses {ratio:.1f} x the life of the pad: a",
              "  thicker layer runs hotter, swings more, and ages faster -",
              "  the choice of material is a design-for-reliability decision,",
              "  and its growth rate comes from the maker's power-cycling",
              "  tests, not from this rule"]
    emit("v_tim", lines)
    return dict(rows=rows, ratio=ratio)


if __name__ == "__main__":
    access()
    fit_claim()
    xray_value()
    learning()
    coverage_sampling()
    tim_ageing()
