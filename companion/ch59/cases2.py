"""Chapter 59, deeper lessons for cases E-J: common cause, data needed,
criticality; imbalance and the service envelope; study inputs, interfaces
and collector options; conditions precedent and the DSCR profile; land
and livelihood; the equipment hierarchy and information requirements.

Run from the project root:   python -m companion.ch59.cases2
"""
from __future__ import annotations

import collections
import contextlib
import io
import math

import numpy as np

from companion.ch59 import common  # noqa: F401  (path)
from companion.ch59.common import emit


# ------------------------------------------------------- E reliability
def e_ccf() -> dict:
    from companion.ch52 import lab_f
    from companion.ch52 import sources as s52
    from plantp import ram
    n, lam, mttr, delay, *_ = s52.CLASSES["main transformer"]
    q = lam * (mttr + delay) / 8760.0
    with contextlib.redirect_stdout(io.StringIO()):
        poc = float(lab_f.series()["poc"].sum())
    lines = ["the two main transformers: both out, with a common cause (beta factor)",
             f"  one unit unavailable q = {lam} x ({mttr:.0f} + {delay:.0f}) h / 8760 = {q:.4f}"]
    out = {}
    for beta in (0.0, 0.02, 0.05, 0.10):
        p = ram.pair_with_ccf(q, beta)
        out[beta] = p
        lines.append(f"  beta {beta:4.2f}: both out {p:.2e} of the year,"
                     f" {p * poc:7.1f} MWh/yr")
    lines += [f"  a 5 % common cause makes 'both out' {out[0.05] / out[0.0]:.0f} times more likely",
              "  than independent failures: a shared fire, flood or protection",
              "  error matters more than a second transformer's own failure"]
    emit("e_ccf", lines)
    return dict(q=q, out=out, ratio=out[0.05] / out[0.0])


def e_data() -> dict:
    """Failures needed for a 90 % interval no wider than a factor 2, and the
    years a fleet takes to see them (chi-square, as ch 52)."""
    from companion.ch52 import sources as s52
    from scipy.stats import chi2
    k = 1
    while True:
        lo = chi2.ppf(0.05, 2 * k) / 2
        hi = chi2.ppf(0.95, 2 * k + 2) / 2
        if hi / lo <= 2.0:                    # upper bound at most twice the lower (as ch 52)
            break
        k += 1
    lines = [f"failures needed before a rate is known within a factor 2: {k}",
             f"  {'class':32s} {'units':>5s} {'per yr':>7s} {'years':>7s}"]
    out = {}
    for cls in ("PV inverter", "wind turbine (minor)", "wind turbine (major)",
                "PV unit transformer", "main transformer", "BESS PCS"):
        n, lam = s52.CLASSES[cls][0], s52.CLASSES[cls][1]
        yrs = k / (n * lam)
        out[cls] = yrs
        lines.append(f"  {cls:32s} {n:5d} {n * lam:7.2f} {yrs:7.1f}")
    lines += ["  the plant itself never shows the rate of rare failures: for",
              "  major turbine parts and main transformers the evidence is the",
              "  maker's fleet data, asked for in the contract (ch 39, 52)"]
    emit("e_data", lines)
    return dict(k=k, out=out)


def e_crit() -> dict:
    from companion.ch52 import lab_f
    from companion.ch52 import sources as s52
    with contextlib.redirect_stdout(io.StringIO()):
        ex = lab_f.expected()
    rows = []
    for cls, (n, lam, mttr, delay, pmh, cons, mw) in s52.CLASSES.items():
        if cls not in ex or ex[cls] <= 0:
            continue
        freq = n * lam
        rows.append((cls, cons, freq, ex[cls]))
    by_e = sorted(rows, key=lambda r: -r[3])
    by_c = sorted(rows, key=lambda r: (-r[1], -r[3]))
    lines = ["critical-equipment register: two rankings (ch 52 classes)",
             f"  {'class':32s} {'cons.':>5s} {'fail/yr':>8s} {'MWh/yr':>8s}"]
    for cls, c, f, e in by_c:
        lines.append(f"  {cls:32s} {c:5d} {f:8.2f} {e:8,.0f}")
    top_e = [r[0] for r in by_e[:3]]
    top_c = [r[0] for r in by_c[:3]]
    lines += ["  by energy: " + ", ".join(top_e),
              "  by consequence: " + ", ".join(top_c),
              "  the register keeps both: energy decides spares and contracts,",
              "  consequence decides protection, inspection and emergency plans"]
    emit("e_crit", lines)
    return dict(top_e=top_e, top_c=top_c)


