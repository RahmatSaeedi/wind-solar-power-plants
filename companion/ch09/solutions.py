"""Chapter 9 - numerical answers to the end-of-chapter problems (P01 ...).
Criteria-based problems are answered in the text.

Run from the project root:   python -m companion.ch09.solutions
Writes companion/ch09/expected/solutions.txt.
"""
from __future__ import annotations

import math

from companion.ch09 import pvyear
from companion.ch09.common import emit
from plantp import datapack, mppt as mp, pe

S2, S3 = math.sqrt(2), math.sqrt(3)
OUT: list[str] = []


def p(pid: str, text: str) -> None:
    OUT.append(f"{pid}: {text}")


def level_1() -> None:
    p("P01", f"linear: loss {400 * 50 / 1e3:.0f} kW, efficiency {400 / 800:.2f}")
    d = pe.buck_duty(1100, 550)
    p("P02", f"D {d:.2f}; ripple {pe.buck_ripple(1100, d, 0.5e-3, 8e3):.2f} A")
    d = pe.boost_duty(500, 800)
    p("P03", f"D {d:.3f}; ripple {pe.boost_ripple(500, d, 1e-3, 1e4):.2f} A")
    p("P04", f"{pe.rectifier_6p_vdc(690):.1f} V; at 45 deg "
             f"{pe.rectifier_6p_vdc(690, alpha_deg=45):.1f} V")
    p("P05", f"{0.9 * 1000 * S3 / (2 * S2):.0f} V; SVPWM max "
             f"{pe.vll_max(1000):.0f} V")
    p("P06", f"{pe.vdc_min(480):.0f} V; with 10 % {pe.vdc_min(480, headroom=0.1):.0f} V")
    p("P07", f"m_f = {2500 / 50:.0f}")
    p("P08", f"IGBT {0.9 + 0.5e-3 * 1200:.2f} V, MOSFET {2e-3 * 1200:.2f} V; "
             f"equal at {0.9 / (2e-3 - 0.5e-3):.0f} A")
    p("P09", f"{pe.gate_drive_power(5e-6, 25, 1e4):.2f} W")
    p("P10", f"{pe.overshoot_v(50e-9, 4e9):.0f} V")
    p("P11", f"{40 + 800 * 0.05:.0f} C")
    e = pe.capacitor_energy_j(12e-3, 1100)
    t = 50e3 * 12e-3 * math.log(1100 / 50)
    p("P12", f"{e / 1e3:.2f} kJ; tau 600 s; to 50 V in {t:,.0f} s")
    p("P13", f"{pe.lcl_resonance(100e-6, 50e-6, 200e-6):,.0f} Hz")
    p("P14", f"life x {pe.relative_cycle_life(30, 20):.3f}")
    p("P15", f"{pe.deadtime_error(1100, 2e-6, 4e3):.1f} V")
    p("P16", f"{pe.dclink_ripple_current_rms(1.0, 1.0, 1.0):.3f} I -> "
             f"{pe.dclink_ripple_current_rms(1000, 1.0, 1.0):.0f} A")
    p("P17", f"SCR {1000 / 100:.0f} and {300 / 100:.0f}")
    iq, ip = pe.frt_currents(0.6)
    p("P18", f"I_q {iq:.2f}, I_p {ip:.3f} pu")
    p("P19", f"{100 * (0.5 / 50) / 0.05:.0f} % of rating")
    p("P20", f"{1 / (1 + 0.5 * 48 / 8760):.5f}")
    p("P21", f"{0.99 ** 7:.3f}")
    p("P22", f"{60e3 / (3600 * 5):.2f} kg/s")
    p("P23", f"{5.5e6 / (S3 * 600):,.0f} A; {5.5e6 / (S3 * 690):,.0f} A")
    k = float(pe.derating(45, 1500))
    p("P24", f"{k:.3f} pu = {5 * k:.2f} MW")
    p("P25", f"{13.75 * 12 * 365 / 1e3:.1f} MWh per inverter")


