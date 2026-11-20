"""Chapter 43, lab D: specification and dossier lab for main transformer
T1 - requirement to clause to test, the factory traveler audited, the
test report reviewed with corrections, tolerances and deductions, the
open decisions with their owners, and the loss/temperature calculator.

Run from the project root:   python -m companion.ch43.lab_d
Writes companion/ch43/expected/d_*.txt. Fictional factory (A-460..A-464).
"""
from __future__ import annotations

import numpy as np

from companion.ch43 import sources as src
from companion.ch43.common import emit
from companion.ch43.examples_c import corrected, gases, heatrun, ratio, sound
from plantp import xfmrdesign as xd

M, T, C = src.MAIN_B, src.TESTS, src.COSTS


# ------------------------------------------------ 1. trace
def trace() -> dict[str, int]:
    lines = ["requirement -> purchase clause -> test -> evidence at FAT",
             "  requirement                         clause                "
             "status"]
    count = {}
    for req, clause, test, status in src.REQS:
        count[status] = count.get(status, 0) + 1
        lines.append(f"  {req:35s} {clause:21s} {status}")
    lines += [f"  {count.get('done', 0)} done, {count.get('partial', 0)} partial, "
              f"{count.get('open', 0)} open of {len(src.REQS)}",
              "  each row names the test that proves it; a requirement",
              "  without a test row is a wish, and an 'open' row is a",
              "  decision someone must still make before acceptance"]
    emit("d_trace", lines)
    return count


# ------------------------------------------------ 2. traveler
# [start: audit]
def audit(traveler) -> list[tuple[str, str]]:
    """Stages whose record is missing, partial or carries a note."""
    out = []
    for stage, want, found, note in traveler:
        if found in ("not found", "") or note:
            out.append((stage, note or f"{want}: {found}"))
    return out
# [end: audit]


def traveler() -> list[tuple[str, str]]:
    gaps = audit(src.TRAVELER)
    lines = [f"traveler of T1: {len(src.TRAVELER)} stages, {len(gaps)} with a gap",
             "  stage                gap"]
    for stage, note in gaps:
        lines.append(f"  {stage:20s} {note}")
    off = (2052 - 2041) / 2
    lines += ["  the windings' heights differ by 11 mm: their magnetic",
              f"  centres by {off:.1f} mm, which turns a short circuit into an",
              "  axial force the clamps must carry - the designer confirms",
              "  it is inside the design allowance; the wet oil, the",
              "  missing drying end point and the missing impact recorder",
              "  are NCRs before shipment, not after"]
    emit("d_traveler", lines)
    return gaps


# ------------------------------------------------ 3. test report review
def review() -> dict[str, float]:
    lo = corrected()
    hr = heatrun()
    snd = sound()
    rt = ratio()
    gs = gases()
    tol = M["tol"]
    dp0 = max(0.0, lo["p0"] - M["p0_kw"])
    dpk = max(0.0, lo["pk75"] - M["pk_kw"])
    tot, tot_g = lo["p0"] + lo["pk75"], M["p0_kw"] + M["pk_kw"]
    rows = [
        ("no-load loss kW", M["p0_kw"], lo["p0"], lo["p0"] <= M["p0_kw"] * (1 + tol["p0"])),
        ("load loss kW, 75 C", M["pk_kw"], lo["pk75"],
         lo["pk75"] <= M["pk_kw"] * (1 + tol["pk"])),
        ("total loss kW", tot_g, tot, tot <= tot_g * (1 + tol["total"])),
        ("impedance %", M["uk_pct"], T["uk_pct"],
         abs(T["uk_pct"] / M["uk_pct"] - 1) <= tol["uk"]),
        ("ratio error %, worst", 0.5, T["ratio_err_pct"][rt["bad"]], False),
        ("top-oil rise K", M["top_oil_rise"], T["top_oil_rise"],
         T["top_oil_rise"] <= M["top_oil_rise"]),
        ("winding rise K", M["winding_rise"], hr["rise"], hr["rise"] <= M["winding_rise"]),
        ("sound power dB(A)", M["sound_lwa"], snd["lw"], snd["lw"] <= M["sound_lwa"]),
        ("partial discharge pC", T["pd_limit_pc"], T["pd_pc"], T["pd_pc"] <= T["pd_limit_pc"]),
    ]
    lines = ["test report TR-T1 reviewed (corrected values; contract teaching",
             "  tolerances)",
             "  quantity               guarantee   measured   verdict"]
    for name, g, m, ok in rows:
        lines.append(f"  {name:22s} {g:9.1f}   {m:8.1f}   {'pass' if ok else 'FAIL'}")
    ded = dp0 * C["a_kw"] + dpk * C["b_kw"]
    fails = sum(1 for r in rows if not r[3])
    lines += ["  deductions for losses above guarantee:",
              f"    {dp0:.1f} kW x {C['a_kw']} + {dpk:.1f} kW x {C['b_kw']} = "
              f"{ded:.1f} k u",
              f"  {fails} failures; acetylene {gs['C2H2']:+.1f} ppm after the "
              "heat run; FRA files",
              "  for the LV winding missing; short-circuit proof still open",
              "  the report said 'all pass': it used the uncorrected 2-minute",
              "  reading and left the failed tap and the PD level unremarked"]
    emit("d_review", lines)
    return dict(ded=ded, fails=fails, dp0=dp0, dpk=dpk, rise=hr["rise"])


