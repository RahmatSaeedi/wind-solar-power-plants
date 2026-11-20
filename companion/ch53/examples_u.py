"""Chapter 53, round u: the plant's lifecycle cost per MWh to date, an
extension's energy and cost against retirement at 25, the order of
decommissioning works, residual service of a replaced part, insurance
and the deductible near the end, the decision record as a register, and
a retirement evidence checklist.

Run from the project root:   python -m companion.ch53.examples_u
Writes companion/ch53/expected/u_*.txt. Teaching values (A-538 to A-545).
"""
from __future__ import annotations

from companion.ch53 import sources as src
from companion.ch53.common import emit
from plantp import lifecycle as lc


# ------------------------------------------------ 1. extend to 30 or retire at 25
def extend_or_retire(e_mwh: float = 255_000.0) -> dict:
    yrs = 5
    capex = 9_000.0                       # inverters, gearbox programme, controls (teaching)
    opex = 4_400.0                        # k u a year in years 26-30 (rising with age)
    value = e_mwh * 0.94 * src.PRICE_AFTER / 1000          # availability falling
    af = (1 - (1 + src.RATE) ** -yrs) / src.RATE
    disc = (1 + src.RATE) ** -(src.LIFE - src.YEAR_NOW)
    npv = (-capex + (value - opex) * af) * disc
    lines = [f"extend to year 30 or retire at 25 (seen from year {src.YEAR_NOW}, teaching)",
             f"  extension capex {capex:,.0f} k u; years 26-30: energy value {value:,.0f} k u",
             f"  a year at {src.PRICE_AFTER:.0f} u/MWh, opex {opex:,.0f} k u a year",
             f"  NPV of the extension today: {npv:+,.0f} k u",
             "  the decommissioning cost is the same, only later (a deferral",
             "  worth something at 7.5 %) - the extension is decided with the",
             "  tower fatigue, the permits and the price after the PPA"]
    emit("u_extend", lines)
    return dict(npv=npv, value=value)


# ------------------------------------------------ 2. order of decommissioning works
def order() -> list:
    steps = ["isolate and earth all circuits under permits (ch 32, ch 50 in reverse)",
             "drain and recover oils and gas (licensed contractors)",
             "remove batteries (dangerous goods)",
             "dismantle turbines (crane campaign) and PV fields",
             "remove cables, substation and foundations to the agreed depth",
             "restore the ground and start the monitoring",
             "hand the land back on the monitoring record"]
    lines = ["decommissioning works in order (records, not a method statement)"]
    lines += [f"  {k + 1}. {s}" for k, s in enumerate(steps)]
    lines += ["  each step ends with its record - an isolation certificate, a",
              "  transfer note, a receiver's certificate, a survey - and the",
              "  next step starts on that record (ch 49 hold points)"]
    emit("u_order", lines)
    return steps


# ------------------------------------------------ 3. residual service of a replaced part
def residual() -> dict:
    new_life_h = 150_000.0 * 0.886                    # Weibull mean of a new gearbox (k 2.5)
    used_h = 7 * 0.93 * 8760                          # to year 25
    share = used_h / new_life_h
    lines = [f"a gearbox replaced now: mean life {new_life_h:,.0f} h, used to year 25 "
             f"{used_h:,.0f} h",
             f"  share of its life the plant uses: {share:.0%}; {1 - share:.0%} is residual",
             "  service - worth something only if sold, reused at another",
             "  plant or carried into an extension; a footprint or cost that",
             "  charges the whole unit to 7 years overstates the option"]
    emit("u_residual", lines)
    return dict(share=share)


# ------------------------------------------------ 4. insurance near the end
def insurance(premium: float = 420.0, deductible: float = 250.0) -> dict:
    p_loss = 0.15
    loss = 1_800.0
    exp = p_loss * max(loss - deductible, 0)
    lines = [f"property insurance at year {src.YEAR_NOW}: premium {premium:,.0f} k u, deductible "
             f"{deductible:,.0f} k u",
             f"  expected recovery {p_loss:.0%} x ({loss:,.0f} - {deductible:,.0f}) = {exp:,.0f} k u a year",
             f"  premium minus expected recovery: {premium - exp:,.0f} k u a year - the price of",
             "  not carrying the tail; near the end the insurer asks for",
             "  condition evidence (lesson E) and the premium follows it"]
    emit("u_insure", lines)
    return dict(exp=exp, net=premium - exp)


# ------------------------------------------------ 5. the decision record as a register
def register() -> list:
    rows = [("D-057-1", "gearboxes: repair at failure to year 25", "lesson D", "price, k, restore"),
            ("D-057-2", "inverters: replace before year 21", "the upgrade lesson", "repairs, support"),
            ("D-057-3", "repowering studied as a new application", "lesson B", "grid gaps, permits"),
            ("D-057-4", "decommissioning fund from now", "lesson C", "scrap prices"),
            ("D-057-5", "records migrated, access removed", "lesson H", "obligations")]
    lines = ["lifecycle decisions as a register: what, evidence, what would change it"]
    for i, d, e, c in rows:
        lines += [f"  {i}  {d}", f"     evidence: {e}; re-open if these change: {c}"]
    lines += ["  a decision that names what would re-open it can be re-taken",
              "  (ch 38 change control, ch 59 evidence case)"]
    emit("u_register", lines)
    return rows


# ------------------------------------------------ 6. retirement evidence checklist
def checklist() -> dict:
    items = [("isolation certificates for every circuit", True),
             ("transfer notes reconciled for every hazardous load", False),
             ("receivers' certificates", False), ("SF6 recovery records", False),
             ("foundation removal survey to the agreed depth", False),
             ("restoration monitoring record", False), ("land acceptance by the landholder", False),
             ("records migrated and access removed (scan)", False),
             ("commitments closed with evidence", False), ("fund released", False)]
    done = sum(1 for _, d in items if d)
    lines = ["retirement evidence: what closes the plant (at the start of the works)"]
    lines += [f"  [{'x' if d else ' '}] {k}" for k, d in items]
    lines += [f"  {done} of {len(items)} at the start - the list is the plan of the",
              "  closure: each item has an owner and a date, and the plant is",
              "  closed when the last one is evidenced, not when the last",
              "  turbine leaves"]
    emit("u_checklist", lines)
    return dict(done=done, total=len(items))


# ------------------------------------------------ 7. the functional unit
def functional_unit() -> dict:
    opts = {"repair (to 25)": ((450 + 1_100), 7, 7 * 255_000.0),
            "replace (to 25)": ((1_400 + 1_100), 7, 7 * 256_500.0),
            "repower (to 35)": ((21_600 + 2_700 + 1_200), 17, 17 * 310_000.0)}
    lines = ["the same three options per year of service and per kWh delivered"]
    lines += [f"  {k:16s} {t / y:7,.0f} t CO2e a year   {t * 1e6 / (e * 1e3):5.2f} g/kWh"
              for k, (t, y, e) in opts.items()]
    per_year = sorted(opts, key=lambda k: opts[k][0] / opts[k][1])
    per_kwh = sorted(opts, key=lambda k: opts[k][0] / opts[k][2])
    lines += [f"  ranking per year: {' < '.join(per_year)}",
              f"  ranking per kWh:  {' < '.join(per_kwh)}",
              "  the rankings agree here, but per year hides that the options",
              "  deliver different energy over different lives: the",
              "  functional unit follows the service - energy delivered"]
    emit("u_fu", lines)
    return dict(same=per_year == per_kwh)


if __name__ == "__main__":
    extend_or_retire()
    order()
    residual()
    insurance()
    register()
    checklist()
    functional_unit()
