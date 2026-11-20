"""Chapter 18, further architecture lessons: battery size against what it
recaptures under two export limits, the exact (section by section)
collector loss against the screening bound, feeders for the PV blocks,
export voltage 132 against 66 kV, the reactive-power budget at the POC,
the balance-of-plant availability budget, and the interfaces that
cross contract packages.

Run from the project root:   python -m companion.ch18.examples_h
Writes companion/ch18/expected/h_*.txt and diagrams/data/ch18-*.csv.
Teaching values A-286 (technical), A-287 (costs), A-288 (reliability).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch14 import lab_d as l14, sources as s14
from companion.ch15 import sources as s15
from companion.ch18 import examples_g as eg, sources as src
from companion.ch18.common import csv, emit
from plantp import architecture as ar, siting as st
from plantp.yieldrisk import annuity

C, R = src.COST, src.REL
RT = 0.98 * 0.90 * 0.98                      # AC-coupled round trip (A-286)


# [start: recapture]
def recapture(p_mw: float, limit: float) -> float:
    """MWh a year an AC-coupled battery of p_mw and 2 h returns from
    energy the export limit would curtail (greedy: charge on surplus,
    discharge into the next headroom)."""
    poc = s15.plant_year()["poc"]
    e_max, one = 2.0 * p_mw, math.sqrt(RT)
    soc = back = 0.0
    for p in poc:
        if p > limit:                                    # surplus: charge
            ch = min(p - limit, p_mw, (e_max - soc) / one)
            soc += ch * one
        elif soc > 0:                                    # headroom: discharge
            d = min(limit - p, p_mw, soc * one)
            soc -= d / one
            back += d
    return back
# [end: recapture]


def battery_sweep() -> None:
    lines = ["battery size against energy recaptured from the export limit",
             "  (AC-coupled, 2 h, greedy; teaching costs A-287):",
             "  limit  battery MW  recaptured MWh  value k u/yr  cost k u/yr"]
    rows = []
    for lim in (80.0, 100.0):
        for mw in (0, 5, 10, 20, 40):
            back = recapture(float(mw), lim) if mw else 0.0
            capex = C["bess_per_mw"] * mw + C["bess_per_mwh"] * 2 * mw
            yearly = capex / annuity(C["rate"], C["years"]) + C["opex_share"] * capex
            lines.append(f"  {lim:5.0f}  {mw:9d}   {back:12,.0f}"
                         f"   {back * C['price'] / 1e3:10.1f}   {yearly:10,.1f}")
            rows.append((int(lim), mw, f"{back / 1e3:.3f}"))
    lines += ["  recapture alone never pays for the battery: at 100 MW there",
              "  is little to recapture, at 80 MW a few GWh; the battery is",
              "  bought for price shifting and services (chapters 19-21) and",
              "  recapture is a by-product"]
    emit("h_battery", lines)
    csv("ch18-battery.csv", "lim,mw,gwh", rows)


def _sections(xy, root, chain):
    pos, out = np.asarray(root, float), []
    for k in chain:
        out.append(float(np.hypot(*(xy[k] - pos))) / 1000)
        pos = xy[k]
    return out


# [start: exact]
def string_loss(km_sections, p_unit, kv, ohm_km, pf=0.95) -> float:
    """Yearly I^2 R loss (MWh) of a radial string: section k carries
    the units at and beyond it."""
    n = len(km_sections)
    loss = 0.0
    for k, km in enumerate(km_sections):
        p = p_unit * (n - k)
        loss += float(ar.loss_mw(p, kv, ohm_km * km, pf).sum())
    return loss
# [end: exact]


def collector_exact() -> None:
    xy = l14.layouts()["W2b plain, adjusted"]
    strings, _ = st.radial_strings(xy, s14.SITE_SUB, 4)
    p_t = s15.plant_year()["w_av"] / 12.0
    lines = ["W2b collector loss, section by section against the bound:",
             "  cable            bound MWh   exact MWh   exact % of wind"]
    w = s15.plant_year()["w_av"].sum()
    from companion.ch18 import examples_f as ef
    for name in ("33 kV 240 mm2", "33 kV 630 mm2"):
        kv, ohm = src.CABLES[name][0], src.CABLES[name][1]
        exact = sum(string_loss(_sections(xy, s14.SITE_SUB, c), p_t, kv, ohm)
                    for c in strings)
        bound = ef.collector_option(name)["loss"]
        lines.append(f"  {name:15s} {bound:10,.0f}  {exact:10,.0f}       {100 * exact / w:5.2f}")
    lines += ["  the far sections carry one to three turbines, so the exact",
              "  loss is well below the bound; the first section from the",
              "  substation carries the whole string and sets the cable size"]
    emit("h_exact", lines)


def pv_feeders() -> None:
    """Ten 5 MW blocks in two rows east of the substation (teaching)."""
    sub = np.asarray(s14.SITE_SUB, float) / 1000
    blocks = [np.array([7.04 + 0.28 * k, y]) for y in (2.94, 2.51) for k in range(5)]
    p_b = s15.plant_year()["pv_av"] / 10.0
    options = {"2 feeders of 5, 240 mm2": ([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], "33 kV 240 mm2"),
               "2 feeders of 5, 630 mm2": ([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]], "33 kV 630 mm2"),
               "3 feeders 4/3/3, 240 mm2": ([[0, 1, 2, 3], [4, 9, 8], [5, 6, 7]], "33 kV 240 mm2")}
    lines = ["PV block feeders at 33 kV (block centres teaching, A-286):",
             "  option                     peak kA  rating  loss MWh  km   cost k u"]
    for name, (feeders, cab) in options.items():
        kv, ohm, mh, amp, cost = src.CABLES[cab]
        loss = km_tot = 0.0
        worst = 0.0
        for f in feeders:
            pos, secs = sub, []
            for b in f:
                secs.append(float(np.hypot(*(blocks[b] - pos))))
                pos = blocks[b]
            km_tot += sum(secs)
            loss += string_loss(secs, p_b, kv, ohm)
            worst = max(worst, float(ar.current_ka(5.0 * len(f), kv, 0.95)))
        ok = "ok" if worst <= amp else "over"
        lines.append(f"  {name:25s}  {worst:6.3f}  {amp:4.2f} {ok:4s} {loss:7,.0f}"
                     f"  {km_tot:4.2f}  {cost * km_tot:7,.0f}")
    lines += ["  two feeders of five blocks exceed the 240 mm2 rating at full",
              "  output: either the larger cable or a third feeder (and a",
              "  third 33 kV bay); the third feeder also shrinks what one",
              "  cable fault takes out (four blocks or fewer, not five)"]
    emit("h_pvfeeders", lines)


def export_voltage() -> None:
    """The same 7.06 km line at 132 kV and at 66 kV (teaching)."""
    p = np.clip(s15.plant_year()["net"], 0, None)
    r_ohm, x_ohm = 0.12 * 7.06, 0.40 * 7.06
    lines = ["export voltage for the 7.06 km line (same conductor, teaching):",
             "  voltage  loss MWh/yr  loss %   voltage rise at 100 MW, pf 1"]
    for kv in (132.0, 66.0):
        loss = float(ar.loss_mw(p, kv, r_ohm).sum())
        rise = 100.0 * r_ohm * 100.0 / kv ** 2
        lines.append(f"  {kv:5.0f}    {loss:9,.0f}   {100 * loss / p.sum():5.2f}       {rise:5.2f} %")
    lines += ["  66 kV loses four times as much and lifts the voltage four",
              "  times as far; it is chosen only when the grid bay is 66 kV,",
              "  and then the grid decides it, not the plant (chapter 17)"]
    emit("h_voltage", lines)


# [start: reactive]
def reactive_budget() -> None:
    """Mvar the plant can give at full output against what the POC asks
    (pf 0.95 lagging at 100 MW) plus what the transformers and line use."""
    need_poc = 100.0 * math.tan(math.acos(0.95))          # 32.9 Mvar
    s = 100.0 / 0.95
    use = {"main transformers (x 12 %, 2 x 63 MVA)": 0.12 * s ** 2 / 126.0,
           "line reactance (2.82 ohm)": (s / 132.0) ** 2 * 0.40 * 7.06,
           "line charging (gives)": -ar.charging_mvar(132.0, 0.009, 7.06),
           "turbine transformers (x 6 %)": 0.06 * (60 / 0.95) ** 2 / 67.2,
           "PV block transformers (x 6 %)": 0.06 * (50 / 0.95) ** 2 / 55.0}
    give = {"wind turbines (0.33 of P at full output)": 0.33 * 60.0,
            "PV inverters (0.30 of P at full output)": 0.30 * 50.0,
            "battery inverters idle (20 MVA)": 20.0}
    lines = ["reactive-power budget at full output (teaching, A-286):",
             f"  asked at the POC (pf 0.95 at 100 MW):  {need_poc:6.1f} Mvar"]
    lines += [f"  used by {k:38s} {v:5.1f}" for k, v in use.items()]
    total_need = need_poc + sum(use.values())
    pad = " " * 20
    lines += [f"  needed at the units{pad}{total_need:6.1f} Mvar"]
    lines += [f"  from {k:41s} {v:5.1f}" for k, v in give.items()]
    total_give = sum(give.values())
    margin = total_give - total_need
    lines += [f"  available          {pad}{total_give:6.1f} Mvar",
              f"  margin             {pad}{margin:6.1f} Mvar",
              "  without the battery inverters the plant is short; with them",
              "  the margin depends on the battery being free to give Mvar;",
              "  a dedicated compensator is the other choice (chapter 27)"]
    emit("h_reactive", lines)
    csv("ch18-reactive.csv", "bar,poc,loss,wind,pv,bess",
        [(1, f"{need_poc:.1f}", f"{sum(use.values()):.1f}", 0, 0, 0),
         (2, 0, 0, *(f"{v:.1f}" for v in give.values()))])
# [end: reactive]


def availability_budget() -> None:
    """Expected unserved energy of the balance of plant (A-288)."""
    p = np.minimum(s15.plant_year()["poc"], 100.0).clip(0, None)
    pv = s15.plant_year()["pv_av"]
    xy = l14.layouts()["W2b plain, adjusted"]
    items = {
        "PV inverters (10 central)": 10 * R["central_fail"] * R["central_mttr_h"] * pv.mean() / 10,
        "collector cables (radial)": 82.0,
        "main transformers (2 x 63 MVA)": 2 * R["trafo_fail"] * R["trafo_repair_h"]
        * np.clip(p - 60.0, 0, None).mean(),
        "export line (single circuit)": 0.006 * 7.06 * 12.0 * p.mean(),
        "33 kV busbar (split, 0.01/yr, 48 h)": 0.01 * 48.0 * 0.5 * p.mean(),
    }
    tot = sum(items.values())
    lines = ["balance-of-plant availability budget (expected values, A-288):",
             "  element                                MWh/yr"]
    lines += [f"  {k:38s} {v:7,.0f}" for k, v in items.items()]
    lines += [f"  total                                  {tot:7,.0f}",
              f"  share of 295.14 GWh: {100 * tot / 295140:.2f} %; electrical availability"
              f" {100 - 100 * tot / 295140:.2f} %",
              "  model 15.1's availabilities (wind 0.981, PV 0.990) already",
              "  hold part of these: the budget checks the assumption, it",
              "  does not add to it"]
    emit("h_availability", lines)


# [start: lots]
LOTS = {
    "single EPC": {"wind": "turbine supplier", "PV": "EPC", "BESS": "EPC",
                   "collector": "EPC", "substation": "EPC", "grid": "operator",
                   "control": "EPC", "water": "EPC", "civil": "EPC"},
    "multi-contract": {"wind": "turbine supplier", "PV": "PV EPC",
                       "BESS": "BESS supplier", "collector": "BOP electrical",
                       "substation": "BOP electrical", "grid": "operator",
                       "control": "integrator", "water": "civil",
                       "civil": "civil"},
}
# [end: lots]


def lots() -> None:
    lines = ["system pairs whose interface crosses a contract boundary:",
             "  packaging        lots  crossing pairs  of 18"]
    for name, lot in LOTS.items():
        cross = [(eg.SYSTEMS[i], eg.SYSTEMS[j]) for (i, j) in eg.LINKS
                 if lot[eg.SYSTEMS[i]] != lot[eg.SYSTEMS[j]]]
        lines.append(f"  {name:15s}  {len(set(lot.values())):4d}  {len(cross):13d}")
    multi = LOTS["multi-contract"]
    cross = sorted(f"{eg.SYSTEMS[i]}-{eg.SYSTEMS[j]}" for (i, j) in eg.LINKS
                   if multi[eg.SYSTEMS[i]] != multi[eg.SYSTEMS[j]])
    lines += ["  multi-contract crossings:"]
    lines += ["    " + ", ".join(cross[k:k + 4]) for k in range(0, len(cross), 4)]
    lines += ["  each crossing is an interface the owner must manage; the",
              "  single EPC contract keeps most of them inside one firm and",
              "  is priced for that risk"]
    emit("h_lots", lines)


if __name__ == "__main__":
    battery_sweep()
    collector_exact()
    pv_feeders()
    export_voltage()
    reactive_budget()
    availability_budget()
    lots()
