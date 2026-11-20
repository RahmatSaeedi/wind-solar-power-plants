"""Tests of plantp.architecture (chapter 18). Hand values in comments."""
import math

import numpy as np
import pytest

from plantp import architecture as ar


def test_chains():
    assert ar.chain(0.98, 0.98) == pytest.approx(0.9604)
    ac = ar.ac_coupled(0.98, 0.98, 0.90)
    # 0.98 x 0.98 x 0.90 x 0.98 = 0.8471
    assert ac["pv_to_grid_via_battery"] == pytest.approx(0.98 * 0.98 * 0.90 * 0.98)
    dc = ar.dc_coupled(0.98, 0.99, 0.90)
    # 0.99 x 0.90 x 0.99 x 0.98 = 0.8644
    assert dc["pv_to_grid_via_battery"] == pytest.approx(0.99 * 0.90 * 0.99 * 0.98)
    assert dc["pv_to_grid_via_battery"] > ac["pv_to_grid_via_battery"]


def test_circuits():
    # 100 MW at 132 kV, pf 1: I = 100 / (sqrt3 x 132) = 0.4374 kA
    assert float(ar.current_ka(100, 132)) == pytest.approx(0.4374, abs=1e-4)
    # loss = 3 I^2 R = R (P/V)^2 for pf 1
    assert float(ar.loss_mw(100, 132, 0.847)) == pytest.approx(0.847 * (100 / 132) ** 2)
    assert float(ar.drop_pct(100, 132, 0.847, 2.824)) == pytest.approx(0.486, abs=1e-3)
    # 132 kV, 0.2 uF/km, 7 km: 132^2 x 314.16 x 0.2e-6 x 7 = 7.66 Mvar
    assert ar.charging_mvar(132, 0.2, 7) == pytest.approx(7.66, abs=0.01)


def test_unserved():
    p = np.full(8760, 40.0)
    assert ar.unserved_mwh(p, 0.5, 20) == pytest.approx(0.5 * 20 * 40)
    assert ar.unserved_mwh(p, 0.5, 20, circuits=2, rating_mw=100) == 0.0


def test_breakdown_and_interfaces():
    root = ar.Node("plant", "plant").add(
        ar.Node("wind", "system").add(ar.Node("turbine", "equipment", 12).add(
            ar.Node("blade", "unit", 3))))
    counts = {n.name: k for n, k, _ in root.walk()}
    assert counts["blade"] == 36 and counts["turbine"] == 12
    ok = ar.Interface("I1", "electrical", "inverter", "transformer", "LV kV", 0.6, 0.6, 0.02)
    bad = ar.Interface("I2", "electrical", "inverter", "transformer", "LV kV", 0.6, 0.69, 0.02)
    proto = ar.Interface("I3", "comms", "BESS", "PPC", "protocol", "Modbus TCP",
                         {"IEC 61850", "IEC 60870-5-104"})
    assert ok.mismatch() == "" and bad.mismatch() and proto.mismatch()


def test_water_balance():
    stock, unmet = ar.water_balance([100] * 3, {"use": [50, 200, 50]}, 300, 100)
    # usable 200: 200+100-50=250 -> 200; 200+100-200=100; 100+100-50=150
    assert list(stock) == [200, 100, 150] and unmet.sum() == 0
    stock, unmet = ar.water_balance([0, 0], {"use": [150, 150]}, 300, 100)
    assert unmet[1] == pytest.approx(100.0)                       # reserve untouched
