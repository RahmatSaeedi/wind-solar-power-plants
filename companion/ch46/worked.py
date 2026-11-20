"""Chapter 46 - small worked examples (E-lines) and the numerical answers
of the exercises (P-lines), each computed here.

Run from the project root:   python -m companion.ch46.worked
Writes companion/ch46/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

import math

from companion.ch46 import examples_a as ea
from companion.ch46 import examples_b as eb
from companion.ch46 import examples_c as ec
from companion.ch46 import integrated as it
from companion.ch46 import lab_d
from companion.ch46.common import emit
from plantp import cablemfg as km


def worked() -> None:
    lines = [f"E01 0.0826 ohm at 25 C to 20 C (Al): {km.r_to_20(0.0826, 25):.4f} ohm",
             f"E02 0.0748 ohm at 9 C to 20 C (Al): {km.r_to_20(0.0748, 9):.4f} ohm",
             f"E03 current of 20 MW at 33 kV, pf 0.95: "
             f"{20e6 / (math.sqrt(3) * 33e3 * 0.95):.0f} A",
             f"E04 pole spread of 55.3 / 59.8 / 55.2 ms: "
             f"{km.pole_spread((55.3, 59.8, 55.2)):.1f} ms",
             f"E05 states of three two-position switches: {2 ** 3}",
             f"E06 states reachable with correct interlocks: {len(km.reachable())}",
             f"E07 print 2012 to 2997 m: {2997 - 2012} m on the drum",
             f"E08 loss of 368 A in 0.85 km at 0.0564 ohm/km: "
             f"{3 * 368 ** 2 * 0.0564 * 0.85 / 1000:.1f} kW"]
    emit("worked", lines)


def solutions() -> None:
    st = ea.string_loss()
    dr = ea.drums()
    cr = ea.crimps()
    pr = ea.print_length()
    ct = eb.contacts()
    tm = eb.timing()
    il = eb.interlocks()
    pp = ec.p2p()
    te = ec.terminals()
    rl = ec.relays()
    sc = lab_d.schedule()
    mp = lab_d.mapping()
    mx = lab_d.matrix()
    hb = it.by_hand()
    rej = [d for d, (_, ok) in dr["out"].items() if not ok]
    out = [f"P01 string WS1 loss and far-end drop: {st['loss']:.0f} kW, "
           f"{st['drop']:.2f} %",
           f"P02 drums rejected after correction / by raw reading: "
           f"{', '.join(rej)} / {', '.join(dr['raw_bad'])}",
           f"P03 low crimps and their tool: {len(cr['bad'])}, "
           f"{cr['bad'][0][2]}",
           f"P04 drum D405 length by print and shortfall: {pr['printed']:.0f} m, "
           f"{pr['short']:.0f} m",
           f"P05 panels to check for contact resistance: {', '.join(ct['bad'])}",
           f"P06 panels over the pole-spread limit: {', '.join(tm['bad'])}",
           f"P07 states reachable, correct logic / forbidden reached with fault: "
           f"{il['good']} / {len(il['bad'])}",
           f"P08 missing and extra connections in panel WS1: {len(pp['missing'])}, "
           f"{len(pp['extra'])}",
           f"P09 terminal-plan problems: {len(te)}",
           f"P10 relays differing from the register: {', '.join(rl['odd'])}",
           f"P11 schedule problems: {len(sc['problems'])}",
           f"P12 one-line mapping gaps: {len(mp['gaps'])}",
           f"P13 matrix checks needing a qualified person: {mx}",
           f"P14 segment W001 by hand, current, loss, drop: {hb['i']:.0f} A, "
           f"{hb['loss']:.1f} kW, {hb['drop']:.3f} %"]
    from companion.ch46 import examples_e as ee
    from companion.ch46 import examples_f as ef
    from companion.ch46 import examples_g as eg
    fd = ee.field()
    th = ee.thickness()
    rp = ee.reports()
    cp = ee.compound()
    ag = ee.ageing()
    ho = ee.holm()
    ph = ef.pole_heat()
    tv = ef.travel()
    gs = ef.gas()
    va = ef.variants()
    ctr = ef.ct_records()
    tt = ef.typetest()
    itf = ef.interfaces()
    tr = eg.trip_matrix()
    mk = eg.markers()
    ce = eg.ct_earths()
    wh = eg.wiring_hours()
    pu = eg.punch()
    rd = eg.redlines()
    dt = lab_d.drum_trace()
    ds = lab_d.dossier()
    rc = lab_d.recall()
    out += [f"P15 peak field of the 240 / 630 mm2 cores: {fd['out'][240][2]:.2f} / "
            f"{fd['out'][630][2]:.2f} kV/mm",
            f"P16 peak field of 240 mm2 at a 7.1 mm thin spot: {fd['e_thin']:.2f} kV/mm",
            f"P17 drum ends failing the thickness rules: "
            f"{', '.join(f'{d} {e}' for d, e in th['bad'])}",
            f"P18 report findings / drums: {len(rp)} / {len({d for d, _ in rp})}",
            f"P19 drums and cables under the C-17 notice: {', '.join(cp['drums'])}; "
            f"{', '.join(cp['cables'])}",
            f"P20 L-B ratio rise per 1000 cycles, cycles to 1.0: {ag['L-B'][0]:.2f}, "
            f"{ag['L-B'][1]:.0f}",
            f"P21 Al, 20 kN, 1 spot / 10 spots: {ho[20][0]:.2f} / {ho[20][1]:.2f} "
            "micro-ohm",
            f"P22 extra heat of PVF1 pole L2 at full output: {ph['w']:.1f} W",
            f"P23 closing speed baseline / now: {tv['vb']:.2f} / {tv['vs']:.2f} m/s",
            f"P24 leaking compartment and years to alarm: {', '.join(gs['flagged'])}, "
            f"{gs['years']:.1f}",
            f"P25 ordered-vs-built differences: {len(va)}",
            f"P26 CT records differing: {', '.join(ctr['odd'])}",
            f"P27 type-test gaps: {len(tt)}",
            f"P28 interface problems: {len(itf)}",
            f"P29 trip-matrix differences: {len(tr)}",
            f"P30 marker findings: {len(mk)}",
            f"P31 CT circuits not earthed once: "
            f"{', '.join(c for c, n, _ in ce if n != 1)}",
            f"P32 wiring days by hand / with tester: {wh['days']:.0f} / "
            f"{wh['days_auto']:.0f}",
            f"P33 panels held at the factory: {', '.join(pu['hold'])}",
            f"P34 drawings owed a revision: {', '.join(d for _, d in rd)}",
            f"P35 circuits losing their drum, metres to re-order: {len(dt['hit'])}, "
            f"{dt['need']:,}",
            f"P36 records present / complete cables: {ds['got']}/{ds['tot']}, "
            f"{ds['full']}",
            f"P37 terminations under the K-23 notice: {len(rc['hit'])}"]
    from companion.ch46 import examples_s as es
    from companion.ch46 import examples_t as et
    sm = es.sampling()
    cap = es.capacitance()
    pdr = es.pd_results()
    bb = es.busbar_rise()
    ts = es.timing_stats()
    fs = es.fat_to_site()
    ws = es.wire_sizes()
    fp = es.fat_plan()
    hi = es.history()
    rv = es.revisions()
    rp2 = es.replan()
    it2 = es.itp_cover()
    cy = et.capability()
    co = et.coil_voltage()
    dc = et.dc_demand()
    sp = et.spares()
    pl = et.nameplates()
    al = et.aslaid()
    out += [f"P38 chance 8 of 40 drums find one of 3 bad: {sm[8]:.1%}",
            f"P39 capacitance 240 / 400 / 630 mm2 from geometry: "
            f"{cap['c'][240]:.3f} / {cap['c'][400]:.3f} / {cap['c'][630]:.3f} uF/km",
            f"P40 PD results not credible or missing: "
            f"{', '.join(sorted(d for d, v in pdr.items() if not v.startswith('pass')))}",
            f"P41 busbar rise at 1600 A (n 1.8), current at 65 K: {bb[1.8][0]:.0f} K, "
            f"{bb[1.8][1]:.0f} A",
            f"P42 breakers flagged by ordinary / robust z: "
            f"{', '.join(ts['flag_z']) or 'none'} / {', '.join(ts['flag_r'])}",
            f"P43 poles that rose from FAT to site: "
            f"{', '.join(f'{p} {q}' for p, q, *_ in fs['odd'])}",
            f"P44 wires under the size rule: {len(ws)}",
            f"P45 FAT days and witnessed days: {fp['days']:.1f}, {fp['w_days']:.1f}",
            f"P46 setting change without a record: {', '.join(hi['odd'])}",
            f"P47 revision C: added {', '.join(rv['added'])}, removed "
            f"{', '.join(rv['removed'])}, changed {len(rv['changed'])}",
            f"P48 drums of 1000 / 1500 / 2500 m and waste: "
            + "; ".join(f"{k} x{v[0]} {v[1]} m" for k, v in rp2.items()),
            f"P49 failure modes without a check: {len(it2['gaps'])}",
            f"P50 drum resistance Cpk and expected share over the limit: "
            f"{cy['cpk']:.2f}, {cy['ppm'] / 1e4:.1f} %",
            f"P51 coil voltage with 0.75 / 1.5 mm2: {co[0.75][1]:.1f} / "
            f"{co[1.5][1]:.1f} V",
            f"P52 line-up trip peak and spring recharge: {dc['trip']:.0f} A, "
            f"{dc['motor']:.0f} A",
            f"P53 cabinets below 10 % spare terminals: "
            f"{', '.join(p for p, *_ in sp)}",
            f"P54 nameplates out of place: {len(pl)}",
            f"P55 string WS1 loss, schedule and as laid: {al['loss']['schedule']:.1f}, "
            f"{al['loss']['as laid']:.1f} kW"]
    from companion.ch46 import examples_u as eu
    jn = eu.joints()
    bd = eu.bending()
    tt2 = eu.trip_time()
    rt = eu.retest()
    dtp = eu.drum_temp()
    pr2 = eu.profile()
    out += [f"P56 WS1 cables needing a joint as laid: "
            f"{', '.join(c for c, n in jn.items() if n)}",
            f"P57 bending radius of the 630 mm2 cable and fit: {bd[630][0]:.0f} mm, "
            f"{'yes' if bd[630][1] else 'no'}",
            f"P58 trip path before / after K5, margin left: {tt2['before']:.1f} / "
            f"{tt2['after']:.1f} ms, {tt2['left']:.3f} s",
            f"P59 tests to repeat after the FAT changes: {rt['n']}",
            f"P60 D401 at 20 C with the core at 22 C: {dtp[22.0][0]:.4f} ohm/km",
            f"P61 drop at the far turbine of WS1: {pr2[-1][1]:.2f} %"]
    emit("solutions", out)


if __name__ == "__main__":
    worked()
    solutions()
