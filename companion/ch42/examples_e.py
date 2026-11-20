"""Chapter 42, lesson E - manufacturing engineering of the turbine supply
chain: supplier tiers and the longest lead time, first-article
capability from few parts, torque operations and human error, storage
interventions, blade damage categories and where they are repaired,
weather windows for field repair from the data pack, and the serial
defect trigger.

Run from the project root:   python -m companion.ch42.examples_e
Writes companion/ch42/expected/e_*.txt and diagrams/data/ch42-*.csv.
Teaching values (A-456, A-457).
"""
from __future__ import annotations

import math
import random

from companion.ch42.common import csv, emit
from plantp import datapack

# ------------------------------------------------ supplier tiers
CHAIN = [  # part, tier-2 input, weeks tier 2, weeks tier 1, weeks assembly
    ("main bearing", "forged rings", 26, 14, 6),
    ("gearbox", "gear forgings, bearings", 22, 18, 6),
    ("hub", "casting pattern, iron", 12, 10, 6),
    ("blade", "glass, resin, balsa", 6, 8, 4),
    ("generator", "electrical steel, copper", 10, 12, 6),
    ("tower", "plate", 8, 10, 0),
]


def tiers() -> dict[str, int]:
    out = {}
    lines = ["supplier tiers and lead time to a turbine ready to ship (teaching)",
             "  part           tier-2 input              weeks t2 + t1 + nacelle"]
    for part, inp, w2, w1, wa in CHAIN:
        tot = w2 + w1 + wa
        out[part] = tot
        lines.append(f"  {part:14s} {inp:25s} {w2:3d} + {w1:2d} + {wa}"
                     f" = {tot:3d}")
    top = max(out.values())
    crit = " and ".join(k for k, v in out.items() if v == top)
    lines += [f"  the {crit} set the turbine's lead time: {top} weeks",
              "  the longest chain is often two tiers down, at a forge the",
              "  turbine maker never sees; reserving forging capacity at",
              "  award (ch 39, slots) and a qualified second forge cut the",
              "  risk more than pressing the final assembler"]
    emit("e_tiers", lines)
    return out


# ------------------------------------------------ first-article capability
def first_article(cpk: float = 1.50) -> dict[int, float]:
    z = 1.645
    out = {}
    lines = [f"capability of a new blade mould from its first blades (observed "
             f"Cpk {cpk})",
             "  blades measured   95 % lower bound   proves 1.33?"]
    for n in (5, 10, 30, 100):
        low = cpk - z * math.sqrt(1 / (9 * n) + cpk ** 2 / (2 * (n - 1)))
        out[n] = low
        lines.append(f"  {n:15d}   {low:16.2f}   "
                     f"{'yes' if low >= 1.33 else 'no'}")
    lines += ["  five blades cannot prove a capability, however good they",
              f"  look, and even a hundred give only {out[100]:.2f}: the first",
              "  article proves the drawing is met; the process is released",
              "  on a plan that keeps measuring, and a target of 1.33 needs",
              "  an observed Cpk well above it (ch 40, capability interval)"]
    emit("e_first", lines)
    return out


# ------------------------------------------------ torque operations
OPS = [("blade root inserts (3 x 96)", 288), ("hub to main shaft", 90),
       ("pitch bearings (3 x 120)", 360), ("yaw bearing", 140),
       ("tower flanges (3 x 150)", 450), ("anchor cage", 160)]


def torque(miss: float = 1 / 2000, logged: float = 1 / 200000):
    total = sum(n for _, n in OPS)
    lines = ["tightening operations on one turbine (teaching counts)"]
    for name, n in OPS:
        lines.append(f"  {name:28s} {n:5d}")
    lines += [f"  total {total:,} a turbine; {total * 12:,} for the plant",
              f"  a person missing one in {1 / miss:,.0f}: "
              f"{total * 12 * miss:.1f} loose joints expected",
              f"  tools that log torque and angle per bolt: "
              f"{total * 12 * logged:.2f}",
              "  a missed bolt is a fatigue crack waiting: the logged record",
              "  per bolt is the evidence, and the 500-hour re-tension of",
              "  the commissioning plan (ch 50) catches what is left"]
    emit("e_torque", lines)
    return dict(total=total, manual=total * 12 * miss, logged=total * 12 * logged)


