"""Chapter 52, lesson D (worked example): an unexplained production loss
traced from the data to a verified repair.

Ten PV blocks over 120 days of the data-pack year. In block PVF2-3 one
combiner (CB14, 20 strings) drops out on case day 52 and two more strings
on day 75; the block's pyranometer drifts low on days 40-46 and its
energy tag freezes on days 88-89. The case follows the evidence in order:
data quality, detection by peer ratio and CUSUM, localisation by combiner
currents, the safe diagnosis record, the root-cause chain, the repair, and
acceptance by the peer ratio after the repair.

Run from the project root:   python -m companion.ch52.lab_d
Writes companion/ch52/expected/d_*.txt and diagrams/data/ch52-ratio.csv.
Teaching values (A-533). No test voltages or procedures: records only.
"""
from __future__ import annotations

import numpy as np

from companion.ch15 import sources as s15
from companion.ch40 import sources as s40
from companion.ch52 import sources as src
from companion.ch52.common import csv, emit
from plantp import performance as pf

FIRST_DAY = 100                    # case day 0 = day 100 of the data-pack year
PRICE = 70.0                       # u/MWh (ch 21 PPA, teaching)


def blocks(seed: int = 533) -> dict:
    """Daily energy of the ten blocks (MWh), the faulty block's own POA
    sensor, its frozen tag and the true (unfaulted) energy."""
    c = src.CASE
    pv = s15.plant_year()["pv_av"]
    days = c["days"]
    daily = np.array([pv[(FIRST_DAY + d) * 24:(FIRST_DAY + d + 1) * 24].sum() / 10
                      for d in range(days)])
    rng = np.random.default_rng(seed)
    gain = 1 + rng.normal(0, 0.004, (10, 1))                 # small fixed block spread
    e = daily * gain * (1 + rng.normal(0, 0.006, (10, days)))
    true = e.copy()
    b = c["bad_block"]
    lost = np.zeros(days)
    lost[c["cb_out_day"]:c["repair_day"]] += c["cb_strings"] / c["strings_block"]
    lost[c["partial_day"]:c["repair_day"]] += c["partial_strings"] / c["strings_block"]
    e[b] *= 1 - lost
    tag = e[b].copy()
    d0, d1 = c["stale_days"]
    tag[d0:d1 + 1] = tag[d0 - 1]                             # frozen value
    poa = daily / daily.mean()
    sensor = poa.copy()
    s0, s1, drop = c["sensor_drift"]
    sensor[s0:s1 + 1] *= 1 - drop
    return dict(e=e, true=true, tag=tag, poa=poa, sensor=sensor, lost=lost)


# ------------------------------------------------ step 1: data quality
def quality() -> dict:
    d = blocks()
    c = src.CASE
    b = c["bad_block"]
    frozen = [k for k in range(1, c["days"]) if d["tag"][k] == d["tag"][k - 1]]
    pr_own = d["e"][b] / d["sensor"] / (d["e"][b] / d["poa"]).mean()
    s0, s1, _ = c["sensor_drift"]
    lines = [f"step 1 - data quality for block {s40.BLOCKS[b]} before any diagnosis",
             f"  energy tag frozen on case days {', '.join(map(str, frozen))}: those days "
             "are excluded",
             f"  own pyranometer reads {c['sensor_drift'][2]:.0%} low on days {s0}-{s1}: the "
             "block's PR",
             f"  rises to {pr_own[s0:s1 + 1].mean():.3f} there (a 'better' block that is not) -",
             "  so the comparison uses the other blocks (peer ratio), which",
             "  share the sun and need no sensor"]
    emit("d_quality", lines)
    return dict(frozen=frozen, pr_drift=float(pr_own[s0:s1 + 1].mean()))


# ------------------------------------------------ step 2: detection
def detection(k: float = 0.01, h: float = 0.05) -> dict:
    d = blocks()
    c = src.CASE
    b = c["bad_block"]
    e = d["e"].copy()
    e[b] = d["tag"]
    others = np.delete(e, b, axis=0)
    ratio = e[b] / np.median(others, axis=0)
    base = float(np.median(ratio[:30]))
    resid = ratio / base - 1
    ok = np.ones(c["days"], bool)
    d0, d1 = c["stale_days"]
    ok[d0:d1 + 1] = False
    idx = np.where(ok)[0]
    hit = pf.cusum(resid[idx], k, h)
    day = int(idx[hit]) if hit is not None else None
    csv("ch52-ratio.csv", "day,ratio", [(int(t), round(float(r / base), 4))
                                       for t, r in enumerate(ratio) if ok[t]])
    found = c["repair_day"] - 1
    lines = [f"step 2 - detection: daily energy of {s40.BLOCKS[b]} over the median of the "
             "other nine",
             f"  ratio normalised to its first 30 days; lower CUSUM k {k}, h {h}",
             f"  ratio after day {c['cb_out_day']}: {np.mean(ratio[c['cb_out_day']:c['partial_day']] / base):.3f}"
             f"; after day {c['partial_day']}: "
             f"{np.mean(ratio[c['partial_day']:c['repair_day']][ok[c['partial_day']:c['repair_day']]] / base):.3f}",
             f"  CUSUM signal on case day {day}: {day - c['cb_out_day']} day(s) after the fault",
             f"  the fault was found on day {found} by the thermography flight -",
             f"  {found - c['cb_out_day']} days late; the ratio was in SCADA all the time,",
             "  nobody watched it (ch 37 CUSUM)"]
    emit("d_detect", lines)
    return dict(day=day, delay=day - c["cb_out_day"], found=found, base=base,
                r1=float(np.mean(ratio[c["cb_out_day"]:c["partial_day"]] / base)))