def level_2() -> None:
    ct, cd = pe.conduction_losses(1000, 0.9, 1.0, 0.8, 1e-3, 0.9, 0.8e-3)
    p("P31", f"IGBT {ct:.0f} W, diode {cd:.0f} W")
    st, sd = pe.switching_losses(1000, 700, 4000, 0.12, 0.04, 600, 600)
    p("P32", f"IGBT {st:.0f} W, diode {sd:.0f} W")
    p("P33", f"f = 2.5 x 42.1 / 20.6 = {2.5 * 42.1 / 20.6:.2f} kHz")
    p("P34", f"one side {1 - 0.0125:.4f}; both sides about "
             f"{(1 - 0.0125) ** 2:.4f}")
    r = pe.foster_step(1000, [0.01, 0.03], [0.05, 2.0], [0.1, 10.0])
    p("P35", f"rise {r[0]:.1f} K at 0.1 s, {r[1]:.1f} K at 10 s")
    c = pe.fit_loss_coeffs([(0.1, 0.96), (0.5, 0.985), (1.0, 0.982)])
    p("P36", f"c0 {1e3 * c[0]:.2f}, c1 {1e3 * c[1]:.2f}, c2 {1e3 * c[2]:.2f} "
             f"per mille; peak at {math.sqrt(c[0] / c[2]):.2f} pu")
    p("P37", f"European {pe.weighted_efficiency(c, pe.EURO_WEIGHTS):.4f}, "
             f"CEC {pe.weighted_efficiency(c, pe.CEC_WEIGHTS):.4f}")
    l1 = pe.l_for_ripple(1100, 2500, 0.15 * 6224)
    p("P38", f"L1 {l1 * 1e6:.1f} uH")
    z_b = 690 ** 2 / 5.26e6
    c_f = 0.05 / (2 * math.pi * 50 * z_b)
    p("P39", f"Z_b {z_b * 1e3:.1f} mohm; C {c_f * 1e3:.2f} mF per phase")
    w = 2 * math.pi * 2500
    l2 = 11 / (w * w * c_f)
    f_r = pe.lcl_resonance(l1, l2, c_f)
    p("P40", f"L2 {l2 * 1e6:.1f} uH; resonance {f_r:.0f} Hz (500 to 1250)")
    p("P41", f"R_d {1e3 / (3 * 2 * math.pi * f_r * c_f):.1f} mohm")
    p("P42", f"{pe.dclink_c_for_holdup(5e6, 5e-3, 1100, 1000):.3f} F")
    wn = 2 * math.pi * 10
    p("P43", f"kp {2 * 0.707 * wn:.1f}, ki {wn * wn:.0f}")
    wc, wb = 2 * math.pi * 200, 2 * math.pi * 50
    p("P44", f"kp {0.15 / wb * wc:.3f}, ki {0.004 * wc:.2f}")
    p("P45", f"H 2.4 s: {0.1 / (2 * 2.4) * 50:.2f} Hz/s; H 4.0 s: "
             f"{0.1 / (2 * 4.0) * 50:.3f} Hz/s")
    x = (100 / 300) * 10 / math.sqrt(101)
    p("P46", f"x {x:.4f} pu; dV {100 * x * 0.2:.1f} %")
    p("P47", f"{0.2 * 1.375e6 / (2 * 2 * math.pi * 50 * 0.012 * 1000):.1f} V")
    p("P48", f"{50 * 0.25e-9 * 8e9:.0f} A")
    mu = 1.31
    cum = 0.0
    for k in range(6):
        cum += math.exp(-mu) * mu ** k / math.factorial(k)
        if k == 3:
            p("P49", f"P(N > 3) = {1 - cum:.4f}")
    cv = mp.PVM_550.at(1000, 70, 26)
    p("P50", f"V_mp {cv.mpp()[0]:.0f} V; floor 933 V")
    v_cold = mp.PVM_550.at(1000, -10, 28).voc
    p("P51", f"28 modules at -10 C: V_oc {v_cold:.0f} V > 1500 V")
    p("P52", f"{pe.boost_cap_ripple(50, 0.4, 200e-6, 16e3):.2f} V")
    p("P53", f"{pe.rectifier_6p_vdc(690, 50e-6, 1000):.1f} V")
    p("P54", f"{0.23 * 1000 / (49 * 2 * math.pi * 50 * 100e-6):.0f} A")
    p("P56", f"{pe.vll_max(933 / 1.1):.0f} V")
    af = (1 - 1.07 ** -20) / 0.07
    p("P57", f"{1656 * 50:,.0f} u/yr; present value {1656 * 50 * af / 1e3:,.0f}"
             " thousand u")
    p("P58", f"{0.001 * 101.4e3:.0f} MWh/yr")
    p("P59", f"{10 * 13.7 * 12 * 365 / 1e3:.0f} MWh/yr; "
             f"{10 * 13.7 * 12 * 365 / 1e3 * 50:,.0f} u/yr")
    p("P60", f"(14 / 29)^5 = {(14 / 29) ** 5:.3f}")
    p("P61", f"{math.ceil(50 / 0.3)} units, {math.ceil(50 / 0.3) * 0.15:.0f} "
             "failures/yr")
    loss = 84e3 - 0.3 * 22.9e3
    p("P64", f"{loss / 1e3:.1f} kW; efficiency {5e6 / (5e6 + loss):.5f}")
    p("P65", f"{45 + 494 * 0.08:.1f} C")


