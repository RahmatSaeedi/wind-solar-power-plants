"""Chapter 48 - small worked examples (E-lines) and the numerical answers
of the exercises (P-lines), each computed here.

Run from the project root:   python -m companion.ch48.worked
Writes companion/ch48/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

import math

from companion.ch48 import examples_a as ea
from companion.ch48 import examples_b as eb
from companion.ch48 import examples_c as ec
from companion.ch48 import examples_s as es
from companion.ch48 import integrated as it
from companion.ch48 import lab_d
from companion.ch48.common import emit
from plantp import hwmfg as hw


def worked() -> None:
    lines = [f"E01 4-20 mA for 600 W/m2 on 0-1600: {4 + 16 * 600 / 1600:.2f} mA",
             f"E02 RSS of 15, 10, 10 and 4 W/m2: {math.sqrt(15**2 + 10**2 + 10**2 + 4**2):.1f}",
             f"E03 chain error of 0.2, 0.2 and 0.5 %: RSS "
             f"{hw.chain_error(0.2, 0.2, 0.5)[0]:.2f} %, worst {hw.chain_error(0.2, 0.2, 0.5)[1]:.1f} %",
             f"E04 expected loss of 2.0 km, 2 connectors, 4 splices: "
             f"{2.0 * 0.35 + 2 * 0.5 + 4 * 0.1:.2f} dB",
             f"E05 int16 with scale 0.01 tops at: {32767 * 0.01:.2f}",
             f"E06 sample for 95 % and 2 % defective: "
             f"{math.ceil(math.log(0.05) / math.log(0.98))}",
             f"E07 offset of a clock 15 ms late against a 2 ms limit: "
             f"{'beyond' if 15 > 2 else 'ok'}",
             f"E08 spare share of 24 ports with 22 used: {(24 - 22) / 24:.0%}"]
    emit("worked", lines)


def solutions() -> None:
    bu = ea.budgets()
    ce = ea.certs()
    mt = ea.metering()
    cb = ea.cabinets()
    bo = ea.bonding()
    po = eb.ports()
    fb = eb.fibre()
    cu = eb.copper()
    pw = eb.power()
    fw = ec.firmware()
    bk = ec.backups()
    ck = ec.clocks()
    rm = ec.regmap()
    fo = ec.failover()
    tg = lab_d.tags()
    cn = lab_d.connections()
    df = lab_d.dataflow()
    hb = it.by_hand()
    ip = es.ip()
    em = es.emc()
    sg = es.surge()
    iv = es.interval()
    mo = es.money()
    sp = es.spare_ports()
    cr = es.cores()
    ps = es.psu()
    lp = es.loops()
    tr = es.trace()
    out = [f"P01 RSS of pyranometer / transducer at 45 C, 2 years: "
           f"{bu['pyranometer']['rss']:.1f} W/m2 / {bu['power transducer']['rss']:.2f} MW",
           f"P02 certificates with findings: {', '.join(ce)}",
           f"P03 metering chain RSS / worst: {mt['rss']:.2f} / {mt['worst']:.2f} %",
           f"P04 meter loads outside the class: {', '.join(map(str, mt['bad']))} %",
           f"P05 cabinets with devices too hot: {', '.join(cb)}",
           f"P06 bonds over the limit / shields against the rule: "
           f"{', '.join(bo['high'])} / {len(bo['wrong'])}",
           f"P07 SW-T05 field changes / extra ports: {len(po['changed'])} / "
           f"{len(po['extra'])}",
           f"P08 fibre links not ok: "
           + ", ".join(f"{k} {v[2]}" for k, v in fb.items() if v[2] != "ok"),
           f"P09 copper links failing: {', '.join(cu['bad'])}",
           f"P10 cabinets on one power source: {', '.join(pw['bad'])}",
           f"P11 firmware findings: {len(fw)}",
           f"P12 stale backups: {', '.join(d for d, *_ in bk)}",
           f"P13 clocks beyond the limit: {', '.join(ck['beyond'])}",
           f"P14 register-map findings: {len(rm)}",
           f"P15 failover failed / not done: {', '.join(fo['bad'])} / "
           f"{', '.join(fo['missing'])}",
           f"P16 tag problems: {len(tg)}",
           f"P17 connection changes at the core switch: {len(cn['changed'])}",
           f"P18 worst-case sensor-to-historian delay: {df['total']:.0f} s",
           f"P19 hand checks: {hb['rss']:.1f} W/m2, {hb['ma']:.2f} mA, {hb['fo']:.2f} dB",
           f"P20 enclosures rated too low: {', '.join(ip)}",
           f"P21 devices short on EMC: {', '.join(em)}",
           f"P22 outdoor lines without surge protection: {len(sg)}",
           f"P23 years to 2.5 % for the pyranometer: {iv['years']:.1f}",
           f"P24 metering error worth a year: {mo['ku']:.0f} k u",
           f"P25 switches below the spare-port rule: {', '.join(sp)}",
           f"P26 fibre cable with a core outside the plan: "
           + ", ".join(c for c, (d, _) in cr.items() if d),
           f"P27 cabinets not N+1: {', '.join(ps)}",
           f"P28 loop checks done / points: {lp['done']} / {lp['tot']}",
           f"P29 first wrong stage of the traced value: {tr['first']}"]
    from companion.ch48 import examples_t as et
    from companion.ch48 import examples_u as eu
    an = et.anemometer()
    cm = et.check_meter()
    iso = et.isolation()
    bd = et.bend()
    pe = et.poe()
    hd = et.hardening()
    nt = et.ntp()
    al = et.alarm_tests()
    nm = et.names()
    vw = et.views()
    ro = eu.rotation()
    sg2 = eu.segregation()
    ch = eu.chains()
    pr = eu.pr_bias()
    hr = eu.cabinet_hours()
    dt = eu.detection()
    out += [f"P30 anemometer bias and energy effect: {an['bias']:.1%}, {an['energy']:.1%}",
            f"P31 meter drift significant / beyond 0.3 %: day {cm['seen']} / day "
            f"{cm['first']}",
            f"P32 loops crossing without an isolator: {', '.join(iso)}",
            f"P33 bend found at: {bd['km'][0]:.2f} km",
            f"P34 PoE load against 60 W: {pe['tot']:.1f} W",
            f"P35 hardening findings / time-source findings: {len(hd)} / {len(nt)}",
            f"P36 critical alarms untested: {al['crit_left']}",
            f"P37 bad point names: {len(nm)}",
            f"P38 devices in one view only: {', '.join(vw['only_p'] + vw['only_l'])}",
            f"P39 spares for the rotation: {ro['spares']}",
            f"P40 trays breaking segregation: {', '.join(sorted({t for t, *_ in sg2}))}",
            f"P41 crossed patch chains: {len(ch)}",
            f"P42 reported PR with a +2 % sensor: {pr[0.02]:.3f}",
            f"P43 summer hours above 50 C / above 55 C: {hr['over']} / {hr['hard']}",
            f"P44 mean days unseen, daily / quarterly comparison: {dt[1]:.1f} / "
            f"{dt[90]:.0f}"]
    from companion.ch48 import examples_v as ev
    from companion.ch48 import examples_w as ew
    al2 = ev.alignment()
    an2 = ev.antenna()
    hs = ev.hashes()
    df2 = ev.config_diff()
    co = ev.correction()
    io = ew.io_spares()
    rc = ew.reconcile()
    st = ew.staging()
    ch2 = ew.cal_chain()
    li = ew.licence()
    out += [f"P45 alignment error of a 2 deg tilt at 50 / 70 deg: {al2[50] * 100:+.1f} / "
            f"{al2[70] * 100:+.1f} %",
            f"P46 antenna margin, standard / low-loss cable: {an2['left'] - 10:.1f} / "
            f"{an2['left2'] - 10:.1f} dB",
            f"P47 firmware files differing from the published hash: {', '.join(hs)}",
            f"P48 unrecorded configuration lines: {len(df2)}",
            f"P49 days of wind speed with a wrong unit: {co['days']}",
            f"P50 card types below the spare rule: {', '.join(io)}",
            f"P51 reconciliation gap / chain uncertainty: {rc['gap']:.2f} / "
            f"{rc['u']:.2f} GWh",
            f"P52 devices never staged: {', '.join(st['never'])}",
            f"P53 calibration expanded uncertainty / ratio: {ch2['U']:.2f} % / "
            f"{ch2['tur']:.1f}",
            f"P54 tags after the extension / short of the licence: {li['later']:,} / "
            f"{li['short']:,}"]
    from companion.ch48 import examples_x as ex
    lb = ex.loop_budget()
    gu = ex.gust()
    pf = ex.profile()
    cp = ex.compat()
    cn2 = ex.connectors()
    lab = ex.labels()
    out += [f"P55 loops short of 12 V with the isolator: {', '.join(lb['bad'])} "
            f"({lb['out']['L-104'][0]:.1f} V)",
            f"P56 gust events / peak / highest one-minute mean: {gu['events']} / "
            f"{gu['peak']:.1f} / {gu['mean_max']:.1f} m/s",
            f"P57 profile gap: {pf['gap']:.1f} MWh",
            f"P58 untested firmware pairs: {', '.join(d for d, _ in cp)}",
            f"P59 links failing, as received / inspected: "
            f"{cn2['mate as received']:.2%} / {cn2['inspect, clean, mate']:.2%}",
            f"P60 one-interval shift: value / energy into the next day: "
            f"{lab['diff']:+,.0f} u / {lab['moved']:.1f} MWh"]
    from companion.ch48 import examples_y as ey
    af = ey.as_found()
    se = ey.seals()
    ctr = ey.ct_reversed()
    dw = ey.condensation()
    inr = ey.inrush()
    wv = ey.wan_video()
    out += [f"P61 data flagged after the as-found: from {af['since']}, {af['days']} days, "
            f"mean {af['mean']:.2f} %",
            f"P62 seal findings: {', '.join(se)}",
            f"P63 export read with one reversed CT: {ctr['bad']:.2f} of {ctr['ok']:.2f} MW",
            f"P64 dew point / hours below it, unheated / heated: {dw['td']:.1f} C / "
            f"{dw['wet']:.1f} / {dw['wet_h']:.1f} h",
            f"P65 breakers over the maker's inrush table: {', '.join(inr)}",
            f"P66 SCADA wait with one camera, no priority: "
            f"{wv['one camera, no priority'][1] * 1000:.1f} ms"]
    from companion.ch48 import examples_z as ez
    ss = ez.stow_sensors()
    fc = ez.fat_coverage()
    out += [f"P67 missed-stow chance, one / two sensors: {ss['pfd1']:.4f} / "
            f"{ss['pfd2']:.4f}",
            f"P68 points left for the site / hours: {fc['left']} / {fc['hours']:.0f}"]
    emit("solutions", out)


if __name__ == "__main__":
    worked()
    solutions()
