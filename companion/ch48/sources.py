"""Chapter 48 - teaching data for the manufacture and acceptance of Plant P's
sensors, meters, control cabinets and plant network by a fictional
instrument maker, a fictional cabinet builder and a fictional network
integrator (ch 12, 13, 34-36). Values are illustrative, not makers' data
and not a standard's limits (A-498 to A-505).

SPECS       datasheet error terms of five instruments (A-498)
CAL_CERTS   calibration certificates with planted gaps (A-498)
METER       revenue-metering chain and its site test record (A-499)
CABINETS    enclosures, inside temperature and device ratings (A-500)
BONDS       cabinet bonding readings and cable-shield earthing (A-500)
PORTS       planned and actual port schedules of one switch (A-501)
FIBRE       fibre link records: length, joints, measured loss (A-501)
COPPER      copper link certification records (A-501)
POWER       cabinets' two power feeds and their sources (A-502)
FIRMWARE    device inventory and approved baseline (A-503)
BACKUPS     configuration backups against last changes (A-503)
CLOCKS      clock offsets read at the SAT (A-503)
REGMAP      protocol register map against the tag database (A-504)
TAGS        tag database with planted faults (A-504)
FAILOVER    redundancy tests: expected and measured (A-505)
"""
from __future__ import annotations

from datetime import date

from companion.ch48 import common  # noqa: F401  (puts plantp on the path)

TODAY = date(2027, 6, 1)

# [start: specs]
SPECS = {   # instrument: datasheet terms (teaching), reading, full scale, unit
    "pyranometer": (dict(acc_rdg=1.5, tc_rdg=0.04, t_ref=20, drift_rdg_yr=0.5,
                         nl_fs=0.2), 1000.0, 2000.0, "W/m2"),
    "reference cell": (dict(acc_rdg=2.0, tc_rdg=0.06, t_ref=25, drift_rdg_yr=0.3,
                            nl_fs=0.1), 1000.0, 1500.0, "W/m2"),
    "cup anemometer": (dict(acc_rdg=1.0, acc_fs=0.2, tc_rdg=0.0, drift_rdg_yr=0.4,
                            nl_fs=0.3), 10.0, 50.0, "m/s"),
    "power transducer": (dict(acc_rdg=0.2, tc_rdg=0.005, t_ref=23, drift_rdg_yr=0.1,
                              nl_fs=0.05), 100.0, 120.0, "MW"),
    "Pt100 + transmitter": (dict(acc_fs=0.1, tc_rdg=0.0, drift_rdg_yr=0.0,
                                 nl_fs=0.05), 45.0, 100.0, "C"),
}
# [end: specs]

CAL_CERTS = [   # serial, instrument, accredited lab, traceable, uncertainty stated,
                # conformity statement, calibrated, due
    ("PY-1031", "pyranometer", True, True, True, True, date(2027, 1, 12), date(2028, 1, 12)),
    ("PY-1032", "pyranometer", True, True, False, True, date(2027, 1, 12), date(2028, 1, 12)),
    ("RC-2204", "reference cell", False, True, True, True, date(2026, 11, 3), date(2027, 11, 3)),
    ("AN-5510", "cup anemometer", True, True, True, True, date(2025, 4, 2), date(2026, 4, 2)),
    ("PT-0718", "power transducer", True, False, True, True, date(2027, 2, 20), date(2028, 2, 20)),
    ("TT-3301", "Pt100 + transmitter", True, True, True, False, date(2027, 3, 1), date(2028, 3, 1)),
]

METER = dict(ct=0.2, vt=0.2, meter=0.2,                # class errors, % (teaching)
             site_test=[(5, 0.46), (20, 0.18), (100, 0.12)],   # % load, error %
             class_limits={5: 0.4, 20: 0.2, 100: 0.2})

CABINETS = {   # cabinet: (IP, inside max C on a summer day, devices: (name, max C))
    "MET-1": ("IP55", 52.0, [("logger", 60), ("modem", 55), ("PSU", 70)]),
    "WTG-T05": ("IP54", 48.0, [("PLC", 60), ("switch", 70), ("PSU", 60)]),
    "SUB-RTU": ("IP42", 41.0, [("RTU", 55), ("switch", 50), ("GPS clock", 50)]),
    "PV-B07": ("IP65", 58.0, [("datalogger", 60), ("switch", 55), ("PSU", 70)]),
}

