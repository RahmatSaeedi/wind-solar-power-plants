"""Chapter 53 - small worked examples (E-lines) and the numerical answers
of the exercises (P-lines), each computed here.

Run from the project root:   python -m companion.ch53.worked
Writes companion/ch53/expected/worked.txt and solutions.txt.
Do not run during a render: it rewrites the included outputs.
"""
from __future__ import annotations

import math

from companion.ch53 import examples_a as ea
from companion.ch53 import examples_b as eb
from companion.ch53 import examples_c as ec
from companion.ch53 import examples_e as ee
from companion.ch53 import examples_g as eg
from companion.ch53 import integrated as it
from companion.ch53 import lab_d
from companion.ch53.common import emit
from plantp import lifecycle as lc


def worked() -> None:
    lines = [f"E01 PV of 50 k u a year for 5 years at 7.5 %: {lc.option_pv(0, 50, 0, 0, 5, 0.075):,.1f} k u",
             f"E02 EAC of 1,000 k u over 10 years at 7.5 %: {lc.eac(1000, 10, 0.075):,.1f} k u",
             f"E03 memoryless: P(1,000 h more) at MTBF 10,000 h = {math.exp(-0.1):.3f}",
             f"E04 sinking fund for 1,000 k u in 10 years at 4 %: {lc.sinking_fund(1000, 10, 0.04):,.1f} k u",
             f"E05 0.4 %/yr degradation over 25 years: {1 - 0.004 * 25:.0%} of nameplate",
             f"E06 19,670 t at 25 t a load: {19_670 / 25:,.0f} loads",
             f"E07 1,000 t CO2e over 2,000,000 MWh: {1000 * 1e6 / 2e9:.2f} g/kWh",
             f"E08 avoided emissions 255,000 MWh x 0.55 t/MWh: {255_000 * 0.55:,.0f} t"]
    emit("worked", lines)