# ---------------------------------------------- F forecasting, services
def f_imbalance() -> dict:
    from companion.ch15 import forecast as fc
    from companion.ch20 import sources as s20
    w_, pv, *_ = fc.truth()
    act = w_ + pv
    pr = s20.IMBALANCE
    lines = ["imbalance against the forecast schedule (teaching prices A-301:",
             f"short {pr['short']:.0f}, long {pr['long']:.0f} u/MWh)",
             f"  {'lead h':>6s} {'short MWh':>10s} {'long MWh':>10s} {'cost k u':>9s}"
             f" {'with 20 MW':>11s}"]
    out = {}
    for lead in (1, 6, 24, 36):
        wf, pf = fc.nwp(lead)
        e = act - (wf + pf)
        short = float(np.clip(-e, 0, None).sum())
        long_ = float(np.clip(e, 0, None).sum())
        cost = (short * pr["short"] + long_ * pr["long"]) / 1000
        short_b = float(np.clip(-e - 20.0, 0, None).sum())
        cost_b = (short_b * pr["short"] + long_ * pr["long"]) / 1000
        out[lead] = (short, long_, cost, cost_b)
        lines.append(f"  {lead:6d} {short:10,.0f} {long_:10,.0f} {cost:9,.0f} {cost_b:11,.0f}")
    c24 = out[24]
    lines += [f"  day-ahead: the battery could cut the imbalance cost from {c24[2]:,.0f} to",
              f"  {c24[3]:,.0f} k u - an upper bound, ignoring its state of charge and the",
              "  energy it must hold for other duties (ch 20 E)"]
    emit("f_imbalance", lines)
    return out


# ------------------------------------------------------------ G export
def g_inputs() -> dict:
    from companion.ch28 import register as r28
    st = collections.Counter(x[3] for x in r28.INPUTS)
    owners = collections.Counter(x[2] for x in r28.INPUTS)
    missing = [x[0] for x in r28.INPUTS if x[3] in ("requested", "assumed", "missing")]
    lines = [f"grid-study and protection inputs (ch 28 register): {len(r28.INPUTS)} items",
             "  status: " + ", ".join(f"{k} {v}" for k, v in st.most_common()),
             "  owners: " + ", ".join(f"{k} {v}" for k, v in owners.most_common()),
             f"  not yet in hand: {len(missing)} - " + ", ".join(missing[:8])
             + (" ..." if len(missing) > 8 else ""),
             "  each missing input is a condition of the connection agreement",
             "  and a line in the request to the network operator (ch 54-57)"]
    emit("g_inputs", lines)
    return dict(st=dict(st), missing=len(missing), n=len(r28.INPUTS))


def g_interfaces() -> dict:
    from companion.ch18 import sources as s18
    its = s18.interfaces()
    bad = [(i.iid, i.mismatch()) for i in its if i.mismatch()]
    kinds = collections.Counter(i.kind for i in its)
    lines = [f"interface register (ch 18): {len(its)} interfaces",
             "  by kind: " + ", ".join(f"{k} {v}" for k, v in kinds.most_common()),
             f"  mismatches found by the check: {len(bad)}"]
    lines += [f"    {i}: {m}" for i, m in bad]
    lines += ["  the ch 18 register keeps its planted mismatches as data; the",
              "  dossier lists the decision that answers each (D-012 inverter",
              "  voltage, ch 41 connector type, D-023 battery HVAC, D-039",
              "  protocols) and reruns the check at each design revision"]
    emit("g_interfaces", lines)
    return dict(n=len(its), bad=len(bad))


