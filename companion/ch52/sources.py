"""Chapter 52 sources: the maintained plant of Plant P after its first
operating year (ch 51). All values are synthetic teaching values
(A-530 to A-537); failure rates follow ch 18 (A-288) where it gave them.

Units: hours (h), years (yr), MW, MWh, k u (thousand currency units).
"""
from __future__ import annotations

from datetime import date

YEAR_H = 8760.0
TODAY = date(2029, 6, 1)          # end of the first operating year (as ch 51)

# ------------------------------------------------ A. strategy (A-530)
# asset class: (units, failures a unit-year, MTTR active h, logistics delay h,
# PM hours a unit-year, consequence 1-5, MW a unit)
CLASSES = {
    "PV inverter": (10, 0.5, 24.0, 48.0, 16.0, 3, 5.0),
    "PV unit transformer": (10, 0.02, 48.0, 672.0, 8.0, 3, 5.0),
    "PV combiner box": (210, 0.05, 4.0, 24.0, 1.0, 1, 0.24),
    "wind turbine (minor)": (12, 5.0, 6.0, 8.0, 0.0, 2, 5.0),
    "wind turbine (major)": (12, 0.06, 240.0, 1200.0, 0.0, 4, 5.0),
    "turbine PM visit": (12, 0.0, 0.0, 0.0, 60.0, 2, 5.0),
    "BESS PCS": (4, 0.5, 24.0, 48.0, 12.0, 2, 5.0),
    "BESS container": (8, 0.3, 24.0, 48.0, 16.0, 2, 2.5),
    "main transformer": (2, 0.01, 240.0, 4140.0, 24.0, 5, 63.0),
    "132 kV line (permanent fault)": (1, 2.0, 4.2, 0.0, 16.0, 5, 150.0),
    "33 kV collector cable (per km)": (38, 0.01, 72.0, 48.0, 0.0, 3, 0.0),
    "PPC": (1, 0.1, 4.0, 4.0, 4.0, 5, 150.0),
}

WORK_HOURS = dict(technicians=10, hours_each=1_804, overhead=0.35)   # ch 51 hours a person

