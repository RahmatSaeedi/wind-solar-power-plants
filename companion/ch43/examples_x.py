"""Chapter 43, a seventh round: deductions against the evaluated cost,
the partial-discharge reading against its calibration and background,
phase resistances of a delta from line readings, each finding of T1 put
into an acceptance category, and a second dossier for a PV unit.

Run from the project root:   python -m companion.ch43.examples_x
Writes companion/ch43/expected/x_*.txt.
Teaching values (A-462, A-463); no test procedures.
"""
from __future__ import annotations

from scipy.optimize import fsolve

from companion.ch43 import sources as src
from companion.ch43.common import emit
from plantp import xfmrdesign as xd

M, C = src.MAIN_B, src.COSTS


# ------------------------------------------------ deductions close the gap
def closure(price: float = 1700.0) -> dict[str, float]:
    p0, pk = 42.2, 298.0
    bid = price + C["a_kw"] * M["p0_kw"] + C["b_kw"] * M["pk_kw"]
    built = price + C["a_kw"] * p0 + C["b_kw"] * pk
    ded = C["a_kw"] * (p0 - M["p0_kw"]) + C["b_kw"] * (pk - M["pk_kw"])
    lines = ["bid B as evaluated and T1 as tested, with the same A and B",
             f"  evaluated at award: {price:,.0f} + {C['a_kw']} x {M['p0_kw']:.0f} + "
             f"{C['b_kw']} x {M['pk_kw']:.0f} = {bid:,.1f} k u",
             f"  as tested:          {price:,.0f} + {C['a_kw']} x {p0} + "
             f"{C['b_kw']} x {pk:.0f} = {built:,.1f} k u",
             f"  difference {built - bid:.1f} k u = the deduction {ded:.1f} k u",
             "  a deduction priced with the enquiry's own A and B puts the",
             "  owner where the evaluation assumed: the bids stay compared",
             "  on the same footing after the test (ch 25, penalty)"]
    emit("x_closure", lines)
    return dict(bid=bid, built=built, ded=ded)


# ------------------------------------------------ PD reading
def pd(cal_pc: float = 500.0, cal_reading: float = 2.50, reading: float = 0.60,
       background_pc: float = 30.0, limit_pc: float = 100.0) -> dict[str, float]:
    scale = cal_pc / cal_reading
    q = reading * scale
    lines = [f"partial discharge: the circuit is calibrated with a known "
             f"{cal_pc:.0f} pC (teaching)",
             f"  calibration reading {cal_reading} units -> {scale:.0f} pC per unit",
             f"  test reading {reading} units -> {q:.0f} pC; background "
             f"{background_pc:.0f} pC; limit {limit_pc:.0f} pC",
             f"  signal to background {q / background_pc:.1f}: the reading is "
             "distinguishable and over the limit",
             "  a reading near the background could not be told apart from",
             "  noise; the report states calibration and background, or the",
             "  pC number means nothing"]
    emit("x_pd", lines)
    return dict(q=q, sn=q / background_pc)


# ------------------------------------------------ delta resistances
# [start: delta]
def delta_phases(r_ab: float, r_bc: float, r_ca: float) -> list[float]:
    """Phase resistances of a closed delta from its three line readings:
    each reading is one phase in parallel with the other two in series."""
    def eqs(r):
        a, b, c = r
        s = a + b + c
        return [a * (b + c) / s - r_ab, b * (c + a) / s - r_bc,
                c * (a + b) / s - r_ca]
    guess = [1.5 * r_ab, 1.5 * r_bc, 1.5 * r_ca]
    return [float(x) for x in fsolve(eqs, guess)]
# [end: delta]


def delta(r_phase: float = 0.0693, bad: float = 0.02) -> dict[str, float]:
    a, b, c = r_phase * (1 + bad), r_phase, r_phase
    s = a + b + c
    lines_r = (a * (b + c) / s, b * (c + a) / s, c * (a + b) / s)
    back = delta_phases(*lines_r)
    spread_line = (max(lines_r) / min(lines_r) - 1)
    lines = [f"LV delta read line to line, one phase {bad:.0%} high (teaching)",
             "  line readings ohm: " + ", ".join(f"{x:.5f}" for x in lines_r),
             f"  spread of the line readings {spread_line:.2%}",
             "  phases solved back: " + ", ".join(f"{x:.5f}" for x in back),
             f"  the phase fault shows at {spread_line / bad:.0%} of its size in the",
             "  line readings: a delta shares each reading among all three",
             "  phases - the comparison is made on solved phase values"]
    emit("x_delta", lines)
    return dict(spread=spread_line, back=back)


# ------------------------------------------------ acceptance categories
FINDINGS = [   # finding, category
    ("losses within tolerance, above guarantee", "accept with deduction"),
    ("impedance 12.6 % inside the band", "accept"),
    ("ratio fail at tap +8.75 %", "hold: rework and retest"),
    ("winding rise 66.5 K over 65 K", "owner: concession or repair"),
    ("PD 120 pC over 100 pC", "hold: investigate and retest"),
    ("acetylene after heat run", "hold: explain before shipment"),
    ("FRA file of the LV winding missing", "hold: deliver the record"),
    ("short-circuit proof", "open technical query"),
]


def categories() -> dict[str, int]:
    count: dict[str, int] = {}
    lines = ["each finding of T1 in an acceptance category",
             "  finding                                   category"]
    for f, cat in FINDINGS:
        key = cat.split(":")[0]
        count[key] = count.get(key, 0) + 1
        lines.append(f"  {f:41s} {cat}")
    items = [f"{k} {v}" for k, v in count.items()]
    lines += ["  " + ", ".join(items[:3]) + ",", "  " + ", ".join(items[3:]),
              "  one 'hold' is enough to stop shipment; a concession is the",
              "  owner's written choice; a deduction is arithmetic - three",
              "  kinds of decision with three kinds of owner"]
    emit("x_categories", lines)
    return count


# ------------------------------------------------ PV unit dossier
def pv_dossier(llf: float = 0.20) -> dict[str, float]:
    u = src.PVU
    a = C["a_kw"]
    b = a * llf
    meas = dict(p0=4.31, pk75=42.9, uk=7.21)
    rows = [("no-load loss kW", u["p0_kw"], meas["p0"], meas["p0"] <= u["p0_kw"] * 1.15),
            ("load loss kW, 75 C", u["pk_kw"], meas["pk75"], meas["pk75"] <= u["pk_kw"] * 1.15),
            ("impedance %", u["uk_pct"], meas["uk"],
             abs(meas["uk"] / u["uk_pct"] - 1) <= 0.075)]
    ded = a * max(0, meas["p0"] - u["p0_kw"]) + b * max(0, meas["pk75"] - u["pk_kw"])
    lines = [f"PV unit transformer no. 3 (offer U-A): routine test against the "
             "guarantee",
             "  quantity               guarantee   measured   verdict"]
    for name, g, m, ok in rows:
        lines.append(f"  {name:22s} {g:9.2f}   {m:8.2f}   {'pass' if ok else 'FAIL'}")
    lines += [f"  A = {a} and B = A x {llf} = {b:.2f} k u/kW (PV group loss load "
              "factor, ch 25)",
              f"  deduction for this unit {ded:.2f} k u; ten units like it "
              f"{10 * ded:.1f} k u",
              "  each unit passes alone; the series is what the money sees -",
              "  ch 25's series clause and these deductions are two sides of",
              "  the same guarantee"]
    emit("x_pvdossier", lines)
    return dict(ded=ded, b=b)


if __name__ == "__main__":
    closure()
    pd()
    delta()
    categories()
    pv_dossier()
    _ = xd
