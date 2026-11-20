"""Chapter 53, round s: curtailment growing over the years, soiling and
ageing told apart, an inverter upgrade's efficiency and repairs, battery
augmentation or retirement, the permits of a repowering, hazardous
inventories, scrap prices and the provision, equivalent annual cost for
options of different lives, inspecting gearboxes before choosing,
grievances from decommissioning traffic, grazing land returned,
warranties at a change of owner, records past retention, the decision
boundary against the attribution boundary, and recycling credits.

Run from the project root:   python -m companion.ch53.examples_s
Writes companion/ch53/expected/s_*.txt. Teaching values (A-538 to A-545).
"""
from __future__ import annotations

import numpy as np

from companion.ch53 import sources as src
from companion.ch53.common import emit
from plantp import lifecycle as lc


# ------------------------------------------------ 1. curtailment over the years
def curtailment() -> dict:
    yrs = np.arange(1, 19)
    mwh = np.array([230, 260, 300, 380, 450, 560, 640, 790, 900, 1050, 1210, 1380,
                    1500, 1680, 1820, 1950, 2080, 2200], float)
    b, h = lc.trend(yrs[-8:], mwh[-8:])
    y25 = mwh[-1] + b * 7
    lines = ["grid curtailment by year (MWh): the region adds wind and solar",
             "  " + " ".join(f"{x:4.0f}" for x in mwh[:9]),
             "  " + " ".join(f"{x:4.0f}" for x in mwh[9:]),
             f"  last eight years: +{b:.0f} +/- {h:.0f} MWh a year; year 25 by the line: "
             f"{y25:,.0f} MWh",
             "  curtailment grows as the grid fills: a repowering adds most",
             "  energy in windy hours, when curtailment is also most likely -",
             "  its gain must be valued after curtailment, not before"]
    emit("s_curtail", lines)
    return dict(slope=b, y25=y25)


# ------------------------------------------------ 2. soiling and ageing told apart
def soiling_vs_ageing() -> dict:
    before = np.array([76.1, 75.4, 75.0, 74.6])      # PR % just before washes, year 18
    after = np.array([76.8, 76.7, 76.6, 76.7])       # just after
    soil = float(np.mean(after - before))
    lines = ["PR just before and just after the four washes of year 18 (%)",
             "  before " + " ".join(f"{x:.1f}" for x in before),
             "  after  " + " ".join(f"{x:.1f}" for x in after),
             f"  soiling costs {soil:.1f} points on average before a wash; the after-wash",
             f"  level {after.mean():.1f} % is the aged plant - the 76.6 % of lesson A",
             "  is an after-wash series, so the 0.37 %/yr is ageing, not dirt"]
    emit("s_soilage", lines)
    return dict(soil=soil, after=float(after.mean()))


# ------------------------------------------------ 3. inverter upgrade
def inverter_upgrade(pv_mwh: float = 100_000.0) -> dict:
    inv = src.INVERTER
    gain = pv_mwh * (inv["eta_new"] / inv["eta_old"] - 1)
    repairs = inv["failures_yr"][-1] * inv["units"] * inv["repair_k"]
    down = inv["failures_yr"][-1] * inv["units"] * inv["mttr_h"] * 5.0 * 0.25   # MWh, PV hours
    yearly = gain * src.PRICE / 1000 + repairs + down * src.PRICE / 1000
    capex = inv["units"] * inv["replace_k"]
    af = (1 - (1 + src.RATE) ** -7) / src.RATE
    npv7 = yearly * af - capex
    lines = [f"replacing the 10 inverters: efficiency {inv['eta_old']} -> {inv['eta_new']}",
             f"  energy gained {gain:,.0f} MWh a year; repairs avoided {repairs:,.0f} k u a year;",
             f"  downtime avoided {down:,.0f} MWh a year",
             f"  value about {yearly:,.0f} k u a year against {capex:,.0f} k u: payback "
             f"{capex / yearly:.1f} years",
             f"  over the 7 years left at {src.RATE:.1%}: NPV {npv7:+,.0f} k u - it pays inside the",
             "  plant's life once the avoided repairs and downtime are counted;",
             "  lesson A's screen counted energy only and called it negative",
             "  - and support ends at year 21 whatever is decided (lesson B)"]
    emit("s_invupg", lines)
    return dict(gain=gain, yearly=yearly, payback=capex / yearly, npv7=npv7,
                repairs=repairs, lost=gain + down)


