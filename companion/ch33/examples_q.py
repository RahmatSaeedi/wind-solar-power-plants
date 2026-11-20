"""Chapter 33, lesson Q (community and site, more): aviation lights at
night, labour influx against the village clinic, the conduct record of
security staff, local hiring and buying claims checked against evidence,
the value of lost grazing, erosion at the drip lines of the PV tables,
and how often smoke from a battery fire would blow toward the village.

Run from the project root:   python -m companion.ch33.examples_q
Writes companion/ch33/expected/q_*.txt and diagrams/data/ch33-influx.csv,
ch33-smoke.csv. Teaching values (A-380 to A-382); clinic, lighting and
compensation rules come from the authorities and the framework (U-112).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch33 import sources as src
from companion.ch33.common import csv, emit
from plantp import datapack


def lighting() -> None:
    night_h = 4_380.0
    share_aircraft = 0.02                 # night hours an aircraft is near (teaching)
    lines = ["aviation obstacle lights seen from the village at night (teaching)",
             f"  12 turbines, about {night_h:,.0f} night hours a year",
             f"  always on:                         {night_h:7,.0f} lit hours",
             f"  aircraft-detection lighting:       {night_h * share_aircraft:7,.0f} lit hours"
             f" ({share_aircraft * 100:.0f} %)",
             "  synchronised flashing: one pulse across the farm, not",
             "    twelve unrelated blinks",
             "  lights are an aviation-safety requirement, so the choice",
             "  of system is the aviation authority's; where it allows",
             "  detection-activated lights, the night view from the",
             "  village goes dark 98 % of the time - the photomontages",
             "  of lesson A include a night view either way"]
    emit("q_lighting", lines)


def influx() -> None:
    peak, local = 450, 0.40
    incoming = peak * (1 - local)
    village = 600
    clinic_cap, clinic_now = 30.0, 22.0       # visits a day (teaching)
    rate = 0.02                                # visits per incoming worker a day
    add = incoming * rate
    rows = [(1, clinic_now), (2, clinic_now + add), (3, clinic_now + add * 0.25)]
    csv("ch33-influx.csv", "case,visits", rows)
    lines = ["labour influx and the village clinic at the construction peak (teaching)",
             f"  peak workforce {peak}, local {local * 100:.0f} %: {incoming:.0f} people"
             f" arrive, against a village of {village}",
             f"  clinic: {clinic_now:.0f} visits a day now, capacity {clinic_cap:.0f}",
             f"  incoming workers at {rate} visits a day each: +{add:.1f} a day ->"
             f" {(clinic_now + add) / clinic_cap * 100:.0f} % of capacity",
             f"  with a site medic treating three in four: {(clinic_now + add * 0.25) / clinic_cap * 100:.0f} %",
             "  a camp of incoming workers is almost half the village's",
             "  size: clinic, water, rents, shops and the roads all feel",
             "  it - the influx plan counts each local service, pays for",
             "  the site's own medic, and asks the clinic, not assumes"]
    emit("q_influx", lines)


def security() -> None:
    guards, days = 18, 365
    guard_days = guards * days
    complaints = 3
    trained = 16
    lines = ["conduct of the security staff (synthetic year; non-tactical)",
             f"  guards {guards}; guard-days {guard_days:,}",
             f"  trained in the code of conduct and human rights: {trained} of {guards}"
             f" ({trained / guards * 100:.0f} %)",
             f"  conduct complaints from the community: {complaints}"
             f" = {complaints / guard_days * 1000:.2f} per 1,000 guard-days",
             "  every complaint goes through the grievance mechanism,",
             "  is investigated by someone outside the security chain,",
             "  and its outcome is reported; untrained guards do not",
             "  work until trained; force is never a tool against the",
             "  community, and public authorities' involvement follows",
             "  the law and the framework (ch 32 lesson H)"]
    emit("q_security", lines)


def local_claims() -> None:
    claimed_hire, claimed_buy = 0.45, 0.12
    resident = 0.36                   # resident more than 12 months before hiring
    invoices = 0.07                   # spend paid to suppliers registered locally
    lines = ["local hiring and buying: the claim against the evidence (synthetic)",
             "  measure                      claimed   with evidence   rule",
             f"  local hires                  {claimed_hire * 100:6.0f} %  {resident * 100:12.0f} %"
             "   resident > 12 months",
             f"  local purchases              {claimed_buy * 100:6.0f} %  {invoices * 100:12.0f} %"
             "   local invoices",
             "  the claims counted anyone with a local address and every",
             "  purchase through a local agent: the definitions are",
             "  written first, the evidence is kept, and only verified",
             "  numbers go to the village and the lenders"]
    emit("q_claims", lines)


def grazing_value() -> None:
    ha, animals_ha, inc = 3.1, 600 / 780, 0.12      # k u per animal a year
    yearly = ha * animals_ha * inc
    rate, years = 0.06, 25
    pv = yearly * (1 - (1 + rate) ** -years) / rate
    lines = ["the value of 3.1 ha of customary grazing lost (teaching)",
             f"  income it supported: {ha} ha x {animals_ha:.2f} animals/ha x {inc}"
             f" = {yearly:.2f} k u a year",
             f"  present value over {years} years at {rate * 100:.0f} %: {pv:.1f} k u",
             "  a one-off payment of the yearly loss would be far too",
             "  little; replacement land or an improved pasture keeps the",
             "  livelihood itself - whether compensation applies, its",
             "  basis and who receives it are set by the framework with",
             "  local experts and agreed with the families (lab G)"]
    emit("q_grazing", lines)


def dripline() -> None:
    width, strip = 4.6, 0.30                 # table width (2P), drip-line strip m
    conc = width / strip
    rain_mm = 25.0                           # a storm
    lines = ["rain concentrated at the drip lines of the PV tables (teaching)",
             f"  a {width} m wide table sheds its rain onto a strip of about {strip} m:"
             f" x{conc:.0f}",
             f"  a {rain_mm:.0f} mm storm lands on that strip as {rain_mm * conc:.0f} mm",
             "  bare, loose desert soil under the drip line gullies in a",
             "  few seasons - the posts lose cover and the access tracks",
             "  rut; gravel strips or vegetation under the drip lines",
             "  and a block graded to sheet, not channel, the water are",
             "  cheaper than repairs (erosion of the construction phase",
             "  and its sediment pond are in ch 29)"]
    emit("q_dripline", lines)


def smoke() -> None:
    d = datapack.load_hourly()
    wd = d["wd_100m_deg"].to_numpy()
    bx, by = 6500.0, 3500.0                                          # battery yard by the substation
    vx, vy = src.VILLAGE_CENTRE
    to_village = math.degrees(math.atan2(vx - bx, vy - by)) % 360
    from_dir = (to_village + 180) % 360                              # wind FROM here
    diff = np.abs((wd - from_dir + 180) % 360 - 180)
    share = float((diff <= 22.5).mean())
    sectors = np.arange(0, 360, 45)
    rows = []
    for s in sectors:
        dd = np.abs((wd - s + 180) % 360 - 180)
        rows.append((int(s), round(float((dd <= 22.5).mean()) * 100, 1)))
    csv("ch33-smoke.csv", "sector,share", rows)
    dist = math.hypot(vx - bx, vy - by)
    lines = ["how often smoke from a battery fire would blow to the village",
             f"  village centre {dist / 1000:.1f} km at {to_village:.0f} deg from the battery yard",
             f"  wind from {from_dir:.0f} +/- 22.5 deg carries smoke there:"
             f" {share * 100:.1f} % of the hours",
             "  share of hours (%) by the direction the wind comes from:",
             "  " + "  ".join(f"{s:3d}: {p:4.1f}" for s, p in rows[:4]),
             "  " + "  ".join(f"{s:3d}: {p:4.1f}" for s, p in rows[4:]),
             f"  the prevailing west and north-west winds ({rows[6][1] + rows[7][1]:.0f} % of the",
             "  hours) carry smoke east and south-east, away from the",
             f"  village; it goes there in about one hour in {1 / share:.0f} - rare,",
             "  but a fire lasts hours and the wind turns: the plan",
             "  assumes it can, and the message to the village (lesson E)",
             "  does not wait for the wind to decide"]
    emit("q_smoke", lines)


if __name__ == "__main__":
    lighting()
    influx()
    security()
    local_claims()
    grazing_value()
    dripline()
    smoke()
