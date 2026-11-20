"""Chapter 41, lesson E - the module in the plant: connector pairs, the
string check with the lot's own Voc, clamping positions found at the site,
frame bonding, cable loops and lightning, string wiring against uneven
soiling, string monitoring that finds a shorted diode, PID exposure along
a string, the electroluminescence sample at the site, and spare modules
of another class.

Run from the project root:   python -m companion.ch41.examples_e
Writes companion/ch41/expected/e_*.txt and diagrams/data/ch41-*.csv.
Teaching values (A-448); D-012/D-013 string and block layout.
"""
from __future__ import annotations

import math
import random
from statistics import mean, pstdev

import numpy as np

from companion.ch41 import sources as src
from companion.ch41.common import csv, emit
from plantp import pvfab as fab
from plantp.mppt import PVM_550, Curve

BASE = PVM_550.at(1000.0, 25.0)
N_STR = src.PLANT["modules_string"]


def module(scale_i: float = 1.0, scale_v: float = 1.0) -> Curve:
    return Curve(BASE.isc * scale_i, BASE.voc * scale_v,
                 BASE.imp * scale_i, BASE.vmp * scale_v)


# ------------------------------------------------------ connectors
def connectors(i: float = 13.11, r_th: float = 25.0) -> dict[str, float]:
    pairs = src.MODULES_PLANT + 21 * 20 * 10 * 2       # module joints + ends
    lines = [f"connector pairs in Plant P: about {pairs:,} (teaching)",
             "  pair                          contact mOhm   heat W   rise K"]
    out = {}
    for name, r in (("same maker and type", 0.25),
                    ("cross-mated, new", 1.5),
                    ("cross-mated, aged", 10.0)):
        p = i * i * r / 1000
        out[name] = p
        lines.append(f"  {name:29s} {r:12.2f}   {p:6.2f}   {p * r_th:6.1f}")
    lines += ["  the energy is small; the heat is not: an aged mixed pair",
              "  runs tens of kelvin hotter inside a plastic body, and a",
              "  joint that opens under load arcs - pairs of one maker and",
              "  type (IEC 62852), crimped with that maker's tool, and the",
              "  module's connector type is fixed in the purchase order"]
    emit("e_connectors", lines)
    return out


# ------------------------------------------------------ the lot's own Voc
def string_check() -> dict[str, float]:
    from companion.ch41.lab_d import corrected, drift_quiet, parse
    good, _, _ = parse()
    fixed = [r for r in corrected(good, drift_quiet()) if r["p"] > 400]
    vocs = sorted(r["voc"] for r in fixed)
    beta, t_min, v_max = -0.27, src.PLANT["t_min_c"], src.PLANT["v_max"]
    k = 1 + beta / 100 * (t_min - 25)
    cases = {"data sheet 49.90 V": 49.90, "lot mean": mean(vocs),
             "lot 99th percentile": vocs[int(0.99 * len(vocs))],
             "lot maximum": vocs[-1]}
    lines = [f"26-module string at {t_min:.0f} C, beta -0.27 %/K (factor "
             f"{k:.3f})", "  module Voc used         V        string V   "
             "margin to 1,500 V"]
    out = {}
    for name, v in cases.items():
        s = N_STR * v * k
        out[name] = s
        lines.append(f"  {name:22s} {v:6.2f}   {s:8.0f}   {v_max - s:+8.0f} V")
    lines += ["  even 26 of the highest-Voc modules stay below 1,500 V; the",
              "  margin a string design keeps is for exactly this: lot",
              "  spread, the coefficient's tolerance and a colder morning",
              f"  (max string length by the linear rule: "
              f"{fab.max_string_length(vocs[-1], beta, t_min, v_max)})"]
    emit("e_string", lines)
    return out


# ------------------------------------------------------ clamps at the site
def clamp_survey(seed: int = 4110, lo: float = 400.0, hi: float = 550.0):
    rng = random.Random(seed)
    pos = [rng.gauss(472, 30) for _ in range(180)] + \
          [rng.gauss(380, 12) for _ in range(20)]       # one crew's habit
    out = sum(1 for x in pos if not lo <= x <= hi)
    crew = sum(1 for x in pos[180:] if x < lo)
    lines = [f"clamp positions measured on 200 clamps (zone {lo:.0f}-{hi:.0f}"
             " mm, teaching)",
             f"  mean {mean(pos):.0f} mm, sd {pstdev(pos):.0f} mm; outside "
             f"the zone: {out}",
             f"  {crew} of them come from one crew's 20 tables: a template",
             "  set wrong, not random error - the crew's tables are",
             "  re-clamped and the template checked; the sample is taken",
             "  by crew and by day, so a habit shows as a group"]
    emit("e_clamps", lines)
    return dict(out=out, crew=crew)


