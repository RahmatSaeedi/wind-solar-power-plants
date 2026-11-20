"""Chapter 32, lab H (exercise 3): all-hazards emergency preparedness -
the scenarios and response levels of Plant P, the time budget of a
rescue from a nacelle by day and by night, communications coverage of
the turbine pads, a proportionate physical-security risk screen, and a
review of a synthetic remote-site rescue and access-control scenario
that finds its gaps in response time, competence, communications,
community and recovery.

Run from the project root:   python -m companion.ch32.lab_h
Writes companion/ch32/expected/h_*.txt and diagrams/data/ch32-rescue.csv.
Teaching values (A-375). Rescue and medical plans are written by
qualified providers; security measures are risk-based, rights-respecting
and set with local law; no tactical procedure is given.
"""
from __future__ import annotations

from companion.ch32 import sources as src  # noqa: F401  (puts plantp on the path)
from companion.ch32.common import csv, emit
from plantp import safety as sf

# [start: scenarios]
SCENARIOS = [  # (scenario, level, first response on site, outside help)
    ("medical emergency (illness)", 2, "first aider, AED", "ambulance"),
    ("electrical injury", 2, "isolate by plan, first aid", "ambulance"),
    ("person suspended in a harness", 2, "site rescue team", "ambulance"),
    ("injured person in a nacelle", 2, "site rescue team", "ambulance"),
    ("fire (any area, lesson C)", 3, "alarm, people, isolate",
     "fire service"),
    ("dust storm, lightning, heat wave", 1, "stop work, shelter", "-"),
    ("wadi flood at the substation", 2, "evacuate low ground",
     "civil defence"),
    ("access road blocked", 1, "second route, hold work", "road authority"),
    ("loss of communications", 1, "radio, satellite, stop work", "-"),
    ("oil or electrolyte spill", 1, "contain, report",
     "environment office"),
    ("intrusion or theft", 1, "report, do not confront", "police"),
    ("gate blocked by a protest", 1, "liaison officer, hold",
     "local authority"),
]
# [end: scenarios]


def scenarios() -> None:
    lines = ["scenarios and response levels (1 site, 2 local services, 3 major)"]
    for s, lv, on, out in SCENARIOS:
        lines += [f"  {s} - level {lv}",
                  f"      on site: {on}; outside: {out}"]
    lines += ["  the site's first response has limits it states: first aid,",
              "  not treatment; alarm and isolation, not firefighting; report",
              "  and record, never confront - beyond them, outside services"]
    emit("h_scenarios", lines)


def rescue() -> None:
    steps = [("alarm by radio, location confirmed", 2, 2),
             ("colleague starts first aid in the nacelle", 1, 1),
             ("rescue team reaches the tower", 6, 35),
             ("climb by service lift", 12, 12),
             ("assess, package, prepare descent", 15, 15),
             ("lower to the ground by rescue device", 10, 10)]
    amb = 10 + 35 / 60 * 60 + 10
    rows, lines = [], ["rescue from a nacelle: time budget (minutes, teaching)",
                       "  step                                        day   night"]
    tday = tnight = 0.0
    for k, (name, d, n) in enumerate(steps, 1):
        tday += d
        tnight += n
        rows.append((k, tday, tnight))
        lines.append(f"  {name:42s} {d:4d}  {n:5d}")
    csv("ch32-rescue.csv", "step,day,night", rows)
    lines += [f"  casualty on the ground after {tday:.0f} min by day, {tnight:.0f} by night",
              f"  ambulance at the tower after about {amb:.0f} min (mobilise 10,",
              "  35 km, access 10); hospital 45 min further",
              "  by day the casualty is down before the ambulance arrives;",
              "  by night the on-call team adds half an hour. The plan's",
              "  answer is not a faster formula: two trained people on",
              "  every crew, rescue kit in each nacelle, and night work",
              "  only with the team on site - with times agreed with the",
              "  medical provider, who sets what is acceptable"]
    emit("h_rescue", lines)


def comms() -> None:
    pads = {f"T{k:02d}": True for k in range(1, 13)}
    for k in ("T05", "T07", "T08", "T11"):
        pads[k] = False
    gaps = [p for p, ok in pads.items() if not ok]
    lines = ["communications at the twelve turbine pads (survey, synthetic)",
             f"  mobile coverage missing at {len(gaps)}: {', '.join(gaps)}",
             "  site radio reaches all pads; one repeater serves T07-T08",
             "  fallback order: site radio -> satellite phone in each duty",
             "  vehicle -> runner to the substation; a crew with neither",
             "  radio nor satellite phone does not start work at a gap pad",
             f"  loss of the repeater leaves T07 and T08 with satellite only"]
    emit("h_comms", lines)


