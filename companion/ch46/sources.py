"""Chapter 46 - teaching data for the manufacture and acceptance of Plant P's
33 kV cables, terminations, switchgear and protection panels (ch 23-26),
by a fictional cable maker, switchgear maker and panel builder. Values are
illustrative, not makers' data, not a standard's limits (A-482 to A-489).

ENDS        names of the plant's cable ends (turbines, PV blocks, battery
            PCS, switchgear panels) from ch 23
SCHEDULE    the 33 kV cable schedule as issued, with planted faults (A-482)
DRUMS       conductor resistance readings of 400 mm2 drums (A-483)
CRIMPS      pull-test forces of a lot of 240 mm2 lugs (A-484)
PANELS      the 33 kV switchgear line-up of ch 23/26 (A-485)
CONTACTS    main-circuit resistance of each pole (A-485)
TIMES       close and open times of each pole (A-485)
WIRING      one panel's designed and measured connections (A-486)
RELAYS      setting fingerprints of the relays as delivered (A-487)
ONELINE     one feeder from the one-line to compartments, terminals, tests
            (A-488)
"""
from __future__ import annotations

from companion.ch46 import common  # noqa: F401  (puts plantp on the path)
from plantp import convmfg as cm

TURBINES = [f"T{k:02d}" for k in range(1, 13)]
PV = [f"PVF{f}-{b}" for f, n in ((1, 4), (2, 3), (3, 3)) for b in range(1, n + 1)]
BESS = ["BESS-A1", "BESS-A2", "BESS-B1", "BESS-B2"]
# [start: panels]
PANELS = ["INC-A", "WS1", "WS2", "PVF3", "BESS-A", "BC",
          "INC-B", "WS3", "PVF1", "PVF2", "BESS-B", "SST"]
# [end: panels]
ENDS = set(TURBINES) | set(PV) | set(BESS) | {f"SWG/{p}" for p in PANELS}
SIZES = {240, 400, 630}


def schedule() -> list[dict]:
    """33 kV cable schedule: feeder home runs and links (A-482)."""
    rows = []
    k = 1
    strings = {"WS1": TURBINES[0:4], "WS2": TURBINES[4:8], "WS3": TURBINES[8:12]}
    for f, ts in strings.items():
        prev = f"SWG/{f}"
        for i, t in enumerate(ts):
            size = 630 if i == 0 else (400 if i == 1 else 240)
            rows.append(dict(id=f"W{k:03d}", **{"from": prev}, to=t,
                             type="33 kV Al XLPE 3c", size_mm2=size,
                             length_m=850 + 120 * i, cores=3))
            prev, k = t, k + 1
    for f, n in (("PVF1", 4), ("PVF2", 3), ("PVF3", 3)):
        prev = f"SWG/{f}"
        for b in range(1, n + 1):
            blk = f"{f}-{b}"
            rows.append(dict(id=f"W{k:03d}", **{"from": prev}, to=blk,
                             type="33 kV Al XLPE 3c", size_mm2=400 if b == 1 else 240,
                             length_m=600 + 90 * b, cores=3))
            prev, k = blk, k + 1
    for f, ps in (("BESS-A", BESS[:2]), ("BESS-B", BESS[2:])):
        for p in ps:
            rows.append(dict(id=f"W{k:03d}", **{"from": f"SWG/{f}"}, to=p,
                             type="33 kV Al XLPE 3c", size_mm2=240, length_m=180,
                             cores=3))
            k += 1
    # planted faults
    rows[3]["length_m"] = 1.21                       # entered in km
    rows[6]["size_mm2"] = "400mm2"                   # text with unit
    rows[9]["to"] = "T13"                            # no such turbine
    rows[14]["type"] = ""                            # missing type
    rows[17]["id"] = rows[16]["id"]                  # duplicate id
    rows[20]["size_mm2"] = 300                       # not a design size
    return rows


# [start: drums]
DRUMS = [   # drum, length m, measured ohm (whole length), temperature C
    ("D401", 1000, 0.0790, 24.0), ("D402", 1000, 0.0781, 22.0),
    ("D403", 1000, 0.0756, 12.0), ("D404", 1000, 0.0826, 25.0),
    ("D405", 1000, 0.0779, 21.0), ("D406", 1000, 0.0748, 9.0),
]
R20_MAX = 0.0778          # ohm/km, 400 mm2 Al, the design value used as limit
# [end: drums]