def g_collector() -> dict:
    from companion.ch18 import examples_f
    from companion.ch18 import sources as s18
    from companion.ch21 import sources as s21
    from plantp import finance as fn
    price, wacc = s21.TERMS["tariff"], s21.TERMS["wacc"]
    lines = ["collector cable options over 25 years (ch 18; energy at the PPA price)",
             f"  {'option':16s} {'cost':>6s} {'loss MWh':>9s} {'PV loss':>8s} {'total':>7s}"
             f" {'ok':>4s}"]
    out = {}
    for name in s18.CABLES:
        with contextlib.redirect_stdout(io.StringIO()):
            c = examples_f.collector_option(name)
        pv_l = fn.pv(np.full(25, c["loss"] * price / 1e3), wacc)       # k u
        tot = c["cost"] + pv_l
        out[name] = (c["cost"], c["loss"], pv_l, tot, c["ok"])
        lines.append(f"  {name:16s} {c['cost']:6,.0f} {c['loss']:9,.0f} {pv_l:8,.0f}"
                     f" {tot:7,.0f} {'yes' if c['ok'] else 'NO':>4s}")
    best = min((k for k, v in out.items() if v[4]), key=lambda k: out[k][3])
    d33 = out["33 kV 630 mm2"][3] - out["33 kV 240 mm2"][3]
    lines += [f"  lowest life cost among the ratings that carry the current: {best}",
              f"  at 33 kV the larger section costs {d33:+,.0f} k u over the life - a",
              "  break-even; 66 kV cuts the losses most, but its turbine",
              "  transformers and switchgear are not in this comparison (ch 18)"]
    emit("g_collector", lines)
    return dict(out=out, best=best)


# ----------------------------------------------------------- H finance
def h_cp() -> dict:
    from companion.ch21 import lab_g
    st = collections.Counter(c[2] for c in lab_g.CP)
    lines = [f"conditions precedent to financial close (ch 21 register): {len(lab_g.CP)}",
             "  status: " + ", ".join(f"{k} {v}" for k, v in st.most_common())]
    for ev, srcs, s in lab_g.CP:
        lines.append(f"  [{s:5s}] {ev[:46]:46s} {srcs}")
    lines += ["  no condition is closed by the engineering dossier alone: each",
              "  needs a signed contract, a permit or an independent review"]
    emit("h_cp", lines)
    return dict(st=dict(st), n=len(lab_g.CP))


def h_profile() -> dict:
    from companion.ch21 import model
    r = model.run()
    d = np.asarray(r["dscr"])
    yr = int(np.nanargmin(d)) + 1
    eq = np.asarray(r["eq_cash"])
    lines = ["the debt-service cover year by year (ch 21 base, sculpted)",
             "  year: " + " ".join(f"{i + 1:>5d}" for i in range(8)),
             "  DSCR: " + " ".join(f"{v:5.2f}" for v in d[:8]),
             "  year: " + " ".join(f"{i + 9:>5d}" for i in range(len(d) - 8)),
             "  DSCR: " + " ".join(f"{v:5.2f}" for v in d[8:]),
             f"  minimum {np.nanmin(d):.2f} in year {yr}; mean {np.nanmean(d):.2f}",
             f"  equity: {-eq[:2].sum():,.0f} k u in, {eq[2:].sum():,.0f} k u out over the life",
             "  a sculpted profile keeps the cover near its target every year;",
             "  the lenders read the minimum, the sponsor the tail (ch 21 F)"]
    emit("h_profile", lines)
    return dict(min=float(np.nanmin(d)), yr=yr, mean=float(np.nanmean(d)))


# ------------------------------------------------------------ I social
def i_land() -> dict:
    from companion.ch33 import sources as s33
    lu = s33.LAND_USE
    h = s33.HERDERS
    take = sum(v for k, v in lu.items() if "temporary" not in k)
    share = take / h["grazing_ha"]
    loss = h["animals"] * h["income_per_animal"] * share
    lines = ["land take and the herders' livelihood (ch 33 teaching values)",
             f"  permanent take {take:.1f} ha; temporary {lu['laydown (temporary)']:.1f} ha",
             f"  herders: {h['households']} households, {h['animals']} animals,"
             f" {h['grazing_ha']:.0f} ha of grazing",
             f"  if all the take is grazing: {share:.1%} of it, about {loss:.1f} k u a year",
             f"  plus a {h['detour_km']} km detour on the {h['route_to_spring_km']} km"
             " route to the spring",
             "  the money is small; the access route is not - a crossing kept",
             "  open and grazing allowed under the PV rows answer it (ch 33)"]
    emit("i_land", lines)
    return dict(take=take, share=share, loss=loss)


