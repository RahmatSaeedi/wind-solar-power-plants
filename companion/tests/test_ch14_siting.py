"""Tests of plantp.siting (chapter 14). Hand values in comments."""
import math

import numpy as np
import pytest

from plantp import siting as st


def test_slope_and_aspect_of_a_plane():
    g = st.Grid(0, 0, 10.0, 20, 15)
    x, y = g.mesh()
    z = 0.05 * x                                  # rises 5 m per 100 m to the east
    assert np.allclose(st.slope_percent(z, 10.0), 5.0)
    assert np.allclose(st.aspect_deg(z, 10.0), 270.0)   # faces west (downhill)


def test_polygons_and_distances():
    sq = [(0, 0), (100, 0), (100, 100), (0, 100)]
    assert st.polygon_area(sq) == pytest.approx(10000.0)
    inside = st.in_polygon(np.array([50, 150]), np.array([50, 50]), sq)
    assert inside.tolist() == [True, False]
    assert st.distance_to(3.0, 4.0, [(0, 0), (10, 10)]) == pytest.approx(5.0)
    d = st.distance_to_segments(np.array([5.0]), np.array([3.0]), [(0, 0), (10, 0)])
    assert d[0] == pytest.approx(3.0)


def test_speedup_is_zero_on_flat_ground_and_positive_on_a_hill():
    g = st.Grid(0, 0, 50.0, 60, 60)
    x, y = g.mesh()
    flat = np.full(x.shape, 1200.0)
    assert np.allclose(st.hill_speedup(flat, 50.0, 500.0), 0.0)
    hill = 1200 + 40 * np.exp(-((x - 1500) ** 2 + (y - 1500) ** 2) / 300.0 ** 2)
    s = st.hill_speedup(hill, 50.0, 500.0)
    assert s[g.index(1500, 1500)] > 0.05 and s[g.index(200, 200)] == pytest.approx(0, abs=1e-6)


def test_networks():
    pts = [(0, 0), (1, 0), (0, 1), (1, 1)]
    edges, total = st.minimum_spanning_tree(pts)
    assert len(edges) == 3 and total == pytest.approx(3.0)
    strings, length = st.radial_strings([(0, 1), (0, 2), (1, 0), (2, 0)], (0, 0), 2)
    assert sorted(len(s) for s in strings) == [2, 2] and length == pytest.approx(4.0)


def test_least_cost_path_straight_and_detour():
    cost = np.ones((5, 9))
    path, c = st.least_cost_path(cost, (2, 0), (2, 8), 10.0)
    assert st.path_length(path, 10.0) == pytest.approx(80.0) and c == pytest.approx(80.0)
    cost[1:4, 4] = np.inf                         # a wall with gaps at rows 0 and 4
    path, _ = st.least_cost_path(cost, (2, 0), (2, 8), 10.0)
    assert all(not (j in (1, 2, 3) and i == 4) for j, i in path)


def test_cut_fill_balances_and_flicker_geometry():
    cut, fill, lv = st.cut_fill(np.array([[0.0, 2.0], [0.0, 2.0]]), 10.0)
    assert cut == pytest.approx(200.0) and fill == pytest.approx(200.0) and lv == 1.0
    # turbine 500 m south of the house, hub 100 m: sun due south at
    # elevation atan(100/500) = 11.31 deg puts the hub on the line of sight
    el = np.array([math.degrees(math.atan(100 / 500)), 40.0])
    m = st.flicker_minutes((0, 0), [(0, -500)], 100.0, 75.0, el, np.array([180.0, 180.0]), 5.0)
    assert m.tolist() == [5.0, 0.0]


def test_bilinear_sampling_follows_a_plane():
    g = st.Grid(0, 0, 50.0, 10, 10)
    x, y = g.mesh()
    z = 0.1 * x + 0.02 * y
    v = g.interp(z, [137.0, 260.0], [88.0, 301.0])
    assert v == pytest.approx([0.1 * 137 + 0.02 * 88, 0.1 * 260 + 0.02 * 301])