# ------------------------------------------------ 4. battery: augment or retire
def battery() -> dict:
    soh = 0.71                                  # at year 18 (ch 19 fade path, teaching)
    need = 0.80                                 # energy the service contract needs
    aug_mwh = (need - soh) * 40.0
    cost_aug = aug_mwh * 160.0                  # k u per MWh installed (teaching)
    value = 9.0 * 40.0 * need * 300 * 10.0 / 1000   # shifting spread x cycles (teaching)
    lines = [f"battery at year 18: state of health {soh:.0%} of 40 MWh; the service needs "
             f"{need:.0%}",
             f"  augmentation {aug_mwh:.1f} MWh at 160 k u/MWh = {cost_aug:,.0f} k u",
             f"  value of keeping the battery in service: about {value:,.0f} k u a year",
             "  (teaching spread and cycles)",
             f"  augmentation pays back in {cost_aug / value:.1f} years - inside the 7 left; but",
             "  new cells beside 18-year-old ones age differently (ch 19, ch 45):",
             "  the augmentation is a separate string with its own BMS limits"]
    emit("s_battery", lines)
    return dict(aug=aug_mwh, cost=cost_aug, value=value)


# ------------------------------------------------ 5. permits of a repowering
def permits() -> dict:
    items = [("environmental permit amendment", "new turbine height and noise", 14),
             ("aviation clearance", "tip height 205 m", 6),
             ("grid connection amendment", "new capability and studies", 10),
             ("land lease extension", "beyond year 25", 8),
             ("construction permit", "foundations adapted", 5),
             ("bird and bat survey update", "two seasons", 18)]
    crit = max(items, key=lambda r: r[2])
    lines = ["repowering approvals (teaching; real ones from local verification, ch 54-58)",
             "  approval                          subject                       months"]
    lines += [f"  {a:32s} {s:29s} {m:4d}" for a, s, m in items]
    lines += [f"  the longest: {crit[0]} ({crit[2]} months) - two seasons",
              "  of birds cannot be hurried, so the repowering clock starts",
              "  with the survey (ch 33)"]
    emit("s_permits", lines)
    return dict(crit=crit[0], months=crit[2])


# ------------------------------------------------ 6. hazardous inventory
def hazardous() -> dict:
    inv = {"SF6 in 33 kV switchgear (kg)": 12 * 5.5, "SF6 in 132 kV breakers (kg)": 3 * 9.0,
           "transformer oil (t)": 85.0, "battery modules (t)": 240.0,
           "lead-acid UPS and DC batteries (t)": 4.2, "refrigerants in HVAC (kg)": 8 * 12.0}
    lines = ["hazardous inventory at closure (from the asset register)"]
    lines += [f"  {k:38s} {v:7.1f}" for k, v in inv.items()]
    sf6 = inv["SF6 in 33 kV switchgear (kg)"] + inv["SF6 in 132 kV breakers (kg)"]
    lines += [f"  SF6 {sf6:.0f} kg: about {sf6 * 24_000 / 1000:,.0f} t CO2e if released (GWP ~24,000,",
              "  approximate, ch 24) - recovered by certified handlers, with",
              "  the recovery record as closure evidence; the inventory comes",
              "  from the register, so its completeness is lesson H's question"]
    emit("s_hazard", lines)
    return dict(sf6=sf6)