# ---------------------------------------------------------- J handover
def j_hierarchy() -> dict:
    from companion.ch18 import sources as s18
    root = s18.breakdown()
    by_level = collections.Counter()
    types = collections.Counter()
    for node, n, depth in root.walk():
        by_level[node.level] += n
        types[node.level] += 1
    lines = ["the equipment hierarchy of Plant P (ch 18 product breakdown)"]
    for lv in ("plant", "system", "subsystem", "equipment", "unit"):
        if lv in by_level:
            lines.append(f"  {lv:10s} {types[lv]:4d} kinds {by_level[lv]:7,d} items")
    lines += [f"  items in all: {sum(by_level.values()):,d}",
              "  every item gets a functional location and a tag; only the",
              "  maintainable ones get an asset record in the CMMS"]
    emit("j_hierarchy", lines)
    return dict(levels=dict(by_level), kinds=dict(types))


REQS = {   # information requirements by asset class (teaching, A-575)
    "inverter": ("tag", "floc", "serial", "firmware", "settings checksum", "FAT", "SAT",
                 "warranty end", "maintenance plan"),
    "transformer": ("tag", "floc", "serial", "FAT report", "oil and DGA baseline",
                    "FRA baseline", "warranty end", "maintenance plan"),
    "turbine": ("tag", "floc", "serial", "type certificate", "SAT", "service contract",
                "SCADA points", "maintenance plan"),
    "relay": ("tag", "floc", "serial", "settings file", "test record", "firmware"),
}


def j_requirements() -> dict:
    tot = sum(len(v) for v in REQS.values())
    lines = ["information requirements by asset class (what the handover must carry)"]
    for k, v in REQS.items():
        lines.append(f"  {k:12s} {len(v):2d}: " + ", ".join(v[:5]) + ("," if len(v) > 5 else ""))
        if len(v) > 5:
            lines.append(f"  {'':16s}" + ", ".join(v[5:]))
    lines += [f"  {tot} fields over four classes; the CMMS import checks each one",
              "  is filled and points to a record that exists (ch 50)"]
    emit("j_requirements", lines)
    return dict(tot=tot)


def f_tech() -> dict:
    from companion.ch15 import forecast as fc
    w_, pv, *_ = fc.truth()
    lines = ["forecast error by technology and lead (RMSE, % of each capacity:",
             "wind 60 MW, PV 50 MW AC; same archive and seeds)",
             f"  {'lead h':>6s} {'wind':>7s} {'PV':>7s} {'plant':>7s}"]
    out = {}
    for lead in (1, 6, 24, 36):
        wf, pf = fc.nwp(lead)
        ew = float(np.sqrt(np.mean((w_ - wf) ** 2))) / 60.0
        ep = float(np.sqrt(np.mean((pv - pf) ** 2))) / 50.0
        eh = float(np.sqrt(np.mean((w_ + pv - wf - pf) ** 2))) / fc.CAP
        out[lead] = (ew, ep, eh)
        lines.append(f"  {lead:6d} {ew:7.1%} {ep:7.1%} {eh:7.1%}")
    w24, p24, h24 = out[24]
    mw_w, mw_p, mw_h = w24 * 60.0, p24 * 50.0, h24 * fc.CAP
    rss = (mw_w ** 2 + mw_p ** 2) ** 0.5
    lines += [f"  day-ahead in MW: wind {mw_w:.1f}, PV {mw_p:.1f}, plant {mw_h:.1f}; root-sum-",
              f"  square of the two {rss:.1f}: the errors are nearly independent and the",
              "  wind error dominates - the wind forecast is where better data pays"]
    emit("f_tech", lines)
    return out


def main() -> dict:
    out = {}
    for f in (f_tech, e_ccf, e_data, e_crit, f_imbalance, g_inputs, g_interfaces, g_collector,
              h_cp, h_profile, i_land, j_hierarchy, j_requirements):
        out[f.__name__] = f()
    return out


if __name__ == "__main__":
    main()
