"""Chapter 5 - numerical answers of the end-of-chapter problems.

Run from the project root:   python -m companion.ch05.solutions
Writes companion/ch05/expected/solutions.txt; each line starts with the problem id.
Data pack 1.1.0 (synthetic); money in fictional units.
"""
from __future__ import annotations

import math
import re
import zoneinfo
from datetime import date, datetime, timedelta, timezone

import numpy as np

from companion.ch05 import step1_convert as s1, step3_model as m
from companion.ch05.common import emit
from plantp import assets, datapack, dataio, dispatch, losses, money

OUT: list[str] = []


def p(pid: str, text: str) -> None:
    OUT.append(f"{pid}: {text}")


def level_1() -> None:
    p("P01", f"2023 = {2023:b} (binary) = 0x{2023:X}")
    p("P02", f"0x1F4 = {0x1F4}; needs {0x1F4.bit_length()} bits")
    p("P03", f"0x8000 signed {dataio.to_int16(0x8000)}; 0xFFFE signed "
             f"{dataio.to_int16(0xFFFE)}")
    p("P04", f"(0x42C8, 0x0000) = {dataio.decode_float32(0x42C8, 0)}; (0x3F00, 0x0000) = "
             f"{dataio.decode_float32(0x3F00, 0)}")
    bits = [k for k in range(16) if 45 >> k & 1]
    p("P05", f"45 = {45:016b}: bits {bits}")
    w = "نیرو"                       # the word niru
    try:
        w.encode("cp1256")
        cp = "encodable"
    except UnicodeEncodeError:
        cp = "fails at U+06CC (no Persian yeh in that code page)"
    w_ar = w.replace("ی", "ي")
    p("P06", f"4 letters: UTF-8 {len(w.encode('utf-8'))} bytes; Windows-1256 {cp};")
    OUT.append(f"     with Arabic yeh instead: {len(w_ar.encode('cp1256'))} bytes")
    t = datetime.fromisoformat("2023-04-03T14:10:00+04:00")
    p("P07", f"{t.astimezone(timezone.utc).isoformat()}")
    k = datetime(2023, 6, 1, 12, 30, tzinfo=timezone(timedelta(hours=4.5)))
    p("P08", f"Kabul 12:30 = {k.astimezone(timezone.utc):%H:%M} UTC = "
             f"{k.astimezone(timezone(timedelta(hours=4))):%H:%M} Plant P")
    p("P09", f"36 km/h = {s1.convert(36, 'km/h', 'm/s'):g} m/s; 950 hPa = "
             f"{s1.convert(950, 'hPa', 'kPa'):g} kPa; 3.6e9 J = "
             f"{s1.convert(3.6e9, 'J', 'MWh'):g} MWh")
    p("P13", f"17 // 5 = {17 // 5}; 17 % 5 = {17 % 5}; 2 ** 10 = {2 ** 10}")
    a, b, c = (int(x) for x in "2.3.1".split("."))
    p("P15", f"from 2.3.1: fix {a}.{b}.{c + 1}; feature {a}.{b + 1}.0; break {a + 1}.0.0")
    vs = ["1.2.0", "1.10.0", "1.9.3"]
    p("P16", f"{sorted(vs, key=lambda v: tuple(map(int, v.split('.'))))} "
             f"(as text: {sorted(vs)})")
    tags = ["PLP-WTG-07-GEN", "PLP-WTG-7-GEN", "PLP-XYZ-01", "PLP-INV-10",
            "PLP-MET-01-ANM2", "plp-swg-01"]
    p("P20", ", ".join(f"{t} {'ok' if assets.TAG_PATTERN.match(t) else 'no'}"
                       for t in tags))
    p("P21", f"vector mean of 10 and 350 = {dataio.vector_mean_deg([10, 350]):.1f} deg; "
             f"arithmetic {(10 + 350) / 2:.0f} deg")
    v = np.array([5.0, 9.0])
    p("P23", f"mean(v^3) = {np.mean(v ** 3):.0f}, (mean v)^3 = {v.mean() ** 3:.0f}, "
             f"ratio {np.mean(v ** 3) / v.mean() ** 3:.3f}")


