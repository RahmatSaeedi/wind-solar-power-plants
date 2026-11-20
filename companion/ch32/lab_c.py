"""Chapter 32, lab C (worked example 1): the fire-hazard register of
Plant P, a concept-level protection matrix by area, and a trace of the
cause-and-effect logic from detection to alarm, isolation and response,
with a checker that finds the errors planted in a draft matrix.

Run from the project root:   python -m companion.ch32.lab_c
Writes companion/ch32/expected/c_*.txt and diagrams/data/ch32-register.csv.
Teaching values (A-369, A-372). The matrix shows which questions each
area raises and who answers them; it prescribes no suppression system.
Methods, rates, separations and the logic itself come from the
project's fire strategy, the authority having jurisdiction and the
product tests (U-105, U-110).
"""
from __future__ import annotations

from companion.ch32 import sources as src
from companion.ch32.common import csv, emit
from plantp import safety as sf

# [start: register]
REGISTER = [  # (id, area, scenario, L, S, consequence driver)
    ("F01", "BESS containers", "thermal runaway, off-gas, spread", 2, 5,
     "explosion of off-gas, spread to the next unit"),
    ("F02", "PV array", "arc fault or cable fire in a string", 3, 2,
     "local damage; grass ignition"),
    ("F03", "PV array", "grass fire across the array", 2, 3,
     "many tables, smoke over the road"),
    ("F04", "inverter stations", "electronics or unit-transformer fire", 2, 3,
     "one block out for months"),
    ("F05", "nacelles", "fire with no one on board", 2, 4,
     "turbine lost; burning debris"),
    ("F06", "nacelles", "fire with technicians on board", 1, 5,
     "escape from height"),
    ("F07", "main transformers", "oil fire after an internal fault", 1, 5,
     "half the export lost for a year"),
    ("F08", "control and MV buildings", "cable or panel fire", 2, 4,
     "loss of control; toxic smoke"),
    ("F09", "construction areas", "hot work, fuel or waste fire", 3, 3,
     "injury; damage to stored parts"),
]
# [end: register]

MATRIX = {   # area: what each column asks (teaching concept, owners in brackets)
    "BESS containers": dict(
        prevent="cell monitoring, BMS limits, maker's commissioning tests",
        passive="spacing or barriers from the product test (strategy)",
        detect="off-gas, smoke, BMS temperature (layers, ch 19)",
        isolate="PCS stop and DC contactors open, with feedback",
        act="explosion control and water use: strategy and tests decide",
        access="approach routes, stand-off, responder information"),
    "PV array": dict(
        prevent="connector quality, cable support, vegetation control",
        passive="firebreaks around and through the array",
        detect="inverter arc and insulation alarms, patrols",
        isolate="inverter stop; array stays energised in daylight",
        act="grass fire tactics with the fire service; no DC contact",
        access="perimeter road and gates as firebreaks"),
    "inverter stations": dict(
        prevent="cooling, cleaning, torque checks, thermography",
        passive="separation of the oil unit transformer (strategy)",
        detect="station smoke and temperature alarms",
        isolate="MV switch open, inverter stop, with feedback",
        act="by the strategy; exposure protection if specified",
        access="hard standing by each station"),
    "nacelles": dict(
        prevent="maintenance of brakes, bearings, converters; housekeeping",
        passive="materials of low flammability (maker)",
        detect="nacelle smoke and heat, SCADA alarm",
        isolate="turbine stop and MV switch open",
        act="maker's system if fitted; ground: exclusion zone",
        access="evacuation devices for people at height"),
    "main transformers": dict(
        prevent="protection, oil tests, bushing checks (ch 25, 26)",
        passive="bund, fire walls or separation (standard, strategy)",
        detect="protection trip, temperature, fire detection if fitted",
        isolate="breakers on both sides open by protection",
        act="by the strategy; firewater only if specified (D)",
        access="hydrant or tanker point if specified; drainage (D)"),
    "control and MV buildings": dict(
        prevent="cable segregation, housekeeping, no storage",
        passive="fire stopping of every cable penetration",
        detect="aspirating smoke detection, manual call points",
        isolate="HVAC stop, local isolation by the strategy",
        act="by the strategy; portable extinguishers for trained staff",
        access="two exits, signs, emergency lighting"),
    "construction areas": dict(
        prevent="hot-work permits, fuel storage rules, waste removal",
        passive="separation of fuel, gas bottles and laydown",
        detect="fire watch during and after hot work",
        isolate="permit control of temporary supplies",
        act="extinguishers and trained staff; call the fire service",
        access="kept-clear routes on the traffic plan"),
}


