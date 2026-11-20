"""Chapter 18 - architecture data for Plant P (teaching values A-286):
conversion efficiencies for the coupling comparison, cable and line data
for collector and export options, the product breakdown tree, the
interface register (with three planted mismatches for the worked
example), and the water sources and uses.

Nothing here is a recommended design; ratings come from suppliers with
evidence (chapters 25 and 39).
"""
from __future__ import annotations

from companion.ch18 import common  # noqa: F401  (puts plantp on the path)
from plantp import architecture as ar

# [start: effs]
EFF = {                                 # one-way efficiencies (A-286)
    "pv_inverter": 0.983,               # chapter 10 curve at mean load
    "bess_inverter": 0.980,
    "dcdc": 0.990,                      # DC-coupled battery converter
    "cell_round_trip": 0.90,            # battery cells and their auxiliaries
}
# [end: effs]

CABLES = {                              # 3-core collector cables (A-286)
    #  name               kV    ohm/km  mH/km  amp  cost k u/km
    "33 kV 240 mm2":      (33.0, 0.160, 0.37, 0.41, 95.0),
    "33 kV 630 mm2":      (33.0, 0.064, 0.33, 0.66, 165.0),
    "66 kV 240 mm2":      (66.0, 0.160, 0.40, 0.42, 150.0),
}

EXPORT = {                              # 132 kV, 7.06 km (A-286)
    "overhead line, single circuit": {"r": 0.12, "x": 0.40, "c_uf": 0.009,
                                      "cost_per_km": 450.0, "fail_per_km": 0.006,
                                      "repair_h": 12.0, "circuits": 1},
    "overhead line, double circuit": {"r": 0.12, "x": 0.40, "c_uf": 0.009,
                                      "cost_per_km": 680.0, "fail_per_km": 0.006,
                                      "repair_h": 12.0, "circuits": 2},
    "underground cable": {"r": 0.03, "x": 0.12, "c_uf": 0.20,
                          "cost_per_km": 1600.0, "fail_per_km": 0.002,
                          "repair_h": 240.0, "circuits": 1},
}


def breakdown() -> ar.Node:
    """Plant > system > subsystem > equipment > replaceable unit."""
    N = ar.Node
    wind = N("wind farm", "system").add(
        N("wind turbine", "subsystem", 12, "buy").add(
            N("rotor", "equipment", 1, "buy").add(N("blade", "unit", 3), N("pitch drive", "unit", 3)),
            N("drivetrain", "equipment", 1, "buy").add(N("main bearing", "unit", 1),
                                                       N("gearbox", "unit", 1),
                                                       N("generator", "unit", 1)),
            N("converter", "equipment", 1, "buy").add(N("power module", "unit", 6)),
            N("tower and foundation", "equipment", 1, "buy+make").add(N("tower section", "unit", 4)),
            N("unit transformer", "equipment", 1, "buy")))
    pv = N("PV plant", "system").add(
        N("PV block", "subsystem", 10, "buy+integrate").add(
            N("inverter", "equipment", 1, "buy").add(N("power stage", "unit", 4), N("fan set", "unit", 2)),
            N("combiner box", "equipment", 21, "buy").add(N("string fuse", "unit", 40)),
            N("module table", "equipment", 210, "buy+make").add(N("module", "unit", 52)),
            N("block transformer", "equipment", 1, "buy")))
    bess = N("battery (S1)", "system").add(
        N("battery container", "subsystem", 8, "buy").add(N("rack", "unit", 12), N("HVAC unit", "unit", 2)),
        N("BESS inverter", "subsystem", 4, "buy").add(N("power stage", "unit", 4)))
    grid = N("collection and export", "system").add(
        N("33 kV collector", "subsystem", 1, "make").add(N("cable circuit", "equipment", 6)),
        N("export substation", "subsystem", 1, "buy+integrate").add(
            N("main transformer", "equipment", 1, "buy"), N("132 kV switchgear bay", "equipment", 2, "buy"),
            N("33 kV switchgear panel", "equipment", 14, "buy")),
        N("export line", "subsystem", 1, "make"))
    plant = N("Plant P", "plant").add(
        wind, pv, bess, grid,
        N("control and SCADA", "system", 1, "buy+integrate").add(N("plant controller", "equipment", 2)),
        N("water service", "system", 1, "make").add(N("tank", "equipment", 2), N("pump set", "equipment", 2)),
        N("civil works", "system", 1, "make"))
    return plant


