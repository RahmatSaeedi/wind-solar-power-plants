"""Chapter 23, sections E and F - auxiliary and common services: the
load register by operating state, the classes, station-service and
standby sizing, motor starting on the transformer and on the generator,
fault current at the LV board, the DC system and the UPS, heat loads of
the rooms, the load-shed matrix, the cause-and-effect matrix, the loss
of normal supply and its restoration, and whether a standby generator is
justified.

Run from the project root:   python -m companion.ch23.examples_e
Writes companion/ch23/expected/e_*.txt and f_*.txt, diagrams/data/ch23-*.csv.
Teaching values A-317 and A-318; equipment is sized from makers' data
and the applicable standards by qualified engineers.
"""
from __future__ import annotations

import math

from companion.ch23 import sources as src
from companion.ch23.common import csv, emit
from plantp import auxpower as ax

GEN_KVA, GEN_XD = 150.0, 0.15        # standby generator (A-317)


def register() -> None:
    lines = ["station-service load register (kW at full duty; duty by state):",
             "  load                              kW  class  ess  norm  degr  emer  mnt"]
    for ld in src.AUX:
        d = [ld.duty[s] for s in ax.STATES]
        lines.append(f"  {ld.tag:32s} {ld.kw:4.0f}  {ld.kind[:5]:5s}  {'yes' if ld.essential else 'no ':3s}"
                     + "".join(f"  {x:4.1f}" for x in d))
    lines.append(f"  demand by state (diversity {src.DIVERSITY}):")
    rows = []
    for st in ax.STATES:
        p, q, s = ax.demand(src.AUX, st, src.DIVERSITY)
        lines.append(f"    {st:12s} {p:6.1f} kW {q:6.1f} kvar {s:6.1f} kVA  pf {p / s:.2f}")
        rows.append((st, f"{p:.1f}", f"{s:.1f}"))
    lines += ["  normal and degraded are equal: degraded means one supply",
              "  out, the same loads on the other; emergency keeps only the",
              "  essential loads; maintenance trades fans for tools"]
    emit("e_register", lines)
    csv("ch23-states.csv", "state,kw,kva", rows)


def classes() -> None:
    tot = {}
    for ld in src.AUX:
        key = (ld.kind, "essential" if ld.essential else "non-essential")
        tot[key] = tot.get(key, 0.0) + ld.kw_in("normal")
    lines = ["normal-state kW by class:"]
    for (k, e), v in sorted(tot.items()):
        lines.append(f"  {k:12s} {e:14s} {v:6.1f}")
    lines += ["  continuous essential loads (DC chargers, UPS) are small",
              "  but must never stop; the intermittent motors set the",
              "  starting duty; the non-essential loads are what a standby",
              "  supply may leave off"]
    emit("e_classes", lines)


def sizing() -> None:
    p, q, s = ax.demand(src.AUX, "normal", src.DIVERSITY)
    sst = ax.next_size(s, 0.2)
    pe, qe, se = ax.demand(src.AUX, "emergency", src.DIVERSITY)
    gen = ax.next_size(se, 0.25, sizes=(60, 80, 100, 125, 150, 200, 250))
    big = max((ld for ld in src.AUX if ld.duty["emergency"] > 0),
              key=lambda x: x.motor_start_kva)
    dip_t = ax.start_dip(max(ld.motor_start_kva for ld in src.AUX), sst, 0.045)
    dip_g = ax.start_dip(big.motor_start_kva, GEN_KVA, GEN_XD)
    dip_g0 = ax.start_dip(big.motor_start_kva, gen, GEN_XD)
    i_lv = ax.sc_current_ka(sst, 0.4, 0.045, s_source_mva=562.0)
    lines = ["station service and standby supply (teaching):",
             f"  normal demand {s:.0f} kVA; with 20 % margin {s * 1.2:.0f} kVA:",
             f"    two {sst} kVA transformers, each for the whole plant (N-1)",
             f"  emergency demand {se:.0f} kVA; with 25 % margin: generator {gen} kVA",
             f"  largest start on a transformer (well pump 200 kVA): dip {dip_t:.1%}",
             f"  largest essential start on the generator: {big.tag},",
             f"    {big.motor_start_kva:.0f} kVA: dip {dip_g0:.1%} on {gen} kVA,"
             f" {dip_g:.1%} on {GEN_KVA:.0f} kVA",
             "  with a 12 % dip limit (teaching; the makers' limits apply)",
             f"    the generator is {GEN_KVA:.0f} kVA: starting, not running, sizes it",
             f"  fault current at the 0.4 kV board: {i_lv:.1f} kA (LV board rating",
             "  chosen above it with the maker; ch 24)",
             "  the well pump may start direct on a transformer but not on",
             "  the generator: it is non-essential and shed in emergency;",
             "  a soft starter would be needed if it were essential"]
    emit("f_sizing", lines)


