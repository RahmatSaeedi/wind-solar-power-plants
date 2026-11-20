"""Chapter 44, lab D: integration lab for the PCI-5500 - a loss and
thermal budget with the factory's spread (Monte Carlo over 96 module
positions), a non-live functional test sequence run against a simulated
state machine with fault injection (and against a faulty version that
the tests must catch), MPPT efficiency on a synthetic PV curve as test
evidence, and the interface trace.

Run from the project root:   python -m companion.ch44.lab_d
Writes companion/ch44/expected/d_*.txt and diagrams/data/ch44-*.csv.
Educational simulations; nothing here is firmware (A-466 to A-472).
"""
from __future__ import annotations

import numpy as np

from companion.ch44 import sources as src
from companion.ch44.common import csv, emit
from plantp import convmfg as cm
from plantp import mppt

S, I = src.STACKUP, src.INVERTER


# ------------------------------------------------ 1. thermal budget with spread
def montecarlo(seed: int = 4401, n: int = 48, limit_c: float = 90.0) -> dict:
    rng = np.random.default_rng(seed)
    p = S["p_module_w"] * rng.normal(1.0, 0.04, n)           # loss spread
    t_um = np.clip(rng.normal(S["tim_um"], 15.0, n), 50, None)  # print
    void = rng.uniform(0.0, 0.25, n)
    r_hs = S["r_hs"] * rng.normal(1.0, 0.05, n)
    void[37] = 0.55                                           # one bad print
    r_tim = np.array([cm.tim_r(t, S["tim_k"], S["tim_area_cm2"], v)
                      for t, v in zip(t_um, void)])
    t_j = I["coolant_c"] + p * (S["r_jc"] + r_tim + r_hs)
    order = np.argsort(-t_j)
    hot, nxt = order[0], order[1]
    csv("ch44-tj.csv", "pos,tj",
        [(k + 1, round(float(x), 1)) for k, x in enumerate(t_j)])
    lines = [f"junction temperature of the {n} outer-switch modules (T1, T4)"
             " of one inverter",
             "  (loss +-4 %, print 100 +- 15 um, voids 0-25 %, cold plate"
             " +-5 %)",
             f"  mean {t_j.mean():.1f} C, sd {t_j.std():.1f} K, highest "
             f"{t_j[hot]:.1f} C at module {hot + 1}",
             f"  next highest {t_j[nxt]:.1f} C; modules above "
             f"{limit_c:.0f} C: {int((t_j > limit_c).sum())}",
             f"  module {hot + 1}'s print left {void[hot]:.0%} voids: one bad"
             " print",
             f"  stands {t_j[hot] - t_j[nxt]:.1f} K above the next module",
             "  a full-power run with thermography or the drivers' own",
             "  temperature readings finds that module before shipment"]
    emit("d_tj", lines)
    return dict(mean=float(t_j.mean()), max=float(t_j[hot]), pos=int(hot + 1),
                second=float(t_j[nxt]))


# ------------------------------------------------ 2. state machine tests
class FaultySim(cm.ConverterSim):
    """Version 0.9 of the same sequence: the precharge timeout is
    missing (a planted fault the tests must find)."""
    PRECHARGE_MAX_S = float("inf")


# [start: tests]
START = [("start", {})]
CHARGED = START + [("tick", dict(v_dc=900))]
RUNNING = CHARGED + [("grid_ok", {}), ("synced", {})]
OVERTEMP = [("fault", dict(kind="overtemp"))]


def tick(v: float, k: int = 1) -> list:
    return [("tick", dict(v_dc=v))] * k


CASES = [   # name, events (event, kwargs), expected final state
    ("normal start", RUNNING, "RUN"),
    ("precharge too slow", START + tick(300, 12), "FAULT"),
    ("DC overvoltage", START + tick(1350), "FAULT"),
    ("grid lost in run", RUNNING + [("grid_lost", {})], "FAULT"),
    ("reset without cause cleared", OVERTEMP + [("reset", {})], "FAULT"),
    ("reset after cause cleared",
     OVERTEMP + [("reset", dict(cause_cleared=True))], "OFF"),
    ("run before sync refused", CHARGED + [("synced", {})], "READY"),
    ("boundary: DC exactly 850 V", START + tick(850), "READY"),
    ("boundary: DC 849.9 V", START + tick(849.9), "PRECHARGE"),
    ("boundary: DC exactly 1300 V", START + tick(1300), "READY"),
    ("boundary: precharge 10 s", START + tick(300, 10), "PRECHARGE"),
    ("DC overvoltage in run", RUNNING + tick(1350), "FAULT"),
]


def run_cases(sim_cls) -> list[tuple[str, str, str, bool]]:
    out = []
    for name, events, want in CASES:
        sim = sim_cls()
        for ev, kw in events:
            sim.event(ev, **kw)
        out.append((name, want, sim.state, sim.state == want))
    return out
# [end: tests]


def statemachine() -> dict[str, int]:
    good = run_cases(cm.ConverterSim)
    bad = run_cases(FaultySim)
    lines = ["functional test sequence against the simulated start-up (non-live)",
             "  case                           expected   v1.0      v0.9"]
    for (name, want, got1, _), (_, _, got2, _) in zip(good, bad):
        lines.append(f"  {name:30s} {want:9s}  {got1:9s} {got2}")
    p1 = sum(r[3] for r in good)
    p2 = sum(r[3] for r in bad)
    failed = [g[0] for g, b in zip(good, bad) if g[3] and not b[3]]
    lines += [f"  v1.0 passes {p1} of {len(CASES)}; v0.9 passes {p2}, failing: "
              + ", ".join(failed),
              "  the missing timeout leaves a slow precharge charging for",
              "  ever, which only a test that injects the fault can show;",
              "  the boundary cases pin the limits to the released values;",
              "  the test list is part of the release record of every",
              "  firmware version"]
    sims = {}
    for name, cls in (("v1.0", cm.ConverterSim), ("v0.9", FaultySim)):
        sim = cls()
        for ev, kw in CASES[1][1]:
            sim.event(ev, **kw)
        sims[name] = sim.log
    lines += ["  transition log of 'precharge too slow' (from, to, reason):"]
    for name, log in sims.items():
        lines.append(f"    {name}: " + "; ".join(f"{a}->{b} ({w})" for a, b, w in log))
    emit("d_sm", lines)
    return dict(v10=p1, v09=p2, n=len(CASES))


