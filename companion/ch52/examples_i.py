"""Chapter 52, lesson I: the CMMS/EAM data workflow - work orders checked
against the asset hierarchy, failure codes, test evidence, labour and
parts, repeat failures from the orders themselves, warranty claims in
time, MTBF from orders against SCADA events, the alarm-to-order handoff,
and obsolescence notices.

Run from the project root:   python -m companion.ch52.examples_i
Writes companion/ch52/expected/i_*.txt. Teaching values (A-537).
"""
from __future__ import annotations

from companion.ch52 import sources as src
from companion.ch52.common import emit


def assets() -> set:
    out = set(src.HIERARCHY)
    for kids in src.HIERARCHY.values():
        out.update(kids)
    return out


# ------------------------------------------------ 1. data-quality checks
def checks() -> dict:
    known = assets()
    res = {"no or unknown asset": [], "corrective without a failure code": [],
           "code not in the list": [], "closed without a test record": [],
           "open (not closed)": []}
    for wo, a, typ, code, lab, parts, test, closed in src.WORK_ORDERS:
        if a not in known:
            res["no or unknown asset"].append(wo)
        if typ == "CM" and not code:
            res["corrective without a failure code"].append(wo)
        if code and code not in src.FAILURE_CODES:
            res["code not in the list"].append(wo)
        if closed and not test:
            res["closed without a test record"].append(wo)
        if not closed:
            res["open (not closed)"].append(wo)
    bad = {w for v in res.values() for w in v if v is not res["open (not closed)"]}
    lines = [f"work orders checked: {len(src.WORK_ORDERS)}"]
    lines += [f"  {k:34s} {len(v)}  {', '.join(v)}" for k, v in res.items()]
    lines += [f"  {len(bad)} of {len(src.WORK_ORDERS)} orders fail a check: WT07's gearbox is",
              "  not in the hierarchy (the asset was never loaded), WO-0431",
              "  has no asset at all - neither reaches the reliability data"]
    emit("i_checks", lines)
    return dict(res={k: len(v) for k, v in res.items()}, bad=len(bad))


# ------------------------------------------------ 2. repeats from the orders
def repeats() -> dict:
    by = {}
    for wo, a, typ, code, *_ in src.WORK_ORDERS:
        if typ == "CM" and a and code:
            by.setdefault((a, code), []).append(wo)
    rep = {k: v for k, v in by.items() if len(v) > 1}
    lines = ["repeat failures found by asset and failure code"]
    lines += [f"  {a} {c}: {', '.join(v)}" for (a, c), v in rep.items()]
    lines += ["  the query works only on orders with an asset and a code:",
              "  WO-0418 (no code) may be a third pitch-battery failure on",
              "  WT03 - it cannot be counted, and lesson C's RCA misses it"]
    emit("i_repeats", lines)
    return dict(rep=len(rep))


# ------------------------------------------------ 3. warranty claims in time
def warranty(cod_day: int = 0, months: int = 24) -> dict:
    limit = cod_day + months * 30.4
    claims = [(wo, a, code) for wo, a, typ, code, _, parts, test, closed in src.WORK_ORDERS
              if typ == "CM" and parts and closed and closed <= limit]
    ready = [c for c in claims if c[0] not in ("WO-0418", "WO-0431")]
    lines = [f"warranty: corrective orders with parts inside {months} months of COD"]
    lines += [f"  {wo} {a or '(no asset)'} {code}" for wo, a, code in claims]
    lines += [f"  {len(claims)} candidate claims; {len(ready)} have the asset, code and",
              "  test record a maker asks for - the rest are lost money unless",
              "  the records are completed before the warranty ends"]
    emit("i_warranty", lines)
    return dict(claims=len(claims), ready=len(ready))


# ------------------------------------------------ 4. MTBF from orders against SCADA
def mtbf_sources(exposure_h: float = 12 * 8760.0) -> dict:
    scada_trips = 14                       # T-fleet converter trips needing a visit (SCADA)
    wo_coded = 9                           # orders with a converter code
    lines = ["turbine converter failures in the first year, by source",
             f"  SCADA events needing a visit: {scada_trips}; work orders coded CNV: {wo_coded}",
             f"  MTBF from the orders {exposure_h / wo_coded:,.0f} h, from SCADA "
             f"{exposure_h / scada_trips:,.0f} h",
             f"  the orders undercount by {1 - wo_coded / scada_trips:.0%}: uncoded or merged",
             "  visits - a reliability figure is only as good as the",
             "  orders behind it; the two sources are reconciled monthly"]
    emit("i_mtbf", lines)
    return dict(wo=exposure_h / wo_coded, scada=exposure_h / scada_trips)


# ------------------------------------------------ 5. alarm-to-order handoff
def handoff() -> dict:
    lat = [0.2, 0.5, 1.0, 0.3, 26.0, 2.0, 0.4, 70.0, 0.8, 1.5]   # h from alarm to order
    late = [x for x in lat if x > 24]
    lat_s = sorted(lat)
    lines = ["SCADA alarm to work order: hours, ten corrective jobs",
             "  " + " ".join(f"{x:5.1f}" for x in lat),
             f"  median {lat_s[len(lat_s) // 2 - 1] / 2 + lat_s[len(lat_s) // 2] / 2:.1f} h; "
             f"over a day: {len(late)}",
             "  the two late ones came in over a weekend with nobody",
             "  creating orders from alarms - an automatic order for set",
             "  alarm classes (with a person approving it) closes the gap"]
    emit("i_handoff", lines)
    return dict(late=len(late))


# ------------------------------------------------ 6. obsolescence
def obsolescence() -> dict:
    notices = {"IGBT stack PCI-5500": ("last-time buy 2031", 2, 4),
               "pitch battery pack": ("end of production 2030", 6, 12),
               "RTU CPU card": ("discontinued", 1, 3),
               "SCADA server OS": ("support ends 2032", 0, 0)}
    lines = ["obsolescence notices against stock and the need to end of life"]
    lines += [f"  {k:22s} {n:24s} held {h:2d}  need {d:2d}" for k, (n, h, d) in notices.items()]
    lines += ["  for parts: buy to the remaining need or plan a successor",
              "  (ch 53); for software: a migration plan, not a stock of",
              "  disks - an unsupported OS is a security finding (ch 36)"]
    emit("i_obsol", lines)
    return notices


if __name__ == "__main__":
    checks()
    repeats()
    warranty()
    mtbf_sources()
    handoff()
    obsolescence()
