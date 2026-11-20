"""Chapter 40 - synthetic factory data for the ten PV station skids of
Plant P, built by a fictional skid integrator (teaching values A-434 to
A-441). Nothing here describes a real company, product or process recipe.

BLOCKS      the ten PV blocks (ch 23 tags) and the skid serial of each
SKID        one skid's bill of materials, level 1, with make/buy
ROUTE       operations OP10-OP90: station, hours, first-pass yield, rework
DEMAND      skids needed, weeks and shift hours available
RESIST      joint resistance at FAT, micro-ohm, five joints a skid
GRR         micro-ohmmeter study, 10 joints x 3 inspectors x 2 repeats
FMEA        process FMEA of the skid line
GENEALOGY   per skid: build days, OP40 torque tool, lug lot, serials
TOOL_CHECKS daily checks of torque wrench TW-14 against a torque analyser
DOSSIER     the test dossier of skid S-07, with the ITP it answers to
PILOT       failure times in the pilot extended-run test
CONSEQUENCE the plant-side values of the escaped defect
"""
from __future__ import annotations

import random

from companion.ch40 import common  # noqa: F401  (puts plantp on the path)

BLOCKS = ["PVF1-1", "PVF1-2", "PVF1-3", "PVF1-4", "PVF2-1", "PVF2-2",
          "PVF2-3", "PVF3-1", "PVF3-2", "PVF3-3"]
SERIALS = [f"S-{k:02d}" for k in range(1, 11)]

# [start: bom]
SKID = [  # (item, qty, unit, make/buy, source, lead weeks)
    ("base frame, welded and painted", 1, "pc", "make", "own shop", 3),
    ("unit transformer 5.6 MVA (ch 39, U-A)", 1, "pc", "buy", "U-A", 30),
    ("central inverter 5 MW", 1, "pc", "buy", "inverter maker", 20),
    ("ring main unit 33 kV", 1, "pc", "buy", "switchgear maker", 16),
    ("LV busbar set (24 bolted joints)", 1, "set", "make", "own shop", 2),
    ("LV cable with crimped lugs", 36, "end", "make", "own shop", 1),
    ("auxiliary and control panel", 1, "pc", "buy", "panel builder", 10),
    ("earthing and bonding kit", 1, "set", "buy", "stockist", 2),
    ("fasteners M12 8.8, plated", 120, "pc", "buy", "stockist", 1),
]
# [end: bom]

# [start: route]
ROUTE = [  # (op, work, station, hours, first-pass yield, rework hours)
    ("OP10", "weld, inspect, paint base frame", "S1", 16.0, 0.97, 6.0),
    ("OP20", "receive and inspect equipment", "S2", 4.0, 0.99, 8.0),
    ("OP30", "set and bolt equipment on frame", "S2", 10.0, 0.99, 4.0),
    ("OP40", "LV busbar and cable terminations", "S3", 14.0, 0.95, 5.0),
    ("OP50", "MV cable termination at RMU", "S4", 6.0, 0.98, 6.0),
    ("OP60", "auxiliary and control wiring", "S5", 12.0, 0.94, 4.0),
    ("OP70", "earthing and bonding", "S4", 4.0, 0.99, 2.0),
    ("OP80", "factory acceptance test", "S6", 8.0, 0.92, 6.0),
    ("OP90", "preserve, pack, dispatch", "S6", 5.0, 1.00, 0.0),
]
DEMAND = dict(skids=10, weeks=4, hours_week=40.0)
# [end: route]

# joint resistance at FAT, micro-ohm, USL 20 (A-436): S-05..S-07 were
# built with the drifted wrench and show the shift
_rng = random.Random(40)
RESIST = {}
for _k, _s in enumerate(SERIALS, 1):
    _mu, _sd = (15.6, 2.2) if _k in (5, 6, 7) else (12.0, 1.4)
    RESIST[_s] = [round(_rng.gauss(_mu, _sd), 1) for _ in range(5)]

# gauge study: true joint values, inspector bias, repeatability (A-436)
_rng2 = random.Random(41)
_true = [round(_rng2.gauss(12.5, 1.6), 2) for _ in range(10)]
_bias = [0.0, 0.18, -0.12]


def _grr(rep_sd: float, seed: int):
    r = random.Random(seed)
    return [[[round(t + b + r.gauss(0, rep_sd), 2) for _ in range(2)]
             for b in _bias] for t in _true]


GRR = _grr(0.32, 42)              # hand-held probes
GRR_FIXTURE = _grr(0.12, 43)      # after the probe fixture

# [start: fmea]
FMEA = [  # process FMEA of the skid line (ratings 1-10, A-437)
    dict(op="OP40", mode="LV joint under-torqued", effect="hot joint, trip,"
         " fire risk", cause="torque tool drift", s=9, o=3, d=8),
    dict(op="OP40", mode="lug crimped with wrong die", effect="hot lug",
         cause="die not checked", s=8, o=3, d=6),
    dict(op="OP50", mode="MV stress cone misplaced",
         effect="MV fault", cause="jointer error", s=10, o=2, d=7),
    dict(op="OP60", mode="control wire on wrong terminal",
         effect="wrong signal", cause="drawing revision", s=5, o=5, d=3),
    dict(op="OP70", mode="earth bond missing", effect="touch voltage",
         cause="step skipped", s=9, o=2, d=5),
    dict(op="OP10", mode="paint film too thin", effect="corrosion",
         cause="gun setting", s=4, o=4, d=4),
    dict(op="OP30", mode="transformer damaged in handling",
         effect="oil leak", cause="lift plan", s=7, o=2, d=4),
    dict(op="OP90", mode="desiccant missing in packing",
         effect="condensation", cause="pack list", s=5, o=3, d=6),
]
# [end: fmea]

