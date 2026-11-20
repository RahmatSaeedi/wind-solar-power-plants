"""Chapter 26 - teaching data for Plant P's protection, earthing and
lightning (A-331 to A-335), on the network of chapter 23 (fault levels by
the MVA method, 400 A earthing resistors) and the cables of chapter 24.

Settings here are illustrative; real settings come from the approved
network model and the responsible operator's requirements, and are
approved before use.
"""
from __future__ import annotations

from companion.ch26 import common  # noqa: F401  (puts plantp on the path)

# [start: settings]
RELAYS = {   # standard-inverse overcurrent (A-331), derived in examples_b
    "feeder": dict(ct=600, pickup=480.0, tms=0.10),
    "incomer": dict(ct=1600, pickup=1600.0, tms=0.11),
    "T1 HV side": dict(ct=400, pickup=400.0, tms=0.18),
}
EARTH = {    # earth-fault elements on the resistance-earthed 33 kV (A-331)
    "feeder": dict(pickup=40.0, delay=0.5),
    "NER standby": dict(pickup=80.0, delay=1.5),
    "earthing resistor": dict(rating_a=400.0, rating_s=10.0),
}
# [end: settings]

NETWORK = dict(   # from chapter 23 (A-320) and teaching values (A-332)
    ik_33_one=6.4e3, ik_33_both=9.8e3, conv_ka=2.7e3, ik_132=5.2e3,
    z1_33=33 ** 2 / 365.0, z0_et=2.0, r_ner=47.6,
    z_line=7.06 * 0.418, z_next=20 * 0.418)

# wind feeder =WS1: first section 630 mm2, then 240 mm2 (ch 24), 1.1 km
# each; resistances at 90 C, reactance and capacitance per km (ch 24)
SECTION = [dict(r=0.0601, x=0.101, c=0.30)] + [dict(r=0.160, x=0.116, c=0.21)] * 3
KM = 1.1
FEEDER_MVA = 4 * 5.26          # four 5 MW turbines at power factor 0.95
SECTION_MVA = 65 / 0.95        # largest generation of one bus section
E_PH = 33e3 / 3 ** 0.5


def feeder_z(n: int) -> complex:
    """Impedance (ohm) from the 33 kV bus to the end of section n of =WS1
    (one transformer in service)."""
    z = complex(0, NETWORK["z1_33"])
    for s in SECTION[:n]:
        z += complex(s["r"], s["x"]) * KM
    return z


def feeder_c_uf() -> float:
    """Capacitance per phase of the whole =WS1 cable (uF)."""
    return sum(s["c"] for s in SECTION) * KM

GRID = dict(rho=150.0, l_m=100.0, w_m=70.0, conductor_m=2_400.0,   # A-333
            split=0.4)                    # share of fault current to earth

LIGHTNING = dict(ng=2.0, hub=100.0, rotor_r=75.0, turbines=12)    # A-334
