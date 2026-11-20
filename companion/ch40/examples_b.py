"""Chapter 40, lesson B (quality planning): the process FMEA ranked by
severity first and by RPN, the control plan of the top risks, the
inspection and test plan with hold, witness and review points, a gauge
R&R study before and after a probe fixture, the capability of the joint
resistance, X-bar/R charts that catch the drifted skids, and sampling
plans for crimp lugs with their operating-characteristic curves.

Run from the project root:   python -m companion.ch40.examples_b
Writes companion/ch40/expected/b_*.txt and diagrams/data/ch40-*.csv.
Teaching values (A-436, A-437); a fictional integrator.
"""
from __future__ import annotations

from companion.ch40 import sources as src
from companion.ch40.common import csv, emit
from plantp import quality as qa

USL = 20.0                                   # joint resistance, micro-ohm


def fmea() -> list[dict]:
    by_sev = qa.fmea_rank(src.FMEA)
    by_rpn = sorted(src.FMEA, key=lambda r: -qa.rpn(r["s"], r["o"], r["d"]))
    lines = ["process FMEA of the skid line: severity first vs RPN",
             "  rank  severity-first                    S  O  D  RPN   RPN rank"]
    for k, r in enumerate(by_sev, 1):
        rk = by_rpn.index(r) + 1
        lines.append(f"  {k:4d}  {r['mode'][:32]:32s} {r['s']:2d} {r['o']:2d}"
                     f" {r['d']:2d}  {qa.rpn(r['s'], r['o'], r['d']):3d}"
                     f"   {rk:2d}")
    lines += ["  classes: S 9-10, then S 7-8, then the rest; within a class",
              "  by S x O (criticality), then by D. By RPN alone the",
              "  wrong-die crimp (S 8) ranks above the MV termination",
              "  (S 10): a product of three ratings hides the severity,",
              "  so RPN only orders rows inside a class (IEC 60812 offers",
              "  the criticality matrix beside RPN)"]
    emit("b_fmea", lines)
    return by_sev


# [start: control]
CONTROL = [  # characteristic, spec, method, sample, reaction (A-437)
    ("MV termination position", "kit drawing", "jointer check + photo",
     "every termination", "stop, re-terminate, report"),
    ("LV joint torque", "70 N m +/- 10 %", "logged wrench + paint mark",
     "every joint", "re-torque, check tool"),
    ("torque wrench TW-xx", "70 +/- 1.4 N m", "analyser check",
     "each shift", "quarantine tool, trace joints"),
    ("earth bond continuity", "<= 0.1 ohm", "low-ohm meter", "every bond",
     "re-make, retest"),
    ("joint resistance", "<= 20 micro-ohm", "micro-ohmmeter, fixture",
     "5 joints a skid, all if one > 17", "100 %, contain skid"),
]
# [end: control]


def control_plan() -> None:
    lines = ["control plan for the top risks of the FMEA"]
    for ch, spec, meth, samp, react in CONTROL:
        lines += [f"  {ch}: {spec}", f"      how: {meth}; {samp}",
                  f"      if out: {react}"]
    lines += ["  each row answers one FMEA cause with a prevention or a",
              "  detection and says what happens when it trips; the",
              "  shift check of the wrench is the row lesson D shows missing"]
    emit("b_control", lines)


def itp() -> dict[str, int]:
    lines = ["inspection and test plan of the skid (H hold, W witness,",
             "R review); the owner's points marked"]
    count = {"H": 0, "W": 0, "R": 0}
    for check, kind in src.ITP.items():
        count[kind] += 1
        lines.append(f"  {kind}  {check}")
    lines += [f"  hold {count['H']}, witness {count['W']}, review "
              f"{count['R']}",
              "  a hold stops work until the owner releases it; a",
              "  witness is notified and may attend, work goes on if",
              "  they do not come; a review is of records only"]
    emit("b_itp", lines)
    return count


def grr() -> tuple[dict, dict]:
    a, b = qa.grr_anova(src.GRR), qa.grr_anova(src.GRR_FIXTURE)
    lines = ["gauge R&R of the micro-ohmmeter (10 joints x 3 inspectors x 2)",
             "  study            repeat.  reprod.   part   %GRR   ndc"]
    for name, r in (("hand-held probes", a), ("probe fixture", b)):
        lines.append(f"  {name:16s} {r['repeatability']:7.3f}  "
                     f"{r['reproducibility']:7.3f}  {r['part']:5.2f}  "
                     f"{r['grr_pct']:5.1f}  {r['ndc']:4d}")
    lines += ["  (variances in micro-ohm squared; ndc = distinct categories)",
              "  a common industry guide: %GRR under 10 good, 10-30",
              "  acceptable with reason, over 30 not; the fixture cut",
              "  repeatability, but the inspectors' bias stays - that",
              "  needs one probe position and training, not hardware"]
    emit("b_grr", lines)
    return a, b


