"""Chapter 26 - manufacture and test evidence of the protection hardware:
CT ratio error from a test, the knee point found in a magnetising curve,
breaker timing and contact resistance records, the test families of a
relay, a panel FAT punch list, and what each factory controls and
records (purpose and records only; methods belong to the makers and
qualified test staff).

Run from the project root:   python -m companion.ch26.examples_k
Writes companion/ch26/expected/k_*.txt. Teaching limits A-331 to A-335:
the real limits come from the product standards and the contract.
"""
from __future__ import annotations

from companion.ch26.common import emit


def ct_ratio() -> None:
    kn = 600 / 1
    lines = ["CT ratio error from a routine test (600/1, teaching limit 1 %):",
             "  primary A   secondary A   error %   within"]
    for ip, i_s in ((600.0, 0.9985), (300.0, 0.4991), (60.0, 0.0985)):
        e = (kn * i_s - ip) / ip * 100
        lines.append(f"  {ip:9.0f}   {i_s:11.4f}   {e:7.2f}   {'yes' if abs(e) <= 1.0 else 'NO'}")
    lines += ["  error = (Kn x Is - Ip) / Ip; a protection CT's accuracy",
              "  matters most at fault currents (its accuracy limit factor),",
              "  a metering CT's at load currents - two cores, two classes,",
              "  each proved by its own test record"]
    emit("k_ratio", lines)


# [start: knee]
CURVE = [(10, 0.004), (50, 0.008), (100, 0.012), (150, 0.016), (200, 0.022),
         (230, 0.030), (250, 0.045), (265, 0.070), (275, 0.110), (285, 0.180)]


def knee(points: list) -> tuple:
    """First point where a 10 % rise in voltage needs a 50 % rise in
    magnetising current (interpolating the measured curve)."""
    for (v, i) in points:
        v2 = 1.1 * v
        for (va, ia), (vb, ib) in zip(points, points[1:]):
            if va <= v2 <= vb:
                i2 = ia + (ib - ia) * (v2 - va) / (vb - va)
                if i2 >= 1.5 * i:
                    return v, i
    return None
# [end: knee]


def magnetising() -> None:
    v, i = knee(CURVE)
    lines = ["knee point from a CT magnetising-curve test (teaching data):",
             "  voltage V   current A"]
    lines += [f"  {a:9d}   {b:9.3f}" for a, b in CURVE]
    lines += [f"  knee (10 % more volts needs 50 % more amps): {v} V at {i:.3f} A",
              "  lesson A's feeder CT needs 188 V: this core has margin;",
              "  the curve in the test record is the evidence, not the",
              "  nameplate"]
    emit("k_knee", lines)


def breaker() -> None:
    recs = {"=WS1-Q1": dict(open=(28, 29, 31), res=(35, 36, 37)),
            "=WS2-Q1": dict(open=(29, 30, 42), res=(34, 36, 35)),
            "=PVF3-Q1": dict(open=(28, 28, 29), res=(36, 35, 58))}
    lim_open, lim_spread, lim_res = 35, 3.3, 45
    lines = ["breaker timing and contact-resistance records (teaching limits:",
             f"  opening <= {lim_open} ms, pole spread <= {lim_spread} ms,"
             f" resistance <= {lim_res} uOhm)",
             "  breaker     opening ms     spread   resistance uOhm   result"]
    for name, r in recs.items():
        o, res = r["open"], r["res"]
        spread = max(o) - min(o)
        bad = [k for k, ok in (("slow pole", max(o) <= lim_open),
                               ("spread", spread <= lim_spread),
                               ("contact", max(res) <= lim_res)) if not ok]
        lines.append(f"  {name:10s} {str(o):14s} {spread:6d}   {str(res):15s}   "
                     f"{', '.join(bad) if bad else 'pass'}")
    lines += ["  a slow pole points to the mechanism (lubrication, a",
              "  spring, a coil); a high contact resistance to a loose or",
              "  worn joint that will heat under load - both go back to the",
              "  maker's checks before energising; the timing also enters",
              "  the breaker-failure timer of lesson E"]
    emit("k_breaker", lines)


def relay_tests() -> None:
    fam = [("type tests (once per design)", "EMC immunity and emission, insulation,",
            "climatic, mechanical, functional accuracy - certificates"),
           ("routine tests (every unit)", "functions, calibration of inputs,",
            "self-supervision - the unit's test report"),
           ("firmware and configuration", "version recorded, checksum, release",
            "notes - part of the configuration record"),
           ("panel FAT (the assembly)", "wiring, functions, trips, interlocks",
            "with the project's schematics - FAT record and punch list")]
    lines = ["test families of a protection relay and its panel:"]
    for a, b, c in fam:
        lines += [f"  {a}:", f"    {b}", f"    {c}"]
    lines += ["  the type test proves the design; the routine test proves",
              "  this unit; the FAT proves this panel as wired for Plant P"]
    emit("k_relaytests", lines)


def fat() -> None:
    punch = [("terminal X2:14 wired to X2:41", "B", "closed"),
             ("CT shorting link left open on core 2", "A", "closed"),
             ("trip relay contact on wrong coil", "A", "closed"),
             ("setting file rev A loaded, rev B approved", "A", "closed"),
             ("ferrule labels missing on 12 wires", "C", "closed"),
             ("+H03 trip coil 2 link X5:7 missing", "B", "open"),
             ("door earth strap missing", "C", "open")]
    lines = ["panel FAT punch list (A must close before shipping, B before",
             "  energising, C at completion):",
             "  item                                       class   status"]
    lines += [f"  {a:42s}   {b:5s}   {c}" for a, b, c in punch]
    open_a = [p for p in punch if p[1] == "A" and p[2] != "closed"]
    lines += [f"  open class A items: {len(open_a)} -> panel may ship: {'yes' if not open_a else 'no'}",
              f"  open B and C items travel with the panel: {sum(p[2] == 'open' for p in punch)}",
              "  an open CT link on site would put the CT secondary open -",
              "  dangerous voltages - which is why it is a class A item",
              "  the missing coil-2 link was classed B: a backup trip path",
              "  that does not exist is a protection defect and should have",
              "  been class A (lab E shows what followed)"]
    emit("k_fat", lines)


def flows() -> None:
    f = [("current transformer", "core, winding, insulation, cure",
          "material certificates, routine test record"),
         ("voltage transformer", "core, winding, insulation, cure",
          "routine tests, ratio and polarity"),
         ("breaker", "interrupter, mechanism, run-in operations",
          "timing, resistance, voltage tests"),
         ("relay", "boards, firmware load, burn-in, calibration",
          "routine report, firmware version"),
         ("panel", "frame, wiring to drawings, labels, FAT",
          "wiring check, FAT record, punch list")]
    lines = ["manufacture of the protection hardware (purpose and records):"]
    for a, b, c in f:
        lines += [f"  {a}:", f"    steps: {b}", f"    records: {c}"]
    lines += ["  the detailed processes are the makers' (ch 43 for the",
              "  electrical factories); the plant asks for the records"]
    emit("k_flows", lines)


if __name__ == "__main__":
    ct_ratio()
    magnetising()
    breaker()
    relay_tests()
    fat()
    flows()
