"""Chapter 19, last two calculations: what the S1 battery does to the
energy-yield statement of chapter 15 (less energy, more value), and the
SOC estimate over a month when coulomb counting is reset with the OCV
at the ends of each day's cycle.

Run from the project root:   python -m companion.ch19.examples_q
Writes companion/ch19/expected/q_*.txt.
Data pack S1, model 15.1, teaching sensor errors A-294.
"""
from __future__ import annotations

import numpy as np

from companion.ch19 import lab_d, sources as src
from companion.ch19.common import emit
from plantp import storage as st

C = src.LFP


def yield_effect() -> None:
    y = lab_d.year()
    r = y["r"]
    ch, dis = y["ch"].sum(), y["dis"].sum()
    net0 = r["net"].sum()
    pr = src.prices()
    v0 = (pr * r["net"]).sum() / 1000
    v1 = (pr * (r["net"] - y["ch"] + y["dis"])).sum() / 1000
    lines = ["what S1 does to the yield statement (model 15.1, lab D rule):",
             f"  S0 net {net0 / 1000:8.2f} GWh, value {v0:8,.0f} k u (teaching prices)",
             f"  battery charged {ch:,.0f} MWh, discharged {dis:,.0f} MWh",
             f"  S1 net {(net0 - ch + dis) / 1000:8.2f} GWh ({(dis - ch) / 1000:+.2f} GWh),"
             f" value {v1:8,.0f} k u ({v1 - v0:+,.0f})",
             "  the yield statement shows the round-trip loss as a loss line",
             "  (chapter 15) and the value belongs to the price model; the",
             "  auxiliaries of the battery are a second loss line if they",
             "  are taken from the plant"]
    emit("q_yield", lines)


def soc_filter() -> None:
    """A month of one cycle a day; a current offset; reset with the OCV
    (2 mV error) at the bottom of each cycle, where LFP is steep."""
    i_day = np.concatenate([np.full(19, 0.5 * C.q_ah), np.zeros(12),
                            np.full(19, -0.5 * C.q_ah), np.zeros(238)])
    cur = np.tile(i_day, 30)
    dt = 300.0
    true = st.coulomb_count(cur, dt, C.q_ah, 0.9)
    lines = ["SOC over a month of one cycle a day: counting with a sensor",
             "  offset, with and without a daily OCV reset at the bottom of",
             "  the cycle (2 mV error):",
             "  offset A   no reset, 30 days   daily reset: largest   mean"]
    for bias in (0.5, 0.05):
        rng = np.random.default_rng(1994)
        est = np.empty_like(true)
        s = 0.9
        for k, i in enumerate(cur):
            s -= (i + bias) * dt / 3600.0 / C.q_ah
            if k % 288 == 25:                    # at rest after the discharge
                v = float(st.ocv(true[k])) + rng.normal(0, 0.002)
                s = float(st.soc_from_ocv(v))
            est[k] = s
        no_reset = st.coulomb_count(cur, dt, C.q_ah, 0.9, bias_a=bias)
        e1 = 100 * np.abs(est - true)
        e0 = 100 * np.abs(no_reset - true)
        lines.append(f"  {bias:8.2f}   {e0[-1]:15.1f} %   {e1.max():18.2f} %"
                     f"   {e1.mean():5.2f} %")
    lines += ["  the reset holds the error to one day's drift plus the reset",
              "  error; with a good sensor the two together give a few",
              "  tenths of a per cent; the dispatch must visit the steep",
              "  end of the window regularly for the reset to work"]
    emit("q_filter", lines)


if __name__ == "__main__":
    yield_effect()
    soc_filter()