def capability() -> dict[str, tuple]:
    drift = {"S-05", "S-06", "S-07"}
    good = [x for s in src.SERIALS if s not in drift for x in src.RESIST[s]]
    bad = [x for s in drift for x in src.RESIST[s]]
    lines = [f"capability of joint resistance (upper limit {USL:.0f} micro-ohm)"]
    out = {}
    for name, v in (("good tools (35 joints)", good),
                    ("drifted TW-14 (15 joints)", bad)):
        m, s, _, cpk = qa.cp_cpk(v, None, USL)
        ppm = qa.ppm_out(m, s, None, USL)
        out[name] = (m, s, cpk, ppm)
        lines.append(f"  {name:26s} mean {m:5.2f}  sd {s:4.2f}  Cpk "
                     f"{cpk:4.2f}  {ppm:9,.0f} ppm over")
    lines += ["  only one-sided: lower resistance is always better",
              "  a Cpk of 1.9 leaves almost nothing over the limit; the",
              "  drifted tool puts about one joint in fifty over it -",
              "  and many more just under it, where heat builds slowly"]
    emit("b_capability", lines)
    return out


def chart() -> dict:
    base = [src.RESIST[s] for s in src.SERIALS[:4]]
    lim = qa.xbar_r_limits(base)
    lines = ["X-bar and R charts of joint resistance, limits from S-01..S-04",
             f"  X-bar: centre {lim['x_centre']:.2f}, UCL {lim['x_ucl']:.2f},"
             f" LCL {lim['x_lcl']:.2f}",
             f"  R:     centre {lim['r_centre']:.2f}, UCL {lim['r_ucl']:.2f}",
             "  skid   mean   range  signal"]
    rows, flagged = [], []
    for k, s in enumerate(src.SERIALS, 1):
        g = src.RESIST[s]
        m, r = sum(g) / len(g), max(g) - min(g)
        sig = []
        if m > lim["x_ucl"] or m < lim["x_lcl"]:
            sig.append("mean")
        if r > lim["r_ucl"]:
            sig.append("range")
        if sig:
            flagged.append(s)
        rows.append((k, round(m, 2), round(r, 2)))
        lines.append(f"  {s}  {m:5.2f}  {r:5.2f}   {', '.join(sig) or '-'}")
    lines += [f"  out of control: {', '.join(flagged)}",
              "  with four skids the limits are rough; they are refined as",
              "  data grows. The chart would have flagged the drift on the",
              "  first skid built with it - had joint resistance been",
              "  measured at all (lesson D)"]
    csv("ch40-xbar.csv", "k,mean,range", rows)
    csv("ch40-xbar-limits.csv", "what,value",
        [(k, round(v, 3)) for k, v in lim.items()])
    emit("b_chart", lines)
    return dict(lim=lim, flagged=flagged)


def sampling() -> tuple[int, int]:
    n, c = qa.find_plan(0.01, 0.05)
    plans = [(n, c), (50, 1), (20, 0)]
    lines = ["incoming sampling of crimp lugs (lot 2,000; AQL 1 %, LTPD 5 %;",
             "producer's risk 5 %, consumer's risk 10 %)",
             f"  smallest plan that meets both: n = {n}, accept if <= {c}",
             "  plan       P(accept) at 1 %   at 5 %"]
    for pn, pc in plans:
        lines.append(f"  n={pn:3d} c={pc}   {qa.p_accept(pn, pc, 0.01):10.3f}"
                     f"   {qa.p_accept(pn, pc, 0.05):6.3f}")
    lines += ["  the small plans look strict but let most bad lots through;",
              "  sampling protects against bad lots, not bad pieces - a",
              "  critical crimp is controlled at the press (die check), not",
              "  only by sampling what arrives"]
    rows = []
    for k in range(0, 101):
        p = k / 1000
        rows.append((round(p * 100, 1),) + tuple(
            round(qa.p_accept(pn, pc, p), 4) for pn, pc in plans))
    csv("ch40-oc.csv", "p,a,b,c", rows)
    emit("b_sampling", lines)
    return n, c


if __name__ == "__main__":
    fmea()
    control_plan()
    itp()
    grr()
    capability()
    chart()
    sampling()