# ------------------------------------------------ step 3: localisation
def localise(seed: int = 534) -> dict:
    rng = np.random.default_rng(seed)
    cur = 20 * 11.8 * 0.82 * (1 + rng.normal(0, 0.01, 21))   # A at 820 W/m2 (teaching)
    cur[13] = 0.0                                            # CB14
    cur[6] *= 18 / 20                                        # CB07: two strings
    med = float(np.median(cur))
    low = [(k + 1, float(x)) for k, x in enumerate(cur) if x < 0.95 * med]
    csv("ch52-combiners.csv", "cb,amps", [(k + 1, round(float(x), 1)) for k, x in enumerate(cur)])
    lines = ["step 3 - localisation: the 21 combiner currents of PVF2-3 at noon on a clear",
             f"  day (A); median {med:.0f} A",
             "  " + " ".join(f"{x:4.0f}" for x in cur[:11]),
             "  " + " ".join(f"{x:4.0f}" for x in cur[11:]),
             f"  below 95 % of the median: " + ", ".join(f"CB{k:02d} {x:.0f} A" for k, x in low),
             "  CB14 is dead (all 20 strings) and CB07 two strings short:",
             "  one combiner explains 4.8 % of the block, two strings 0.5 %",
             "  - together the drop the ratio showed"]
    emit("d_localise", lines)
    return dict(low=low, med=med)


# ------------------------------------------------ step 4: diagnosis record
RECORD = [   # step, by whom, record
    ("permit issued, CB14 isolated and proven dead", "authorised person", "PTW-0761"),
    ("fuses checked: 3 open (+ and - of string 7, - of string 12)", "technician",
     "WO-0533 sheet 1"),
    ("insulation test of strings 7 and 12 (qualified tester)", "test engineer",
     "IR sheet: string 7 fails, 12 passes"),
    ("string 7 traced: connector at module 18 half-mated, water inside", "technician",
     "photos P-1..P-4"),
    ("CB07: two strings with a blown fuse each, no insulation fault", "technician",
     "WO-0534")]


def diagnosis() -> dict:
    lines = ["step 4 - the safe diagnosis as a record (no procedure or test values here)"]
    for k, (s, who, rec) in enumerate(RECORD):
        lines += [f"  {k + 1}. {s}", f"     by {who}; record {rec}"]
    lines += ["  every step names who did it and where the evidence is: the",
              "  test was done by a qualified person under the permit, and",
              "  the CB14 fuses were not replaced before the fault was found",
              "  - a fuse put back on an insulation fault opens again"]
    emit("d_diagnosis", lines)
    return dict(steps=len(RECORD))


# ------------------------------------------------ step 5: root cause and action
CHAIN = [("why was CB14 dead?", "fuses of strings 7 and 12 open", "WO-0533"),
         ("why did they open?", "fault current from string 7 to earth", "IR sheet"),
         ("why the earth fault?", "water in a half-mated connector", "photos P-1..P-4"),
         ("why half-mated?", "connector not pushed home at installation",
          "installation QC sheet"),
         ("why not caught then?", "the pull check was sampled, row 31 not sampled",
          "ch 49 ITP sample")]


def root_cause(rows_crew: int = 64) -> dict:
    gaps = [w for w, _, e in CHAIN if not e]
    lines = ["step 5 - root cause, each link with its evidence"]
    for w, a, e in CHAIN:
        lines += [f"  {w}", f"     -> {a} [{e}]"]
    lines += [f"  links without evidence: {len(gaps)}",
              f"  corrective action: check every connector in the {rows_crew} rows the same",
              "  crew built (the cause is a practice, not one connector);",
              "  preventive: a pull check on every connector in future work",
              "  (ch 49 ITP), not a sample"]
    emit("d_rootcause", lines)
    return dict(gaps=len(gaps), rows=rows_crew)


# ------------------------------------------------ step 6: acceptance and the cost
def acceptance(days_after: int = 14, tol: float = 0.01) -> dict:
    d = blocks()
    c = src.CASE
    b = c["bad_block"]
    det = detection()
    # after the repair: block restored (days repair_day onwards are already unfaulted)
    others = np.delete(d["e"], b, axis=0)
    ratio = d["e"][b] / np.median(others, axis=0) / det["base"]
    after = ratio[c["repair_day"]:c["repair_day"] + days_after]
    m, sd = float(after.mean()), float(after.std(ddof=1))
    half = 2.16 * sd / np.sqrt(after.size)                   # t(0.975, 13)
    ok = abs(m - 1) + half <= tol
    lost = float(np.sum(d["true"][b] - d["e"][b]))
    early = det["day"]
    saved = float(np.sum((d["true"][b] - d["e"][b])[early + 2:]))
    lines = [f"step 6 - acceptance: block ratio over {days_after} days after the repair",
             f"  mean {m:.4f}, 95 % interval +/-{half:.4f}; criterion: within 1 +/- {tol}",
             f"  -> {'ACCEPTED' if ok else 'not yet accepted'}; the work order closes on this record",
             f"  energy lost to the fault: {lost:.1f} MWh = {lost * PRICE:,.0f} u",
             f"  had the CUSUM been watched (signal day {early}, repair 2 days later):",
             f"  {lost - saved:.1f} MWh lost instead - {saved:.1f} MWh "
             f"({saved / lost:.0%}) was the price of not looking"]
    emit("d_accept", lines)
    return dict(mean=m, half=half, ok=ok, lost=lost, saved=saved)


if __name__ == "__main__":
    quality()
    detection()
    localise()
    diagnosis()
    root_cause()
    acceptance()
