"""Chapter 52, lesson F (RAM mastery exercise): the Plant P reliability
case inside a stated boundary - a failure-mode register, the expected
energy lost by class, the plant's energy availability against the
assumption of model 15.1, a Monte Carlo of a year's loss, and scenarios
for repair time, spares, a common cause, the month of planned work and
grid outages.

Boundary: from the generating units to the POC meter; the grid beyond the
POC is a separate scenario; BESS outages shift energy, they do not lose
it, so the battery is counted in time only.

Run from the project root:   python -m companion.ch52.lab_f
Writes companion/ch52/expected/f_*.txt and diagrams/data/ch52-scen.csv.
Teaching values (A-534).
"""
from __future__ import annotations

import numpy as np

from companion.ch15 import sources as s15
from companion.ch52 import sources as src
from companion.ch52.common import csv, emit
from plantp import ram

PRICE = 70.0


def series() -> dict:
    y = s15.plant_year()
    return dict(wind=np.asarray(y["w_lt"], float), pv=np.asarray(y["pv_deg"], float),
                poc=np.asarray(y["poc"], float), month=np.asarray(y["month"]))


# ------------------------------------------------ 1. failure-mode register
FMEA = [   # mode, block, effect, severity 1-5, occurrence 1-5, detection 1-5
    ("inverter IGBT stack failure", "PV inverter", "block lost", 3, 3, 2),
    ("combiner fuses open (earth fault)", "PV combiner box", "20 strings lost", 2, 3, 4),
    ("unit transformer winding fault", "PV unit transformer", "block lost months", 4, 1, 3),
    ("turbine converter trip on dips", "wind turbine (minor)", "turbine stops", 2, 4, 2),
    ("gearbox bearing wear-out", "wind turbine (major)", "turbine out weeks", 4, 2, 2),
    ("main transformer internal fault", "main transformer", "export halved months", 5, 1, 3),
    ("line permanent fault", "132 kV line (permanent fault)", "no export hours", 5, 2, 1),
    ("collector cable joint failure", "33 kV collector cable (per km)", "feeder lost days", 3, 2, 2),
    ("PPC failure", "PPC", "fallback mode", 3, 1, 1),
    ("BESS PCS fault", "BESS PCS", "storage reduced", 2, 3, 1)]


def register() -> list:
    rank = sorted(FMEA, key=lambda r: (-r[3] * r[4] * r[5], -r[3]))
    lines = ["failure-mode register (teaching scores 1-5; RPN = S x O x D)",
             "  mode                               S  O  D  RPN  effect"]
    lines += [f"  {m:34s} {s} {o:2d} {d:2d} {s * o * d:4d}  {e}" for m, _, e, s, o, d in rank]
    lines += ["  the combiner earth fault ranks high on detection (lesson D:",
              "  43 days unseen) though its effect is small; the main",
              "  transformer ranks by severity - the RPN mixes the two, so",
              "  the register keeps S visible beside it (ch 40)"]
    emit("f_register", lines)
    return [m for m, *_ in rank]


# ------------------------------------------------ 2. expected energy lost by class
def expected(classes=None, cap_mw: float = 63.0, ccf_q: float = 0.0) -> dict:
    c = classes or src.CLASSES
    s = series()
    wind_h, pv_h, poc_h = s["wind"].mean(), s["pv"].mean(), s["poc"].mean()
    above = float(np.clip(s["poc"] - cap_mw, 0, None).sum())       # MWh a year over 63 MW
    out = {}
    for k, (n, lam, mttr, delay, pmh, cons, mw) in c.items():
        down = n * lam * (mttr + delay)                              # unit-hours a year
        if k.startswith("PV inverter") or k.startswith("PV unit"):
            e = down * pv_h / 10
        elif k.startswith("PV combiner"):
            e = down * pv_h / 210
        elif k.startswith("wind turbine"):
            e = down * wind_h / 12
        elif k == "main transformer":
            e = n * lam * (mttr + delay) / 8760 * above
        elif k.startswith("132 kV line"):
            e = down * poc_h
        elif k.startswith("33 kV collector"):
            e = down * poc_h / 6
        elif k == "PPC":
            e = down * poc_h * 0.2
        else:
            e = 0.0                                                  # BESS: shifted, not lost
        out[k] = e
    if ccf_q:
        out["both main transformers (common cause)"] = ccf_q * (s["poc"].sum())
    n_t, _, _, _, pm_t, *_ = c["turbine PM visit"]
    out["turbine services (planned)"] = n_t * pm_t * wind_h / 12
    return out


