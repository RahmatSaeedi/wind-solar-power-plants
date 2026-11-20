"""Chapter 18, section F - collector and export architecture: the W2b
collector strings at 33 kV with two cable sizes and at 66 kV (length,
current, losses over the year, voltage drop, cost), and three export
options for the 7.06 km route (losses, cable charging, outage energy,
cost). Teaching cable and line data A-286; selection stays conditional
on grid data, permits, terrain and ownership (U-065..U-068).

Run from the project root:   python -m companion.ch18.examples_f
Writes companion/ch18/expected/f_*.txt.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch14 import lab_d as l14, sources as s14
from companion.ch15 import sources as s15
from companion.ch18 import sources as src
from companion.ch18.common import emit
from plantp import architecture as ar, siting as st


def collector_option(name: str) -> dict:
    """Yearly loss (MWh), worst voltage drop (%), peak current (kA) and
    cable cost (k u) of the W2b strings with one cable option."""
    kv, ohm, mh, amp, cost = src.CABLES[name]
    xy = l14.layouts()["W2b plain, adjusted"]
    strings, total_m = st.radial_strings(xy, s14.SITE_SUB, 4)
    p_t = s15.plant_year()["w_av"] / 12.0              # MW per turbine, hourly
    loss = drop = 0.0
    for s in strings:
        km = _string_length(xy, s14.SITE_SUB, s) / 1000    # to the far end
        p_s = p_t * len(s)
        r_ohm = ohm * km               # whole string current, whole length
        x_ohm = 2 * math.pi * 50 * mh * 1e-3 * km
        loss += float(ar.loss_mw(p_s, kv, r_ohm, 0.95).sum())
        drop = max(drop, float(ar.drop_pct(p_s.max(), kv, r_ohm, x_ohm, 0.95)))
    peak = float(ar.current_ka(4 * 5.0, kv, 0.95))
    return {"loss": loss, "drop": drop, "peak_ka": peak, "ok": peak <= amp,
            "cost": cost * total_m / 1000, "km": total_m / 1000,
            "strings": len(strings)}


def collector() -> None:
    """Four turbines per string; each string's current is the sum of its
    turbines' output (wind at MV / 12 per turbine, hourly)."""
    w = s15.plant_year()["w_av"].sum()
    first = collector_option(next(iter(src.CABLES)))
    lines = [f"W2b collector: {first['strings']} radial strings of 4 turbines,"
             f" {first['km']:.2f} km of cable route",
             "  option            peak kA   loss MWh/yr   loss %   drop % (peak)"
             "   cost k u"]
    for name in src.CABLES:
        c = collector_option(name)
        ok = "ok" if c["ok"] else "over"
        lines.append(f"  {name:16s}  {c['peak_ka']:6.3f} {ok:4s} {c['loss']:9,.0f}"
                     f"   {100 * c['loss'] / w:5.2f}      {c['drop']:5.2f}"
                     f"        {c['cost']:7,.0f}")
    lines += ["  the whole string current through the whole length overstates",
              "  the loss (the far sections carry less): a screening bound;",
              "  66 kV cuts losses four times for the same section but costs",
              "  more in cable and switchgear; the larger 33 kV section cuts",
              "  them by 60 %; whether either pays is lab E's question (at the",
              "  teaching costs the 240 mm2 cable stays)"]
    emit("f_collector", lines)


def _string_length(xy, root, idx) -> float:
    pos = np.asarray(root, float)
    total = 0.0
    for k in idx:
        total += float(np.hypot(*(xy[k] - pos)))
        pos = xy[k]
    return total


# [start: export]
def export_option(name: str, km: float = 7.06) -> dict:
    """Yearly loss and expected unserved energy (MWh), charging (Mvar)
    and cost (M u) of one export option on the 132 kV route."""
    p = np.clip(s15.plant_year()["net"], 0, None)
    d = src.EXPORT[name]
    n = d["circuits"]
    r_ohm = d["r"] * km / n              # parallel circuits share current
    return {"loss": float(ar.loss_mw(p, 132.0, r_ohm).sum()),
            "q": ar.charging_mvar(132.0, d["c_uf"], km) * n,
            "out": ar.unserved_mwh(p, d["fail_per_km"] * km,
                                   d["repair_h"], n, 100.0),
            "cost": d["cost_per_km"] * km / 1000}
# [end: export]


def export() -> None:
    lines = ["export options for the 7.06 km route at 132 kV (A-286):",
             "  option                            loss  charging    outage    cost",
             "                                  MWh/yr      Mvar    MWh/yr     M u"]
    for name in src.EXPORT:
        e = export_option(name)
        lines.append(f"  {name:29s} {e['loss']:9,.0f} {e['q']:9.2f}"
                     f" {e['out']:9,.0f} {e['cost']:7.2f}")
    lines += ["  the double circuit halves losses and carries the plant through",
              "  a single fault; the cable loses little, but its repairs are",
              "  long and it produces reactive power to manage; the route,",
              "  permits and owner (chapter 17) decide before the numbers do"]
    emit("f_export", lines)


if __name__ == "__main__":
    collector()
    export()
