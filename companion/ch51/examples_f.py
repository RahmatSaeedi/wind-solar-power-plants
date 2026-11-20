"""Chapter 51, lessons F (auxiliary systems), G (fire readiness), H (water
stewardship) and K (export assets): the station battery's autonomy and the
diesel's fuel, fire tests against their intervals, water metered against
the model and cleaning decided by measured recovery, line patrols and
vegetation, and outage requests against the network owner's notice.

Run from the project root:   python -m companion.ch51.examples_f
Writes companion/ch51/expected/f_*.txt, g_*.txt, h_*.txt and k_*.txt.
"""
from __future__ import annotations

from companion.ch51 import sources as src
from companion.ch51.common import emit
from plantp import operations


def auxiliaries() -> dict:
    a = src.AUX_OP
    hours = operations.autonomy_h(a["battery_kwh"], a["load_kw"])
    run_h = sum(h for _, h in a["diesel_runs"])
    fuel = run_h * a["fuel_l_h"]
    longest = max(h for _, h in a["diesel_runs"])
    lines = ["station service in the first year",
             f"  110 V battery {a['battery_kwh']:.0f} kWh, DC load {a['load_kw']} kW, 20 % "
             f"kept: {hours:.1f} h of autonomy",
             f"  diesel ran {len(a['diesel_runs'])} times, {run_h:.1f} h in all; longest "
             f"{longest} h",
             f"  fuel used {fuel:.0f} L of a {a['tank_l']:.0f} L tank; the tank holds "
             f"{a['tank_l'] / a['fuel_l_h']:.0f} h",
             "  the six-hour run (day 150, both feeds lost) was the longest",
             "  supply outage: the battery alone would have carried the",
             "  DC loads; the diesel carried the HVAC and the chargers -",
             "  refill is ordered at half a tank, not when it is empty"]
    emit("f_aux", lines)
    return dict(hours=hours, run_h=run_h, fuel=fuel)


def fire_tests() -> list:
    rows = []
    for k, (iv, last, today) in src.FIRE_TESTS.items():
        age = today - last
        rows.append((k, iv, age, age > iv))
    over = [r for r in rows if r[3]]
    lines = ["fire-system inspections and tests against their intervals (day 365)",
             "  system                           interval d  since last d"]
    lines += [f"  {k:32s} {iv:10d}  {age:12d}" + ("  OVERDUE" if o else "")
              for k, iv, age, o in rows]
    lines += [f"  {len(over)} overdue: each is an impairment until done - with an",
              "  owner, a compensating measure and a notice (ch 32, ch 49);",
              "  the detection loops are the most overdue, and they are the",
              "  ones every other function depends on"]
    emit("g_tests", lines)
    return over


def water() -> dict:
    rows = [(m, a, b, (a - b) / b) for m, (a, b) in src.WATER_MONTHS.items()]
    over = [r for r in rows if r[3] > 0.10]
    lines = ["water metered against the ch 29 model, first half-year (m3)",
             "  month  metered  modelled  difference"]
    lines += [f"  {m:5d}  {a:7d}  {b:8d}  {x:+10.0%}" for m, a, b, x in rows]
    lines += [f"  months more than 10 % over: {', '.join(str(r[0]) for r in over)}",
              "  February's 14 % has no recorded cause and is investigated",
              "  (a leak, a meter); April's 27 % is an extra wash after a dust",
              "  storm: the cleaning trigger fired as designed (ch 10); the model is",
              "  updated with the measured washes, and the well's share is",
              "  watched against the drought trigger of ch 29"]
    emit("h_water", lines)
    return dict(over=[r[0] for r in over])


def wash_value(recovery_mwh: float = 46.0, price: float = 50.0, cost_u: float = 1800.0,
               water_m3: float = 109.2, scarce_price: float = 12.0) -> dict:
    value = recovery_mwh * price
    normal = value - cost_u
    scarce = value - cost_u - water_m3 * scarce_price
    lines = ["one wash of the whole PV plant: measured recovery against its cost",
             f"  recovered {recovery_mwh} MWh until the next wash at {price:.0f} u/MWh: "
             f"{value:,.0f} u",
             f"  wash cost {cost_u:,.0f} u: net {normal:+,.0f} u",
             f"  in a drought, water at {scarce_price:.0f} u/m3 ({water_m3} m3): net "
             f"{scarce:+,.0f} u",
             "  the recovery is measured (the cleaned reference cell of",
             "  ch 37), not assumed; in a drought the trigger moves to a",
             "  higher soiling level, and the decision is logged with both"]
    emit("h_wash", lines)
    return dict(normal=normal, scarce=scarce)


def patrol() -> dict:
    late = [k for k, (d, _) in src.LINE_PATROL.items() if 365 - d > src.PATROL_DAYS]
    close = [(k, c) for k, (_, c) in src.LINE_PATROL.items() if c < src.CLEARANCE_M]
    lines = [f"132 kV line: patrols (every {src.PATROL_DAYS} days) and vegetation clearance",
             f"  (teaching minimum {src.CLEARANCE_M} m) on day 365"]
    lines += [f"  {k:8s} last patrol day {d:3d}  clearance {c} m"
              + ("  LATE" if k in late else "") + ("  CLOSE" if c < src.CLEARANCE_M else "")
              for k, (d, c) in src.LINE_PATROL.items()]
    lines += ["  T05-T08 and T13-T18 are both late and inside the clearance:",
              "  the trees grew while nobody looked; the cutting is done",
              "  under the network owner's outage and the landowner's",
              "  access agreement (ch 49 corridor), and recorded per span"]
    emit("k_patrol", lines)
    return dict(late=late, close=[k for k, _ in close])


def outages() -> list:
    short = [(w, n - r, need) for w, r, n, need in src.OUTAGE_REQ if n - r < need]
    lines = ["outage requests to the network owner against its notice period"]
    lines += [f"  {w:28s} {n - r:3d} days notice (needs {need})"
              + ("  SHORT" if n - r < need else "") for w, r, n, need in src.OUTAGE_REQ]
    lines += [f"  {len(short)} requests short: the vegetation outage waits for the",
              "  network owner's next window - the trees keep growing",
              "  meanwhile; the yearly outage plan is agreed in advance and",
              "  the urgent ones are the exception"]
    emit("k_outages", lines)
    return short


if __name__ == "__main__":
    auxiliaries()
    fire_tests()
    water()
    wash_value()
    patrol()
    outages()
