"""Chapter 8 - four more lessons: an induction motor on unbalanced voltage,
the acceleration time and starting heat of a motor, slot-pole choice with
cogging and winding factor, and the capability chart of the backup
generator with a leading (capacitive) night load.

Run from the project root:   python -m companion.ch08.examples_more3
Writes companion/ch08/expected/z_*.txt and diagrams/data/ch08-*.csv.
Teaching values A-113, A-114, A-125, A-129, A-140 .. A-143 (fictional).
"""
from __future__ import annotations

import math

from companion.ch08.common import csv, emit
from companion.ch08.examples_a import MOTOR
from plantp import machines as m
from plantp.phasors import polar

P_RATED = 30e3
K_DEEP = 2.0                     # rotor resistance factor at 100 Hz (A-140)


# [start: unbalance]
def negative_sequence(u_pct: float, slip: float) -> dict:
    """Negative-sequence circuit of the motor: voltage u % of the positive
    sequence, slip 2 - s, rotor resistance raised by the deep-bar factor."""
    data = dict(MOTOR, v_ph=MOTOR["v_ph"] * u_pct / 100,
                r2=MOTOR["r2"] * K_DEEP)
    return m.InductionMachine(**data).operate(2 - slip)
# [end: unbalance]


def unbalance() -> None:
    im = m.InductionMachine(**MOTOR)
    s = im.slip_for_shaft_power(P_RATED)
    pos = im.operate(s)
    i_pos = abs(pos["i1"])
    cu = pos["p_cu1"] + pos["p_cu2"]
    lines = [f"30 kW motor at rated load: slip {100 * s:.2f} %, "
             f"I {i_pos:.1f} A, copper loss {cu:.0f} W",
             f"negative sequence: slip 2 - s = {2 - s:.4f}, rotor R x "
             f"{K_DEEP} at 100 Hz (A-140)",
             "  u_V    I_neg  I_neg/I  worst phase  extra Cu   hot phase Cu",
             "    %        A        %            A         W     x rated"]
    for u in (1, 2, 3, 5):
        neg = negative_sequence(u, s)
        i_neg = abs(neg["i1"])
        extra = neg["p_cu1"] + neg["p_cu2"]
        hot = ((i_pos + i_neg) / i_pos) ** 2
        share = 100 * i_neg / i_pos
        lines.append(f"  {u:3.0f}  {i_neg:7.1f}  {share:7.1f}"
                     f"  {i_pos + i_neg:11.1f}  {extra:8.0f}  {hot:13.2f}")
    t_neg = negative_sequence(2, s)["torque"]
    ratio = abs(negative_sequence(2, s)["i1"]) / i_pos / 0.02
    lines += [f"  current unbalance is about {ratio:.1f} times "
              "the voltage unbalance",
              "  (the negative sequence meets the low locked-rotor impedance)",
              f"  braking torque of the 2 % negative sequence: {t_neg:.2f} "
              f"N m of {pos['torque']:.0f}"]
    # derating: largest shaft power with the worst phase at rated current
    for u in (2, 3, 5):
        lo, hi = 5e3, P_RATED
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            s_m = im.slip_for_shaft_power(mid)
            worst = (abs(im.operate(s_m)["i1"])
                     + abs(negative_sequence(u, s_m)["i1"]))
            lo, hi = (mid, hi) if worst < i_pos else (lo, mid)
        lines.append(f"  worst phase held at {i_pos:.1f} A with {u} %: shaft "
                     f"power {lo / 1e3:.1f} kW ({100 * lo / P_RATED:.0f} %)")
    emit("z_unbalance", lines)


# [start: accel]
def run_up(v_frac: float, j: float, load, dt: float = 1e-3,
           t_end: float = 3.0) -> dict:
    """Integrate J dw/dt = T_motor - T_load from standstill at a fixed
    supply voltage (fraction of rated); returns the speed record and the
    time and rotor heat to reach 95 % of synchronous speed."""
    im = m.InductionMachine(**dict(MOTOR, v_ph=MOTOR["v_ph"] * v_frac))
    w_s = 2 * math.pi * im.n_sync / 60
    w, t, e_rotor, e_stator = 0.0, 0.0, 0.0, 0.0
    rec, t95, e95 = [], None, None
    while t < t_end:
        op = im.operate(max(1e-4, 1 - w / w_s))
        acc = (op["torque"] - load(w / w_s)) / j
        if t95 is None:
            e_rotor += op["p_cu2"] * dt
            e_stator += op["p_cu1"] * dt
        w += acc * dt
        t += dt
        if t95 is None and w >= 0.95 * w_s:
            t95, e95 = t, (e_rotor, e_stator)
        rec.append((t, 60 * w / (2 * math.pi)))
    return {"t95": t95, "e95": e95, "rec": rec, "w_s": w_s}
