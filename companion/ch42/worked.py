"""Chapter 42 - small worked examples (E-lines) and the numerical answers
of the exercises (P-lines), each computed here.

Run from the project root:   python -m companion.ch42.worked
Writes companion/ch42/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

import math

from companion.ch42 import examples_a as ea
from companion.ch42 import examples_b as eb
from companion.ch42 import examples_c as ec
from companion.ch42 import examples_e as ee
from companion.ch42 import lab_d
from companion.ch42.common import emit
from plantp import materials as mt
from plantp import turbinemfg as tm


def worked() -> None:
    vf = tm.fibre_volume(0.70, 2.55, 1.15)
    e, _ = mt.rule_of_mixtures(72.0, 3.2, vf)
    lines = [f"E01 V_f of a 70 % fibre-mass glass laminate: {vf:.3f}",
             f"E02 its modulus along the fibres: {e:.1f} GPa",
             f"E03 insert pull at 15.4 MN m (96 on 3.2 m): "
             f"{tm.insert_tension(15.4e6, 96, 3.2) / 1e3:.0f} kN",
             f"E04 unbalance of 484.0, 486.2, 482.9 t m: "
             f"{tm.set_unbalance([484.0, 486.2, 482.9]):.2f} t m",
             f"E05 POD of a 40 mm disbond (a50 20, beta 0.45): "
             f"{tm.pod(40, 20, 0.45)[0]:.0%}",
             f"E06 grid power, back to back at 5 MW, eta 0.98: "
             f"{tm.back_to_back_power(5000, 0.98):.0f} kW",
             f"E07 shrink rise, 0.5 mm on 0.9 m: "
             f"{tm.shrink_delta_t(0.5e-3, 0.9):.0f} K",
             f"E08 insulation life 10 K over the design point: "
             f"{tm.halving_life(130, 120, 20):.0f} years",
             f"E09 filter beta 200 removes: {tm.filter_removal(200):.1%}",
             f"E10 eccentricity for grade 2.5 at 1155 rpm: "
             f"{2.5 / (1155 * 2 * math.pi / 60) * 1000:.1f} um"]
    emit("worked", lines)


def solutions() -> None:
    tr = ea.tree()
    rj = ea.root_joint()
    dt = ea.drivetrain()
    al = ea.allocation()
    rp = ea.replacements()
    en = ea.envelope()
    ff = eb.fibre_fraction()
    vo = eb.voids()
    ca = eb.caps()
    cu = eb.cure()
    po = eb.bondline()
    ma = eb.matching()
    cs = eb.casting()
    sh = eb.shrink()
    hb = eb.hub_route()
    out = [f"P01 mass above the foundation: {tr['above']:.0f} t",
           f"P02 extreme insert pull and opening margin: "
           f"{rj['extreme (2 x)']['pull'] / 1e3:.0f} kN, "
           f"x{rj['extreme (2 x)']['margin']:.1f}",
           f"P03 drivetrain chain and heat at rated: {dt['eta']:.3f}, "
           f"{dt['heat']:.0f} kW",
           f"P04 downtime and availability: {al['hours']:.0f} h, "
           f"{al['avail']:.2%}",
           f"P05 crane campaigns in 25 years: {rp['total']:.0f}",
           f"P06 hottest air and its density: {en['t_max']:.1f} C, "
           f"{en['rho_hot']:.3f} kg/m3",
           f"P07 V_f needed for 45 GPa: {ff['vf_need']:.3f}",
           f"P08 worst coupon void content: {vo['worst']:.1%}",
           f"P09 carbon caps for equal EI: {ca['m_carbon']:.1f} t, cost x"
           f"{ca['c_ratio']:.1f}",
           f"P10 cure and Tg of sample S9: {cu['s9'][0]:.3f}, "
           f"{cu['s9'][1]:.1f} C",
           f"P11 a90 of the bond-line scan: {po['a90']:.0f} mm",
           f"P12 set unbalance, sorted / random: {ma['sorted']:.2f} / "
           f"{ma['random']:.2f} t m",
           f"P13 casting indications over limits: {cs['rejected']} of {cs['n']}",
           f"P14 shrink-fit temperature rise: {sh['dt']:.0f} K",
           f"P15 cast/fabricated hub break-even: {hb['be']:.0f} hubs"]
    out += more()
    emit("solutions", out)


def more() -> list[str]:
    b2 = ec.back_to_back()
    fi = ec.filters()
    co = ec.cooling()
    il = ec.insulation_life()
    ba = ec.balance()
    alg = ec.alignment()
    we = ec.weld_fatigue()
    ya = ec.yaw_brakes()
    pi = ec.pi_index()
    run = lab_d.runin()
    plan = lab_d.quality_plan()
    ncr = lab_d.escalation()
    ti = ee.tiers()
    fa = ee.first_article()
    tq = ee.torque()
    dm = ee.damage()
    wi = ee.windows()
    sd = ee.serial_defect()
    return [f"P16 grid power back to back at eta 0.97: {b2[0.97]:.0f} kW",
            f"P17 particles at balance, beta 200 vs 10: {fi[200] / fi[10]:.2f}",
            f"P18 gearbox oil and generator air flows: {co['oil']:.1f}, "
            f"{co['air']:.1f} kg/s",
            f"P19 hours above 35 C; lowest cooling capacity: {co['hot_h']}, "
            f"{co['cap_min']:.0%}",
            f"P20 insulation life, normal / 10 K hotter: {il['life']:.0f} / "
            f"{il['life_hot']:.0f} years",
            f"P21 permissible residual unbalance: {ba['u_perm']:,.0f} g mm",
            f"P22 shims front / back: {alg['front']:+.2f} / {alg['back']:+.2f} mm",
            f"P23 weld damage in 20 years, category 71 / 90: {we[71.0]:.2f} / "
            f"{we[90.0]:.2f}",
            f"P24 yaw calipers needed: {ya['need']}",
            f"P25 insulation index dry / damp: {pi['pi']:.1f} / {pi['pi_wet']:.2f}",
            f"P26 gearboxes held after run-in: "
            f"{sum(1 for v in run.values() if v != 'accept')}",
            f"P27 holds in the blade plan: {plan['H']}",
            f"P28 NCRs past their limit: {ncr['late']}",
            f"P29 longest supplier chain: {max(ti.values())} weeks",
            f"P30 Cpk lower bound from 10 blades: {fa[10]:.2f}",
            f"P31 loose joints expected, manual / logged: {tq['manual']:.1f} / "
            f"{tq['logged']:.2f}",
            f"P32 blade repair cost and turbine-days: {dm['cost']:,.0f} k u, "
            f"{dm['days']:.0f}",
            f"P33 field-repair hours in the best month: {max(wi.values())}",
            f"P34 serial clause triggers at 10 %: {sd[0.10]:.0%}"] + rounds()


def rounds() -> list[str]:
    from companion.ch42 import examples_s as es
    from companion.ch42 import examples_t as et
    from companion.ch42 import examples_u as eu
    from companion.ch42 import examples_v as ev
    mb = es.mass_budget()
    inf = es.infusion()
    ex = es.exotherm()
    gy = es.generator_year()
    oi = es.oil_settling()
    cr = es.crane_value()
    oa = et.offaxis()
    ft = et.fatigue_test()
    ins = et.inserts()
    wt = et.weights()
    ch = eu.chvorinov()
    pl = eu.preload()
    pi = eu.pitch()
    sc = eu.shaft_crack()
    sf = eu.surface()
    tw = ev.twist()
    pc = ev.placement()
    rt = ev.retension()
    return [f"P35 blade first mass moment: {mb['moment']:.0f} t m",
            f"P36 fill time to 2 m: {inf[2.0]:.0f} min",
            f"P37 adiabatic rise of a thick laminate: {ex['rise']:.0f} K",
            f"P38 generator efficiency rated / year: {gy['eta_rated']:.2%} / "
            f"{gy['eta_year']:.2%}",
            f"P39 oil settling time at each step: {oi['t_ok']:.0f} min",
            f"P40 present value of crane campaigns: {cr['pv']:,.0f} k u",
            f"P41 ply modulus at 45 deg: {oa[45]:.1f} GPa",
            f"P42 fatigue test days and equivalent cycles: {ft['days']:.0f}, "
            f"{ft['equiv']:.2e}",
            f"P43 insert characteristic pull-out: {ins['char']:.0f} kN",
            f"P44 first blade over the weight limit: {wt['first']}",
            f"P45 flange solidification time: {ch['flange (200 mm)']:.0f} min",
            f"P46 opening margin, wrench / tensioner: "
            f"{pl['torque wrench']:.2f} / {pl['hydraulic tension']:.2f}",
            f"P47 pitch power and feather energy a blade: {pi['p_kw']:.0f} kW, "
            f"{pi['e_kj']:.0f} kJ",
            f"P48 critical crack depth of the shaft: {sc['a_c']:.1f} mm",
            f"P49 endurance limit with forging skin: {sf['forged skin']:.0f} MPa",
            f"P50 untwists in the data-pack year: {tw['untwists']}",
            f"P51 cable loss down the tower, 690 V / 33 kV: "
            f"{pc['690 V from the converter']:.1f} / "
            f"{pc['33 kV from a nacelle transformer']:.1f} kW",
            f"P52 chance a 10 % bolt check finds looseness: {rt['found']:.0%}"
            ] + rounds2()


def rounds2() -> list[str]:
    from companion.ch42 import examples_w as ew
    from companion.ch42 import examples_x as ex
    modes = ew.pfmea()
    n_crit = ew.critical()
    cd = ew.case_depth()
    cp = ew.cap_thickness()
    cq = ew.copq()
    bf = ex.bolt_fatigue()
    wr = ex.winding_rise()
    sh = ex.shocks()
    sc = ex.scarf()
    bl = ex.baseline()
    return [f"P53 first failure mode of the process ranking: {modes[0]}",
            f"P54 critical characteristics of the turbine: {n_crit}",
            f"P55 case depth of heat HT-43: {cd['HT-43']:.2f} mm",
            f"P56 cap thickness Cpk at 50 m: {cp[50.0]:.2f}",
            f"P57 cost of quality of a year's blades: {cq['total']:,.0f} k u",
            f"P58 bolt damage closed / open: "
            f"{bf['closed (preload kept)']:.2f} / {bf['open (preload lost)']:.0f}",
            f"P59 hot winding temperature and rise: {wr['t_hot']:.1f} C, "
            f"{wr['rise']:.1f} K",
            f"P60 nacelles over the shock limit: {', '.join(sh['over'])}",
            f"P61 scarf length each side for a 20 mm skin: {sc[20.0]:.2f} m",
            f"P62 first year above the alert: {bl['first']}"] + rounds3()


def rounds3() -> list[str]:
    from companion.ch42 import examples_y as ey
    from companion.ch42 import examples_z as ez
    cl = ey.clearance()
    fq = ey.frequency()
    ct = ey.contact()
    se = ey.settling()
    tw = ey.tower_welds()
    lk = ey.leak()
    lu = ez.loss_uncertainty()
    cg = ez.cog()
    ci = ez.circle()
    sa = ez.saddles()
    co = ez.coating()
    return [f"P63 clearance taken worst / RSS: {cl['worst']:.2f} / {cl['rss']:.2f} m",
            f"P64 error of the stiffness estimate, sd: {fq['err_sd']:.2f} %",
            f"P65 case depth needed nominal / edge load: "
            f"{ct['nominal']:.2f} / {ct['edge load x 1.3']:.2f} mm",
            f"P66 preload lost bare / painted: "
            f"{se['bare steel (embedding)']:.1%} / "
            f"{se['painted, coating creeps 15 %']:.1%}",
            f"P67 weld length of a tower: {tw['weld_m']:.0f} m",
            f"P68 leak test fall corrected for temperature: "
            f"{lk['corrected']:.0f} mbar",
            f"P69 gearbox loss uncertainty direct / back to back: "
            f"{lu['direct']:.0f} / {lu['b2b']:.1f} kW",
            f"P70 centre of gravity off the drawing: {cg['off']:.0f} mm",
            f"P71 worst insert: {ci['worst']}, {ci['dev']:+.2f} mm",
            f"P72 worst overload, three saddles B: {sa['three B'] - 1:.0%}",
            f"P73 blade to recoat: {', '.join(co['bad'])}"] + rounds4()


def rounds4() -> list[str]:
    from companion.ch42 import examples_m as em
    ps = em.passes()
    sh = em.sharing()
    fo = em.fouling()
    ag = em.airgap()
    lf = em.local_factory()
    return [f"P74 lowest preload after passes 1, 2, 3: "
            + ", ".join(f"{x:.0%}" for x in ps["crosswise"]),
            f"P75 load factor and life at 20 um pin error: {sh[20.0]:.3f}, "
            f"{sh[20.0] ** (-10 / 3):.0%}",
            f"P76 energy lost with the cooler at 70 %: {fo[0.70]:,.0f} MWh/yr",
            f"P77 rotor offset in the air gap: {ag['e']:.2f} mm "
            f"({ag['share']:.1%})",
            f"P78 blades to break even on a local factory: {lf['blades']:,.0f}"
            ] + rounds5()


def rounds5() -> list[str]:
    from companion.ch42 import examples_n as en
    mo = en.moulds()
    sc = en.scan_data()
    rv = en.runin_value()
    return [f"P79 blades a week from two mould sets: {mo['per_week']:.1f}",
            f"P80 full scan waveforms of one blade: {sc['full_gb']:.0f} GB",
            f"P81 expected saving of the run-in: {rv['saved']:,.0f} k u"]


if __name__ == "__main__":
    worked()
    solutions()
