"""Chapter 51, integrated Plant P examples: three numbers by hand, the
first-year operating review and the operating basis D-055.

Run from the project root:   python -m companion.ch51.integrated
Writes companion/ch51/expected/int_*.txt.
"""
from __future__ import annotations

from companion.ch20 import sources as s20
from companion.ch51 import sources as src
from companion.ch51.common import emit
from plantp import operations


def by_hand() -> dict:
    eta = s20.LIMITS["eta"]
    floor = s20.LIMITS["e_min"] + 5.0 / eta
    room = (s20.LIMITS["e_max"] - 30.0) / eta
    a = src.AUX_OP
    hours = operations.autonomy_h(a["battery_kwh"], a["load_kw"])
    lines = ["three numbers by hand, checked by the scripts",
             f"  service floor: 4 + 5 / {eta:.3f} = {floor:.1f} MWh",
             f"  room to charge at 30 MWh: (36 - 30) / {eta:.3f} = {room:.1f} MWh",
             f"  station battery: 44 x 0.8 / 4.6 = {hours:.1f} h"]
    emit("int_hand", lines)
    return dict(floor=floor, room=room, hours=hours)


def review() -> dict:
    items = {
        "roles covered on every shift": False,
        "handovers complete": False,
        "procedures reviewed within a year": False,
        "events reported within a day": False,
        "settlement data validated before submission": True,
        "service availability at its target": False,
        "fire tests within their intervals": False,
        "water within 10 % of the model, causes known": False,
        "line patrols and clearances in date": False,
        "commitments on time": False,
        "asset register matching SCADA": False,
        "exercises done as planned": False,
    }
    ok = sum(items.values())
    lines = ["first-year operating review: does the operation run on its records?"]
    lines += [f"  [{'x' if v else ' '}] {k}" for k, v in items.items()]
    lines += [f"  {ok} of {len(items)}: the plant ran and exported all year; the",
              "  records that prove how it was run lag behind it - each open",
              "  line has its lesson in this chapter, an owner and a date",
              "  for the second year"]
    emit("int_review", lines)
    return dict(ok=ok, total=len(items))


def basis() -> None:
    lines = ["D-055 operating basis",
             "  1 every role covered on every shift, checked role by role;",
             "    handovers by checklist; an hourly log round",
             "  2 the day planned from the forecast with its version; plans",
             "    changed on updates and notices, decisions logged with who",
             "    was told; learning recorded the next day",
             "  3 lost energy recorded by cause; abnormal events by procedure",
             "    (reviewed yearly), permits checked by isolation point",
             "  4 settlement data validated and flagged before submission;",
             "    schedules and reserves by written rules, not hour by hour",
             "  5 services only within approved capability; suspended and",
             "    reported when not deliverable",
             "  6 auxiliaries, fire tests, water and export assets run on",
             "    their intervals, with impairments and notices",
             "  7 commitments with owners, reported; asset register updated",
             "    by every change; work orders closed only with asset, code",
             "    and test record",
             "  8 exercises as planned; incidents and near misses closed with",
             "    lessons",
             "  open: the operator's procedures and the grid operator's",
             "    operating instructions; market or contract rules (U-132)"]
    emit("int_basis", lines)


if __name__ == "__main__":
    by_hand()
    review()
    basis()
