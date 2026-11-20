"""Chapter 47, round t: flange flatness after the best plane is removed,
transport masses of the sections against the plan of ch 31, weighed
against calculated mass and the tower's frequency, UT repairs by welder,
and the foundation's embedded items checked before the pour.

Run from the project root:   python -m companion.ch47.examples_t
Writes companion/ch47/expected/t_*.txt.
Teaching values (A-490 to A-497); no design approval implied.
"""
from __future__ import annotations

import math

import numpy as np

from companion.ch30 import sources as s30
from companion.ch31 import sources as s31
from companion.ch47 import examples_a as ea
from companion.ch47.common import csv, emit

ANG = [k * 30.0 for k in range(12)]
FLANGES = {   # flange: 12 level readings around the circle, mm
    "F1": [0.0, 0.2, 0.3, 0.1, -0.2, -0.3, -0.1, 0.2, 0.3, 0.1, -0.1, -0.2],
    "F2": [0.0, 0.6, 1.1, 0.4, -0.3, -0.5, 0.2, 0.9, 0.4, -0.2, -0.6, -0.3],
    "F3": [0.4, 0.5, 0.6, 0.6, 0.5, 0.4, 0.2, 0.1, 0.0, 0.0, 0.1, 0.2],
    "F4": [0.1, -0.1, 0.2, 0.0, -0.2, 0.1, 0.0, -0.1, 0.2, 0.1, -0.2, 0.0],
}


# ------------------------------------------------ 1. flange flatness
def flatness(limit: float = 1.2) -> dict:
    th = np.radians(ANG)
    a = np.column_stack([np.ones(12), np.cos(th), np.sin(th)])
    lines = ["flange flatness at 12 points after removing the best plane",
             f"  (teaching limit {limit} mm)",
             "  flange   raw range mm   tilt part mm   flatness mm   verdict"]
    out = {}
    for f, z in FLANGES.items():
        z = np.array(z)
        coef, *_ = np.linalg.lstsq(a, z, rcond=None)
        res = z - a @ coef
        flat = float(res.max() - res.min())
        tilt = 2 * math.hypot(coef[1], coef[2])
        out[f] = (float(z.max() - z.min()), tilt, flat)
        if f == "F2":
            res_f2 = res
        if f == "F3":
            raw_f3, res_f3 = z, res
        lines.append(f"  {f}       {z.max() - z.min():12.2f}   {tilt:12.2f}   "
                     f"{flat:11.2f}   {'ok' if flat <= limit else 'OVER (NCR-202)'}")
    csv("ch47-flatness.csv", "deg,f3raw,f3res,f2res",
        [(d, round(float(x), 3), round(float(y), 3), round(float(w), 3))
         for d, x, y, w in zip(ANG + [360.0], list(raw_f3) + [raw_f3[0]],
                               list(res_f3) + [res_f3[0]],
                               list(res_f2) + [res_f2[0]])])
    lines += ["  F3's raw range is mostly a tilt of the whole flange, which the",
              "  survey's plane removes (the tower stands on the plane); F2",
              "  is wavy - two humps that no plane removes, and a wavy flange",
              "  opens on one side under load (ch 11 flange, ch 30 joint);",
              "  the flatness is read after the plane, never as a raw range"]
    emit("t_flatness", lines)
    return out


# ------------------------------------------------ 2. transport masses
EXTRA = {1: 20.0, 2: 12.0, 3: 0.0, 4: 0.0}        # fatigue steel by section, t


def transport(share: float = 0.12) -> dict:
    rows = ea.tower_steel()
    lines = ["section masses for transport and lifting: ch 31's plan against",
             "  this chapter's take-off (fatigue steel low down, +12 % fittings)",
             "  section   ch 31 t   now t   change"]
    out = {}
    for sec, _, _, _, shell in rows:
        plan = s31.COMPONENTS[f"tower section {sec}"][0]
        now = (shell + EXTRA[sec]) * (1 + share)
        out[sec] = (plan, now)
        lines.append(f"  {sec:7d}   {plan:7.0f}   {now:5.0f}   {now / plan - 1:+6.0%}")
    lines += [f"  section 1 is {out[1][1] - out[1][0]:.0f} t heavier than the transport "
              "plan:",
              "  ch 31's axle loads, bridge checks and crane chart were run on",
              "  the shell alone - the weighed mass of each section goes back",
              "  to the logistics plan before the first convoy (ch 31)"]
    emit("t_transport", lines)
    return out