def level_2() -> None:
    p("P26", f"float32 spacing near 1e6: {np.spacing(np.float32(1e6))}; near 1e9: "
             f"{np.spacing(np.float32(1e9))}")
    days = 2 ** 32 / (60e6 * 0.337 * 24)
    p("P27", f"60 MW at CF 0.337 fills a 32-bit Wh counter in {days:.1f} days")
    before, after = 4_294_960_000, 12_705
    e = after - before + 2 ** 32
    p("P28", f"{after:,} - {before:,} + 2^32 = {e:,} Wh = {e / 1e6:.6f} MWh")
    p("P29", f"12 x 5 MW x 8760 h x 0.337 = {60 * 8760 * 0.337 / 1000:.1f} GWh")
    tc = float(m.cell_temperature(900, 30))
    fac = 1 - 0.0035 * (tc - 25)
    p("P30", f"T_cell = 30 + 25/800 x 900 = {tc:.2f} C; factor {fac:.4f}")
    p("P31", f"P_AC = 60 x 0.9 x {fac:.4f} x 0.90 x 0.98 = {float(m.pv_ac_mw(900, 30)):.2f} MW")
    rho = float(m.air_density(879.0, 16.8))
    p("P32", f"rho = 87900 / (287.05 x 289.95) = {rho:.4f} kg/m3")
    curve = datapack.load_power_curve()
    veq = 10 * (rho / 1.225) ** (1 / 3)
    pk = float(np.interp(veq, curve["wind_speed_ms"], curve["power_kw"]))
    p10 = float(np.interp(10, curve["wind_speed_ms"], curve["power_kw"]))
    p("P33", f"v_eq = 10 x ({rho:.4f}/1.225)^(1/3) = {veq:.3f} m/s; P = {pk:.0f} kW "
             f"(at 1.225: {p10:.0f} kW)")
    i = float(losses.current_a(25, 33, 0.95))
    lc = float(losses.cable_loss_mw(25, 33, 0.95, 0.10, 6.0))
    p("P34", f"I = {i:.1f} A; loss in 6 km at 70 C = {lc * 1e3:.1f} kW")
    lt = float(losses.transformer_loss_mw(60, 0.95, 120, 0.060, 0.400))
    p("P35", f"S = {60 / 0.95:.2f} MVA; loss = 60 + 400 x ({60 / 0.95:.2f}/120)^2 = "
             f"{lt * 1e3:.1f} kW")
    crf = money.capital_recovery(0.06, 15)
    p("P36", f"CRF(6 %, 15) = {crf:.5f}; service on 70 million = {70 * crf:.3f} million/yr")
    p("P37", f"DSCR = 10.0 / {70 * crf:.3f} = {10.0 / (70 * crf):.3f}")
    cash = [-100.0] + [12.0] * 25
    p("P38", f"NPV(7 %) = {money.npv(0.07, cash):.2f} million; IRR = "
             f"{100 * money.irr(cash):.2f} %")
    eta = math.sqrt(0.86)
    soc = 20 * eta
    p("P39", f"after 1 h at 20 MW: {soc:.2f} MWh stored; at 20 MW out it lasts "
             f"{soc * eta / 20:.3f} h")
    p("P40", f"gain per MWh delivered = 100 - 30 / 0.86 = {100 - 30 / 0.86:.1f} u")
    p("P41", f"annual GHI = 222 x 8760 / 1000 = {222 * 8760 / 1000:.1f} kWh/m2 "
             "(valid only if gaps are random)")
    p("P42", f"recovery = 8100 / 8760 = {100 * 8100 / 8760:.2f} %")
    order = math.log2(0.5 / 0.031)
    p("P43", f"order = log2(0.5/0.031) = {order:.2f}; error at 8 elements ~ "
             f"{0.031 / 2 ** order:.4f} %")
    u = [8000 * 0.04] * 12
    p("P45", f"correlated +- {sum(u):,.0f} MWh; independent +- {math.sqrt(sum(x * x for x in u)):,.1f} MWh")
    p("P46", f"cycles = 10 000 / {eta:.4f} / 32 = {10_000 / eta / 32:.0f}")
    berlin = zoneinfo.ZoneInfo("Europe/Berlin")
    a = datetime(2023, 3, 26, tzinfo=berlin).astimezone(timezone.utc)
    b = datetime(2023, 3, 27, tzinfo=berlin).astimezone(timezone.utc)
    p("P47", f"26 March 2023 in Europe/Berlin: {(b - a) / timedelta(hours=1):.0f} h = "
             f"{int((b - a) / timedelta(minutes=10))} ten-minute records")


CONFIG_P50 = """
run_id: PLP-X
data_release: "1.1"
scenario: S1
pv: {dc_mwp: 60, ac_mw: 50, noct_c: 45, gamma_per_k: -0.0035, k_other: 0.9,
     eta_inverter: 98}
wind: {turbines: 12, loss: 0.12, density_correction: true}
export_limit_mw: 100
outputs: {folder: out}
"""


