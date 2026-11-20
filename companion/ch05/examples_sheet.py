"""Chapter 5, section A - a spreadsheet as an engineering model, audited by code.

Run from the project root:   python -m companion.ch05.examples_sheet
The yield sheet (A-096) is synthetic: monthly irradiation from data pack 1.1.0, the
screening factors of chapter 1, and six planted mistakes for the auditor to find.
"""
from __future__ import annotations

import numpy as np

from companion.ch05.common import emit
from plantp import datapack, screening as sc
from plantp.sheet import Sheet, audit

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def monthly_ghi() -> list[float]:
    h = datapack.load_hourly()
    return [round(float(v), 1) for v in h["ghi_wm2"].groupby(h.index.month).sum() / 1000]


def build(ghi: list[float], with_errors: bool) -> Sheet:
    cells = {"A1": "Plant P yield sheet (synthetic; data pack 1.1.0; S0)",
             "A2": "PV DC capacity", "B2": 60, "C2": "MWp",
             "A3": "DC performance ratio", "B3": 0.85, "C3": "-",
             "A4": "Inverter efficiency", "B4": 0.98, "C4": "-",
             "A5": "Inverter limit", "B5": 50, "C5": "MW",
             "A6": "Hours in the year", "B6": 8760, "C6": "h",
             "A8": "month", "B8": "GHI kWh/m2", "C8": "energy MWh"}
    for k, (m, g) in enumerate(zip(MONTHS, ghi)):
        r = 9 + k
        cells[f"A{r}"], cells[f"B{r}"] = m, g
        cells[f"C{r}"] = f"=$B$2*B{r}*$B$3*$B$4"
    cells.update({"A21": "total", "B21": "=SUM(B9:B20)", "C21": "=SUM(C9:C20)",
                  "A22": "capacity factor (AC)", "C22": "=C21/(B5*B6)",
                  "A23": "check: total GHI vs data pack", "C23": "=B21-E2",
                  "D2": "data pack annual GHI", "E2": 1947.2})
    if with_errors:
        cells["C14"] = 15000                                  # 1 overwritten formula
        cells["C17"] = "=$B$2*B17*0.85*$B$4"                  # 2 number typed in
        cells["C19"] = "=$B$2*B18*$B$3*$B$4"                  # 3 wrong row
        cells["C21"] = "=SUM(C9:C19)"                         # 4 range one short
        cells["C22"] = "=C21/(B5*B7)"                         # 5 empty cell B7
        cells["E3"], cells["E4"] = "=E4+1", "=E3*2"           # 6 circular pair
    return Sheet(cells, names={"dc_mwp": "B2"})


def main() -> None:
    ghi = monthly_ghi()
    bad = build(ghi, True)
    findings = audit(bad)
    lines = ["audit of the yield sheet with planted mistakes:"]
    lines += [f"  {f}" for f in findings]
    try:
        total_bad = bad.value("C21")
    except Exception as e:                                    # pragma: no cover
        total_bad = float("nan")
        lines.append(f"  evaluation failed: {e}")
    good = build(ghi, False)
    assert audit(good) == []
    total = good.value("C21")
    cf = good.value("C22")
    lines += [f"total with mistakes {total_bad:,.0f} MWh; corrected sheet {total:,.0f} MWh, "
              f"capacity factor {cf:.3f}",
              f"check cell C23 (sum of months - data pack): {good.value('C23'):+.1f} kWh/m2"]
    emit("a_sheet_audit", lines)
    h = datapack.load_hourly()
    p = np.asarray(sc.pv_ac_power_mw(h["ghi_wm2"], 60, 50))
    p_unclipped = 60 * h["ghi_wm2"].to_numpy() / 1000 * 0.85 * 0.98
    emit("a_sheet_check", [
        "independent spot check in Python (hourly, chapter 1 model):",
        f"  without the inverter limit {p_unclipped.sum():,.0f} MWh (sheet: {total:,.0f})",
        f"  with the 50 MW limit       {p.sum():,.0f} MWh; the monthly sheet cannot see "
        f"clipping ({p_unclipped.sum() - p.sum():.1f} MWh)",
        f"  one hand check, January: 60 x {ghi[0]} x 0.85 x 0.98 = "
        f"{60 * ghi[0] * 0.85 * 0.98:,.0f} MWh = cell C9 {good.value('C9'):,.0f}",
    ])
    u_rel = 0.04                                              # A-029: irradiation 4 %
    months = [good.value(f"C{9 + k}") for k in range(12)]
    u_month = [x * u_rel for x in months]
    u_indep = sum(u ** 2 for u in u_month) ** 0.5
    emit("a_sheet_uncert", [
        "uncertainty column D = C x 4 % (A-029, annual irradiation, one standard deviation):",
        f"  June {months[5]:,.0f} +- {u_month[5]:,.0f} MWh; December {months[11]:,.0f} +- "
        f"{u_month[11]:,.0f} MWh",
        f"  year, months fully correlated (one common error): +- {sum(u_month):,.0f} MWh "
        f"({100 * sum(u_month) / total:.1f} %)",
        f"  year, months independent (root-sum-square):     +- {u_indep:,.0f} MWh "
        f"({100 * u_indep / total:.1f} %)",
        "  say which case applies: a pyranometer calibration error is common to",
        "  all months; weather noise is not",
    ])
    rows = ["  cell  content"]
    for c in ("B2", "B3", "C9", "C10", "C20", "C21", "C22"):
        rows.append(f"  {c:5s} {good.cells[c]}")
    emit("a_sheet_cells", ["formulas of the corrected sheet (inputs in B2:B6):"] + rows)


if __name__ == "__main__":
    main()