def level_3() -> None:
    day = datapack.load_hourly("day_summer")
    row = day.iloc[12]
    g, ta = float(row["ghi_wm2"]), float(row["t_air_c"])
    tc = float(mp.cell_temperature(ta, g))
    c = mp.PVM_550.at(g, tc, 26)
    v, ps = c.mpp()
    p_dc = ps * pvyear.N_STRINGS / pvyear.N_INV * (1 - pvyear.DC_LOSS)
    p("P66", f"12:00: G {g:.0f}, cell {tc:.1f} C, MPP {v:.0f} V, "
             f"inverter DC {p_dc / 1e6:.3f} MW")
    share = 1 - float(c.p(1073)) / ps
    p("P67", f"held at 1073 V: {100 * share:.1f} % of the hour's energy lost")
    mu = 1.31
    k, cum = 0, 0.0
    while True:
        cum += math.exp(-mu) * mu ** k / math.factorial(k)
        if cum >= 0.95:
            break
        k += 1
    p("P70", f"stock {k} fans: P(N <= {k}) = {cum:.3f}")
    d = pvyear.hourly()
    june = slice(int(151 * 24), int(181 * 24))
    e_june = d["p_dc"][june].sum() / 1e6 * 0.984
    p("P71", f"June AC about {e_june:,.0f} MWh; one inverter for the month "
             f"{e_june / 10:,.0f} MWh")
    p_inv = d["p_dc"] / pvyear.N_INV
    p("P72", f"hours above 4.0 MW per inverter: {int((p_inv >= 4.0e6).sum())}")
    v26 = mp.PVM_550.at(1000, 25, 26).vmp
    p("P74", f"26 x V_mp(STC) {v26:.0f} V; 24 modules {v26 * 24 / 26:.0f} V")


