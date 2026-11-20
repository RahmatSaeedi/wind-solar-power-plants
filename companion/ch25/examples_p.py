"""Chapter 25 - fourth round: the impedance chosen between fault current,
regulation and force; the HV neutral and the grid's earth faults; the
tap range from the voltage band; the transport mass; oil acceptance;
mineral oil or ester; the physics of an oil fire's radiation and of
draining the bund; the substation's control cables; and the transformer
trip matrix.

Run from the project root:   python -m companion.ch25.examples_p
Writes companion/ch25/expected/p_*.txt. Teaching values (A-326..A-330
extended). Fire separation and protection are decided by the fire
engineer and the authority; tests are named by purpose.
"""
from __future__ import annotations

import math

from companion.ch25 import sources as src
from companion.ch25.common import emit
from plantp import transformer as tr

M = src.MAIN


def impedance_choice() -> None:
    s_grid = 1196.0                     # MVA at the 132 kV bus (ch 23)
    lines = ["choosing the impedance: fault current, regulation, force (teaching):",
             "  uk %   33 kV fault, both T + converters kA   regulation % (0.95)   force x"]
    for uk in (8, 10, 12, 14, 16):
        s_t = M["s_mva"] / (uk / 100)
        s_bus = 1 / (1 / s_grid + 1 / (2 * s_t))
        ik = s_bus / (math.sqrt(3) * 33) + 2.7
        reg = tr.regulation_pct(0.004, uk / 100, 1.0, 0.95)
        lines.append(f"  {uk:4d}   {ik:37.1f}   {reg:19.1f}   {(12 / uk) ** 2:7.2f}")
    lines += ["  low impedance: small drop, but high fault current (the 25 kA",
              "  gear) and large forces; high impedance: the opposite and more",
              "  reactive power drawn - 10 to 14 % keeps the fault well under",
              "  25 kA and the regulation under about 6 %: 12 % is the basis,",
              "  confirmed by the fault study (ch 26) and the voltage study"]
    emit("p_impedance", lines)


def hv_neutral() -> None:
    e = 132e3 / math.sqrt(3)
    z1g, z0g = 132 ** 2 / 1196.0, 132 ** 2 / 1196.0 * 1.4
    z0t = 0.9 * 0.12 * 132 ** 2 / M["s_mva"]
    lines = ["the HV star point: earthed (YN) or not, seen by a 132 kV earth fault",
             f"  grid Z1 {z1g:.1f} ohm, Z0 {z0g:.1f} ohm; each transformer Z0 {z0t:.1f} ohm",
             "  plant star points earthed   earth-fault kA   share from the plant"]
    for n in (0, 1, 2):
        z0 = z0g if n == 0 else 1 / (1 / z0g + n / z0t)
        i = 3 * e / (2 * z1g + z0) / 1e3
        share = 0 if n == 0 else 1 - z0 / z0g
        lines.append(f"  {n:27d}   {i:14.1f}   {share:20.0%}")
    lines += ["  an earthed star point makes the plant a source of zero-",
              "  sequence current: the grid's earth faults grow and the",
              "  utility's earth-fault protection sees the plant - so the",
              "  utility decides whether the HV neutral is earthed, solid",
              "  or through an impedance (U-089), and the vector group",
              "  and neutral bushing follow that decision"]
    emit("p_neutral", lines)


def tap_range() -> None:
    lines = ["tap range from the voltage band (teaching; exporting, so the 33 kV",
             "  side sits above the HV side by the regulation):",
             "  HV voltage pu   rise %   HV tap % for 33 kV at 1.00 (as lesson A)"]
    need = []
    for v_hv in (0.90, 0.95, 1.05, 1.10):
        for reg in (0.0, 4.8):
            tap = (v_hv * (1 + reg / 100) - 1) * 100
            need.append(tap)
            lines.append(f"  {v_hv:13.2f}   {reg:6.1f}   {tap:+16.1f}")
    lines += [f"  needed from {min(need):+.1f} to {max(need):+.1f} %; the +/- 10 % in 1.25 %"
              " steps",
              "  covers the band except the corner of high grid voltage at",
              "  full export, where the plant absorbs reactive power (ch 20)",
              "  to pull the 33 kV down - the tap range follows the voltage",
              "  study"]
    emit("p_taps", lines)


def transport_mass() -> None:
    parts = [("oil (22 m3 x 0.88 t/m3)", 19.4), ("radiators and fans", 3.0),
             ("conservator and piping", 0.6)]
    m = M["mass_t"]
    lines = ["what comes off for transport (teaching breakdown):",
             f"  mass in service {m:.0f} t"]
    for name, t in parts:
        m -= t
        lines.append(f"    less {name:26s} {t:5.1f} t -> {m:5.1f} t")
    axles = 8
    lines += [f"  transport mass {m:.0f} t on a trailer of {axles} axles: {m / axles:.1f} t per axle",
              "  (plus the trailer's own mass, checked against the road and",
              "  bridge limits)",
              "  the tank travels filled with dry gas under pressure, with a",
              "  gauge and the impact recorder; the oil follows in tankers",
              "  and is processed on site to the maker's limits"]
    emit("p_transport", lines)


OIL = [("new oil, delivery", 75, 8, 0.01, "new"), ("after processing", 72, 6, 0.01, "new"),
       ("in service, year 8", 48, 22, 0.08, "service"), ("in service, year 15", 32, 35, 0.15, "service")]