# ------------------------------------------------------ frame bonding
def bonding(seed: int = 4111, limit: float = 0.5) -> dict[str, int]:
    rng = random.Random(seed)
    r = [abs(rng.gauss(0.08, 0.03)) for _ in range(60)]
    for k in (17, 44):
        r[k] = 4.2 if k == 17 else 1.3                 # washer missing
    bad = [k + 1 for k, x in enumerate(r) if x > limit]
    lines = [f"frame-to-earth continuity on 60 tables (teaching limit "
             f"{limit} ohm)",
             f"  median {sorted(r)[30]:.2f} ohm; above the limit: tables "
             f"{bad}",
             "  a missing serrated washer leaves the frame bonded through",
             "  paint and anodising - the reading jumps by orders of",
             "  magnitude, not by a little: the test finds an absent",
             "  joint, so it is done on every table, not on a sample"]
    emit("e_bonding", lines)
    return dict(bad=len(bad))


# ------------------------------------------------------ loops and lightning
def loops(d: float = 50.0, didt: float = 1e10) -> dict[str, float]:
    mu = 2e-7                                       # mu0 / 2 pi
    length = N_STR * 1.134
    cases = {"return beside the outgoing cable": 0.3 * length * 0.02,
             "return along the far table edge": length * 2.3}
    lines = [f"voltage induced in a string loop by a strike {d:.0f} m away"
             " (10 kA/us, teaching)",
             "  routing                              loop m2   volts"]
    out = {}
    for name, a in cases.items():
        v = mu * a / d * didt
        out[name] = v
        lines.append(f"  {name:36s} {a:7.1f}   {v:6.0f}")
    lines += ["  the loop area, not the cable size, decides the surge: the",
              "  return conductor runs beside the outgoing one along the",
              "  table - a routing rule on the drawings, checked at the",
              "  site, that costs nothing when planned"]
    emit("e_loops", lines)
    return out


