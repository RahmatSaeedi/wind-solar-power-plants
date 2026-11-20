"""Chapter 43, a sixth round: natural oil flow through the windings, the
factory test sequence and its duration, the insulation loss factor
referred to a common temperature, the scatter of oil breakdown readings,
the buyer's witness plan, and the design review's technical queries.

Run from the project root:   python -m companion.ch43.examples_w
Writes companion/ch43/expected/w_*.txt.
Teaching values (A-460 to A-462); purposes and arithmetic, no procedures.
"""
from __future__ import annotations

import math
from statistics import mean, stdev

from companion.ch43 import sources as src
from companion.ch43.common import emit

M = src.MAIN_B


# ------------------------------------------------ natural oil flow
def oil_flow(cp: float = 1.9, rho: float = 870.0, dt_oil: float = 20.0):
    k = M["s_onan_mva"] / M["s_mva"]
    loss = 42.0 + 290.0 * k ** 2
    m = loss / (cp * dt_oil)
    q = m / rho * 1000
    lines = [f"oil flow of the ONAN rating ({M['s_onan_mva']:.0f} MVA): losses "
             f"{loss:.0f} kW",
             f"  bottom-to-top oil rise {dt_oil:.0f} K (teaching), cp {cp} kJ/kg K",
             f"  flow = P / (cp dT) = {m:.1f} kg/s = {q:.1f} L/s, driven only by",
             "  the lighter hot oil rising in the windings and the heavier",
             "  cooled oil sinking in the radiators",
             "  a duct narrowed by a shifted spacer or a sludge layer slows",
             "  this flow where it matters: the hot spot rises before the",
             "  top oil shows it - why the heat run reads the winding, not",
             "  only the oil (lesson C)"]
    emit("w_flow", lines)
    return dict(loss=loss, m=m, q=q)


# ------------------------------------------------ test sequence
TESTS_SEQ = [   # test, hours (teaching), why here
    ("ratio and vector group", 3, "first: wrong taps spoil the rest"),
    ("winding resistance, cold", 4, "base for losses and the heat run"),
    ("no-load loss and current", 3, "core as built"),
    ("load loss and impedance", 4, "windings as built"),
    ("heat run (short-circuit method)", 14, "before dielectrics, oil sampled"),
    ("dissolved gas after heat run", 2, "within hours of the heat run"),
    ("dielectric tests with PD", 10, "after the heat run"),
    ("lightning impulse", 6, "insulation of discs and leads"),
    ("no-load loss repeated", 2, "nothing changed by the dielectrics"),
    ("sound", 4, "fans and core"),
    ("frequency response, all windings", 4, "baseline at the end"),
    ("functional tests, OLTC, devices", 6, "accessories"),
]


def sequence(hours_day: float = 16.0) -> dict[str, float]:
    total = sum(h for _, h, _ in TESTS_SEQ)
    lines = [f"factory test sequence of T1 (teaching hours; {hours_day:.0f} h a day)",
             "  test                              hours   why in this place"]
    for t, h, why in TESTS_SEQ:
        lines.append(f"  {t:33s} {h:5.0f}   {why}")
    lines += [f"  {total:.0f} hours, about {math.ceil(total / hours_day)} working days "
              "in the bay",
              "  the order is evidence too: a repeated no-load test after the",
              "  dielectrics shows they changed nothing, and the frequency",
              "  response taken last is the state that will travel"]
    emit("w_sequence", lines)
    return dict(total=total, days=math.ceil(total / hours_day))


# ------------------------------------------------ loss factor to 20 C
def tan_delta(measured=((0.0042, 32.0), (0.0031, 24.0)), alpha: float = 0.024):
    lines = ["insulation loss factor (tan delta) of the windings referred to",
             f"  20 C with a teaching factor exp(-{alpha} (T - 20))",
             "  reading      at C   at 20 C"]
    out = []
    for td, t in measured:
        r = td * math.exp(-alpha * (t - 20))
        out.append(r)
        lines.append(f"  {td:.4f}   {t:7.0f}   {r:.4f}")
    lines += ["  two readings that look far apart come close once both are",
              "  referred to 20 C: the factory value and every later site",
              "  value are compared at one temperature - the correction",
              "  curve is the insulation's and the test set maker's"]
    emit("w_tand", lines)
    return dict(ref=out)


