"""Chapter 39, lab D (bid evaluation): three fictional offers for the PV unit
transformers compared with a transparent compliance and deviation matrix,
an evaluated price with capitalised losses, delivery and currency, the
factory capability audit, the supplier data schedule, and the award
recommendation that follows from all of them.

Run from the project root:   python -m companion.ch39.lab_d
Writes companion/ch39/expected/d_*.txt.
Synthetic offers (A-425 to A-428).
"""
from __future__ import annotations

from companion.ch39 import sources as src
from companion.ch39.common import csv, emit
from plantp import procure as pr
from plantp import transformer as tr

CRITICAL = {r for r, (_, c) in src.REQS.items() if c}


def matrix() -> None:
    lines = ["compliance and deviation matrix (C comply, D deviate, N not offered)",
             "  req   critical   U-A   U-B   U-C   requirement"]
    code = {"comply": "C", "deviate": "D", "no": "N"}
    for r, (text, crit) in src.REQS.items():
        row = [code[src.OFFERS[o]["answers"][r]] for o in src.OFFERS]
        if set(row) == {"C"}:
            continue                                   # show only where offers differ
        lines.append(f"  {r}   {'yes' if crit else '':8s}   {row[0]:3s}   {row[1]:3s}"
                     f"   {row[2]:3s}   {text}")
    for o, off in src.OFFERS.items():
        share, missed = pr.compliance(off["answers"], CRITICAL)
        lines.append(f"  {o}: full compliance {share * 100:.0f} %; critical not met:"
                     f" {', '.join(missed) or 'none'}")
    lines += ["  a deviation on a critical item is not priced, it is",
              "  cleared or the offer is not acceptable; U-B offers no",
              "  witness of the heat run and no data schedule"]
    emit("d_matrix", lines)


def evaluated() -> dict:
    f = src.FINANCE
    a, b = tr.ab_factors(f["energy_price"], f["years"], f["rate"], f["load_loss_factor"])
    rows = {}
    for o, off in src.OFFERS.items():
        losses = src.PACKAGE["units"] * tr.loss_cost(off["p0_kw"], off["pk_kw"], a, b)
        late = max(0, off["week"] - src.PACKAGE["need_week"])
        ld_rate = f["ld_per_week"] * off["price"]
        ev = pr.evaluated_price(off["price"], off["deviations"], losses, late, ld_rate,
                                off["foreign"], f["fx_allowance"])
        rows[o] = dict(price=off["price"], dev=off["deviations"], losses=losses,
                       late=late * ld_rate, fx=off["price"] * off["foreign"]
                       * f["fx_allowance"], total=ev)
    return rows


def price_table() -> None:
    f = src.FINANCE
    a, b = tr.ab_factors(f["energy_price"], f["years"], f["rate"], f["load_loss_factor"])
    rows = evaluated()
    lines = [f"evaluated price, k u (losses at A {a:.2f}, B {b:.2f} k u/kW; ch 25)",
             "  offer   price   deviations   losses   late delivery   currency    total"]
    for o, r in rows.items():
        lines.append(f"  {o:5s} {r['price']:7,.0f}   {r['dev']:10.0f}   {r['losses']:6,.0f}"
                     f"   {r['late']:13.0f}   {r['fx']:8.0f}   {r['total']:6,.0f}")
    csv("ch39-evaluated.csv", "i,price,dev,losses,late,fx",
        [(i, round(r["price"]), round(r["dev"]), round(r["losses"]), round(r["late"]),
          round(r["fx"])) for i, r in enumerate(rows.values())])
    low = min(rows, key=lambda k: rows[k]["price"])
    best = min(rows, key=lambda k: rows[k]["total"])
    lines += [f"  lowest price: {low}; lowest evaluated price: {best}",
              "  the losses over 25 years cost about as much as the units;",
              "  the cheapest offer is the most expensive to own. Late",
              "  delivery is priced at the delay damages it would cost the",
              "  project, currency at an allowance on the foreign share"]
    emit("d_price", lines)


def audits() -> None:
    lines = ["factory capability audit, scores 0-5 with critical floors (A-426)",
             "  item                    weight   U-A   U-B   U-C   floor"]
    for k, w in src.AUDIT_WEIGHTS.items():
        sc = [src.AUDITS[o][k] for o in src.AUDITS]
        fl = src.AUDIT_FLOORS.get(k)
        lines.append(f"  {k:22s} {w:6d}   {sc[0]:3d}   {sc[1]:3d}   {sc[2]:3d}"
                     f"   {fl if fl else '':>5}")
    for o in src.AUDITS:
        s, fails = pr.audit_score(src.AUDITS[o], src.AUDIT_WEIGHTS, src.AUDIT_FLOORS)
        lines.append(f"  {o}: weighted {s:.2f}; below a floor: {', '.join(fails) or 'none'}")
    lines += ["  a weighted score hides a weak critical process; the floor",
              "  makes it a fail whatever the other scores. U-C's low",
              "  capacity score is a delivery risk to watch, not a fail"]
    emit("d_audit", lines)


def data_schedule() -> None:
    lines = ["supplier data schedule: 14 items committed and valid",
             "  offer   share   missing or not valid"]
    for o, c in src.DATA_COMMIT.items():
        share, bad = pr.schedule_completeness(src.DATA_ITEMS, c)
        short = ", ".join(b.split()[0] for b in bad) or "none"
        lines.append(f"  {o:5s} {share * 100:5.0f} %   {short}")
    lines += ["  a delivery defined as 'documents' would accept all three;",
              "  defined as data items with a schema, an update duty and",
              "  the right to use them, none meets it in full - U-A lacks",
              "  only the update duty, which is negotiated before award"]
    emit("d_data", lines)


def award() -> None:
    rows = evaluated()
    verdict = []
    for o, off in src.OFFERS.items():
        _, missed = pr.compliance(off["answers"], CRITICAL)
        _, fails = pr.audit_score(src.AUDITS[o], src.AUDIT_WEIGHTS, src.AUDIT_FLOORS)
        ok = not missed and not fails
        verdict.append((o, rows[o]["total"], ok, missed + fails))
    accept = sorted([v for v in verdict if v[2]], key=lambda v: v[1])
    lines = ["award recommendation for the PV unit transformers (A-428)"]
    for o, total, ok, why in verdict:
        lines.append(f"  {o}: evaluated {total:,.0f} k u; "
                     + ("acceptable" if ok else "not acceptable - " + ", ".join(why)))
    win = accept[0]
    lines += [f"  recommended: {win[0]}, lowest evaluated price among acceptable offers,",
              f"    {accept[1][1] - win[1]:,.0f} k u ({(accept[1][1] - win[1]) / win[1] * 100:.0f} %) below the"
              " next - a margin inside",
              "    the uncertainty of the loss evaluation; the audit (3.76",
              "    against 3.24) and the data schedule decide it as well",
              "  conditions: close U-A's two deviations (fluid, monitoring",
              "  interface) and its data update duty before signature;",
              "  the recommendation is the procurement team's; the award",
              "  is the owner's decision"]
    emit("d_award", lines)


if __name__ == "__main__":
    matrix()
    price_table()
    audits()
    data_schedule()
    award()
