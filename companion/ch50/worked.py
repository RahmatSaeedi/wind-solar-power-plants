"""Chapter 50 - small worked examples (E-lines) and the numerical answers
of the exercises (P-lines), each computed here.

Run from the project root:   python -m companion.ch50.worked
Writes companion/ch50/expected/worked.txt and solutions.txt.
Do not run during a render: it rewrites the included outputs.
"""
from __future__ import annotations

from companion.ch50 import examples_a as ea
from companion.ch50 import examples_b as eb
from companion.ch50 import examples_c as ec
from companion.ch50 import examples_e as ee
from companion.ch50 import examples_g as eg
from companion.ch50 import examples_i as ei
from companion.ch50 import integrated as it
from companion.ch50 import lab_d
from companion.ch50.common import emit
from plantp import protection


def worked() -> None:
    lines = [f"E01 strings of CB07 and modules: 20 x 26 = {20 * 26}",
             f"E02 SI curve at 5 x pickup, TMS 1: {protection.trip_time(5, 1, 1):.2f} s",
             f"E03 tolerance of 0.86 s at 5 % + 40 ms: +/-{0.05 * 0.86 + 0.04:.3f} s",
             f"E04 PR of 353 MWh on 60 MWp and 7.1 kWh/m2: {353 / (60 * 7.1):.3f}",
             f"E05 droop 4 % as pu per Hz: {100 / (50 * 4):.2f}",
             f"E06 UPS shortfall 26 of 30 min: {(30 - 26) / 30:.0%}",
             f"E07 cause-effect pairs proven 14 of 17: {14 / 17:.0%}",
             f"E08 contact age 2027-11-02 to 2028-04-01: {151} days"]
    emit("worked", lines)


