"""Chapter 4, third part — blade aerofoil, sunlight through the air, skin effect, generator
speed, heat-sink chain, layout noise, stress concentration, buried cables, cathodic
protection, glass strength, solder fatigue, casting, machining, coating mass, transformer
winding, true position and ultrasonic thickness.

Run from the project root:   python -m companion.ch04.examples_deep
Writes companion/ch04/expected/s_*.txt and diagrams/data/ch04-s-*.csv.
Values marked "assumed" (A-069 .. A-074) are teaching values, not a design.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch04.common import csv, emit
from plantp import datapack, materials as mt, physics as ph, solar

W_ROTOR = 10.5 * 2 * math.pi / 60


def aerofoil() -> None:
    rho, v, a, r, chord, cl, cd = 1.05, 10.0, 1 / 3, 50.0, 2.0, 1.0, 0.01   # A-069
    w, phi = ph.inflow(v, a, W_ROTOR, r)
    q = 0.5 * rho * w ** 2
    lift, drag = q * chord * cl, q * chord * cd
    p = math.radians(phi)
    tang = lift * math.sin(p) - drag * math.cos(p)
    thrust = lift * math.cos(p) + drag * math.sin(p)
    tang_nodrag = lift * math.sin(p)
    emit("s_aerofoil", [
        f"blade section at r = {r:.0f} m, wind 10 m/s, induction 1/3, 10.5 rpm (A-069)",
        f"  axial {v * (1 - a):.2f} m/s, tangential omega r = {W_ROTOR * r:.1f} m/s",
        f"  relative speed W = {w:.1f} m/s, inflow angle phi = {phi:.2f} deg",
        f"  chord 2 m, C_L 1.0, C_D 0.01: lift {lift / 1e3:.2f} kN/m, drag {drag:.0f} N/m",
        f"  force along the rotation (drives torque): {tang:.0f} N/m",
        f"  force along the wind (thrust):            {thrust:.0f} N/m",
        f"  without drag the driving force would be {tang_nodrag:.0f} N/m: drag costs "
        f"{100 * (1 - tang / tang_nodrag):.0f} %",
        "  the section moves 8 x faster than the air reaching the rotor: the lift",
        "  points almost along the wind, and only a small part of it turns the rotor",
    ])


def sunlight() -> None:
    day = datapack.load_hourly("day_summer")
    hours = np.arange(24) + 0.5
    elev, _ = solar.sun_position(34.0, 174, solar.solar_time(hours, 174))
    elev = np.asarray(elev, dtype=float)
    lines = ["clear-sky beam: DNI = 1353 x 0.7^(AM^0.678), AM = 1 / sin(elevation)",
             "  (Meinel's empirical fit; solar constant today about 1361 W/m2)"]
    for e in (90, 60, 30, 15):
        lines.append(f"  elevation {e:2d} deg: air mass {float(ph.air_mass(e)):.2f}, model DNI "
                     f"{float(ph.meinel_dni(e)):4.0f} W/m2")
    k = int(np.argmax(elev))
    dni = day["dni_wm2"].to_numpy()
    lines.append(f"summer subset day (day 174), hour {k}: elevation {elev[k]:.1f} deg;")
    lines.append(f"  model {float(ph.meinel_dni(elev[k])):.0f} W/m2, data pack {dni[k]:.0f} W/m2")
    lines.append(f"  at 1200 m the air above is thinner (p/p0 = {877.2 / 1013.25:.3f});")
    lines.append("  a pressure-corrected air mass lowers the loss")
    emit("s_sunlight", lines)
    rows = []
    for h, e, d in zip(range(24), elev, dni):
        rows.append((h, f"{float(ph.meinel_dni(e)) if e > 3 else 0.0:.1f}", f"{d:.1f}"))
    csv("ch04-s-sun.csv", "hour,model,data", rows)


def skin_and_generator() -> None:
    lines = ["skin depth sqrt(2 rho / (omega mu0)) at 50 Hz:"]
    for name, rho in (("copper", 1.72e-8), ("aluminium", 2.82e-8)):
        lines.append(f"  {name:9s}: {ph.skin_depth(rho, 50) * 1000:.2f} mm")
    lines.append("R_ac / R_dc of an isolated round solid conductor (Bessel solution):")
    for area in (240, 630, 1000, 2000):
        r = math.sqrt(area / math.pi) / 1000
        lines.append(f"  copper {area:4d} mm2 (radius {r * 1000:5.1f} mm): "
                     f"{ph.ac_dc_ratio_round(r, 1.72e-8, 50):.3f}")
    lines.append("  very large conductors are split into insulated segments to use the core")
    emit("s_skin", lines)
    lines = ["synchronous speed n = 120 f / p at 50 Hz:"]
    for p in (4, 6, 8):
        lines.append(f"  {p} poles: {120 * 50 / p:.0f} rpm")
    lines += [f"  geared generator at 1155 rpm (a_torque) with 4 poles: slip "
              f"{100 * (1500 - 1155) / 1500:.0f} % below synchronous",
              f"  a direct-drive rotor at 10.5 rpm would need {120 * 50 / 10.5:.0f} poles for 50 Hz",
              "  with a full converter the generator frequency is free: the converter makes 50 Hz"]
    emit("s_generator", lines)


def heat_sink_and_noise() -> None:
    p_loss = 2000.0                                     # W per power module (A-070)
    r_jc, r_ch, r_ha = 0.020, 0.010, 0.015
    lines = ["power module losses 2 kW; R_jc 0.020, R_ch 0.010, R_ha 0.015 K/W (A-070)"]
    for t_air, scale, label in ((40.0, 1.0, "cabinet air 40 C"), (50.0, 1.0, "cabinet air 50 C"),
                                (50.0, 1.143, "50 C, 1200 m (R_ha x 1.143)")):
        tj = t_air + p_loss * (r_jc + r_ch + r_ha * scale)
        lines.append(f"  {label:28s}: junction {tj:.0f} C")
    lines.append("  the heat-sink-to-air step is where altitude and dust act; a 150 C limit")
    lines.append("    leaves little margin on a hot day, so the converter derates its current")
    emit("s_heatsink", lines)
    rng_x = np.arange(4) * 750.0
    rng_y = np.arange(3) * 1050.0
    turbines = [(x, y) for x in rng_x for y in rng_y]
    rec = (-800.0, 1050.0)
    d = np.array([math.hypot(x - rec[0], y - rec[1]) for x, y in turbines])
    lp = ph.spl_at_distance(105.0, d)
    total = ph.sum_levels_db(lp)
    order = np.argsort(d)
    emit("s_noise", [
        "12 turbines on a 3 x 4 grid (750 m x 1050 m, assumed); a house 800 m",
        "  west of the middle row; each 105 dB(A), spherical spreading only",
        f"  nearest turbine {d[order[0]]:.0f} m: {lp[order[0]]:.1f} dB(A); farthest "
        f"{d[order[-1]]:.0f} m: {lp[order[-1]]:.1f} dB(A)",
        f"  all twelve together: {total:.1f} dB(A)",
        f"  the three nearest alone: {ph.sum_levels_db(lp[order[:3]]):.1f} dB(A)",
        "  the nearest few turbines decide the level; distant ones add little",
    ])


def materials_b() -> None:
    emit("s_kt", [
        "stress concentration at a round hole in a wide plate under tension: Kt = 3",
        "  nominal 100 MPa -> 300 MPa at the edge of the hole",
        "  for fatigue the local stress counts: holes, door openings, weld toes and",
        "    sharp corners are where cracks start; generous radii and reinforcement help",
    ])
    r1 = ph.kennelly_resistance(1.0, 0.8, 0.05)
    w_per_m = 572.0 ** 2 * 0.125e-3                     # A-032 conductor, peak current
    lines = [f"buried cable, depth 0.8 m, diameter 50 mm: R_th = (rho / 2 pi) acosh(2u/D)",
             f"  peak loss of one feeder cable 572^2 x 0.125 milliohm/m = {w_per_m:.1f} W/m"]
    for rho_s, label in ((0.7, "moist soil"), (1.0, "design value (assumed)"), (2.5, "dried-out sand")):
        r = ph.kennelly_resistance(rho_s, 0.8, 0.05)
        lines.append(f"  {label:23s} rho {rho_s} K m/W: R_th {r:.2f} K m/W, soil rise "
                     f"{r * w_per_m:.0f} K")
    lines.append("  heat dries the soil around a loaded cable: the rating rests on the driest case")
    emit("s_soil", lines)
    _ = r1
    cap = 96485 * 2 / 65.38 / 3600 * 1000            # Ah per kg, zinc
    need = 0.5 * 20 * 8760
    mass = need / (cap * 0.95 * 0.85)
    emit("s_cathodic", [
        "sacrificial zinc anodes for 0.5 A over 20 years (assumed demand, A-071)",
        f"  zinc n F / M = {cap:.0f} Ah/kg (theory); efficiency 0.95, utilisation 0.85",
        f"  charge needed 0.5 A x 20 x 8760 h = {need:,.0f} Ah -> {mass:.0f} kg of zinc",
        "  the demand comes from coating quality and soil: a coated structure needs",
        "  far less; cathodic protection is designed and monitored by specialists",
    ])
    rows = []
    s = np.linspace(0, 160, 81)
    for x in s:
        rows.append((f"{x:.1f}", f"{1 - math.exp(-(x / 50.0) ** 7):.5f}",
                     f"{1 - math.exp(-(x / 150.0) ** 7):.5f}"))
    csv("ch04-s-glass.csv", "s,annealed,tempered", rows)
    emit("s_glass", [
        "brittle strength is statistical: P_f = 1 - exp(-(sigma / sigma0)^m) (A-072)",
        "  annealed glass sigma0 50 MPa, tempered glass sigma0 150 MPa, m = 7 (assumed)",
        f"  at 30 MPa: annealed {1 - math.exp(-(30 / 50) ** 7):.3f}, tempered "
        f"{1 - math.exp(-(30 / 150) ** 7):.1e}",
        f"  at 60 MPa: annealed {1 - math.exp(-(60 / 50) ** 7):.3f}, tempered "
        f"{1 - math.exp(-(60 / 150) ** 7):.4f}",
        "  tempering locks compression into the surface: a crack must first overcome it",
    ])
    beta = 2.0
    emit("s_solder", [
        "solder joint fatigue, Coffin-Manson N ~ (plastic strain range)^(-beta), beta 2",
        f"  strain ~ temperature swing: cycles to failure at 60 K vs 100 K swing: "
        f"x {(100 / 60) ** beta:.2f}",
        "  one daily cycle per year in the field = 365; a 200-cycle chamber test at a",
        "    larger swing stands in for many field years (acceleration factor)",
        "  the exponent comes from tests of the real joint; this is the idea only",
    ])


def processes() -> None:
    b = 2.5                                              # min per cm2, assumed (A-073)
    lines = ["Chvorinov's rule t = B (V/A)^2, B = 2.5 min/cm2 (assumed, A-073):"]
    for label, va in (("plate 50 mm thick", 2.5), ("plate 100 mm", 5.0), ("section 200 mm", 10.0)):
        lines.append(f"  {label:18s} V/A = {va:4.1f} cm: {b * va ** 2:6.1f} min to solidify")
    lines.append("  thick parts freeze last and shrink: risers feed them, and ultrasonic")
    lines.append("    testing looks there for shrinkage porosity")
    emit("s_casting", lines)
    area = math.pi / 4 * (0.6 ** 2 - 0.4 ** 2)
    v_c, f, d = 150.0, 0.4e-3, 2e-3
    lines = ["facing a ring flange 600 / 400 mm: cutting speed 150 m/min, feed 0.4 mm/rev",
             f"  face area {area:.3f} m2 -> time per pass area / (f v) = "
             f"{area / (f * v_c):.1f} min",
             f"  material removal rate v f d (2 mm depth) = {v_c * f * d * 1e6:.0f} cm3/min",
             "  a finer feed gives a smoother face (roughness ~ f^2) at the price of time"]
    emit("s_machining", lines)
    g_m2 = 85 * 7.14
    piles = 8000
    emit("s_coating", [
        f"zinc 85 micrometre x 7.14 g/cm3 = {g_m2:.0f} g/m2",
        f"  a pile with 2.4 m2 of surface carries {g_m2 * 2.4 / 1000:.2f} kg of zinc",
        f"  {piles:,} piles (assumed) carry {g_m2 * 2.4 * piles / 1e6:.1f} t of zinc",
        "  coating mass per area and thickness are two ways to state one requirement",
    ])
    n, l_turn, j = 175, 2.5, 3.0                          # A-074
    i = 100e6 / (3 * 33e3)
    a_cond = i / j * 1e-6
    length = n * l_turn
    rho75 = 1.72e-8 * (1 + 0.00393 * 55)
    r = rho75 * length / a_cond
    emit("s_winding", [
        f"LV winding of the export transformer: {n} turns of 2.5 m, 3 A/mm2 (A-074)",
        f"  rated phase current {i:.0f} A -> conductor {a_cond * 1e6:.0f} mm2",
        f"  conductor length {length:.0f} m, resistance at 75 C {r * 1000:.1f} milliohm",
        f"  load loss I^2 R per phase {i ** 2 * r / 1e3:.1f} kW, three phases {3 * i ** 2 * r / 1e3:.0f} kW",
        f"  copper mass {3 * 8960 * length * a_cond / 1000:.2f} t (LV winding only)",
        f"  at 2.5 A/mm2 instead of 3: loss x {2.5 / 3:.3f}, copper x {3 / 2.5:.2f}",
        "  a lower current density cuts the loss but adds copper: the Kelvin",
        "  trade-off of chapter 3 again, inside the transformer",
    ])


def inspection() -> None:
    holes = [(0.10, 0.12), (0.18, -0.20), (-0.05, 0.22), (0.21, 0.17)]
    lines = ["true position = 2 sqrt(dx^2 + dy^2), tolerance diameter 0.5 mm:"]
    for k, (dx, dy) in enumerate(holes, 1):
        tp = 2 * math.hypot(dx, dy)
        lines.append(f"  hole {k}: dx {dx:+.2f}, dy {dy:+.2f} mm -> {tp:.3f} mm "
                     f"{'accept' if tp <= 0.5 else 'reject'}")
    lines.append("  hole 4 fails though each coordinate is within +-0.25: position is a circle,")
    lines.append("    not a square, around the true location")
    emit("s_position", lines)
    v = 5920.0
    lines = ["ultrasonic thickness, longitudinal wave in steel about 5920 m/s:"]
    for t_us in (13.51, 12.80, 12.20):
        lines.append(f"  round-trip time {t_us:5.2f} microseconds -> {v * t_us * 1e-6 / 2 * 1000:.1f} mm")
    lines.append(f"  1 microsecond of timing error = {v * 1e-6 / 2 * 1000:.2f} mm of thickness")
    lines.append("  calibrate on a block of known thickness: the sound speed depends on the")
    lines.append("    material and temperature, and coatings add their own delay")
    emit("s_ut", lines)


def main() -> None:
    aerofoil()
    sunlight()
    skin_and_generator()
    heat_sink_and_noise()
    materials_b()
    processes()
    inspection()


if __name__ == "__main__":
    main()
