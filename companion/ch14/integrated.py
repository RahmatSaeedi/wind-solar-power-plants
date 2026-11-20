"""Chapter 14 - three integrated Plant P examples: the site on one page
(introductory), the preliminary layout package of wind, PV, substation,
roads, cables and export route (intermediate), and the constraint
register that carries every screening result to its owner and its
verification (integrated).

Run from the project root:   python -m companion.ch14.integrated
Writes companion/ch14/expected/i_*.txt.
Synthetic site A-259 .. A-263; D-015, D-017, D-018.
"""
from __future__ import annotations

import numpy as np

from companion.ch14 import examples_a as ea, examples_e as ee, lab_d, sources as src
from companion.ch14.common import emit
from plantp import siting as st

G = src.GRID


def one_page() -> None:
    ok_wt, _ = ea.buildable("wt")
    ok_pv, _ = ea.buildable("pv")
    z = src.terrain()
    lines = ["Plant P site on one page (screening, synthetic A-259):",
             "  window 13 x 7 km; project land 6,300 ha west of x = 9 km",
             f"  ground {z.min():.0f} .. {z.max():.0f} m; ridge in the west, wadi in the south",
             f"  buildable for turbines {ok_wt.sum() * G.cell ** 2 / 1e4:,.0f} ha, for PV"
             f" {ok_pv.sum() * G.cell ** 2 / 1e4:,.0f} ha (teaching setbacks A-260)",
             "  people: village of 25 houses (NE), 3 houses, 1 seasonal camp",
             "  users: state rangeland, 2 farms, herders (customary, Apr-Oct),",
             "    village lands, 8 farm strips on the export side",
             "  sensitive: raptor nest (ridge), wetland (wadi), spring, cemetery,",
             "    caravanserai ruin (export side)",
             "  grid: 132 kV substation 6.2 km east of the site substation",
             "  water: the spring has no spare water in Jun-Sep",
             "  first reading: wind on the plain, PV in the east, a corridor",
             "  north or south of the farm strips; the ridge only after a bird",
             "  survey"]
    emit("i_onepage", lines)


def package() -> None:
    m = lab_d.metrics("W2b plain, adjusted")
    c = ee.cost_raster()
    p, _ = st.least_cost_path(c, G.index(*src.SITE_SUB), G.index(*src.GRID_SUB), G.cell)
    route = ee.route_stats(p)
    pv_ha = st.polygon_area(src.PV_BLOCK) / 1e4
    lines = ["preliminary layout package (D-018, to be frozen only after surveys):",
             "  wind: W2b, 12 x WT-5.0-150, hub 100 m, two rows across 285 deg",
             f"    long-term {m['energy']:.1f} GWh a year, wake loss"
             f" {100 * m['loss']:.1f} % (other losses: ch 15)",
             f"  PV: block of {pv_ha:.0f} ha east of the farm, 60 MWp at GCR 0.40"
             " (88 ha used)",
             "  site substation 33/132 kV at (6.5, 3.5) km, between wind and PV",
             f"  collector strings {m['strings']:.1f} km (wind), roads {m['road']:.1f} km,"
             f" pads {m['earth']:,.0f} m3",
             f"  export: least-cost route {route['km']:.2f} km inside a 5 % corridor"
             " of 784 ha",
             f"  footprint {m['fp']:.1f} ha (wind) + {pv_ha:.0f} ha (PV); customary"
             f" grazing {m['grazing']:.1f} ha",
             f"  dwellings: highest noise {m['noise'][1]:.1f} dB(A), flicker"
             f" {m['flicker'][0]:.0f} h/yr worst case",
             "  georeferenced in the local grid (x east, y north, metres from",
             "  the window's south-west corner); a surveyed projected system",
             "  replaces it before design (chapter 29)"]
    emit("i_package", lines)


REGISTER = [
    ("C-01", "raptor nest on the ridge", "ecology layer (desk)", "open", "ecologist",
     "one-year bird survey (U-051)", "W1"),
    ("C-02", "herders' seasonal camp B", "screening survey", "open", "social lead",
     "walk-over with herders; noise and flicker study", "W2, W2b"),
    ("C-03", "customary grazing area", "screening survey", "open", "social lead",
     "participatory mapping; agreement on access (U-052)", "W2b roads"),
    ("C-04", "spring and channel", "screening survey", "open", "water lead",
     "flow records; no plant use; source and permit (U-053)", "all"),
    ("C-05", "wadi floods", "terrain model", "open", "civil lead",
     "hydrology study; culvert design (U-050)", "roads, cables"),
    ("C-06", "setbacks to dwellings, roads, lines", "teaching values A-260", "open",
     "permitting lead", "authority's rules (ch 55-57)", "all"),
    ("C-07", "terrain and soils", "50 m terrain model", "open", "civil lead",
     "topographic and geotechnical survey (U-050)", "pads, roads"),
    ("C-08", "caravanserai ruin", "heritage layer (desk)", "open", "heritage specialist",
     "walk-over; chance-find procedure", "export route"),
    ("C-09", "farm strips on the export side", "screening survey", "open", "land lead",
     "owner list; easements (U-052)", "export route"),
    ("C-10", "grid substation bay and route", "grid operator (to ask)", "open",
     "grid lead", "connection offer; route consent (U-054)", "export"),
    ("C-11", "aviation and radar", "none yet", "open", "permitting lead",
     "obstacle evaluation request (U-055)", "all turbines"),
    ("C-12", "water for construction and cleaning", "demand estimate A-261", "open",
     "water lead", "well licence or supply contract", "PV, roads"),
]


def register() -> None:
    lines = ["constraint register PLP-GEN-REG-0003, rev A (screening):",
             "  id    constraint                          source"]
    for cid, what, source, status, owner, verify, affects in REGISTER:
        lines.append(f"  {cid}  {what:36s} {source}")
    lines += ["  every row also has: status (all open), owner, the verification",
              "  that closes it and the layouts it affects; rows close with",
              "  evidence, never with a date alone"]
    emit("i_register", lines)


if __name__ == "__main__":
    one_page()
    package()
    register()