# [end: accel]


def row(name: str, r: dict, j: float) -> str:
    e_r, e_s = r["e95"]
    return (f"  {name:8s}  {r['t95']:8.2f} s  {e_r / 1e3:8.1f} kJ"
            f"  {e_s / 1e3:9.1f} kJ  {0.5 * j * r['w_s'] ** 2 / 1e3:7.1f} kJ")


def acceleration() -> None:
    im = m.InductionMachine(**MOTOR)
    t_r = im.operate(im.slip_for_shaft_power(P_RATED))["torque"]
    j_comp, j_fan = 1.0, 15.0                                     # A-141
    comp = lambda x: t_r * (0.10 + 0.30 * x * x)       # unloaded start
    fan = lambda x: t_r * (x / 0.9835) ** 2            # fan at rated speed
    lines = [f"run-up of the 30 kW motor (A-114), rated torque {t_r:.0f} N m"
             " (A-141):",
             f"  compressor started unloaded, J {j_comp} kg m2, "
             "T_L = T_r (0.10 + 0.30 x^2)",
             "  supply      t to 95 %   rotor heat   stator heat   1/2 J w^2"]
    curves = {}
    for name, v in (("100 %", 1.0), ("94.2 %", 0.942), ("81.3 %", 0.813)):
        r = run_up(v, j_comp, comp)
        curves[name] = r["rec"]
        lines.append(row(name, r, j_comp))
    lines.append(f"  same motor on a fan, J {j_fan} kg m2, T_L = T_r x^2:")
    for name, v in (("100 %", 1.0), ("81.3 %", 0.813)):
        r = run_up(v, j_fan, fan, t_end=20.0)
        lines.append(row(name, r, j_fan))
    lines += ["  rotor heat in a start is at least the kinetic energy given",
              "  to the load (1/2 J w^2, no-load case); a load torque and a",
              "  weak supply add to it; compare the run-up time with the",
              "  safe stall time on the motor data sheet"]
    emit("z_accel", lines)
    keys = list(curves)
    rows = []
    for i in range(0, 1500, 20):                        # every 20 ms to 1.5 s
        rows.append([f"{curves[keys[0]][i][0]:.2f}"]
                    + [f"{curves[k][i][1]:.1f}" for k in keys])
    csv("ch08-accel.csv", "t,n100,n94,n81", rows)


def cogging() -> None:
    n = 1155.0                                                    # A-047
    combos = [(54, 6, 9, "q 3, full pitch"), (54, 6, 8, "q 3, 8/9 pitch"),
              (48, 8, 5, "q 2, 5/6 pitch"), (54, 8, 7, "q 2.25"),
              (36, 8, 4, "q 1.5"), (12, 10, 1, "tooth coils"),
              (9, 8, 1, "tooth coils")]                           # A-142
    lines = ["slot-pole choices for the geared generator at 1155 rpm (A-142):",
             "  Q / p   winding          k_w1   lcm  gcd  cogging Hz  f_el Hz"]
    for q, p, y, note in combos:
        kw = m.winding_factor(q, p, y)
        nc, g = m.cogging_periods(q, p)
        lines.append(f"  {q:2d}/{p:<3d}  {note:15s}  {kw:.3f}  {nc:4d}  {g:3d}"
                     f"  {nc * n / 60:10.0f}  {p * n / 120:7.2f}")
    slot_mech = 360 / 54
    skew_el = 3 * slot_mech
    lines += ["  higher lcm and lower gcd: weaker, higher-frequency cogging;",
              "  tooth coils: short end windings, but lower k_w1 and more",
              "  air-gap harmonics (rotor and magnet losses)",
              f"  54/6 skewed one slot pitch ({slot_mech:.2f} deg mech = "
              f"{skew_el:.0f} deg el):",
              f"    k_skew {m.skew_factor(skew_el):.4f}: the EMF falls by "
              f"{100 * (1 - m.skew_factor(skew_el)):.1f} %,",
              "    and the slot-harmonic EMFs (17th, 19th) are multiplied",
              f"    by {m.skew_factor(skew_el, 17):.3f} and "
              f"{abs(m.skew_factor(skew_el, 19)):.3f}"]
    emit("z_cogging", lines)


