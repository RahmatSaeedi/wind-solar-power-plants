"""Tests for plantp.finance (chapter 21) against hand calculations."""
import numpy as np
import pytest

from plantp import finance as fn


def test_index_and_fisher():
    assert list(fn.index(0.1, 3)) == pytest.approx([1.0, 1.1, 1.21])
    assert fn.real_to_nominal_rate(0.04, 0.025) == pytest.approx(0.066)


def test_pv_irr():
    assert fn.pv([110.0], 0.10) == pytest.approx(100.0)
    assert fn.irr([-100, 110]) == pytest.approx(0.10, abs=1e-7)
    assert fn.irr([-100, 60, 60]) == pytest.approx(0.1307, abs=1e-4)


def test_lcoe():
    # capex 100, no costs, 10 MWh a year for 2 years at 0 %: 100/20 = 5
    assert fn.lcoe(100.0, [0, 0], [10, 10], 0.0) == pytest.approx(5.0)


def test_construction_idc():
    spend, idc = fn.construction(100.0, [1, 1], 0.10)
    assert list(spend) == [50, 50]
    # balances 25 and 75 on average
    assert list(idc) == pytest.approx([2.5, 7.5])


def test_tax_losses():
    tax = fn.tax_schedule([10, 10, 50], [30, 0, 0], [0, 0, 0], 0.25)
    # year 1 loss 20; year 2 base 10 - 20 -> loss 10; year 3 base 50 - 10 = 40
    assert list(tax) == pytest.approx([0, 0, 10])


def test_annuity_and_sculpted():
    i, p, b = fn.annuity_debt(100.0, 0.10, 2)
    assert p.sum() == pytest.approx(100.0)
    assert (i + p)[0] == pytest.approx((i + p)[1])
    debt, i2, p2, b2 = fn.sculpted_debt([22.0, 22.0], 1.10, 0.10)
    # service 20 each year: PV at 10 % = 34.71
    assert debt == pytest.approx(20 / 1.1 + 20 / 1.21)
    assert p2.sum() == pytest.approx(debt)
    assert list(fn.dscr([22, 22], i2 + p2)) == pytest.approx([1.1, 1.1])


def test_llcr_equals_dscr_when_sculpted():
    debt, i, p, b = fn.sculpted_debt([30, 30, 30], 1.25, 0.08)
    assert fn.llcr([30, 30, 30], b, 0.08, 3)[0] == pytest.approx(1.25)


def test_size_debt_and_check():
    d, why = fn.size_debt({"P50": [30] * 3, "P90": [24] * 3}, {"P50": 1.3, "P90": 1.2},
                          0.08, 3, 100.0, 0.8)
    assert why.startswith("DSCR")
    rows = [(50, 20, 0, 0, 5, 15)]
    assert fn.check_dscr(rows) == pytest.approx([1.5])


def test_breakeven():
    assert fn.breakeven(lambda x: 2 * x - 3, 0, 10) == pytest.approx(1.5, abs=1e-5)