# ------------------------------------------------ oil breakdown scatter
def breakdown(shots=(62.0, 71.0, 58.0, 69.0, 74.0, 65.0), shots_b=(48.0, 76.0, 39.0,
              70.0, 81.0, 55.0)) -> dict[str, float]:
    lines = ["oil breakdown voltages of two samples (kV, teaching)",
             "  sample   shots                    mean    CV"]
    out = {}
    for name, sh in (("A", shots), ("B", shots_b)):
        mu, sd = mean(sh), stdev(sh)
        out[name] = (mu, sd / mu)
        lines.append(f"  {name:6s}   " + ", ".join(f"{x:.0f}" for x in sh)
                     + f"   {mu:5.1f}  {sd / mu:4.0%}")
    lines += ["  B's mean is close to A's but its shots scatter widely:",
              "  particles or free water make some gaps weak - the mean",
              "  alone would pass it; the scatter is the warning, and the",
              "  oil standard and the laboratory set the method (STD-178)"]
    emit("w_breakdown", lines)
    return out


# ------------------------------------------------ witness plan
WITNESS = [   # point, kind (H hold, W witness, R review)
    ("design review closed", "H"), ("core steel certificates", "R"),
    ("bare-core loss", "W"), ("winding dimensions", "R"),
    ("active part before drying", "W"), ("drying end point", "R"),
    ("oil before filling", "R"), ("routine and type tests", "H"),
    ("frequency response, DGA baselines", "R"), ("preparation for shipment", "W"),
]


def witness(trip_days: float = 3.0) -> dict[str, int]:
    count = {k: sum(1 for _, x in WITNESS if x == k) for k in "HWR"}
    trips = count["H"] + count["W"]
    lines = ["the buyer's inspection points at the factory (teaching plan)",
             "  point                                kind"]
    for p, k in WITNESS:
        lines.append(f"  {p:36s} {k}")
    lines += [f"  {count['H']} holds, {count['W']} witness, {count['R']} record reviews; "
              f"{trips} visits, about {trips * trip_days:.0f} days",
              "  three of T1's five gaps sit on 'R' rows (winding heights,",
              "  drying, oil), the burr on no row at all, the recorder on a",
              "  witness still ahead - a witnessed drying end point would",
              "  have been cheap; the plan is set from the FMEA (lesson C)"]
    emit("w_witness", lines)
    return dict(count, trips=trips)


# ------------------------------------------------ technical queries
TQS = [   # query from the design review, raised because, status
    ("TQ-01 steel grade and building factor", "P0 42 kW needs 1.15 W/kg at 1.22", "answered"),
    ("TQ-02 tap steps of 9 turns", "ratio -0.43 % at the -10 % tap", "answered"),
    ("TQ-03 energising tap", "1.89 T if energised at -10 %", "open"),
    ("TQ-04 short-circuit proof", "inner winding supported? test or calc", "open"),
    ("TQ-05 HV radial build", "106 mm from the CTC against 110 mm", "answered"),
    ("TQ-06 paper grade", "upgraded paper for later storage", "open"),
    ("TQ-07 DC injection limit", "PV unit core, 0.5 % DC = 2.7 x magnetising", "open"),
]


def queries() -> dict[str, int]:
    st = {}
    lines = ["technical queries raised by the preliminary design (teaching log)",
             "  query                                    status"]
    for q, why, status in TQS:
        st[status] = st.get(status, 0) + 1
        lines.append(f"  {q:40s} {status}")
        lines.append(f"    because: {why}")
    lines += [f"  {st.get('open', 0)} of {len(TQS)} open: each became a question to the maker",
              "  because the simple sum and the offer disagreed or could not",
              "  see - the review's product is the query, not a redesign"]
    emit("w_queries", lines)
    return st


if __name__ == "__main__":
    oil_flow()
    sequence()
    tan_delta()
    breakdown()
    witness()
    queries()
