"""Chapter 39, lessons A to C (sourcing, technical bid review, commercial and
quality controls): package boundaries and interfaces, make or buy,
sub-supplier mapping and continuity, the technical review of an offer,
comparable environmental data, delay damages and their cap, warranty and
spares over life, witness points and concessions.

Run from the project root:   python -m companion.ch39.examples_a
Writes companion/ch39/expected/a_*.txt.
Teaching values (A-425 to A-429); no real supplier or law.
"""
from __future__ import annotations

from companion.ch39.common import emit
from plantp import procure as pr


def packages() -> None:
    options = {"single EPC": (1, 0, 1.00), "EPC + turbine OEM": (2, 1, 0.97),
               "five packages": (5, 10, 0.93)}
    lines = ["package strategy: contracts, interfaces between them, relative price",
             "  strategy              contracts   interfaces   price   owner's risk"]
    for name, (c, i, p) in options.items():
        risk = "low" if i == 0 else ("medium" if i <= 2 else "high")
        lines.append(f"  {name:20s} {c:9d}   {i:10d}   {p:5.2f}   {risk}")
    lines += ["  every split saves margin and adds interfaces the owner must",
              "  manage; with n packages there are up to n(n-1)/2 of them.",
              "  The split follows the owner's ability to manage interfaces",
              "  (ch 18, ch 38), not only the price"]
    emit("a_packages", lines)


def make_buy() -> None:
    rows = [("PV mounting structures", "buy, local fabricator", "simple, heavy to ship"),
            ("turbines", "buy, OEM", "design, certificate"),
            ("SCADA integration", "make, owner's engineer", "knowledge kept"),
            ("MV cables", "buy, two qualified makers", "continuity of supply"),
            ("site civil works", "buy, local contractor", "local labour")]
    lines = ["make or buy decisions (teaching)",
             "  item                     decision                      main reason"]
    for a, b, c in rows:
        lines.append(f"  {a:24s} {b:29s} {c}")
    lines += ["  'make' keeps knowledge and control and needs the people;",
              "  'buy' needs a specification, a qualified supplier and",
              "  someone who can judge the result"]
    emit("a_makebuy", lines)


def subtier() -> None:
    chain = [("transformer factory", 1, 0.99), ("core steel mill", 2, 0.95),
             ("copper wire drawer", 2, 0.97), ("bushing maker", 2, 0.96),
             ("tap changer maker", 2, 0.98)]
    p_all = 1.0
    for _, _, p in chain:
        p_all *= p
    lines = ["critical sub-suppliers of a transformer and their on-time chance (teaching)",
             "  supplier               tier   on time"]
    for a, t, p in chain:
        lines.append(f"  {a:22s} {t:4d}   {p * 100:6.0f} %")
    lines += [f"  all on time together: {p_all * 100:.0f} %",
              f"  the factory's own record is 99 %, the chain's {p_all * 100:.0f} %; the",
              "  audit maps the second tier, and a single-source part with",
              "  a long lead (core steel) gets a buffer or a second source"]
    emit("a_subtier", lines)


def bid_review() -> None:
    checks = [("design assumptions", "45 C ambient, 1,000 m - as specified"),
              ("standard editions", "power transformer parts quoted with years"),
              ("deviations", "listed, each with a reason and a price"),
              ("drawings", "outline, rating plate, foundation loads"),
              ("calculations", "short-circuit withstand, temperature rise"),
              ("material declarations", "fluid, core steel grade, paint"),
              ("certificates", "type test report: which unit, which lab"),
              ("test plan", "routine, type, witness points"),
              ("spares, tools, training", "listed with prices and lead times"),
              ("repair limits", "what can be repaired on site"),
              ("life-cycle support", "years of spares and service")]
    lines = ["technical review of an offer: what is checked (teaching)"]
    for a, b in checks:
        lines.append(f"  {a:24s} {b}")
    lines += ["  a type test report for another rating, an undated standard",
              "  or a deviation hidden in a footnote each turn a compliant",
              "  offer into one that is not"]
    emit("a_review", lines)