def energy_case() -> dict:
    s = series()
    pot = float(s["wind"].sum() + s["pv"].sum())
    e = expected()
    tot = sum(e.values())
    ea = 1 - tot / pot
    model = (193.14 + 108.36) / (196.88 + 109.45)
    lines = ["expected energy lost a year by class (MWh), units to POC (teaching data)"]
    lines += [f"  {k:32s} {v:8.0f}" for k, v in sorted(e.items(), key=lambda kv: -kv[1]) if v > 0]
    gap = (model - ea) * pot
    lines += [f"  total {tot:,.0f} MWh of {pot / 1000:,.1f} GWh: energy availability {ea:.2%}",
              f"  model 15.1 assumed {model:.2%} (its availability step): the RAM case",
              f"  is {'below' if ea < model else 'above'} it by {abs(model - ea) * 100:.2f} points "
              f"({abs(gap) / 1000:.1f} GWh a year) - the finding",
              "  goes back to the energy model (ch 15) with this register as",
              "  its basis; PV preventive work is done at night and costs",
              "  no energy, so it is not in the list"]
    emit("f_energy", lines)
    return dict(tot=tot, ea=ea, model=model, by=e, gap=gap)


# ------------------------------------------------ 3. Monte Carlo of a year
def monte_carlo(years: int = 400, seed: int = 52) -> dict:
    s = series()
    per_h = {"PV inverter": s["pv"].mean() / 10, "PV unit transformer": s["pv"].mean() / 10,
             "PV combiner box": s["pv"].mean() / 210,
             "wind turbine (minor)": s["wind"].mean() / 12,
             "wind turbine (major)": s["wind"].mean() / 12,
             "132 kV line (permanent fault)": s["poc"].mean()}
    def blocks(stocked=()):
        return {k: dict(n=src.CLASSES[k][0], mtbf=8760 / src.CLASSES[k][1],
                        repair_h=src.CLASSES[k][2] / np.exp(0.125),   # lognormal mean = MTTR
                        stock=1 if k in stocked else 0,
                        lead_h=src.CLASSES[k][3] if src.CLASSES[k][3] > 0 else None)
                for k in per_h}

    def years_of(b, seed_):
        rng = np.random.default_rng(seed_)
        out = []
        for _ in range(years):
            r = ram.simulate(b, 8760.0, seed=int(rng.integers(1 << 30)))
            out.append(sum(r[k]["down_h"] * per_h[k] for k in per_h))
        return np.array(out)

    annual = years_of(blocks(), seed)
    spared = years_of(blocks(("PV inverter", "wind turbine (major)")), seed)
    analytic = sum(src.CLASSES[k][0] * src.CLASSES[k][1] * (src.CLASSES[k][2] + src.CLASSES[k][3])
                   * per_h[k] for k in per_h)
    mean_e = float(annual.mean())
    lines = [f"Monte Carlo of six repairable classes over {years} simulated years",
             "  (exponential failures, lognormal repairs, every part waits its lead time)",
             f"  mean loss {mean_e:,.0f} MWh a year (expected-value sum {analytic:,.0f}; lower",
             "  because an outage running past the year's end is cut there);",
             f"  single years: P50 {np.percentile(annual, 50):,.0f}, P90 "
             f"{np.percentile(annual, 90):,.0f}, max {annual.max():,.0f}",
             f"  with one spare inverter and one major turbine kit on the shelf:",
             f"  mean {spared.mean():,.0f}, P90 {np.percentile(spared, 90):,.0f} MWh",
             "  the mean hides the tail: one year in ten loses more than",
             f"  {np.percentile(annual, 90) / np.percentile(annual, 50):.1f} times the median - "
             "a major turbine repair or a long",
             "  line fault in the wrong month; the budget and the debt",
             "  case use the tail (ch 16, ch 21)"]
    emit("f_montecarlo", lines)
    return dict(mean=mean_e, p50=float(np.percentile(annual, 50)),
                p90=float(np.percentile(annual, 90)), analytic=analytic,
                spared=float(spared.mean()), spared90=float(np.percentile(spared, 90)))


