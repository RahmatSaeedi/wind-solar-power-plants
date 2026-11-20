"""Chapter 41, lesson C - the module as a product and its reliability:
bill of materials, cell-to-module ratio, the half-cut layout as a design
for shading, lamination control, what accelerated tests do and do not
say, clamping zones, bypass-diode heat, insulation of a whole block,
defects and the failure-analysis ladder, transport screening, repair
limits, and qualification against production tests.

Run from the project root:   python -m companion.ch41.examples_c
Writes companion/ch41/expected/c_*.txt and diagrams/data/ch41-*.csv.
Teaching values (A-444, A-445); a fictional module maker.
"""
from __future__ import annotations

import math
import random
from statistics import mean

import numpy as np

from companion.ch41 import sources as src
from companion.ch41.common import csv, emit
from plantp.mppt import PVM_550, Curve

BASE = PVM_550.at(1000.0, 25.0)        # module curve at STC (ch 15 model)
K_EV = 8.617e-5                        # Boltzmann constant, eV/K


# ------------------------------------------------------------ BOM
def bom() -> dict[str, float]:
    total = sum(r[1] * 0 + r[3] for r in src.BOM)
    lines = [f"bill of materials of one PVM-550 ({total:.1f} kg)",
             "  part                                mass kg  share  control"]
    for part, qty, unit, kg, ctrl in src.BOM:
        lines.append(f"  {part:36s} {kg:6.2f}  {kg / total:5.0%}  {ctrl}")
    glass = src.BOM[0][3]
    lines += [f"  glass is {glass / total:.0%} of the mass; for {src.MODULES_PLANT:,}"
              f" modules the plant receives {total * src.MODULES_PLANT / 1000:,.0f} t",
              "  every line has a control: the BOM is also the list of",
              "  incoming inspections and of the parts whose change needs",
              "  re-qualification (lesson C, tests)"]
    emit("c_bom", lines)
    return dict(total=total)


# ------------------------------------------------------ cell-to-module
# [start: ctm]
CTM = [("cell power, 72 cells x 7.71 W", None),
       ("glass and encapsulant absorption and reflection", 0.985),
       ("light from the gaps returned by the backsheet", 1.015),
       ("interconnect resistance (half-cut, ch 10)", 0.9955),
       ("cell mismatch within the module", 0.998),
       ("junction box and cables", 0.999)]   # A-444
# [end: ctm]


def ctm() -> dict[str, float]:
    p = 72 * 7.71
    lines = ["cell-to-module: from 72 x 7.71 W to the module",
             "  step                                              factor   power W",
             f"  {CTM[0][0]:48s}      -   {p:7.1f}"]
    for name, k in CTM[1:]:
        p *= k
        lines.append(f"  {name:48s}  {k:6.4f}   {p:7.1f}")
    ratio = p / (72 * 7.71)
    lot = mean(src.FLASH)
    lines += [f"  cell-to-module ratio {ratio:.3f}; the lot of lesson D averages"
              f" {lot:.1f} W",
              "  a ratio near 1 is not free: it needs AR glass, reflective",
              "  backsheet and low-loss joints, each a BOM choice"]
    emit("c_ctm", lines)
    return dict(p=p, ratio=ratio)


# ------------------------------------------ the half-cut layout and shade
def _string(n: int, scale: float, half: bool) -> Curve:
    k = 0.5 if half else 1.0
    return Curve(BASE.isc * k * scale, BASE.voc / 72 * n,
                 BASE.imp * k * scale, BASE.vmp / 72 * n)


def _block_v(curves, i: float, v_bypass: float = 0.5) -> float:
    """Voltage of strings in parallel at total current i (bisection)."""
    if i >= sum(c.isc for c in curves):
        return -v_bypass
    lo, hi = 0.0, max(c.voc for c in curves)
    for _ in range(60):
        mid = (lo + hi) / 2
        if sum(float(c.i(mid)) for c in curves) > i:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def module_pmax(blocks) -> float:
    """Blocks in series, each a parallel set of strings with one bypass."""
    i_top = max(sum(c.isc for c in b) for b in blocks)
    best = 0.0
    for i in np.linspace(0.0, i_top, 700):
        v = sum(_block_v(b, i) for b in blocks)
        best = max(best, v * i)
    return best


