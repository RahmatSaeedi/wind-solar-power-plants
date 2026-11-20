"""Chapter 42 - synthetic data for the manufacture of Plant P's fictional
WT-5.0-150 (A-211: rotor 150 m, hub 100 m, 5 MW, geared drivetrain
D-011) by fictional suppliers (teaching values A-450 to A-457). Nothing
here is a real design, supplier or process recipe.

TURBINE    the turbine values of ch 11 used again here
TREE       subassembly/interface tree: id, parent, name, mass t, tier,
           carries rotor loads?, interfaces
FIBRES, RESIN, CORES   textbook composite material properties
INSERTS    the blade root joint
RUNIN      synthetic gearbox run-in vibration (ten units, three planted
           faults)
NCRS       nonconformity reports of the turbine's suppliers
"""
from __future__ import annotations

import math
import random

from companion.ch42 import common  # noqa: F401  (puts plantp on the path)

TURBINE = dict(p_rated_kw=5000.0, radius=75.0, hub=100.0, rpm_rated=11.5,
               eta_drive=0.94, blade_t=22.0, r_cg=22.0, thrust_kn=923.0,
               flap_mnm=15.4, edge_mnm=4.75, ratio=100.4, n_gen=1155.0,
               tower_t=340.0, nacelle_t=160.0, hub_t=45.0)      # ch 11

# [start: tree]
TREE = [  # id, parent, name, mass t, tier, load path?, interfaces
    ("WTG", None, "turbine", 0, 0, True, []),
    ("ROT", "WTG", "rotor", 0, 1, True, ["NAC"]),
    ("BLD", "ROT", "blade (x3)", 66.0, 2, True, ["HUB", "LPS"]),
    ("HUB", "ROT", "hub casting", 30.0, 2, True, ["BLD", "PIT", "MSH"]),
    ("PIT", "ROT", "pitch bearings and drives", 15.0, 2, True, ["HUB", "CTL"]),
    ("NAC", "WTG", "nacelle", 0, 1, True, ["TWR"]),
    ("MSH", "NAC", "main shaft and bearing", 35.0, 2, True, ["HUB", "GBX"]),
    ("GBX", "NAC", "gearbox", 45.0, 2, True, ["MSH", "GEN", "FRM"]),
    ("GEN", "NAC", "generator", 12.0, 2, False, ["GBX", "CNV"]),
    ("CNV", "NAC", "converter", 6.0, 2, False, ["GEN", "TRF"]),
    ("FRM", "NAC", "bedplate and frame", 40.0, 2, True, ["GBX", "YAW"]),
    ("YAW", "NAC", "yaw bearing, drives, brakes", 14.0, 2, True, ["FRM", "TWR"]),
    ("TWR", "WTG", "tower (4 sections)", 340.0, 1, True, ["YAW", "FND"]),
    ("FND", "WTG", "anchor cage and foundation", 1700.0, 1, True, ["TWR"]),
    ("TRF", "TWR", "dry transformer, tower base", 8.0, 2, False, ["CNV", "FND"]),
    ("LPS", "WTG", "lightning protection", 0.5, 2, False, ["BLD", "FND"]),
    ("CTL", "WTG", "controller and sensors", 1.5, 2, False, ["PIT", "YAW"]),
]
# [end: tree]

# [start: materials]
FIBRES = {"E-glass": dict(e_gpa=72.0, rho=2.55),
          "carbon (standard modulus)": dict(e_gpa=230.0, rho=1.78)}
RESIN = dict(name="epoxy", e_gpa=3.2, rho=1.15)
CORES = {"balsa": 0.15, "PET foam": 0.10}             # density, g/cm3
# [end: materials]

INSERTS = dict(n=96, circle_m=3.2, preload_kn=320.0)   # A-451


def _runin(seed: int = 4201, fs: float = 2048.0, secs: float = 4.0):
    """Ten gearbox high-speed-shaft accelerations on the run-in bench at
    1155 rpm (19.25 Hz); mesh at 27 x shaft. Unit G04 has a damaged
    tooth (sidebands at shaft rate around mesh), G07 an imbalance
    (strong 1x), G09 a misalignment (strong 2x)."""
    rng = random.Random(seed)
    f1, mesh = 1155.0 / 60.0, 27 * 1155.0 / 60.0
    n = int(fs * secs)
    units = {}
    for u in range(1, 11):
        name = f"G{u:02d}"
        a1 = 0.20 + (1.6 if name == "G07" else 0.0)
        a2 = 0.10 + (1.2 if name == "G09" else 0.0)
        am = 1.0 + rng.gauss(0, 0.05)
        sb = 0.45 if name == "G04" else 0.02
        sig = []
        for k in range(n):
            t = k / fs
            x = (a1 * math.sin(2 * math.pi * f1 * t)
                 + a2 * math.sin(2 * math.pi * 2 * f1 * t + 0.3)
                 + am * math.sin(2 * math.pi * mesh * t)
                 + sb * math.sin(2 * math.pi * (mesh - f1) * t)
                 + sb * math.sin(2 * math.pi * (mesh + f1) * t)
                 + rng.gauss(0, 0.15))
            sig.append(x)
        units[name] = sig
    return fs, units


NCRS = [  # id, part, defect, severity 1-3, location, days open
    ("NCR-101", "blade B-117", "dry fibre spot in shell, 40 x 60 mm", 2,
     "factory", 3),
    ("NCR-102", "blade B-121", "bond-line gap in web joint over 0.8 m", 3,
     "factory", 9),
    ("NCR-103", "hub H-022", "casting porosity at a flange, UT indication",
     3, "factory", 21),
    ("NCR-104", "tower section T3-14", "flange flatness over tolerance", 2,
     "factory", 5),
    ("NCR-105", "gearbox G04", "sidebands at mesh on run-in", 3, "factory", 2),
    ("NCR-106", "blade B-109", "transport frame scratched leading edge", 1,
     "port", 1),
    ("NCR-107", "nacelle N-05", "cable tray bolts missing", 1, "site", 4),
    ("NCR-108", "pitch bearing P-31", "seal damaged at receipt", 2, "site", 12),
]