def dc() -> None:
    raw, ah = ax.battery_ah(src.DC_DUTY)
    rated = next(c for c in (100, 150, 200, 250, 300, 400) if c >= ah)
    ch = ax.charger_a(40.0, rated, 10.0)
    kva, kwh = ax.ups(src.UPS_KW, 0.95, src.UPS_MIN)
    minutes = sum(m for _, m in src.DC_DUTY)
    lines = ["DC system 110 V and UPS (teaching duty cycle):",
             "  duty: " + ", ".join(f"{a:.0f} A for {m:.0f} min" for a, m in src.DC_DUTY),
             f"  {minutes / 60:.0f} h autonomy: raw {raw:.1f} Ah; x 1.11 temperature x 1.25 ageing",
             f"  x 1.10 margin = {ah:.1f} Ah -> {rated} Ah battery",
             f"  charger: 40 A standing + 1.1 x {rated} Ah / 10 h = {ch:.0f} A",
             f"  UPS: {src.UPS_KW:.0f} kW for {src.UPS_MIN:.0f} min -> {kva:.0f} kVA,"
             f" battery {kwh:.1f} kWh",
             "  two chargers (one standby) and a battery split or duplicated",
             "  where the protection philosophy asks for it; the duty cycle",
             "  comes from the protection and control design, the factors",
             "  from the battery maker and the applicable standard"]
    emit("f_dc", lines)


def rooms() -> None:
    rooms = [("control room", 12.0, 0.40, 3.0), ("switchgear room", 18.0, 0.60, 2.0),
             ("battery and charger room", 2.0, 0.30, 1.0)]
    lines = ["heat loads of the rooms at 45 C outside, 25 C inside:",
             "  room                      losses  walls  solar  cooling  electric"]
    for name, loss, ua, sol in rooms:
        q, e = ax.hvac_kw(loss, ua, 45.0, 25.0, sol)
        lines.append(f"  {name:24s} {loss:6.1f} {ua * 20:6.1f} {sol:6.1f} {q:8.1f} {e:9.1f}")
    lines += ["  the control room's 30 kW in the register is the rated input",
              "  of two units (one standby) for 25 kW of cooling; the battery",
              "  room is ventilated for its own reasons (gases, the maker's",
              "  data), not only for heat"]
    emit("e_rooms", lines)


def shed_matrix() -> None:
    lines = ["load-shed matrix: what each supply can keep (kVA available):"]
    cases = [("one transformer (250 kVA)", "degraded", 250.0),
             ("generator 150 kVA", "emergency", 150.0),
             ("generator derated 50 %", "emergency", 75.0)]
    for name, st, kva in cases:
        kept, cut, k = ax.shed(src.AUX, st, kva, src.DIVERSITY)
        lines.append(f"  {name}: keeps {len(kept)} loads ({k:.0f} kVA), sheds {len(cut)}")
        if cut:
            lines.append("    shed: " + ", ".join(cut))
    lines += ["  priorities, not sizes, decide what stays: the UPS and the",
              "  DC chargers are priority 1 and stay in every case"]
    emit("e_shed", lines)


