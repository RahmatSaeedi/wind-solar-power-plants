"""Chapter 25, sections C, D, F and G - the test dossier reviewed against
the guarantees (worked example), transport and installation numbers, oil
containment and the fire interfaces, sound at the site boundary, and the
export substation's bus arrangements compared by expected outage hours.

Run from the project root:   python -m companion.ch25.examples_c
Writes companion/ch25/expected/c_*.txt, d_*.txt, f_*.txt and g_*.txt.
Teaching values A-326 to A-330; tolerances are contract terms here, not a
standard's figures.
"""
from __future__ import annotations

from companion.ch25 import sources as src
from companion.ch25.common import emit
from plantp import transformer as tr


# [start: review]
def review_item(name, declared, measured, tol):
    kind, t = tol
    if kind == "max":
        ok = measured <= declared * (1 + t)
        how = f"<= {declared * (1 + t):.3g}"
    elif kind == "band":
        ok = abs(measured - declared) <= declared * t
        how = f"{declared * (1 - t):.3g} to {declared * (1 + t):.3g}"
    elif kind == "abs":
        ok = abs(measured - declared) <= t
        how = f"within +/- {t}"
    else:                                          # a limit not to exceed
        ok = measured <= declared
        how = f"<= {declared:.3g}"
    return ok, how
# [end: review]


def dossier() -> None:
    lines = ["worked example: review of a fictional routine and type test dossier",
             "  quantity                       declared  measured  accept       result"]
    fails = []
    for name, d, m, tol in src.DOSSIER:
        ok, how = review_item(name, d, m, tol)
        lines.append(f"  {name:30s} {d:8.3g}  {m:8.3g}  {how:12s} {'ok' if ok else 'NOT OK'}")
        if not ok:
            fails.append(name)
    lines += [f"  not accepted: {', '.join(fails)}",
              "  the impedance is outside its band: the fault level, the",
              "  regulation and the parallel sharing change (section A) - the",
              "  grid study is re-run before acceptance; the winding rise",
              "  exceeds its limit: the maker explains and the owner decides",
              "  (repair, de-rate or reject) under the contract; loss",
              "  overruns inside tolerance may still cost money if the",
              "  contract prices them"]
    emit("d_dossier", lines)


def loss_penalty() -> None:
    a, b = 6.84, 0.88                           # from b_bids (k u per kW)
    p0 = 36.1 - 35.0
    pk = 262.0 - 250.0
    lines = ["loss overrun priced with the evaluation factors:",
             f"  no-load +{p0:.1f} kW x {a} = {p0 * a:.1f} k u; load +{pk:.0f} kW x {b} = {pk * b:.1f} k u",
             f"  total {p0 * a + pk * b:.1f} k u - inside tolerance but a cost to the",
             "  owner for 25 years; contracts often deduct it from the price"]
    emit("d_penalty", lines)


def transport() -> None:
    m = src.MAIN
    lines = ["transport and installation of a 63 MVA unit (teaching):",
             f"  mass in service {m['mass_t']:.0f} t; transport mass {m['transport_t']:.0f} t"
             " (oil and radiators off)",
             "  transport: the route survey (bridges, bends, overhead lines),",
             "  an impact recorder on the tank, the tank filled with dry gas",
             "  or oil, and a check of the record on arrival",
             "  installation: foundation level and loading, assembly of",
             "  bushings and coolers, oil processing to the maker's limits,",
             "  checks before energising - each a record, done under the",
             "  maker's supervision (vacuum, hot oil and high voltage work",
             "  belong to purpose-built equipment and qualified staff)"]
    emit("c_transport", lines)


def containment() -> None:
    m = src.MAIN
    lines = ["oil containment and fire interfaces of the main transformers:"]
    for area in (60.0, 90.0):
        v = tr.bund_m3(m["oil_m3"], 50.0, area)
        lines.append(f"  bund {area:.0f} m2: 110 % of {m['oil_m3']:.0f} m3 oil + 50 mm of rain"
                     f" = {v:.1f} m3")
    lines += ["  interfaces the fire design fixes (ch 31), not this chapter:",
              "    separation or a barrier wall between the two units and",
              "    the control building; containment and its drain to an",
              "    oil separator; detection; any suppression or exposure",
              "    protection; access for the fire service",
              "  dry-type unit transformers in the towers carry no oil but",
              "  their own fire and ventilation interfaces"]
    emit("f_containment", lines)


def sound() -> None:
    lines = ["transformer sound at the site boundary (free field, teaching):",
             "  each unit 72 dB(A) at 2 m; two units together:"
             f" {tr.sound_sum([72, 72]):.1f} dB(A) at 2 m"]
    for r in (50, 150, 400):
        lines.append(f"  at {r:4d} m: {tr.sound_at(tr.sound_sum([72, 72]), 2, r):5.1f} dB(A)")
    lines += ["  the limit at a home and the method come from the authority",
              "  and the noise study (ch 14, 33); low-noise cores or walls",
              "  are bought only if the study needs them"]
    emit("f_sound", lines)


def buses() -> None:
    br, bb = src.BUS["breaker"], src.BUS["busbar section"]
    tf = src.BUS["transformer"]
    # expected hours a year the export path is lost (teaching, series terms)
    single = br[0] * br[1] * 3 + bb[0] * bb[1]
    sectioned = br[0] * br[1] * 3 + bb[0] * bb[1] * 0.5
    double = br[0] * br[1] * 3 * 0.3 + bb[0] * bb[1] * 0.1
    lines = ["132 kV bus arrangements of the export substation (teaching):",
             "  arrangement             bays  breakers  export lost h/yr  cost index",
             f"  single bus                 3         3   {single:16.2f}        1.0",
             f"  single bus, sectioned      3         4   {sectioned:16.2f}        1.2",
             f"  double bus                 3         4   {double:16.2f}        1.6",
             f"  the line: {src.BUS['line'][0] * src.BUS['line'][1]:.1f} h/yr;"
             f" one transformer: {2 * tf[0] * tf[1]:.0f} h/yr at half export (ch 18)",
             "  the long repair of a transformer dominates; the double bus",
             "  saves under 2 h a year for 60 % more cost - a single bus",
             "  with a bus disconnector suits Plant P, and a spare-unit or",
             "  repair strategy matters more; the utility's rules for its",
             "  own bay may ask more (U-065)"]
    emit("g_buses", lines)


def bays() -> None:
    lines = ["export line bay E1 from the line to the plant bus (concept):",
             "  surge arresters at the line entrance and at the transformers",
             "  line disconnector with earthing switch (ownership boundary)",
             "  CTs: protection cores (line, busbar) and a metering core",
             "  VTs: protection, synchronising check and revenue metering",
             "  circuit breaker with its own protection and control",
             "  telecom: protection signalling, SCADA to the utility",
             "  the bay's equipment list, ratings and the utility's",
             "  acceptance tests are set by the connection agreement"]
    emit("g_bays", lines)


if __name__ == "__main__":
    dossier()
    loss_penalty()
    transport()
    containment()
    sound()
    buses()
    bays()