# [start: register]
def interfaces() -> list:
    I = ar.Interface
    return [
        I("IF-001", "electrical", "PV inverter", "block transformer",
          "LV voltage kV", 0.600, 0.690, 0.02, "EPC electrical"),
        I("IF-002", "electrical", "block transformer", "33 kV collector",
          "HV voltage kV", 33.0, 33.0, 0.0, "EPC electrical"),
        I("IF-003", "mechanical", "module", "module table",
          "clamp zone mm", 400.0, 400.0, 0.05, "PV supplier"),
        I("IF-004", "electrical", "module", "string cable",
          "DC connector", "type MC-A", {"type MC-A"}, 0.0, "PV supplier"),
        I("IF-005", "electrical", "combiner box", "string cable",
          "DC connector", "type MC-B", {"type MC-A"}, 0.0, "EPC electrical"),
        I("IF-006", "thermal", "battery container", "HVAC unit",
          "heat to reject kW", 120.0, 100.0, 0.05, "BESS supplier"),
        I("IF-007", "comms", "BESS controller", "plant controller",
          "protocol", "Modbus TCP", {"IEC 61850", "IEC 60870-5-104"}, 0.0,
          "integrator"),
        I("IF-008", "protection", "export bay", "grid bay",
          "relay settings source", "operator", "operator", 0.0,
          "grid operator"),
        I("IF-009", "civil", "transformer", "foundation",
          "mass t", 95.0, 100.0, 0.10, "civil"),
        I("IF-010", "water", "cleaning truck", "water tank",
          "fill rate m3/h", 20.0, 25.0, 0.25, "O&M"),
    ]
# [end: register]


WATER = {                               # m3 a month unless noted (A-286)
    "well_supply": 1500.0,              # permitted abstraction (teaching)
    "tank_m3": 2400.0,
    "fire_reserve_m3": 900.0,           # placeholder held for the authority
    "staff": 25, "l_per_person_day": 120.0,
    "bess_makeup": 15.0,                # closed-loop chiller top-up
    "dust_construction": 2500.0,        # during the build only
    "per_cleaning_m3": 109.2,           # 1 L per module (chapter 15)
}

# [start: costs]
COST = {                                # teaching screening costs (A-287)
    "wind_per_mw": 1300.0,              # k u per MW, installed
    "pv_per_mw_ac": 720.0,              # k u per MW AC at DC/AC 1.2
    "connection": 15000.0,              # k u, substation + line, 100 MW
    "connection_per_mw": 90.0,          # k u per MW of export limit above 100
    "opex_share": 0.02,                 # of capex a year
    "rate": 0.06, "years": 20,
    "price": 50.0,                      # u per MWh (A-281)
    "trafo_63": 1900.0, "trafo_125": 3100.0,     # k u each, installed
    "bess_inv_per_mw": 60.0,            # AC battery inverters
    "bess_ac_mv": 620.0,                # their MV transformers and 33 kV bays
    "dcdc_per_mw": 45.0,                # DC/DC converters in the PV blocks
    "bess_per_mw": 150.0,               # whole battery system: power part
    "bess_per_mwh": 250.0,              # and energy part, k u per MWh
}
# [end: costs]

# [start: reliability]
REL = {                                 # teaching reliability (A-288)
    "trafo_fail": 0.01,                 # large power transformer, per year
    "trafo_repair_h": 4380.0,           # replace without a spare: 6 months
    "trafo_spare_h": 720.0,             # with a shared spare unit
    "central_fail": 0.5, "central_mttr_h": 72.0,     # 5 MW inverter
    "string_fail": 0.1, "string_mttr_h": 24.0,       # 250 kW inverter
    "cable_fail_per_km": 0.01, "cable_repair_h": 120.0,  # 33 kV collector
}
# [end: reliability]
