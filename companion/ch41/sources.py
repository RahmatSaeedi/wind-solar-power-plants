"""Chapter 41 - synthetic manufacturing data for Plant P's fictional module
PVM-550 (data pack 1.1.0: 144 half-cut mono cells, 550 W) made by a
fictional module factory (teaching values A-442 to A-449). Nothing here
is a real product, a real factory or a process recipe: process steps are
named with their purpose and the variable that is controlled, never with
settings.

BOM          bill of materials of one module with mass and controls
CELL_STEPS   the cell process map: purpose, controlled variable, defect
LINE         the module line: station, takt seconds, checks
FLASH        flash-test results of a 3,000-module lot (planted outliers)
EL_GRADES    electroluminescence grades of the same lot
DEFECTS      module defect catalogue: cause, detection, consequence, test
CELL_BINS    current bins of the cells sent to the module line
PLANT        Plant P string and site values for integration checks
"""
from __future__ import annotations

import random

from companion.ch41 import common  # noqa: F401  (puts plantp on the path)

MODULES_PLANT = 109_200            # D-013: 10 x 21 x 20 strings x 26

# [start: bom]
BOM = [  # (part, qty, unit, mass kg, critical control) - A-442
    ("front glass, tempered, AR-coated", 1, "pc", 20.7, "thickness, flatness"),
    ("half-cut cells", 144, "pc", 0.85, "current bin, EL grade"),
    ("interconnect ribbon / wire", 1, "set", 0.35, "solder or bond peel"),
    ("encapsulant sheets", 2, "pc", 1.2, "gel content, laminated"),
    ("backsheet", 1, "pc", 0.6, "adhesion, insulation"),
    ("aluminium frame", 1, "set", 3.5, "dimensions, corners"),
    ("frame sealant / adhesive", 1, "set", 0.3, "bead, cure"),
    ("junction box, 3 bypass diodes", 1, "pc", 0.25, "diode test, potting"),
    ("cables and connectors", 1, "set", 0.35, "type matches the plant"),
    ("labels (rating, serial)", 1, "set", 0.0, "serial = flash record"),
]
# [end: bom]

CELL_STEPS = [  # (step, purpose, controlled variable, typical defect)
    ("wafer inspection", "reject cracked or thin wafers",
     "thickness, cracks, resistivity", "micro-crack, chipped edge"),
    ("texturing", "trap light by surface structure", "reflectance",
     "uneven texture -> colour, current loss"),
    ("junction formation", "make the p-n junction",
     "sheet resistance", "non-uniform doping -> FF loss"),
    ("passivation", "slow surface recombination",
     "lifetime, layer thickness", "poor passivation -> Voc loss"),
    ("anti-reflection coating", "cut reflection, add passivation",
     "thickness, colour", "colour mismatch, current loss"),
    ("metallisation", "print contacts and fingers",
     "finger width, line resistance", "broken fingers -> Rs, hot spots"),
    ("firing / thermal step", "form contacts", "temperature profile",
     "poor contact -> Rs; warping"),
    ("edge isolation", "stop shunts at the edge", "edge leakage",
     "shunt -> low Rsh, reverse-bias heating"),
    ("cell sorting", "bin by current and appearance", "IV, EL, colour",
     "mixed bins -> mismatch"),
    ("laser cutting (half-cut)", "halve the cell current",
     "cut quality", "edge damage -> cracks later"),
]

# [start: line]
LINE = [  # (station, purpose, takt s, in-line check) - A-443
    ("stringer", "join cells into strings", 28, "string EL, peel sample"),
    ("lay-up", "glass, encapsulant, strings, busbars", 30, "visual, spacing"),
    ("pre-lamination EL", "find cracks before it is sealed", 25, "EL image"),
    ("laminator", "bond and encapsulate", 30, "gel content sample, voids"),
    ("trimming", "cut excess encapsulant", 20, "edge visual"),
    ("framing", "frame and seal", 28, "frame dimensions, sealant"),
    ("junction box", "attach, connect, pot", 26, "diode check"),
    ("curing", "cure sealant and potting", 0, "time in buffer"),
    ("IV flash and EL", "rate the module", 22, "Pmax, EL grade"),
    ("insulation test", "safety of the package", 18, "insulation, earth"),
    ("packing", "pallet and label", 24, "label = flash record"),
]
# [end: line]


def _flash(seed: int = 41):
    """Pmax at STC (W) of a 3,000-module lot; planted outliers: 6 cracked
    modules low, 2 with a failed diode lower, 3 mis-binned high, and a
    shift of the flash tester from module 2,401 (reference cell drift)."""
    rng = random.Random(seed)
    p = [round(rng.gauss(552.4, 1.6), 1) for _ in range(3000)]
    for k in (211, 655, 1023, 1490, 1902, 2777):
        p[k] = round(p[k] - rng.uniform(9, 14), 1)       # cracks
    for k in (840, 2310):
        p[k] = round(p[k] - rng.uniform(170, 190), 1)    # a bypass diode open
    for k in (402, 1555, 2049):
        p[k] = round(p[k] + rng.uniform(8, 10), 1)       # cells of a higher bin
    for k in range(2400, 3000):
        p[k] = round(p[k] + 2.4, 1)                      # tester drift
    return p


FLASH = _flash()


def _el(seed: int = 42):
    rng = random.Random(seed)
    grades = ["A"] * 3000
    for k in rng.sample(range(3000), 90):
        grades[k] = "B"
    for k in (211, 655, 1023, 1490, 1902, 2777):
        grades[k] = "C"
    return grades


EL_GRADES = _el()

DEFECTS = [  # (defect, cause in the process, detected by, consequence)
    ("cell micro-crack", "handling, stringer, lamination pressure",
     "EL image", "inactive area grows in the field -> power loss"),
    ("cold solder / weak bond", "temperature, flux, contact force",
     "peel test, EL, flash Rs", "hot joint, power loss"),
    ("lamination void / bubble", "moisture, vacuum, contamination",
     "visual, pre-lam EL", "delamination, moisture path"),
    ("low gel content", "lamination cure", "gel-content sample",
     "creep, delamination"),
    ("delamination", "adhesion, contamination", "visual, damp heat",
     "moisture ingress, corrosion"),
    ("corrosion of contacts", "moisture, acetic acid", "EL after stress",
     "series resistance rises"),
    ("hot spot", "shaded or cracked cell, shunt", "IR under bias",
     "burn mark, glass breakage, fire risk"),
    ("bypass diode open or short", "assembly, surge", "diode check, flash",
     "string loses a third, or hot spot unprotected"),
    ("insulation failure", "backsheet, edge seal", "insulation test",
     "leakage, earth fault in the plant"),
]

CELL_BINS = [13.80, 13.90, 14.00, 14.10, 14.20]     # full-cell Isc bin edges, A

PLANT = dict(v_max=1500.0, t_min_c=-15.0, t_hot_c=72.0, modules_string=26,
             connector_plant="type P", inverter_mppt_v=(933.0, 1300.0))  # D-012/13