# ------------------------------------------------ 4. open decisions
OPEN = [   # item, who decides, possible outcomes
    ("tap +8.75 % ratio", "maker", "correct the lead, repeat ratio test"),
    ("winding rise 1.5 K over", "owner with the maker",
     "repair cooling, accept with a rating limit, or reject"),
    ("PD 120 pC over 100", "maker, witnessed", "find the source, repeat the test"),
    ("acetylene after heat run", "maker and owner's specialist",
     "explain from records or investigate inside"),
    ("FRA of the LV winding", "maker", "deliver the files before shipment"),
    ("drying end point, oil water", "maker", "records or re-process"),
    ("short-circuit proof", "owner's engineer", "test or design review (STD-175)"),
    ("impact recorder", "maker and transporter", "fit before shipment (ch 31)"),
]


def decisions() -> int:
    lines = ["open decisions before T1 is accepted (owners and outcomes)",
             "  item                         who decides"]
    for item, who, outcome in OPEN:
        lines.append(f"  {item:28s} {who}")
        lines.append(f"    -> {outcome}")
    lines += [f"  {len(OPEN)} items: the factory acceptance is a list of evidence,",
              "  not a signature - each item closes with a record"]
    emit("d_open", lines)
    return len(OPEN)


# ------------------------------------------------ 5. loss and temperature calculator
def calculator() -> dict[str, dict[str, float]]:
    from companion.ch25.examples_b import unit_load
    from plantp import datapack
    k = unit_load()
    amb = datapack.load_hourly()["t_air_c"].to_numpy()
    calc = xd.LossTempCalc(M["p0_kw"], M["pk_kw"], k, amb)
    res = calc.sensitivity({"ambient +5 K": dict(ambient=5.0),
                            "load +10 %": dict(load=1.10),
                            "Pk as tested (+2.8 %)": dict(pk=1.028),
                            "load +30 % (more PV)": dict(load=1.30)})
    lines = ["loss and temperature calculator on the data-pack year (bid B unit)",
             "  case                    losses MWh   hot spot max C   life days"]
    for name, r in res.items():
        lines.append(f"  {name:22s}  {r['loss_mwh']:10.0f}   {r['hs_max']:14.0f}"
                     f"   {r['life_days']:9.1f}")
    b = res["base"]
    lines += [f"  a hot year adds {res['ambient +5 K']['life_days'] - b['life_days']:.1f}"
              " days of ageing; 30 % more load raises",
              f"  the hot spot by {res['load +30 % (more PV)']['hs_max'] - b['hs_max']:.0f}"
              " K - the plant's transformers age slowly,",
              "  so their acceptance turns on losses and evidence, not on",
              "  thermal life (teaching thermal model of ch 25)"]
    emit("d_calc", lines)
    return res


if __name__ == "__main__":
    trace()
    traveler()
    review()
    decisions()
    calculator()
    _ = np
