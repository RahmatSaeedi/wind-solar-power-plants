"""Chapter 50, round t: two test permits on one boundary, turbines released
to production one by one, as-built documents at handover, UPS autonomy at
the design load from a test at part load, the fire service's arrival in a
drill, and the battery's energy reserve for a frequency service.

Run from the project root:   python -m companion.ch50.examples_t
Writes companion/ch50/expected/t_*.txt.
Teaching values (A-514 to A-521).
"""
from __future__ import annotations

from companion.ch50.common import emit

# ------------------------------------------------ 1. overlapping test permits
PERMITS = [   # permit, boundary, from hour, to hour (one test day)
    ("SFT-031", "=PVF1-3.MV", 8, 12), ("SFT-033", "=PVF1-3.MV", 11, 15),
    ("SFT-034", "=PVF1-2.MV", 9, 13), ("SFT-035", "=PVF1-3.INV", 13, 17),
]


def overlaps() -> list:
    bad = []
    for i, (p1, b1, s1, e1) in enumerate(PERMITS):
        for p2, b2, s2, e2 in PERMITS[i + 1:]:
            if b1 == b2 and s1 < e2 and s2 < e1:
                bad.append((p1, p2, b1, max(s1, s2), min(e1, e2)))
    lines = ["sanction-for-test permits on one test day: two on the same boundary"]
    lines += [f"  {a} and {b} on {bd}: both live {s}:00-{e}:00" for a, b, bd, s, e in bad]
    lines += ["  two test teams on one boundary is two sets of assumptions",
              "  about what is isolated: the permit office issues one at a",
              "  time per boundary, and the second waits for the first's",
              "  cancellation (ch 32 permits)"]
    emit("t_overlap", lines)
    return bad


# ------------------------------------------------ 2. turbines released to production
STEPS = ["mechanical", "electrical", "controller", "SCADA", "grid code", "maker sign-off"]
TURBINES = {f"T{k:02d}": v for k, v in enumerate([
    "111111", "111111", "111011", "111111", "111110", "110000", "111111", "111111",
    "111101", "111111", "111111", "100000"], 1)}


def release() -> dict:
    ready = [t for t, s in TURBINES.items() if s == "1" * len(STEPS)]
    missing = {t: [STEPS[i] for i, c in enumerate(s) if c == "0"]
               for t, s in TURBINES.items() if t not in ready}
    lines = ["turbine commissioning steps:", f"  {', '.join(STEPS)}",
             f"  released to production: {len(ready)} of {len(TURBINES)} "
             f"({', '.join(ready)})"]
    lines += [f"  {t}: waiting for {', '.join(m)}" for t, m in missing.items()]
    lines += ["  a turbine produces only when its own six steps are signed:",
              "  T03 waits for SCADA, T05 for the maker's sign-off - and",
              "  energy before release is test energy, recorded as such"]
    emit("t_release", lines)
    return dict(ready=ready, missing=missing)


# ------------------------------------------------ 3. as-built documents
MDR = {   # discipline: (documents, at ASB, at IFC still)
    "electrical": (120, 96, 24), "civil": (85, 80, 5), "control": (60, 41, 19),
    "mechanical": (40, 38, 2), "fire": (25, 18, 7),
}


def asbuilt() -> dict:
    rows = [(d, n, a, a / n) for d, (n, a, _) in MDR.items()]
    tot = sum(n for _, n, _, _ in rows)
    asb = sum(a for _, _, a, _ in rows)
    lines = ["documents at as-built status (ASB, ch 38) by discipline at handover",
             "  discipline  documents  at ASB  share"]
    lines += [f"  {d:10s}  {n:9d}  {a:6d}  {s:5.0%}" for d, n, a, s in rows]
    lines += [f"  plant: {asb} of {tot} ({asb / tot:.0%})",
              "  control is furthest behind - the very drawings whose",
              "  changes lessons B and C of ch 48 found; an IFC drawing at",
              "  handover is a drawing of a plant that was never built"]
    emit("t_asbuilt", lines)
    return dict(share=asb / tot)


# ------------------------------------------------ 4. UPS autonomy at the design load
def ups_extrapolate(p_test: float = 6.4, t_test: float = 26.0, p_design: float = 8.0,
                    exponent: float = 1.15, required: float = 30.0) -> dict:
    t_design = t_test * (p_test / p_design) ** exponent
    need_kwh = required / 60 * p_design
    lines = [f"UPS-1 autonomy: tested {t_test:.0f} min at {p_test} kW; the design load is "
             f"{p_design} kW",
             f"  teaching scaling t ~ P^-{exponent}: at the design load {t_design:.1f} min",
             f"  {required:.0f} min at {p_design} kW needs about {need_kwh:.1f} kWh "
             "delivered",
             "  a test at part load flatters a battery: the replacement",
             "  string of DEV-14 is sized and tested at the design load,",
             "  with the maker's discharge table, not this scaling"]
    emit("t_ups", lines)
    return dict(t_design=t_design)


# ------------------------------------------------ 5. fire service in a drill
def drill(planned_min: float = 53.0, measured=(9, 41, 12, 6)) -> dict:
    names = ["call to dispatch", "travel 35 km", "site gate to scene", "set-up"]
    total = sum(measured)
    lines = ["night drill: the fire service called to the substation (times in min)"]
    lines += [f"  {n:20s} {m:3d}" for n, m in zip(names, measured)]
    lines += [f"  total {total} min against the {planned_min:.0f} min planned (ch 32 "
              "placeholders)",
              "  the 12 gate-to-scene minutes are the plant's own: an escort",
              "  waiting at the gate and a lit route save most of them; the",
              "  fire strategy uses the measured time, not the planned one",
              "  (U-110)"]
    emit("t_drill", lines)
    return dict(total=total, late=total - planned_min)


# ------------------------------------------------ 6. battery reserve for a service
def reserve(p_service: float = 20.0, minutes: float = 30.0, e_usable: float = 40.1 * 0.8,
            soc_now: float = 0.50, window=(0.10, 0.90)) -> dict:
    e_need = p_service * minutes / 60
    up = (soc_now - window[0]) / (window[1] - window[0]) * e_usable
    down = (window[1] - soc_now) / (window[1] - window[0]) * e_usable
    lines = [f"BESS reserve for a {p_service:.0f} MW frequency service held {minutes:.0f} min",
             f"  energy needed each way: {e_need:.1f} MWh",
             f"  at SOC {soc_now:.0%} in a {window[0]:.0%}-{window[1]:.0%} window: "
             f"{up:.1f} MWh to give, {down:.1f} MWh to take",
             f"  both directions covered: {'yes' if min(up, down) >= e_need else 'no'} - "
             "the test checks",
             "  the controller keeps SOC near the middle (ch 20 reserve",
             "  energy); a service test at 85 % SOC would pass upward and",
             "  fail downward"]
    emit("t_reserve", lines)
    return dict(e_need=e_need, up=up, down=down)


if __name__ == "__main__":
    overlaps()
    release()
    asbuilt()
    ups_extrapolate()
    drill()
    reserve()
