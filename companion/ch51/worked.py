"""Chapter 51 - small worked examples (E-lines) and the numerical answers
of the exercises (P-lines), each computed here.

Run from the project root:   python -m companion.ch51.worked
Writes companion/ch51/expected/worked.txt and solutions.txt.
Do not run during a render: it rewrites the included outputs.
"""
from __future__ import annotations

from companion.ch51 import examples_a as ea
from companion.ch51 import examples_b as eb
from companion.ch51 import examples_e as ee
from companion.ch51 import examples_f as ef
from companion.ch51 import examples_l as el
from companion.ch51 import integrated as it
from companion.ch51 import lab_d
from companion.ch51.common import emit


def worked() -> None:
    lines = [f"E01 hours on shift of a 4-shift 12-h roster in a year: {8760 / 4:,.0f} each",
             f"E02 battery energy for 5 MW over 1 h at eta 0.927: {5 / 0.927:.2f} MWh",
             f"E03 imbalance of 450 MWh short at 30 u: {450 * 30:,} u",
             f"E04 week of 1-hour logs: {7 * 24} rounds",
             f"E05 permits overrun 17 of 283: {17 / 283:.1%}",
             f"E06 diesel tank 1,200 L at 24 L/h: {1200 / 24:.0f} h",
             f"E07 wash net 46 MWh x 50 - 1,800: {46 * 50 - 1800:+,} u",
             f"E08 local share 15 of 46: {15 / 46:.0%}"]
    emit("worked", lines)


