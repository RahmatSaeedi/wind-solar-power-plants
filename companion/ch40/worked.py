"""Chapter 40 - small worked examples (E-lines) and the numerical answers
of the exercises (P-lines), each computed here.

Run from the project root:   python -m companion.ch40.worked
Writes companion/ch40/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

import math

from companion.ch40 import examples_a, examples_c, examples_e
from companion.ch40 import sources as src
from companion.ch40.common import emit
from plantp import quality as qa


def worked() -> None:
    m, s, cp, cpk = qa.cp_cpk([9.0, 10.0, 11.0, 10.0, 10.0], 7.0, 13.0)
    lines = [f"E01 RTY of three steps 0.98, 0.95, 0.90: "
             f"{qa.rty([0.98, 0.95, 0.90]):.3f}",
             f"E02 takt, 12 units in 3 weeks of 40 h: {qa.takt(120, 12):.0f} h",
             f"E03 Cp and Cpk of 9, 10, 11, 10, 10 in 7-13: {cp:.2f}, "
             f"{cpk:.2f}",
             f"E04 P(accept) n = 50, c = 1 at 2 %: {qa.p_accept(50, 1, 0.02):.3f}",
             f"E05 RPN of S 9, O 3, D 8: {qa.rpn(9, 3, 8)}",
             f"E06 escape after checks finding 50 % and 80 %: "
             f"{qa.escape(1.0, [0.5, 0.8]):.2f}",
             f"E07 TUR, tolerance +/- 5, uncertainty 1.25: "
             f"{qa.tur(5, 1.25):.1f}",
             f"E08 sling leg, 100 kN on two legs at 45 degrees: "
             f"{qa.sling_leg(100, 2, 45):.1f} kN",
             f"E09 learning curve 85 %, unit 4 of a 100 h first: "
             f"{examples_a.unit_hours(100, 4):.1f} h",
             f"E10 ppm over a one-sided limit 3 sigma above the mean: "
             f"{qa.ppm_out(0, 1, None, 3):,.0f}"]
    emit("worked", lines)


def solutions() -> None:
    hours = sum(r[3] for r in src.ROUTE)
    rework = sum((1 - r[4]) * r[5] for r in src.ROUTE)
    y = qa.rty([r[4] for r in src.ROUTE])
    st = examples_a.station_times(False)
    learn = sum(examples_a.unit_hours(125, n, floor=79) for n in range(1, 11))
    good = [x for s in src.SERIALS if s not in ("S-05", "S-06", "S-07")
            for x in src.RESIST[s]]
    m, sd, _, cpk = qa.cp_cpk(good, None, 20.0)
    lim = qa.xbar_r_limits([src.RESIST[s] for s in src.SERIALS[:4]])
    n, c = qa.find_plan(0.01, 0.05)
    g1, g2 = qa.grr_anova(src.GRR), qa.grr_anova(src.GRR_FIXTURE)
    fit = qa.crow_amsaa(src.PILOT, src.PILOT_T)
    t_need = examples_e.target_time(fit, src.TARGET_MTBF)
    pres = examples_c.preservation()
    k = src.CONSEQUENCE
    mwh = k["block_mw"] * k["cf_july"] * 24 * k["outage_days"]
    lat = src.LATENT
    caught48 = lat["share"] * lat["boards"] * examples_e.weibull_cdf(
        48, lat["beta"], lat["eta_h"])
    out = [f"P01 touch hours of a skid: {hours:.0f} h",
           f"P02 expected rework a skid: {rework:.2f} h",
           f"P03 rolled throughput yield: {y:.3f}",
           f"P04 skids needing rework, of ten: {10 * (1 - y):.1f}",
           f"P05 takt, 10 skids in 4 weeks of 40 h: {qa.takt(160, 10):.0f} h",
           f"P06 load of S1 with frames made: {st['S1']:.2f} h",
           f"P07 balance efficiency, frames made: "
           f"{qa.line_balance(st)['efficiency']:.0%}",
           f"P08 hours of the ten first skids on the learning curve: "
           f"{learn:.0f} h",
           f"P09 TUR of the torque wrench (+/- 7 vs +/- 2.8 N m): "
           f"{qa.tur(7, 2.8):.1f}",
           f"P10 guard-banded torque limits: {70 - 7 + 2.8:.1f} to "
           f"{70 + 7 - 2.8:.1f} N m",
           f"P11 RPN of the under-torqued joint (9, 3, 8): {qa.rpn(9, 3, 8)}",
           f"P12 RPN of the MV stress cone (10, 2, 7): {qa.rpn(10, 2, 7)}",
           f"P13 Cpk of joint resistance, good tools: {cpk:.2f}",
           f"P14 mean and sd of joint resistance, good tools: {m:.2f}, "
           f"{sd:.2f} micro-ohm",
           f"P15 X-bar UCL from S-01..S-04: {lim['x_ucl']:.2f} micro-ohm",
           f"P16 R-chart UCL: {lim['r_ucl']:.2f} micro-ohm",
           f"P17 sampling plan for AQL 1 %, LTPD 5 %: n = {n}, c = {c}",
           f"P18 P(accept) n = 50, c = 1 at 5 %: {qa.p_accept(50, 1, 0.05):.3f}",
           f"P19 %GRR with hand-held probes: {g1['grr_pct']:.1f}",
           f"P20 %GRR with the fixture: {g2['grr_pct']:.1f}",
           f"P21 distinct categories with the fixture: {g2['ndc']}",
           f"P22 Crow-AMSAA beta of the pilot run: {fit['beta']:.2f}",
           f"P23 instantaneous MTBF at 2,000 h: {fit['mtbf_now']:.0f} h",
           f"P24 test hours to an MTBF of 1,000 h: {t_need:,.0f} h",
           f"P25 desiccant life in storage: {pres['days']:.1f} days",
           f"P26 energy lost by S-06, 9 days in July: {mwh:.0f} MWh",
           f"P27 its value at 70 u/MWh: {mwh * 70 / 1000:.1f} k u",
           f"P28 escape share before / after the actions: "
           f"{qa.escape(1, [0, 0.3, 0]):.2f} / "
           f"{qa.escape(1, [0.5, 0.3, 0.95]):.4f}",
           f"P29 latent boards caught by a 48 h burn-in: {caught48:.2f}",
           f"P30 sling leg, 257 kN, two legs at 60 degrees: "
           f"{qa.sling_leg(257, 2, 60):.0f} kN",
           f"P31 solvent from 300 L of paint at 420 g/L: {300 * 0.42:.0f} kg",
           f"P32 DC link: time to fall from 1,100 V to 50 V, tau 100 s: "
           f"{100 * math.log(1100 / 50):.0f} s"]
    out += more_solutions()
    emit("solutions", out)


def more_solutions() -> list[str]:
    from companion.ch40 import examples_s as es, examples_t as et
    o = es.oee(160, 22, 8, 13, 12)
    span, _ = es.flow_shop(list(es_station_times().values()), 10)
    ss = 1.645 * 18 * math.sqrt(10)
    cq = {k: sum(v.values()) for k, v in es.COPQ.items()}
    ub = math.sqrt(sum(u * u for _, u, _ in et.BUDGET))
    w = et.warranty_cost()
    m = et.mtbf_interval()
    c = et.cpk_interval()
    a = et.aoq()
    return [f"P33 OEE of the FAT bay: {o['oee']:.0%}",
            f"P34 lead time with WIP 15 at 2.5 skids a week: {15 / (10 / 160):.0f} h",
            f"P35 stations for 36 h of tasks at a 16 h cycle: "
            f"{len(es.assign(es.TASKS, 16.0))}",
            f"P36 ten skids through the line (frames bought): {span:.1f} h",
            f"P37 safety stock of lugs: {ss:.0f}; reorder point "
            f"{60 * 10 + ss:.0f}",
            f"P38 cost of quality of the ten skids: {sum(cq.values()):.1f} k u",
            f"P39 calibration interval for 95 % in tolerance (M 400 d): "
            f"{-400 * math.log(0.95):.0f} days",
            f"P40 combined and expanded uncertainty of a reading: {ub:.2f}, "
            f"{2 * ub:.2f} micro-ohm",
            f"P41 95 % lower bound of Cpk from 35 joints: {c['lower']:.2f}",
            f"P42 worst average outgoing quality (n 132, c 3): {a['aoql']:.2%}",
            f"P43 expected warranty claims of 60 parts: {w['claims']:.1f}",
            f"P44 95 % lower bound of MTBF (4 failures, 43,800 h): "
            f"{m['lower']:,.0f} h"] + third_round()


def third_round() -> list[str]:
    from companion.ch40 import examples_u as eu
    t = eu.time_study()
    lay = eu.layout()
    fa = eu.false_accept()
    arl = eu.arl()
    return [f"P45 standard time of one joint: {t['std']:.2f} min; 24 joints "
            f"{t['per_skid']:.2f} h",
            f"P46 kanban cards for busbar kits: {eu.kanban()['cards']}",
            f"P47 economic order quantity of frames: {eu.eoq()['q']:.1f}",
            f"P48 flow distance saved by the straight line: "
            f"{lay['as built'] - lay['straight line']:.0f} m a skid",
            f"P49 chance a 19.9 reading is really over 20: {fa[19.9]:.1%}",
            f"P50 ARL of the X-bar chart at a half-sigma shift: {arl[0.5]:.0f}",
            f"P51 share found by ten thermal cycles (k 0.12): "
            f"{eu.screen()[10]:.0%}",
            f"P52 zero-failure hours for MTBF 1,000 h at 90 %: "
            f"{eu.demo_test()[0.9]:,.0f} h"] + fourth_round()


def fourth_round() -> list[str]:
    from companion.ch40 import examples_v as ev
    pull = ev.crimp_capability()
    sc = ev.sampling_compare()
    d = ev.factorial()
    ss = ev.stress_strength()
    return [f"P53 Cpk of crimp pull force: {pull['cpk']:.2f} "
            f"({pull['ppm']:,.0f} ppm under)",
            f"P54 variables plan for AQL 1 %, LTPD 5 %: n = {sc['n_var']},"
            f" k = {sc['k']:.2f}",
            f"P55 effects of the crimp factorial: A {d['a']:+.2f}, B "
            f"{d['b']:+.2f}, AB {d['ab']:+.2f} kN",
            f"P56 chance of lug failure, strength 300 kN sd 50: "
            f"{ss[(300.0, 50.0)]:.1e}",
            f"P57 certificates with a finding: "
            f"{sum(1 for v in ev.certificates().values() if v)} of 6"] \
        + fifth_round()


def fifth_round() -> list[str]:
    from companion.ch40 import examples_w as ew
    vc = ew.variance_components()
    wc = ew.wiring_check()
    ci = ew.cut_in()
    ir = ew.ir_corrected()
    return [f"P58 break-even defective share of relay injection: "
            f"{0.40 / 45.0:.2%}",
            f"P59 share of variance between skids, good tools / all: "
            f"{vc['good']['share_between']:.0%} / "
            f"{vc['all']['share_between']:.0%}",
            f"P60 wrong wires reaching the site in ten skids, by hand: "
            f"{wc['point-to-point by hand']:.2f}",
            f"P61 cost of retrofitting five skids at the factory: "
            f"{ci['retrofit at the factory']:.1f} k u",
            f"P62 S-04 insulation corrected to 20 C: {ir['S-04']:,.0f} MOhm"]


def es_station_times():
    return examples_a.station_times(True)


if __name__ == "__main__":
    worked()
    solutions()