# [start: cause]
EVENTS = {   # event -> actions (cause-and-effect, A-318)
    "loss of grid supply": ["UPS and DC carry", "start generator",
                            "shed non-essential", "alarm"],
    "station transformer A trips": ["transfer to B", "alarm"],
    "both station supplies lost": ["start generator",
                                   "shed non-essential", "alarm"],
    "DC charger fault": ["standby charger on", "alarm"],
    "fire alarm in a battery container": [
        "stop that battery block", "alarm",
        "actions of the fire design (ch 31)"],
    "33 kV bus A fault": ["trip feeders and incomer A", "alarm"],
    "PPC comms lost": ["PPC fallback (ch 20)", "alarm"],
    "high room temperature": ["standby HVAC on", "alarm"],
}
# [end: cause]


def cause_effect() -> None:
    actions = sorted({a for v in EVENTS.values() for a in v})
    lines = ["cause-and-effect matrix (events x actions; x = initiates):",
             f"  {len(EVENTS)} events, {len(actions)} actions"]
    for e, acts in EVENTS.items():
        lines.append(f"  {e}:")
        lines.append("    " + "; ".join(acts))
    no_alarm = [e for e, a in EVENTS.items() if "alarm" not in a]
    lines += [f"  events without an alarm: {no_alarm or 'none'}",
              "  checks: every event has an action and an alarm; every",
              "  action has an event that starts it; the fire actions are",
              "  only a pointer - the fire design and the authority set",
              "  them (ch 31), the matrix records the interface"]
    emit("e_cause", lines)


def restoration() -> None:
    _, _, se = ax.demand(src.AUX, "emergency", src.DIVERSITY)
    pe = ax.demand(src.AUX, "emergency", src.DIVERSITY)[0]
    events = [(0.0, "grid lost: UPS and DC carry", src.UPS_KW + 4.4),
              (0.25, "generator starts", src.UPS_KW + 4.4),
              (1.0, "generator on, essential loads back", 0.0),
              (240.0, "grid back; plant resynchronised by operator", 0.0),
              (250.0, "generator stopped, normal state", 0.0)]
    rows, kwh = ax.timeline(events)
    fuel = pe * (240 - 1) / 60 * 0.27
    lines = ["loss of normal supply and restoration (teaching timeline, min):"]
    for t0, t1, lab, kw, e in rows:
        lines.append(f"  {t0:6.2f}-{t1:6.2f}  {lab:44s} UPS {e:5.2f} kWh")
    lines += [f"  UPS and DC give {kwh:.2f} kWh before the generator takes over;",
              f"  the generator then runs {pe:.0f} kW for 4 h: about {fuel:.0f} litres",
              "  if the generator fails to start, the UPS's 60 min and the",
              "  DC battery's 4 h are the time to restore supply - the",
              "  autonomy requirement is the restoration case written down"]
    emit("f_restoration", lines)
    csv("ch23-restoration.csv", "t,label", [(f"{t:.2f}", lab.split(":")[0].replace(",", ""))
                                            for t, lab, _ in events])


def standby() -> None:
    pe = ax.demand(src.AUX, "emergency", src.DIVERSITY)[0]
    hours = 8.0
    kwh = pe * hours / 0.9
    lines = ["is a standby generator justified? (an 8 h grid outage):",
             f"  essential load {pe:.0f} kW for {hours:.0f} h = {pe * hours:.0f} kWh;"
             f" a battery for it ~ {kwh:.0f} kWh usable",
             "  options: (a) generator 150 kVA with a day tank; (b) a larger",
             "  UPS and DC battery for 8 h; (c) supply from the plant's own",
             "  battery (S1) through a transfer switch (ch 18 island)",
             "  (c) costs little if the battery exists and is kept above a",
             "  floor (ch 20); (b) is a large battery for rare events; (a)",
             "  covers long outages and S0 - the choice follows the",
             "  requirement for autonomy (REQ in ch 17), not a habit"]
    emit("f_standby", lines)


if __name__ == "__main__":
    register()
    classes()
    sizing()
    dc()
    rooms()
    shed_matrix()
    cause_effect()
    restoration()
    standby()
