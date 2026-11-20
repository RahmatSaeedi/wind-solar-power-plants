"""Chapter 4, last part — rain erosion of blade tips, carbon equivalent from a mill
certificate, a process FMEA for a busbar joint, and six classic calculation errors.

Run from the project root:   python -m companion.ch04.examples_extra
Writes companion/ch04/expected/v_*.txt. Values marked "assumed" (A-084 .. A-086) are
teaching values, not a design.
"""
from __future__ import annotations

import math

from companion.ch04.common import emit
from plantp import materials as mt, physics as ph

W_ROTOR = 10.5 * 2 * math.pi / 60


def erosion() -> None:
    rho_w, c_w, n = 1000.0, 1500.0, 7.0                     # A-084 (exponent assumed)
    lines = ["raindrop impact on the leading edge: water-hammer pressure p = rho c v",
             "  erosion rate taken as proportional to v^7 (assumed exponent, A-084);",
             "  erosion is shown relative to the section at r = 50 m"]
    base = W_ROTOR * 50
    for r in (25.0, 50.0, 75.0):
        v = W_ROTOR * r
        lines.append(f"  r {r:4.0f} m: speed {v:5.1f} m/s, impact {rho_w * c_w * v / 1e6:4.0f} MPa, "
                     f"erosion x {(v / base) ** n:5.2f}")
    lines.append(f"  a rotor with 90 m/s tip speed erodes {(90 / (W_ROTOR * 75)) ** n:.2f} x faster")
    lines.append("  the outer tenth of the blade takes most of the wear: tip protection, and")
    lines.append("    inspection of the leading edge, focus there (chapters 42 and 52)")
    emit("v_erosion", lines)


def carbon_equivalent() -> None:
    heats = {"heat A": dict(C=0.18, Mn=1.45, Cr=0.05, Mo=0.02, V=0.01, Ni=0.08, Cu=0.15),
             "heat B": dict(C=0.12, Mn=1.30, Cr=0.03, Mo=0.01, V=0.00, Ni=0.05, Cu=0.10)}
    lines = ["carbon equivalent CE = C + Mn/6 + (Cr + Mo + V)/5 + (Ni + Cu)/15 (mass %)",
             "  (a widely used weldability indicator; certificate values assumed, A-085)"]
    for name, h in heats.items():
        ce = h["C"] + h["Mn"] / 6 + (h["Cr"] + h["Mo"] + h["V"]) / 5 + (h["Ni"] + h["Cu"]) / 15
        lines.append(f"  {name}: C {h['C']:.2f}, Mn {h['Mn']:.2f} -> CE {ce:.3f}")
    lines.append("  higher CE: a harder heat-affected zone and more risk of cold cracking; the")
    lines.append("    welding procedure sets preheat from CE, thickness and heat input")
    emit("v_ce", lines)


def fmea() -> None:
    rows = [("low bolt preload", 8, 5, 4, "calibrated tools, torque record, marking"),
            ("dirty or oxidised contact surface", 8, 4, 6, "cleaning step with sign-off"),
            ("Al-Cu contact without transition", 7, 3, 5, "bimetal lug specified"),
            ("wrong washer type", 6, 3, 3, "kit per joint, visual check"),
            ("hot joint missed by thermography", 8, 4, 7, "taped targets, load record")]
    lines = ["process FMEA, busbar bolted joint: RPN = severity x occurrence x detection",
             "  (scores 1..10 assumed, A-086; higher = worse)",
             "  failure mode                          S  O  D   RPN"]
    for name, s, o, d, _ in sorted(rows, key=lambda r: -r[1] * r[2] * r[3]):
        lines.append(f"  {name:36s} {s:2d} {o:2d} {d:2d} {s * o * d:5d}")
    after = {"hot joint missed by thermography": 3, "dirty or oxidised contact surface": 3}
    lines.append("after actions (detection improved for the two highest):")
    for name, s, o, d, act in rows:
        if name in after:
            lines.append(f"  {name}: D {d} -> {after[name]}, RPN {s * o * d} -> "
                         f"{s * o * after[name]} ({act})")
    lines.append("  RPN ranks attention; a severity-10 mode deserves action whatever its RPN")
    emit("v_fmea", lines)


def error_hunt() -> None:
    p, t = 87720.0, 15.0
    right_rho = p / (287.05 * (t + 273.15))
    wrong_rho = p / (287.05 * t)
    area, rho, v, ct = math.pi * 75 ** 2, 1.05, 11.0, 0.8
    right_f = 0.5 * rho * area * v ** 2 * ct
    wrong_f = 0.5 * rho * area * v ** 3 * ct
    d_range = mt.miner_damage([40.0], [1e6], 71, 2e6, 3)
    d_amp = mt.miner_damage([20.0], [1e6], 71, 2e6, 3)
    r_ok = math.sqrt(630 / math.pi) / 1000
    ratio_ok = ph.ac_dc_ratio_round(r_ok, 1.72e-8, 50)
    ratio_bad = ph.ac_dc_ratio_round(2 * r_ok, 1.72e-8, 50)
    lines = ["six calculation errors and what they cost:",
             f"  1 gas law with C, not K: rho {wrong_rho:.1f} instead of {right_rho:.3f} kg/m3",
             f"  2 thrust with v^3, not v^2: {wrong_f / 1e3:,.0f} kN instead of {right_f / 1e3:.0f} kN",
             f"  3 S-N with amplitude, not range: damage {d_amp:.3f} instead of {d_range:.3f} "
             f"(x {d_range / d_amp:.0f})",
             f"  4 3600 psi read as MPa: {3600 / (3600 * 6894.757 / 1e6):.0f} x too strong",
             f"  5 skin effect with the diameter as radius: R_ac/R_dc {ratio_bad:.2f} instead of "
             f"{ratio_ok:.2f}",
             "  6 power of a sine as peak V x peak I: 2 x the true average power",
             "  each is caught by a unit check, a limiting case or an order-of-magnitude look"]
    emit("v_errors", lines)


