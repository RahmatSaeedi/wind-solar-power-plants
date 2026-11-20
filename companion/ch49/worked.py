"""Chapter 49 - small worked examples (E-lines) and the numerical answers
of the exercises (P-lines), each computed here.

Run from the project root:   python -m companion.ch49.worked
Writes companion/ch49/expected/worked.txt and solutions.txt.
Do not run during a render: it rewrites the included outputs.
"""
from __future__ import annotations

import math

from companion.ch49 import examples_a as ea
from companion.ch49 import examples_b as eb
from companion.ch49 import examples_c as ec
from companion.ch49 import examples_e as ee
from companion.ch49 import examples_f as ef
from companion.ch49 import integrated as it
from companion.ch49 import lab_d
from companion.ch49 import sources as src
from companion.ch49.common import emit


def worked() -> None:
    lines = [f"E01 posts in block PVF1-3: 210 x 12 = {210 * 12:,}; modules 21 x 20 x 26 = "
             f"{src.BLOCK['modules']:,}",
             f"E02 piling days, 2,520 posts at 220 a rig-day, 2 rigs: {2520 / 440:.1f}",
             f"E03 radial error of (25, -18) mm: {math.hypot(25, -18):.1f} mm",
             f"E04 torque band of 25 Nm +/- 10 %: {25 * 0.9:.1f} to {25 * 1.1:.1f} Nm",
             f"E05 as-laid change 395 -> 452 m: {(452 - 395) / 395:+.1%}",
             f"E06 joints in a 3,100 m section on 1,500 m drums: "
             f"{math.ceil(3100 / 1500) - 1}",
             f"E07 rate of 5,600 modules in 1,250 crew-hours: {5600 / 1250:.2f} an hour",
             f"E08 toilets for 450 at 1 per 15: {math.ceil(450 / 15)}"]
    emit("worked", lines)