# ------------------------------------------------ 7. scrap prices and the provision
def scrap() -> dict:
    steel_t = 4_932 + 2_900 + 1_980 * 0.8
    cu_al_t = 510.0
    out = {}
    for case, ps, pc in (("low", 0.08, 0.6), ("central", 0.12, 1.0), ("high", 0.16, 1.4)):
        out[case] = steel_t * ps + cu_al_t * pc
    lines = ["salvage value of steel and cable metal at closure (k u, teaching prices)"]
    lines += [f"  {k:8s} {v:7,.0f}" for k, v in out.items()]
    net = src.DECOM_COST - src.SALVAGE
    lines += [f"  the salvage swings by {out['high'] - out['low']:,.0f} k u between the cases -",
              f"  {(out['high'] - out['low']) / net:.0%} of the net decommissioning cost of {net:,.0f} (ch 21): the",
              "  provision is sized on the low case and reviewed, never on",
              "  the high one"]
    emit("s_scrap", lines)
    return out


# ------------------------------------------------ 8. equivalent annual cost
def eac_options() -> dict:
    up = inverter_upgrade()
    p_k = src.PRICE / 1000                          # k u per MWh
    keep = lc.eac(lc.option_pv(0, up["repairs"], up["lost"], p_k, 7, src.RATE), 7, src.RATE)
    new = lc.eac(lc.option_pv(4_200.0, 40.0, 30.0, p_k, 15, src.RATE), 15, src.RATE)
    lines = ["inverters: keep repairing (7 years left) or new units (15-year life)",
             f"  keep: {up['repairs']:,.0f} k u repairs and {up['lost']:,.0f} MWh lost a year -> EAC "
             f"{keep:,.0f} k u",
             f"  new: 4,200 k u, then 40 k u and 30 MWh a year over 15 years -> EAC {new:,.0f} k u",
             "  equivalent annual cost compares options of different lives on",
             f"  one footing: new units cost {keep - new:,.0f} k u a year less; the 15 years",
             "  count fully only if the plant (or a buyer) uses them - here the",
             "  7-year NPV of the previous lesson agrees, so both views point",
             "  the same way"]
    emit("s_eac", lines)
    return dict(keep=keep, new=new)


# ------------------------------------------------ 9. inspect the gearboxes first
def inspect_first(p_bad: float = 0.3, cost_insp: float = 15.0) -> dict:
    # a borescope finds a gearbox near failure (bad) with certainty (teaching)
    fail_cost = 380.0 + 900 * 1.84 * src.PRICE / 1000       # repair + downtime at failure
    planned = 380.0 + 700 * 0.94 * src.PRICE / 1000         # planned repair in June
    blind = p_bad * fail_cost
    informed = cost_insp + p_bad * planned
    lines = [f"each gearbox: {p_bad:.0%} chance of failing within a year (lesson D's model)",
             f"  failure in service costs {fail_cost:,.0f} k u (repair + downtime);",
             f"  a planned repair in June {planned:,.0f} k u",
             f"  wait blind: {blind:,.0f} k u expected; borescope ({cost_insp:.0f} k u) and plan",
             f"  the bad ones: {informed:,.0f} k u",
             f"  the inspection saves {blind - informed:,.0f} k u a gearbox a year - it turns",
             "  lesson D's 'repair at failure' into 'repair before failure'",
             "  where the evidence says so (ch 52 P-F)"]
    emit("s_inspect", lines)
    return dict(blind=blind, informed=informed)


# ------------------------------------------------ 10. grievances from traffic
def grievances(loads: float = 787.0, rate: float = 6.0) -> dict:
    exp = loads / 1000 * rate * 2
    lines = [f"construction had {rate:.0f} traffic grievances per 1,000 loads past the village",
             f"  (ch 49, teaching); {loads:,.0f} loads x 2 passes: about {exp:.0f} grievances expected",
             "  the mechanism runs to the end (lesson G) with its times;",
             "  the expected number staffs it, and a falling rate per load",
             "  shows the traffic plan works"]
    emit("s_griev", lines)
    return dict(exp=exp)


# ------------------------------------------------ 11. grazing land returned
def grazing() -> dict:
    ha = 119.0 + 18.7                                  # PV block and roads (ch 33)
    income = ha / 780.0 * 600 * 0.12                   # share of grazing x animals x income
    lines = [f"land returned to grazing: {ha:.0f} ha (PV block and roads, ch 33)",
             f"  about {ha / 780:.0%} of the herders' 780 ha - worth about {income:.1f} k u a year",
             "  to them once the cover is back (lesson C: plot 2 is not)",
             "  the return is accepted by the landholder and the herders",
             "  on the monitoring record, not on a date"]
    emit("s_grazing", lines)
    return dict(ha=ha, income=income)


