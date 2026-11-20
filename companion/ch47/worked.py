"""Chapter 47 - small worked examples (E-lines) and the numerical answers
of the exercises (P-lines), each computed here.

Run from the project root:   python -m companion.ch47.worked
Writes companion/ch47/expected/worked.txt and solutions.txt.
"""
from __future__ import annotations

import math

from companion.ch47 import examples_a as ea
from companion.ch47 import examples_b as eb
from companion.ch47 import examples_c as ec
from companion.ch47 import examples_s as es
from companion.ch47 import integrated as it
from companion.ch47 import lab_d
from companion.ch47.common import emit
from plantp import civilmfg as cv


def worked() -> None:
    lines = [f"E01 CEV of C 0.16, Mn 1.45, Cu 0.05: {cv.cev(0.16, 1.45, cu=0.05):.3f}",
             f"E02 mass of a 25 mm bar: {cv.bar_mass(25):.2f} kg/m",
             f"E03 mass of 240 bars of 25 mm, 3.6 m: "
             f"{cv.bar_mass(25) * 3.6 * 240 / 1000:.2f} t",
             f"E04 diameter change from 12 mm more circumference: {12 / math.pi:.2f} mm",
             f"E05 thermal movement of 60 m steel for 40 K: "
             f"{60 * 12e-6 * 40 * 1000:.1f} mm",
             f"E06 dynamic pressure at 41.1 m/s, rho 1.09: {0.5 * 1.09 * 41.1 ** 2:.0f} Pa",
             f"E07 lean at 100 m of a 0.92 mm/m tilt: {0.92 * 100:.0f} mm",
             f"E08 specimens for 893 m3 at one set of 3 per 50 m3: "
             f"{math.ceil(893 / 50) * 3}"]
    emit("worked", lines)


