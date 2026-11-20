"""Chapter 44, lesson A: product and electrical architecture of the
PCI-5500 - the product tree with counts, mass, cost and failure rates,
where the failures come from, a simplified loss budget of one stack
checked device by device, the interfaces to the plant, the
configuration items of the product, and the plant's converter fleet.

Run from the project root:   python -m companion.ch44.examples_a
Writes companion/ch44/expected/a_*.txt.
Teaching values (A-466).
"""
from __future__ import annotations

import math

from companion.ch44 import sources as src
from companion.ch44.common import csv, emit
from plantp import pe


def _counts():
    """Number of each item in one inverter (count x parent's count)."""
    mult = {}
    for nid, parent, _name, n, *_ in src.TREE:
        mult[nid] = n * (mult[parent] if parent else 1)
    return mult


# ------------------------------------------------ product tree
def tree() -> dict[str, float]:
    mult = _counts()
    lines = ["product tree of one PCI-5500 (teaching values)",
             "  item                                each  in unit"
             "   kg     k u      FIT"]
    mass = cost = fit = 0.0
    fits = {}
    for nid, parent, name, n, kg, ku, f in src.TREE:
        if parent is None:
            continue
        k = mult[nid]
        mass += k * kg
        cost += k * ku
        fit += k * f
        fits[name] = k * f
        lines.append(f"  {name:35s} {n:4d}  {k:6d}  {k * kg:6.0f}  "
                     f"{k * ku:6.1f}  {k * f:7.0f}")
    ranked = sorted(((n, v) for n, v in fits.items() if v > 0),
                    key=lambda x: -x[1])
    csv("ch44-fit.csv", "k,fit,share",
        [(k, round(v), round(100 * v / fit, 1))
         for k, (_, v) in enumerate(ranked, 1)])
    top = ranked[:3]
    lines += [f"  unit: {mass / 1000:.1f} t, {cost:,.0f} k u, {fit:,.0f} FIT "
              f"({fit * 8760 / 1e9:.2f} failures a year; ch 9: 56,400)",
              "  largest shares: "
              + "; ".join(f"{n} {v / fit:.0%}" for n, v in top[:2]) + ";",
              f"    {top[2][0]} {top[2][1] / fit:.0%}",
              "  the power modules are not where most failures come from:",
              "  cooling, boards and supplies are - the factory evidence",
              "  and the spares follow the failure shares, not the price"]
    emit("a_tree", lines)
    return dict(mass=mass, cost=cost, fit=fit, top=top[0][0])


# ------------------------------------------------ loss budget, simplified
# [start: budget]
DEV = dict(v_t0=0.75, r_t=0.35e-3, v_d0=0.8, r_d=0.3e-3, e_on_off=0.9,
           e_rr=0.2, i_ref=2800, v_ref=600)       # one switch position (ch 9)


def simple_leg(i_pk, m, pf, v_dc, f_sw, dev=DEV):
    """Simplified NPC leg: conduction as a two-level leg with two devices
    in the current path; switching as a two-level leg at V_dc / 2."""
    p_t, p_d = pe.conduction_losses(i_pk, m, pf, dev["v_t0"], dev["r_t"],
                                    dev["v_d0"], dev["r_d"])
    s_t, s_d = pe.switching_losses(i_pk, v_dc / 2, f_sw, dev["e_on_off"],
                                   dev["e_rr"], dev["i_ref"], dev["v_ref"])
    return dict(cond=4 * (p_t + p_d), sw=2 * (s_t + s_d))
# [end: budget]