# [start: layout]
def layouts(row_shade: float = 0.5) -> dict[str, dict[str, float]]:
    """Portrait module, three bypass diodes. Full cells: three strings of
    24 cells, each crossing the bottom row. Half-cut: in each third an
    upper and a lower string of 24 half cells in parallel."""
    full = {"none": [[_string(24, 1, False)]] * 3,
            "bottom row": [[_string(24, row_shade, False)]] * 3,
            "one column": [[_string(24, row_shade, False)]]
            + [[_string(24, 1, False)]] * 2}
    half = {"none": [[_string(24, 1, True), _string(24, 1, True)]] * 3,
            "bottom row": [[_string(24, 1, True),
                            _string(24, row_shade, True)]] * 3,
            "one column": [[_string(24, row_shade, True),
                            _string(24, row_shade, True)]]
            + [[_string(24, 1, True), _string(24, 1, True)]] * 2}
    return {k: {"full": module_pmax(full[k]), "half": module_pmax(half[k])}
            for k in full}
# [end: layout]


def layout_lesson() -> dict[str, dict[str, float]]:
    r = layouts()
    p0 = r["none"]["full"]
    csv("ch41-layout.csv", "case,full,half",
        [(k, round(v["full"] / p0 * 100), round(v["half"] / p0 * 100))
         for k, v in zip((1, 2, 3), r.values())])
    lines = ["shade on a portrait module (cells at 50 % light), ch 15 curves",
             "  shade                full cells      half-cut cells"]
    for k, v in r.items():
        lines.append(f"  {k:18s} {v['full']:7.1f} W {v['full'] / p0:4.0%}"
                     f"   {v['half']:7.1f} W {v['half'] / p0:4.0%}")
    lines += ["  a shaded bottom row (soiling at the lower frame, the next",
              "  row's shadow at low sun) limits every full-cell string;",
              "  in the half-cut module only the lower halves are limited",
              "  and the upper halves carry on - a design for shading;",
              "  a shaded column takes one third in both layouts: the",
              "  layout helps only for shade along the short side"]
    emit("c_layout", lines)
    return r


# ------------------------------------------------ lamination control
def lamination(seed: int = 4106) -> dict[str, list[int]]:
    rng = random.Random(seed)
    data = {}
    for lam in ("L1", "L2", "L3"):
        vals = []
        for d in range(30):
            mu = 84.0 - (0.35 * (d - 14) if lam == "L2" and d >= 15 else 0)
            vals.append(round(rng.gauss(mu, 1.2), 1))
        data[lam] = vals
    lsl = 75.0                                  # encapsulant maker's minimum
    out, rows = {}, []
    lines = ["gel content of one daily sample per laminator (%, 30 days)",
             "  individuals chart from days 1-15",
             f"  lower specification {lsl:.0f} % (encapsulant maker, teaching)"]
    for lam, v in data.items():
        base = v[:15]
        mr = mean(abs(a - b) for a, b in zip(base[1:], base))
        cl = mean(base)
        lcl = cl - 2.66 * mr
        sig = [d + 1 for d, x in enumerate(v) if x < lcl]
        out[lam] = sig
        first = sig[0] if sig else None
        lines.append(f"  {lam}: centre {cl:.1f}, LCL {lcl:.1f}; first signal "
                     f"day {first if first else 'none'}; below spec: "
                     f"{sum(x < lsl for x in v)} days")
        for d, x in enumerate(v):
            rows.append((lam, d + 1, x))
    csv("ch41-gel.csv", "day,gel", [(r[1], r[2]) for r in rows if
                                        r[0] == "L2"])
    worst = min(data["L2"])
    lines += [f"  L2 drifts from day 16; the chart signals on day "
              f"{out['L2'][0]}, while",
              f"  every sample still meets the specification (lowest "
              f"{worst:.1f} %):",
              "  the drift is caught before it makes a defect - modules since",
              "  the signal are held and traced (genealogy, lesson B) and",
              "  the laminator's own record (temperature, time) is checked;",
              "  low gel content shows later as creep and delamination"]
    emit("c_lamination", lines)
    return out


# ------------------------------------------ accelerated tests are not lives
def acceleration() -> dict[str, float]:
    t_test, t_field = 85 + 273.15, 35 + 273.15
    lines = ["damp heat 1,000 h at 85 C / 85 % RH: what does it equal?",
             "  (Peck model, AF = exp(Ea/k (1/Tf - 1/Tt)) (RHt/RHf)^3,",
             "  field module at 35 C - all teaching values)",
             "  Ea eV   RH field   acceleration   1,000 h equals"]
    out = {}
    for ea in (0.5, 0.7, 0.9):
        for rh in (30.0, 60.0):
            af = math.exp(ea / K_EV * (1 / t_field - 1 / t_test)) \
                * (85.0 / rh) ** 3
            out[(ea, rh)] = af
            lines.append(f"  {ea:5.1f}   {rh:6.0f} %   {af:12,.0f}   "
                         f"{1000 * af / 8760:8,.0f} years")
    n = 2.0
    af_tc = (125.0 / 40.0) ** n
    span = max(out.values()) / min(out.values())
    lines += [f"  thermal cycling -40..85 C against 40 K field days (n = 2):",
              f"    AF {af_tc:.1f}: 200 cycles = {200 * af_tc / 365:.1f} "
              "years of daily cycles",
              f"  the answer spans a {span:.0f}-fold range with plausible",
              "  inputs: qualification tests screen a design for known",
              "  weaknesses and compare designs - they do not predict life"]
    emit("c_accel", lines)
    return dict(min=min(out.values()), max=max(out.values()), tc=af_tc)


