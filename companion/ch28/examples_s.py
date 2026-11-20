"""Chapter 28 - expansion round 8: what a firmware change does to the
ride-through results, an independent check of the load flow by a second
method (Gauss-Seidel), and the events that require a study to be rerun.

Run from the project root:   python -m companion.ch28.examples_s
Writes companion/ch28/expected/s_*.txt. Teaching values.
"""
from __future__ import annotations

import numpy as np

from companion.ch28 import sources as src
from companion.ch28.common import emit
from plantp import gridstudy as gs


def firmware() -> None:
    t = np.arange(0, 1.5, 0.001)
    e = np.where((t >= 0.1) & (t < 0.25), 0.50, 1.0)
    z = gs.thevenin(900, 6, 122.2)
    lines = ["a firmware change raises the reactive-current gain from 2.0 to 2.5",
             "  (weak grid, the grid source dips to 0.50 pu for 150 ms)",
             "  quantity                        k 2.0 (studied)   k 2.5 (new)   rows hit"]
    out = {k: gs.frt_sim(t, e, z, 100 / 122.2, k=k) for k in (2.0, 2.5)}
    dip = (t > 0.15) & (t < 0.25)
    rows = [("POC voltage in the dip pu", lambda o: o["u"][dip].mean(), "G04, G06"),
            ("reactive power in the dip Mvar", lambda o: 122.2 * o["q"][dip].max(), "G06"),
            ("highest voltage after clearing pu", lambda o: o["u"][t > 0.25].max(), "G05"),
            ("active power back (90 %) s", lambda o: t[t >= 0.25][np.argmax(o["p"][t >= 0.25]
                                                                           >= 0.9 * 100 / 122.2)] - 0.25, "G07")]
    for name, f, hit in rows:
        lines.append(f"  {name:33s} {f(out[2.0]):15.2f}   {f(out[2.5]):11.2f}   {hit}")
    lines += ["  the dip voltage improves, but the overshoot after clearing",
              "  grows, and the larger reactive current now cuts active",
              "  current, so the recovery requirement applies where it did",
              "  not before - a change that helps one requirement can hurt",
              "  another: every compliance row touched by the changed",
              "  parameter is rerun, and the OEM's statement names them"]
    emit("s_firmware", lines)


# [start: gs]
def gauss_seidel(y: np.ndarray, s: np.ndarray, v0: float = 1.0,
                 tol: float = 1e-10, max_iter: int = 20000) -> tuple:
    """Second method for the same load flow: bus 0 is the slack, the
    others PQ with complex injections s (pu). Returns (V, iterations)."""
    n = len(s)
    v = np.ones(n, complex) * v0
    for it in range(1, max_iter + 1):
        biggest = 0.0
        for k in range(1, n):
            if y[k, k] == 0:
                continue
            sigma = y[k] @ v - y[k, k] * v[k]
            new = (np.conj(s[k] / v[k]) - sigma) / y[k, k]
            biggest = max(biggest, abs(new - v[k]))
            v[k] = new
        if biggest < tol:
            return v, it
    raise RuntimeError("Gauss-Seidel did not converge")
# [end: gs]


def independent() -> None:
    ps = {"wind": 1.0, "pv": 0.84}
    nr = src.solve(ps, 0.12)
    br = nr["branches"]
    y = gs.ybus(src.N, br)
    s = np.zeros(src.N, complex)
    for k, f in enumerate(src.FEEDERS):
        if f.kind in ps:
            s[13 + k] = complex(f.units * f.unit_mw * ps[f.kind], f.units * f.unit_mva * 0.12) / 100
    keep = [k for k in range(src.N) if np.abs(y[k]).sum() > 0]
    v_gs, it = gauss_seidel(y[np.ix_(keep, keep)], s[keep])
    v = np.zeros(src.N, complex)
    v[keep] = v_gs
    fl = gs.flows(v, br)
    s_poc = -fl[1]["s_ij"] * 100
    loss = sum(f["loss"].real for f in fl[1:]) * 100
    lines = ["the same full-output load flow by a second method",
             "  quantity               Newton-Raphson   Gauss-Seidel   difference",
             f"  P at POC MW            {nr['s_poc'].real:14.4f}   {s_poc.real:12.4f}   {abs(nr['s_poc'].real - s_poc.real):10.1e}",
             f"  Q at POC Mvar          {nr['s_poc'].imag:14.4f}   {s_poc.imag:12.4f}   {abs(nr['s_poc'].imag - s_poc.imag):10.1e}",
             f"  losses MW              {nr['loss_mw']:14.4f}   {loss:12.4f}   {abs(nr['loss_mw'] - loss):10.1e}",
             f"  iterations             {nr['iterations']:14d}   {it:12d}",
             "  two methods, one answer: the check finds an error in the",
             "  solver, not in the data - the data checks of lesson A and",
             "  the hand checks of the integrated example do that part;",
             "  an independent checker uses all three"]
    emit("s_independent", lines)


def triggers() -> None:
    w_before = gs.wscr([1500, 1500, 1095], [100, 80, 60])
    w_after = gs.wscr([1500, 1500, 1095, 1500], [100, 80, 60, 50])
    rows = [("a new plant beside the POC (50 MW)", f"WSCR {w_before:.1f} -> {w_after:.1f}", "E, B-locus"),
            ("grid strength falls 20 %", "SCR 15 -> 12", "B-sc, C-vcontrol"),
            ("unit firmware changed", "k 2.0 -> 2.5", "C-frt, F-versions"),
            ("line re-conductored", "R -30 %", "B-losses, G-line"),
            ("battery added (S0 -> S1)", "+20 MVA", "B, C, F all"),
            ("code revised by the operator", "U-102", "matrix, all")]
    lines = ["events that reopen the study (teaching register)",
             "  event                              change             rerun"]
    for ev, ch, rr in rows:
        lines.append(f"  {ev:34s} {ch:18s} {rr}")
    lines += ["  the study is a living record: each trigger names the",
              "  studies to rerun and the matrix rows to reopen; the plant's",
              "  change control (ch 38) asks the question for every change"]
    emit("s_triggers", lines)


if __name__ == "__main__":
    firmware()
    independent()
    triggers()
