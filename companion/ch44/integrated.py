"""Chapter 44 - three integrated Plant P examples: one stack's loss and
junction temperature by hand, the acceptance of the ten PCI-5500 at the
factory, and the converter manufacturing and acceptance basis D-048.

Run from the project root:   python -m companion.ch44.integrated
Writes companion/ch44/expected/int_*.txt.
"""
from __future__ import annotations

import math

from companion.ch44 import sources as src
from companion.ch44.common import emit
from plantp import convmfg as cm


# [start: hand]
def by_hand() -> dict[str, float]:
    inv, st = src.INVERTER, src.STACKUP
    i_rms = inv["s_stack_mva"] * 1e6 / (math.sqrt(3) * inv["v_ll"])
    p_stack_kw = inv["s_stack_mva"] * 1000 * inv["pf"]
    modules = inv["positions"] * inv["parallel"]
    mean_w = inv["loss_stack_kw"] * 1000 / modules
    r_tim = cm.tim_r(st["tim_um"], st["tim_k"], st["tim_area_cm2"])
    t_j = cm.tj(st["p_module_w"], st["r_jc"], r_tim, st["r_hs"],
                inv["coolant_c"])
    eta_semis = 1 - inv["loss_stack_kw"] / p_stack_kw
    # [end: hand]
    lines = ["one stack of the PCI-5500 by hand",
             f"  {inv['s_stack_mva']} MVA at {inv['v_ll']:.0f} V: line current "
             f"{i_rms:,.0f} A rms",
             f"  semiconductor loss {inv['loss_stack_kw']} kW over "
             f"{inv['positions']} x {inv['parallel']} modules: mean {mean_w:.0f} W,",
             f"    but the outer switch T1 carries {st['p_module_w']:.0f} W a module"
             " (lesson A)",
             f"  R_jc {st['r_jc']} + interface {r_tim:.4f} + plate {st['r_hs']} = "
             f"{st['r_jc'] + r_tim + st['r_hs']:.4f} K/W",
             f"  Tj of the hottest module at {inv['coolant_c']:.0f} C coolant: "
             f"{t_j:.1f} C (ch 9: 75 C)",
             f"  semiconductor efficiency at {p_stack_kw:,.0f} kW: {eta_semis:.2%}"
             " (other losses on top)",
             "  check: four stacks carry 5.5 MVA; 24 modules a stack is 12",
             "  positions with 2 in parallel (ch 9, ratings)"]
    emit("int_hand", lines)
    return dict(i_rms=i_rms, per_module=st["p_module_w"], mean_w=mean_w, t_j=t_j,
                eta=eta_semis)


def acceptance() -> dict[str, int]:
    from companion.ch44 import examples_c as ec
    from companion.ch44 import lab_d
    fp = ec.fingerprints()
    mc = lab_d.montecarlo()
    sm = lab_d.statemachine()
    eol = ec.eol()
    lines = ["acceptance of the ten PCI-5500 at the factory, summarised",
             f"  parameter fingerprints: {len(fp['odd'])} inverters differ "
             f"({', '.join(fp['odd'])})",
             f"  thermal: module {mc['pos']} at {mc['max']:.1f} C stands out -"
             " reprint and re-run",
             f"  firmware test list: v1.0 {sm['v10']} of {sm['n']}; v0.9 would have "
             f"failed {sm['n'] - sm['v09']}",
             f"  end-of-line coverage: {eol['missing']} tree item without a test "
             "(auxiliary supply)",
             "  decision: INV-04 and INV-09 ship after a reload with the",
             "  released set and a repeated functional test; the unit with",
             "  the hot module after the reprint and a new full-power run;",
             "  the hold-up test is added to the end-of-line list for all"]
    emit("int_accept", lines)
    return dict(odd=len(fp["odd"]))


def basis() -> None:
    lines = ["D-048 converter manufacturing and acceptance basis",
             "  1 product defined by hardware, BOM, firmware, parameters and",
             "    calibration - each with a version and a record",
             "  2 interface print weighed; module serial, lot and position",
             "    recorded at mounting; modules paired by voltage class",
             "  3 board line with paste, optical, X-ray and in-circuit",
             "    inspection; escapes counted; broker parts screened",
             "  4 released parameter set and firmware fingerprinted at the",
             "    end-of-line test and again at the site",
             "  5 every tree item met by an end-of-line test; full-power run",
             "    with temperature reading of every position",
             "  6 firmware test list with fault injection in the release",
             "    record; MPPT efficiency steady and dynamic as evidence",
             "  7 derating and creepage checked at design review, not left",
             "    to the factory",
             "  8 later findings: busbar spacing a critical characteristic",
             "    (a quarter of the switches over the rule); control supply",
             "    hold-up 102 of 150 ms; sensor offsets trimmed against the",
             "    DC limit; Q(V) checked across the curve; N+1 fans for hot",
             "    days; a spare stack pays (+33 k u); the as-left set read",
             "    back against the authorised set",
             "  open: type tests of the design (DC injection, ride-through)",
             "    and the maker's firmware release records (U-125)"]
    emit("int_basis", lines)


if __name__ == "__main__":
    by_hand()
    acceptance()
    basis()
