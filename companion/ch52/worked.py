"""Chapter 52 - small worked examples (E-lines) and the numerical answers
of the exercises (P-lines), each computed here.

Run from the project root:   python -m companion.ch52.worked
Writes companion/ch52/expected/worked.txt and solutions.txt.
Do not run during a render: it rewrites the included outputs.
"""
from __future__ import annotations

import math

from companion.ch52 import examples_a as ea
from companion.ch52 import examples_b as eb
from companion.ch52 import examples_c as ec
from companion.ch52 import examples_e as ee
from companion.ch52 import examples_g as eg
from companion.ch52 import examples_h as eh
from companion.ch52 import examples_i as ei
from companion.ch52 import integrated as it
from companion.ch52 import lab_d, lab_f
from companion.ch52.common import emit
from plantp import ram


def worked() -> None:
    lines = [f"E01 MTBF from 5 failures in 10 unit-years: {10 * 8760 / 5:,.0f} h",
             f"E02 A_i for MTBF 17,520 h, MTTR 24 h: {ram.a_inherent(17_520, 24):.5f}",
             f"E03 series 0.99 and 0.98: {ram.series([0.99, 0.98]):.4f}",
             f"E04 two in parallel at 0.9: {ram.parallel([0.9, 0.9]):.4f}",
             f"E05 2 of 3 at 0.95: {ram.k_of_n(2, 3, 0.95):.5f}",
             f"E06 Weibull R(30,000 h; 2.5, 60,000 h): "
             f"{float(ram.w_reliability(30_000, 2.5, 60_000)):.3f}",
             f"E07 Poisson P(no demand) for a mean of 0.5: {math.exp(-0.5):.3f}",
             f"E08 best cleaning interval for C 6,608 u, r E p 25.2 u/day2: "
             f"{math.sqrt(2 * 6_608 / 25.2):.0f} days"]
    emit("worked", lines)