def register() -> None:
    rows = []
    lines = ["the fire-hazard register of Plant P (teaching scores)",
             "  id   area                      L  S  score  band"]
    for fid, area, scen, lk, sv, drv in sorted(REGISTER, key=lambda r: -r[3] * r[4]):
        s = sf.risk_score(lk, sv)
        rows.append((fid, lk, sv, s))
        lines.append(f"  {fid}  {area:25s} {lk}  {sv}  {s:5d}  {sf.risk_band(s)}")
        lines.append(f"       {scen}; {drv}")
    csv("ch32-register.csv", "id,l,s,score", rows)
    lines += ["  the battery heads the list on severity, the construction",
              "  site on likelihood; the main transformer scores only medium",
              "  but its loss stops half the export for a year - a matrix",
              "  ranks attention, and the strategy still treats every row"]
    emit("c_register", lines)


def matrix() -> None:
    cols = ("prevent", "passive", "detect", "isolate", "act", "access")
    lines = ["concept protection matrix by area (questions and owners, not designs)"]
    for area, m in MATRIX.items():
        lines.append(f"  {area}")
        for c in cols:
            lines.append(f"    {c:8s} {m[c]}")
    lines += ["  each line names what must be decided and who decides it;",
              "  a method appears only where it is the same everywhere",
              "  (fire stopping, detection layers, isolation with feedback)"]
    emit("c_matrix", lines)


# [start: logic]
INPUTS = {   # id: (device, location)
    "I1": ("off-gas detector", "BESS-1"), "I2": ("smoke detector", "BESS-1"),
    "I3": ("BMS thermal alarm", "BESS-1"), "I4": ("nacelle smoke", "T03"),
    "I5": ("aspirating smoke, alert", "building"),
    "I6": ("aspirating smoke, fire", "building"),
    "I7": ("transformer protection trip", "TR1"),
    "I8": ("manual call point", "building")}
OUTPUTS = {  # id: (action, location, feedback?)
    "O1": ("alarm in control room and remote centre", "all", True),
    "O2": ("call the fire service by the plan", "all", True),
    "O3": ("PCS stop", "BESS-1", True),
    "O4": ("DC contactors open", "BESS-1", False),
    "O5": ("turbine stop and MV switch open", "T04", True),
    "O6": ("HVAC stop", "building", True),
    "O7": ("evacuation alarm", "building", True),
    "O8": ("breakers both sides open", "TR1", True)}
DRAFT = {"I1": ["O1", "O2", "O3", "O4"], "I2": ["O3", "O4"],
         "I3": ["O1", "O3"], "I4": ["O1", "O2", "O5"], "I5": ["O1"],
         "I6": ["O1", "O2", "O6", "O7"], "I7": ["O1", "O8"],
         "I8": ["O1", "O2", "O7"]}
# [end: logic]


def check(ce: dict, outputs: dict) -> list[str]:
    """Rules: every input alarms the control room; an input drives only
    outputs at its own location (or plant-wide ones); every output that
    moves equipment reports its position back."""
    found = []
    for i, outs in ce.items():
        dev, loc = INPUTS[i]
        if "O1" not in outs:
            found.append(f"{i} {dev} at {loc}: no alarm to the control room")
        for o in outs:
            act, oloc, fb = outputs[o]
            if oloc not in ("all", loc):
                found.append(f"{i} at {loc} drives {o} '{act}' at {oloc}")
            if not fb:
                found.append(f"{o} '{act}' has no position feedback")
    return sorted(set(found))


def logic() -> None:
    lines = ["cause and effect: the draft matrix checked (teaching logic)",
             "  input  device                        location   outputs"]
    for i, outs in DRAFT.items():
        dev, loc = INPUTS[i]
        lines.append(f"  {i:5s}  {dev:28s}  {loc:9s}  {' '.join(outs)}")
    errs = check(DRAFT, OUTPUTS)
    lines.append(f"  checker findings: {len(errs)}")
    lines += [f"    {e}" for e in errs]
    fixed = dict(DRAFT, I2=["O1", "O2", "O3", "O4"])
    outs = dict(OUTPUTS, O4=("DC contactors open", "BESS-1", True),
                O5=("turbine stop and MV switch open", "T03", True))
    left = check(fixed, outs)
    lines += [f"  after the three fixes: {len(left)} findings",
              "  the wrong turbine, the silent smoke detector and the open",
              "  contactor with no feedback are each easy to miss by eye;",
              "  which outputs an input drives at all (and whether a second",
              "  detector must confirm) is the strategy's decision"]
    emit("c_logic", lines)


if __name__ == "__main__":
    register()
    matrix()
    logic()