def solutions() -> None:
    ro = ea.roster()
    ho = ea.handover()
    lw = ea.log_week()
    dl = ea.deadline()
    pm = ea.permits()
    rp = ea.reporting()
    pr = ea.procedures()
    lb = eb.lost_by_cause()
    sc = eb.soc_limits()
    cm = eb.comms_loss()
    al = eb.alarms()
    rs = eb.restoration()
    tl = lab_d.timeline()
    cp = lab_d.compare()
    lg = lab_d.shift_log()
    ln = lab_d.learning()
    st = ee.settlement()
    im = ee.imbalance_month()
    bi = ee.bias()
    re_ = ee.reserve()
    p9 = ee.p90_schedule()
    sv = ee.service()
    ax = ef.auxiliaries()
    ft = ef.fire_tests()
    wa = ef.water()
    wv = ef.wash_value()
    pt = ef.patrol()
    ou = ef.outages()
    co = el.commitments()
    tg = el.tags()
    wo = el.work_orders()
    ex = el.exercises()
    hb = it.by_hand()
    rv = it.review()
    a, b = cp["A follow the plan"], cp["B act on update"]
    out = [f"P01 roster gaps: {len(ro)}",
           f"P02 handover items missed: {len(ho)}",
           f"P03 silent log hours / at night: {lw['silent']} / {lw['night']}",
           f"P04 days with under an hour before the DA deadline: {len(dl['late'])}",
           f"P05 permits / overran / conflicts: {pm['tot']} / {pm['over']} / {pm['conf']}",
           f"P06 events reported late: {len(rp)}",
           f"P07 procedures past review: {len(pr)}",
           f"P08 lost energy total / named: {lb['total']:,.0f} / "
           f"{lb['total'] - lb['lost'].get('unexplained', 0):,.0f} MWh",
           f"P09 battery hours at the upper limit / at the floor: {sc['at_max']} / "
           f"{sc['at_floor']}",
           f"P10 hours on fallback in the comms loss: {cm['fallback']}",
           f"P11 alarm hours over the target / worst hour: {al['over']} / {al['top']}",
           f"P12 restoration to full export: {rs['total']} min",
           f"P13 shift A / B curtailed: {a['curt']:.1f} / {b['curt']:.1f} MWh",
           f"P14 shift A / B imbalance: {a['imb']:,.0f} / {b['imb']:,.0f} u",
           f"P15 log entries missing a field: {len(lg['missing'])}",
           f"P16 learning items: {len(ln)}",
           f"P17 months with missing meter intervals: {', '.join(map(str, st['bad']))}",
           f"P18 half-year imbalance: {sum(im.values()):,.0f} u",
           f"P19 forecast bias before / after the update: {bi['before']:+.1f} / "
           f"{bi['after']:+.1f} MW",
           f"P20 reserve for 95 % of daytime hours: {re_['up']:.1f} MW",
           f"P21 imbalance P50 / P90 schedule: {p9['p50']:,.0f} / {p9['p90']:,.0f} u",
           f"P22 service availability: {sv['a']:.1%}",
           f"P23 station battery autonomy / diesel hours / fuel: {ax['hours']:.1f} h / "
           f"{ax['run_h']:.1f} h / {ax['fuel']:.0f} L",
           f"P24 fire tests overdue: {len(ft)}",
           f"P25 water months over 10 %: {', '.join(map(str, wa['over']))}",
           f"P26 wash net, normal / drought: {wv['normal']:+,.0f} / {wv['scarce']:+,.0f} u",
           f"P27 spans late / too close: {', '.join(pt['late'])} / {', '.join(pt['close'])}",
           f"P28 outage requests short of notice: {len(ou)}",
           f"P29 commitments late / local share: {len(co['late'])} / {co['local']:.0%}",
           f"P30 SCADA tags missing from the register: {len(tg)}",
           f"P31 work orders without asset / code / test: {len(wo['no_asset'])} / "
           f"{len(wo['no_code'])} / {len(wo['no_test'])}",
           f"P32 exercises short / incidents / near misses: {len(ex['short'])} / "
           f"{ex['inc']} / {ex['nm']}",
           f"P33 hand checks: {hb['floor']:.1f} MWh, {hb['room']:.1f} MWh, {hb['hours']:.1f} h",
           f"P34 operating review: {rv['ok']} of {rv['total']}"]
    from companion.ch51 import examples_s as es
    fa = es.fatigue()
    rb = es.repeat_back()
    ot = es.outages()
    xc = es.excursions()
    mc = es.moc()
    cc = es.curtailment_classes()
    hv = es.hvac()
    ww = es.wash_water()
    sk = es.skill()
    ac = es.activations()
    lf = es.line_faults()
    gv = es.grievances()
    fw = es.firmware()
    dq = es.data_quality()
    out += [f"P35 people over the night-shift limit: {len(fa)}",
            f"P36 instructions without repeat-back / time: {len(rb['no_rb'])} / "
            f"{len(rb['no_t'])}",
            f"P37 outages / hours / MTTR / waiting: {len(es.OUTAGES)} / {ot['down']} / "
            f"{ot['mttr']:.1f} h / {ot['wait'] / ot['down']:.0%}",
            f"P38 minutes over the export limit / peak: {xc['minutes']} / {xc['peak']:.1f} MW",
            f"P39 changes open: {len(mc)} of {len(es.CHANGES)}",
            f"P40 curtailment total: {cc['tot']:.0f} MWh",
            f"P41 control room to 35 C: {hv['minutes']:.0f} min (steady {hv['t_ss']:.0f} C)",
            f"P42 wash-water samples over the limit: {len(ww)}",
            f"P43 skill at 1 / 3 / 24 h: " + " / ".join(f"{sk[k][1]:+.2f}" for k in (1, 3, 24)),
            f"P44 failed service activations: {ac['bad']}",
            f"P45 permanent line faults / hours: {lf['perm']} / {lf['hours']:.1f}",
            f"P46 grievances / late ack / late close: {gv['n']} / {gv['late_ack']} / "
            f"{gv['late_close']}",
            f"P47 devices off the firmware baseline: {sum(fw.values())}",
            f"P48 tags not usable: {dq['tot']} ({dq['share']:.1%})"]
    from companion.ch51 import examples_t as et
    sf = et.staffing()
    lr = et.limits_register()
    sd = et.soc_drift()
    qf = et.q_following()
    cp2 = et.competence()
    rd = et.redeclare()
    rw = et.ramp_warnings()
    rc = et.recovery()
    dz = et.diesel_tests()
    bt = et.battery_trend()
    fl = et.false_alarms()
    ln2 = et.line_rating()
    nt = et.notice()
    sp = et.spares()
    ct = et.contacts()
    out += [f"P49 people needed / on roster / overtime: {sf['need']:.1f} / {sf['have']} / "
            f"{sf['overtime']:,.0f} h",
            f"P50 limits that disagree: {len(lr)}",
            f"P51 longest gap / SOC error / days the margin allows: {sd['worst']} d / "
            f"{sd['err']:.1f} % / {sd['days']:.1f} d",
            f"P52 Q intervals out of tolerance after settling: {qf['out']}",
            f"P53 competences expired / expiring / APs valid next month: "
            f"{cp2['expired']} / {cp2['soon']} / {cp2['ap_ok']}",
            f"P54 hours with a wrong declaration: {rd['missed']}",
            f"P55 ramps: hits / misses / false / POD / FAR: {rw['hits']} / {rw['misses']} / "
            f"{rw['false']} / {rw['pod']:.0%} / {rw['far']:.0%}",
            f"P56 drawn / recovery / left after 3 / hours: "
            f"{rc['used']:.2f} MWh / {rc['t_rec']:.0f} min / {rc['after3']:.2f} / "
            f"{rc['hours_left']:.2f}",
            f"P57 light diesel runs / loaded quarters: {dz['light']} / {dz['quarters']}",
            f"P58 battery slope / years to 80 %: {bt['slope']:.2f} %/q / {bt['years']:.1f}",
            f"P59 false alarms / worst type: {fl['tot']} / {fl['worst']}",
            f"P60 min rating / h < 437 A / hottest / hot still h: "
            f"{ln2['min']:.0f} A / {ln2['below']} / {ln2['tmax']:.1f} C / {ln2['both']}",
            f"P61 works with short notice: {len(nt)}",
            f"P62 spares lines differing / missing value: {sp['diff']} / {sp['short']:.1f} k u",
            f"P63 stale emergency contacts: {len(ct)}"]
    from companion.ch51 import examples_u as eu
    hl = eu.handover_length()
    cr = eu.curtail_response()
    cn = eu.containers()
    ni = eu.night_import()
    fa2 = eu.field_audit()
    iv = eu.invoices()
    pv = eu.providers()
    py = eu.service_payment()
    fi = eu.filters()
    pr2 = eu.pump_runs()
    ro = eu.ro()
    th = eu.thermography()
    lc = eu.local_spend()
    rl = eu.redlines()
    gt = eu.gate()
    out += [f"P64 handover correlation / missed short / long: {hl['r']:+.2f} / "
            f"{hl['short']:.1f} / {hl['long']:.1f}",
            f"P65 cap instructions late at the ramp limit: {len(cr)}",
            f"P66 battery energy availability / worst share: {cn['e']:.2%} / "
            f"{cn['worst']:.0%}",
            f"P67 import hours / MWh / worst month: {ni['hours']} / {ni['mwh']:.1f} / "
            f"{ni['worst']}",
            f"P68 audit share / interval: {fa2['share']:.0%} / {fa2['lo']:.0%}-{fa2['hi']:.0%}",
            f"P69 invoice months to check / SCADA over meter: {iv['bad']} / "
            f"{iv['smin']:+.1%} to {iv['smax']:+.1%}",
            f"P70 provider costs A / B: {pv['out']['A (in use)'][2]:,.0f} / "
            f"{pv['out']['B (trial)'][2]:,.0f} u",
            f"P71 payment factor / less: {py['factor']:.3f} / {py['lost']:,.0f} u",
            f"P72 filter slope / weeks left: {fi['slope']:.1f} Pa/wk / {fi['weeks']:.0f}",
            f"P73 pump weeks missed / out of band: {pr2['missing']} / {pr2['low']}",
            f"P74 RO trigger month / cleaned: {ro['first']} / {ro['clean']}",
            f"P75 thermography repair now / plan: {len(th.get('repair now', []))} / "
            f"{len(th.get('plan repair', []))}",
            f"P76 local share / without spares: {lc['share']:.0%} / {lc['share_ex']:.0%}",
            f"P77 redlines older than 90 days: {len(rl)}",
            f"P78 entries without induction: {sum(gt.values())}"]
    from companion.ch51 import examples_v as ev
    ov = ev.overrides()
    st2 = ev.stow()
    tr = ev.trips()
    ig = ev.investigations()
    cm2 = ev.compensation()
    fd = ev.feed_outage()
    ul = ev.ups_life()
    hw = ev.hot_work()
    wl = ev.well()
    po = ev.protection_ops()
    spd = ev.speeds()
    cr2 = ev.criticality()
    ht = ev.heat()
    out += [f"P79 overrides past review / never approved: {ov['old']} / {ov['unapp']}",
            f"P80 stow hours / lost: {st2['hours']} / {st2['lost']:,.0f} MWh "
            f"({st2['share']:.2%})",
            f"P81 inverter trips / top-two share / unknown: {tr['tot']} / {tr['top2']:.0%} / "
            f"{tr['unknown']}",
            f"P82 investigations late / actions closed: {ig['late']} / {ig['done']} of "
            f"{ig['acts']}",
            f"P83 compensation claim: {cm2['claim']:,.0f} u",
            f"P84 imbalance forecast / persistence: {fd['fc']:,.0f} / {fd['pers']:,.0f} u",
            f"P85 UPS life used / years: {ul['used']:.2f} / {ul['years']:.1f}",
            f"P86 hot work without watch / final check: {hw['no_watch']} / {hw['no_final']}",
            f"P87 well slope / months to trigger: {wl['slope']:.2f} m / {wl['months']:.0f}",
            f"P88 protection dependability on faults: {po['dep']:.0%} ({po['tot']} operations)",
            f"P89 speeding passes / of the new crew: {spd['n_over']} / {spd['n_new']}",
            f"P90 most critical: {cr2[0]}, {cr2[1]}",
            f"P91 day-shift hours >= 35 C / peak hour / >= 38 C: {ht['day']} / "
            f"{ht['peak']:02d} / {ht['h38']}"]
    from companion.ch51 import examples_w as ew
    nq = ew.night_q()
    ew.monthly_report()
    wi = ew.outage_window()
    pc = ew.pcs_outage()
    bk = ew.backups()
    dr = ew.drills()
    out += [f"P92 night Q hours / energy / cost: {nq['asked']:,} / {nq['mwh']:.1f} MWh / "
            f"{nq['cost']:,.0f} u",
            f"P93 best outage day / energy: {wi['best']} / {wi['low']:.1f} MWh "
            f"(highest {wi['high']:.1f})",
            f"P94 PCS outage: power left / window hours: {pc['left']:.0f} MW / "
            f"{pc['window_h']}",
            f"P95 devices changed after their last backup: {len(bk)}",
            f"P96 drill meeting the plan / minutes gained: {dr['first_ok']} / "
            f"{dr['gain']:.0f}"]
    emit("solutions", out)


if __name__ == "__main__":
    worked()
    solutions()
