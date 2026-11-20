"""Chapter 39, further lessons on sourcing and commercial control in
numbers: one supplier or two (and a shared sub-supplier), the order date
from a lead-time distribution, currency exposure of the three offers,
the energy price at which the cheapest offer would win, milestone
payments against the owner's exposure and the securities that cover it,
strategic spare transformers by the Poisson law, a delay claim and a
change order priced, and how many factory tests to witness.

Run from the project root:   python -m companion.ch39.examples_s
Writes companion/ch39/expected/s_*.txt and diagrams/data/ch39-*.csv.
Teaching values (A-429); concepts, not legal advice; fictional parties.
"""
from __future__ import annotations

import math

from companion.ch39 import sources as src
from companion.ch39.common import csv, emit
from plantp import procure as pr
from plantp import transformer as tr


# ----------------------------------------------- one supplier or two
def dual_source() -> dict[str, float]:
    p = 0.10                         # chance a supplier fails to deliver
    p_common = 0.06                  # chance the shared core-steel mill fails
    one = p
    two_indep = p * p
    own = (p - p_common) / (1 - p_common)     # own risk when the mill is fine
    two_shared = p_common + (1 - p_common) * own ** 2
    lines = ["one supplier or two for ten transformers (teaching chances)",
             f"  one supplier fails to deliver:          {one:.3f}",
             f"  two independent suppliers both fail:    {two_indep:.3f}",
             f"  two sharing one core-steel mill:        {two_shared:.3f}",
             "  (the mill fails with 0.06; each supplier's own risk is",
             "  the rest of its 0.10)",
             "  splitting the order looks like a cure, but a shared",
             "  sub-supplier brings most of the risk back: map tier 2",
             "  before paying the premium of two smaller orders"]
    emit("s_dual", lines)
    return dict(one=one, indep=two_indep, shared=two_shared)


# ------------------------------------------- lead time and order date
def lognormal_quantile(median: float, sigma: float, q: float) -> float:
    """Quantile of a lognormal lead time (inverse normal by bisection)."""
    lo, hi = -8.0, 8.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if 0.5 * (1 + math.erf(mid / math.sqrt(2))) < q:
            lo = mid
        else:
            hi = mid
    return median * math.exp(sigma * (lo + hi) / 2)


def order_date() -> dict[float, float]:
    need = float(src.PACKAGE["need_week"])          # weeks after the order
    median, sigma = 30.0, 0.15
    z = math.log(need / median) / sigma
    on_time = 0.5 * (1 + math.erf(z / math.sqrt(2)))
    lines = ["lead time of the transformers: median 30 weeks, spread 15 %",
             f"(lognormal); needed on site {need:.0f} weeks after the order",
             f"  chance of arriving in time if ordered as planned: "
             f"{on_time:.0%}",
             "  chance   lead weeks   order this much earlier"]
    out, rows = {}, []
    for q in (0.50, 0.80, 0.90, 0.95):
        w = lognormal_quantile(median, sigma, q)
        out[q] = w
        lines.append(f"  {q:5.0%}   {w:10.1f}   {max(0.0, w - need):10.1f}")
    for k in range(18, 46):
        zk = math.log(k / median) / sigma
        rows.append((k, round(0.5 * (1 + math.erf(zk / math.sqrt(2))), 4)))
    csv("ch39-leadtime.csv", "weeks,chance", rows)
    out["on_time"] = on_time
    lines += ["  the four weeks between the median and the need buy only",
              f"  an {on_time:.0%} chance; a 90 % chance means ordering "
              f"{out[0.90] - need:.1f} weeks",
              "  earlier - which the critical path of ch 38 must find"]
    emit("s_leadtime", lines)
    return out


# ------------------------------------------------- currency exposure
def currency() -> dict[str, float]:
    vol, z90 = 0.10, 1.2816                     # yearly FX spread, 90 %
    lines = ["currency exposure over the year to delivery (10 % spread)",
             "  offer  price k u  foreign  90 % adverse move k u"]
    out = {}
    for o, d in src.OFFERS.items():
        move = d["price"] * d["foreign"] * vol * z90
        out[o] = move
        lines.append(f"  {o:5s}  {d['price']:8,.0f}  {d['foreign']:6.0%}"
                     f"  {move:18.0f}")
    lines += ["  the evaluated price of lesson D carries an 8 % allowance;",
              "  a 90 % adverse move is larger for U-C (90 % foreign);",
              "  a forward contract fixes the rate at a cost - a",
              "  treasury decision, named here as a concept only"]
    emit("s_currency", lines)
    return out