# ------------------------------------------------ 3. MPPT efficiency
# [start: dpo]
class DriftFreePO:
    """Educational perturb-and-observe that alternates a perturb step and
    a hold step: the change seen while holding is the sun's, so it is
    taken out of the change seen while perturbing (not firmware)."""

    def __init__(self, v_ref: float, step: float):
        self.v_ref, self.step = v_ref, step
        self.direction, self.phase = 1.0, "perturb"
        self.p_before = self.p_after = 0.0

    def update(self, v_meas: float, i_meas: float) -> float:
        p = v_meas * i_meas
        if self.phase == "perturb":            # p is after the last hold
            self.p_before = p
            self.v_ref += self.direction * self.step
            self.phase = "measure"
        elif self.phase == "measure":          # p is after the perturbation
            self.p_after = p
            self.phase = "hold"                # keep v_ref for one step
        else:                                  # p after holding: sun only
            d_sun = p - self.p_after
            d_v = (self.p_after - self.p_before) - d_sun
            if d_v < 0:
                self.direction = -self.direction
            self.phase = "perturb"
        return self.v_ref
# [end: dpo]


def mppt_eff(n_series: int = 26, steps: int = 400) -> dict[str, float]:
    t = np.arange(steps)
    g = np.where(t < 100, 300.0, np.where(t < 200, 300.0 + 7.0 * (t - 100),
                                          np.where(t < 300, 1000.0, 1000.0 - 6.0 * (t - 300))))
    curves = [mppt.PVM_550.at(float(x), 45.0, n_series) for x in g]
    p_avail = np.array([c.mpp()[1] for c in curves])
    out = {}
    tracks = {}
    for name, tr in (("perturb and observe", mppt.PerturbObserve(v_ref=900.0, step=4.0)),
                     ("incremental conductance",
                      mppt.IncrementalConductance(v_ref=900.0, step=4.0)),
                     ("perturb-hold-compare", DriftFreePO(v_ref=900.0, step=4.0))):
        v = 900.0
        got = []
        vs = []
        for c in curves:
            v = min(max(v, 0.0), c.voc)
            i = float(c.i(v))
            got.append(v * i)
            vs.append(v)
            v = tr.update(v, i)
        tracks[name] = vs
        got = np.array(got)
        static = got[50:100].sum() / p_avail[50:100].sum()
        ramp = got[100:200].sum() / p_avail[100:200].sum()
        out[name] = dict(static=static, ramp=ramp, total=got.sum() / p_avail.sum())
    vmp = [c.mpp()[0] for c in curves]
    csv("ch44-mppt.csv", "t,vmp,po,hc",
        [(int(k), round(vmp[k], 1), round(tracks["perturb and observe"][k], 1),
          round(tracks["perturb-hold-compare"][k], 1)) for k in range(0, steps, 2)])
    lines = ["MPPT efficiency on a synthetic string (26 x PVM-550, 45 C), one step",
             "  a second: steady 300 W/m2, ramp to 1000, steady, ramp down",
             "  tracker                      steady   ramp up   whole profile"]
    for name, r in out.items():
        lines.append(f"  {name:27s} {r['static']:7.2%}  {r['ramp']:8.2%}  {r['total']:10.2%}")
    lines += ["  all hold the steady point; on the rising ramp the plain",
              "  trackers read the sun's rise as their own success and walk",
              "  away from the maximum - separating the two changes keeps",
              "  the tracker on it; the dynamic MPPT efficiency is evidence",
              "  the efficiency standard asks for (STD-049); educational",
              "  simulations of ch 9's algorithms, not firmware"]
    emit("d_mppt", lines)
    return out


# ------------------------------------------------ 4. interface trace
TRACE = [   # requirement, verified by, evidence, status
    ("DC window 933-1300 V (D-012)", "DC voltage tests at FAT", "test report", "done"),
    ("Q(V) with 4 % droop (ch 20)", "fingerprint, functional test", "parameter record", "done"),
    ("island detection on", "fingerprint", "parameter record", "failed: INV-04"),
    ("DC injection limit (ch 43)", "type test of the design", "type-test report", "open"),
    ("SCADA point list (ch 35)", "point-to-point at FAT", "point list signed", "done"),
    ("cooling 45 C coolant", "full-power run", "heat-run record", "done"),
    ("ride-through (ch 26, 28)", "type test, model validation", "type-test report", "open"),
]


def trace() -> dict[str, int]:
    st = {}
    lines = ["interface requirements of the PCI-5500 traced to evidence",
             "  requirement                     verified by                   status"]
    for req, by, _ev, s in TRACE:
        key = s.split(":")[0]
        st[key] = st.get(key, 0) + 1
        lines.append(f"  {req:31s} {by:29s} {s}")
    lines += ["  " + ", ".join(f"{k} {v}" for k, v in st.items()),
              "  the type-test rows belong to the design, the others to each",
              "  unit: one failed unit row (INV-04) is a re-test, the open",
              "  type rows are questions to the maker (U-125)"]
    emit("d_trace", lines)
    return st


if __name__ == "__main__":
    montecarlo()
    statemachine()
    mppt_eff()
    trace()