# ------------------------------------------------ clamping zones
def clamping(length_m: float = 2.278, area_m2: float = 2.583,
             load_pa: float = 2400.0) -> dict[str, float]:
    w = load_pa * area_m2 / length_m          # N per metre along the module
    rows = []
    for k in range(0, 41):
        a = k * 0.01 * length_m
        if 2 * a >= length_m:
            break
        m_sup = w * a * a / 2
        m_mid = w * (length_m - 2 * a) ** 2 / 8 - m_sup
        rows.append((round(a / length_m, 3), round(max(m_sup, m_mid), 2)))
    a_opt = length_m / (2 + 2 * math.sqrt(2))
    m_opt = w * a_opt ** 2 / 2
    m_end = w * length_m ** 2 / 8
    csv("ch41-clamp.csv", "a,m", rows)
    lines = [f"clamping zones of a {length_m} m module under {load_pa:.0f} Pa"
             " (teaching)",
             f"  load {load_pa * area_m2 / 1000:.2f} kN; per clamp (four) "
             f"{load_pa * area_m2 / 4000:.2f} kN",
             f"  supports at the ends: largest bending moment {m_end:.0f} N m",
             f"  supports {a_opt * 1000:.0f} mm in from each end (0.207 L): "
             f"{m_opt:.0f} N m",
             f"  {m_end / m_opt:.1f} times less bending in the glass and the "
             "cells: the maker's",
             "  clamping zones sit near this point, and a clamp outside",
             "  them can void the mechanical rating (cracked cells under",
             "  snow or wind); the mounting interface is part of the",
             "  module's design, checked at the site (lesson E)"]
    emit("c_clamp", lines)
    return dict(a=a_opt, ratio=m_end / m_opt)


# ------------------------------------------------ bypass-diode heat
def diode_heat(t_box: float = 70.0, vf: float = 0.45, r_th: float = 9.0,
               coupling: float = 3.0, t_max: float = 200.0):
    i = BASE.isc * 1.25                        # high irradiance, A
    lines = [f"bypass diodes conducting {i:.1f} A (1,250 W/m2), box at "
             f"{t_box:.0f} C (teaching)",
             "  diodes on   heat each W   junction C   margin to the rating"]
    out = {}
    for n_on in (1, 2, 3):
        p = i * vf
        tj = t_box + p * r_th + (n_on - 1) * p * coupling
        out[n_on] = tj
        lines.append(f"  {n_on:9d}   {p:11.1f}   {tj:10.0f}   "
                     f"{t_max - tj:+8.0f} K")
    lines += ["  one diode bypassing all afternoon (a pole's shadow) runs",
              "  hot for hours a day: the bypass-diode thermal test checks",
              "  the box design; in the plant, string monitoring finds a",
              "  module that loses a third (lesson E)"]
    emit("c_diode", lines)
    return out


# ------------------------------------------------ insulation of a block
def insulation(r_dry: float = 400e6, r_wet: float = 40e6) -> dict[str, float]:
    n = 21 * 20 * 26                           # modules in one PV block
    v_mid = 1091.0 / 2                         # string at MPP, floating
    out = {}
    lines = [f"insulation of one PV block: {n:,} modules in parallel to earth",
             "  module (teaching)   block resistance   leakage at 545 V"]
    for name, r in (("dry 400 MOhm", r_dry), ("dew 40 MOhm", r_wet)):
        rb = r / n
        out[name] = rb
        lines.append(f"  {name:17s}   {rb / 1000:12.1f} kOhm   "
                     f"{v_mid / rb * 1000:10.0f} mA")
    lines += ["  each module passes its own insulation test by a wide margin,",
              "  yet ten thousand in parallel look like a few kilohms on a",
              "  dew morning: the inverter's insulation check may delay the",
              "  start until the array dries (energy lost at sunrise) - the",
              "  threshold is a setting agreed with the inverter maker, and",
              "  a falling trend points at a damaged cable or connector"]
    emit("c_insulation", lines)
    return out


# ------------------------------------------------ defects and analysis
LADDER = ["visual inspection and records (serial, lot, flash)",
          "I-V curve against the flash record",
          "electroluminescence image (cracks, dark cells, contacts)",
          "infrared image under current (hot cells, joints, diodes)",
          "insulation and wet leakage",
          "junction box opened: diodes, joints, potting",
          "destructive: cross-section, peel, chemical analysis"]