def solutions() -> None:
    wl = ea.workload()
    st = ea.strategy()
    av = ea.availabilities()
    pr = ea.priorities()
    mb = ea.make_or_buy()
    sp = ea.spares()
    ps = eb.pv_sample()
    vb = eb.vibration()
    pf = eb.pf()
    ol = eb.oil()
    hs = eb.heatsink()
    dg = eb.dga()
    wr = eb.wear()
    so = eb.bess_soh()
    se = eb.sensor()
    fb = eb.fibre()
    pm = eb.pm_by_subsystem()
    ch = ec.chronology()
    au = ec.authority()
    rc = ec.rca()
    sg = ec.stages()
    vf = ec.verify()
    rp = ec.repeats()
    pt = ec.permits()
    q = lab_d.quality()
    dt = lab_d.detection()
    lc = lab_d.localise()
    dg2 = lab_d.diagnosis()
    rt = lab_d.root_cause()
    ac = lab_d.acceptance()
    wb = ee.exp_vs_weibull()
    mt = ee.mtbf_meaning()
    iv = ee.intervals()
    gr = ee.growth()
    rb = ee.export_rbd()
    ft = ee.fault_tree()
    cc = ee.ccf()
    kn = ee.turbines()
    sh = ee.shared_cable()
    al = ee.allocation()
    rg = lab_f.register()
    en = lab_f.energy_case()
    mc = lab_f.monte_carlo()
    sc = lab_f.scenarios()
    me = eg.methods()
    ci = eg.interval()
    rs = eg.residue()
    bk = eg.breakage()
    wh = eg.wash_hours()
    ro = eg.runoff()
    rbt = eg.robots()
    ins = eh.inspections()
    esp = eh.spares()
    tm = eh.outage_timing()
    lr = eh.line_repair()
    bd = eh.boundary()
    ck = ei.checks()
    rq = ei.repeats()
    wa = ei.warranty()
    ms = ei.mtbf_sources()
    ho = ei.handoff()
    hb = it.by_hand()
    rv = it.review()
    out = [f"P01 PM / CM hours / crew load: {wl['pm']:,.0f} / {wl['cm']:,.0f} / {wl['load']:.0%}",
           f"P02 classes given 'condition-based': "
           f"{sum(1 for v in st.values() if v.startswith('condition'))}",
           f"P03 operational availability, PV inverter: {av['PV inverter'][2]:.4f}",
           f"P04 first request: {pr[0]}",
           f"P05 in-house / contractor / break-even: {mb['c_in']:,.0f} / {mb['c_co']:,.0f} u / "
           f"{mb['be']:,.0f} h",
           f"P06 spares inverter / PCS: {sp['PV inverter'][1]} / {sp['BESS PCS'][1]}",
           f"P07 sample size / chance to find one bad string: {ps['n']} / {ps['p_find']:.0%}",
           f"P08 vibration alert / alarm week: {vb['alert']} / {vb['alarm']}",
           f"P09 hand readings needed / interval: {pf['hand-held reading'][1]} / "
           f"{pf['hand-held reading'][2]:.1f} weeks",
           f"P10 fastest oil iron rise: {ol['worst']} {ol['rate']:+.1f} ppm/month",
           f"P11 heat-sink slope / filters changed: {hs['slope']:.2f} K/month / month {hs['clean']}",
           f"P12 H2 rise in a quarter: x{dg['h2_ratio']:.1f}",
           f"P13 WS2 wear used: {wr['WS2']:.1%}",
           f"P14 container below median - 1.5: {so['low']}",
           f"P15 pyranometer drop before cleaning: {se['drop']:.1%}",
           f"P16 west ring margin: {fb['west ring']:.1f} dB",
           f"P17 PV preventive hours: {pm['PV'][0]:,.0f}",
           f"P18 first event / unit that rode through: {ch['first']} / {ch['rode']}",
           f"P19 tasks needing the grid operator: {au['grid']}",
           f"P20 RCA links without evidence: {rc['gaps']}",
           f"P21 detect / wait-parts share of down time: {sg['share']['detect']:.0%} / "
           f"{sg['share']['wait parts']:.0%}",
           f"P22 failing bins / thin bins: {vf['fail']} / {vf['thin']}",
           f"P23 assets with repeats: {', '.join(rp['rep'])}",
           f"P24 missing permit / isolation / hand-back: {pt['miss']}",
           f"P25 frozen days / PR in the drift: {q['frozen']} / {q['pr_drift']:.3f}",
           f"P26 CUSUM day / delay / found: {dt['day']} / {dt['delay']} / {dt['found']}",
           f"P27 low combiners: {', '.join(f'CB{k:02d}' for k, _ in lc['low'])}",
           f"P28 diagnosis steps recorded: {dg2['steps']}",
           f"P29 root-cause links without evidence / rows to check: {rt['gaps']} / {rt['rows']}",
           f"P30 accept mean / +/- / lost / avoidable: {ac['mean']:.4f} / "
           f"{ac['half']:.4f} / {ac['lost']:.1f} / {ac['saved']:.1f} MWh",
           f"P31 Weibull mean life: {wb['mean']:,.0f} h",
           f"P32 inverter MTBF / one-year survival: {mt['mtbf']:,.0f} h / {mt['surv']:.0%}",
           f"P33 failures for a factor-2 interval: {iv['need']}",
           f"P34 Crow-AMSAA slope: {gr['beta']:.2f}",
           f"P35 some / full export availability: {rb['any']:.5f} / {rb['full']:.5f}",
           f"P36 cut sets / top / line share: {ft['cuts']} / {ft['exact']:.2e} / {ft['line']:.0%}",
           f"P37 server pair at beta 0.10: {cc[0.10]:.6f}",
           f"P38 all 12 turbines up: {kn[12]:.3f}",
           f"P39 all four blocks out, independent / shared: {sh['indep']:.1e} / {sh['shared']:.1e}",
           f"P40 plant energy availability (first year): {al['plant']:.1%}",
           f"P41 highest RPN: {rg[0]}",
           f"P42 energy lost / availability / gap to model: {en['tot']:,.0f} MWh / {en['ea']:.2%} "
           f"/ {en['gap'] / 1000:.1f} GWh",
           f"P43 MC mean / P90 / with spares: {mc['mean']:,.0f} / {mc['p90']:,.0f} / "
           f"{mc['spared']:,.0f} MWh",
           f"P44 services June vs December: "
           f"{sc['turbine services all in December'] - sc['turbine services all in June']:,.0f} MWh",
           f"P45 water a campaign, truck + brush: {me['truck with brush, RO water']['water']:.0f} m3",
           f"P46 best interval, truck + brush: {ci['truck with brush, RO water'][1]:.0f} days",
           f"P47 residue, raw well water: {rs['raw well water']:.0f} mg/m2",
           f"P48 modules broken a year by the lance: {bk['truck, high pressure lance']:.1f}",
           f"P49 hot day hours / night hours: {wh['hot_day']} / {wh['night']:,}",
           f"P50 runoff a year, lance: {ro['truck, high pressure lance']:.0f} m3",
           f"P51 robots down on an average day: {rbt['down']:.1f}",
           f"P52 export inspections overdue / plant's: {ins['late']} / {ins['mine']}",
           f"P53 export spare lines short: {len(esp)}",
           f"P54 outage energy day / night: {tm['day']:,.0f} / {tm['night']:,.0f} MWh",
           f"P55 line restore mean / P90 / mean with part: {lr['mean']:.1f} / {lr['p90']:.1f} / "
           f"{lr['mean_np']:.1f} h",
           f"P56 assets by owner: {bd}",
           f"P57 orders failing a check: {ck['bad']}",
           f"P58 repeat pairs from orders: {rq['rep']}",
           f"P59 warranty candidates / ready: {wa['claims']} / {wa['ready']}",
           f"P60 MTBF orders / SCADA: {ms['wo']:,.0f} / {ms['scada']:,.0f} h",
           f"P61 handoffs over a day: {ho['late']}",
           f"P62 hand checks: A_i {hb['ai']:.5f}, q_T {hb['q_t']:.4f}, m {hb['m']:.2f}",
           f"P63 maintenance review: {rv['ok']} of {rv['total']}"]
    from companion.ch52 import examples_s as es
    kp = es.indicators()
    er = es.erosion()
    ph = es.pitch_heat()
    tr = es.tracker()
    rs2 = es.response()
    rr = es.rate_ratio()
    ag = es.age_replace()
    pa = es.pair()
    im = es.importance()
    sn = es.sensitivity()
    rb2 = es.robot_vs_truck()
    pt2 = es.patrol()
    oc = es.other_code()
    cl = es.closing()
    out += [f"P64 PM on time / backlog weeks: {kp['on_time']:.0%} / {kp['weeks']:.1f}",
            f"P65 category 3 lost energy: {er['cat 3 (leading edge open)'][0]:.0f} MWh/yr",
            f"P66 T03 pitch battery life: {ph['T03 (fan seized)']:.1f} years",
            f"P67 tracker rows flagged: {', '.join(tr['bad'])}",
            f"P68 contractor late / median: {rs2['late']} / {rs2['median']:.1f} h",
            f"P69 rate ratio / p: {rr['ratio']:.2f} / {rr['p']:.3f}",
            f"P70 best age / cost rate / run to failure: {ag['t']:.2f} yr / {ag['rate']:.3f} / "
            f"{ag['run']:.3f}",
            f"P71 both transformers out, two crews / one: {pa['two']:.2e} / {pa['one']:.2e}",
            f"P72 importance of the line / of T1: {im['line']:.5f} / {im['T1']:.5f}",
            f"P73 most sensitive input: {sn['top'][0]} {sn['top'][1]} {sn['top'][2]:+.0f} MWh",
            f"P74 NPV truck / robots: {rb2['npv_t']:,.0f} / {rb2['npv_r']:,.0f} u",
            f"P75 patrol cost foot / drone: {pt2['foot'][1]:,.0f} / {pt2['drone'][1]:,.0f} u",
            f"P76 share of 'OTHER' codes: {oc['share']:.0%}",
            f"P77 closing median / over a week: {cl['median']:.1f} d / {cl['late']}"]
    from companion.ch52 import examples_t as et
    bu = et.budget()
    op = et.opportunistic()
    hs2 = et.hotspots()
    ra = et.radiators()
    sf = et.sf6()
    ce = et.cell_spread()
    yw = et.yaw()
    ca = et.causes()
    sb = et.standby()
    bs = et.bootstrap()
    hl = et.hail()
    td = et.trafo_day()
    ss = et.soiling_triggers()
    cf = et.cable_fault()
    fr = et.field_audit()
    nm = et.naming()
    out += [f"P78 budget / per MW: {bu['tot']:,.0f} / {bu['per_mw']:.1f} k u",
            f"P79 opportunistic energy kept: {op['mwh']:.0f} MWh",
            f"P80 hot spots to replace: {hs2['replace (>= 20 K)']}",
            f"P81 radiator excess at 0.85 pu: {ra['excess']:.1f} K",
            f"P82 SF6 months to alarm: {sf['months']:.0f}",
            f"P83 cell spread rise: {ce['rise']} mV",
            f"P84 yaw loss: {yw['loss']:.1%} = {yw['mwh']:.0f} MWh",
            f"P85 two likeliest causes: {ca['share2']:.0%}",
            f"P86 active pair / cold standby: {sb['active']:.6f} / {sb['cold']:.6f}",
            f"P87 availability / 90 % interval: {bs['a']:.4f} / {bs['lo']:.4f}-{bs['hi']:.4f}",
            f"P88 hail expected / in the event: {hl['exp']:.0f} / {hl['event']:,.0f} MWh",
            f"P89 days without loss / by quarter: {td['zero']} / {td['q']}",
            f"P90 washes / mean ratio: {ss['n']} / {ss['mean']:.3f}",
            f"P91 fastest location: {min(cf.values()):.0f} h",
            f"P92 register mismatch / interval: {fr['p']:.0%} / {fr['lo']:.0%}-{fr['hi']:.0%}",
            f"P93 IDs breaking the rule: {len(nm['bad'])}"]
    from companion.ch52 import examples_u as eu
    rc2 = eu.rcm()
    hd = eu.hidden()
    po = eu.pool()
    fbk = eu.fallback()
    wt = eu.wash_water()
    cp = eu.cost_pareto()
    rv2 = eu.response_value()
    sk = eu.key_person()
    sp2 = eu.repair_spread()
    out += [f"P94 modes given a failure-finding test: "
            f"{sum(1 for v in rc2.values() if v.startswith('failure-finding'))}",
            f"P95 test interval detector / relay / diesel: "
            f"{hd['fire detector loop']:.1f} / {hd['protection relay trip path']:.1f} / "
            f"{hd['diesel start']:.1f} months",
            f"P96 inverter spares one plant / pooled two: {po['one']} / {po['two']}",
            f"P97 fallback dead, yearly / half-yearly test: {fbk['q12']:.3f} / {fbk['q6']:.4f}",
            f"P98 water margin normal / drought: {wt['normal']:+,.0f} / {wt['drought']:+,.0f} m3",
            f"P99 first by count / by cost: {cp['count']} / {cp['cost']}",
            f"P100 4 h / 24 h response a year: {rv2['rows'][0][2]:,.0f} / "
            f"{rv2['rows'][2][2]:,.0f} u",
            f"P101 single-person / no-person skills: {sk['single']} / {sk['none']}",
            f"P102 outage median / mean / P90: {sp2['med']:.0f} / {sp2['mean']:.1f} / "
            f"{sp2['p90']:.0f} h"]
    emit("solutions", out)


if __name__ == "__main__":
    worked()
    solutions()
