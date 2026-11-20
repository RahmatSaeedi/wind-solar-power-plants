"""Chapter 19 - battery data for Plant P (teaching values, A-290 to
A-293): the LFP cell of the S1 battery and an NMC cell for comparison,
the build-up from cell to system (matching the chapter 18 breakdown),
scenario S1 from the data pack, container thermal data, fade and
warranty parameters, and the chapter 15 teaching prices.

Nothing here is a product's data sheet or a recommended design; real
values come from the maker with test evidence (chapters 39 and 44).
"""
from __future__ import annotations

from companion.ch19 import common  # noqa: F401  (puts plantp on the path)
from plantp import storage as st

# [start: cells]
LFP = st.Cell(q_ah=314.0, r0=0.00025, r1=0.00015, c1=200000.0,
              chem="LFP", v_min=2.5, v_max=3.6)           # A-290
NMC = st.Cell(q_ah=100.0, r0=0.0006, r1=0.0004, c1=75000.0,
              chem="NMC", v_min=3.0, v_max=4.2)           # comparison
V_NOM = {"LFP": 3.2, "NMC": 3.7}
# [end: cells]

# [start: build]
BUILD = {"s_module": 52, "m_rack": 8, "r_container": 12,
         "containers": 8, "pcs": 4, "pcs_mw": 5.0}        # A-290
# [end: build]

S1 = {"power_mw": 20.0, "energy_mwh": 40.0, "soc_lo": 0.10,
      "soc_hi": 0.90, "rt_ac": 0.86, "fade_per_year": 0.02}  # data pack

THERMAL = {"ua_kw_k": 1.5, "c_kwh_k": 6.0, "hvac_kw": 100.0,
           "solar_kw_peak": 8.0, "aux_kw": 3.0, "setpoint": 25.0,
           "r_growth_eol": 1.8}                           # A-291

FADE = {"k25": 0.02, "ea_ev": 0.5, "n100": 4000.0, "k": 1.3,
        "loss_at_life": 0.2}                              # A-292

WARRANTY = {"throughput": 14600.0, "efc": 365.0, "soc_mean": 0.70,
            "t_max": 45.0}                                # A-293

PCS_ETA = 0.98            # one-way PCS efficiency (A-286)
MV_ETA = 0.995            # MV transformer and cables, one way (teaching)
AUX_SHARE = 0.01          # HVAC and BMS as a share of discharged energy


def prices():
    """Chapter 15 teaching prices (A-273): low at midday, high 18-22 h."""
    from companion.ch15 import examples_n
    return examples_n.prices()
