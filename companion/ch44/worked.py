"""Chapter 44 - small worked examples (E-lines) and the numerical answers
of the exercises (P-lines), each computed here.

Run from the project root:   python -m companion.ch44.worked
Writes companion/ch44/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

from companion.ch44 import examples_a as ea
from companion.ch44 import examples_b as eb
from companion.ch44 import examples_c as ec
from companion.ch44 import integrated as it
from companion.ch44 import lab_d
from companion.ch44.common import emit
from plantp import convmfg as cm
from plantp import pe


def worked() -> None:
    lines = [f"E01 interface 100 um, k 0.8, 80 cm2: {cm.tim_r(100, 0.8, 80):.4f} K/W",
             f"E02 same with 40 % voids: {cm.tim_r(100, 0.8, 80, 0.4):.4f} K/W",
             f"E03 Tj at 494 W, 0.028 + 0.0156 + 0.016 K/W, 45 C: "
             f"{cm.tj(494, 0.028, 0.0156, 0.016, 45):.1f} C",
             f"E04 life at a 37.2 K swing against 29.5 K: "
             f"{pe.relative_cycle_life(37.2, 29.5):.0%}",
             f"E05 shares of 0.985 / 1.015: "
             + " / ".join(f"{x:.3f}" for x in cm.shares([0.985, 1.015])),
             f"E06 solder strain, 3.2 mm, 11 ppm, 40 K, 0.1 mm: "
             f"{cm.solder_strain(3.2, 11, 40, 0.1):.4f}",
             f"E07 cycles at that strain: {cm.cycles_to_failure(0.0141):,.0f}",
             f"E08 800 ppm bridges after 85 % and 60 % stations: "
             f"{800 * 0.15 * 0.4:.0f} ppm",
             f"E09 fingerprint of {{'a': 1}}: {cm.fingerprint({'a': 1})}",
             f"E10 units to show R 90 % at 90 % confidence: "
             f"{ec.demonstration()['n']}"]
    emit("worked", lines)


def solutions() -> None:
    tr = ea.tree()
    ifc = ea.interfaces()
    ci = ea.config_items()
    fl = ea.fleet()
    ti = eb.tim_states()
    pa = eb.parallel()
    ca = eb.caps()
    so = eb.solder()
    cr = eb.creepage()
    de = eb.derate()
    jo = eb.joint()
    out = [f"P01 inverter mass, cost and FIT: {tr['mass'] / 1000:.1f} t, "
           f"{tr['cost']:,.0f} k u, {tr['fit']:,.0f}",
           f"P02 largest failure contributor: {tr['top']}",
           f"P03 interfaces: {ifc}",
           f"P04 configuration items: {ci}",
           f"P05 modules and boards in the PV fleet: {fl['modules']}, {fl['boards']}",
           f"P06 Tj as designed / dried interface: "
           f"{ti['as designed']['tj']:.0f} / {ti['pumped out and dried']['tj']:.0f} C",
           f"P07 cycle life with a dried interface: "
           f"{ti['pumped out and dried']['life']:.0%}",
           f"P08 Tj rise with a 6 % spread: {pa[0.06]:.1f} K",
           f"P09 hottest capacitor current, heat and life: {ca['hot']:.2f}, "
           f"{ca['heat']:.2f}, x{ca['life']:.2f}",
           f"P10 shunt cycles at 40 K: {so['2512 current shunt'][1]:,.0f}",
           f"P11 creepage pairs failing: {sum(1 for v in cr.values() if not v)}",
           f"P12 parts over the derating rule: {len(de)}",
           f"P13 joint heat at 25 % preload: {jo[0.25]:.1f} W"]
    out += more()
    emit("solutions", out)


def more() -> list[str]:
    ln = ec.line()
    tw = ec.tim_weight()
    fp = ec.fingerprints()
    ge = ec.genealogy()
    eo = ec.eol()
    br = ec.brokers()
    mc = lab_d.montecarlo()
    sm = lab_d.statemachine()
    mp = lab_d.mppt_eff()
    trc = lab_d.trace()
    hb = it.by_hand()
    return [f"P14 escaping ppm and most frequent escape: {ln['out']:.1f}, {ln['worst']}",
            f"P15 paste target and reprints: {tw['target']:.2f} g, {len(tw['bad'])}",
            f"P16 inverters with a different fingerprint: {', '.join(fp['odd'])}",
            f"P17 inverters with lot L2212: {ge['n']}",
            f"P18 tree items without an end-of-line test: {eo['missing']}",
            f"P19 doubtful broker lines left: {br['left']:.1f}",
            f"P20 hottest module and its Tj: {mc['pos']}, {mc['max']:.1f} C",
            f"P21 test cases passed, v1.0 / v0.9: {sm['v10']} / {sm['v09']}",
            f"P22 ramp MPPT efficiency, P&O / hold-compare: "
            f"{mp['perturb and observe']['ramp']:.2%} / "
            f"{mp['perturb-hold-compare']['ramp']:.2%}",
            f"P23 trace rows done / open: {trc.get('done', 0)} / {trc.get('open', 0)}",
            f"P24 stack current, module loss and Tj: {hb['i_rms']:,.0f} A, "
            f"{hb['per_module']:.0f} W, {hb['t_j']:.1f} C"]


if __name__ == "__main__":
    worked()
    solutions()