# [start: capability]
def capability_limits(p: float, xd: float, e_max: float, d_max_deg: float):
    """Reactive range (pu, generator convention) of a round-rotor machine
    at active power p: stator circle, field circle, stability margin."""
    r_f = e_max / xd                                # field circle radius
    q_hi = min(math.sqrt(max(0.0, 1 - p * p)),
               math.sqrt(max(0.0, r_f * r_f - p * p)) - 1 / xd)
    q_lo = max(-math.sqrt(max(0.0, 1 - p * p)),
               -1 / xd + p / math.tan(math.radians(d_max_deg)))
    return q_lo, q_hi
# [end: capability]


def capability() -> None:
    xd, p_max, d_max = 2.5, 0.8, 70.0                    # A-113, A-143
    i_r = polar(1.0, -math.degrees(math.acos(0.8)))
    e_max = abs(m.sm_emf(1 + 0j, i_r, xd))
    lines = [f"backup generator 200 kVA, x_d {xd} pu (A-113),",
             f"  engine {p_max} pu, delta max {d_max:.0f} deg (A-143)",
             "  field limit from the rated point (pf 0.8): "
             f"E_max {e_max:.2f} pu,",
             f"  field circle centre -1/x_d = {-1 / xd:.2f} pu",
             "  P pu     Q min      Q max     (pu of 200 kVA)"]
    for p in (0.0, 0.2, 0.4, 0.6, 0.8):
        lo, hi = capability_limits(p, xd, e_max, d_max)
        lines.append(f"  {p:4.1f}  {lo:8.3f}  {hi:8.3f}")
    day_p, day_q = 112.0, 64.0                            # x_backup, A-129
    night = [("UPS", 12.0, 0.9), ("SCADA", 8.0, 0.95), ("lighting", 3.0, 0.95)]
    n_p = sum(x[1] for x in night)
    n_q = sum(x[1] * math.tan(math.acos(x[2])) for x in night)
    lines.append("  operating points (generator convention, + = delivered):")
    pts = [("essential loads, day", day_p, day_q)]
    for c in (50.0, 100.0):                                       # A-143
        pts.append((f"night, UPS filter {c:.0f} kvar", n_p, n_q - c))
    rows = []
    for name, pk, qk in pts:
        p, q = pk / 200, qk / 200
        lo, hi = capability_limits(p, xd, e_max, d_max)
        ok = "inside" if lo <= q <= hi else "OUTSIDE"
        i = complex(p, -q)                         # I = conj(S) / V, V = 1
        e = m.sm_emf(1 + 0j, i, xd)
        dl = math.degrees(math.atan2(e.imag, e.real))
        lines.append(f"  {name:26s} P {p:5.3f} Q {q:6.3f}: E {abs(e):.2f},"
                     f" delta {dl:5.1f} {ok}")
        rows.append((f"{q:.3f}", f"{p:.3f}"))
    lines += ["  a leading load drives the machine under-excited; near the",
              "  limit the AVR loses control and the voltage can run away:",
              "  check UPS and filter reactive power against the maker's",
              "  capability chart"]
    emit("z_capability", lines)
    csv("ch08-capab-pts.csv", "q,p", rows)
    bound = []
    steps = 40
    for k in range(steps + 1):
        p = p_max * k / steps
        bound.append((capability_limits(p, xd, e_max, d_max)[1], p))
    for k in range(steps, -1, -1):
        p = p_max * k / steps
        bound.append((capability_limits(p, xd, e_max, d_max)[0], p))
    csv("ch08-capab.csv", "q,p", [(f"{q:.4f}", f"{p:.4f}") for q, p in bound])


if __name__ == "__main__":
    unbalance()
    acceleration()
    cogging()
    capability()
