"""Chapter 41 - small worked examples (E-lines) and the numerical answers
of the exercises (P-lines), each computed here.

Run from the project root:   python -m companion.ch41.worked
Writes companion/ch41/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

import math

from companion.ch41 import examples_a as ea
from companion.ch41 import examples_b as eb
from companion.ch41 import examples_c as ec
from companion.ch41 import examples_e as ee
from companion.ch41 import lab_d
from companion.ch41.common import emit
from plantp import pvfab as fab


def worked() -> None:
    rho = 1 / (ea.Q * 1e16 * 400)
    L10 = fab.diffusion_length_um(ea.VT300 * 1050, 10e-6)
    tau = 1 / (1 / 1e-3 + 2 * 10 / 0.015)
    lines = [f"E01 resistivity of p-type silicon, 1e16 cm-3, mu 400: "
             f"{rho:.2f} ohm cm",
             f"E02 diffusion length for 10 us (D 27.1 cm2/s): {L10:.0f} um",
             f"E03 tau_eff, bulk 1 ms, S 10 cm/s, 150 um (no Auger): "
             f"{tau * 1e6:.0f} us",
             f"E04 Voc from Jsc 41.8 mA/cm2 and J0 91 fA/cm2: "
             f"{fab.voc(0.0418, 9.1e-14):.3f} V",
             f"E05 ideal FF for Voc 0.690 V: {fab.fill_factor(0.69):.3f}",
             f"E06 gallium at half the ingot, relative to the seed end: "
             f"{eb.scheil(0.5, 0.008) / eb.scheil(0, 0.008):.2f}",
             f"E07 quarter-wave coating for 600 nm at n 2.0: "
             f"{600 / (4 * 2.0):.0f} nm",
             f"E08 sheet resistance from V/I 26.5 ohm: {4.532 * 26.5:.0f} "
             "ohm/sq",
             f"E09 clamp position on a 2,278 mm module: "
             f"{2278 / (2 + 2 * math.sqrt(2)):.0f} mm",
             f"E10 EL sample for 1 % at 95 %: "
             f"{math.ceil(math.log(0.05) / math.log(0.99))} modules",
             f"E11 heat in a 10 mOhm connector at 13.11 A: "
             f"{13.11 ** 2 * 0.010:.2f} W",
             f"E12 robust z of 538 W, median 552.3, MAD 1.1 W: "
             f"{0.6745 * (538 - 552.3) / 1.1:.1f}"]
    emit("worked", lines)


def solutions() -> None:
    pas = ea.passivation()
    g = ea.grid()
    v = ea.variation()
    t = ea.tempco()
    ing = eb.ingot()
    si = eb.silicon()
    arc = eb.arc()
    fi = eb.firing()
    ll = eb.low_light()
    bn = eb.binning_lesson()
    gen = eb.genealogy()
    ch = eb.chain()
    out = [f"P01 implied Voc, bulk 1 ms, S 10 cm/s: {pas[(1e-3, 10)]:.3f} V",
           f"P02 implied Voc, bulk 1 ms, S 1,000 cm/s: "
           f"{pas[(1e-3, 1000)]:.3f} V",
           f"P03 best finger spacing and its loss: {g['s_mm']:.1f} mm, "
           f"{g['total']:.1%}",
           f"P04 efficiency mean and sd of the varied cells: "
           f"{v['mean']:.2%}, {v['sd']:.2%}",
           f"P05 share of variance from J0: {v['j0']:.0%}",
           f"P06 Voc coefficient of a 0.690 V cell: {t[0.69]:.3f} %/K",
           f"P07 usable ingot length, gallium: {ing['gallium']:.0%}",
           f"P08 silicon per watt, 150 um wafer, 55 um kerf: {si[150]:.2f} g/W",
           f"P09 mean reflectance, bare and coated in air: "
           f"{arc['bare, in air']:.1%}, {arc['75 nm n 2.0, in air']:.1%}",
           f"P10 firing window and Cpk: {fi['lo']:.2f}-{fi['hi']:.2f}, "
           f"{fi['cpk']:.2f}",
           f"P11 relative efficiency at 200 W/m2, shunt 300 ohm cm2: "
           f"{ll[300.0][1] / ll[300.0][0]:.3f}",
           f"P12 cells in a neighbour bin (repeatability 0.02 A): "
           f"{bn['rep']:.1%}",
           f"P13 modules holding one contaminated cell lot: {gen['lot']}",
           f"P14 expanded uncertainty of a flash reading: {ch['U']:.2f} %"]
    out += more()
    emit("solutions", out)


def more() -> list[str]:
    b = ec.bom()
    c = ec.ctm()
    lay = ec.layouts()
    lam = ec.lamination()
    acc = ec.acceleration()
    cl = ec.clamping()
    dh = ec.diode_heat()
    ins = ec.insulation()
    tr = ec.transport()
    val = lab_d.validate()
    d = lab_d.drift_quiet()
    o = lab_d.outliers()
    cls = lab_d.classes()
    mc = lab_d.mismatch_cells()
    pl = lab_d.plans()
    con = ee.connectors()
    st = ee.string_check()
    lo = ee.loops()
    w = ee.wiring()
    mo = ee.monitoring()
    pid = ee.pid()
    sp = ee.spares()
    return [f"P15 module mass and glass share: {b['total']:.1f} kg, 74 %",
            f"P16 module power after the CTM steps: {c['p']:.1f} W "
            f"(CTM {c['ratio']:.3f})",
            f"P17 bottom row at 50 %, full / half-cut: "
            f"{lay['bottom row']['full']:.0f} / {lay['bottom row']['half']:.0f} W",
            f"P18 first gel-content signal of L2: day {lam['L2'][0]}",
            f"P19 damp-heat acceleration range: {acc['min']:.0f} to "
            f"{acc['max']:,.0f}",
            f"P20 thermal-cycling acceleration (n 2): {acc['tc']:.1f}",
            f"P21 bending moment ratio, ends vs 0.207 L: {cl['ratio']:.1f}",
            f"P22 diode junction, three diodes on: {dh[3]:.0f} C",
            f"P23 block insulation on a dew morning: "
            f"{ins['dew 40 MOhm'] / 1000:.1f} kOhm",
            f"P24 rough containers caught by the pallet rule: "
            f"{tr['catch']:.0%}",
            f"P25 data problems in the flash file: {val['problems']}",
            f"P26 tester drift: {d['shift']:+.2f} W from seq {d['first']}",
            f"P27 outliers flagged after the correction: {o['flags']}",
            f"P28 labels reissued: {cls['moved']}",
            f"P29 cell mismatch, unsorted / one cell 10 % low: "
            f"{mc['unsorted']:.2%} / {mc['one cell 10 % low']:.2%}",
            f"P30 visual AQL plan per container: n = {pl['n']}, c = {pl['c']}",
            f"P31 heat in an aged cross-mated pair: "
            f"{con['cross-mated, aged']:.2f} W",
            f"P32 string Voc at -15 C with the lot maximum: "
            f"{st['lot maximum']:.0f} V",
            f"P33 surge in the open loop: "
            f"{lo['return along the far table edge']:,.0f} V",
            f"P34 extra loss of U-shaped strings: "
            f"{1 - w['u'] / w['row']:.2%}",
            f"P35 drop of the diode-short string's ratio: {abs(mo['step']):.2%}",
            f"P36 modules below -300 V, floating string: "
            f"{pid['floating, symmetric']}",
            f"P37 string change with one 520 W spare: "
            f"{sp['aged 520 W']:.1f} W"] + rounds()


def rounds() -> list[str]:
    from companion.ch41 import examples_s as es
    from companion.ch41 import examples_t as et
    from companion.ch41 import examples_u as eu
    cap = es.capacity()
    cls = es.classes()["cells sorted into bins"]
    ft = es.flash_temperature()
    lid = es.lid_value()
    rs = es.rs_two_curves()
    tr = et.trapping()["light trapping (4n2)"]
    gr = et.grading()
    pl = et.el_placement()
    wa = eu.warranty()
    iv = eu.field_iv()
    cr = eu.site_crimps()
    return [f"P38 modules a day and days for the order: {cap['per_day']:,.0f},"
            f" {cap['days']:.0f}",
            f"P39 share in the 560 W class with sorted cells: {cls[560]:.1%}",
            f"P40 power error of a 1 K flash temperature error: {ft[1.0]:.2f} W",
            f"P41 life value of 2 % against 0.3 % LID: "
            f"{lid[0.02] - lid[0.003]:,.0f} k u",
            f"P42 Rs from two curves vs the fit: {rs['rs']:.3f} vs "
            f"{rs['fit']:.3f} ohm",
            f"P43 current absorbed by 100 um with light trapping: "
            f"{tr[100]:.1f} mA/cm2",
            f"P44 kappa of the two EL graders: {gr['kappa']:.2f}",
            f"P45 cost with and without pre-lamination EL: "
            f"{pl['pre'] / 1000:.1f} / {pl['post'] / 1000:.1f} k u",
            f"P46 smallest shortfall shown, other lab / same lab (n 100): "
            f"{wa['another lab, new reference'][100]:.2f} / "
            f"{wa['same lab, kept control modules'][100]:.2f} %",
            f"P47 expanded uncertainty of a field I-V curve: {2 * iv['u']:.1f} %",
            f"P48 chance a 5 % crimper is caught in 10 days: {cr[10]:.0%}"] \
        + rounds_vw()


def rounds_vw() -> list[str]:
    from companion.ch41 import examples_v as ev
    from companion.ch41 import examples_w as ew
    r = ev.resistances()
    el = ev.el_image()
    c = ev.cost()
    t = ev.temperature()
    pal = ev.pallets()
    con = ew.contacts()
    fl = ew.flow()
    st = ew.stackup()
    sh = ew.shelf()
    lo = ew.lots()
    return [f"P49 Rs and Rsh read for the weak-joint module: "
            f"{r['weak joints'][0]:.3f} ohm, {r['weak joints'][1]:.0f} ohm",
            f"P50 worst inactive share in the EL image: {el['worst']:.0%}",
            f"P51 module cost and the frame +30 % effect: {c['total']:.3f} u/W,"
            f" +{c['frame30']:.1%}",
            f"P52 energy lost by the hotter build: {t['loss']:.2%}",
            f"P53 modules a container and mass: {pal['per_ctn']}, "
            f"{pal['mass'] / 1000:.1f} t",
            f"P54 contact part at 3 mOhm cm2: {con[3.0]:.3f} ohm cm2",
            f"P55 curing buffer: {fl['buffer']:.0f} modules",
            f"P56 tolerance stack, worst / statistical: +-{st['worst']:.0f} / "
            f"+-{st['rss']:.0f} mm",
            f"P57 encapsulant rolls past their life: {sh['expired']} of 40",
            f"P58 first lot below the lower limit: {lo['first']}"] + round_x()


def round_x() -> list[str]:
    from companion.ch41 import examples_x as ex
    r = ex.routes()
    f = ex.formats()
    e = ex.edge()
    fl = ex.flashers()
    return [f"P59 mean iVoc, pulled mono / multi: "
            f"{r['pulled mono (Cz)'][0]:.3f} / {r['multi (cast)'][0]:.3f} V",
            f"P60 module Isc and mass with 210 mm cells: "
            f"{f['210 mm']['isc']:.2f} A, {f['210 mm']['mass']:.1f} kg",
            f"P61 area share of one mm of edge: {e['per_mm']:.2%}",
            f"P62 %GRR of the flashers, as found / matched: "
            f"{fl['as found (B reads +1.2 W)']['grr']:.0f} / "
            f"{fl['after golden-module match']['grr']:.0f}"]


if __name__ == "__main__":
    worked()
    solutions()
