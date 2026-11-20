"""Chapter 43 - small worked examples (E-lines) and the numerical answers
of the exercises (P-lines), each computed here.

Run from the project root:   python -m companion.ch43.worked
Writes companion/ch43/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

import math

from companion.ch43 import examples_a as ea
from companion.ch43 import examples_b as eb
from companion.ch43 import examples_c as ec
from companion.ch43 import examples_e as ee
from companion.ch43 import integrated as it
from companion.ch43 import lab_d
from companion.ch43.common import emit
from plantp import transformer as tr
from plantp import xfmrdesign as xd


def worked() -> None:
    lines = [f"E01 volts a turn at 1.7 T on 0.25 m2: "
             f"{tr.volts_per_turn(1.7, 0.25):.1f} V",
             f"E02 net core area for 110 V at 1.7 T: "
             f"{xd.core_section(110.0, 1.7)['a_net']:.4f} m2",
             f"E03 fill of a 7-step core: {xd.stepped_fill(7)[0]:.3f}",
             f"E04 HV phase current of 63 MVA at 132 kV: "
             f"{63e6 / (math.sqrt(3) * 132e3):.1f} A",
             f"E05 resistance 0.5293 ohm at 22 C, at 75 C: "
             f"{xd.r_to_ref(0.5293, 22.0):.4f} ohm",
             f"E06 no-load loss 43.5 kW, rms 3 % above mean: "
             f"{xd.waveform_corrected(43.5, 1.03, 1.0):.1f} kW",
             f"E07 water saturation of oil at 20 C: "
             f"{xd.water_solubility_ppm(20.0):.0f} ppm",
             f"E08 sound power, 68 dB(A) over 84 m2: "
             f"{xd.sound_power_db(68.0, 84.0):.1f} dB(A)",
             f"E09 free buckling, 10 mm on a 0.753 m copper winding: "
             f"{xd.buckling_free_mpa(110e9, 0.010, 0.753):.0f} MPa",
             f"E10 field in 66 mm oil + 9 mm board at 100 kV: "
             f"{xd.field_in_gap(100.0, 66.0, 9.0)[0]:.2f} kV/mm"]
    emit("worked", lines)


def solutions() -> None:
    fl = ea.flux()
    tu = ea.turns()
    cu = ea.currents()
    im = ea.impedance()
    lo = ea.losses()
    gp = ea.gap()
    fo = ea.forces()
    st = eb.steps()
    sl = eb.steels()
    de = eb.density()
    sd = eb.strands()
    ma = eb.mass()
    pv = eb.pv_unit()
    out = [f"P01 over-excited flux at 1.7 T design: {fl[1.70]['bo']:.2f} T",
           f"P02 no-load loss at 1.5 / 1.8 T: {fl[1.50]['p0']:.1f} / "
           f"{fl[1.80]['p0']:.1f} kW",
           f"P03 volts a turn and HV ratio error: {tu['e_t']:.1f} V, "
           f"{tu['err0']:+.2f} %",
           f"P04 worst tap ratio error, 8 / 9 turns a step: {tu['worst8']:+.2f} / "
           f"{tu['worst9']:+.2f} %",
           f"P05 HV and LV phase currents: {cu['i_hv']:.1f} / {cu['i_lv']:.1f} A",
           f"P06 conductor areas at 3.5 A/mm2: {cu['a_hv']:.1f} / {cu['a_lv']:.1f} mm2",
           f"P07 impedance from the geometry: {im['ux']:.2f} %",
           f"P08 impedance change per mm of gap: {im['per_mm']:.3f} %",
           f"P09 I2R and load loss at 75 C: {lo['i2r']:.0f} / {lo['pk']:.0f} kW",
           f"P10 efficiency at 0.5 pu, pf 0.95: {lo['eff'][0.5]:.3%}",
           f"P11 oil margin all-oil / barriers: {gp['m_all']:.2f} / {gp['m_bar']:.2f}",
           f"P12 HV tension and LV compression: {fo['s_hv']:.0f} / {fo['s_lv']:.0f} MPa",
           f"P13 free / supported buckling: {fo['free']:.0f} / {fo['held']:,.0f} MPa",
           f"P14 fill of 9 steps: {st[9]:.3f}",
           f"P15 no-load loss in high-permeability steel: "
           f"{sl['high-permeability GO']:.1f} kW",
           f"P16 two-term optimum current density: {de['j_opt']:.1f} A/mm2",
           f"P17 eddy share of 2.5 mm strands (axial): {sd[2.5]:.2%}",
           f"P18 shipping mass: {ma['ship']:.0f} t",
           f"P19 PV unit volts a turn with 16 LV turns: {pv[16]:.2f} V"]
    out += more()
    emit("solutions", out)


def more() -> list[str]:
    jn = ec.joints()
    wa = ec.water()
    ra = ec.ratio()
    co = ec.corrected()
    hr = ec.heatrun()
    so = ec.sound()
    ga = ec.gases()
    trc = lab_d.trace()
    gaps = lab_d.audit(lab_d.src.TRAVELER)
    rv = lab_d.review()
    nop = lab_d.decisions()
    fa = ee.fans()
    sp = ee.spill()
    dt = ee.data()
    bs = ee.baselines()
    hb = it.by_hand()
    return [f"P20 no-load current, step-lap / mitred: "
            f"{jn['step-lap']:.2f} / {jn['mitred, single lap']:.2f} %",
            f"P21 relative saturation of 18 ppm at 20 C: {wa[20.0]:.0%}",
            f"P22 failing tap and turns implied: {ra['bad']:+.2f} %, "
            f"{ra['turns']:.1f}",
            f"P23 corrected P0 and Pk at 75 C: {co['p0']:.1f} / {co['pk75']:.0f} kW",
            f"P24 winding rise, extrapolated / 2-minute: {hr['rise']:.1f} / "
            f"{hr['first']:.1f} K",
            f"P25 sound power: {so['lw']:.1f} dB(A)",
            f"P26 acetylene rise in the heat run: {ga['C2H2']:+.1f} ppm",
            f"P27 trace rows done / open: {trc.get('done', 0)} / {trc.get('open', 0)}",
            f"P28 traveler gaps: {len(gaps)}",
            f"P29 test failures and deductions: {rv['fails']}, {rv['ded']:.1f} k u",
            f"P30 open decisions: {nop}",
            f"P31 fan hours and starts: {fa['hours']}, {fa['starts']}",
            f"P32 differential spill at -10 % tap, 1 pu: {sp[-10.0]:.3f} pu",
            f"P33 maker data partial: {dt.get('partial', 0)}",
            f"P34 baselines available: {bs['have']} of {bs['total']}",
            f"P35 PV unit HV turns and peak flux: {hb['n_hv']}, "
            f"{hb['phi'] * 1000:.1f} mWb",
            f"P36 PV unit efficiency at 0.6 load: {hb['eff']:.2%}"] + rounds()


def rounds() -> list[str]:
    from companion.ch43 import examples_s as es
    from companion.ch43 import examples_t as et
    tf = es.tap_flux()
    vo = es.void()
    cl = es.clamping()
    jo = es.joint()
    tb = es.testbay()
    sh = es.shunts()
    bu = es.bushing()
    br = et.burr()
    la = et.lamination()
    di = et.disc_build()
    se = et.settle()
    bg = et.bridge()
    li = et.rating_limit()
    sc = et.schedule()
    return [f"P37 flux energised from 132 kV at the -10 % tap: {tf[-10.0]:.2f} T",
            f"P38 void field and discharge in a 0.2 mm void: "
            f"{4.4 * 4.0:.1f} kV/mm, {'yes' if vo[0.2][1] else 'no'}",
            f"P39 clamping left after 2 % shrinkage: {cl[2.0]:.0%}",
            f"P40 poor joint heat and phase resistance change: "
            f"{jo['p_bad']:.0f} W, {jo['share']:.3%}",
            f"P41 test supply and heat-run current: {tb['s_test']:.2f} MVA, "
            f"{tb['i_ratio']:.3f} x",
            f"P42 shunts: kW saved and value: {sh['saved']:.0f}, {sh['value']:.0f} k u",
            f"P43 bushing field ungraded / graded: {bu['e_plain']:.2f} / "
            f"{bu['e_graded']:.2f} kV/mm",
            f"P44 no-load loss at 10 / 40 um burr: {br[10.0]:.1f} / {br[40.0]:.1f} kW",
            f"P45 classical eddy loss, 0.27 mm sheet: {la[0.27]:.3f} W/kg",
            f"P46 HV radial build and discs: {di['build'] * 1000:.0f} mm, {di['discs']}",
            f"P47 resistance reading to 0.1 %: {se['t_01'] / 60:.1f} min",
            f"P48 TUR and guard band: {bg['tur']:.0f}, {bg['guard']:.2f} %",
            f"P49 rating limit for 65 K: {li['mva']:.1f} MVA; hours over: {li['over']}",
            f"P50 factory weeks and winding float: {sc['end']:.0f}, "
            f"{sc['float_w']:.0f}"] + rounds2()


def rounds2() -> list[str]:
    from companion.ch43 import examples_u as eu
    from companion.ch43 import examples_v as ev
    pa = eu.paper()
    al = eu.aluminium()
    th = eu.thermal_sc()
    dc = eu.dc_injection()
    am = eu.hot_ambient()
    ce = eu.core_earth()
    ol = ev.oltc()
    bu = ev.bushings()
    pf = ev.pfmea()
    cr = ev.critical()
    nf = ev.night_fans()
    dr = ev.drying()
    return [f"P51 life used at 130 % load, kraft / upgraded: "
            f"{pa['kraft (non-upgraded)']:.1f} / {pa['thermally upgraded']:.1f} days",
            f"P52 aluminium windings mass and conductor saving: "
            f"{al['al_kg'] / 1000:.1f} t, {al['saving']:.0f} k u",
            f"P53 winding rise in a 2 s fault: {th['dt']:.0f} K",
            f"P54 DC ampere-turns against magnetising: {dc['at_dc']:.0f} / "
            f"{dc['at_mag']:.0f}",
            f"P55 PV unit at 45 C: {am['k']:.3f} pu, {am['equiv']:.1f} MVA at 40 C",
            f"P56 core earthed twice: {ce['i']:,.0f} A, {ce['p'] / 1000:.1f} kW",
            f"P57 OLTC step voltage and step capacity: {ol['step_v']:.0f} V, "
            f"{ol['cap']:.0f} kVA",
            f"P58 bushing ratings HV / LV: {bu['hv']} / {bu['lv']} A",
            f"P59 first process failure mode: {pf[0]}",
            f"P60 critical characteristics: {cr}",
            f"P61 fan hours and those at night: {nf['hours']}, {nf['night']}",
            f"P62 drying end point and water removed: hour {dr['below']:.0f}, "
            f"{dr['water']:.0f} L"] + rounds3()


def rounds3() -> list[str]:
    from companion.ch43 import examples_w as ew
    from companion.ch43 import examples_x as ex
    fl = ew.oil_flow()
    sq = ew.sequence()
    td = ew.tan_delta()
    bd = ew.breakdown()
    wi = ew.witness()
    tq = ew.queries()
    cl = ex.closure()
    pd = ex.pd()
    de = ex.delta()
    ca = ex.categories()
    pv = ex.pv_dossier()
    return [f"P63 natural oil flow at ONAN: {fl['m']:.1f} kg/s, {fl['q']:.1f} L/s",
            f"P64 test hours and working days: {sq['total']:.0f}, {sq['days']}",
            f"P65 tan delta at 20 C of the two readings: "
            f"{td['ref'][0]:.4f} / {td['ref'][1]:.4f}",
            f"P66 breakdown mean and CV, sample B: {bd['B'][0]:.1f} kV, "
            f"{bd['B'][1]:.0%}",
            f"P67 buyer's visits: {wi['trips']}",
            f"P68 technical queries open: {tq.get('open', 0)} of "
            f"{sum(tq.values())}",
            f"P69 evaluated cost as tested minus at award: "
            f"{cl['built'] - cl['bid']:.1f} k u",
            f"P70 PD charge and signal to background: {pd['q']:.0f} pC, "
            f"{pd['sn']:.1f}",
            f"P71 line-reading spread for a 2 % phase fault: {de['spread']:.2%}",
            f"P72 findings on hold: {ca.get('hold', 0)}",
            f"P73 PV unit deduction: {pv['ded']:.2f} k u"] + rounds4()


def rounds4() -> list[str]:
    from companion.ch43 import examples_y as ey
    from companion.ch43 import examples_z as ez
    sc = ey.sc_decision()
    br = ey.bracing()
    mo = ey.first_month()
    pl = ey.nameplate()
    nl = ez.noload()
    ll = ez.loadloss()
    lt = ez.late()
    ac = ez.actions()
    return [f"P74 expected cost: no proof / review / test: {sc['no proof']:.0f} / "
            f"{sc['design review']:.0f} / {sc['test on this unit']:.0f} k u",
            f"P75 bracing force along the road: {br['along']:.2f} MN",
            f"P76 gas trends in the first month: H2 {mo['h2']:+.1f}, "
            f"C2H4 {mo['c2h4']:+.1f} ppm",
            f"P77 rating-plate items that differ: {pl['bad']}",
            f"P78 no-load exponents below / above rated: {nl['n_low']:.1f} / "
            f"{nl['n_high']:.1f}",
            f"P79 load loss ratio full / half current: {ll['ratio']:.2f}",
            f"P80 energy lost with T1 three weeks late: {lt['mwh']:,.0f} MWh, "
            f"{lt['k_u']:.0f} k u",
            f"P81 corrective actions before T2: {ac}"] + rounds5()


def rounds5() -> list[str]:
    from companion.ch43 import examples_m as em
    ne = em.neutral()
    cr = em.creep()
    re_ = em.remanence()
    au = em.aux()
    pb = em.pv_bay()
    return [f"P82 132 kV earth fault with / without the neutral: "
            f"{ne['i_with']:.2f} / {ne['i_without']:.2f} kA",
            f"    current in the neutral {ne['i_n']:.2f} kA",
            f"P83 straight gap and creep path at 100 kV: {cr['gap']:.0f} / "
            f"{cr['path']:.0f} mm",
            f"P84 inrush peak after DC tests / demagnetised: "
            f"{re_['after the DC tests']:,.0f} / {re_['demagnetised']:,.0f} A",
            f"P85 auxiliary peak and energy: {au['peak']:.1f} kW, {au['mwh']:.1f} MWh",
            f"P86 bay days for ten PV units: {pb['days']:.1f}"] + rounds6()


def rounds6() -> list[str]:
    from companion.ch43 import examples_n as en
    hs = en.hotspot_factor()
    em = en.energy_model()
    we = en.weighed()
    return [f"P87 hot-spot factor from the sensors: {hs['h']:.2f}",
            f"P88 extra loss energy of T1 a year: {em['mwh']:.1f} MWh",
            f"P89 weighed shipping mass and margin: {we['ship']:.1f} t, "
            f"{we['margin']:.1f} t"]


if __name__ == "__main__":
    worked()
    solutions()