def loss_budget() -> dict[str, float]:
    inv = src.INVERTER
    i_rms = inv["s_stack_mva"] * 1e6 / (math.sqrt(3) * inv["v_ll"])
    i_pk = math.sqrt(2) * i_rms
    leg = simple_leg(i_pk, inv["m"], inv["pf"], inv["v_dc"], inv["f_sw"])
    simple = 3 * (leg["cond"] + leg["sw"])
    full = pe.npc_leg_losses(i_pk, inv["m"], math.degrees(math.acos(inv["pf"])),
                             inv["v_dc"], inv["f_sw"], DEV)
    numeric = 3 * sum(full.values())
    hot = max(full, key=full.get)
    lines = [f"semiconductor loss of one stack, {inv['s_stack_mva']} MVA, pf "
             f"{inv['pf']}, m {inv['m']}, {inv['f_sw'] / 1e3:.0f} kHz",
             f"  peak current {i_pk:,.0f} A; device data of ch 9",
             "  simplified (two-level formulas, two devices in the path,",
             "  switching at V_dc / 2), per leg:",
             f"    conduction {leg['cond']:,.0f} W, switching {leg['sw']:,.0f} W",
             f"  stack: simplified {simple / 1e3:.2f} kW, NPC device by device "
             f"{numeric / 1e3:.2f} kW ({simple / numeric - 1:+.1%})",
             "  per device of a leg (W): " + ", ".join(
                 f"{k} {v:.0f}" for k, v in full.items() if k in ("T1", "T2", "D5")),
             f"  hottest: {hot}, {full[hot]:,.0f} W a position, "
             f"{full[hot] / inv['parallel']:.0f} W a module",
             "  the hand budget is close in total but cannot say which",
             "  device is hottest: the thermal design needs the device split"]
    emit("a_budget", lines)
    return dict(simple=simple, numeric=numeric, hot=hot, hot_w=full[hot],
                module_w=full[hot] / inv["parallel"])


# ------------------------------------------------ interfaces
INTERFACES = [   # interface, what crosses, check, owners
    ("PV combiners - DC input", "1000 V DC, 6 MWp", "DC window, polarity, IMD", "PV, inverter"),
    ("inverter - unit transformer", "600 V AC, 5,300 A", "phases, torque, DC limit",
     "inverter, transformer"),
    ("plant controller - inverter", "P and Q set-points", "range, rate, fallback", "PPC, inverter"),
    ("SCADA - inverter", "data points, alarms", "point list, time stamps", "SCADA, inverter"),
    ("auxiliary supply", "400 V AC, 24 V DC", "hold-up, ride-through", "aux, inverter"),
    ("cooling", "glycol loop, 45 C", "flow, pressure, leak", "inverter"),
    ("earthing", "PE, frame, IMD", "continuity, bonding", "civil, inverter"),
]


def interfaces() -> int:
    lines = ["interfaces of the PCI-5500 to the plant",
             "  interface                     crosses              check"]
    for name, what, check, _own in INTERFACES:
        lines.append(f"  {name:29s} {what:20s} {check}")
    lines += [f"  {len(INTERFACES)} interfaces, each with two owners and a check made at",
              "  the factory or on site; the DC-injection limit sits on the",
              "  transformer row (ch 43) and the fallback on the controller",
              "  row (ch 20)"]
    emit("a_interfaces", lines)
    return len(INTERFACES)


# ------------------------------------------------ configuration items
CONFIG_ITEMS = [   # item, changes when, re-test needed
    ("bill of materials revision", "part or supplier", "type qualification"),
    ("PCB assembly revision", "layout or assembly", "board tests, EMC"),
    ("firmware image", "any code change", "regression, grid code"),
    ("parameter set", "a site setting", "function, fingerprint"),
    ("calibration constants", "sensor or board", "calibration check"),
]


def config_items() -> int:
    lines = ["configuration items of a converter: what defines the product",
             "  item                          changes with         re-test"]
    for item, when, test in CONFIG_ITEMS:
        lines.append(f"  {item:29s} {when:20s} {test}")
    lines += ["  hardware alone does not define a converter: two identical",
              "  cabinets with different firmware or parameters are two",
              "  products - each item has a version and a record (ch 38)"]
    emit("a_config", lines)
    return len(CONFIG_ITEMS)


# ------------------------------------------------ the fleet
def fleet() -> dict[str, int]:
    mult = _counts()
    units = src.INVERTER["units"]
    boards = mult["GDB"] + mult["CTL"] + mult["AUX"]
    lines = ["Plant P's converter fleet and what the factory builds for it",
             f"  PV central inverters: {units} x PCI-5500",
             f"    IGBT modules {units * mult['MOD']}, boards {units * boards}, "
             f"DC-link capacitors {units * mult['DCL']}",
             "  wind: 12 turbine converters (machine and grid side, ch 11)",
             "  storage (S1): 4 PCS of 5 MW for the 8 battery containers (ch 19)",
             "  one design, many copies: a systematic defect repeats in",
             "  every unit, a random one in some - the first unit's tests",
             "  look for the first, the line's tests for the second"]
    emit("a_fleet", lines)
    return dict(modules=units * mult["MOD"], boards=units * boards)


if __name__ == "__main__":
    tree()
    loss_budget()
    interfaces()
    config_items()
    fleet()
