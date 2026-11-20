"""Chapter 42, a seventh round: what preload does to the fatigue of the
root bolts, winding temperature rise read from resistance, shock logs of
the nacelles in transport, the size of a composite scarf repair, and a
service vibration baseline taken from the factory run-in.

Run from the project root:   python -m companion.ch42.examples_x
Writes companion/ch42/expected/x_*.txt.
Teaching values (A-454, A-457); measurement relations, no procedures.
"""
from __future__ import annotations

import random
from statistics import mean, pstdev

from companion.ch42.common import emit
from plantp import structures as st


# ------------------------------------------------ root bolts in fatigue
def bolt_fatigue(pull_range_kn: float = 120.0, area_mm2: float = 1120.0,
                 n_cycles: float = 1e8, cat: float = 50.0, phi: float = 0.15):
    out = {}
    lines = ["root bolt fatigue: damage-equivalent pull range "
             f"{pull_range_kn:.0f} kN, {n_cycles:.0e} cycles",
             f"  bolt stress area {area_mm2:.0f} mm2, detail category {cat:.0f} "
             "MPa (teaching)",
             "  joint state            bolt share   stress range MPa   damage"]
    for name, share in (("closed (preload kept)", phi), ("open (preload lost)", 1.0)):
        ds = share * pull_range_kn * 1e3 / area_mm2
        d = n_cycles / st.sn_life(ds, cat)
        out[name] = d
        lines.append(f"  {name:22s} {share:10.2f}   {ds:16.1f}   {d:6.2f}")
    lines += [f"  losing the preload multiplies the damage by "
              f"{out['open (preload lost)'] / out['closed (preload kept)']:,.0f}:",
              "  the bolt that sees only a share of the load lasts the",
              "  turbine's life; the same bolt carrying all of it fails in",
              f"  about {20 * 365 / out['open (preload lost)']:.0f} days - why the "
              "preload record is a critical",
              "  characteristic"]
    emit("x_bolts", lines)
    return out


# ------------------------------------------------ winding rise by resistance
def winding_rise(r_cold: float = 0.01520, t_cold: float = 20.0,
                 r_hot: float = 0.02010) -> dict[str, float]:
    t_hot = r_hot / r_cold * (234.5 + t_cold) - 234.5
    rise = t_hot - t_cold
    lines = ["winding temperature from its resistance (copper, 234.5 K rule)",
             f"  cold {r_cold * 1000:.2f} mOhm at {t_cold:.0f} C; hot "
             f"{r_hot * 1000:.2f} mOhm after the heat run",
             f"  T_hot = R_hot / R_cold x (234.5 + T_cold) - 234.5 = {t_hot:.1f} C",
             f"  average rise {rise:.1f} K (the hot spot is higher)",
             "  the resistance gives the winding's mean temperature, which",
             "  no sensor on the surface can: the heat run's record is how",
             "  the generator's thermal class margin is shown (lesson C)"]
    emit("x_rise", lines)
    return dict(t_hot=t_hot, rise=rise)


# ------------------------------------------------ nacelle shock logs
def shocks(seed: int = 4215, limit_g: float = 3.0) -> dict[str, list[str]]:
    rng = random.Random(seed)
    logs = {}
    for k in range(1, 13):
        peaks = [abs(rng.gauss(1.2, 0.5)) for _ in range(40)]
        if k in (5, 11):
            peaks.append(4.1 if k == 5 else 3.4)
        logs[f"N-{k:02d}"] = max(peaks)
    over = [k for k, v in logs.items() if v > limit_g]
    lines = [f"shock recorders on 12 nacelles in transport (limit {limit_g} g, "
             "teaching)",
             "  " + ", ".join(f"{k} {v:.1f}" for k, v in list(logs.items())[:6]),
             "  " + ", ".join(f"{k} {v:.1f}" for k, v in list(logs.items())[6:]),
             f"  over the limit: {over}",
             "  a hard bump can mark the bearings of a still drivetrain;",
             "  those nacelles get a bearing and alignment check before",
             "  erection, and the transport claim is opened with the log",
             "  as evidence (ch 31)"]
    emit("x_shocks", lines)
    return dict(over=over)


# ------------------------------------------------ scarf repair size
def scarf(thickness_mm=(5.0, 12.0, 20.0), ratio: float = 50.0,
          kg_m2_mm: float = 1.9) -> dict[float, float]:
    out = {}
    lines = [f"scarf repair of a laminate, taper 1:{ratio:.0f} (teaching; the "
             "maker's manual sets it)",
             "  skin mm   scarf length each side m   repair mass kg (1 m wide)"]
    for t in thickness_mm:
        l = t * ratio / 1000
        mass = (2 * l + 0.1) * 1.0 * t * kg_m2_mm * 0.5
        out[t] = l
        lines.append(f"  {t:7.0f}   {l:26.2f}   {mass:25.1f}")
    lines += ["  a gentle taper spreads the load over a long joint: a 20 mm",
              "  skin needs a repair a metre each side - which is why",
              "  structural repairs (category 4) leave the rope and go to the",
              "  ground, and why each repair's mass goes into the balance"]
    emit("x_scarf", lines)
    return out


# ------------------------------------------------ service vibration baseline
def baseline(seed: int = 4216) -> dict[str, float]:
    rng = random.Random(seed)
    factory = [rng.gauss(1.00, 0.05) for _ in range(10)]
    m, s = mean(factory), pstdev(factory)
    alert = m + 3 * s
    years = [1.00, 1.02, 1.03, 1.05, 1.28]
    first = next((k + 1 for k, v in enumerate(years) if v > alert), None)
    lines = ["mesh amplitude of a gearbox: factory run-in as the baseline",
             f"  ten units at the factory: mean {m:.2f}, sd {s:.2f}; alert above "
             f"{alert:.2f}",
             "  one unit in service, yearly: " + ", ".join(f"{v:.2f}" for v in years),
             f"  first above the alert: year {first}",
             "  a baseline from the factory, at known load and speed, makes",
             "  the condition monitoring of ch 37 sharper than a generic",
             "  limit: the run-in record is handed over for that reason"]
    emit("x_baseline", lines)
    return dict(alert=alert, first=first or 0)


if __name__ == "__main__":
    bolt_fatigue()
    winding_rise()
    shocks()
    scarf()
    baseline()
