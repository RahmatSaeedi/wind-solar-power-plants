"""Appendix X - answers of the Part II diagnostic mastery test (chapters
6-11): trace each source's conversion, explain equipment interfaces, and
separate gross production from delivered output at the point of
connection (POC).

Run from the project root:   python -m companion.appx.mastery_part2
Writes companion/appx/expected/mastery_part2.txt.
Data pack 1.1.0 (synthetic), S0; models of chapters 7, 9, 10 and 11.
Test values marked (test) are fictional and used only in this appendix.
"""
from __future__ import annotations

import math
import warnings

import numpy as np

from companion.appx.common import emit
from companion.ch10 import pvyear10
from companion.ch10.integrated import EFF_POINTS
from companion.ch11 import lab_d, rotor
from plantp import pe, wind as w

warnings.simplefilter("ignore", RuntimeWarning)
OUT: list[str] = []
EXPORT_MW = 100.0
NOLOAD_MW = 0.10        # transformers' no-load losses, always on (test)
LOADLOSS = 0.015        # load losses at 100 MW, scale with P^2 (test)
AV_WIND = 0.981         # energy-based availability, chapter 11
AV_PV = 0.990           # (test)
AUX_PV = 0.003          # PV plant own use, share of output (test)
AUX_WIND_MW = 12 * 168.2 / 8760   # chapter 11, mean own use of 12 turbines


def p(pid: str, text: str) -> None:
    OUT.append(f"{pid}: {text}")


def pv_ac_hourly() -> np.ndarray:
    """PV AC power (W) at the inverters' outputs, chapter 10 chain."""
    c0, c1, c2 = pe.fit_loss_coeffs(EFF_POINTS)
    x = pvyear10.dc_power() / 50e6
    y = np.where(x > c0, (-(1 + c1) + np.sqrt((1 + c1) ** 2 - 4 * c2 * (c0 - x)))
                 / (2 * c2), 0.0)
    return np.minimum(y * 50e6, 50e6 * 0.98)


def trace() -> None:
    k = (174 - 1) * 24 + 13                          # 23 June, 13:00
    s = pvyear10.strings()
    dc = pvyear10.dc_power()[k] / 1e6
    ac = pv_ac_hourly()[k] / 1e6
    p("M21", f"PV 23 June 13:00: string {s['v_mp'][k]:.0f} V; array DC"
             f" {dc:.2f} MW after 3 % DC losses")
    p("   ", f"inverters' AC {ac:.2f} MW ({100 * ac / dc:.1f} % of DC)")
    v, rho = 9.50, 1.002
    op = w.operate(rotor.turbine(), v, rho)
    pw_air = 0.5 * rho * rotor.AREA * v ** 3
    om_g = 1032 * 2 * math.pi / 60
    p("M22", f"wind day 142 11:00: air {pw_air / 1e6:.2f} MW, Cp {op.cp:.3f},"
             f" electric {op.power_w / 1e3:,.0f} kW")
    p("   ", f"generator torque {op.power_w / 0.94 / om_g / 1e3:.1f} kN m at"
             f" 1032 rpm; 33 kV current"
             f" {op.power_w / (math.sqrt(3) * 33e3):.1f} A at pf 1")
    p("M23", f"PV year: 606 GWh of sunlight on the modules -> AC 111.3 GWh"
             f" ({100 * 111.339 / 606.3:.1f} %)")
    p("   ", f"wind at the hour above: {100 * op.power_w / pw_air:.1f} % of"
             " the air's power")


def interfaces() -> None:
    p("M24", "DC window, 23 June 13:00: 965 V against the 933 V floor"
             " (D-012)")
    p("   ", "margin 32 V; 17 h a year below the floor (U-032 closed)")
    p("M25", f"tower: 1P {11.5 / 60:.3f} Hz < f1 0.215 Hz < 3P"
             f" {3 * 11.5 / 60:.3f} Hz; margins"
             f" {100 * (0.215 / (11.5 / 60) - 1):.0f} % and"
             f" {100 * (1 - 0.215 / (3 * 11.5 / 60)):.0f} %")


def gross_delivered() -> None:
    v, _, rho = lab_d.hourly()
    v_eq = w.density_equivalent_speed(v, rho)
    wake = 188.16 / 201.23
    wind = 12 * lab_d.pack_power(v_eq) / 1e3 * wake * AV_WIND        # MW
    pv = pv_ac_hourly() / 1e6 * (1 - 0.0143) * (1 - 0.0007) * AV_PV  # MW
    p33 = wind + pv
    loss = NOLOAD_MW + LOADLOSS * EXPORT_MW * (p33 / EXPORT_MW) ** 2
    poc = p33 - loss - AUX_WIND_MW - AUX_PV * pv
    delivered = np.minimum(poc, EXPORT_MW)
    export = np.clip(delivered, 0.0, None).sum()
    imported = -np.clip(delivered, None, 0.0).sum()
    cut = np.clip(poc - EXPORT_MW, 0.0, None)
    p("M26", f"33 kV: wind {wind.sum() / 1e3:.2f} GWh (wakes, availability),"
             f" PV {pv.sum() / 1e3:.2f} GWh")
    p("   ", f"together {p33.sum() / 1e3:.2f} GWh")
    p("M27", f"electrical losses {loss.sum() / 1e3:.2f} GWh; own use"
             f" {(AUX_WIND_MW * 8760 + AUX_PV * pv.sum()) / 1e3:.2f} GWh")
    p("   ", f"curtailed at 100 MW: {cut.sum() / 1e3:.3f} GWh in"
             f" {(cut > 0).sum()} h")
    p("M28", f"delivered (export) {export / 1e3:.2f} GWh; imported"
             f" {imported:,.0f} MWh in {(delivered < 0).sum():,} h")
    p("   ", f"capacity factor at the POC {export / (EXPORT_MW * 8760):.3f}")
    p("M29", f"peak at 33 kV {p33.max():.1f} MW; {(p33 > EXPORT_MW).sum()} h"
             " above 100 MW at 33 kV")
    p("   ", "gross before any loss: wind 218.79 GWh + PV 129.15 GWh")


if __name__ == "__main__":
    trace()
    interfaces()
    gross_delivered()
    emit("mastery_part2", OUT)
