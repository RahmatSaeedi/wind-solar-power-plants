"""Chapter 8 - more lessons: interior-magnet torque and field weakening,
a two-node thermal model through a gust, an insulation-resistance trend,
bearing life under the real load spectrum, rotor speed rise during a grid
dip, reading a nameplate, identifying induction-motor parameters from
tests, and the fault contribution of the whole plant.

Run from the project root:   python -m companion.ch08.examples_more2
Writes companion/ch08/expected/y_*.txt and diagrams/data/ch08-*.csv.
Teaching values A-111, A-114, A-116, A-130 .. A-135 (fictional).
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch08.common import csv, emit
from companion.ch08.lab_d import generator_year
from plantp import machines as m

S3 = math.sqrt(3)


def ipm() -> None:
    psi, ld, lq, poles = 0.9, 0.20e-3, 0.28e-3, 6                  # A-130
    pp = poles / 2
    i_s = 6000.0                                                    # peak A
    best = (0.0, 0.0)
    for beta in np.radians(np.arange(0, 90.1, 0.5)):
        i_d, i_q = -i_s * math.sin(beta), i_s * math.cos(beta)
        t = 1.5 * pp * (psi * i_q + (ld - lq) * i_d * i_q)
        if t > best[0]:
            best = (t, math.degrees(beta))
    t0 = 1.5 * pp * psi * i_s
    emit("y_ipm", [
        f"interior-magnet machine (A-130): psi {psi} Wb, L_d {ld * 1e3:.2f} mH, "
        f"L_q {lq * 1e3:.2f} mH, {poles} poles",
        "  T = 1.5 (p/2) [psi i_q + (L_d - L_q) i_d i_q]",
        f"  current 6000 A peak, all in q: T {t0 / 1e3:.1f} kN m",
        f"  best angle {best[1]:.1f} deg into negative d: T {best[0] / 1e3:.1f} kN m "
        f"(+{100 * (best[0] / t0 - 1):.1f} %)",
        "  the reluctance torque adds to the magnet torque: more torque per",
        "  ampere and less magnet; the converter must know L_d and L_q",
    ])


def field_weakening() -> None:
    psi, ld, poles = 1.553, 0.20e-3, 6                             # A-111/A-130
    v_ph_pk = 1100 / S3 * 0.95                                      # A-131
    lines = [f"PM generator, psi {psi} Wb; converter limit about {v_ph_pk:.0f} V "
             "peak phase (A-131):"]
    for n in (900, 1155, 1300, 1450):
        w_e = 2 * math.pi * n * poles / 120
        e_pk = w_e * psi
        need = max(0.0, (e_pk - v_ph_pk) / (w_e * ld))
        lines.append(f"  {n} rpm: EMF {e_pk:5.0f} V peak; i_d needed "
                     f"{-need + 0.0:7.0f} A peak")
    lines += ["  above about 1240 rpm the EMF exceeds the limit: a negative i_d",
              "  cancels part of the magnet flux; if the converter trips at",
              "  speed, nothing holds the EMF down (section D, overspeed)"]
    emit("y_fieldweak", lines)


def thermal2() -> None:
    c_w, c_c = 1.6e6, 9.0e6                                         # J/K, A-132
    g_wc, g_ca = 2400.0, 6000.0                                     # W/K
    dt = 10.0
    t = np.arange(0, 3 * 3600 + dt, dt)
    p_cu = np.where((t > 3600) & (t < 3600 + 900), 1.3 ** 2, 1.0) * 63.5e3
    p_fe = np.full_like(t, 40e3)
    tw, tc = 40.0 + 63.5e3 / g_wc + 103.5e3 / g_ca, 40.0 + 103.5e3 / g_ca
    rows, tw_max = [], tw
    for k, tt in enumerate(t):
        q_wc = g_wc * (tw - tc)
        tw += dt * (p_cu[k] - q_wc) / c_w
        tc += dt * (p_fe[k] + q_wc - g_ca * (tc - 40.0)) / c_c
        tw_max = max(tw_max, tw)
        if k % 6 == 0:
            rows.append((f"{tt / 60:.0f}", f"{tw:.2f}", f"{tc:.2f}"))
    emit("y_thermal2", [
        "two-node model, winding and core, coolant 40 C (A-132):",
        f"  steady state: winding {40 + 63.5e3 / g_wc + 103.5e3 / g_ca:.1f} C, core "
        f"{40 + 103.5e3 / g_ca:.1f} C",
        f"  a 15-min gust at 130 % current (copper loss x 1.69): winding peaks at "
        f"{tw_max:.1f} C",
        f"  the steady state at 130 % would be "
        f"{40 + 1.69 * 63.5e3 / g_wc + (40e3 + 1.69 * 63.5e3) / g_ca:.1f} C: the "
        "short gust",
        "  does not reach it; thermal mass is what makes short overloads "
        "acceptable",
    ])
    csv("ch08-gust.csv", "t_min,tw,tc", rows)


def ir_trend() -> None:
    rng = np.random.default_rng(17)                                 # A-133
    years = np.arange(0, 10.5, 0.5)
    temp = 25 + 10 * np.sin(2 * np.pi * years) + rng.normal(0, 3, len(years))
    true40 = 2000 * np.exp(-0.08 * years)
    true40[years >= 8] *= np.exp(-0.9 * (years[years >= 8] - 7.5))
    meas = true40 * 2 ** ((40 - temp) / 10) * np.exp(rng.normal(0, 0.08, len(years)))
    corr = meas * 2 ** ((temp - 40) / 10)
    fit = np.polyfit(years[years < 7.6], np.log(corr[years < 7.6]), 1)
    pred = np.exp(np.polyval(fit, years))
    drop = corr / pred
    first = years[np.argmax(drop < 0.6)]
    lines = ["insulation resistance of one generator every six months (A-133):",
             f"  raw readings range {meas.min():,.0f} to {meas.max():,.0f} Mohm "
             "(temperature swings it)",
             f"  corrected to 40 C and fitted on years 0-7.5: decline "
             f"{100 * (1 - math.exp(fit[0])):.1f} %/yr",
             f"  first reading below 60 % of the trend: year {first:.1f}",
             "  the raw values hide this: a summer reading looks low, a winter",
             "  one high; correct for temperature, then look at the trend"]
    emit("y_irtrend", lines)
    csv("ch08-ir.csv", "year,raw,corr,trend",
        [(f"{a:.1f}", f"{b:.0f}", f"{c:.0f}", f"{d:.0f}")
         for a, b, c, d in zip(years, meas, corr, pred)])


def bearing_spectrum() -> None:
    p_gen, _ = generator_year()
    load = p_gen / 5.13e6
    run = load > 0
    p_rel = 0.4 + 0.6 * load[run]                 # bearing load share, A-134
    p_eq = (np.mean(p_rel ** 3)) ** (1 / 3)
    speed = np.clip(600 + 555 * np.sqrt(load[run]), 600, 1155)
    rev = (speed * 60).sum()
    l10_rated = 12 ** 3 * 1e6 / (1155 * 60)
    life_years = (12 / p_eq) ** 3 * 1e6 / (rev / 1.0)
    emit("y_bearing", [
        "bearing load = 40 % fixed (weight, magnetic pull) + 60 % with load "
        "(A-134)",
        f"  equivalent load over the data-pack year {p_eq:.3f} of the rated-load "
        "value",
        f"  revolutions per year {rev / 1e6:,.0f} million (speed follows the wind)",
        f"  C/P 12 at rated: {l10_rated:,.0f} h at rated speed;",
        f"  with the real spectrum about {life_years:.1f} years",
        "  the load spectrum, not the rated point, sets the life (Miner-type "
        "rule)",
    ])


def ride_through() -> None:
    e_k = 32.2e6                                                    # chapter 4
    lines = ["grid dip: the converter cannot export, the rotor keeps its 5 MW "
             "input:"]
    for dur in (0.15, 0.5, 1.0):
        de = 5.0e6 * dur
        rise = math.sqrt(1 + de / e_k) - 1
        lines.append(f"  {1000 * dur:5.0f} ms: {de / 1e6:.2f} MJ into a rotor "
                     f"holding {e_k / 1e6:.1f} MJ -> speed +{100 * rise:.1f} %")
    lines += ["  a chopper resistor in the DC link burns the energy or the",
              "  pitch reduces the input; the drivetrain sees a torque step",
              "  that the gearbox and coupling must withstand (chapters 9, 11)"]
    emit("y_ridethrough", lines)


def nameplate() -> None:
    plate = {"P": 30.0, "U": 400.0, "I": 54.0, "pf": 0.85, "eff": 0.947,
             "n": 1475.0, "f": 50.0}                                # A-135
    p_in = plate["P"] / plate["eff"]
    i_calc = p_in * 1e3 / (S3 * plate["U"] * plate["pf"])
    s = (1500 - plate["n"]) / 1500
    t = m.torque_nm(plate["P"] * 1e3, plate["n"])
    emit("y_nameplate", [
        "motor nameplate (A-135): 30 kW, 400 V, 54 A, pf 0.85, eff 94.7 %,",
        "  1475 rpm, 50 Hz",
        f"  check 1: input {p_in:.2f} kW -> current {i_calc:.1f} A (plate 54 A)",
        f"  check 2: 4 poles (1500 rpm synchronous), slip {100 * s:.2f} %",
        f"  check 3: rated torque {t:.0f} N m",
        "  the plate is self-consistent; an inconsistent plate is a question",
        "  for the supplier, not something to 'correct' quietly",
    ])


def im_tests() -> None:
    v_ll = 400.0                                                    # A-135
    nl_v, nl_i, nl_p = 400.0, 22.6, 1050.0
    lr_v, lr_i, lr_p = 70.0, 54.0, 1950.0
    r1 = 0.09
    z_lr = lr_v / S3 / lr_i
    r_lr = lr_p / (3 * lr_i ** 2)
    x_lr = math.sqrt(z_lr ** 2 - r_lr ** 2)
    r2 = r_lr - r1
    x1 = x2 = x_lr / 2
    z_nl = nl_v / S3 / nl_i
    xm = z_nl - x1
    p_rot = nl_p - 3 * nl_i ** 2 * r1
    emit("y_imtests", [
        "induction-motor tests (A-135): no load 400 V, 22.6 A, 1050 W;",
        "  locked rotor 70 V, 54 A, 1950 W; stator resistance 0.090 ohm/phase",
        f"  locked rotor: |Z| {z_lr:.3f}, R {r_lr:.3f}, X {x_lr:.3f} ohm -> R2 "
        f"{r2:.3f}, X1 = X2 = {x1:.3f}",
        f"  no load: |Z| {z_nl:.2f} ohm -> X_m about {xm:.2f} ohm; core and "
        f"friction {p_rot:.0f} W",
        "  model A-114: X1 0.33, X2 0.35, X_m 10.0 ohm: reactances agree",
        "  within about 5 %; but R2 0.133 against 0.075: at standstill the",
        "  rotor current has 50 Hz and crowds into the bar tops (deep bar),",
        "  so the locked-rotor test overstates the running R2; a reduced-",
        "  frequency test or the rated slip gives the running value",
    ])


def plant_fault() -> None:
    i_pv = 5.0e6 / (S3 * 33e3) * 1.1 * 10                          # A-117
    i_wt = 5.0e6 / (S3 * 33e3) * 1.1 * 12
    i_grid = 8.75e3
    emit("y_plantfault", [
        "fault at the 33 kV bus of Plant P (chapter 7 and A-117):",
        f"  grid {i_grid / 1e3:.2f} kA; 10 PV inverters {i_pv:.0f} A; 12 turbines "
        f"{i_wt:.0f} A",
        f"  units add {100 * (i_pv + i_wt) / i_grid:.0f} % to the grid's "
        "contribution",
        "  a plant of synchronous machines of the same size would add about",
        f"  {110e6 / (S3 * 33e3) / 0.2 / 1e3:.1f} kA (x_d'' 0.2 on 110 MVA): "
        "protection must work with less",
    ])


# [start: pipeline]
def size_pm_machine(p_shaft, n_rpm, poles, d_over_l, j, v_ll=690.0):
    """Conceptual sizing of a surface-PM generator (A-136 teaching values).
    Returns a dict of dimensions, current, masses and losses."""
    sigma, b1, br, g = 40e3, 0.9, 1.2, 0.004      # Pa, T, T, m air gap
    end = 1.2                                     # end winding, m per side
    t = m.torque_nm(p_shaft, n_rpm)
    vr = t / (2 * sigma)
    d = (4 * vr * d_over_l / math.pi) ** (1 / 3)
    length = d / d_over_l
    f = n_rpm * poles / 120
    k_ac = 1 + 0.012 * f                          # eddy currents in bars
    phi = 2 / math.pi * b1 * math.pi * d * length / poles
    n_turns = (v_ll / S3) / (4.44 * f * phi * 0.95)
    a_rms = math.sqrt(2) * sigma / b1             # electric loading
    i_ph = a_rms * math.pi * d / (6 * n_turns)
    area = i_ph / j
    l_turn = 2 * (length + end)
    rho95 = 1.72e-8 * (234.5 + 95) / (234.5 + 20)
    r_ph = rho95 * n_turns * l_turn / area
    p_cu = k_ac * 3 * i_ph ** 2 * r_ph
    m_cu = 3 * n_turns * l_turn * area * 8960
    h_m = b1 * 1.05 * g / (br - b1)               # magnet thickness
    m_mag = math.pi * d * length * h_m * 0.8 * 7500
    d_o = d + 2 * (0.35 * math.pi * d / poles + 0.08)   # yoke + slots
    m_fe = math.pi / 4 * (d_o ** 2 - d ** 2) * length * 0.95 * 0.85 * 7650
    p_fe = m_fe * 5.0 * 1.3 * (f / 50) ** 1.5     # W/kg, building 1.3
    return {"T": t, "D": d, "L": length, "f": f, "N": n_turns, "I": i_ph,
            "P_cu": p_cu, "P_fe": p_fe, "m_cu": m_cu, "m_mag": m_mag,
            "m_fe": m_fe}
# [end: pipeline]


def pipeline() -> None:
    lines = ["conceptual sizing pipeline (A-136), shaft 5.16 MW after the "
             "gearbox:"]
    cost = {"m_cu": 9.0, "m_mag": 60.0, "m_fe": 1.5}               # u/kg
    for name, n, poles, dl, j in (("geared HS 1155 rpm", 1155.0, 6, 0.73, 4.5e6),
                                  ("geared MS 420 rpm", 420.0, 24, 1.0, 4.0e6),
                                  ("direct drive 10.5 rpm", 10.5, 120, 5.0, 2.5e6)):
        r = size_pm_machine(5.16e6, n, poles, dl, j)
        mass = r["m_cu"] + r["m_mag"] + r["m_fe"]
        money = sum(r[k] * v for k, v in cost.items())
        lines.append(f"  {name}: D {r['D']:.2f} m, L {r['L']:.2f} m, "
                     f"{r['f']:.1f} Hz, N {r['N']:.1f}, J {j / 1e6:.1f} A/mm2")
        lines.append(f"    copper {r['m_cu'] / 1e3:5.2f} t, magnet "
                     f"{r['m_mag'] / 1e3:5.2f} t, core {r['m_fe'] / 1e3:5.2f} t; "
                     f"active {mass / 1e3:5.1f} t")
        lines.append(f"    losses: copper {r['P_cu'] / 1e3:5.1f} kW, core "
                     f"{r['P_fe'] / 1e3:5.1f} kW; materials {money / 1e3:,.0f} k u")
    lines += ["A-111 assumed 63.5 kW copper and 39.7 kW core at rating: the",
              "  pipeline lands near both for the geared machine, a cross-check",
              "  of two independent sets of teaching numbers; the direct drive",
              "  buys its low current density with many tonnes of copper"]
    emit("y_pipeline", lines)


def ump() -> None:
    b, d, length = 0.9, 0.79, 1.08                                  # pipeline
    mu0 = 4e-7 * math.pi
    pressure = b ** 2 / (2 * mu0)
    area_half = math.pi * d * length / 2
    lines = [f"magnetic pressure B^2 / (2 mu0) at {b} T: {pressure / 1e3:.0f} kPa "
             "on the rotor surface",
             f"  half the rotor surface {area_half:.2f} m2: "
             f"{pressure * area_half / 1e3:,.0f} kN outwards,",
             "  balanced by the other half when the gap is uniform"]
    for ecc in (0.05, 0.10, 0.20):
        f_ump = ecc * pressure * area_half                         # A-137
        lines.append(f"  eccentricity {100 * ecc:3.0f} % of the gap: net pull about "
                     f"{f_ump / 1e3:5.1f} kN")
    lines += [f"  rotor weight 3 t = {3000 * 9.81 / 1e3:.1f} kN: a 10 % eccentric gap "
              "pulls as much",
              "  air-gap uniformity is a manufacturing hold point (C.6) and a",
              "  bearing load (B.6); the pull also lowers the critical speed"]
    emit("y_ump", lines)


def voltage_choice() -> None:
    p, length = 5.0e6, 2 * 110.0                                   # A-138
    lines = [f"generator to converter at the tower base: {length / 2:.0f} m route, "
             "5 MW (A-138)"]
    for name, v, n_par, area, r_km in (("690 V", 690.0, 12, 240e-6, 0.0754),
                                       ("3.3 kV", 3300.0, 3, 150e-6, 0.124)):
        i = p / (S3 * v)
        r = r_km * (length / 2) / 1000 / n_par
        loss = 3 * i ** 2 * r * 1.2                       # 1.2 for 70 C
        cu = 3 * n_par * area * (length / 2) * 8960
        lines.append(f"  {name}: {i:,.0f} A in {n_par} parallel cables per phase; "
                     f"loss {loss / 1e3:.1f} kW,")
        lines.append(f"    copper {cu / 1e3:.1f} t")
    lines += ["  the higher voltage needs 4.8 times less current: fewer cables in",
              "  the tower and lower loss, at the price of MV insulation in the",
              "  generator and the converter (chapters 9, 24)"]
    emit("y_voltage", lines)


def misalignment() -> None:
    fs, dur = 2048.0, 4.0
    t = np.arange(0, dur, 1 / fs)
    fr = 1155 / 60
    rng = np.random.default_rng(19)                                 # A-139
    x = (0.8 * np.sin(2 * np.pi * fr * t) + 1.6 * np.sin(2 * np.pi * 2 * fr * t + 0.4)
         + 0.4 * np.sin(2 * np.pi * 3 * fr * t) + 0.3 * rng.standard_normal(len(t)))
    win = np.hanning(len(t))
    amp = np.abs(np.fft.rfft(x * win)) / (win.sum() / 2)
    f = np.fft.rfftfreq(len(t), 1 / fs)
    peaks = []
    for k in (1, 2, 3):
        idx = np.argmin(np.abs(f - k * fr))
        peaks.append(amp[idx - 2: idx + 3].max())
    emit("y_misalign", [
        "commissioning record at the generator drive-end bearing (A-139):",
        f"  amplitudes at 1x, 2x, 3x shaft speed ({fr:.2f} Hz): "
        + ", ".join(f"{a:.2f}" for a in peaks) + " (relative)",
        f"  2x / 1x = {peaks[1] / peaks[0]:.1f}: a large 2x line with an axial",
        "  component is the classic sign of misalignment; unbalance shows",
        "  mainly at 1x; the alignment report from installation is checked",
        "  and the coupling realigned by the installer (chapters 49, 50)",
    ])
    sel = f <= 100
    csv("ch08-misalign.csv", "f,a", [(f"{a:.2f}", f"{b:.4f}")
                                     for a, b in zip(f[sel], amp[sel])])


def life_losses() -> None:
    _, loss = generator_year()
    e_loss = 12 * loss.sum() / 1e6                                  # MWh/yr
    years, rate = 20, 0.07
    total = e_loss * years
    af = (1 - (1 + rate) ** -years) / rate
    emit("y_lifeloss", [
        f"12 generators, gross data-pack year: {e_loss:,.0f} MWh/yr of losses",
        f"  over {years} years: {total / 1e3:.0f} GWh, about "
        f"{total / (12 * 18.7e3):.1f} years of the 12-turbine farm",
        f"  ({total / 18.7e3:.1f} turbine-years of output)",
        f"  present value at 50 u/MWh and {100 * rate:.0f} %: "
        f"{e_loss * 50 * af / 1e6:.2f} million u",
        "  one per cent of generator efficiency is worth a large share of the",
        "  generator's price: losses belong in the purchase decision",
    ])


if __name__ == "__main__":
    pipeline()
    ump()
    voltage_choice()
    misalignment()
    life_losses()
    ipm()
    field_weakening()
    thermal2()
    ir_trend()
    bearing_spectrum()
    ride_through()
    nameplate()
    im_tests()
    plant_fault()