# ------------------------------------------------ storage interventions
def storage(months: int = 9) -> dict[str, int]:
    tasks = [("nacelle main shaft turned (bearing marks)", 1),
             ("desiccant and humidity check", 1),
             ("generator heater and insulation check", 3),
             ("blade covers and supports", 3),
             ("gearbox oil sample", 6)]
    out = {}
    lines = [f"components stored {months} months at the port or site (teaching)",
             "  task                                        every   times"]
    for name, every in tasks:
        k = months // every
        out[name] = k
        lines.append(f"  {name:42s} {every:3d} mo  {k:5d}")
    lines += ["  a bearing that does not turn for months gets marks where",
              "  the rollers sit and vibration shakes them (false",
              "  brinelling): storage is a process with a record, and a",
              "  missed turn is a nonconformity, not a detail"]
    emit("e_storage", lines)
    return out


# ------------------------------------------------ blade damage and repair
CATS = [  # category, description, where repaired, days, k u
    (1, "coating scratch", "rope access", 0.5, 2),
    (2, "leading-edge erosion into the laminate", "rope access", 2, 8),
    (3, "skin damage, no structure", "rope or platform", 4, 20),
    (4, "damage reaching a cap or web", "ground, crane", 20, 180),
    (5, "structural crack or root damage", "replace blade", 60, 900),
]


def damage(seed: int = 4207, blades: int = 36):
    rng = random.Random(seed)
    w = [0.55, 0.30, 0.10, 0.04, 0.01]
    counts = {c[0]: 0 for c in CATS}
    for _ in range(blades):
        r, acc = rng.random(), 0.0
        for c, p in zip(counts, w):
            acc += p
            if r < acc:
                counts[c] += 1
                break
    lines = [f"inspection of {blades} blades after three years (teaching damage)",
             "  cat  description                              repair           count"]
    cost = days = 0.0
    for cat, desc, where, d, k in CATS:
        n = counts[cat]
        cost += n * k
        days += n * d
        lines.append(f"  {cat:3d}  {desc:40s} {where:16s} {n:4d}")
    lines += [f"  repair cost {cost:,.0f} k u and {days:.0f} turbine-days down",
              "  categories 1-3 are field repairs within the maker's limits;",
              "  4-5 need the designer and usually a crane: the category",
              "  is set by an inspector against the maker's damage manual,",
              "  and a field repair is valid only with its record"]
    emit("e_damage", lines)
    return dict(cost=cost, days=days, **{str(k): v for k, v in counts.items()})


# ------------------------------------------------ field repair windows
def windows(t_lo: float = 10.0, t_hi: float = 35.0, v_max: float = 12.0):
    h = datapack.load_hourly()
    ok = ((h["t_air_c"] >= t_lo) & (h["t_air_c"] <= t_hi)
          & (h["ws_100m_ms"] <= v_max) & (h["ghi_wm2"] > 0))
    month = [1 + min(11, k // 730) for k in range(len(h))]
    out = {m: int(sum(1 for mm, o in zip(month, ok) if mm == m and o))
           for m in range(1, 13)}
    csv("ch42-windows.csv", "month,hours", list(out.items()))
    best, worst = max(out, key=out.get), min(out, key=out.get)
    lines = [f"daylight hours for a composite field repair: {t_lo:.0f} to "
             f"{t_hi:.0f} C, hub wind <= {v_max:.0f} m/s",
             "  (teaching limits; the resin's own limits decide)",
             "  month " + " ".join(f"{m:4d}" for m in range(1, 13)),
             "  hours " + " ".join(f"{out[m]:4d}" for m in range(1, 13)),
             f"  best month {best} ({out[best]} h), worst month {worst} "
             f"({out[worst]} h)",
             "  a resin cures only in its temperature band, and rope access",
             "  stops in wind: repair campaigns are planned for the months",
             "  the data allow, with the cure recorded like the factory's"]
    emit("e_windows", lines)
    return out


# ------------------------------------------------ serial defect trigger
def serial_defect(n: int = 36, k: int = 3):
    def p_ge(p):
        return 1 - sum(math.comb(n, j) * p ** j * (1 - p) ** (n - j)
                       for j in range(k))
    out = {p: p_ge(p) for p in (0.01, 0.03, 0.10)}
    lines = [f"serial defect clause: {k} or more of the same failure in {n} "
             "blades (teaching)",
             "  true failure share   chance the clause triggers"]
    for p, v in out.items():
        lines.append(f"  {p:18.0%}   {v:26.0%}")
    lines += ["  a clause that triggers by chance on a sound fleet is a",
              "  dispute; one that never triggers on a bad fleet is no",
              "  protection - the threshold is a sampling plan in a",
              "  contract and is judged by the same OC curve (ch 39)"]
    emit("e_serial", lines)
    return out


if __name__ == "__main__":
    tiers()
    first_article()
    torque()
    storage()
    damage()
    windows()
    serial_defect()
