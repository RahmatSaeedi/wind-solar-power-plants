"""Chapter 30 - structures of Plant P (teaching values A-356 to A-362).

The WT-5.0-150 turbine of chapter 11 (masses A-214, tower A-218/A-235,
flange A-236), the ground of chapter 29 (A-349), the PV tables of
chapter 10 (D-013), the 132 kV line of chapters 24, 28 and 29, and the
main transformer of chapter 25. Loads, factors and limits here are
teaching values for a fictional site, never a design: real values come
from the turbine maker's load document, the project's codes and the
type certificate.
"""
from __future__ import annotations

import math

from companion.ch30 import common  # noqa: F401  (puts plantp on the path)
from companion.ch11 import examples_b as b11
from companion.ch11 import rotor

HUB = rotor.HUB
TOP_T = (b11.MASS["blades (3 x 22 t)"] + b11.MASS["hub with pitch system"]
         + b11.MASS["nacelle with drivetrain"])                 # 271 t
TOWER_T = b11.MASS["tower (100 m steel)"]                        # 340 t
F1_FIXED = 0.215                                                 # Hz, ch 11 b_campbell
ONE_P_MAX = 0.192                                                # Hz, 11.5 rpm

# [start: loads]
LOADS = {   # tower-base loads, characteristic, teaching (A-356)
    "production (peak)": dict(m_mnm=92.3, h_mn=0.92, kind="normal"),
    "extreme (parked, 50-yr gust)": dict(m_mnm=184.6, h_mn=1.60, kind="extreme"),
    "fatigue: DEL at 1e7 cycles": dict(m_mnm=30.0, h_mn=0.0, kind="fatigue"),
}
# [end: loads]

FOUNDATION = dict(r=10.0, depth=3.5, concrete_m3=620.0, backfill_m3=800.0,
                  gamma_c=24.0, gamma_b=18.0)                    # circular gravity base (A-357)

SOILS = {   # operating-strain shear modulus of the founding layer, teaching (A-358, ch 29)
    "dense sand and gravel (T01-T06, T08-T12)": dict(g_mpa=80.0, nu=0.30, q_ult=8400.0),
    "medium sand at founding level (T07)": dict(g_mpa=25.0, nu=0.35, q_ult=5360.0),
    "T07 with water at 0.5 m": dict(g_mpa=20.0, nu=0.35, q_ult=2700.0),
}

MARGIN_1P = 0.10          # teaching OEM requirement: f1 at least 10 % above 1P max (A-359)

TOWER = [  # section, D base, D top, t mm, length (ch 11 c_tower, A-218)
    (1, 4.50, 4.12, 46, 25.0), (2, 4.12, 3.75, 40, 25.0),
    (3, 3.75, 3.38, 32, 25.0), (4, 3.38, 3.00, 26, 25.0)]

STEEL = dict(e=210e9, fy=355e6, rho=7850.0, alpha=12e-6)

PV_TABLE = dict(rows=2, modules_per_row=26, module_l=2.278, module_w=1.134, tilt_deg=25.0,
                frames=6, posts_per_frame=2, module_kn=0.27, steel_kn=15.0)   # D-013, A-360

SITE = dict(rho=1.09, gust50_10m=41.1, ag=0.25, tc=0.6, snow_kpa=0.4)      # A-361


def tube_w(d: float, t: float) -> float:
    """Elastic section modulus of a thin tube (m3)."""
    return math.pi / 32 * (d ** 4 - (d - 2 * t) ** 4) / d