# ------------------------------------------------ B. subsystem tasks (A-531)
PM_TASKS = [   # (subsystem, task, interval months, hours a unit, units, needs outage)
    ("PV", "visual and thermography of modules", 12, 0.02, 109_200 // 26, False),
    ("PV", "string I-V sample (5 %)", 12, 0.5, 210, False),
    ("PV", "combiner torque and fuses", 12, 1.0, 210, True),
    ("PV", "inverter filters and fans", 6, 4.0, 10, True),
    ("PV", "tracker drive and stow test", 12, 1.5, 2_100, False),
    ("wind", "turbine annual service", 12, 60.0, 12, True),
    ("wind", "blade inspection (drone)", 12, 3.0, 12, True),
    ("wind", "oil sample gearbox", 6, 0.5, 12, False),
    ("converter", "BESS PCS service", 12, 12.0, 4, True),
    ("transformer", "main transformer DGA", 3, 1.0, 2, False),
    ("transformer", "unit transformer inspection", 12, 4.0, 10, True),
    ("switchgear", "33 kV breaker service", 36, 8.0, 12, True),
    ("cables", "termination thermography", 12, 0.3, 120, False),
    ("storage", "container HVAC and filters", 3, 2.0, 8, False),
    ("civil", "drainage and roads after rains", 6, 16.0, 1, False),
    ("sensors", "pyranometer cleaning and check", 1, 0.3, 4, False),
    ("comms", "fibre ring loss check", 12, 4.0, 3, False),
]

# ------------------------------------------------ C. diagnosis (A-532)
EVENTS_T03 = [   # turbine T03 converter trip: (time s from 14:02:00, source, event)
    (0.000, "PCS-T03", "DC-link overvoltage"), (0.004, "PCS-T03", "converter trip"),
    (0.020, "T03 controller", "emergency pitch"), (0.150, "SCADA", "T03 grid loss alarm"),
    (-0.120, "WS1 relay", "voltage dip 0.78 pu"), (2.300, "SCADA", "T03 stopped"),
    (-0.118, "T04 controller", "FRT active"), (0.900, "T04 controller", "FRT ended")]

# ------------------------------------------------ D. troubleshooting case (A-533)
CASE = dict(blocks=10, days=120, bad_block=6, cb_out_day=52, cb_strings=20,
            strings_block=420, partial_day=75, partial_strings=2,
            stale_days=(88, 89), sensor_drift=(40, 46, 0.06), repair_day=96)

# ------------------------------------------------ G. cleaning (A-535)
CLEAN_METHODS = {   # method: (L/module, recovered %, breakage per 10^5 passes,
    #                  crew h per MW, runoff L/module)
    "truck with brush, RO water": (1.0, 3.4, 2.0, 2.2, 0.35),
    "truck, high pressure lance": (1.5, 3.6, 9.0, 1.8, 0.80),
    "waterless robot (dry brush)": (0.0, 2.6, 0.5, 0.3, 0.0),
    "manual, low pressure, RO": (0.8, 3.5, 1.0, 9.0, 0.25),
}
SOILING = dict(rate_pct_day=0.12, price=70.0, mwh_day=300.0, water_u_m3=3.0)

# ------------------------------------------------ H. export assets (A-536)
EXPORT_ASSETS = {   # asset: (owner, inspection months, last day done, outage needed)
    "132 kV line towers T01-T38": ("network owner", 12, 160, False),
    "line insulators and fittings": ("network owner", 12, 0, True),
    "line corridor vegetation": ("plant", 6, 200, False),
    "plant HV bay (E1)": ("plant", 12, 300, True),
    "grid HV bay": ("network owner", 12, 120, True),
    "33 kV cable terminations": ("plant", 12, 330, False),
    "protection relays (plant end)": ("plant", 48, 0, True),
    "line differential teleprotection": ("shared", 12, 250, True),
    "access road to line towers": ("plant", 6, 120, False),
}
SPARES_EXPORT = {"132 kV insulator string": (6, 2), "33 kV termination kit": (12, 8),
                 "CT 600/1 A": (2, 0), "surge arrester 132 kV": (3, 1)}   # (needed, held)

# ------------------------------------------------ I. CMMS (A-537)
HIERARCHY = {
    "=PVF2-3": ["=PVF2-3-INV", "=PVF2-3-TR", "=PVF2-3-CB01", "=PVF2-3-CB02"],
    "=WT03": ["=WT03-GBX", "=WT03-CNV", "=WT03-PIT", "=WT03-YAW"],
    "=BESS-A": ["=BESS-A-PCS1", "=BESS-A-C1", "=BESS-A-C2"],
}
WORK_ORDERS = [   # id, asset, type, failure code, labour h, parts, test record, closed day
    ("WO-0412", "=WT03-CNV", "CM", "CNV-IGBT", 14.0, "IGBT stack", True, 120),
    ("WO-0418", "=WT03", "CM", "", 3.0, "", False, 125),
    ("WO-0430", "=PVF2-3-CB01", "CM", "FUSE-OPEN", 2.0, "fuse 15 A x3", True, 140),
    ("WO-0431", "", "CM", "FUSE-OPEN", 2.5, "fuse 15 A x2", True, 141),
    ("WO-0455", "=BESS-A-PCS1", "PM", "", 12.0, "filters", True, 150),
    ("WO-0460", "=WT03-PIT", "CM", "PIT-BAT", 6.0, "pitch battery", False, 0),
    ("WO-0461", "=WT03-PIT", "CM", "PIT-BAT", 5.5, "pitch battery", True, 172),
    ("WO-0477", "=PVF2-3-INV", "CM", "FAN", 1.5, "fan", True, 180),
    ("WO-0490", "=WT07-GBX", "CM", "GBX-BRG", 40.0, "bearing", True, 201),
    ("WO-0502", "=BESS-A-C2", "CM", "HVAC-FLT", 8.0, "compressor", False, 0),
]
FAILURE_CODES = {"CNV-IGBT", "FUSE-OPEN", "PIT-BAT", "FAN", "GBX-BRG", "HVAC-FLT",
                 "INS-FLT", "CON-WATER"}