def foundation() -> None:
    vol, gamma_c, b_width = 600.0, 24.0e3, 20.0           # m3, N/m3, m (A-087)
    w_found = vol * gamma_c
    w_soil = 800.0 * 18.0e3                                # backfill on the slab (A-087)
    w_turb = (494e3 + 350e3) * 9.80665
    lines = ["gravity foundation: 600 m3 concrete (24 kN/m3), 800 m3 backfill (18 kN/m3),",
             "  square base 20 m (A-087); B/6 = 3.33 m",
             f"  weights: concrete {w_found / 1e6:.1f} MN, backfill {w_soil / 1e6:.1f} MN, "
             f"tower and top {w_turb / 1e6:.1f} MN",
             "  case                      water        FS     e (m)   base"]
    for m_ot, label in ((89.8e6, "operating (a_thrust)"), (150e6, "extreme (assumed)")):
        for submerged, wl in ((0.0, "dry"), (700.0, "half depth")):
            n = w_found + w_soil + w_turb - 1000 * 9.80665 * submerged
            fs = n * b_width / 2 / m_ot
            e = m_ot / n
            state = "fully pressed" if e <= b_width / 6 else "part lifts"
            lines.append(f"  {label:24s}  {wl:10s} {fs:6.2f} {e:8.2f}   {state}")
    lines.append("  buoyancy removes weight exactly when it is needed; beyond B/6 part of the")
    lines.append("    base lifts off: a geotechnical and structural check (chapter 30)")
    emit("v_foundation", lines)


def flatness() -> None:
    import numpy as np
    rng = np.random.default_rng(20260304)                  # synthetic survey (A-088)
    ang = np.radians(np.arange(16) * 22.5)
    x, y = 2.35 * np.cos(ang), 2.35 * np.sin(ang)
    z = 0.0004 * x - 0.0002 * y + 0.00025 * np.cos(2 * ang) + rng.normal(0, 0.00005, 16)
    a_mat = np.column_stack([np.ones(16), x, y])
    coef, *_ = np.linalg.lstsq(a_mat, z, rcond=None)
    resid = z - a_mat @ coef
    raw = (z.max() - z.min()) * 1000
    flat = (resid.max() - resid.min()) * 1000
    emit("v_flatness", [
        "tower flange top surface surveyed at 16 points on a 4.7 m circle (synthetic, A-088)",
        f"  raw height range (tilt included): {raw:.2f} mm",
        f"  least-squares plane z = a + b x + c y: tilt {coef[1] * 1000:.3f} and "
        f"{coef[2] * 1000:.3f} mm/m",
        f"  flatness = range of residuals about the plane: {flat:.2f} mm",
        "  tolerance 1.0 mm (assumed): the raw range would reject a flat but tilted flange;",
        "  tilt is checked separately (verticality of the tower), waviness by flatness",
        "  (a minimum-zone evaluation can give a slightly smaller value than least squares)",
    ])


def end_of_life() -> None:
    inventory = [("tower steel", 494.0, "easy"), ("nacelle and hub iron and steel", 255.0, "easy"),
                 ("copper (generator, cables)", 35.0, "easy"),
                 ("blade composite (3 x 20 t, A-048)", 60.0, "difficult"),
                 ("foundation concrete", 1440.0, "crushed, reused as aggregate"),
                 ("reinforcement steel", 60.0, "easy once separated")]
    total = sum(m for _, m, _ in inventory)
    lines = ["one turbine's main materials (masses from this chapter's assumptions):"]
    for name, m, route in inventory:
        lines.append(f"  {name:32s} {m:7.0f} t ({100 * m / total:4.1f} %)  {route}")
    metal = sum(m for n, m, _ in inventory if "steel" in n or "copper" in n or "iron" in n)
    lines.append(f"  metals {metal:.0f} t = {100 * metal / (total - 1440):.0f} % of everything except "
                 "the concrete")
    lines.append("  by mass the blades are small, by difficulty they are the main problem:")
    lines.append("    thermoset composites do not melt and are hard to separate (chapter 53)")
    emit("v_eol", lines)


def main() -> None:
    erosion()
    end_of_life()
    flatness()
    foundation()
    carbon_equivalent()
    fmea()
    error_hunt()


if __name__ == "__main__":
    main()