# ------------------------------------------------------ wiring vs soiling
def wiring(lower: float = 0.97) -> dict[str, float]:
    row = [module(1.0)] * N_STR
    low_row = [module(lower)] * N_STR
    u_string = [module(1.0)] * (N_STR // 2) + [module(lower)] * (N_STR // 2)
    alone = 2 * N_STR * BASE.mpp()[1]
    one_row = fab.string_pmax(row) + fab.string_pmax(low_row)
    two_u = 2 * fab.string_pmax(u_string)
    lines = [f"2P table, lower row {1 - lower:.0%} more soiled: two strings "
             "per table",
             f"  each string in one row     {one_row / 1000:7.3f} kW",
             f"  each string half in each   {two_u / 1000:7.3f} kW",
             f"  modules alone (no mismatch) {alone * (1 + lower) / 2 / 1000:6.3f}"
             " kW",
             f"  the U-shaped strings lose {1 - two_u / one_row:.2%} more:"
             " the soiled half",
             "  limits the clean half; strings along a row keep each",
             "  string uniform - a wiring choice made on the drawing"]
    emit("e_wiring", lines)
    return dict(row=one_row, u=two_u)


# ------------------------------------------------------ string monitoring
def array_currents(strings, n_v: int = 3000):
    v_top = max(s.voc for s in strings)
    v = np.linspace(0, v_top, n_v)
    total = sum(s.i(v) for s in strings)
    k = int(np.argmax(v * total))
    return v[k], [float(s.i(v[k])) for s in strings]


def monitoring(seed: int = 4112, noise: float = 0.01,
               day_sd: float = 0.0025, fail_day: int = 30) -> dict:
    from plantp.performance import cusum
    rng = random.Random(seed)
    strings = []
    for j in range(20):
        sc = rng.gauss(1.0, noise)
        n_eq = N_STR - (1 / 3 if j == 7 else 0)
        strings.append(Curve(BASE.isc * sc, BASE.voc * n_eq,
                             BASE.imp * sc, BASE.vmp * n_eq))
    v, cur = array_currents(strings)
    healthy = list(strings)
    healthy[7] = Curve(strings[7].isc, BASE.voc * N_STR, strings[7].imp,
                       BASE.vmp * N_STR)
    _, cur0 = array_currents(healthy)
    others = [c for j, c in enumerate(cur) if j != 7]
    z = (cur[7] - mean(others)) / pstdev(others)
    step = cur[7] / cur0[7] - 1
    # the string's own ratio to its peers, day by day (persistent soiling
    # differences cancel; what is left is day-to-day noise)
    ratio = [rng.gauss(0, day_sd) + (step if d >= fail_day else 0.0)
             for d in range(60)]
    hit = cusum(ratio, k=abs(step) / 2, h=5 * day_sd)
    after = hit - fail_day if hit is not None else None
    csv("ch41-cusum.csv", "day,ratio",
        [(d + 1, round(100 * r, 3)) for d, r in enumerate(ratio)])
    lines = ["20 strings at one combiner; string 8 gets a shorted diode",
             f"  array operating voltage {v:.0f} V",
             f"  string 8: {cur[7]:.2f} A; others {mean(others):.2f} A, sd "
             f"{pstdev(others):.2f} (soiling 1 %)",
             f"  one day's comparison: {z:.1f} sd - lost in the spread",
             f"  its own ratio to the peers falls by {abs(step):.2%} at the "
             "failure;",
             f"  CUSUM on that ratio (day noise {day_sd:.2%}) signals on day "
             f"{hit + 1 if hit is not None else 'none'}",
             f"  ({after} day{'s' if after != 1 else ''} after the failure on "
             f"day {fail_day + 1}) - each string is",
             "  compared with its own history, not only with its",
             "  neighbours (ch 37); a whole open string shows at once"]
    emit("e_monitor", lines)
    return dict(z=z, step=step, hit=hit)


# ------------------------------------------------------ PID along a string
def pid(v_string: float = None) -> dict[str, int]:
    v_string = v_string or N_STR * BASE.vmp
    lines = [f"potential of each module to the frame, string at MPP "
             f"{v_string:.0f} V",
             "  earthing of the DC side       modules below -300 V   lowest V"]
    out = {}
    csv("ch41-pid.csv", "module,floating,negative",
        [(k + 1, round(-v_string / 2 + (k + 0.5) * v_string / N_STR, 1),
          round((k + 0.5) * v_string / N_STR, 1)) for k in range(N_STR)])
    for name, v_neg in (("floating, symmetric", -v_string / 2),
                        ("negative pole earthed", 0.0),
                        ("positive pole earthed", -v_string)):
        pots = [v_neg + (k + 0.5) * v_string / N_STR for k in range(N_STR)]
        n = sum(1 for p in pots if p < -300)
        out[name] = n
        lines.append(f"  {name:29s} {n:21d}   {min(pots):8.0f}")
    lines += ["  cells far below the frame's potential can lose power by",
              "  ion drift (PID): the module's PID test result (IEC TS",
              "  62804-1) and the inverter's earthing scheme are chosen",
              "  together; an inverter without isolation cannot earth a",
              "  pole, and night-time offset is a maker's option to ask"]
    emit("e_pid", lines)
    return out


# ------------------------------------------------------ EL sample at site
def el_sample() -> dict[float, int]:
    out = {}
    lines = ["electroluminescence after installation: sample to see a",
             "  cracked share with 95 % confidence (at least one in sample)",
             "  share cracked   modules to image   night hours at 120 / h"]
    for p in (0.02, 0.01, 0.005):
        n = math.ceil(math.log(0.05) / math.log(1 - p))
        out[p] = n
        lines.append(f"  {p:13.1%}   {n:16,d}   {n / 120:15.1f}")
    lines += ["  a sample shows whether cracks exist above a share, not",
              "  which modules have them; it is spread over blocks, crews",
              "  and delivery lots so a cause shows as a cluster"]
    emit("e_el", lines)
    return out


# ------------------------------------------------------ spare modules
def spares() -> dict[str, float]:
    base = fab.string_pmax([module()] * N_STR)
    out = {}
    lines = [f"one module replaced in a string of 26 x 550 W ({base:,.0f} W)",
             "  replacement                  string W   change W"]
    for name, p in (("same class 550 W", 550.0), ("higher class 560 W", 560.0),
                    ("lower class 540 W", 540.0), ("aged 520 W", 520.0)):
        s = math.sqrt(p / 550.0)
        st = [module(s, s)] + [module()] * (N_STR - 1)
        pw = fab.string_pmax(st)
        out[name] = pw - base
        lines.append(f"  {name:27s} {pw:9,.0f}   {pw - base:+8.1f}")
    lines += [f"  a 560 W spare returns {out['higher class 560 W'] / 10:.0%} of its"
              " extra 10 W, a 540 W",
              f"  one costs {-out['lower class 540 W']:.1f} W for its 10 W short,"
              " an aged 520 W one",
              f"  {-out['aged 520 W']:.1f} W for 30 W: the weak module sets the"
              " string's",
              "  current - spares of the same class, connector and clamping",
              "  zones (ch 39 stock)"]
    emit("e_spares", lines)
    return out


if __name__ == "__main__":
    connectors()
    string_check()
    clamp_survey()
    bonding()
    loops()
    wiring()
    monitoring()
    pid()
    el_sample()
    spares()
