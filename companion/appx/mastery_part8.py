"""Appendix X - answers of the Part VIII diagnostic mastery test (chapters
38-50): for each design record, purchase, factory test, site record or
acceptance, what it proves, the sourced numbers behind it, who owns it and
the evidence that closes it - with the numbers computed from the chapters'
companion code.

Run from the project root:   python -m companion.appx.mastery_part8
Writes companion/appx/expected/mastery_part8.txt.
Data pack 1.1.0 (synthetic), S0 unless stated; decisions D-042 to D-054.
Values marked (test) are used only here.
"""
from __future__ import annotations

from companion.appx.common import emit
from plantp import cablemfg, cellmfg, civilmfg, commissioning, construction
from plantp import convmfg, docctl, hwmfg, procure, quality, turbinemfg, xfmrdesign

OUT: list[str] = []


def p(pid: str, text: str) -> None:
    OUT.append(f"{pid}: {text}")


def information_purchase_quality() -> None:
    ev = docctl.earned_value(1_200.0, 1_020.0, 1_150.0, 4_000.0)
    p("M109", f"design hours PV 1,200, EV 1,020, AC 1,150, BAC 4,000 (test): SPI"
              f" {ev['spi']:.2f}, CPI {ev['cpi']:.2f}, estimate at completion"
              f" {ev['eac']:,.0f} h - late and over, both from the same records")
    ld, capped = procure.ld_amount(9, 0.005, 2_072.0, 0.10)
    p("M110", f"9 weeks late at 0.5 % a week on 2,072 k u with a 10 % cap (test):"
              f" {ld:.0f} k u, cap reached: {capped} - damages are a ceiling,"
              " not a cure for the plant's lost energy")
    pa = quality.p_accept(50, 1, 0.04)
    p("M111", f"sample 50, accept on at most 1 defective, lot 4 % defective:"
              f" accepted {pa:.0%} of the time - the OC curve is read before a"
              " plan is agreed")
    sc = docctl.detect_chance(120, 6, 20)
    p("M112", f"20 of 120 documents checked, 6 wrong (test): chance of finding at"
              f" least one {sc:.0%} - a sample finds a problem, it does not prove"
              " its absence")


def factory_products() -> None:
    t = turbinemfg.insert_tension(42e6, 128, 4.2)
    p("M113", f"blade root moment 42 MNm (test) on 128 inserts on a 4.2 m circle:"
              f" largest insert tension {t / 1e3:,.0f} kN by 4M/(nD)")
    ws = xfmrdesign.water_solubility_ppm(60.0)
    p("M114", f"oil saturation water at 60 C (teaching form): {ws:.0f} ppm - the"
              " relative saturation, not the ppm alone, is read in a transformer")
    tj = convmfg.tj(988.0, 0.028, 0.0156, 0.016, 45.0)
    p("M115", f"IGBT position 988 W through 0.028 + 0.0156 + 0.016 K/W to 45 C"
              f" coolant: junction {tj:.1f} C (ch 9, ch 44)")
    k = cellmfg.k_value(3.3105, 3.3062, 14.0)
    p("M116", f"rest test 3.3105 -> 3.3062 V in 14 days (test): K = {k:.2f} mV a"
              " day - a leaker is read against the lot's distribution, not a"
              " fixed number")


def cables_civil_hardware() -> None:
    r = cablemfg.r_to_20(0.0812, 32.0)
    p("M117", f"conductor 0.0812 ohm/km measured at 32 C, aluminium: {r:.4f} ohm/km"
              " at 20 C - compared with the standard's maximum, not the reading")
    c = civilmfg.cev(0.17, 1.45, 0.05, 0.02, 0.01, 0.05, 0.10)
    p("M118", f"plate with C 0.17, Mn 1.45, Cr 0.05, Mo 0.02, V 0.01, Ni 0.05,"
              f" Cu 0.10 (test): CEV {c:.2f} against the order's 0.43")
    m = civilmfg.bar_mass(25.0)
    p("M119", f"25 mm bar: {m:.2f} kg/m by d^2/162 - the BBS mass is checked line"
              " by line against the delivery tickets")
    rss, worst = hwmfg.chain_error(0.2, 0.2, 0.5)
    p("M120", f"metering chain of 0.2, 0.2 and 0.5 % classes: {rss:.2f} % RSS,"
              f" {worst:.1f} % worst case - the site test at low load closes it")


def site_and_acceptance() -> None:
    tasks = {"a": (3, [], "x", 1), "b": (4, ["a"], "y", 0), "c": (2, [], "x", 0),
             "d": (2, ["b", "c"], "x", 1)}
    plan = construction.serial_schedule(tasks, {"x": 1, "y": 1})
    end = max(v[2] for v in plan.values())
    p("M121", f"four packages with one crew of each kind and hold days (test):"
              f" finished on day {end:.0f}; the hold after 'a' sits on the path")
    prog = construction.rules_of_credit({"m": 0.6, "t": 0.2, "i": 0.2},
                                        {"m": 1.0, "t": 0.5, "i": 0.0})
    p("M122", f"rules of credit 60/20/20, steps done 100/50/0 %: earned {prog:.0%},"
              " not the 100 % a 'mounted' count reports")
    v, i = commissioning.string_expected(26, 900.0, 40.0)
    p("M123", f"string of 26 PVM-550 at 900 W/m2 and 40 C: expected Voc {v:,.0f} V,"
              f" Isc {i:.2f} A; a string 49 V short is one module short")
    share, miss = commissioning.cause_effect(
        {"smoke A": {"alarm", "HVAC stop"}, "call point": {"alarm", "fire service"}},
        {("smoke A", "alarm"), ("call point", "alarm"), ("call point", "fire service")})
    miss_txt = ", ".join(f"{c} -> {e}" for c, e in miss)
    p("M124", f"cause-and-effect pairs proven: {share:.0%}; never proven: {miss_txt} -"
              " a function nobody has seen work; no live discharge to prove it")


if __name__ == "__main__":
    information_purchase_quality()
    factory_products()
    cables_civil_hardware()
    site_and_acceptance()
    emit("mastery_part8", OUT)