def security() -> None:
    risks = [("cable theft (copper earth, spares)", 4, 3,
              "aluminium where allowed, marked cable, stores locked"),
             ("module theft from the array edge", 2, 2,
              "fasteners, records, community links"),
             ("intrusion at the substation", 2, 5,
              "fence, signs, locks, alarm to control room"),
             ("vandalism or stone throwing", 3, 2,
              "community relations, quick repair"),
             ("arson of grass near the array", 1, 4,
              "firebreaks, patrols with the community"),
             ("theft by insiders", 3, 2,
              "access badges, stores control, audits")]
    lines = ["physical-security risk screen (proportionate, teaching)",
             "  threat                                L  S  score  band"]
    for t, lk, sv, ctl in sorted(risks, key=lambda r: -r[1] * r[2]):
        s = sf.risk_score(lk, sv)
        lines += [f"  {t:37s} {lk}  {sv}  {s:5d}  {sf.risk_band(s)}",
                  f"      measures: {ctl}"]
    lines += ["  the measures are design, records and relations first;",
              "  detection reports to the control room and the police;",
              "  security staff follow a conduct code, are trained in it",
              "  and never act beyond what law and the lenders allow (G)"]
    emit("h_security", lines)


# [start: review]
SCENARIO = dict(  # the synthetic exercise: a winter night at T07
    time="22:40", place="T07 nacelle", casualty="hand crushed, conscious",
    crew=2, crew_rescue_trained=1, on_call_team_min=40,
    mobile=False, radio_repeater_ok=False, satellite_phone_in_vehicle=False,
    road_to_town="flooded at the wadi crossing", second_route_known=False,
    gate="unmanned", unknown_vehicle_at_gate=True, visitor_log_complete=False,
    village_told=False, debrief_planned=False)
# [end: review]


def review() -> None:
    s = SCENARIO
    gaps = []
    if s["crew_rescue_trained"] < 2:
        gaps.append(("competence", "one rescuer on the crew: no one to rescue the rescuer"))
    if s["on_call_team_min"] > 30:
        gaps.append(("response time",
                     f"on-call team {s['on_call_team_min']} min at night"))
    if not (s["mobile"] or s["radio_repeater_ok"] or s["satellite_phone_in_vehicle"]):
        gaps.append(("communications", "no working link from T07 at all"))
    if s["road_to_town"] != "open" and not s["second_route_known"]:
        gaps.append(("response time", "ambulance route flooded, no second route"))
    if s["unknown_vehicle_at_gate"] and not s["visitor_log_complete"]:
        gaps.append(("access control", "unknown vehicle, incomplete visitor log"))
    if s["gate"] == "unmanned":
        gaps.append(("access control", "no one to meet the ambulance at the gate"))
    if not s["village_told"]:
        gaps.append(("community", "village not told of the flooded road and night traffic"))
    if not s["debrief_planned"]:
        gaps.append(("recovery", "no debrief or support for the crew planned"))
    lines = [f"exercise review: {s['casualty']} at {s['place']}, {s['time']}",
             f"  gaps found: {len(gaps)}"]
    for cat, g in gaps:
        lines.append(f"  {cat:15s} {g}")
    lines += ["  each gap gets an owner and a fix in the emergency plan;",
              "  the unknown vehicle is reported to the control room and",
              "  the police and recorded - no one goes to challenge it;",
              "  the review prescribes no security tactics"]
    emit("h_review", lines)


def programme() -> None:
    rows = [("table-top of one scenario", "quarterly", "managers, control room"),
            ("rescue drill at height", "monthly per team", "rescue teams"),
            ("evacuation and muster", "twice a year", "everyone on site"),
            ("full exercise with services", "yearly", "fire, ambulance, police"),
            ("communications test", "weekly", "control room")]
    lines = ["the exercise programme (teaching frequencies)",
             "  exercise                         how often           who"]
    for e, f, w in rows:
        lines.append(f"  {e:32s} {f:18s}  {w}")
    lines += ["  each exercise ends with findings, owners and dates, and",
              "  the next one tests whether those fixes worked"]
    emit("h_programme", lines)


if __name__ == "__main__":
    scenarios()
    rescue()
    comms()
    security()
    review()
    programme()