# [start: genealogy]
GENEALOGY = {  # serial: build days of OP40, torque tool, lug lot, serials
    "S-01": dict(op40=(3, 4), tool="TW-11", lugs="L-2205", tx="TX-5101"),
    "S-02": dict(op40=(5, 6), tool="TW-11", lugs="L-2205", tx="TX-5102"),
    "S-03": dict(op40=(7, 8), tool="TW-14", lugs="L-2207", tx="TX-5104"),
    "S-04": dict(op40=(9, 10), tool="TW-14", lugs="L-2207", tx="TX-5103"),
    "S-05": dict(op40=(12, 13), tool="TW-14", lugs="L-2208", tx="TX-5106"),
    "S-06": dict(op40=(13, 14), tool="TW-14", lugs="L-2208", tx="TX-5105"),
    "S-07": dict(op40=(15, 16), tool="TW-14", lugs="L-2208", tx="TX-5107"),
    "S-08": dict(op40=(17, 18), tool="TW-11", lugs="L-2208", tx="TX-5108"),
    "S-09": dict(op40=(19, 20), tool="TW-15", lugs="L-2209", tx="TX-5110"),
    "S-10": dict(op40=(21, 22), tool="TW-15", lugs="L-2209", tx="TX-5109"),
}
TOOL_CHECKS = {  # day: reading of TW-14 on the analyser at 70 N m set
    8: 70.4, 9: 69.8, 10: 70.6, 11: 70.1, 16: 78.9}   # days 12-15 missing
# [end: genealogy]

# [start: dossier]
ITP = {  # test or check: point type (H hold, W witness, R review)
    "insulation resistance LV": "W", "insulation resistance MV": "W",
    "MV termination record": "R", "torque record OP40": "R",
    "functional test": "H", "secondary injection of relays": "W",
    "serials against genealogy": "R", "preservation check": "R",
    "earth bond continuity": "R", "paint film thickness": "R",
    "LV busbar visual": "W", "nameplate photos": "R", "packing list": "R",
}
DOSSIER = [  # the S-07 dossier as received (A-438)
    dict(check="insulation resistance LV", day=19, result="1,850 MOhm",
         instrument="IR-03", signed=["integrator", "owner"]),
    dict(check="insulation resistance MV", day=19, result="9,400 MOhm",
         instrument="IR-03", signed=["integrator", "owner"]),
    dict(check="MV termination record", day=17, result="done",
         jointer_cert=None, signed=["integrator"]),
    dict(check="torque record OP40", day=16, result="24 of 24 at 70 N m",
         instrument="TW-14", signed=["integrator"]),
    dict(check="functional test", day=19, result="pass",
         signed=["integrator"]),
    dict(check="secondary injection of relays", day=19, result="pass",
         instrument="SI-02", procedure_rev="B", signed=["integrator",
                                                         "owner"]),
    dict(check="serials against genealogy", day=19, result="TX-5106",
         signed=["integrator"]),
    dict(check="earth bond continuity", day=18, result="0.02 ohm",
         instrument="LO-01", signed=["integrator"]),
    dict(check="paint film thickness", day=6, result="185 um",
         instrument="DFT-02", signed=["integrator"]),
    dict(check="LV busbar visual", day=16, result="no damage",
         signed=["integrator", "owner"]),
    dict(check="nameplate photos", day=19, result="4 photos",
         signed=["integrator"]),
    dict(check="packing list", day=20, result="complete",
         signed=["integrator"]),
    dict(check="preservation check", day=20, result="desiccant fitted",
         deviation="cable gland type changed, agreed by phone",
         signed=["integrator"]),
]
CAL_DUE = {"IR-03": 17, "SI-02": 40, "TW-14": 30, "LO-01": 60,
           "DFT-02": 45}                     # calibration valid to day
PROCEDURE_REV = {"secondary injection of relays": ("C", 18)}  # rev, released
# [end: dossier]

# pilot extended-run test of the first skids: cumulative hours at each
# failure, test stopped at 2,000 h (A-439)
PILOT = [35.0, 90.0, 160.0, 300.0, 420.0, 650.0, 900.0, 1300.0, 1800.0]
PILOT_T = 2000.0
TARGET_MTBF = 1000.0
# latent-defect sub-population of control boards (A-439)
LATENT = dict(share=0.02, beta=0.7, eta_h=300.0, boards=10 * 6)

CONSEQUENCE = dict(block_mw=5.0, cf_july=0.27, outage_days=9,  # A-440
                   price=70.0, repair_ku=35.0, check_ku=4.0)