def oil_tests() -> None:
    lim = {"new": (60, 10, 0.03), "service": (40, 25, 0.15)}
    lines = ["oil tests read against teaching limits (breakdown voltage kV min,",
             "  water mg/kg max, acidity mg KOH/g max):",
             "  sample                BDV   water   acidity   result"]
    for name, bdv, h2o, acid, kind in OIL:
        lb, lw, la = lim[kind]
        bad = [n for n, ok in (("BDV", bdv >= lb), ("water", h2o <= lw), ("acidity", acid < la)) if not ok]
        lines.append(f"  {name:20s} {bdv:5d}   {h2o:5d}   {acid:7.2f}   "
                     f"{', '.join(bad) + ' - act' if bad else 'ok'}")
    lines += ["  new oil is accepted to tighter limits than oil in service;",
              "  the trend of water and acidity tells when to dry or",
              "  regenerate the oil - the limits are the oil standard's and",
              "  the maker's, these are teaching values"]
    emit("p_oil", lines)


def ester() -> None:
    lines = ["mineral oil or natural ester (teaching properties and prices):",
             "  property                     mineral      natural ester",
             "  fire point C                     170               350",
             "  biodegradable                    slowly            readily",
             "  viscosity at 40 C (relative)     1                 ~4",
             "  paper ageing (relative)          1                 slower",
             "  price per m3 (relative)          1                 ~3"]
    for name, v in (("main transformer", M["oil_m3"]), ("PV unit transformer", 2.6)):
        lines.append(f"  extra fluid cost, {name:22s} about {v * 2 * 1.2:.0f} k u")
    lines += ["  (mineral oil taken at 1.2 k u/m3)",
              "  the ester's high fire point may let the fire design relax",
              "  separation or barriers - a decision of the fire engineer and",
              "  the authority, not of the fluid alone; its viscosity needs",
              "  a cooling design made for it (the maker's)"]
    emit("p_ester", lines)


def heat_flux() -> None:
    area, burn, dh, chi = 50.0, 0.039, 46e6, 0.30
    q_total = area * burn * dh
    lines = ["radiation from an oil pool fire (point-source physics, teaching):",
             f"  pool {area:.0f} m2, burning {burn} kg/(m2 s), 46 MJ/kg: {q_total / 1e6:.0f} MW;"
             f" radiated share {chi}",
             "  distance m   flux kW/m2"]
    for r in (8, 12, 16, 24):
        lines.append(f"  {r:10d}   {chi * q_total / (4 * math.pi * r * r) / 1e3:10.1f}")
    lines += ["  the flux falls with the square of the distance: either",
              "  distance or a wall keeps a neighbouring transformer and the",
              "  buildings below the level they can stand - which level,",
              "  which model and which measure are the fire engineer's and",
              "  the authority's decisions (ch 31); this is only the physics"]
    emit("p_heatflux", lines)


def drain() -> None:
    v, t_min = M["oil_m3"], 10.0
    q = v / (t_min * 60)
    lines = ["draining the bund to the separator tank (teaching):",
             f"  {v:.0f} m3 of oil in {t_min:.0f} min: {q * 1000:.0f} L/s",
             "  pipe mm   velocity m/s"]
    for d in (150, 200, 250):
        a = math.pi * (d / 1000) ** 2 / 4
        lines.append(f"  {d:7d}   {q / a:12.2f}")
    lines += ["  a burning pool drained fast stops feeding the fire: gravel",
              "  in the bund quenches flames, the pipe and the separator take",
              "  the oil (and the rain, lesson F) away - the separator",
              "  then keeps the oil from the drainage system"]
    emit("p_drain", lines)


def control_cables() -> None:
    signals, ct_circuits, vt_circuits, power = 56, 12, 4, 10
    cores_per_cable = 12
    signal_cables = math.ceil(signals * 2 / cores_per_cable)
    lines = ["control cables from the two main transformers to the control building",
             f"  signals {signals} (two cores each) -> {signal_cables} cables of"
             f" {cores_per_cable} cores",
             f"  CT circuits {ct_circuits} and VT circuits {vt_circuits}: own screened cables,"
             " 4 cores each",
             f"  power (fans, tap changer, heaters): {power} cables",
             f"  total {signal_cables + ct_circuits + vt_circuits + power} cables, about"
             f" {(signal_cables + ct_circuits + vt_circuits + power) * 80:,d} m on 80 m routes",
             "  CT and VT circuits run in their own cables (lesson D of",
             "  ch 24 and ch 26: separate cores for main and backup), and",
             "  every core is a row of the cable core list"]
    emit("p_cables", lines)


TRIPS = [("87T differential", "HV Q1, LV Q2, lockout"), ("64 restricted earth fault", "HV Q1, LV Q2, lockout"),
         ("63 gas relay, trip stage", "HV Q1, LV Q2, lockout"), ("pressure relief", "HV Q1, LV Q2, lockout"),
         ("26/49 oil and winding temperature", "HV Q1, LV Q2"), ("24 V/Hz", "HV Q1"),
         ("50/51 HV backup", "HV Q1, LV Q2"), ("50BF breaker failure (HV Q1)", "HV bus or line bay")]


def trip_matrix() -> None:
    lines = ["trip matrix of a main transformer (teaching):",
             "  function                          trips"]
    lines += [f"  {a:33s} {b}" for a, b in TRIPS]
    lock = sum("lockout" in b for _, b in TRIPS)
    lines += [f"  {lock} functions also set the lockout (86): the transformer stays",
              "  off until someone has looked - an internal fault must not be",
              "  re-energised by a reflex; the matrix is a drawing of its own,",
              "  tested trip by trip at commissioning (ch 26)"]
    emit("p_trips", lines)


if __name__ == "__main__":
    impedance_choice()
    hv_neutral()
    tap_range()
    transport_mass()
    oil_tests()
    ester()
    heat_flux()
    drain()
    control_cables()
    trip_matrix()
