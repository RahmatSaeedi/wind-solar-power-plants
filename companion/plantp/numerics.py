"""Numerical methods written out plainly for chapter 3 (and reused later).

Each function is the textbook algorithm, short enough to read in the book, and is
tested in companion/tests/test_numerics.py against hand calculations and against
numpy/scipy. Production code would call numpy/scipy directly; the point here is to
see what those libraries do.

    root finding      bisection, newton, secant
    interpolation     lerp_table (with an explicit extrapolation policy), lagrange
    quadrature        trapezoid, simpson, richardson
    ODEs              euler, rk4 (fixed step, any number of states)
    linear algebra    solve_gauss (partial pivoting), power_iteration, condition_number
    PDE               heat_explicit_step (explicit finite differences, diffusion)
    optimisation      newton_minimise (finite-difference gradient and Hessian)
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable

import numpy as np


# ---- root finding ------------------------------------------------------------------
@dataclass
class RootResult:
    root: float
    iterations: int
    history: list[float] = field(default_factory=list)   # estimate after each step
    converged: bool = True


def bisection(f: Callable[[float], float], a: float, b: float, tol: float = 1e-10,
              max_iter: int = 200) -> RootResult:
    """Halve [a, b] until it is shorter than tol. f(a) and f(b) must differ in sign."""
    fa, fb = f(a), f(b)
    if fa == 0:
        return RootResult(a, 0, [a])
    if fb == 0:
        return RootResult(b, 0, [b])
    if fa * fb > 0:
        raise ValueError("f(a) and f(b) must have opposite signs")
    history = []
    for k in range(1, max_iter + 1):
        m = 0.5 * (a + b)
        fm = f(m)
        history.append(m)
        if fm == 0 or 0.5 * (b - a) < tol:
            return RootResult(m, k, history)
        if fa * fm < 0:
            b, fb = m, fm
        else:
            a, fa = m, fm
    return RootResult(0.5 * (a + b), max_iter, history, converged=False)


def newton(f: Callable[[float], float], df: Callable[[float], float], x0: float,
           tol: float = 1e-12, max_iter: int = 50) -> RootResult:
    """Newton's method: x <- x - f(x)/f'(x). Fast near a simple root; may diverge."""
    x = x0
    history = [x]
    for k in range(1, max_iter + 1):
        d = df(x)
        if d == 0:
            raise ZeroDivisionError("zero derivative: Newton step undefined")
        step = f(x) / d
        x -= step
        history.append(x)
        if abs(step) < tol * max(1.0, abs(x)):
            return RootResult(x, k, history)
    return RootResult(x, max_iter, history, converged=False)


def secant(f: Callable[[float], float], x0: float, x1: float, tol: float = 1e-12,
           max_iter: int = 100) -> RootResult:
    """Secant method: Newton with the derivative replaced by a difference quotient."""
    f0, f1 = f(x0), f(x1)
    history = [x0, x1]
    for k in range(1, max_iter + 1):
        if f1 == f0:
            raise ZeroDivisionError("flat secant")
        x2 = x1 - f1 * (x1 - x0) / (f1 - f0)
        history.append(x2)
        if abs(x2 - x1) < tol * max(1.0, abs(x2)):
            return RootResult(x2, k, history)
        x0, f0, x1, f1 = x1, f1, x2, f(x2)
    return RootResult(x1, max_iter, history, converged=False)


# ---- interpolation -----------------------------------------------------------------
def lerp_table(x, xs, ys, outside: str = "error"):
    """Linear interpolation in a table (xs increasing).

    outside: what to do beyond the table - "error" (refuse), "clamp" (hold the end
    value) or "zero" (return 0, e.g. a power curve outside cut-in..cut-out).
    Extrapolating a table silently is a classic modelling error; the caller must
    choose a policy.
    """
    xs = np.asarray(xs, dtype=float)
    ys = np.asarray(ys, dtype=float)
    if np.any(np.diff(xs) <= 0):
        raise ValueError("table x values must be strictly increasing")
    x = np.asarray(x, dtype=float)
    beyond = (x < xs[0]) | (x > xs[-1])
    if np.any(beyond) and outside == "error":
        raise ValueError("x outside the table; choose outside='clamp' or 'zero'")
    y = np.interp(x, xs, ys)
    if outside == "zero":
        y = np.where(beyond, 0.0, y)
    return y if y.ndim else float(y)


def lagrange(x: float, xs, ys) -> float:
    """Value at x of the polynomial through all points (xs, ys)."""
    total = 0.0
    for i, (xi, yi) in enumerate(zip(xs, ys)):
        term = yi
        for j, xj in enumerate(xs):
            if j != i:
                term *= (x - xj) / (xi - xj)
        total += term
    return total


# ---- quadrature --------------------------------------------------------------------
def trapezoid(y, dx: float) -> float:
    """Composite trapezoidal rule for equally spaced samples y."""
    y = np.asarray(y, dtype=float)
    if y.size < 2:
        raise ValueError("need at least two samples")
    return float(dx * (y.sum() - 0.5 * (y[0] + y[-1])))


def simpson(y, dx: float) -> float:
    """Composite Simpson rule; needs an odd number of samples (even intervals)."""
    y = np.asarray(y, dtype=float)
    if y.size < 3 or y.size % 2 == 0:
        raise ValueError("Simpson's rule needs an odd number of samples (>= 3)")
    return float(dx / 3.0 * (y[0] + y[-1] + 4 * y[1:-1:2].sum() + 2 * y[2:-1:2].sum()))


def richardson(coarse: float, fine: float, order: int, ratio: float = 2.0) -> float:
    """Richardson extrapolation: combine two estimates whose error ~ h^order."""
    r = ratio ** order
    return (r * fine - coarse) / (r - 1.0)


# ---- ordinary differential equations -------------------------------------------------
def euler(f: Callable, y0, t0: float, t1: float, dt: float):
    """Explicit Euler: y_{n+1} = y_n + dt f(t_n, y_n). Returns (t, y) arrays."""
    n = int(round((t1 - t0) / dt))
    t = t0 + dt * np.arange(n + 1)
    y = np.empty((n + 1,) + np.shape(y0))
    y[0] = y0
    for k in range(n):
        y[k + 1] = y[k] + dt * np.asarray(f(t[k], y[k]))
    return t, y


def rk4(f: Callable, y0, t0: float, t1: float, dt: float):
    """Classical fourth-order Runge-Kutta with a fixed step. Returns (t, y)."""
    n = int(round((t1 - t0) / dt))
    t = t0 + dt * np.arange(n + 1)
    y = np.empty((n + 1,) + np.shape(y0))
    y[0] = y0
    for k in range(n):
        tk, yk = t[k], y[k]
        k1 = np.asarray(f(tk, yk))
        k2 = np.asarray(f(tk + dt / 2, yk + dt / 2 * k1))
        k3 = np.asarray(f(tk + dt / 2, yk + dt / 2 * k2))
        k4 = np.asarray(f(tk + dt, yk + dt * k3))
        y[k + 1] = yk + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return t, y


# ---- linear algebra -----------------------------------------------------------------
def solve_gauss(a, b):
    """Gaussian elimination with partial pivoting, then back substitution."""
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    n = len(b)
    if a.shape != (n, n):
        raise ValueError("matrix must be square and match b")
    for col in range(n):
        pivot = col + int(np.argmax(np.abs(a[col:, col])))
        if abs(a[pivot, col]) < 1e-14:
            raise np.linalg.LinAlgError("matrix is singular")
        if pivot != col:
            a[[col, pivot]] = a[[pivot, col]]
            b[[col, pivot]] = b[[pivot, col]]
        for row in range(col + 1, n):
            factor = a[row, col] / a[col, col]
            a[row, col:] -= factor * a[col, col:]
            b[row] -= factor * b[col]
    x = np.zeros(n)
    for row in range(n - 1, -1, -1):
        x[row] = (b[row] - a[row, row + 1:] @ x[row + 1:]) / a[row, row]
    return x


def power_iteration(a, iterations: int = 500, tol: float = 1e-12, seed: int = 1):
    """Dominant eigenvalue (largest |lambda|) and its eigenvector by repeated multiplication."""
    a = np.asarray(a, dtype=float)
    v = np.random.default_rng(seed).random(a.shape[0])
    v /= np.linalg.norm(v)
    lam = 0.0
    for k in range(1, iterations + 1):
        w = a @ v
        lam_new = float(v @ w)
        v = w / np.linalg.norm(w)
        if abs(lam_new - lam) < tol * max(1.0, abs(lam_new)):
            return lam_new, v, k
        lam = lam_new
    return lam, v, iterations


def heat_explicit_step(u, r: float, left: float, right: float | None = None):
    """One explicit finite-difference step of u_t = alpha u_zz on equally spaced nodes.

    r = alpha dt / dz^2 must not exceed 1/2 (stability). left is the boundary value at the
    first node; right is the value at the last node, or None for a zero-flux (insulated) end.
    """
    if r > 0.5:
        raise ValueError(f"unstable: r = {r:.3f} > 0.5")
    u = np.asarray(u, dtype=float)
    new = u.copy()
    new[1:-1] = u[1:-1] + r * (u[2:] - 2.0 * u[1:-1] + u[:-2])
    new[0] = left
    new[-1] = new[-2] if right is None else right
    return new


def newton_minimise(f: Callable, x0, h: float = 1e-4, tol: float = 1e-8,
                    max_iter: int = 50):
    """Minimise f(x) (x a vector) by Newton's method with finite-difference gradient and
    Hessian. Returns (x, iterations, history of |gradient|)."""
    x = np.array(x0, dtype=float)
    n = x.size
    hist = []
    for it in range(max_iter):
        g = np.zeros(n)
        hmat = np.zeros((n, n))
        e = np.eye(n) * h
        for i in range(n):
            g[i] = (f(x + e[i]) - f(x - e[i])) / (2 * h)
            for j in range(i, n):
                hmat[i, j] = hmat[j, i] = (f(x + e[i] + e[j]) - f(x + e[i] - e[j])
                                           - f(x - e[i] + e[j]) + f(x - e[i] - e[j])) / (4 * h * h)
        hist.append(float(np.linalg.norm(g)))
        if hist[-1] < tol:
            return x, it, hist
        x = x - np.linalg.solve(hmat, g)
    return x, max_iter, hist


def condition_number(a) -> float:
    """2-norm condition number: how much relative input errors can be amplified."""
    return float(np.linalg.cond(np.asarray(a, dtype=float)))
