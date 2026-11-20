"""Chapter 6 lab: DC wiring loss budget of one PV block, from the hourly data.

Run from the project root:   python -m companion.ch06.lab_budget
Every input is a named constant at the top, with its status, so a reviewer
can change one assumption and re-run.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plantp import datapack, dc  # noqa: E402

# [start: inputs]
STRINGS = 24               # strings per combiner box        (assumed, A-014)
MODULES = 26               # modules per string              (assumed, A-015)
STRING_ONE_WAY_M = 70.0    # mean string cable, one way      (assumed, A-022)
STRING_MM2 = 4.0           # string cable, copper            (assumed)
FEEDER_ONE_WAY_M = 180.0   # combiner to inverter, one way   (assumed, A-018)
FEEDER_MM2 = 240.0         # feeder, aluminium               (assumed)
CONDUCTOR_C = 50.0         # conductor temperature, all year (assumed, A-019)
PR_DC = 0.85               # DC performance factor           (assumed)
# [end: inputs]

# [start: model]
module = dc.PVM_550
v_mp = MODULES * module.v_mp
hourly = datapack.load_hourly()
g = hourly["ghi_wm2"].to_numpy()

# string current in each hour, proportional to irradiance
i_string = module.i_mp * PR_DC * g / 1000.0
i_feeder = STRINGS * i_string

r_string = dc.feeder(1.0, STRING_ONE_WAY_M, STRING_MM2,
                     "copper", CONDUCTOR_C).loop_resistance_ohm
r_feeder = dc.feeder(1.0, FEEDER_ONE_WAY_M, FEEDER_MM2,
                     "aluminium", CONDUCTOR_C).loop_resistance_ohm

e_dc = (v_mp * i_feeder).sum() / 1000.0                  # kWh in one year
e_string = STRINGS * (r_string * i_string**2).sum() / 1000.0
e_feeder = (r_feeder * i_feeder**2).sum() / 1000.0
# [end: model]

# [start: report]
print(datapack.cite("S0", "1.0.0"))
print(f"DC energy of one combiner box: {e_dc:10,.0f} kWh/yr")
print(f"string cables (x{STRINGS}):       {e_string:10,.0f} kWh/yr"
      f"  {100 * e_string / e_dc:5.2f} %")
print(f"feeder:                       {e_feeder:10,.0f} kWh/yr"
      f"  {100 * e_feeder / e_dc:5.2f} %")
print(f"total DC wiring:              {e_string + e_feeder:10,.0f} kWh/yr"
      f"  {100 * (e_string + e_feeder) / e_dc:5.2f} %")
# [end: report]