def solutions() -> None:
    dg = ea.degradation()
    wt = ea.wind_trend()
    ls = ea.lost()
    bm = ea.benchmark()
    sc = ea.screen()
    iv = eb.inverters()
    gb = eb.gearbox()
    rp = eb.repower()
    gr = eb.grid_changes()
    rt = eb.repower_time()
    ma = ec.materials()
    bl = ec.blades()
    pr = ec.provision()
    cu = ec.custody()
    fo = ec.foundations()
    rs = ec.restoration()
    sl = ec.second_life()
    lab_d.options()
    r7 = lab_d.result()
    r12 = lab_d.extension()
    se = lab_d.sensitivity()
    lab_d.evidence()
    ll = ee.long_lead()
    cl = ee.climate()
    ee.continuity()
    ins = ee.insurance()
    ee.feedback()
    mx = ee.lifecycle_matrix()
    iv2 = ee.inspect_value()
    cm = eg.commitments()
    wf = eg.workforce()
    tr = eg.traffic()
    eg.disclosure()
    re_ = eg.retention()
    ac = eg.access()
    fp = eg.footprint()
    av = eg.avoided()
    hb = it.by_hand()
    rv = it.review()
    out = [f"P01 PV degradation: {dg['rate']:.2f} %/yr (slope {dg['b']:+.3f} +/- {dg['h']:.3f} points)",
           f"P02 wind availability trend years 4-9 / 10-18: {wt['early']:+.2f} / {wt['late']:+.2f}",
           f"P03 lost energy year 18 / largest cause: {ls['tot']:,.0f} MWh / {ls['big']}",
           f"P04 gap to peers wind / PV: {bm['gap_w']:.1f} / {bm['gap_p']:.1f} points",
           f"P05 best opportunity NPV: {max(sc.values()):,.0f} k u",
           f"P06 inverter growth slope: {iv['beta']:.2f}",
           f"P07 gearbox median left / survive to 25 / failures: {gb['med']:,.0f} h / "
           f"{gb['r7']:.0%} / {gb['fails']:.1f}",
           f"P08 repowering gain / spilled: {rp['gain'] / 1000:.1f} / {rp['spilled'] / 1000:.1f} GWh",
           f"P09 grid requirement gaps: {gr['gaps']}",
           f"P10 repowering months before stop / down: {rt['before']:.0f} / {rt['down']:.1f}",
           f"P11 materials total / recycled: {ma['total']:,.0f} t / {ma['recycled'] / ma['total']:.0%}",
           f"P12 blade composite: {bl['t']:,.0f} t",
           f"P13 provision at year 25 / fund from 1 / from 18: {pr['net_end']:,.0f} / {pr['start']:,.0f} / "
           f"{pr['late']:,.0f} k u",
           f"P14 custody loads to check: {cu['bad']}",
           f"P15 concrete top 1 m / full: {fo['top 1 m (teaching permit case)'][0]:,.0f} / "
           f"{fo['full removal'][0]:,.0f} t",
           f"P16 plots meeting the cover target: {len(rs['met'])}",
           f"P17 modules fit for second life: {sl['share']:.0%}",
           f"P18 decision 7 yr mean A / B / C: {r7['A']['mean']:,.0f} / {r7['B']['mean']:,.0f} / "
           f"{r7['C']['mean']:,.0f} k u",
           f"P19 decision 12 yr mean A / B / C: {r12['A']['mean']:,.0f} / {r12['B']['mean']:,.0f} / "
           f"{r12['C']['mean']:,.0f} k u",
           f"P20 cheapest across sensitivities: {', '.join(sorted(se['winners']))}",
           f"P21 PCS failure during its lead time: {ll['BESS PCS'][2]:.0%}",
           f"P22 hours >= 40 C now / warmer: {cl['now']} / {cl['later']}",
           f"P23 insurance claims incomplete: {ins['incomplete']}",
           f"P24 decision for SCADA and PPC: {mx['SCADA and PPC']}",
           f"P25 blind / inspect-first cost: {iv2['blind']:.0f} / {iv2['inspect']:.0f} k u",
           f"P26 closure commitments without evidence: {cm['no_ev']}",
           f"P27 decommissioning peak jobs: {wf['peak']}",
           f"P28 loads / a day: {tr['loads']:,.0f} / {tr['per_day']:.1f}",
           f"P29 record sets not migrated: {len(re_['not_migrated'])}",
           f"P30 credentials to remove: {ac['tot']}",
           f"P31 footprint medians: " + ", ".join(f"{v[0]:.2f}" for v in fp.values()) + " g/kWh",
           f"P32 avoided emissions low / high: {min(av.values()):,.0f} / {max(av.values()):,.0f} t",
           f"P33 hand checks: {hb['med']:,.0f} h, {hb['pv']:,.0f} k u, {hb['fund']:,.0f} k u",
           f"P34 lifecycle review: {rv['ok']} of {rv['total']}"]
    from companion.ch53 import examples_s as es
    cu2 = es.curtailment()
    sa = es.soiling_vs_ageing()
    up = es.inverter_upgrade()
    ba = es.battery()
    pe = es.permits()
    hz = es.hazardous()
    sc2 = es.scrap()
    ea2 = es.eac_options()
    bo = es.inspect_first()
    gv = es.grievances()
    gz = es.grazing()
    wa = es.warranties()
    di = es.disposal()
    bd = es.boundaries()
    cr = es.credits()
    out += [f"P35 curtailment slope / year 25: {cu2['slope']:+.0f} MWh/yr / {cu2['y25']:,.0f} MWh",
            f"P36 soiling before a wash / after-wash PR: {sa['soil']:.1f} / {sa['after']:.1f} %",
            f"P37 inverter upgrade value / payback / NPV7: {up['yearly']:,.0f} k u / "
            f"{up['payback']:.1f} yr / {up['npv7']:+,.0f} k u",
            f"P38 battery augmentation / cost / value: {ba['aug']:.1f} MWh / {ba['cost']:,.0f} / "
            f"{ba['value']:,.0f} k u",
            f"P39 longest approval: {pe['crit']} ({pe['months']} months)",
            f"P40 SF6 inventory: {hz['sf6']:.0f} kg",
            f"P41 salvage low / high: {sc2['low']:,.0f} / {sc2['high']:,.0f} k u",
            f"P42 EAC keep / new: {ea2['keep']:,.0f} / {ea2['new']:,.0f} k u",
            f"P43 gearbox blind / with borescope: {bo['blind']:,.0f} / {bo['informed']:,.0f} k u",
            f"P44 expected decommissioning grievances: {gv['exp']:.0f}",
            f"P45 grazing land / value: {gz['ha']:.0f} ha / {gz['income']:.1f} k u",
            f"P46 warranties alive at a sale: {wa['live']}",
            f"P47 record sets due for disposal: {di['n']}",
            f"P48 construction footprint over 25 / 30 yr: {bd['a25']:.1f} / {bd['a30']:.1f} g/kWh",
            f"P49 avoided-burden credit: {cr['avoided']:,.0f} t CO2e"]
    from companion.ch53 import examples_t as et
    ba2 = et.bad_actors()
    tw = et.tower_fatigue()
    ff = et.foundation_fit()
    pa = et.partial()
    ca = et.campaign()
    br = et.battery_recycle()
    ru = et.spares_rundown()
    py = et.payments()
    ad = et.access_days()
    mg = et.migration()
    tp = et.transport()
    rk = et.ranking()
    out += [f"P50 share of the three worst turbines: {ba2['top3']:.0%}",
            f"P51 tower damage used / years left: {tw['used']:.2f} / {tw['left']:.1f}",
            f"P52 foundation utilisation with the new rotor: {ff['util']:.0%}",
            f"P53 k u per GWh/yr, all 12 / worst 6: {pa['full']:,.0f} / {pa['half']:,.0f}",
            f"P54 crane days for the campaign: {ca['days']:.0f}",
            f"P55 battery end-of-life net cost: {br['net']:+,.0f} k u",
            f"P56 gearbox kits short by: {-ru['gearbox kits']:.1f}",
            f"P57 lease to the end: {py['lease']:,.0f} k u",
            f"P58 herders' track closed: {ad['days']:.0f} days",
            f"P59 migration error share / interval: {mg['p']:.1%} / {mg['lo']:.1%}-{mg['hi']:.1%}",
            f"P60 transport footprint: {tp['co2']:,.0f} t CO2e",
            f"P61 repowering footprint at 80 % energy: {rk['low']:.2f} g/kWh"]
    from companion.ch53 import examples_u as eu
    ex = eu.extend_or_retire()
    eu.order()
    rd = eu.residual()
    isu = eu.insurance()
    rg = eu.register()
    ck = eu.checklist()
    fu = eu.functional_unit()
    out += [f"P67 rankings per year and per kWh agree: {fu['same']}",f"P62 extension NPV today: {ex['npv']:+,.0f} k u",
            f"P63 share of a new gearbox's life used to year 25: {rd['share']:.0%}",
            f"P64 premium less expected recovery: {isu['net']:,.0f} k u",
            f"P65 decisions in the register: {len(rg)}",
            f"P66 retirement evidence at the start: {ck['done']} of {ck['total']}"]
    emit("solutions", out)


if __name__ == "__main__":
    worked()
    solutions()