BONDS = {"MET-1": 0.04, "WTG-T05": 0.06, "SUB-RTU": 0.21, "PV-B07": 0.05}   # ohm
SHIELDS = [   # cable, kind, earthed at
    ("C-101", "analogue 4-20 mA", "one end"), ("C-102", "analogue 4-20 mA", "both ends"),
    ("C-103", "RS-485", "one end"), ("C-104", "Ethernet copper", "both ends"),
    ("C-105", "analogue 4-20 mA", "one end"), ("C-106", "Pt100", "none"),
]
SHIELD_RULE = {"analogue 4-20 mA": "one end", "Pt100": "one end", "RS-485": "one end",
               "Ethernet copper": "both ends"}

# [start: ports]
PLANNED = {   # (switch, port): far end, VLAN, speed
    ("SW-T05", 1): dict(far="SW-T04:2", vlan=10, speed="1G"),
    ("SW-T05", 2): dict(far="SW-T06:1", vlan=10, speed="1G"),
    ("SW-T05", 3): dict(far="T05-PLC", vlan=20, speed="100M"),
    ("SW-T05", 4): dict(far="T05-CMS", vlan=30, speed="100M"),
    ("SW-T05", 5): dict(far="T05-CCTV", vlan=40, speed="100M"),
    ("SW-T05", 6): dict(far="T05-MET", vlan=20, speed="100M"),
}
ACTUAL = {k: dict(v) for k, v in PLANNED.items()}
ACTUAL[("SW-T05", 4)]["vlan"] = 20
ACTUAL[("SW-T05", 5)] = dict(far="T05-MET", vlan=20, speed="100M")
ACTUAL[("SW-T05", 6)] = dict(far="T05-CCTV", vlan=40, speed="100M")
ACTUAL[("SW-T05", 8)] = dict(far="laptop", vlan=1, speed="1G")
# [end: ports]

FIBRE = [   # link, km, connectors, splices, measured dB
    ("T04-T05", 0.62, 2, 2, 1.45), ("T05-T06", 0.71, 2, 2, 2.95),
    ("T06-T07", 0.88, 2, 4, 1.78), ("T12-SUB", 4.10, 2, 6, 3.40),
    ("T01-SUB", 6.20, 4, 8, 7.40), ("SUB-CTRL", 0.15, 2, 0, 1.25),
]
FIBRE_DB = dict(per_km=0.35, connector=0.5, splice=0.1, budget=7.0)   # 10 dB - 3 dB, ch 35

COPPER = [   # link, length m, NEXT margin dB, result
    ("CTRL-01", 42, 6.2, "pass"), ("CTRL-02", 67, 3.1, "pass"), ("CTRL-03", 96, 1.1, "pass"),
    ("CTRL-04", 55, -0.4, "pass"), ("CTRL-05", 31, 7.5, "pass"),
]

POWER = {   # cabinet: (feed A source, feed B source)
    "SUB-RTU": ("UPS-1", "DC-110"), "SUB-CORE": ("UPS-1", "UPS-1"),
    "CTRL-SCADA": ("UPS-1", "UPS-2"), "MET-1": ("PV-AUX", "battery"),
}

FIRMWARE = {   # device: (model, version)
    "SW-T01": ("RS-8", "6.2.1"), "SW-T05": ("RS-8", "6.2.1"), "SW-T09": ("RS-8", "6.1.4"),
    "SW-SUB": ("CS-24", "4.0.2"), "GW-PV1": ("GW-2", "2.3.0"), "GW-PV2": ("GW-2", "2.3.0"),
    "RTU-1": ("RTU-X", "8.4"), "CLK-1": ("TS-1", "3.1"), "SW-SPARE": ("RS-9", "1.0.0"),
}
BASELINE = {"RS-8": "6.2.1", "CS-24": "4.0.2", "GW-2": "2.3.0", "RTU-X": "8.4",
            "TS-1": "3.1"}

BACKUPS = {   # device: (last configuration change, last backup)
    "SW-T01": (date(2027, 3, 2), date(2027, 3, 2)), "SW-T05": (date(2027, 5, 18), date(2027, 3, 2)),
    "SW-SUB": (date(2027, 4, 9), date(2027, 4, 10)), "GW-PV1": (date(2027, 5, 2), date(2027, 5, 2)),
    "RTU-1": (date(2027, 5, 20), date(2027, 2, 14)), "CLK-1": (date(2027, 1, 5), date(2027, 1, 5)),
}

