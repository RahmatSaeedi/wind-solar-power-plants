"""Chapter 20, last lessons: what advance notice of an operator cap is
worth (caps known to the day-ahead plan against caps that arrive as a
surprise), and the inertia-like response a grid-forming battery could
give (only where permitted): power and energy against the rate of
change of frequency.

Run from the project root:   python -m companion.ch20.examples_n
Writes companion/ch20/expected/n_*.txt.
Teaching values A-299 to A-303.
"""
from __future__ import annotations

import numpy as np

from companion.ch20 import examples_b as eb, sources as src
from companion.ch20.common import emit
from plantp import control as ct

L = src.LIMITS


def year(plan_caps, real_caps) -> tuple[float, float]:
    act = np.clip(src.poc_actual(), 0, None)
    fc = np.clip(src.poc_forecast(24), 0, None)
    price = src.prices()
    c = ct.Controller(e=L["e_min"])
    val = curt = 0.0
    for d in range(365):
        h = slice(d * 24, d * 24 + 24)
        _, _, plan = ct.dp_schedule(price[h], np.minimum(fc[h], L["bess_mw"]),
                                    np.clip(plan_caps[h] - fc[h], 0, None),
                                    L["bess_mw"], L["e_min"], L["e_max"],
                                    round(c.e), L["eta"], wear=10.0,
                                    e_end=L["e_min"])
        for k in range(24):
            t = d * 24 + k
            r = c.step(t, act[t], plan[k], real_caps[t], True)
            val += r["export"] * price[t]
            curt += r["curtailed"]
    return val, curt


def evening_caps() -> np.ndarray:
    """Teaching: 60 MW from 18:00 to 22:00 on the 40 evenings with the
    highest output."""
    act = np.clip(src.poc_actual(), 0, None).reshape(365, 24)
    days = np.argsort(act[:, 18:22].sum(axis=1))[-40:]
    cap = np.full(8760, L["export_mw"])
    for d in days:
        cap[d * 24 + 18:d * 24 + 22] = 60.0
    return cap


def notice() -> None:
    free = np.full(8760, L["export_mw"])
    lines = ["operator caps known a day ahead or arriving as a surprise:",
             "  caps                  plan sees   export value k u   curtailed MWh"]
    for name, caps in (("midday 80 MW (A-302)", eb.caps()),
                       ("evening 60 MW", evening_caps())):
        known, c_k = year(caps, caps)
        surp, c_s = year(free, caps)
        lines.append(f"  {name:21s} {'yes':>9s}   {known / 1000:16,.1f}   {c_k:13,.0f}")
        lines.append(f"  {'':21s} {'no':>9s}   {surp / 1000:16,.1f}   {c_s:13,.0f}")
    lines += ["  notice is worth almost nothing for Plant P: before a midday",
              "  cap the battery is already empty (it was sold the evening",
              "  before) and the plan charges in those hours anyway; under an",
              "  evening cap the blocked energy simply waits and is sold later",
              "  at similar prices; the evening caps cost about 20 k u of",
              "  export with or without notice; notice would matter for a",
              "  battery that must prepare (fill before a cap that blocks",
              "  charging) - check the value of information before paying",
              "  for it (U-077)"]
    emit("n_notice", lines)


def inertia() -> None:
    lines = ["inertia-like response of grid-forming battery inverters",
             "(only if permitted; 20 MVA; P = 2 H S rocof / 50; A-303):",
             "  H s   RoCoF Hz/s   power MW   energy over 2 s MWh"]
    for h in (2.0, 4.0, 8.0):
        for rocof in (0.1, 0.5, 1.0):
            p = 2 * h * 20.0 * rocof / 50.0
            lines.append(f"  {h:3.0f}   {rocof:10.1f}   {p:8.2f}   {p * 2 / 3600:19.4f}")
    lines += ["  the energy is tiny; the power is not, and it must be there",
              "  at once - the converter keeps headroom for it, and its",
              "  current limit, not the battery, sets what is possible;",
              "  whether such a response is wanted and how it is measured",
              "  are grid-operator decisions (chapter 28)"]
    emit("n_inertia", lines)


if __name__ == "__main__":
    notice()
    inertia()