# ------------------------------------------ energy price and the ranking
def evaluated_at(price_mwh: float) -> dict[str, float]:
    """Evaluated price of each offer as in lab D, with the energy price
    that values the losses changed."""
    f = src.FINANCE
    a, b = tr.ab_factors(price_mwh, f["years"], f["rate"],
                         f["load_loss_factor"])
    out = {}
    for o, d in src.OFFERS.items():
        loss = src.PACKAGE["units"] * tr.loss_cost(d["p0_kw"], d["pk_kw"],
                                                   a, b)
        late = max(0, d["week"] - src.PACKAGE["need_week"])
        out[o] = pr.evaluated_price(d["price"], d["deviations"], loss, late,
                                    f["ld_per_week"] * d["price"],
                                    d["foreign"], f["fx_allowance"])
    return out


def crossing(other: str, base: str = "U-A") -> float:
    """Energy price below which `other` is evaluated cheaper than `base`."""
    lo, hi = 1.0, 100.0
    for _ in range(60):
        mid = (lo + hi) / 2
        ev = evaluated_at(mid)
        if ev[other] < ev[base]:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def reversal() -> dict[str, float]:
    rows, cross, table = [], None, {}
    for price in range(10, 101, 5):
        ev = evaluated_at(float(price))
        table[price] = ev
        rows.append((price, round(ev["U-A"], 1), round(ev["U-B"], 1),
                     round(ev["U-C"], 1)))
    cross = crossing("U-B")
    cross_c = crossing("U-C")
    csv("ch39-reversal.csv", "price,ua,ub,uc", rows)
    lines = ["evaluated price against the energy price that values losses",
             "  energy u/MWh   U-A     U-B     U-C   (k u, ten units)"]
    for pr_ in (20, 40, 70, 100):
        ev = table[pr_]
        lines.append(f"  {pr_:11d}   {ev['U-A']:6,.0f}  {ev['U-B']:6,.0f}  "
                     f"{ev['U-C']:6,.0f}")
    lines += [f"  U-C undercuts U-A below {cross_c:.0f} u/MWh, U-B below "
              f"{cross:.0f} u/MWh",
              "  U-B fails critical items whatever the price (lesson D);",
              f"  the flip that matters is U-C at {cross_c:.0f} u/MWh, "
              f"{1 - cross_c / 70:.0%} under the",
              "  70 used: the recommendation says it holds above that",
              "  value and asks whether the offtake price (ch 21) makes a",
              "  lower one credible - a flip is reported, not hidden"]
    emit("s_reversal", lines)
    return dict(ub=cross, uc=cross_c)


# ------------------------------------- milestones, exposure, securities
MILESTONES = [  # (week, share paid, event) - teaching
    (0, 0.10, "order (advance)"), (8, 0.30, "drawings approved"),
    (26, 0.40, "FAT passed"), (32, 0.20, "delivered to site")]
VALUE = [(0, 0.0), (8, 0.15), (16, 0.45), (26, 0.85), (32, 1.0)]


def value_at(w: float) -> float:
    for (w0, v0), (w1, v1) in zip(VALUE, VALUE[1:]):
        if w0 <= w <= w1:
            return v0 + (v1 - v0) * (w - w0) / (w1 - w0)
    return 1.0


def exposure() -> dict[str, float]:
    price = src.OFFERS["U-A"]["price"]
    rows, peak, peak_cov = [], (0.0, 0), (0.0, 0)
    for w in range(0, 33):
        paid = sum(s for wk, s, _ in MILESTONES if wk <= w)
        exp_ = max(0.0, paid - value_at(w)) * price
        apg = 0.10 * price if w < 26 else 0.0       # advance guarantee to FAT
        uncovered = max(0.0, exp_ - apg)
        rows.append((w, round(paid * price, 1), round(value_at(w) * price, 1),
                     round(exp_, 1), round(uncovered, 1)))
        peak = max(peak, (exp_, w))
        peak_cov = max(peak_cov, (uncovered, w))
    csv("ch39-exposure.csv", "week,paid,value,exposure,uncovered", rows)
    lines = ["owner's exposure on the U-A order: paid minus value built",
             "  milestones:"] + [f"    week {w:2d}  {s:4.0%}  {e}"
                                  for w, s, e in MILESTONES] + [
             f"  peak exposure {peak[0]:.0f} k u in week {peak[1]} (just",
             "  after drawings are approved, before the core is built)",
             f"  with an advance-payment guarantee of 10 % until FAT, the",
             f"  uncovered peak is {peak_cov[0]:.0f} k u in week {peak_cov[1]}",
             "  milestones paid ahead of value create exposure; securities",
             "  and milestone design reduce it - the instruments' wording",
             "  is for the lawyers and the banks (concept only)"]
    emit("s_exposure", lines)
    return dict(peak=peak[0], week=peak[1], uncovered=peak_cov[0])


