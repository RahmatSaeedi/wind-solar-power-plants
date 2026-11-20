"""Chapter 43 - teaching data for the design review and factory acceptance
of Plant P's main transformer as bought (ch 25, D-029: bid B) and of the
PV unit transformer of ch 39 (offer U-A). The factory, its traveler and
its test report are fictional; values are illustrative of their kind,
not a maker's data and not a standard's limits (A-458 to A-465).

MAIN_B      the 63 MVA unit: rating, guarantees, contract tolerances
DESIGN      a preliminary design that reproduces the guarantees (A-458)
STEELS      electrical-steel grades: loss at 1.7 T, building factor (A-459)
COSTS       teaching material prices and the A/B loss factors of ch 25
PVU         the 5.6 MVA PV unit transformer (ch 39, offer U-A)
REQS        requirement -> purchase clause -> test -> evidence (A-460)
TRAVELER    the factory route of unit T1 with its records (A-461)
TESTS       the routine and type test report of T1 (A-462)
DGA         dissolved gases before and after the heat run (A-463)
"""
from __future__ import annotations

from companion.ch43 import common  # noqa: F401  (puts plantp on the path)

# [start: main]
MAIN_B = dict(   # ch 25 D-029, bid B; tolerances are contract teaching values
    s_mva=63.0, s_onan_mva=50.0, hv_kv=132.0, lv_kv=33.0, vector="YNd11",
    uk_pct=12.0, p0_kw=42.0, pk_kw=290.0, taps=(-10.0, 10.0, 1.25),
    transport_t=72.0, mass_t=95.0, oil_m3=22.0, top_oil_rise=60.0, winding_rise=65.0,
    sound_lwa=88.0, tol=dict(p0=0.15, pk=0.15, total=0.10, uk=0.075, ratio=0.5))
# [end: main]

# [start: design]
DESIGN = dict(   # preliminary design of the reviewer, not the maker's (A-458)
    e_t=110.0, b_peak=1.70, stacking=0.97, fill=0.94,
    n_lv=300, n_hv=693, tap_turns=9,
    h=2.05, end_ins=0.35, gap_core=0.025, a1=0.065, a12=0.075, a2=0.110,
    j_a_mm2=3.5, eddy_share=0.06, stray_share=0.12,
    steel="conventional GO", leg_gap=0.03)
# [end: design]

STEELS = {   # W/kg at 1.7 T, 50 Hz; building factor of the core form (A-459)
    "conventional GO": dict(w=1.15, bf=1.22, price=2.6),
    "high-permeability GO": dict(w=0.90, bf=1.12, price=3.2),
    "domain-refined HGO": dict(w=0.80, bf=1.12, price=3.8),
}

COSTS = dict(copper=9.0, steel_default=2.6,      # u per kg (teaching)
             a_kw=6.84, b_kw=0.88)               # k u per kW (ch 25, 70 u/MWh)

PVU = dict(s_mva=5.6, hv_kv=33.0, lv_kv=0.6, vector="Dyn11", p0_kw=4.1,
           pk_kw=41.0, uk_pct=7.0, ambient_c=45.0)

# [start: reqs]
REQS = [   # requirement, purchase clause, test or evidence, status at FAT
    ('63 MVA ONAF, 50 MVA ONAN', 'C-2.1 rating',
     'temperature-rise test', 'done'),
    ('132/33 kV YNd11', 'C-2.2 ratio, vector',
     'ratio and vector test', 'done'),
    ('uk 12 % +-7.5 %', 'C-2.3 impedance',
     'load-loss and impedance test', 'done'),
    ('OLTC +-10 % in 17 positions', 'C-2.4 taps',
     'ratio at every tap; OLTC tests', 'done'),
    ('P0 42, Pk 290 kW, A/B deductions', 'C-4.1 losses',
     'loss tests, corrected', 'done'),
    ('top oil 60 K, winding 65 K', 'C-2.5 temperature',
     'heat run, cooling curve', 'done'),
    ('dielectric to the insulation levels', 'C-3.1 insulation',
     'dielectric tests, PD', 'done'),
    ('short-circuit withstand', 'C-3.4 short circuit',
     'test or design review', 'open'),
    ('LWA 88 dB(A)', 'C-2.7 sound',
     'sound test', 'done'),
    ('frequency-response baseline', 'C-5.2 records',
     'FRA files', 'partial'),
    ('dissolved gas before/after heat run', 'C-5.3 records',
     'DGA report', 'done'),
    ('72 t shipped, impact recorder', 'C-6.1 shipping',
     'weighing, recorder', 'open'),
]
# [end: reqs]

# [start: traveler]
TRAVELER = [   # stage, record expected, record found, note (A-461)
    ("design release", "approved drawings rev C", "rev C", ""),
    ("core steel receipt", "mill certificate per coil", "12 of 12", ""),
    ("core cutting", "burr height per batch", "7 of 8 batches", "batch 8 missing"),
    ("core stacking", "bare-core loss check", "done, 40.8 kW at 1.7 T", ""),
    ("LV winding", "height and radial build", "2,052 mm", ""),
    ("HV winding", "height and radial build", "2,041 mm", "11 mm shorter than LV"),
    ("active part", "clamping force record", "done", ""),
    ("drying", "end-point: water extraction rate", "not found", "end point not shown"),
    ("tank", "pressure and vacuum test", "done", ""),
    ("oil", "water ppm and breakdown before filling", "18 ppm at 20 C",
     "over the 10 ppm limit"),
    ("filling, leak test", "leak test record", "done", ""),
    ("routine tests", "test report", "TR-T1 rev 0", ""),
    ("preservation", "N2 pressure and impact recorder fitted", "N2 only", "recorder missing"),
]
# [end: traveler]

# [start: tests]
TESTS = dict(   # measured values of unit T1 (A-462)
    ratio_err_pct={-10.0: -0.39, -5.0: -0.17, 0.0: 0.04, 5.0: 0.22,
                   8.75: 0.62, 10.0: 0.39},
    r_hv_ohm=0.5293, r_lv_ohm=0.0693, r_temp_c=22.0,    # per phase, cold
    p0_meas_kw=43.5, u_rms_over_mean=1.03,   # mean-value meter at rated
    pk_meas_kw=268.0, pk_temp_c=25.0, uk_pct=12.6,
    top_oil_rise=57.0, oil_avg_rise=46.0, ambient_c=21.0,
    cool_t_min=[2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 15.0, 20.0],
    cool_r_hv=[0.6549, 0.6475, 0.6418, 0.6377,
               0.6340, 0.6311, 0.6286, 0.6254],
    report_rise=62.0,                        # from the 2-minute reading
    lpa_db=68.0, contour_m=24.0, height_m=3.5,
    pd_pc=120.0, pd_limit_pc=100.0,
)
# [end: tests]

DGA = dict(   # ppm before and after the heat run (A-463)
    before=dict(H2=4.0, CH4=1.0, C2H6=0.5, C2H4=0.4, C2H2=0.0, CO=20.0, CO2=180.0),
    after=dict(H2=9.0, CH4=3.0, C2H6=1.2, C2H4=1.6, C2H2=0.8, CO=42.0, CO2=260.0),
    hours=12.0)
