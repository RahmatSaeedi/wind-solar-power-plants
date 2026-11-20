"""Chapter 24 - teaching data for Plant P's cables, line and switchgear
(A-321 to A-325): 33 kV three-core aluminium XLPE collector cables,
installation factors, LV copper cables, a teaching overhead conductor,
switchgear ratings and the circuits of chapter 23.

Values are illustrative of their kind, not a maker's data; real ratings
come from the cable maker's data sheets and the applicable
current-rating standards.
"""
from __future__ import annotations

from companion.ch24 import common  # noqa: F401  (puts plantp on the path)

# [start: mvcables]
MV_CABLES = {   # 33 kV, 3-core Al XLPE (A-321): r20 ohm/km, x ohm/km,
    # C uF/km, rating A (buried, reference conditions), cost k u/km
    240: dict(r20=0.125, x=0.116, c=0.21, i0=410.0, cost=95.0),
    400: dict(r20=0.0778, x=0.108, c=0.25, i0=520.0, cost=125.0),
    630: dict(r20=0.0469, x=0.101, c=0.30, i0=660.0, cost=165.0),
}
K_AL = 94.0          # A s^0.5/mm2, Al conductor, XLPE (adiabatic constant)
K_CU = 143.0         # Cu conductor, XLPE
# [end: mvcables]

# [start: factors]
FACTORS = {   # installation factors against reference conditions (A-322)
    "depth 1.0 m (ref 0.8 m)": 0.97,
    "soil 1.5 K m/W (ref 1.0)": 0.88,
    "ground 30 C (ref 20 C)": 0.93,
    "two circuits 0.4 m apart": 0.85,
}
# [end: factors]

LV_CABLES = {   # 0.6/1 kV Cu XLPE (A-323): r20 ohm/km, rating A in air
    10: (1.83, 75.0), 16: (1.15, 100.0), 25: (0.727, 127.0),
    35: (0.524, 158.0), 50: (0.387, 192.0), 70: (0.268, 246.0),
    95: (0.193, 298.0), 120: (0.153, 346.0), 185: (0.0991, 450.0),
    240: (0.0754, 538.0),
}

LINE = dict(   # teaching 132 kV overhead conductor (A-324)
    name="Al conductor steel reinforced, 300 mm2 class",
    r20=0.10, x=0.40, weight_n_m=11.0, breaking_kn=95.0, rating_a=650.0,
    span_m=300.0, tension_pct=20.0)

SWITCHGEAR = {   # rated values of the teaching gear (A-325)
    "33 kV": dict(ur_kv=36, ir_a=2500, ik_ka=25.0, tk_s=3.0, ip_ka=63.0),
    "132 kV": dict(ur_kv=145, ir_a=2000, ik_ka=31.5, tk_s=3.0, ip_ka=80.0),
    "0.4 kV": dict(ur_kv=0.69, ir_a=400, ik_ka=15.0, tk_s=1.0, ip_ka=30.0),
}