CRIMPS = [5.6, 5.9, 5.4, 5.8, 6.0, 5.7, 3.1, 5.5, 5.9, 5.6, 3.4, 5.8]   # kN
CRIMP_MIN = 4.5           # kN, teaching minimum for the lug and tool

CONTACTS = {   # panel: (pole L1, L2, L3) main-circuit resistance, micro-ohm
    "INC-A": (28, 29, 27), "WS1": (35, 36, 34), "WS2": (36, 35, 37),
    "PVF3": (34, 35, 36), "BESS-A": (35, 34, 35), "BC": (29, 28, 30),
    "INC-B": (28, 27, 29), "WS3": (35, 36, 35), "PVF1": (36, 52, 35),
    "PVF2": (34, 36, 35), "BESS-B": (35, 35, 36), "SST": (40, 41, 40),
}
CONTACT_MAX = {"INC-A": 32, "BC": 32, "INC-B": 32}      # else 42, teaching

TIMES = {   # panel: (close ms L1, L2, L3), (open ms L1, L2, L3)
    "WS1": ((55.1, 55.4, 55.0), (32.2, 32.5, 32.1)),
    "WS2": ((55.6, 55.2, 55.3), (32.0, 32.3, 32.4)),
    "WS3": ((55.3, 59.8, 55.2), (32.1, 32.2, 32.6)),
    "PVF1": ((55.0, 55.5, 55.2), (32.4, 32.0, 32.3)),
}
POLE_SPREAD_MAX = 3.0      # ms, teaching

WIRING_DESIGN = [("X1:1", "K1:A1"), ("X1:2", "K1:A2"), ("X1:3", "F11:CT-L1"),
                 ("X1:4", "F11:CT-L2"), ("X1:5", "F11:CT-L3"), ("X1:6", "F11:CT-N"),
                 ("X2:1", "F11:VT-L1"), ("X2:2", "F11:VT-L2"), ("X2:3", "F11:VT-L3"),
                 ("X3:1", "Q1:CLOSE"), ("X3:2", "Q1:TRIP1"), ("X3:3", "Q1:TRIP2"),
                 ("X3:4", "F11:BO1"), ("X3:5", "F11:BO2"), ("X4:1", "Q1:52a"),
                 ("X4:2", "Q1:52b"), ("X4:3", "Q8:89a"), ("X4:4", "Q2:89a")]
# measured: the two trip coils swapped, one CT wire missing, an extra link
WIRING_MEASURED = [c for c in WIRING_DESIGN
                   if c not in (("X3:2", "Q1:TRIP1"), ("X3:3", "Q1:TRIP2"),
                                ("X1:5", "F11:CT-L3"))] + \
    [("X3:2", "Q1:TRIP2"), ("X3:3", "Q1:TRIP1"), ("X4:3", "X4:4")]

RELAY_SETS = {p: {"50": 1.6, "51": 0.9, "51N": 0.2, "tms": 0.15, "fw": "7.3"}
              for p in PANELS if p not in ("BC",)}
RELAY_SETS["PVF2"]["tms"] = 0.25                     # an earlier study's value
RELAY_SETS["SST"]["fw"] = "7.1"                      # older firmware


def relay_fingerprints() -> dict[str, str]:
    return {p: cm.fingerprint(s) for p, s in RELAY_SETS.items()}


# [start: oneline]
ONELINE = [   # feeder WS1: one-line item, compartment, terminal drawing, tests
    ("Q1 circuit breaker", "breaker compartment", "TD-WS1-03", "FAT, SAT"),
    ("Q2 disconnector", "busbar compartment", "TD-WS1-04", "FAT, SAT"),
    ("Q8 earth switch", "cable compartment", "TD-WS1-04", "FAT, SAT"),
    ("T1 current transformers", "cable compartment", "TD-WS1-02", "FAT, SAT"),
    ("T5 voltage transformer", "cable compartment", "", "FAT"),
    ("F11 feeder relay", "LV compartment", "TD-WS1-01", "FAT, SAT"),
    ("W001 cable to T01", "cable compartment", "TD-WS1-05", ""),
    ("surge arresters", "cable compartment", "TD-WS1-05", "SAT"),
]
# [end: oneline]
