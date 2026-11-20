"""Chapter 42, lesson A - the turbine as a set of manufactured parts:
the subassembly/interface tree and its load path, the blade-root joint,
the drivetrain loss chain and the heat to remove, reliability allocation,
major replacements over the plant's life, the operating envelope from
the data pack, certification evidence and the critical interfaces.

Run from the project root:   python -m companion.ch42.examples_a
Writes companion/ch42/expected/a_*.txt.
Teaching values (A-450, A-451); turbine values from ch 11 (A-211).
"""
from __future__ import annotations

from companion.ch42 import sources as src
from companion.ch42.common import emit
from plantp import datapack
from plantp import turbinemfg as tm

N_WTG = 12                       # ch 14: twelve WT-5.0-150


# ------------------------------------------------ the tree
def tree() -> dict[str, float]:
    kids: dict[str, list] = {}
    for row in src.TREE:
        kids.setdefault(row[1], []).append(row)
    lines = ["subassembly and interface tree of the WT-5.0-150 (A-450)",
             "  id   name                           mass t  tier  load  links"]

    def walk(node, depth):
        for row in kids.get(node, []):
            nid, _, name, mass, tier, load, links = row
            lines.append(f"  {'  ' * depth}{nid:4s} {name:{30 - 2 * depth}s}"
                         f"{'' if not mass else f'{mass:6.1f}':>7s}  {tier:4d}"
                         f"  {'yes' if load else '-':4s}  {','.join(links)}")
            walk(nid, depth + 1)
    walk(None, 0)
    above = sum(r[3] for r in src.TREE if r[0] not in ("FND",))
    links = sum(len(r[6]) for r in src.TREE) // 2
    path = [r[0] for r in src.TREE if r[5] and r[3]]
    lines += [f"  mass above the foundation {above:.0f} t (ch 11: 611 t); about "
              f"{links} interfaces",
              "  load path: " + " > ".join(["BLD", "HUB", "MSH", "GBX/FRM",
                                            "YAW", "TWR", "FND"]),
              "  every part on the load path is fatigue-critical; each",
              "  link in the tree is an interface with a drawing, a",
              "  tolerance and two owners (ch 18, interface register)"]
    emit("a_tree", lines)
    return dict(above=above, links=links, path=len(path))


# ------------------------------------------------ blade-root joint
def root_joint(phi: float = 0.15) -> dict[str, float]:
    t = src.TURBINE
    n, d, f0 = src.INSERTS["n"], src.INSERTS["circle_m"], \
        src.INSERTS["preload_kn"] * 1e3
    out = {}
    lines = [f"blade-root joint: {n} inserts on a {d} m circle, preload "
             f"{f0 / 1e3:.0f} kN each (A-451)",
             f"  joint factor {phi}: a bolt sees {phi:.0%} of the external pull",
             "  until the joint opens",
             "  case                moment MN m   pull kN   bolt kN   opening"]
    for name, m in (("operating (ch 11)", t["flap_mnm"]),
                    ("extreme (2 x)", 2 * t["flap_mnm"])):
        f = tm.insert_tension(m * 1e6, n, d)
        bolt = f0 + phi * f
        margin = f0 / ((1 - phi) * f)
        out[name] = dict(pull=f, bolt=bolt, margin=margin)
        lines.append(f"  {name:18s} {m:10.1f}   {f / 1e3:7.0f}   {bolt / 1e3:7.0f}"
                     f"   x{margin:4.1f} to open")
    ext = out["extreme (2 x)"]["margin"]
    lines += ["  preload keeps the joint closed, so the bolt sees only a",
              "  small share of each load cycle - fatigue depends on the",
              "  preload being there: tightening records per insert and",
              "  re-tension checks are part of the blade's quality record;",
              f"  at the extreme the teaching joint opens (x{ext:.1f}): more",
              "  inserts, a larger circle or more preload is needed - the",
              "  maker's design must show the joint closed at the extreme"]
    emit("a_root", lines)
    return out


# ------------------------------------------------ drivetrain losses
CHAIN = [("main bearing", 0.997), ("gearbox (3 stages)", 0.980),
         ("generator", 0.975), ("converter", 0.985)]      # A-450


def drivetrain() -> dict[str, float]:
    p_out = src.TURBINE["p_rated_kw"]
    eta = 1.0
    for _, e in CHAIN:
        eta *= e
    p_in = p_out / eta
    lines = [f"drivetrain at rated: {p_out:.0f} kW out, chain efficiency "
             f"{eta:.3f} (ch 11: 0.94)",
             "  stage                  efficiency   power in kW   loss kW"]
    p = p_in
    out = {}
    for name, e in CHAIN:
        loss = p * (1 - e)
        out[name] = loss
        lines.append(f"  {name:22s} {e:10.3f}   {p:11.0f}   {loss:7.0f}")
        p *= e
    tot = sum(out.values())
    lines += [f"  heat to remove at rated: {tot:.0f} kW ({tot / p_out:.1%} of "
              "the output)",
              "  gearbox and generator heat leaves by oil and air coolers in",
              "  the nacelle (lesson C); every percent of efficiency is",
              "  50 kW of heat less to carry away at the top of the tower"]
    emit("a_drivetrain", lines)
    return dict(eta=eta, heat=tot, **out)


# ------------------------------------------------ reliability allocation
ALLOC = [  # subsystem, failures a turbine-year, hours down each (incl. wait)
    ("pitch system", 0.60, 12), ("converter", 0.40, 16),
    ("control and sensors", 0.80, 6), ("yaw system", 0.20, 20),
    ("generator (minor)", 0.15, 30), ("gearbox (minor)", 0.20, 24),
    ("hydraulics and brakes", 0.25, 10),
    ("gearbox replacement", 0.015, 900), ("main bearing", 0.010, 800),
    ("generator replacement", 0.010, 500), ("blade replacement", 0.005, 1200),
]