# --------------------------------------------- strategic spare units
def poisson_cdf(k: int, mu: float) -> float:
    return sum(math.exp(-mu) * mu ** i / math.factorial(i)
               for i in range(k + 1))


def spares() -> dict[str, float]:
    units, lam, lead_y = 10, 0.01, 30 / 52        # failures a unit-year
    mu = units * lam * lead_y
    p_more = 1 - poisson_cdf(0, mu)
    years = 25
    fails_life = units * lam * years
    loss_one = 5.0 * 0.22 * 8760 * lead_y * 70 / 1000   # k u for 30 weeks
    cost_spare = 116.0 + 8.0 * years / 10                # unit + upkeep
    exp_loss = fails_life * loss_one
    lines = ["a strategic spare unit transformer? (teaching rates)",
             f"  failures expected in a 30-week replacement lead: {mu:.3f}",
             f"  chance of one or more in that window: {p_more:.1%}",
             f"  failures expected over 25 years: {fails_life:.1f}",
             f"  energy lost per failure without a spare: {loss_one:.0f} k u"
             " (5 MW, CF 0.22, 30 weeks)",
             f"  expected loss over life without a spare: {exp_loss:.0f} k u",
             f"  one spare with storage and upkeep: about {cost_spare:.0f} k u",
             "  the spare pays if failures are as likely as assumed; it",
             "  also needs the same rating and vector group - one more",
             "  reason the ten units are identical (ch 38, C-017)"]
    emit("s_spares", lines)
    return dict(mu=mu, life=fails_life, loss=loss_one, spare=cost_spare,
                exp_loss=exp_loss)


# ------------------------------------ change order and a delay claim
def claim() -> dict[str, float]:
    weeks, overhead = 6, 9.5                 # site overhead k u a week
    base_h, prod_before, prod_during = 4000.0, 1.00, 0.80
    rate = 0.045                             # k u an hour
    prolong = weeks * overhead
    lost_h = base_h * (prod_before / prod_during - 1)
    disrupt = lost_h * rate
    co_units = dict(cable_m=(1200, 0.065), terminations=(24, 0.35))
    co = sum(q * r for q, r in co_units.values())
    lines = ["a delay claim and a change order, priced (concepts only)",
             f"  owner's data six weeks late: prolongation {weeks} x "
             f"{overhead} = {prolong:.0f} k u",
             f"  disruption: productivity 1.00 -> 0.80 on {base_h:,.0f} h:"
             f" {lost_h:,.0f} h extra = {disrupt:.0f} k u",
             f"  change order C-022 (extra feeder) at contract unit rates:"
             f" {co:.1f} k u",
             "  a claim stands on records: the late transmittal (ch 38),",
             "  the planned and actual productivity, the notice given in",
             "  time; without them it is an opinion. Entitlement is for",
             "  the contract and the lawyers - the engineer supplies the",
             "  facts and the arithmetic"]
    emit("s_claim", lines)
    return dict(prolong=prolong, disrupt=disrupt, co=co)


# ------------------------------------------------ witness sampling
def witness_plan() -> dict[int, float]:
    units, bad = 10, 2                       # a systematic fault in 2 units
    lines = ["how many of ten factory tests to witness?",
             "  witnessed  chance to see at least one of 2 faulty units"]
    out = {}
    for n in (1, 2, 3, 5, 10):
        miss = math.comb(units - bad, n) / math.comb(units, n)
        out[n] = 1 - miss
        lines.append(f"  {n:9d}  {1 - miss:6.1%}")
    lines += ["  witnessing three gives about a half chance; the first",
              "  unit always (design faults show there), then a random two,",
              "  and every test report reviewed (lesson C, ch 38 sampling)"]
    emit("s_witness", lines)
    return out


if __name__ == "__main__":
    dual_source()
    order_date()
    currency()
    reversal()
    exposure()
    spares()
    claim()
    witness_plan()