def defects() -> None:
    lines = ["module defects: cause, how found, what follows"]
    for name, cause, found, then in src.DEFECTS:
        lines += [f"  {name}", f"    cause: {cause}",
                  f"    found by: {found}", f"    then: {then}"]
    lines += ["  failure analysis ladder, non-destructive steps first:"]
    for k, step in enumerate(LADDER, 1):
        lines.append(f"    {k}. {step}")
    lines += ["  each step keeps the evidence for the next; a module cut",
              "  open first cannot be flashed again"]
    emit("c_defects", lines)


# ------------------------------------------------ transport screening
def transport(n: int = 31, normal: float = 0.005, bad: float = 0.08,
              c: int = 2) -> dict[str, float]:
    def p_ge(lam, k):
        return 1 - sum(math.exp(-lam) * lam ** j / math.factorial(j)
                       for j in range(k))
    out = {"false": p_ge(n * normal, c), "catch": p_ge(n * bad, c)}
    lines = [f"transport screening: EL of one pallet ({n} modules) a container",
             f"  rule: {c} or more cracked modules -> EL the whole container",
             f"  normal handling ({normal:.1%} cracked): opened by mistake "
             f"{out['false']:.1%}",
             f"  rough handling ({bad:.0%} cracked): caught {out['catch']:.0%}",
             f"  with 177 containers (ch 10) about {177 * out['false']:.0f} "
             "opened needlessly",
             "  shock indicators and pallet damage pick the pallet to image;",
             "  a crack found at receipt is a claim against the carrier or",
             "  the maker; one found after installation is the plant's"]
    emit("c_transport", lines)
    return out


# ------------------------------------------------ repair limits
REPAIR = [
    ("connector damaged", "replace with the same maker and type",
     "insulation, polarity, I-V"),
    ("junction-box lid or potting", "only by the maker's procedure",
     "insulation, diode check"),
    ("bypass diode failed", "maker's procedure, if the box allows",
     "diode check, I-V, IR"),
    ("frame bent", "replace the module", "-"),
    ("glass or laminate broken", "replace the module", "-"),
    ("backsheet scratch", "maker's assessment; tape not a repair",
     "insulation, wet leakage"),
]


def repair() -> None:
    lines = ["repair limits (concept; the maker's warranty terms decide)",
             "  defect                        action"]
    for d, act, test in REPAIR:
        lines += [f"  {d:29s} {act}", f"  {'':29s} then: {test}"]
    lines += ["  the laminate cannot be opened and closed again; what can",
              "  be repaired is outside it, and every repair is followed",
              "  by the tests that the repair could have upset"]
    emit("c_repair", lines)


# ------------------------------------------ qualification vs production
TESTS = [  # test, purpose, when
    ("power at STC (flash)", "rating, label, binning", "every module"),
    ("electroluminescence", "cracks, dark cells, joints", "every module"),
    ("insulation, earth link", "safety of the package", "every module"),
    ("visual and dimensions", "workmanship, frame, labels", "every module"),
    ("wet leakage", "insulation when wet", "sample + qual."),
    ("thermal cycling", "joints and interconnects", "qual. + retest"),
    ("damp heat", "moisture, adhesion, corrosion", "qual. + retest"),
    ("humidity freeze", "edge seal, junction box", "qual. + retest"),
    ("mechanical load", "frame, glass, cells", "qual. + retest"),
    ("hail", "glass", "qualification"),
    ("hot spot", "cell reverse bias", "qualification"),
    ("bypass diode thermal", "junction box heat", "qualification"),
    ("PID", "voltage-induced loss", "qual. + retest"),
    ("transport (package)", "shipping unit", "package qual."),
]


def tests() -> None:
    lines = ["module tests: purpose and when they run",
             "  test                       when           purpose"]
    for t, p, w in TESTS:
        lines.append(f"  {t:26s} {w:14s} {p}")
    every = sum(1 for _, _, w in TESTS if w == "every module")
    lines += [f"  {every} tests run on every module; the rest qualify a design",
              "  (IEC 61215, IEC 61730) on a few samples, and are repeated",
              "  when the BOM or process changes (IEC TS 62915); the",
              "  factory's quality system keeps them valid between (IEC",
              "  62941) - a certificate covers the BOM that was tested"]
    emit("c_tests", lines)


if __name__ == "__main__":
    bom()
    ctm()
    layout_lesson()
    lamination()
    acceleration()
    clamping()
    diode_heat()
    insulation()
    defects()
    transport()
    repair()
    tests()