def solutions() -> None:
    pm = ea.show_permits()
    me = ea.methods()
    co = ea.competence()
    rl = ea.release()
    we = ea.welfare()
    rs = ea.response()
    ind = ea.inductions()
    pi = eb.piles()
    tq = eb.torque()
    al = eb.as_laid()
    te = eb.terminations()
    ea_ = eb.earthing()
    st = eb.preservation()
    cr = eb.credit()
    mc = ec.show_mc()
    pu = ec.punch()
    sg = ec.stages()
    rc = ec.reconcile()
    sc = lab_d.schedule()
    hb = it.by_hand()
    la = ee.lookahead()
    pr = ee.productivity()
    wx = ee.weather()
    rv = ee.recovery()
    cl = ee.clashes()
    ax = ef.aux()
    fi = ef.fire()
    im = ef.impairments()
    wa = ef.water()
    mt = ef.meters()
    cd = ef.corridor()
    gr = ef.grievances()
    hi = ef.hiring()
    tr = ef.traffic()
    cf = ef.chance_find()
    out = [f"P01 approvals late or open: {len(pm)}",
           f"P02 activities without an approved method statement: {len(me)}",
           f"P03 expired / soon / unfilled roles: {len(co['expired'])} / "
           f"{len(co['soon'])} / {len(co['missing'])}",
           f"P04 drawings not issued for construction: {len(rl)}",
           f"P05 peak workers / toilets / water m3 a day / beds: {we['peak']} / "
           f"{we['toilets']} / {we['water']:.1f} / {we['beds']}",
           f"P06 fronts over the response target: {', '.join(rs['over'])} "
           f"({rs['minutes'][rs['over'][0]]:.1f} min)",
           f"P07 people inside without a valid induction: {len(ind)}",
           f"P08 posts off position / short: {len(pi['off'])} / {len(pi['short'])}",
           f"P09 torque: missing / outside / suspect: {len(tq['missing'])} / "
           f"{len(tq['outside'])} / {len(tq['suspect'])}",
           f"P10 cables changed more than 5 %: {', '.join(r[0] for r in al)}",
           f"P11 terminations not closed: {len(te)}",
           f"P12 bonds over the limit / not measured: {len(ea_['high'])} / "
           f"{len(ea_['none'])}",
           f"P13 stored items checked late: {', '.join(st)}",
           f"P14 earned progress / mounted share: {cr['progress']:.1%} / "
           f"{cr['mounted']:.0%}",
           f"P15 subsystems ready for turnover: "
           f"{', '.join(s for s, v in mc['ready'].items() if v)}",
           f"P16 open punch A / B: {len(pu.get('A', []))} / {len(pu.get('B', []))}",
           f"P17 complete asset records: {sum(1 for g in sg.values() if not g)} of {len(sg)}",
           f"P18 missing / extra / duplicate serials / far: {len(rc['r']['missing'])} / "
           f"{len(rc['r']['extra'])} / {len(rc['dup'])} / {len(rc['far'])}",
           f"P19 block finish, earliest rule / priority rule / logic: {sc['end']:.0f} / "
           f"{sc['end_p']:.0f} / {sc['free']:.0f} days",
           f"P20 with a second module crew: {sc['end2']:.0f} days",
           f"P21 hand checks: {hb['prog']:.3f}, {hb['t12']:.1f} min, {hb['dust']:,.0f} m3",
           f"P22 look-ahead packages ready: {len(la['ready'])} of {len(la['open'])}",
           f"P23 mean rate 3 / 4 crews: {pr['three']:.2f} / {pr['four']:.2f}",
           f"P24 worst weather month and share: {wx['worst'][0]}, {wx['worst'][4]:.0%}",
           f"P25 recovery: late {rv['late']:.0f} days; cheapest {rv['best']}",
           f"P26 area clashes: {len(cl)}",
           f"P27 battery stored days: {ax['stored']}",
           f"P28 fire submittals open / penetrations with gaps / detectors: "
           f"{len(fi['sub'])} / {len(fi['pen'])} / {len(fi['det'])}",
           f"P29 open impairments: {len(im)}",
           f"P30 construction water / dust share: {wa['total']:,.0f} m3 / "
           f"{wa['dust_share']:.0%}",
           f"P31 month with tickets over the meter: {mt[0][0]} ({mt[0][1] - mt[0][2]} m3)",
           f"P32 towers without access / sections short of a joint bay: "
           f"{', '.join(cd['blocked'])} / {', '.join(cd['short'])}",
           f"P33 grievances past closing time: {', '.join(gr['over'])}",
           f"P34 first month below the hiring commitment: {hi['below'][0]} "
           f"(last {hi['last']:.0%})",
           f"P35 vehicles in the quiet hours: {sum(tr.values())}",
           f"P36 chance-find notification: {cf['notify_h']:.1f} h"]
    from companion.ch49 import examples_s as es
    ld = es.laydown()
    pl = es.pulls()
    bd = es.burndown()
    cc = es.concurrency()
    sc2 = es.scurve()
    fs = es.firestop()
    pd = es.pond()
    se = es.sectional()
    cp = es.camp()
    ra = es.radio()
    out += [f"P37 pallets of the block / laydown for 3 days: {ld['pallets']} / "
            f"{ld['rows'][1][2]:,.0f} m2",
            f"P38 pulls not accepted: {', '.join(c for c, _ in pl)}",
            f"P39 MC by the current rate / sheets a week needed: day {bd['finish']:.0f} / "
            f"{bd['need']:.0f}",
            f"P40 owner only / both / contractor only: {cc['only_owner']} / "
            f"{cc['overlap']} / {cc['only_con']} days",
            f"P41 SPI / forecast last week: {sc2['spi']:.2f} / {sc2['finish']:.1f}",
            f"P42 chance of a find with 10 / 32 inspected: {fs[10]:.0%} / {fs[32]:.0%}",
            f"P43 peak runoff / volume / pond share: {pd['q']:.2f} m3/s / "
            f"{pd['vol']:,.0f} m3 / {pd['share']:.0%}",
            f"P44 sections with missing signatures: {len(se)}",
            f"P45 camp short in month {cp['over'][0][0]} by {cp['over'][0][1] - 270} beds",
            f"P46 fronts needing a communications fallback: {len(ra)}"]
    emit("solutions", out)


if __name__ == "__main__":
    worked()
    solutions()
