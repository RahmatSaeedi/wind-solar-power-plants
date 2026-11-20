"""Chapter 25 - losses, loading and the design sequence: the two bids
compared with capitalised losses (A and B factors from Plant P's hourly
loading), the hot-spot temperature and the paper's ageing through a
year of Plant P's output and the data pack's air temperature, ONAN and
ONAF, and the design dependencies a reviewer can check.

Run from the project root:   python -m companion.ch25.examples_b
Writes companion/ch25/expected/b_*.txt and diagrams/data/ch25-*.csv.
"""
from __future__ import annotations

import numpy as np

from companion.ch15 import sources as s15
from companion.ch25 import sources as src
from companion.ch25.common import csv, emit
from plantp import datapack
from plantp import transformer as tr


def unit_load() -> np.ndarray:
    """Per-unit load of one main transformer: half the plant's MV
    output (split bus), pf 0.95, against 63 MVA."""
    mv = s15.plant_year()["mv"]                      # MW at MV, whole plant
    return mv / 2 / 0.95 / src.MAIN["s_mva"]


def bids() -> None:
    k = unit_load()
    llf = float(np.mean(k ** 2))
    a, b = tr.ab_factors(70.0, 25, 0.075, llf)
    lines = ["two bids for one 63 MVA transformer, losses capitalised:",
             f"  mean load {k.mean():.2f} pu, loss load factor (mean k^2) {llf:.3f}",
             f"  A = {a:.2f} k u per kW of no-load loss, B = {b:.2f} k u per kW of load loss",
             "  bid                 price   P0 kW  Pk kW   losses PV   total k u"]
    rows = []
    for k, (name, d) in enumerate(src.BIDS.items(), 1):
        lc = tr.loss_cost(d["p0_kw"], d["pk_kw"], a, b)
        lines.append(f"  {name:18s} {d['price']:6,.0f}  {d['p0_kw']:5.0f}  {d['pk_kw']:5.0f}"
                     f"   {lc:9,.0f}   {d['price'] + lc:9,.0f}")
        rows.append((k, f"{d['price']:.0f}", f"{lc:.0f}"))
    csv("ch25-bids.csv", "k,price,losses", rows)
    da = src.BIDS["bid B (low price)"]["p0_kw"] - src.BIDS["bid A (low loss)"]["p0_kw"]
    db = src.BIDS["bid B (low price)"]["pk_kw"] - src.BIDS["bid A (low loss)"]["pk_kw"]
    dp = src.BIDS["bid A (low loss)"]["price"] - src.BIDS["bid B (low price)"]["price"]
    per_price = (da * a + db * b) / 70.0             # PV of the loss gap per u/MWh
    lines += [f"  at 70 u/MWh the cheaper bid wins; bid A wins above about"
              f" {dp / per_price:.0f} u/MWh",
              "  the no-load loss runs all year, so A is large; the load",
              "  loss is weighted by the mean square load, which a plant",
              "  at a 35 % capacity factor keeps small; the evaluation",
              "  formula and the price are stated in the enquiry so every",
              "  bidder optimises the same thing"]
    emit("b_bids", lines)


def thermal() -> None:
    k = unit_load()
    t_air = datapack.load_hourly()["t_air_c"].to_numpy()
    hs = np.array([tr.hot_spot(x, t) for x, t in zip(k, t_air)])
    v = np.array([tr.ageing_rate(h) for h in hs])
    lines = ["hot spot and ageing of one main transformer over the data-pack year:",
             f"  hours above 0.9 pu: {int((k > 0.9).sum())}; max load {k.max():.2f} pu",
             f"  hot spot: max {hs.max():.0f} C, mean {hs.mean():.0f} C",
             f"  ageing: {v.sum() / 24:,.1f} days of life used in 365 days"
             f" (relative rate {v.mean():.3f})",
             "  a plant transformer is lightly loaded most of the year: it",
             "  ages slowly, so a short overload in the hottest hours costs",
             "  little life - the thermal model and the loading guide of the",
             "  maker decide how much, not this teaching model"]
    emit("b_thermal", lines)
    idx = np.argsort(-hs)[:2000]
    rows = [(f"{k[i]:.3f}", f"{hs[i]:.1f}") for i in idx[::10]]
    csv("ch25-hotspot.csv", "k,hs", rows)


def cooling() -> None:
    lines = ["ONAN and ONAF: the same transformer with and without fans:",
             f"  ONAN rating {src.MAIN['s_onan_mva']:.0f} MVA, ONAF rating {src.MAIN['s_mva']:.0f} MVA"]
    k = unit_load() * src.MAIN["s_mva"] / src.MAIN["s_onan_mva"]
    lines += [f"  hours above the ONAN rating: {int((k > 1).sum())} of 8760",
              "  the fans run only in those hours; if they fail, the plant",
              "  controller limits the transformer to its ONAN rating",
              "  (an alarm and a limit in the cause-and-effect, ch 23)"]
    emit("b_cooling", lines)


def design() -> None:
    lines = ["design dependencies a reviewer can check (simplified relations):",
             "  change                          effect",
             "  flux density B up 10 %          turns down 9 %, core loss up ~21 %",
             "  current density J up 10 %       copper section down 9 %, load loss up ~10 %",
             "  impedance up (more leakage)     fault current down, regulation up",
             "  turns up 10 % (same window)     leakage reactance up ~21 % (x ~ N^2)",
             "  cooling ONAN -> ONAF            rating up for the same active part",
             "  each choice moves cost, losses, impedance and size together;",
             "  the maker's design software balances them against the",
             "  specification - simplified equations show the direction,",
             "  not the design"]
    emit("b_design", lines)


if __name__ == "__main__":
    bids()
    thermal()
    cooling()
    design()