def solutions() -> None:
    au = ea.show_authority()
    pre = ea.prerequisites()
    ins = ea.instruments()
    st = eb.strings()
    ir = eb.insulation()
    rl = eb.relays()
    sp = eb.step()
    cap = eb.capability()
    dr = eb.droop()
    pr = eb.pr_test()
    pu = ec.punch()
    dv = ec.deviations()
    tr = ec.training()
    sa = ec.spares()
    pk = lab_d.completeness()
    tf = ee.transfer()
    au2 = ee.autonomy()
    sh = ee.shedding()
    il = ee.interlocks()
    fi = ee.show_fire()
    gt = eg.grid_trace()
    ex = eg.export()
    rows = ei.show_rows()
    imp = ei.import_test()
    rs = ei.restore()
    rd = ei.readiness()
    hb = it.by_hand()
    ac = it.acceptance()
    out = [f"P01 energisation requests stopped: {len(au)}",
           f"P02 open prerequisites: {len(pre)}",
           f"P03 instruments out of calibration / without record: {len(ins['expired'])} / "
           f"{len(ins['none'])}",
           f"P04 expected Voc / Isc: {st['voc']:,.0f} V / {st['isc']:.2f} A",
           f"P05 strings failing: {', '.join(st['bad'])}",
           f"P06 strings below the IR limit or without record: {', '.join(ir)}",
           f"P07 relays out: {', '.join(n for n, *_ in rl)}",
           f"P08 step rise / settling: {sp['m']['rise']:.1f} / {sp['m']['settle']:.1f} s",
           f"P09 capability short at P: {', '.join(str(p) for p, *_ in cap)} MW",
           f"P10 measured droop: {dr['droop']:.2f} %",
           f"P11 PR / lower bound / days used: {pr['pr']:.3f} / {pr['lo']:.3f} / {pr['days']}",
           f"P12 punch open / net rate / empty in week: {pu['open']} / {pu['rate']:.1f} / "
           f"{pu['week']:.0f}",
           f"P13 deviations not accepted: {', '.join(dv)}",
           f"P14 roles short of assessed people: {len(tr['short'])}",
           f"P15 spares short: {len(sa)}",
           f"P16 commissioning-pack gaps: {len(pk['gaps'])} of {pk['steps']} steps",
           f"P17 transfer trials over the limit: {len(tf)}",
           f"P18 UPS / station battery pass: {au2['ups']} / {au2['batt']}",
           f"P19 loads shed in the wrong step: {len(sh)}",
           f"P20 interlocks failed / not tested: {len(il['fail'])} / {len(il['none'])}",
           f"P21 cause-effect proven / pairs missing: {fi['share']:.0%} / {len(fi['missing'])}",
           f"P22 requirements untested / open / failed: {len(gt['untested'])} / "
           f"{len(gt['open'])} / {len(gt['failed'])}",
           f"P23 phasing error / sheath / slow intertrip: {', '.join(ex['swapped'])} / "
           f"{len(ex['sheath'])} / {len(ex['slow'])}",
           f"P24 handover rows with a defect: {rows['bad']} of {rows['rows']}",
           f"P25 import accepted / rejected: {imp['accepted']} / {imp['rejected']}",
           f"P26 restore within the objective: {rs['ok']}",
           f"P27 roles / stale contacts / drills open: {len(rd['no_role'])} / "
           f"{len(rd['stale'])} / {len(rd['drills'])}",
           f"P28 hand checks: {hb['voc'] * 25 / 26:,.0f} V, {hb['t']:.2f} s, {hb['pr']:.3f}",
           f"P29 acceptance criteria met: {ac['met']} of {ac['total']}"]
    from companion.ch50 import examples_s as es
    from companion.ch50 import examples_t as et
    no = es.notice()
    ra = es.ratio()
    la = es.latency()
    rt = es.round_trip()
    rp = es.ramp()
    av = es.availability()
    me = es.meters()
    wa = es.warranty()
    rs2 = es.restart()
    ov = et.overlaps()
    rl2 = et.release()
    ab = et.asbuilt()
    up = et.ups_extrapolate()
    dl = et.drill()
    rv = et.reserve()
    out += [f"P30 witnessed tests inside the notice period: {len(no)}",
            f"P31 T1 ratio difference: {ra['err']:+.2%}",
            f"P32 latency 95th / 99th / over 2 s: {la['p95']:.2f} s / {la['p99']:.2f} s / "
            f"{la['over']:.1%}",
            f"P33 round trip with / without auxiliaries: {rt['rte']:.1%} / {rt['rte_dc']:.1%}",
            f"P34 worst one-minute ramp: {rp['worst']:.1f} MW/min",
            f"P35 telemetry availability: {av['a']:.2%}",
            f"P36 mean main-check difference: {me['mean']:+.3%}",
            f"P37 warranty records differing from the contract: {len(wa)}",
            f"P38 auxiliary restart: {rs2['total']:.1f} min",
            f"P39 overlapping permits: {len(ov)}",
            f"P40 turbines released: {len(rl2['ready'])} of 12",
            f"P41 documents at as-built: {ab['share']:.0%}",
            f"P42 UPS at the design load: {up['t_design']:.1f} min",
            f"P43 drill arrival / later than planned: {dl['total']} / {dl['late']:.0f} min",
            f"P44 reserve need / up / down: {rv['e_need']:.1f} / {rv['up']:.1f} / "
            f"{rv['down']:.1f} MWh"]
    from companion.ch50 import examples_u as eu
    di = eu.differential()
    ea2 = eu.earth()
    pw = eu.pq_week()
    re_ = eu.retention()
    ct = eu.call_tree()
    out += [f"P45 differential with one CT set reversed: "
            f"{di['one LV CT set reversed']:.2f} pu",
            f"P46 rise of potential measured: {ea2['g2']:.2f} kV",
            f"P47 THD 95th percentile / maximum: {pw['p95']:.2f} / {pw['mx']:.2f} %",
            f"P48 data kept shorter than required: {len(re_)}",
            f"P49 call tree: all reached in {ct['reach'][ct['last']]} min"]
    from companion.ch50 import examples_v as ev
    tu = ev.tur()
    sh = ev.shifts()
    mu = ev.muster()
    out += [f"P50 tests with an instrument ratio below 4: {len(tu)}",
            f"P51 shifts without an authorised person: {', '.join(sh['gaps'])}",
            f"P52 unaccounted by the log / really inside / still missing: "
            f"{mu['missing']} / {mu['true']} / {mu['still']}"]
    emit("solutions", out)


if __name__ == "__main__":
    worked()
    solutions()
