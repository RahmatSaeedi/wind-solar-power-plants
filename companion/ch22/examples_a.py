"""Chapter 22, section A - the screening sequence: fatal-flaw tests run
first and cheaply, then the site facts side by side in the order of the
sequence (resource, land, grid, environment and social, permitting,
logistics, cost, schedule, constructability).

Run from the project root:   python -m companion.ch22.examples_a
Writes companion/ch22/expected/a_*.txt.
Teaching values A-311.
"""
from __future__ import annotations

from companion.ch22 import sources as src
from companion.ch22.common import emit
from plantp import appraisal as ap

# [start: tests]
TESTS = {   # True = the site fails (teaching thresholds, A-311)
    "no grid capacity within 50 km":
        lambda f: f["grid_free_mw"] < 100 and f["reinforce"] <= 0,
    "protected bird area overlap > 25 %":
        lambda f: f["bird_overlap"] > 0.25,
    "physical displacement without a plan":
        lambda f: f["displaced"] > 0,
    "permits longer than 36 months":
        lambda f: f["permit_months"] > 36,
}
# [end: tests]


def flaws() -> None:
    res = ap.fatal_flaws(src.SITES, TESTS)
    lines = ["fatal-flaw screen, run before any scoring (A-311):"]
    for site, fails in res.items():
        lines.append(f"  {site:10s} " + ("passes" if not fails else "flags:"))
        lines += [f"    - {f}" for f in fails]
    lines += ["  a flag is a question, not a verdict: P-North's bird overlap",
              "  needs a survey and an avoidance layout before it is fatal,",
              "  and its displacement needs a resettlement plan that meets",
              "  the safeguards (section G) - or the site is dropped; a",
              "  flag that cannot be cleared cheaply stops the spending"]
    emit("a_flaws", lines)


def facts() -> None:
    s = src.SITES
    rows = [("energy P50 GWh", "energy", "{:.0f}"), ("evidence quality", "energy_q", "{:.1f}"),
            ("capex k u", "capex", "{:,.0f}"), ("grid km / free MW", None, None),
            ("reinforcement k u", "reinforce", "{:,.0f}"), ("grid wait months", "grid_wait", "{:d}"),
            ("land ha", "land_ha", "{:,.0f}"), ("households / displaced", None, None),
            ("bird overlap", "bird_overlap", "{:.0%}"), ("permit months", "permit_months", "{:d}"),
            ("new road km", "road_km", "{:.0f}"), ("slope %", "slope_pct", "{:.0f}"),
            ("months to COD", "schedule", "{:d}")]
    names = list(s)
    lines = ["the three sites in the order of the screening sequence:",
             "  item                      " + "".join(f"{n:>13s}" for n in names)]
    for label, key, fmt in rows:
        if label.startswith("grid km"):
            vals = [f"{s[n]['grid_km']:.0f} / {s[n]['grid_free_mw']:.0f}" for n in names]
        elif label.startswith("households"):
            vals = [f"{s[n]['households']} / {s[n]['displaced']}" for n in names]
        else:
            vals = [fmt.format(s[n][key]) for n in names]
        lines.append(f"  {label:26s}" + "".join(f"{v:>13s}" for v in vals))
    lines += ["  P-North has the most energy and every other problem; the",
              "  sequence puts the cheap, decisive questions (grid, protected",
              "  areas, people) before the expensive ones (yield, design)"]
    emit("a_facts", lines)


if __name__ == "__main__":
    flaws()
    facts()