# ------------------------------------------------ 4. scenarios
def scenarios() -> dict:
    base = sum(expected().values())
    out = {"base": base}

    def with_(k, idx, val):
        c = dict(src.CLASSES)
        row = list(c[k])
        row[idx] = val
        c[k] = tuple(row)
        return c

    c = dict(src.CLASSES)
    c = {k: (v[0], v[1], v[2] * 1.5, v[3], *v[4:]) for k, v in c.items()}
    out["repair time +50 %"] = sum(expected(c).values())
    out["main transformer spare held"] = sum(expected(with_("main transformer", 3, 240.0)).values())
    out["turbine crane contract (wait /2)"] = sum(expected(with_("wind turbine (major)", 3, 600.0)).values())
    out["common cause on both transformers"] = sum(expected(ccf_q=0.0005).values())
    s = series()
    jun = float(s["wind"][s["month"] == 5].mean()) / 12 * 60 * 12
    dec = float(s["wind"][s["month"] == 11].mean()) / 12 * 60 * 12
    avg = expected()["turbine services (planned)"]
    out["turbine services all in June"] = base - avg + jun
    out["turbine services all in December"] = base - avg + dec
    out["grid outages 3 x 2 h (outside the boundary)"] = base + 3 * 2 * s["poc"].mean()
    csv("ch52-scen.csv", "k,mwh", [(k + 1, round(v)) for k, v in enumerate(out.values())])
    lines = ["scenarios: expected energy lost a year (MWh) and the change from the base"]
    lines += [f"  {k:44s} {v:7,.0f}  {v - base:+7,.0f}" for k, v in out.items()]
    big = max((k for k in out if k != "base"), key=lambda k: abs(out[k] - base))
    lines += [f"  the services moved from December to June save {dec - jun:,.0f} MWh "
              f"({(dec - jun) * PRICE:,.0f} u) a year",
              "  for no cost; a transformer spare saves "
              f"{base - out['main transformer spare held']:,.0f} MWh a year - its",
              "  price is weighed against that (ch 18 shared spare);",
              f"  the largest single change: {big}"]
    emit("f_scenarios", lines)
    return out


# ------------------------------------------------ 5. time vs energy
def time_vs_energy() -> dict:
    ai = {}
    for k in ("PV inverter", "wind turbine (minor)", "wind turbine (major)", "BESS PCS"):
        n, lam, mttr, delay, pmh, *_ = src.CLASSES[k]
        ai[k] = 1 - (lam * (mttr + delay) + pmh) / 8760
    lines = ["equipment availability (time, one unit) against plant energy availability"]
    lines += [f"  {k:24s} {v:.2%}" for k, v in ai.items()]
    lines += [
              f"  plant energy availability (lesson F): {energy_case()['ea']:.2%}",
              "  three different numbers: the unit's time up, the plant's",
              "  energy delivered, and the contract's definition (ch 37) -",
              "  every report states which one it means"]
    emit("f_time", lines)
    return ai


if __name__ == "__main__":
    register()
    energy_case()
    monte_carlo()
    scenarios()
    time_vs_energy()