# ------------------------------------------------ 3. weighed mass and frequency
WEIGHED = {1: 158.1, 2: 121.6, 3: 74.0, 4: 57.0}


def weighed(tol: float = 0.03) -> dict:
    rows = ea.tower_steel()
    calc = {sec: (shell + EXTRA[sec]) * 1.12 for sec, _, _, _, shell in rows}
    lines = [f"sections weighed at the fabricator against the calculated mass "
             f"(+/-{tol:.0%})", "  section   calculated t   weighed t   difference"]
    odd = []
    for k in calc:
        d = WEIGHED[k] / calc[k] - 1
        if abs(d) > tol:
            odd.append(k)
        lines.append(f"  {k:7d}   {calc[k]:12.1f}   {WEIGHED[k]:9.1f}   {d:+9.1%}")
    tower_old = s30.TOWER_T + 32
    tower_new = sum(WEIGHED.values())
    m_old = s30.TOP_T + 0.24 * tower_old
    m_new = s30.TOP_T + 0.24 * tower_new
    f_ratio = math.sqrt(m_old / m_new)
    lines += [f"  off by more than {tol:.0%}: section {', '.join(map(str, odd))} - its "
              "platform and",
              "  ladder are not yet fitted; the dossier says 'complete'",
              f"  the weighed tower is {tower_new:.0f} t against the {tower_old:.0f} t of "
              "ch 30's frequency",
              f"  check: top mass 271 + 0.24 x tower -> f1 x {f_ratio:.3f} "
              f"({f_ratio - 1:+.1%}, mass only)",
              "  the fittings' mass belongs in the frequency model; the margin",
              "  to 1P of ch 30 is re-checked with the weighed tower"]
    emit("t_weighed", lines)
    return dict(odd=odd, f_ratio=f_ratio, tower=tower_new)


# ------------------------------------------------ 4. UT repairs by welder
REPAIRS = {"W-11": (38.0, 0), "W-12": (12.0, 1), "W-13": (22.0, 0),
           "W-14": (32.0, 4)}                   # welded metres, repairs


def repairs() -> dict:
    tot_l = sum(l for l, _ in REPAIRS.values())
    tot_r = sum(r for _, r in REPAIRS.values())
    p = tot_r / tot_l
    lines = [f"UT repairs of section 1 by welder: {tot_r} repairs in {tot_l:.0f} m "
             f"({p * 100:.1f} a 100 m)",
             "  welder   metres   repairs   expected   upper limit (3 sigma)"]
    odd = []
    for w, (l, r) in REPAIRS.items():
        exp = p * l
        ucl = exp + 3 * math.sqrt(exp)
        if r > ucl:
            odd.append(w)
        lines.append(f"  {w}   {l:6.0f}   {r:7d}   {exp:8.2f}   {ucl:8.2f}")
    lines += [f"  above the limit: {', '.join(odd) or 'none'}",
              "  W-14 made four of the five repairs but stays under the",
              "  Poisson limit: with 104 m in all the data are too few to call",
              "  it a welder problem - the next sections' repairs are added",
              "  to the same chart before anyone is retrained"]
    emit("t_repairs", lines)
    return dict(odd=odd, p=p)


# ------------------------------------------------ 5. embedded items before the pour
EMBEDS = {   # item: (on the drawing, found in the cage before the pour)
    "earthing tail N": (1, 1), "earthing tail E": (1, 1), "earthing tail S": (1, 0),
    "earthing tail W": (1, 1), "power duct": (3, 3), "fibre duct": (2, 2),
    "spare duct": (1, 0), "drain pipe": (1, 1), "cage earthing link": (1, 1),
}


def embeds(fix_before_h: float = 2.0, fix_after_h: float = 32.0) -> dict:
    miss = {k: d - f for k, (d, f) in EMBEDS.items() if f < d}
    lines = ["embedded items of the T05 foundation checked against the drawing",
             "  before the pour"]
    lines += [f"  missing: {k} ({n})" for k, n in miss.items()]
    lines += [f"  {sum(miss.values())} items: about {fix_before_h:.0f} h each to place "
              f"now; after the pour",
              f"  about {fix_after_h:.0f} h each (core drilling through reinforced "
              "concrete,",
              "  a structural engineer's approval, a new earthing route) - in",
              "  lab D's plan the embedded items are a witness point; this",
              "  result is the argument for making them a hold point"]
    emit("t_embeds", lines)
    return dict(miss=miss)


if __name__ == "__main__":
    flatness()
    transport()
    weighed()
    repairs()
    embeds()