def allocation() -> dict[str, float]:
    down = {name: f * h for name, f, h in ALLOC}
    tot = sum(down.values())
    avail = 1 - tot / 8760
    lines = ["downtime a turbine-year from failure rates and repair times",
             "  (teaching; repair time includes waiting, ch 37)",
             "  subsystem                 per year   hours each   hours down"]
    for name, f, h in ALLOC:
        lines.append(f"  {name:25s} {f:8.3f}   {h:10d}   {f * h:10.1f}")
    big = sum(down[n] for n, f, _ in ALLOC if f < 0.05)
    lines += [f"  total {tot:.0f} h: availability {avail:.2%}; the four major",
              f"  replacements are {big / tot:.0%} of the downtime from "
              f"{sum(f for _, f, _ in ALLOC if f < 0.05):.2f} events a year",
              "  frequent small faults and rare big ones need different",
              "  answers: spares and access for the first, crane plans and",
              "  component quality for the second"]
    emit("a_alloc", lines)
    return dict(hours=tot, avail=avail, big=big / tot)


# ------------------------------------------------ major replacements
def replacements(years: int = 25) -> dict[str, float]:
    rates = [(n, f) for n, f, _ in ALLOC if f < 0.05]
    lines = [f"major replacements in {N_WTG} turbines over {years} years "
             "(expected counts)",
             "  component                expected   chance of at least one"]
    out = {}
    for name, f in rates:
        e = f * N_WTG * years
        p1 = 1 - (1 - f) ** (N_WTG * years)
        out[name] = e
        lines.append(f"  {name:24s} {e:8.1f}   {p1:22.0%}")
    tot = sum(out.values())
    lines += [f"  about {tot:.0f} crane campaigns in the plant's life: the",
              "  heavy-lift plan, road access and spare strategy of ch 31",
              "  and ch 52 are sized on this, and the component's quality",
              "  record (this chapter) is where its rate starts"]
    emit("a_replace", lines)
    return dict(total=tot, **out)


# ------------------------------------------------ operating envelope
def envelope() -> dict[str, float]:
    h = datapack.load_hourly()
    t_min, t_max = float(h["t_air_c"].min()), float(h["t_air_c"].max())
    p_min = float(h["p_hpa"].min())
    rho_hot = p_min * 100 / (287.05 * (t_max + 273.15))
    lines = ["operating envelope of the site (data pack 1.1.0)",
             f"  air temperature {t_min:.1f} to {t_max:.1f} C; lowest pressure "
             f"{p_min:.0f} hPa",
             f"  densest-to-thinnest: air at {t_max:.0f} C and {p_min:.0f} hPa is "
             f"{rho_hot:.3f} kg/m3",
             "  turbine envelope asked of the maker (teaching): operation",
             "  -20 to +40 C, survival -30 to +50 C, altitude to 1,500 m",
             f"  the site's {t_max:.1f} C peak exceeds +40 C: a hot-climate",
             "  package (cooling, derating curve) is a purchase item, and",
             "  the derated hours are part of the energy model (ch 15)"]
    emit("a_envelope", lines)
    return dict(t_min=t_min, t_max=t_max, rho_hot=rho_hot)


# ------------------------------------------------ certification evidence
EVIDENCE = [
    ("design evaluation", "loads, control, structures", "certification body"),
    ("power performance", "power curve test", "accredited test lab"),
    ("mechanical loads", "load measurement campaign", "accredited test lab"),
    ("acoustic noise", "noise measurement", "accredited test lab"),
    ("blade", "full-scale static, fatigue tests", "blade test lab"),
    ("gearbox", "prototype and run-in tests", "maker, witnessed"),
    ("manufacturing", "factory and quality system", "certification body"),
    ("project", "site conditions against design", "certification body"),
]


def evidence() -> None:
    lines = ["type and project certification: evidence and who gives it",
             "  evidence             what                               from"]
    for a, b, c in EVIDENCE:
        lines.append(f"  {a:20s} {b:34s} {c}")
    lines += ["  a type certificate says the design was shown to meet its",
              "  class; the project certificate says this site fits the",
              "  class; neither says each unit was built right - that is",
              "  the manufacturing evaluation and the units' own records"]
    emit("a_evidence", lines)


# ------------------------------------------------ critical interfaces
INTERFACES = [
    ("blade - hub", "bolt circle, flatness, preload", "blade, hub"),
    ("hub - main shaft", "flange fit, bolt preload", "hub, nacelle"),
    ("gearbox - bedplate", "torque arm elastomers, alignment", "nacelle"),
    ("gearbox - generator", "coupling alignment", "nacelle"),
    ("nacelle - tower", "yaw flange flatness, bolt circle", "nacelle, tower"),
    ("tower sections", "flange flatness, bolts", "tower (ch 30)"),
    ("tower - foundation", "anchor cage, grout, levelness", "civil (ch 30)"),
]


def interfaces() -> None:
    lines = ["critical interfaces: what is checked and who owns it",
             "  interface             check                                owners"]
    for a, b, c in INTERFACES:
        lines.append(f"  {a:21s} {b:36s} {c}")
    lines += ["  each interface has two owners and one drawing; the check is",
              "  done where the two parts first meet - in a factory for",
              "  blade inserts, on the site for the tower flanges - and its",
              "  record names both parts' serials"]
    emit("a_interfaces", lines)


if __name__ == "__main__":
    tree()
    root_joint()
    drivetrain()
    allocation()
    replacements()
    envelope()
    evidence()
    interfaces()
