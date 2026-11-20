"""Tests of plantp.numerics against hand calculations and numpy/scipy (chapter 3)."""
import math

import numpy as np
import pytest
from scipy import integrate

from plantp import numerics as nm


def test_bisection_newton_secant_find_sqrt2():
    f = lambda x: x * x - 2            # noqa: E731
    b = nm.bisection(f, 0, 2, tol=1e-12)
    n = nm.newton(f, lambda x: 2 * x, 1.0)
    s = nm.secant(f, 1.0, 2.0)
    for r in (b, n, s):
        assert r.root == pytest.approx(math.sqrt(2), abs=1e-10)
    assert n.iterations < s.iterations < b.iterations


def test_bisection_requires_a_sign_change():
    with pytest.raises(ValueError):
        nm.bisection(lambda x: x * x + 1, -1, 1)


def test_newton_zero_derivative():
    with pytest.raises(ZeroDivisionError):
        nm.newton(lambda x: x * x - 1, lambda x: 2 * x, 0.0)


def test_lerp_table_policies():
    xs, ys = [3, 4, 5], [0, 100, 300]
    assert nm.lerp_table(4.5, xs, ys) == pytest.approx(200)
    with pytest.raises(ValueError):
        nm.lerp_table(6, xs, ys)
    assert nm.lerp_table(6, xs, ys, outside="clamp") == pytest.approx(300)
    assert nm.lerp_table(6, xs, ys, outside="zero") == 0.0


def test_lagrange_reproduces_a_quadratic():
    xs = [0.0, 1.0, 2.0]
    ys = [x * x - 1 for x in xs]
    assert nm.lagrange(1.5, xs, ys) == pytest.approx(1.25)


def test_trapezoid_and_simpson_orders():
    x = np.linspace(0, math.pi, 9)
    y = np.sin(x)
    dx = x[1] - x[0]
    assert nm.trapezoid(y, dx) == pytest.approx(integrate.trapezoid(y, x))
    assert abs(nm.simpson(y, dx) - 2) < abs(nm.trapezoid(y, dx) - 2)
    with pytest.raises(ValueError):
        nm.simpson(y[:-1], dx)


def test_richardson_improves_trapezoid():
    f = np.sin
    coarse = nm.trapezoid(f(np.linspace(0, math.pi, 5)), math.pi / 4)
    fine = nm.trapezoid(f(np.linspace(0, math.pi, 9)), math.pi / 8)
    better = nm.richardson(coarse, fine, order=2)
    assert abs(better - 2) < abs(fine - 2) / 10


def test_euler_and_rk4_on_exponential_decay():
    f = lambda t, y: -y / 10.0         # noqa: E731
    _, ye = nm.euler(f, 1.0, 0, 10, 1.0)
    _, yr = nm.rk4(f, 1.0, 0, 10, 1.0)
    exact = math.exp(-1)
    assert abs(yr[-1] - exact) < 1e-5 < abs(ye[-1] - exact)


def test_euler_unstable_for_large_step():
    f = lambda t, y: -y / 1.0          # noqa: E731
    _, y = nm.euler(f, 1.0, 0, 20, 2.5)  # dt > 2 tau
    assert abs(y[-1]) > 1


def test_solve_gauss_matches_numpy_and_needs_pivoting():
    a = [[0.0, 2.0, 1.0], [1.0, 1.0, 1.0], [2.0, 1.0, 0.0]]
    b = [5.0, 6.0, 4.0]
    assert np.allclose(nm.solve_gauss(a, b), np.linalg.solve(a, b))
    with pytest.raises(np.linalg.LinAlgError):
        nm.solve_gauss([[1, 2], [2, 4]], [1, 2])


def test_power_iteration_dominant_eigenvalue():
    a = np.array([[2.0, 1.0], [1.0, 3.0]])
    lam, v, _ = nm.power_iteration(a)
    assert lam == pytest.approx(max(np.linalg.eigvalsh(a)), rel=1e-9)


def test_condition_number_of_nearly_singular_matrix():
    assert nm.condition_number([[1, 1], [1, 1.0001]]) > 1e4
    assert nm.condition_number(np.eye(3)) == pytest.approx(1.0)
