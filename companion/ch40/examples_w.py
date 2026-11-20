"""Chapter 40, a fifth round: when to inspect every unit or none (the
all-or-none rule), where the variation of joint resistance comes from
(variance components), human error in wiring checks against an automatic
tester, the cut-in point of an engineering change, recovering the ten-skid
schedule, and insulation readings corrected to one temperature.

Run from the project root:   python -m companion.ch40.examples_w
Writes companion/ch40/expected/w_*.txt and diagrams/data/ch40-*.csv.
Teaching values (A-435 to A-440); a fictional integrator.
"""
from __future__ import annotations

from statistics import mean

from companion.ch40 import sources as src
from companion.ch40.common import csv, emit

# ------------------------------------------------ inspect all or none
# [start: kp]
CHECKS = [  # check, k1 cost to inspect one skid (k u), k2 cost of one
    #         escape (k u), p share of skids with the defect - A-440
    ("relay secondary injection", 0.40, 45.0, 0.030),
    ("MV cable insulation test", 0.15, 60.0, 0.002),
    ("nameplate and label check", 0.02, 0.3, 0.050),
    ("busbar torque-mark check", 0.05, 20.0, 0.004),
]
# [end: kp]


def all_or_none() -> dict[str, str]:
    lines = ["inspect every skid or none? (stable process, perfect check)",
             "  check                        k1     k2    p     k1/k2  rule"]
    out, rows = {}, []
    for name, k1, k2, p in CHECKS:
        brk = k1 / k2
        rule = "all" if p > brk else "none"
        out[name] = rule
        lines.append(f"  {name:27s} {k1:5.2f} {k2:6.1f} {p:5.3f} "
                     f"{brk:6.4f}  {rule}")
    k1, k2 = 0.40, 45.0
    for k in range(0, 41):
        p = k * 0.001
        rows.append((p * 100, round(k1, 4), round(p * k2, 4)))
    csv("ch40-kp.csv", "p,all,none", rows)
    lines += ["  inspect all when p > k1/k2: the cost of checking a skid is",
              "  less than the expected cost of letting its defect through;",
              "  the cable test fails the rule on cost (p 0.2 % < 0.25 %)",
              "  yet stays a hold point: a safety or a contract duty is",
              "  not an economic choice; 'none' never means 'do not watch",
              "  the process' - a small sample keeps p known"]
    emit("w_kp", lines)
    return out


# ------------------------------------------- where the variation comes from
def components(serials) -> dict[str, float]:
    groups = [src.RESIST[s] for s in serials]
    k, n = len(groups), len(groups[0])
    grand = mean(x for g in groups for x in g)
    msb = n * sum((mean(g) - grand) ** 2 for g in groups) / (k - 1)
    msw = sum((x - mean(g)) ** 2 for g in groups for x in g) / (k * (n - 1))
    s2b = max(0.0, (msb - msw) / n)
    return dict(msb=msb, msw=msw, between=s2b, within=msw,
                share_between=s2b / (s2b + msw))


def variance_components() -> dict[str, dict[str, float]]:
    good = [s for s in src.SERIALS if s not in ("S-05", "S-06", "S-07")]
    g = components(good)
    a = components(src.SERIALS)
    pos = [mean(src.RESIST[s][j] for s in good) for j in range(5)]
    rows = [(k + 1, j + 1, src.RESIST[s][j])
            for k, s in enumerate(src.SERIALS) for j in range(5)]
    csv("ch40-multivari.csv", "skid,joint,r", rows)
    csv("ch40-multimean.csv", "skid,mean",
        [(k + 1, round(mean(src.RESIST[s]), 3))
         for k, s in enumerate(src.SERIALS)])
    lines = ["joint resistance: between skids or within a skid?",
             "  (one-way random-effects analysis, 5 joints a skid)",
             "  data                  var between  var within  share between",
             f"  7 skids, good tools   {g['between']:11.2f}  {g['within']:10.2f}"
             f"  {g['share_between']:13.0%}",
             f"  all 10 skids          {a['between']:11.2f}  {a['within']:10.2f}"
             f"  {a['share_between']:13.0%}",
             "  joint means (good skids): " +
             ", ".join(f"{p:.1f}" for p in pos),
             "  with good tools almost all the scatter is joint to joint,",
             "  so the fix lies in making each joint (surface, torque",
             "  sequence), not in anything a whole skid shares; with the",
             f"  three tool-fault skids the between-skid part rises to "
             f"{a['share_between']:.0%}:",
             "  the same analysis points at the tool"]
    emit("w_components", lines)
    return dict(good=g, all=a)


# ------------------------------------------- wiring check: person vs tester
def wiring_check(points: int = 1200, error_rate: float = 1 / 500,
                 miss_manual: float = 0.05, miss_auto: float = 0.001,
                 fat_find: float = 0.6, skids: int = 10) -> dict[str, float]:
    made = points * error_rate * skids
    out = {}
    lines = [f"control wiring: {points} terminations a skid, one wrong in "
             f"{1 / error_rate:.0f}", f"  errors made in ten skids: {made:.1f}",
             "  check                 misses  left after  left after FAT",
             "                        a check  the check   (FAT finds 60 %)"]
    for name, miss in (("point-to-point by hand", miss_manual),
                       ("automatic tester", miss_auto)):
        left = made * miss
        after = left * (1 - fat_find)
        out[name] = after
        lines.append(f"  {name:22s} {miss:7.1%}  {left:9.2f}  {after:13.3f}")
    hours_manual = points * 0.5 / 60
    per = skids / out["point-to-point by hand"]
    lines += [f"  by hand: {hours_manual:.0f} h a skid, and one wrong wire in "
              f"about {per:.0f} skids",
              "  still reaches the site; the tester needs a",
              "  wiring list in machine form (from the design database of",
              "  ch 38) and about 3 h a skid - a person checking 1,200",
              "  points misses some however careful; the tester's misses",
              "  come from a wrong list, so the list itself is reviewed"]
    emit("w_wiring", lines)
    return out