def further() -> None:
    import numpy as np
    e = pe.capacitor_energy_j(20e-3, 1000)
    p("P126", f"{e / 1e3:.1f} kJ in R; R {1000 / 15:.1f} ohm, tau "
              f"{1000 / 15 * 20e-3:.2f} s")
    phi = 0.4
    pw = 600 * 600 * phi * (math.pi - phi) / (2 * math.pi ** 2 * 5e4 * 1e-5)
    p("P127", f"{pw / 1e3:.1f} kW")
    p("P128", f"{pe.vll_max(950 / 1.1):.0f} V")
    p("P129", f"R {1200 ** 2 / 5e6:.3f} ohm; {5e6 * 0.1 / 1e6:.2f} MJ")
    c, r, l_h, dt = 12e-3, 0.10, 20e-6, 1e-7
    i = i_pk = 0.0
    v = 1000.0
    for _ in range(int(3e-3 / dt)):
        i += (v - r * i) / l_h * dt
        v -= i / c * dt
        i_pk = max(i_pk, i)
    p("P131", f"zeta {r / 2 * math.sqrt(c / l_h):.2f}; peak {i_pk / 1e3:.1f} kA")
    p("P132", f"+-{28 * 50 / 2:.0f} V")
    rng = np.random.default_rng(29)
    p_mean = 101.4e3 / 8760 / 10
    tot = []
    for _ in range(2000):
        n_f = rng.poisson(0.49 * 10 * 25)
        major = rng.random(n_f) < 0.08
        hours = np.where(major, rng.lognormal(math.log(100), 0.5, n_f),
                         rng.lognormal(math.log(36), 0.6, n_f))
        tot.append(hours.sum() * p_mean / 25)
    p("P134", f"mean {np.mean(tot):.0f} MWh/yr, P90 "
              f"{np.percentile(tot, 90):.0f} MWh/yr")


def further2() -> None:
    loss = 20e3 * (1 / 0.95 - 1)
    p("P141", f"{loss / 1e3:.2f} kW; {loss * 8760 / 1e6:.1f} MWh/yr")
    e = 690 * 1.2
    p("P142", f"EMF {e:.0f} V; DC needed {pe.vdc_min(e):.0f} V > 1150 V")
    p("P143", f"{100e3 * 2 ** ((70 - 75) / 10):,.0f} h")
    u = 0.002
    p_in, eta = 5.08e6, 0.984
    u_loss = math.sqrt((p_in * u) ** 2 + (p_in * eta * u) ** 2)
    p("P144", f"efficiency +-{100 * eta * math.sqrt(2) * u:.3f} %; loss "
              f"+-{u_loss / 1e3:.1f} kW ({100 * u_loss / (p_in * (1 - eta)):.0f} %)")
    l1, l2, c = 55.7e-6, 50.9e-6, 608e-6
    l_tx = 0.08 * (600 ** 2 / 1.375e6) / (2 * math.pi * 50)
    l_g = (600 ** 2) / (2 * 1.375e6) / (2 * math.pi * 50) + l_tx
    p("P145", f"{pe.lcl_resonance(l1, l2 + l_g, c):.0f} Hz")
    p("P146", f"sqrt(40) = {math.sqrt(40):.1f}")


def further3() -> None:
    import numpy as np
    h = datapack.load_hourly()
    pc = datapack.load_power_curve()
    p_w = 12 * np.interp(h["ws_100m_ms"].to_numpy(dtype=float),
                         pc["wind_speed_ms"], pc["power_kw"]) / 1e3 * 0.97
    r = pvyear.inverter_year(pe.fit_loss_coeffs(
        [(0.10, 0.970), (0.25, 0.983), (0.50, 0.986), (0.75, 0.985),
         (1.00, 0.983)]))
    tot = p_w + r["p_out"] / 1e6
    parts = []
    for lim in (95.0, 90.0):
        over = np.maximum(tot - lim, 0.0)
        parts.append(f"{lim:.0f} MW: {int((over > 0).sum())} h, "
                     f"{over.sum():,.0f} MWh")
    p("P156", "; ".join(parts))
    p("P157", f"threshold {90 - 2.5:.1f} C: A {'accept' if 86.2 < 87.5 else 'no'},"
              f" B not proven")


if __name__ == "__main__":
    level_1()
    level_2()
    level_3()
    further()
    further2()
    further3()
    emit("solutions", OUT)
