"""Chapter 48, round y: an as-found calibration out of tolerance and the
data it puts in doubt, meter seals against their register, a reversed CT
in a three-phase meter, condensation in an outdoor cabinet, power-supply
inrush against the maker's table, and camera video on the WAN link.

Run from the project root:   python -m companion.ch48.examples_y
Writes companion/ch48/expected/y_*.txt and diagrams/data/ch48-dew.csv.
Teaching values (A-498 to A-505); defensive administration only.
"""
from __future__ import annotations

import math
from datetime import date, timedelta

import numpy as np

from companion.ch48.common import csv, emit


# ------------------------------------------------ 1. as-found out of tolerance
def as_found(tol: float = 1.5, found: float = 2.8, last: date = date(2025, 6, 1),
             now: date = date(2027, 6, 1)) -> dict:
    days = (now - last).days
    cross = tol / found * days                          # linear drift from zero
    since = last + timedelta(days=round(cross))
    lines = [f"pyranometer PYR-2: as found {found} % high at its calibration on {now},",
             f"  tolerance {tol} %",
             f"  last calibration {last} ({days} days); assuming a linear drift "
             "from zero,",
             f"  it left the tolerance on about {since} (day {cross:.0f})",
             f"  data from {since} to {now}: {(now - since).days} days flagged;",
             f"  mean error over them {(tol + found) / 2:.2f} %",
             "  the as-found reading is the most useful line of the",
             "  certificate: it says how long the data were wrong and which",
             "  reports used them (the monthly PR of ch 37); the as-left",
             "  value only says the sensor is right again"]
    emit("y_asfound", lines)
    return dict(since=since, days=(now - since).days, mean=(tol + found) / 2)


# ------------------------------------------------ 2. meter seals
SEAL_REG = {"M-01 main": "S-40211", "M-02 check": "S-40212", "CT box E1": "S-40213",
            "VT box E1": "S-40214", "test block M-01": "S-40215",
            "test block M-02": "S-40216"}
SEAL_SEEN = {"M-01 main": "S-40211", "M-02 check": "S-40212", "CT box E1": "S-40213",
             "VT box E1": "S-40214", "test block M-01": "S-40398",
             "test block M-02": None}


def seals() -> list:
    bad = []
    lines = ["revenue metering seals at the quarterly inspection against the",
             "  seal register"]
    for k, reg in SEAL_REG.items():
        seen = SEAL_SEEN[k]
        ok = seen == reg
        if not ok:
            bad.append(k)
        lines.append(f"  {k:16s} register {reg}  seen {seen or 'none':8s} "
                     f"{'ok' if ok else 'FINDING'}")
    lines += ["  a test block opened and resealed with an unregistered seal,",
              "  and one left unsealed: each is a record to close with the",
              "  person and the reason (a test, a fault), and the energy of",
              "  the open period is checked against the check meter"]
    emit("y_seals", lines)
    return bad


# ------------------------------------------------ 3. a reversed CT
def ct_reversed(p_mw: float = 100.0, pf: float = 0.95) -> dict:
    phi = math.acos(pf)
    s_ph = p_mw / 3 / pf
    ph = [s_ph * np.exp(1j * phi)] * 3                  # per-phase S = V I*
    wrong = [ph[0], ph[1], -ph[2]]                      # phase c CT reversed
    p_ok = sum(x.real for x in ph)
    p_bad = sum(x.real for x in wrong)
    lines = [f"three-phase export meter at {p_mw:.0f} MW, pf {pf}; phase c CT reversed",
             "  phase   P right MW   P read MW"]
    for k, (a, b) in enumerate(zip(ph, wrong)):
        lines.append(f"  {'abc'[k]:5s}   {a.real:10.2f}   {b.real:9.2f}")
    lines += [f"  total   {p_ok:10.2f}   {p_bad:9.2f}  ({p_bad / p_ok:.0%} of the right value)",
              "  one reversed CT turns a third of the energy negative: the",
              "  meter reads a third of the export; the commissioning check",
              "  reads each phase's power and angle, at the first low load,",
              "  before a single interval is settled"]
    emit("y_ct", lines)
    return dict(ok=p_ok, bad=p_bad)


# ------------------------------------------------ 4. condensation in a cabinet
def dew_point(t: float, rh: float) -> float:
    b, c = 17.62, 243.12                                # Magnus coefficients
    g = math.log(rh / 100) + b * t / (c + t)
    return c * g / (b - g)


