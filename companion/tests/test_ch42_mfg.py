"""Chapter 42 turbine manufacturing arithmetic against hand calculations."""
import math

import numpy as np
import pytest

from plantp import turbinemfg as t


def test_composite_by_hand():
    vf = t.fibre_volume(0.70, 2.55, 1.15)
    assert vf == pytest.approx((0.70 / 2.55) / (0.70 / 2.55 + 0.30 / 1.15))
    rho_th = 1 / (0.70 / 2.55 + 0.30 / 1.15)
    assert t.void_content(rho_th, 0.70, 2.55, 1.15) == pytest.approx(0.0, abs=1e-12)
    assert t.void_content(0.98 * rho_th, 0.70, 2.55, 1.15) == pytest.approx(0.02)


def test_inserts_and_sets():
    assert t.insert_tension(1.0e6, 4, 1.0) == pytest.approx(1.0e6)
    assert t.set_unbalance([1.0, 1.0, 1.0]) == pytest.approx(0.0, abs=1e-12)
    assert t.set_unbalance([1.0, 0.0, 0.0]) == pytest.approx(1.0)
    sets = t.match_sets([5, 1, 4, 2, 6, 3])
    assert sorted(sum(sets, ())) == list(range(6))


def test_pod_and_power():
    assert t.pod(3.0, 3.0, 0.5)[0] == pytest.approx(0.5)
    assert t.filter_removal(200) == pytest.approx(0.995)
    assert t.back_to_back_power(1000, 1.0) == pytest.approx(0.0)
    assert t.back_to_back_power(1000, 0.95) == pytest.approx(1000 * (1 / 0.9025 - 1))


def test_spectrum_reads_a_sine():
    fs, n = 1024.0, 4096
    x = 0.7 * np.sin(2 * np.pi * 50.0 * np.arange(n) / fs)
    f, a = t.amplitude_spectrum(x, fs)
    assert t.band_peak(f, a, 50.0) == pytest.approx(0.7, rel=0.02)


def test_shrink_life_alignment():
    assert t.shrink_delta_t(1e-3, 1.0, 1e-5) == pytest.approx(100.0)
    assert t.halving_life(130, 120, 20) == pytest.approx(10.0)
    front, back = t.alignment_moves(0.2, 0.1, 0.5, 1.5)
    assert front == pytest.approx(-0.25) and back == pytest.approx(-0.35)