CLOCKS = {"RTU-1": 0.2, "PPC": -0.4, "T05-PLC": 1.1, "T09-PLC": 0.6, "GW-PV1": 14.8,
          "GW-PV2": 0.9, "BESS-EMS": -0.7, "historian": 0.3}          # ms from the clock

# [start: tags]
UNITS = {"power": {"MW", "kW"}, "irradiance": {"W/m2"}, "speed": {"m/s"},
         "temperature": {"C"}, "voltage": {"kV", "V"}, "state": {"-"}}
TAGS = [
    dict(tag="POC.P", kind="power", unit="MW", lo=-5, hi=120, alarm_lo=-2, alarm_hi=105,
         deadband=0.2),
    dict(tag="POC.Q", kind="power", unit="MW", lo=-60, hi=60, alarm_lo=-50, alarm_hi=50,
         deadband=0.2),
    dict(tag="POC.U", kind="voltage", unit="kV", lo=0, hi=160, alarm_lo=125, alarm_hi=139,
         deadband=0.2),
    dict(tag="MET1.GHI", kind="irradiance", unit="W/m2", lo=0, hi=1600, alarm_lo=0,
         alarm_hi=1400, deadband=2),
    dict(tag="MET1.POA", kind="irradiance", unit="W/m2", lo=0, hi=1600, alarm_lo=1450,
         alarm_hi=1400, deadband=2),
    dict(tag="MET1.WS", kind="speed", unit="m/s", lo=0, hi=50, alarm_lo=0, alarm_hi=30,
         deadband=0.1),
    dict(tag="MET1.TAMB", kind="temperature", unit="C", lo=-30, hi=60, alarm_lo=-20,
         alarm_hi=55, deadband=0.2),
    dict(tag="T05.P", kind="power", unit="kW", lo=0, hi=5500, alarm_lo=0, alarm_hi=5300,
         deadband=900),
    dict(tag="T05.WS", kind="speed", unit="km/h", lo=0, hi=50, alarm_lo=0, alarm_hi=25,
         deadband=0.1),
    dict(tag="T05.TGEN", kind="temperature", unit="C", lo=0, hi=200, alarm_lo=0,
         alarm_hi=150, deadband=0.5),
    dict(tag="PVF1.P", kind="power", unit="MW", lo=0, hi=25, alarm_lo=0, alarm_hi=22,
         deadband=0.1),
    dict(tag="PVF1.P", kind="power", unit="MW", lo=0, hi=25, alarm_lo=0, alarm_hi=22,
         deadband=0.1),
    dict(tag="BESS.SOC", kind="state", unit="-", lo=0, hi=100, alarm_lo=10, alarm_hi=90,
         deadband=0.5),
    dict(tag="BESS.T", kind="temperature", unit="C", lo=60, hi=-10, alarm_lo=0,
         alarm_hi=45, deadband=0.2),
    dict(tag="SUB.TX1.T", kind="temperature", unit="C", lo=0, hi=150, alarm_lo=0,
         alarm_hi=95, deadband=""),
]
# [end: tags]

REGMAP = {   # tag: (register type, scale, unit at the device)
    "POC.P": ("float32", 1.0, "MW"), "POC.Q": ("float32", 1.0, "Mvar"),
    "POC.U": ("int16", 0.01, "kV"), "MET1.GHI": ("int16", 1.0, "W/m2"),
    "T05.P": ("int16", 1.0, "kW"), "T05.WS": ("int16", 0.1, "m/s"),
    "PVF1.P": ("int16", 0.001, "MW"), "BESS.SOC": ("int16", 0.1, "%"),
}

FAILOVER = [   # test, expected max s, measured s (None = not done)
    ("ring W-east fibre cut", 0.05, 0.03), ("ring W-west fibre cut", 0.05, 0.04),
    ("core switch A off", 1.0, 0.6), ("SCADA server A off", 30.0, 22.0),
    ("RTU main CPU off", 5.0, 9.5), ("time source A off", 2.0, None),
    ("PPC communication loss", 10.0, 6.0),
]
