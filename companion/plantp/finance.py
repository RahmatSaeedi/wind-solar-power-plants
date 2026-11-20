"""Project economics and project finance (chapter 21): escalation and
real/nominal conversion, capital phasing with interest during
construction, straight-line depreciation and tax with losses carried
forward, working capital, cash flow available for debt service (CFADS),
annuity and sculpted debt, debt sizing by cover ratio and gearing, the
debt service reserve, DSCR and LLCR, equity IRR, levelised cost, an
independent DSCR check and a break-even search.

Annual periods; money in k u (thousand units). Every rate, ratio and
term is a teaching value (A-304 onwards): transaction documents and
lenders' definitions govern real projects.
"""
from __future__ import annotations

import numpy as np


# ------------------------------------------------------------ time value
def index(rate: float, years: int, base_year: int = 0) -> np.ndarray:
    """Escalation index (1 + rate)^(t - base_year) for t = 0..years-1."""
    t = np.arange(years) - base_year
    return (1.0 + rate) ** t


def real_to_nominal_rate(real: float, inflation: float) -> float:
    """Fisher relation: (1 + nominal) = (1 + real)(1 + inflation)."""
    return (1 + real) * (1 + inflation) - 1


def pv(cash, rate: float, start: int = 1) -> float:
    """Present value of cash[0..] received at the end of years start,
    start + 1, ..."""
    cash = np.asarray(cash, float)
    t = np.arange(start, start + cash.size)
    return float((cash / (1 + rate) ** t).sum())


def irr(cash, low: float = -0.99, high: float = 1.0, tol: float = 1e-9) -> float:
    """Internal rate of return of cash[0..] at years 0, 1, ... by
    bisection (one sign change assumed; nan if none in the bracket)."""
    cash = np.asarray(cash, float)

    def f(r):
        return float((cash / (1 + r) ** np.arange(cash.size)).sum())
    fl, fh = f(low), f(high)
    if fl * fh > 0:
        return float("nan")
    for _ in range(200):
        mid = 0.5 * (low + high)
        fm = f(mid)
        if abs(fm) < tol:
            break
        if fl * fm < 0:
            high, fh = mid, fm
        else:
            low, fl = mid, fm
    return 0.5 * (low + high)


def lcoe(capex: float, costs, energy, rate: float) -> float:
    """Levelised cost: (capex + PV costs) / PV energy (energy and costs
    of operating years 1..n)."""
    return (capex + pv(costs, rate)) / pv(energy, rate)


# ------------------------------------------------------------ construction
# [start: idc]
def construction(capex: float, phasing, rate: float, fee: float = 0.0):
    """Capital spent over construction years with the share 'phasing'
    each year, paid mid-year; interest during construction (IDC) on the
    debt-funded part at 'rate', capitalised. Returns (spend by year,
    IDC by year)."""
    ph = np.asarray(phasing, float)
    spend = capex * ph / ph.sum()
    drawn = np.cumsum(spend) - spend / 2           # average balance
    idc = drawn * rate
    return spend, idc + fee * spend
# [end: idc]


# ------------------------------------------------------------ tax
def tax_schedule(ebitda, depreciation, interest, rate: float):
    """Tax paid each year on EBITDA - depreciation - interest, with tax
    losses carried forward without limit (teaching rule)."""
    ebitda, dep, intr = (np.asarray(x, float) for x in (ebitda, depreciation, interest))
    loss = 0.0
    tax = np.zeros_like(ebitda)
    for k in range(ebitda.size):
        base = ebitda[k] - dep[k] - intr[k] - loss
        if base > 0:
            tax[k] = base * rate
            loss = 0.0
        else:
            loss = -base
    return tax


def straight_line(cost: float, years: int, horizon: int) -> np.ndarray:
    d = np.zeros(horizon)
    d[:years] = cost / years
    return d


# ------------------------------------------------------------ debt
# [start: debt]
def annuity_debt(principal: float, rate: float, tenor: int):
    """Level payments: returns (interest, principal, balance at start)."""
    pay = principal * rate / (1 - (1 + rate) ** -tenor)
    bal = principal
    i_, p_, b_ = [], [], []
    for _ in range(tenor):
        b_.append(bal)
        i = bal * rate
        i_.append(i)
        p_.append(pay - i)
        bal -= pay - i
    return np.array(i_), np.array(p_), np.array(b_)


def sculpted_debt(cfads, target_dscr: float, rate: float):
    """Debt service = CFADS / target DSCR each year; the debt it can
    repay is the PV of that service. Returns (debt, interest,
    principal, balance at start)."""
    ds = np.asarray(cfads, float) / target_dscr
    debt = pv(ds, rate)
    bal = debt
    i_, p_, b_ = [], [], []
    for d in ds:
        b_.append(bal)
        i = bal * rate
        i_.append(i)
        p_.append(d - i)
        bal -= d - i
    return debt, np.array(i_), np.array(p_), np.array(b_)
# [end: debt]


def size_debt(cfads_cases: dict, dscr_cases: dict, rate: float, tenor: int,
              cost: float, max_gearing: float) -> tuple[float, str]:
    """Largest sculpted debt that holds every case's target DSCR and the
    gearing cap; returns (debt, binding constraint)."""
    best, why = max_gearing * cost, "gearing"
    for k, cf in cfads_cases.items():
        d, *_ = sculpted_debt(np.asarray(cf, float)[:tenor], dscr_cases[k], rate)
        if d < best:
            best, why = d, f"DSCR {dscr_cases[k]:.2f} on {k}"
    return best, why


# [start: ratios]
def dscr(cfads, debt_service) -> np.ndarray:
    """Debt service cover ratio per period: CFADS / scheduled debt
    service (periods without debt service give nan)."""
    cf, ds = np.asarray(cfads, float), np.asarray(debt_service, float)
    return np.where(ds > 0, cf / np.where(ds > 0, ds, 1.0), np.nan)


def llcr(cfads, balance_start, rate: float, tenor: int) -> np.ndarray:
    """Loan life cover ratio at the start of each loan year: PV of the
    CFADS of the remaining loan life at the debt rate / debt outstanding."""
    cf = np.asarray(cfads, float)
    out = np.full(tenor, np.nan)
    for k in range(tenor):
        if balance_start[k] > 1e-9:
            out[k] = pv(cf[k:tenor], rate) / balance_start[k]
    return out
# [end: ratios]


def check_dscr(rows) -> list[float]:
    """Independent check: DSCR recomputed line by line from a plain list
    of (revenue, opex, tax, wc_change, interest, principal) rows."""
    out = []
    for rev, opx, tax, dwc, i, p in rows:
        cfads = rev - opx - tax - dwc
        out.append(cfads / (i + p) if i + p > 0 else float("nan"))
    return out


def breakeven(f, lo: float, hi: float, target: float = 0.0, tol: float = 1e-6) -> float:
    """Value x in [lo, hi] where f(x) = target, by bisection (f monotone)."""
    flo = f(lo) - target
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        fm = f(mid) - target
        if abs(fm) < tol or hi - lo < tol:
            return mid
        if (fm > 0) == (flo > 0):
            lo, flo = mid, fm
        else:
            hi = mid
    return 0.5 * (lo + hi)