def solutions() -> None:
    tk = ea.takeoff()
    lp = ea.load_path()
    ce = eb.certs()
    gn = eb.genealogy()
    wl = eb.welders()
    nd = eb.ndt()
    tr = eb.tracker()
    zn = eb.zinc()
    bb = eb.bbs()
    tkt = eb.tickets()
    stg = eb.strength()
    nc = ec.ncrs()
    ds = ec.dossier()
    an = ec.anchor()
    ps = ec.posts()
    rel = lab_d.release()
    itp = lab_d.itp()
    ap = lab_d.approvals()
    hb = it.by_hand()
    sw = es.stow()
    th = es.thermal()
    fu = es.fitup()
    zm = es.zinc_mass()
    sp = es.specimens()
    pa = es.pareto()
    fm = es.farm()
    ck = es.crack()
    vi = es.visits()
    out = [f"P01 tower shell / with fatigue steel and flanges: "
           f"{tk['shell']:.0f} / {tk['tower']:.0f} t",
           f"P02 rebar of one foundation at 95 kg/m3: {tk['rebar']:.0f} t",
           f"P03 PV tables and their steel: {tk['tables']:,}, {tk['pv_steel']:,.0f} t",
           f"P04 worst flange bolt pull at the extreme: {lp['f_bolt']:,.0f} kN",
           f"P05 eccentricity, compressed area, pressure: {lp['e']:.2f} m, "
           f"{lp['a']:.0f} m2, {lp['q']:.0f} kPa",
           f"P06 plates not matching the order: {', '.join(ce)}",
           f"P07 cans from heat H5523: {', '.join(gn['cans'])}",
           f"P08 joints by welders not qualified on the day: "
           f"{', '.join(j for j, *_ in wl)}",
           f"P09 NDT categories short of the plan: {', '.join(nd['short'])}",
           f"P10 torque-tube offset: {tr['off']:.1f} mm at {tr['x']:.0f} m",
           f"P11 drives with findings: {', '.join(s for s, _ in tr['odd'])}",
           f"P12 zinc lots rejected: {', '.join(zn['bad'])}",
           f"P13 BBS problems and clean mass: {len(bb['probs'])}, "
           f"{bb['mass'] / 1000:.1f} t",
           f"P14 trucks outside the rules: {', '.join(str(k) for k, _ in tkt['bad'])}",
           f"P15 pours not conforming: {', '.join(stg)}",
           f"P16 NCRs open over 90 days: {', '.join(nc['old'])}",
           f"P17 dossier documents missing for section 1: {len(ds['miss'])}",
           f"P18 cage tilt before / after, lean at the hub: {an['t0']:.2f} / "
           f"{an['t1']:.2f} mm/m, {an['lean']:.0f} mm",
           f"P19 posts outside tolerance, shifted rows: {ps['out']}, "
           f"{', '.join(map(str, ps['sys_rows']))}",
           f"P20 holds by section: " + ", ".join(f"{k}: {v}" for k, v in rel.items()),
           f"P21 ITP hold points, steps for licensed engineers: {itp['holds']}, "
           f"{itp['lic']}",
           f"P22 decisions for licensed engineers: {ap['lic']} of {ap['n']}",
           f"P23 CEV of P105 by hand: {hb['cev']:.3f}",
           f"P24 stow torque at the 50-year gust: {sw[41.1]:.1f} kN m",
           f"P25 thermal movement of the tube: {th['mm']:.1f} mm",
           f"P26 seams over the fit-up limit: {', '.join(map(str, fu['bad']))}",
           f"P27 zinc on the PV field: {zm['zn']:.0f} t",
           f"P28 specimens for twelve foundations: {sp['n']}",
           f"P29 share of the two largest NCR causes: {pa['top2']:.0%}",
           f"P30 farm dossiers: missing documents {fm['gaps']}, complete sections "
           f"{fm['complete']}",
           f"P31 other cans to scan after the lamination: {ck['n']}",
           f"P32 inspector visits all / sampled: {vi['all']} / {vi['sample']}"]
    from companion.ch47 import examples_t as et
    from companion.ch47 import examples_u as eu
    from companion.ch47 import examples_v as ev
    fl = et.flatness()
    tr2 = et.transport()
    wg = et.weighed()
    rp = et.repairs()
    em = et.embeds()
    pl = eu.plinths()
    ho = eu.holes()
    rb = eu.rebar()
    er = eu.erection()
    gr = eu.grout()
    ov = eu.ovality()
    bl = eu.backlog()
    pv = ev.pv_rates()
    kt = ev.kettle()
    ln = ev.tower_lines()
    hw = ev.hold_waits()
    out += [f"P33 flatness of F2 after the plane / raw range: {fl['F2'][2]:.2f} / "
            f"{fl['F2'][0]:.2f} mm",
            f"P34 section 1 for transport, plan / now: {tr2[1][0]:.0f} / "
            f"{tr2[1][1]:.0f} t",
            f"P35 weighed tower and frequency factor: {wg['tower']:.0f} t, "
            f"{wg['f_ratio']:.3f}",
            f"P36 sections off their calculated mass: "
            f"{', '.join(map(str, wg['odd']))}",
            f"P37 welders above the repair limit: {', '.join(rp['odd']) or 'none'}",
            f"P38 embedded items missing before the pour: {sum(em['miss'].values())}",
            f"P39 plinths needing a shim plan: {', '.join(pl['bad'])}",
            f"P40 supports with a hole out of pattern: "
            f"{', '.join(k for k, v in ho.items() if v[2] == 'one hole off')}",
            f"P41 rebar bundles held: {', '.join(rb)}",
            f"P42 erection end day and crane idle days: {er['end']:.0f}, "
            f"{er['idle']:.0f}",
            f"P43 grout thickness range on T05: {gr['thin']:.1f} - {gr['thick']:.1f} mm",
            f"P44 ovality Cpk and expected share over: {ov['cpk']:.2f}, "
            f"{ov['ppm'] / 1e4:.1f} %",
            f"P45 NCR wait by Little's law: {bl['w']:.0f} days",
            f"P46 posts, rigs and crews: {pv['posts']:,}, {pv['rigs']}, {pv['crews']}",
            f"P47 kettle days for the PV steel: {kt['days']:.0f}",
            f"P48 tower fabrication lead before the first erection: {ln['lead']:.0f} "
            "days",
            f"P49 hold-point waiting, all and with notice: {hw['total']:.0f} / "
            f"{hw['notice']:.0f} days"]
    from companion.ch47 import examples_w as ew
    from companion.ch47 import examples_x as ex
    bo = ew.bolt_lots()
    mv = ew.marks_value()
    br = ew.bearing_gaps()
    fa = ew.fasteners()
    ck2 = ew.cert_types()
    ar = ew.arrival()
    lg2 = ex.logistics()
    dft = ex.dft()
    zm2 = ex.zinc_methods()
    rc = ex.records()
    ea2 = ex.early()
    out += [f"P50 flanges with mixed bolt lots: {', '.join(bo['mixed'])}",
            f"P51 recall cost without / with marks, cost of marking: {mv['no']:.0f} / "
            f"{mv['with_']:.1f} / {mv['mark']:.1f} k u",
            f"P52 bearing room to grow / shrink set at 20 C: {br[20.0][0]:.1f} / "
            f"{br[20.0][1]:.1f} mm",
            f"P53 fasteners to sample: {fa['n']}",
            f"P54 plates with non-specific certificates: {', '.join(ck2['ns'])}",
            f"P55 sections with an NCR on arrival: {', '.join(ar['odd'])}",
            f"P56 trailer axle load on 14 / 16 axles: {lg2['axles'][14]:.0f} / "
            f"{lg2['axles'][16]:.0f} kN; lift use {lg2['use']:.2f}",
            f"P57 sections failing DFT: {', '.join(map(str, dft['bad']))}",
            f"P58 zinc of Z-02/08 by mass: {zm2['Z-02/08'][0]:.0f} um",
            f"P59 records to read and reviewer-days: {rc['n']:,}, {rc['days']:.0f}",
            f"P60 pours warned at 7 days: {', '.join(ea2['warn'])}"]
    emit("solutions", out)


if __name__ == "__main__":
    worked()
    solutions()