def condensation(t_eve: float = 30.0, rh_eve: float = 50.0, own_k: float = 2.0,
                 heater_k: float = 6.0) -> dict:
    td = dew_point(t_eve, rh_eve)
    hours = np.arange(0, 24.01, 0.25)
    amb = 23 + 9 * np.sin((hours - 9) / 24 * 2 * np.pi)
    cab = amb + own_k
    heated = np.maximum(cab, np.minimum(cab + heater_k, td + 3))   # thermostat
    csv("ch48-dew.csv", "h,amb,cab,heated,td",
        [(h, round(a, 2), round(c, 2), round(x, 2), round(td, 2))
         for h, a, c, x in zip(hours, amb, cab, heated)])
    wet = float((cab < td).sum() * 0.25)
    wet_h = float((heated < td).sum() * 0.25)
    lines = [f"outdoor cabinet, air sealed in at {t_eve:.0f} C and {rh_eve:.0f} % in the "
             "evening:",
             f"  dew point {td:.1f} C (Magnus); night low outside {amb.min():.0f} C",
             f"  cabinet with its own {own_k:.0f} K of device heat: {wet:.1f} h a night "
             "below the dew point",
             f"  with a heater of up to {heater_k:.0f} K held 3 K above the dew point: "
             f"{wet_h:.1f} h",
             "  water condenses on the coldest surface - terminals and the",
             "  door - in the hours around 03:00; a heater with a thermostat",
             "  and a breather keep the cabinet above the dew point, and",
             "  the heater circuit is on the FAT list like any other"]
    emit("y_dew", lines)
    return dict(td=td, wet=wet, wet_h=wet_h)


# ------------------------------------------------ 5. PSU inrush vs the maker's table
MAX_PER_MCB = {"B10": 2, "C10": 4, "C16": 6}           # maker's table (teaching)
PANEL = {"F11 (C10)": ("C10", 6), "F12 (C10)": ("C10", 3), "F13 (B10)": ("B10", 2),
         "F14 (C16)": ("C16", 5)}


def inrush() -> list:
    bad = [k for k, (t, n) in PANEL.items() if n > MAX_PER_MCB[t]]
    lines = ["24 V power supplies per miniature circuit breaker against the",
             "  maker's inrush table (units switched on together)"]
    lines += [f"  {k:10s} {n} units, table allows {MAX_PER_MCB[t]}  "
              f"{'ok' if n <= MAX_PER_MCB[t] else 'TRIPS AT SWITCH-ON'}"
              for k, (t, n) in PANEL.items()]
    lines += [f"  {', '.join(bad)}: the breaker can trip each time the panel",
              "  is energised - after every black start; the supplies are",
              "  split or switched on in steps, and the FAT switches the",
              "  panel on cold, as it will be at site"]
    emit("y_inrush", lines)
    return bad


# ------------------------------------------------ 6. camera video on the WAN
def wan_video(link: float = 2.0, scada: float = 0.35, video: float = 1.5,
              pkt_bits: float = 4000) -> dict:
    lines = [f"WAN to the control centre {link} Mbit/s (ch 35); SCADA {scada} Mbit/s",
             "  case                              load   SCADA wait"]
    out = {}
    for name, v, prio in (("SCADA only", 0.0, False),
                          ("one camera, no priority", video, False),
                          ("two cameras, no priority", 2 * video, False),
                          ("SCADA first, video capped 1.5", video, True)):
        rho = (scada + v) / link
        mu = link * 1e6 / pkt_bits                      # packets a second
        if prio:
            w = (scada / link) / (mu * (1 - scada / link))   # sees only itself
        elif rho < 1:
            w = rho / (mu * (1 - rho))                  # M/M/1 waiting time
        else:
            w = math.inf
        out[name] = (rho, w)
        wt = "grows without end" if math.isinf(w) else f"{w * 1000:.1f} ms"
        lines.append(f"  {name:32s}  {rho:5.0%}   {wt}")
    r1, w1 = out["one camera, no priority"]
    w0 = out["SCADA only"][1]
    lines += [f"  one remote camera view takes the WAN to {r1:.0%} and SCADA",
              f"  waits {w1 / w0:.0f} times longer; two overrun the link; with",
              "  SCADA first and video capped below the rest of the link,",
              "  telemetry does not notice the cameras (ch 35 queue, ch 36",
              "  conduits)"]
    emit("y_wan", lines)
    return out


if __name__ == "__main__":
    as_found()
    seals()
    ct_reversed()
    condensation()
    inrush()
    wan_video()