# ------------------------------------------- engineering change: cut-in
def cut_in() -> dict[str, float]:
    built = 5                                   # S-01..S-05 before ECO-07
    factory_h, site_h, rate = 4.0, 8.0, 0.06    # h a skid; k u a person-hour
    travel = 1.2                                # k u a site visit
    config_yr, years = 0.8, 25                  # k u a year for a second config
    opts = {
        "retrofit at the factory": built * factory_h * rate * 2,
        "retrofit at the site": built * (site_h * rate * 2 + travel),
        "leave as built (concession)": config_yr * years,
    }
    lines = ["ECO-07 (relay firmware with the corrected trip logic) after S-05",
             f"  cut-in at S-06; {built} skids already built",
             "  option                         cost k u   then"]
    for k, v in opts.items():
        then = {"retrofit at the factory": "one configuration, retest",
                "retrofit at the site": "one configuration, site test",
                "leave as built (concession)": "two configurations, 25 y"}[k]
        lines.append(f"  {k:30s} {v:8.1f}   {then}")
    lines += ["  the retrofit before shipping is the cheapest and leaves one",
              "  configuration; a concession looks free today but every",
              "  spare, procedure and setting file must know which skid",
              "  has which firmware for 25 years - and a safety function",
              "  that is known wrong is never left by concession"]
    emit("w_cutin", lines)
    return opts


# ------------------------------------------- recovering the schedule
def recover() -> dict[str, dict[str, float]]:
    from companion.ch40.examples_s import schedule
    sch = schedule()
    gap = sch["span"] - 160.0
    crew, rate = 6, 0.06                        # people on the line; k u/h
    opts = {
        "start a week early": dict(hours=40.0, cost=6.5,
                                     note="parts a week sooner"),
        "overtime 10 h/week, 4 weeks": dict(hours=40.0,
                                              cost=40 * crew * rate * 0.5,
                                              note="fatigue, errors"),
        "second shift in week 1": dict(hours=40.0,
                                       cost=40 * crew * rate * 0.25,
                                       note="second trained crew"),
        "overtime at the bottleneck": dict(hours=0.0, cost=0.0,
                                                note="fill time unchanged"),
    }
    lines = [f"ten skids need {sch['span']:.1f} h; the window has 160 h "
             f"(gap {gap:.1f} h)",
             "  option                       hours  cost k u  gap  note"]
    for k, v in opts.items():
        ok = "yes" if v["hours"] >= gap else "no"
        lines.append(f"  {k:28s} {v['hours']:5.0f}  {v['cost']:8.1f}  "
                     f"{ok:4s} {v['note']}")
    cheap = min((k for k in opts if opts[k]["hours"] >= gap),
                key=lambda k: opts[k]["cost"])
    lines += [f"  the gap is the time to fill the line ({sch['first']:.0f} h),",
              "  not its pace: speeding the bottleneck does nothing;",
              f"  cheapest: {cheap} - only if a second",
              "  qualified crew exists, and OP50 has one jointer (lesson",
              "  A); the early start then wins: no fatigue, no new crew,",
              "  if bought parts come a week sooner (a ch 39 question)"]
    emit("w_recover", lines)
    return opts


# ------------------------------------------- insulation at one temperature
IR = {  # skid: (megohm read, bay temperature C) - A-436
    "S-01": (2600, 22), "S-02": (2400, 24), "S-03": (2900, 20),
    "S-04": (1100, 38), "S-05": (2300, 25), "S-06": (2500, 23),
    "S-07": (2200, 26), "S-08": (2700, 21), "S-09": (1500, 21),
    "S-10": (1900, 30),
}


def ir_corrected(base_c: float = 20.0, halving_c: float = 10.0):
    lines = ["MV cable insulation resistance, corrected to 20 C (teaching",
             "  rule: halves for every 10 C rise; the maker's or the",
             "  standard's correction applies in a real test)",
             "  skid   read MOhm  at C  corrected"]
    out, rows = {}, []
    for s, (r, t) in IR.items():
        c = r * 2 ** ((t - base_c) / halving_c)
        out[s] = c
        rows.append((t, r, round(c)))
        lines.append(f"  {s}  {r:9,d}  {t:4d}  {c:9,.0f}")
    raw_low = min(IR, key=lambda s: IR[s][0])
    cor_low = min(out, key=out.get)
    csv("ch40-ir.csv", "t,read,corrected", rows)
    lines += [f"  lowest as read: {raw_low} (a hot bay); lowest corrected: "
              f"{cor_low}",
              "  compare readings only at one temperature: the hot skid is",
              "  normal, and the skid that looked ordinary is the one to",
              "  look at again (a damp termination?)"]
    emit("w_ir", lines)
    return out


if __name__ == "__main__":
    all_or_none()
    variance_components()
    wiring_check()
    cut_in()
    recover()
    ir_corrected()
