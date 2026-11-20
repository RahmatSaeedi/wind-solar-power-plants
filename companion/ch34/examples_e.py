"""Chapter 34, lesson E: control-power resilience - which supply feeds
which function, the 24 V control loads added to the 110 V battery,
undervoltage alarms against what each device needs at the end of
discharge, behaviour on loss of each supply, the UPS and its load
shedding, the restart sequence after a blackout, and the matrix of
loss-of-supply tests.

Run from the project root:   python -m companion.ch34.examples_e
Writes companion/ch34/expected/e_*.txt and diagrams/data/ch34-restart.csv.
Battery and UPS of chapter 23 (D-027); teaching loads A-389.
"""
from __future__ import annotations

from companion.ch34 import sources as src
from companion.ch34.common import csv, emit
from plantp import auxpower as ax
from plantp import instrumentation as ic

CELLS, V_FLOAT, V_END = 55, 2.23, 1.75          # ch 23


def supply_map() -> None:
    rows = [("protection IEDs, trip and close coils", "110 V DC battery"),
            ("breaker spring motors, indication", "110 V DC battery"),
            ("PLC, remote I/O, field loops", "24 V DC from 110 V DC"),
            ("PPC, SCADA servers, HMI, telecom", "UPS 230 V AC"),
            ("time server, firewall, switches", "24 V DC from 110 V DC"),
            ("fire panel", "its own batteries (fire system)"),
            ("BESS container HVAC and PCS auxiliaries", "station service (ch 23)")]
    lines = ["which supply carries which function (teaching, Plant P)",
             "  function                                  supply"]
    for f, s in rows:
        lines.append(f"  {f:41s} {s}")
    lines += ["  the 24 V control supply hangs on the 110 V battery, not on",
              "  the UPS: when the UPS fails, interlocks and I/O still work;",
              "  the fire panel keeps its own batteries so that life safety",
              "  never depends on the plant's control power"]
    emit("e_map", lines)


def battery_with_24v() -> None:
    w24 = sum(w for _, w in src.CONTROL_24V)
    extra = w24 / 0.90 / src.DC["volts"]            # DC/DC converter 90 %
    base = src.DC["standing_a"]
    a0 = ic.autonomy_h(src.DC["ah"], base)
    a1 = ic.autonomy_h(src.DC["ah"], base + extra)
    lines = ["the 24 V control loads on the 110 V battery (teaching)",
             f"  24 V loads: {w24:.0f} W through a 90 % converter = {extra:.1f} A at 110 V",
             f"  standing load {base:.0f} A (ch 23) -> {base + extra:.1f} A if not yet counted",
             f"  autonomy of {src.DC['ah']:.0f} Ah at 80 % usable: {a0:.1f} h -> {a1:.1f} h",
             "  still above the 4 h requirement, with less margin: the",
             "  control designer's load list goes back to the battery",
             "  sizing of ch 23 so that no load is counted twice or",
             "  missed - an interface, owned by one engineer"]
    emit("e_battery", lines)


def undervoltage() -> None:
    v_float = CELLS * V_FLOAT
    v_end = CELLS * V_END
    warn, urgent = CELLS * 1.90, CELLS * 1.80
    needs = [("protection IED (teaching: 80 % of 110 V)", 88.0),
             ("trip coil (teaching: 70 %)", 77.0),
             ("DC/DC converter input (teaching)", 85.0)]
    lines = ["110 V DC undervoltage alarms and what the devices need (teaching)",
             f"  float {v_float:.1f} V; end of discharge {v_end:.1f} V ({CELLS} cells x {V_END})",
             f"  alarm 'DC low' at {warn:.1f} V (1.90 V/cell), 'DC very low' at"
             f" {urgent:.1f} V (1.80)"]
    for label, area in (("feeder to the far panel as drawn, 2.5 mm2", 2.5),
                        ("the same feeder enlarged to 10 mm2", 10.0)):
        drop = 2 * 0.0175 * 60 / area * 15.0          # 60 m, 15 A for that panel
        at = v_end - drop
        lines.append(f"  {label}:")
        lines.append(f"    drop {drop:.1f} V at 15 A, the panel sees {at:.1f} V")
        for name, need in needs:
            lines.append(f"    {name:43s} needs {need:4.0f}   {'ok' if at >= need else 'FAILS'}")
    lines += ["  at the end of the autonomy the far panel's IED loses its",
              "  supply on the thin feeder: the DC drop is checked at the",
              "  end-of-discharge voltage, not at float; the alarms come",
              "  first - 'DC low' to restore the charger, 'DC very low' to",
              "  start the orderly shedding - so the protection keeps its",
              "  voltage to the end of the autonomy"]
    emit("e_uv", lines)


