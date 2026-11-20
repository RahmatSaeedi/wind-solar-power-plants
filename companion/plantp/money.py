"""Mathematics of money over time, chapter 3 (finance itself is chapter 21).

    geometric_sum       a + a q + ... + a q^(n-1)
    discount_factors    1 / (1 + r)^t for t = 1..n (end-of-year convention)
    present_value       sum of cash_t / (1 + r)^t, t = 1..n
    annuity_factor      present value of 1 per year for n years
    capital_recovery    equal annual payment that repays 1 today (inverse of annuity_factor)
    discounted_energy   sum of E_1 (1 - d)^(t-1) / (1 + r)^t, with annual degradation d
    lcoe                (capex + PV of opex) / discounted energy
    npv, irr            chapter 5: cash[0] at year 0; IRR by bisection
    project_cash_flow   chapter 5: revenue, CFADS, annuity debt service, DSCR, equity cash

All amounts are in whatever money unit the caller uses; the book uses fictional units.
Rates are fractions per year (0.07 = 7 %).
"""
from __future__ import annotations

import numpy as np


def geometric_sum(a: float, q: float, n: int) -> float:
    if n < 0:
        raise ValueError("n must be >= 0")
    if q == 1.0:
        return a * n
    return a * (1.0 - q ** n) / (1.0 - q)


def discount_factors(rate: float, years: int) -> np.ndarray:
    if rate <= -1.0:
        raise ValueError("rate must be > -1")
    t = np.arange(1, years + 1)
    return 1.0 / (1.0 + rate) ** t


def present_value(cash, rate: float) -> float:
    cash = np.asarray(cash, dtype=float)
    return float(cash @ discount_factors(rate, cash.size))


def annuity_factor(rate: float, years: int) -> float:
    if rate == 0.0:
        return float(years)
    return (1.0 - (1.0 + rate) ** -years) / rate


def capital_recovery(rate: float, years: int) -> float:
    return 1.0 / annuity_factor(rate, years)


def discounted_energy(e_first: float, rate: float, years: int,
                      degradation: float = 0.0) -> float:
    t = np.arange(1, years + 1)
    return float(np.sum(e_first * (1.0 - degradation) ** (t - 1) / (1.0 + rate) ** t))


def lcoe(capex: float, opex_per_year: float, energy_pv: float, rate: float,
         years: int) -> float:
    """Levelised cost: capex at year 0, constant opex at each year end, energy already
    discounted (see discounted_energy)."""
    if energy_pv <= 0:
        raise ValueError("discounted energy must be positive")
    return (capex + opex_per_year * annuity_factor(rate, years)) / energy_pv


# ---- chapter 5: an auditable project cash flow ---------------------------------------
def npv(rate: float, cash) -> float:
    """Net present value with cash[0] at year 0 (not discounted)."""
    c = np.asarray(cash, dtype=float)
    t = np.arange(c.size)
    return float(np.sum(c / (1.0 + rate) ** t))


def irr(cash, low: float = -0.9, high: float = 1.0, tol: float = 1e-10) -> float:
    """Internal rate of return by bisection (requires one sign change of NPV)."""
    f_low = npv(low, cash)
    if f_low * npv(high, cash) > 0:
        raise ValueError("NPV does not change sign in the bracket")
    for _ in range(200):
        mid = 0.5 * (low + high)
        f_mid = npv(mid, cash)
        if abs(f_mid) < tol or high - low < tol:
            return mid
        if f_low * f_mid < 0:
            high = mid
        else:
            low, f_low = mid, f_mid
    return 0.5 * (low + high)


def project_cash_flow(energy_mwh_yr1: float, price: float, capex: float,
                      opex: float, years: int, degradation: float,
                      debt_share: float, debt_rate: float,
                      debt_years: int) -> dict:
    """Year-by-year table (lists, year 0 first): revenue, opex, CFADS,
    debt service, DSCR, equity cash. Annuity debt; no tax, no inflation
    (teaching model)."""
    debt = capex * debt_share
    service = debt * capital_recovery(debt_rate, debt_years) if debt else 0.0
    rows = {"year": [0], "revenue": [0.0], "opex": [0.0], "cfads": [0.0],
            "debt_service": [0.0], "dscr": [float("nan")],
            "equity_cash": [-(capex - debt)]}
    for y in range(1, years + 1):
        rev = energy_mwh_yr1 * (1 - degradation) ** (y - 1) * price
        cfads = rev - opex
        ds = service if y <= debt_years else 0.0
        rows["year"].append(y)
        rows["revenue"].append(rev)
        rows["opex"].append(opex)
        rows["cfads"].append(cfads)
        rows["debt_service"].append(ds)
        rows["dscr"].append(cfads / ds if ds > 0 else float("nan"))
        rows["equity_cash"].append(cfads - ds)
    return rows
