"""Chapter 48, lesson A: measurement and control hardware - datasheets
turned into site error budgets, calibration certificates read for what
they prove, the revenue-metering chain and its site test, cabinet
temperatures against the devices inside, and bonding and cable shields.

Run from the project root:   python -m companion.ch48.examples_a
Writes companion/ch48/expected/a_*.txt.
Teaching values (A-498 to A-500); no live work.
"""
from __future__ import annotations

from companion.ch48 import sources as src
from companion.ch48.common import emit
from plantp import hwmfg as hw


# ------------------------------------------------ 1. error budgets
def budgets(t_site: float = 45.0, years: float = 2.0) -> dict:
    lines = [f"datasheet error terms at site: {t_site:.0f} C, {years:.0f} years after "
             "calibration",
             "  instrument            reading      RSS    worst   largest term"]
    out = {}
    for name, (spec, rdg, fs, unit) in src.SPECS.items():
        b = hw.error_budget(spec, t_site, years, rdg, fs)
        big = max(b["terms"], key=b["terms"].get)
        out[name] = b
        lines.append(f"  {name:20s}  {rdg:6.0f} {unit:4s}  {b['rss']:6.2f}  "
                     f"{b['worst']:6.2f}   {big}")
    py = out["pyranometer"]
    tm = py["terms"]
    rest = (py["rss"] ** 2 - tm["accuracy"] ** 2) ** 0.5
    lines += ["  pyranometer terms, W/m2: " + ", ".join(f"{k} {v:.0f}"
                                                     for k, v in tm.items()),
              f"  its {py['rss']:.0f} W/m2 RSS is {py['rss'] / 10:.1f} % of the reading; "
              "the accuracy in",
              f"  bold is {tm['accuracy']:.0f}, and the terms the datasheet prints in "
              f"small type add {rest:.0f}",
              "  - temperature (reference 20 C) and two years of drift; the",
              "  recalibration interval is part of the budget (ch 34)"]
    emit("a_budgets", lines)
    return out


# ------------------------------------------------ 2. calibration certificates
def certs() -> dict:
    lines = [f"calibration certificates read on {src.TODAY} for what they prove",
             "  serial    instrument            finding"]
    bad = {}
    for s, inst, acc, trace, unc, conf, cal, due in src.CAL_CERTS:
        why = []
        if not acc:
            why.append("lab not accredited")
        if not trace:
            why.append("no traceability chain")
        if not unc:
            why.append("no uncertainty stated")
        if not conf:
            why.append("no conformity statement")
        if due < src.TODAY:
            why.append(f"overdue since {due}")
        if why:
            bad[s] = why
        lines.append(f"  {s}   {inst:20s}  {'; '.join(why) or 'ok'}")
    lines += [f"  {len(bad)} of {len(src.CAL_CERTS)} certificates do not prove what "
              "they claim:",
              "  a number without its uncertainty cannot be compared with a",
              "  limit; without a traceability chain it is a number from an",
              "  unknown reference; an overdue anemometer has measured a year",
              "  of the plant's wind without a valid calibration (ch 13)"]
    emit("a_certs", lines)
    return bad


# ------------------------------------------------ 3. metering chain
def metering() -> dict:
    m = src.METER
    rss, worst = hw.chain_error(m["ct"], m["vt"], m["meter"])
    lines = [f"revenue metering at the POC: CT {m['ct']} %, VT {m['vt']} %, meter "
             f"{m['meter']} % (class errors)",
             f"  combined: RSS {rss:.2f} %, worst case {worst:.2f} %",
             "  site test of the meter (error at a share of rated load):"]
    bad = []
    for load, err in m["site_test"]:
        lim = m["class_limits"][load]
        ok = abs(err) <= lim
        if not ok:
            bad.append(load)
        lines.append(f"    {load:3d} %   {err:+.2f} %   limit {lim:.1f} %   "
                     f"{'ok' if ok else 'OVER'}")
    lines += [f"  at {', '.join(map(str, bad))} % load the meter is outside its "
              "class: the plant",
              "  exports at low load for hours every morning and evening - the",
              f"  {rss:.2f} % chain error on 295 GWh is about "
              f"{295 * rss / 100:.1f} GWh a year;",
              "  the meter's own test record belongs to the settlement",
              "  dossier, witnessed by the grid operator (ch 34, ch 37)"]
    emit("a_metering", lines)
    return dict(rss=rss, worst=worst, bad=bad)


# ------------------------------------------------ 4. cabinets and devices
def cabinets() -> dict:
    lines = ["cabinets on a summer day: inside temperature against each device's",
             "  rating", "  cabinet   IP     inside C   devices over their rating"]
    bad = {}
    for c, (ip, t, devs) in src.CABINETS.items():
        over = [d for d, mx in devs if mx < t + 5]
        if over:
            bad[c] = over
        lines.append(f"  {c:8s}  {ip:5s}  {t:8.0f}   {', '.join(over) or '-'}")
    lines += ["  (teaching rule: a device keeps 5 K below its rating)",
              "  the PV block cabinet in full sun is the worst; a device run",
              "  near its limit ages fast (ch 34 life in a hot cabinet) - the",
              "  choice is a sun shield, a cooler or a device rated higher,",
              "  and the IP rating keeps dust out but also heat in"]
    emit("a_cabinets", lines)
    return bad


# ------------------------------------------------ 5. bonding and shields
def bonding(limit: float = 0.1) -> dict:
    lines = [f"cabinet bonding to the earth bar (teaching limit {limit} ohm) and "
             "cable shields"]
    high = [c for c, r in src.BONDS.items() if r > limit]
    for c, r in src.BONDS.items():
        lines.append(f"  {c:8s}  {r:.2f} ohm  {'HIGH' if r > limit else 'ok'}")
    wrong = [(c, k, e) for c, k, e in src.SHIELDS if e != src.SHIELD_RULE[k]]
    lines += ["  shields against the project's rule by cable kind:"]
    lines += [f"    {c} ({k}): earthed at {e}, rule {src.SHIELD_RULE[k]}"
              for c, k, e in wrong]
    lines += ["  a high bond lets a fault or surge raise the cabinet against",
              "  earth; an analogue shield earthed at both ends carries a loop",
              "  current that the 4-20 mA signal reads as noise; an unearthed",
              "  Pt100 shield screens nothing - each is a line in the",
              "  cabinet's test record, found before the first reading"]
    emit("a_bonding", lines)
    return dict(high=high, wrong=wrong)


if __name__ == "__main__":
    budgets()
    certs()
    metering()
    cabinets()
    bonding()