def loss_behaviour() -> None:
    rows = [("station-service AC lost", "UPS and DC carry; diesel starts"),
            ("one charger fails", "second charger carries; alarm"),
            ("both chargers fail", "battery carries; autonomy clock"),
            ("UPS fails (bypass on)", "PPC and SCADA on raw AC; alarm"),
            ("110 V DC lost", "protection blind: plant tripped"),
            ("24 V DC lost", "PLC outputs off: stops, no permits"),
            ("network lost", "PPC holds, then falls back (ch 20)")]
    lines = ["what the plant does on the loss of each supply (teaching design intent)",
             "  loss                         behaviour"]
    for a, b in rows:
        lines.append(f"  {a:28s} {b}")
    lines += ["  every row is a written intent with a test (lesson E,",
              "  tests); the one row the design avoids is a plant running",
              "  without protection - loss of all DC trips it on purpose,",
              "  and the second battery or charger makes that rare"]
    emit("e_loss", lines)


def ups_shedding() -> None:
    kw, minutes = src.DC["ups_kw"], src.DC["ups_min"]
    kva, kwh = ax.ups(kw, 0.95, minutes)
    shed_kw, at_min = 8.0, 20.0                  # HMI screens, historian, office (teaching)
    used = kw * at_min / 60
    left = kwh * 0.92 - used                     # kWh delivered left after 20 min
    extra_min = left / (kw - shed_kw) * 60
    lines = ["the UPS of the control building and load shedding (ch 23 sizing)",
             f"  {kw:.0f} kW for {minutes:.0f} min: {kva:.1f} kVA, battery {kwh:.1f} kWh",
             f"  shed {shed_kw:.0f} kW of non-critical loads after {at_min:.0f} min:"
             f" total {at_min + extra_min:.0f} min",
             "  shedding by priority (HMI screens and the historian first,",
             "  the PPC, telecom and time server last) buys more time for",
             "  what must keep running; the shedding list is part of the",
             "  cause-and-effect matrix (lesson C)"]
    emit("e_ups", lines)


def restart() -> None:
    steps = [  # name, start after (s), duration (s)
        ("DC and protection healthy (on battery)", 0, 0),
        ("diesel generator start and supply", 0, 15),
        ("UPS back on mains, essential AC", 15, 5),
        ("network switches and time server boot", 20, 60),
        ("PLC pair boot and self-test", 20, 90),
        ("PPC and SCADA servers boot", 20, 180),
        ("I/O quality good, permissives evaluated", 110, 30),
        ("operator checks, grid operator called", 200, 600),
        ("energisation stages S0-S4 (ch 23)", 800, 1800)]
    out = []
    lines = ["restart sequence after a total blackout (teaching durations)",
             "  step                                       start s   end s"]
    end = 0
    for k, (name, s, d) in enumerate(steps, 1):
        lines.append(f"  {name:42s} {s:7d}   {s + d:5d}")
        out.append((k, s, s + d))
        end = max(end, s + d)
    csv("ch34-restart.csv", "k,start,end", out)
    lines += [f"  back to export after about {end / 60:.0f} minutes, most of it",
              "  people and checks, not machines: the sequence is written",
              "  down, each step has a 'ready' signal, and the plant",
              "  cannot be energised before the PPC and protection say",
              "  they are healthy"]
    emit("e_restart", lines)


def tests() -> None:
    supplies = ["station AC", "charger A", "charger B", "UPS", "24 V DC", "network"]
    states = ["normal operation", "plant stopped"]
    n = len(supplies) * len(states)
    lines = ["loss-of-supply test matrix (commissioning, teaching)",
             f"  {len(supplies)} supplies x {len(states)} plant states = {n} tests",
             "  each test: open the supply's isolating device by the",
             "  commissioning procedure (authorised staff, no work on live",
             "  parts), record alarms, times and outputs, restore, compare",
             "  with the written intent of the loss table; the battery",
             "  autonomy itself is proved by a capacity test of the",
             "  battery, not by draining the plant's battery in service"]
    emit("e_tests", lines)


if __name__ == "__main__":
    supply_map()
    battery_with_24v()
    undervoltage()
    loss_behaviour()
    ups_shedding()
    restart()
    tests()