def environment_data() -> None:
    rows = [("U-A", "EPD, verified", "cradle to gate", 2024, "+/- 10 %", 41.0),
            ("U-B", "maker's declaration", "gate to gate", 2019, "not stated", 8.0),
            ("U-C", "generic factor", "cradle to gate", 2016, "+/- 30 %", 36.0)]
    lines = ["footprint of one 5.6 MVA unit, t CO2e, as offered (synthetic)",
             "  offer  source               boundary         year   uncertainty   value"]
    for o, src, bnd, yr, unc, v in rows:
        lines.append(f"  {o:5s}  {src:19s}  {bnd:15s}  {yr:4d}   {unc:11s}   {v:5.1f}")
    lines += ["  U-B looks lowest because its boundary leaves out the",
              "  materials; U-C's generic factor is old and wide. Only",
              "  U-A's verified declaration can be compared - and only with",
              "  another one on the same boundary and rules. None is a",
              "  guaranteed project result (ch 33, life-cycle data);",
              "  lesson J brings all three to one boundary"]
    emit("a_envdata", lines)


def delay_damages() -> None:
    price = 1_160.0
    lines = ["delay damages on the transformer order: 0.5 % a week, cap 10 % (teaching)",
             "  weeks late   damages k u   cap reached"]
    for w in (2, 8, 20, 30):
        amt, cap = pr.ld_amount(w, 0.005, price, 0.10)
        lines.append(f"  {w:10d}   {amt:11.1f}   {'yes' if cap else 'no'}")
    project_cost_week = 107_426 * 70.0 / 52 / 1000      # PV energy a week at 70 u/MWh
    lines += [f"  a week of late PV costs the project about {project_cost_week:.0f} k u"
              " (107 GWh/yr at 70 u/MWh);",
              "  the damages pay 5.8 k u a week and stop at 116 k u. They",
              "  are a pre-agreed estimate, not insurance: the schedule",
              "  float and the follow-up of the order protect the project"]
    emit("a_ld", lines)


def warranty_spares(rate: float = 0.075) -> None:
    rows = [("U-A", 5, 30.0), ("U-B", 2, 18.0), ("U-C", 3, 24.0)]
    vals = {}
    repair = 60.0                                       # k u for one repair after warranty
    fail_rate = 0.01                                    # per unit-year (teaching)
    lines = ["warranty years and spares, present value over 25 years (teaching)",
             "  offer   warranty   expected repairs after warranty, k u   spares k u"]
    for o, y, sp in rows:
        exp = sum(10 * fail_rate * repair / (1 + rate) ** t for t in range(y + 1, 26))
        vals[o] = exp
        lines.append(f"  {o:5s}   {y:8d}   {exp:37.1f}   {sp:10.0f}")
    lines += [f"  U-A's longer warranty is worth {vals['U-B'] - vals['U-A']:.0f} k u against U-B in repairs;",
              "  the bigger value is the evidence a warranty period",
              "  produces (early failures found while the maker pays)"]
    emit("a_warranty", lines)


def witness() -> None:
    rows = [("heat run", "witnessed", "temperature rise, not just losses"),
            ("loss measurement", "witnessed", "the guarantee is paid on it"),
            ("applied voltage", "witnessed", "insulation"),
            ("routine tests", "reports reviewed", "every unit"),
            ("painting", "sample inspected", "thickness readings")]
    lines = ["factory witness points of the transformer order (teaching)",
             "  test or step         how                why"]
    for a, b, c in rows:
        lines.append(f"  {a:19s}  {b:17s}  {c}")
    lines += ["  a failed test makes a nonconformity: repaired and",
              "  retested, or accepted as is by a written concession with",
              "  a price or a longer warranty - never by silence (ch 40)"]
    emit("a_witness", lines)


if __name__ == "__main__":
    packages()
    make_buy()
    subtier()
    bid_review()
    environment_data()
    delay_damages()
    warranty_spares()
    witness()
