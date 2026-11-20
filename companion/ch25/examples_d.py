"""Chapter 25, section B - the transformer as a product: core mass and
no-load loss from the steel's specific loss, the factory route of an
oil-filled and a dry-type unit, the quality gates with their purpose and
evidence, and the oil and dry unit transformers compared.

Run from the project root:   python -m companion.ch25.examples_d
Writes companion/ch25/expected/m_*.txt. Teaching values A-326 to A-330.
"""
from __future__ import annotations

from companion.ch25 import sources as src
from companion.ch25.common import emit


def core() -> None:
    p0 = src.MAIN["p0_kw"]
    lines = ["core mass and no-load loss (teaching steel data):",
             "  steel W/kg at 1.7 T   building factor   core mass for P0 = 35 kW"]
    for wkg in (0.80, 0.90, 1.05):
        for bf in (1.10, 1.20):
            lines.append(f"  {wkg:18.2f}   {bf:15.2f}   {p0 * 1e3 / (wkg * bf) / 1e3:10.1f} t")
    lines += ["  better steel (lower W/kg) and careful cutting and stacking",
              "  (a lower building factor: the joints add loss) give the",
              "  same no-load loss with a different core; the maker's",
              "  guarantee is checked by the no-load test, not by this sum"]
    emit("m_core", lines)


def route() -> None:
    oil = ["approved design and material traceability",
           "core cutting and stacking (step-lap joints)",
           "winding of the coils, inspection of conductors and turns",
           "insulation assembly (pressboard, spacers, barriers)",
           "lead connection and active-part clamping",
           "drying of the active part to the maker's moisture target",
           "tanking, vacuum and oil filling with processed oil",
           "sealing, leak check, finishing, tests, transport preparation"]
    dry = ["approved design and material traceability",
           "core cutting and stacking",
           "winding (foil or strip), cast or impregnated in resin",
           "curing under controlled temperature",
           "assembly in the frame, leads and taps",
           "enclosure, sensors, tests, transport preparation"]
    lines = ["factory route of a transformer (concept):", "  oil-filled:"]
    lines += [f"    {k + 1}. {s}" for k, s in enumerate(oil)]
    lines.append("  dry-type (cast resin):")
    lines += [f"    {k + 1}. {s}" for k, s in enumerate(dry)]
    lines += ["  drying, vacuum and oil processing need purpose-built plant",
              "  and approved procedures; their records (moisture, oil",
              "  quality, vacuum hold) belong in the dossier"]
    emit("m_route", lines)


def gates() -> None:
    g = [("material certificates", "core steel, copper, pressboard, oil are as specified"),
         ("dimensional checks", "core and windings are as designed"),
         ("winding and lead inspection", "no damage, joints and clearances right"),
         ("moisture control after drying", "insulation is dry before tanking"),
         ("leak check", "the tank and seals hold"),
         ("ratio, polarity, vector group", "the windings are connected right"),
         ("winding resistance", "joints are sound; base for the load-loss test"),
         ("losses and impedance", "the guarantees and the system values"),
         ("dielectric tests", "the insulation withstands its levels"),
         ("temperature rise (type or special)", "the cooling meets the rating")]
    lines = ["quality gates in the factory (purpose, not procedure):",
             "  gate                               proves that"]
    lines += [f"  {a:34s} {b}" for a, b in g]
    lines += ["  each gate leaves a record; the factory acceptance test",
              "  (FAT) is witnessed by the owner, and the dossier is",
              "  reviewed against the contract (worked example, section D)"]
    emit("m_gates", lines)


def oil_vs_dry() -> None:
    u = src.UNIT
    o, d = u["PV block, oil, outdoor skid"], u["turbine, dry type, in tower"]
    lines = ["oil-filled and dry-type unit transformers (teaching data):",
             "                              oil skid        dry in tower",
             f"  rating MVA                  {o['s_mva']:8.1f}        {d['s_mva']:8.1f}",
             f"  no-load loss kW             {o['p0_kw']:8.1f}        {d['p0_kw']:8.1f}",
             f"  load loss kW                {o['pk_kw']:8.1f}        {d['pk_kw']:8.1f}",
             f"  oil m3                      {o['oil_m3']:8.1f}        {d['oil_m3']:8.1f}",
             "  site needs: oil skid - bund, outdoor, sampling; dry type -",
             "  indoor, ventilation, cleaner air, no oil fire load",
             "  the dry unit costs more loss and money but fits inside a",
             "  tower where an oil fire would be unacceptable; outdoors on",
             "  a skid, oil is cheaper and cools better"]
    emit("m_oildry", lines)


if __name__ == "__main__":
    core()
    route()
    gates()
    oil_vs_dry()