# ------------------------------------------------ 12. warranties at a change of owner
def warranties(year: int = 18) -> dict:
    w = {"new gearbox T05 (repaired year 16)": 18 + 2, "inverter IGBT stacks": 0,
         "BESS augmentation string": 0, "repowered blades (if done)": 0,
         "PV modules (power warranty 25 yr)": 25, "transformer T1 rewind (year 15)": 15 + 5}
    live = {k: v - year for k, v in w.items() if v > year}
    lines = [f"warranties alive at a sale of the plant in year {year} (end year)"]
    lines += [f"  {k:36s} {'ends ' + str(v) if v else '-':>10s}" for k, v in w.items()]
    lines += [f"  {len(live)} pass to the buyer only if transferable and with their",
              "  records (lesson H); the module power warranty is the largest",
              "  and needs the flash and PR history to be claimed"]
    emit("s_warranty", lines)
    return dict(live=len(live))


# ------------------------------------------------ 13. records past retention
def disposal() -> dict:
    sets = {"SCADA raw data, years 1-15": (3, 15), "shift logs, years 1-12": (7, 12),
            "visitor and gate logs": (2, 18), "CCTV": (0.1, 18)}   # (keep years, age)
    out = [k for k, (keep, age) in sets.items() if age > keep]
    lines = ["records past their (teaching) retention period at year 18"]
    lines += [f"  {k:28s} keep {keep:>4} yr, oldest {age} yr" for k, (keep, age) in sets.items()]
    lines += [f"  {len(out)} sets due for disposal; personal data (gate logs, CCTV)",
              "  must not be kept longer than the obligation allows - disposal",
              "  is a recorded act with a certificate, not a deletion"]
    emit("s_dispose", lines)
    return dict(n=len(out))


# ------------------------------------------------ 14. decision boundary vs attribution
def boundaries() -> dict:
    built = 260_000.0                          # t CO2e embodied at construction (ch 33 order)
    energy_25 = 25 * 290_000.0                 # MWh over the life
    energy_30 = 30 * 285_000.0
    attr_25 = built * 1e6 / (energy_25 * 1e3)
    attr_30 = built * 1e6 / (energy_30 * 1e3)
    lines = [f"construction footprint about {built:,.0f} t CO2e (teaching, ch 33 order)",
             f"  attributed over 25 years: {attr_25:.1f} g/kWh; over 30 years: {attr_30:.1f} g/kWh",
             "  that is the attribution view (the plant's whole life); the",
             "  decision view of lesson I counts only what the decision adds",
             "  - the past is sunk and the same for every option, so mixing",
             "  the two makes a life extension look cleaner than it is"]
    emit("s_bound", lines)
    return dict(a25=attr_25, a30=attr_30)


# ------------------------------------------------ 15. recycling credits
def credits(steel_t: float = 9_416.0) -> dict:
    cutoff = 0.0
    avoided = -steel_t * 1.5                         # t CO2e avoided virgin steel (teaching)
    lines = [f"recycling {steel_t:,.0f} t of steel at closure, two accounting rules",
             f"  cut-off: the credit goes to the next product: {cutoff:,.0f} t CO2e here",
             f"  avoided burden: credit {avoided:,.0f} t CO2e to this plant",
             "  the same steel, two numbers: the rule is stated, kept the same",
             "  for every option, and the credit is shown apart - never",
             "  netted silently (ch 33, ISO 14044 allocation)"]
    emit("s_credit", lines)
    return dict(avoided=avoided)


if __name__ == "__main__":
    curtailment()
    soiling_vs_ageing()
    inverter_upgrade()
    battery()
    permits()
    hazardous()
    scrap()
    eac_options()
    inspect_first()
    grievances()
    grazing()
    warranties()
    disposal()
    boundaries()
    credits()