def level_2b() -> None:
    import yaml
    from plantp import schema
    cfg = yaml.safe_load(CONFIG_P50)
    for issue in schema.check(cfg, schema.RUN_SCHEMA):
        p("P50", issue)
    p("P50", f"scenario {cfg['scenario']} without a bess block passes the schema")


def level_3() -> None:
    t = datetime.fromisoformat("2023-04-03T08:00:00+00:00")
    p("P51", f"{t.astimezone(timezone(timedelta(hours=4))):%Y-%m-%d %H:%M}+04:00 local; "
             f"{float('12345,6'.replace(',', '.')) / 1000:.4f} MWh; availability "
             f"{float('98,5'.replace(',', '.')) / 100:.3f}")
    end = datetime(2023, 4, 5, 0, 0, tzinfo=timezone(timedelta(hours=4)))
    start = (end - timedelta(minutes=10)).astimezone(timezone.utc)
    p("P52", f"interval start {start.isoformat()}")
    rows = [dict(tag="PLP-PLT-01", parent="", description="Plant P", criticality="A"),
            dict(tag="PLP-INV-02", parent="PLP-PVB-02", description="Inverter 2",
                 criticality="A"),
            dict(tag="PLP-PVB-02", parent="PLP-PLT-01", description="", criticality="B"),
            dict(tag="PLP-TRF-1", parent="PLP-SUB-01", description="Trafo",
                 criticality="A"),
            dict(tag="PLP-MET-01-ANM", parent="PLP-MET-01", description="Anemometer",
                 criticality="B", installed="2025-03-01", commissioned="2025-02-01")]
    for issue in assets.validate_register(rows):
        p("P53", issue)
    vals = [7.1, 7.4, -9999, 7.0, 7.3, 7.2]
    good = [v for v in vals if v != -9999]
    p("P59", f"valid {len(good)} of 6; mean {sum(good) / len(good):.2f} m/s (with the "
             f"sentinel: {sum(vals) / 6:.1f})")
    p("P62", f"PV on DC basis: 96.43 / (60 x 8.76) = {96.43 / (60 * 8.76):.4f}")
    full = 4 * float(losses.cable_loss_mw(25, 33, 0.95, 0.10, 6.0))
    half = 4 * float(losses.cable_loss_mw(12.5, 33, 0.95, 0.10, 6.0))
    p("P63", f"cable loss at 100 MW {full:.3f} MW ({full:.2f} %); at 50 MW {half:.3f} MW "
             f"({100 * half / 50:.2f} %)")
    p("P64", f"NPV swing 30.54 million for +-5 u/MWh -> {30.54 / 10:.3f} million per u/MWh")
    start_d = date(2025, 7, 1)
    p("P67", f"warranty from {start_d} for 2 years ends {start_d.replace(year=2027)}")


def level_4_5() -> None:
    gen = np.array([30.0] * 24)
    r = dispatch.rule_based_shift(gen, range(10, 14), range(18, 22), 20, 32, 0.86, 100)
    p("P78", f"charged {r.charge_mw.sum():.2f} MWh, delivered {r.discharge_mw.sum():.2f} MWh, "
             f"left {r.soc_mwh[-1]:.2f} MWh")
    cf = money.project_cash_flow(273_520, 45.0, 100e6, 2.75e6, 25, 0.005, 0.70, 0.06, 15)
    p("P86", f"price 45: DSCR year 1 {cf['dscr'][1]:.3f}, minimum "
             f"{min(x for x in cf['dscr'][1:16]):.3f}")
    cf = money.project_cash_flow(273_520, 50.0, 100e6, 2.75e6, 25, 0.005, 0.75, 0.06, 15)
    p("P87", f"75 % debt: DSCR year 1 {cf['dscr'][1]:.3f}, minimum "
             f"{min(x for x in cf['dscr'][1:16]):.3f}")
    r20 = 0.10 * (1 + 0.00403 * 70)
    p("P88", f"R at 90 C / R at 70 C = {(1 + 0.00403 * 70) / (1 + 0.00403 * 50):.4f}")
    p("P89", f"loss ratio for 240 -> 300 mm2 (R ~ 1/A): {240 / 300:.2f}; R20 {r20:.4f} "
             "ohm/km at 90 C for 0.10 at 20 C")


if __name__ == "__main__":
    level_1()
    level_2()
    level_2b()
    level_3()
    level_4_5()
    emit("solutions", OUT)
