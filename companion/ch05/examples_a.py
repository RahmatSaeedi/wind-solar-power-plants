"""Chapter 5, section A - data literacy: numbers in bits, text encodings, CSV, time,
sampling, missing values, units, metadata and quality flags, applied to Plant P.

Run from the project root:   python -m companion.ch05.examples_a
Writes companion/ch05/expected/a_*.txt and diagrams/data/ch05-*.csv.
Data: Plant P Reference Data Pack 1.1.0 (synthetic). Bit maps and counters are fictional.
"""
from __future__ import annotations

import csv as csvmod
import io
import math
import struct
import unicodedata
import zoneinfo
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import numpy as np
import tzdata

from companion.ch05.common import csv, emit
from plantp import assets, datapack, dataio, screening as sc
from plantp.units import Q


def numbers_in_bits() -> None:
    n = 2026
    emit("a_binary", [
        f"{n} in binary {n:b} ({n.bit_length()} bits), in hexadecimal 0x{n:X}",
        f"  check: 0x7EA = 7 x 256 + 14 x 16 + 10 = {7 * 256 + 14 * 16 + 10}",
        "one 16-bit register: unsigned 0 .. 65 535, signed (two's complement) "
        "-32 768 .. 32 767",
        f"  register 0xFF9C read as unsigned: {0xFF9C}; as signed: "
        f"{dataio.to_int16(0xFF9C)} (e.g. -100 kvar)",
        f"two registers 0x4148, 0x0000 as one float32 (high word first): "
        f"{dataio.decode_float32(0x4148, 0x0000)} (e.g. 12.5 m/s)",
        f"  the same registers in the wrong word order: "
        f"{dataio.decode_float32(0x0000, 0x4148):.3e} (nonsense, but no error)",
    ])
    word = 0b0000_0000_0010_0101
    bitmap = {0: "grid OK", 1: "local mode", 2: "yaw active", 3: "icing alarm",
              4: "pitch fault", 5: "power limited"}           # fictional bit map
    set_bits = [k for k in range(16) if word >> k & 1]
    emit("a_status", [
        f"status word {word} = 0x{word:04X} = {word:016b}",
        "  bits set: " + ", ".join(f"{k} ({bitmap[k]})" for k in set_bits),
        "  test one bit:  (word >> 3) & 1 = "
        f"{word >> 3 & 1} -> icing alarm {'ON' if word >> 3 & 1 else 'off'}",
        "the meaning of each bit comes ONLY from the device's register map (fictional here)",
    ])
    # an energy counter in Wh that wraps around at 2^32
    wrap = 2 ** 32
    p_kw, cf = 5000.0, 0.366
    days = wrap / (p_kw * 1000 * cf * 24)
    before, after = 4_294_000_000, 1_032_704
    diff = after - before
    emit("a_counter", [
        f"unsigned 32-bit counter in Wh: largest value {wrap - 1:,} Wh = "
        f"{(wrap - 1) / 1e6:,.0f} MWh",
        f"  a 5 MW turbine at capacity factor {cf} fills it in {days:.0f} days",
        f"reading before {before:,} Wh, after {after:,} Wh: naive difference {diff:,} Wh",
        f"  corrected for one wrap: {diff + wrap:,} Wh = {(diff + wrap) / 1e6:.3f} MWh",
        f"  plausible? one hour at 5 MW is at most 5.000 MWh: "
        f"{'yes' if (diff + wrap) / 1e6 <= 5 else 'no'}",
    ])


def floating_point() -> None:
    lines = [f"0.1 + 0.2 = {0.1 + 0.2!r}; equal to 0.3? {0.1 + 0.2 == 0.3}; "
             f"math.isclose: {math.isclose(0.1 + 0.2, 0.3)}"]
    e = 2.898e11                                       # Wh, Plant P's annual export
    lines += [f"spacing of float32 numbers near {e:.3e} Wh: {np.spacing(np.float32(e)):,.0f} Wh",
              f"  near 1 000 000: {np.spacing(np.float32(1e6))}; float64 near {e:.3e}: "
              f"{np.spacing(e):.2e} Wh"]
    inc = np.full(52_560, 5.0e6 / 6, dtype=np.float64)   # 10-min increments of 5 MW, Wh
    s64 = float(np.sum(inc))
    s32 = np.float32(0.0)
    for x in inc.astype(np.float32):
        s32 = np.float32(s32 + x)
    lines += ["a year of 10-minute energy increments of 5 MW (52 560 additions):",
              f"  float64 sum {s64 / 1e6:,.3f} MWh; float32 running sum {float(s32) / 1e6:,.3f} "
              f"MWh; error {100 * (float(s32) - s64) / s64:+.3f} %"]
    imp, exp_ = np.float32(289_812_345.6), np.float32(289_812_100.2)    # kWh meters
    lines += [f"difference of two large meter readings in float32: {float(imp - exp_):.1f} kWh "
              f"(true {289_812_345.6 - 289_812_100.2:.1f})"]
    emit("a_float", lines)
    money = 0.0
    for _ in range(10):
        money += 0.1
    emit("a_round", [
        f"adding 0.1 ten times in binary floating point: {money!r}",
        f"  sum([0.1] * 10) = {sum([0.1] * 10)!r} (Python 3.12+ compensates); "
        f"math.fsum: {math.fsum([0.1] * 10)!r}",
        f"ten times Decimal('0.1'): {sum([Decimal('0.1')] * 10)} (decimal arithmetic for money)",
        f"Python round(2.5) = {round(2.5)}, round(3.5) = {round(3.5)} (ties go to even)",
        f"formatting is not rounding the stored value: f'{{2/3:.2f}}' = {2 / 3:.2f}, the "
        f"value stays {2 / 3!r}",
    ])


def _in_cp1256(ch: str) -> bool:
    try:
        ch.encode("cp1256")
        return True
    except UnicodeEncodeError:
        return False


def text_encodings() -> None:
    word = "باد"
    u8, w1256 = word.encode("utf-8"), word.encode("cp1256")
    mojibake = u8.decode("cp1252", errors="replace")
    codes = " ".join(f"U+{ord(ch):04X}" for ch in mojibake)
    lines = [f"the word 'wind' (3 letters): UTF-8 {len(u8)} bytes {u8.hex(' ')}; "
             f"Windows-1256 {len(w1256)} bytes {w1256.hex(' ')}",
             f"  UTF-8 bytes read as Windows-1252 give {len(mojibake)} Latin-1 characters",
             f"    {codes} (mojibake, see the figure)",
             f"  UTF-8 byte-order mark: {'﻿'.encode('utf-8').hex(' ')}; Latin 'A' is 1 byte "
             f"({'A'.encode('utf-8').hex()}), the euro sign 3 bytes"]
    missing = [f"U+{ord(c):04X}" for c in ("ی", "ک")
               if not _in_cp1256(c)]
    lines += [f"Windows-1256 has Arabic yeh U+064A but not Persian yeh: missing "
              f"{', '.join(missing)}", "  (old Persian files therefore store the "
              "Arabic letter)"]
    persian_digits = "۱۲۳۴"
    pd_codes = "..".join(f"U+{ord(ch):04X}" for ch in persian_digits[::3])
    lines += [f"Persian digits one to four ({pd_codes}): Python int() gives "
              f"{int(persian_digits)};", "  many other tools give an error or text"]
    y_fa, y_ar = "ی", "ي"
    a, b = "سیستم", "سيستم"
    lines += [f"Persian yeh U+{ord(y_fa):04X} and Arabic yeh U+{ord(y_ar):04X} look alike:",
              f"  'system' typed both ways equal? {a == b}; after normalising: "
              f"{assets.normalise_persian(a) == assets.normalise_persian(b)}",
              f"the word mi-shavad written with a zero-width non-joiner (U+200C) has "
              f"{len('می‌شود')} code",
              "  points: 5 letters + 1 invisible character"]
    composed = unicodedata.normalize("NFC", "é")
    lines += [f"'e' + combining accent: 2 code points; NFC form: {len(composed)} code point"]
    emit("a_encoding", lines)


def csv_pitfalls() -> None:
    text = ('tag,description,value\n'
            'PLP-TRF-01,"Transformer, 120 MVA",120\n'
            'PLP-SWG-01,"Panel ""A"" line-up",33\n')
    naive = [line.split(",") for line in text.splitlines()]
    proper = list(csvmod.reader(io.StringIO(text)))
    lines = ["naive split(',') of a quoted field:",
             f"  row 2 -> {len(naive[1])} pieces {naive[1]}",
             "csv.reader (quotes, doubled quotes, commas inside fields):",
             f"  row 2 -> {proper[1]}", f"  row 3 -> {proper[2]}"]
    euro = "time;energy_kwh\n2023-04-03T08:00:00Z;12345,6\n"
    rows = list(csvmod.reader(io.StringIO(euro), delimiter=";"))
    lines += [f"semicolon file with decimal comma: {rows[1]} -> float after replace: "
              f"{float(rows[1][1].replace(',', '.'))}"]
    serial = "1234567890123456789"
    lines += [f"a 19-digit serial number stored as a float: {int(float(serial))} "
              f"(last digits lost; floats carry 15 to 17 significant digits)",
              "leading zeros of '007' are lost when the column is read as a number: "
              f"{int('007')}",
              "values such as '1-2', '3E5' or 'MAR1' may be converted to dates or numbers "
              "by spreadsheet programs; import such columns as text"]
    emit("a_csv", lines)


def time_and_zones() -> None:
    t = datetime(2023, 6, 21, 12, 0, tzinfo=timezone(timedelta(hours=4)))
    lines = [f"Plant P noon: {t.isoformat()}  =  {t.astimezone(timezone.utc).isoformat()}"]
    for zone in ("Asia/Tehran", "Asia/Kabul", "Asia/Dushanbe"):
        z = zoneinfo.ZoneInfo(zone)
        lines.append(f"  in {zone:14s} {t.astimezone(z).isoformat()}")
    lines.append(f"IANA time-zone database {tzdata.IANA_VERSION} (Python tzdata package):")
    for zone in ("Asia/Tehran", "Asia/Kabul", "Asia/Dushanbe"):
        z = zoneinfo.ZoneInfo(zone)
        offs = []
        for year in (2021, 2023):
            jan = datetime(year, 1, 15, 12, tzinfo=z).utcoffset()
            jul = datetime(year, 7, 15, 12, tzinfo=z).utcoffset()
            offs.append(f"{year}: Jan {jan.total_seconds() / 3600:+.1f} h, Jul "
                        f"{jul.total_seconds() / 3600:+.1f} h")
        lines.append(f"  {zone:14s} " + "; ".join(offs))
    lines.append("  (legal time is set by national law; the database follows it with a delay)")
    emit("a_zones", lines)
    berlin = zoneinfo.ZoneInfo("Europe/Berlin")
    rows = []
    for day in (datetime(2023, 3, 26), datetime(2023, 10, 29), datetime(2023, 6, 1)):
        start = day.replace(tzinfo=berlin)
        end = (day + timedelta(days=1)).replace(tzinfo=berlin)
        hours = (end.astimezone(timezone.utc) - start.astimezone(timezone.utc)) / timedelta(hours=1)
        rows.append(f"  {day.date()}: {hours:.0f} hours")
    amb = datetime(2023, 10, 29, 2, 30, tzinfo=berlin)
    emit("a_dst", ["a zone with daylight saving (Europe/Berlin), length of three local days:"]
         + rows + [
        f"  02:30 on 2023-10-29 happens twice: fold=0 -> {amb.astimezone(timezone.utc):%H:%M} "
        f"UTC, fold=1 -> {amb.replace(fold=1).astimezone(timezone.utc):%H:%M} UTC",
        "a plant there that stores local clock times without offset loses one hour in "
        "March and double-counts one in October"])


def intervals() -> None:
    hourly = datapack.load_hourly()
    pv = np.asarray(sc.pv_ac_power_mw(hourly["ghi_wm2"], 60, 50))
    wind = np.asarray(sc.wind_power_mw(hourly["ws_100m_ms"].to_numpy(),
                                       *map(np.asarray, datapack.load_power_curve().T.values), 12))
    export = np.minimum(pv + wind, 100.0)
    hour = hourly.index.hour.to_numpy()

    def revenue(series):
        price = np.where((hour >= 18) & (hour < 22), 90.0, 40.0)    # ch 1 fictional tariff
        return float(np.sum(series * price)) / 1e6
    right = revenue(export)
    late = revenue(np.roll(export, 1))                 # labels one hour too late
    early = revenue(np.roll(export, -1))
    rms = float(np.sqrt(np.mean((pv - np.roll(pv, 1)) ** 2)))
    pv_noon = float(np.mean(hourly["ghi_wm2"].to_numpy().reshape(365, 24), axis=0).argmax())
    emit("a_interval", [
        "Plant P export with the fictional time-of-use tariff of chapter 1 (S0, 1.1.0):",
        f"  correct labels      {right:.2f} million u/yr",
        f"  shifted one hour later  {late:.2f} ({100 * (late - right) / right:+.1f} %)",
        f"  shifted one hour earlier {early:.2f} ({100 * (early - right) / right:+.1f} %)",
        "  the change is small and has the same sign both ways: it depends on the shape",
        "  of the profile, so the error of a wrong label cannot be guessed, only avoided",
        f"hourly PV, correct vs one hour late: annual totals equal, hourly RMS difference "
        f"{rms:.1f} MW = {100 * rms / pv[pv > 0].mean():.0f} % of the mean daylight power",
        f"mean irradiance peaks in the hour starting {pv_noon:.0f}:00 (interval-start labels);",
        f"  with interval-end labels the same hour is called {pv_noon + 1:.0f}:00",
    ])


def sampling() -> None:
    hourly = datapack.load_hourly()
    curve = datapack.load_power_curve()
    vs, pk = curve["wind_speed_ms"].to_numpy(), curve["power_kw"].to_numpy()
    v = hourly["ws_100m_ms"].to_numpy()
    e_h = float(np.sum(np.interp(v, vs, pk))) * 12 / 1e6
    v_day = np.repeat(v.reshape(365, 24).mean(axis=1), 24)
    e_d = float(np.sum(np.interp(v_day, vs, pk))) * 12 / 1e6
    v_yr = np.full(8760, v.mean())
    e_y = float(np.sum(np.interp(v_yr, vs, pk))) * 12 / 1e6
    emit("a_sampling", [
        "gross energy of 12 turbines (no losses) from the same speeds averaged differently:",
        f"  hourly means      {e_h:7.1f} GWh",
        f"  daily means       {e_d:7.1f} GWh ({100 * (e_d - e_h) / e_h:+.1f} %)",
        f"  one annual mean   {e_y:7.1f} GWh ({100 * (e_y - e_h) / e_h:+.1f} %)",
        f"mean of v^3 / (mean v)^3 over the year: {np.mean(v ** 3) / v.mean() ** 3:.2f}",
        "averaging first hides the variability that the cubic power curve rewards",
    ])
    csv("ch05-averaging.csv", "case,gwh", [(0, f"{e_h:.1f}"), (1, f"{e_d:.1f}"),
                                          (2, f"{e_y:.1f}")])


def missing_values() -> None:
    ghi = datapack.load_hourly()["ghi_wm2"].to_numpy()
    true = ghi.sum() / 1000
    rng = np.random.default_rng(5)
    rand = rng.random(8760) < 0.10
    est_rand = ghi[~rand].mean() * 8760 / 1000
    hour = np.arange(8760) % 24
    day_gap = (hour >= 10) & (hour < 14) & (rng.random(8760) < 0.40)
    est_day = ghi[~day_gap].mean() * 8760 / 1000
    nights = ghi == 0
    est_nonight = ghi[~nights].mean() * 8760 / 1000
    clim = ghi.reshape(365, 24).copy()
    mask = day_gap.reshape(365, 24)
    hourly_mean = np.array([clim[~mask[:, h], h].mean() for h in range(24)])
    filled = np.where(mask, hourly_mean[None, :], clim).sum() / 1000
    emit("a_missing", [
        f"annual GHI of the complete series: {true:.1f} kWh/m2",
        f"10 % of hours missing at random, mean x 8760: {est_rand:.1f} "
        f"({100 * (est_rand - true) / true:+.1f} %)",
        f"{day_gap.sum()} midday hours missing (10-14 h), mean x 8760: {est_day:.1f} "
        f"({100 * (est_day - true) / true:+.1f} %)",
        f"  filled with the mean of the same clock hour: {filled:.1f} "
        f"({100 * (filled - true) / true:+.1f} %)",
        f"logger that drops zero values (nights): mean x 8760 = {est_nonight:.1f} "
        f"({100 * (est_nonight - true) / true:+.0f} %)",
        f"data recovery with midday gaps: {100 * (1 - day_gap.mean()):.1f} % of hours "
        f"(but {100 * day_gap.sum() / (ghi > 0).sum():.1f} % of daylight hours)",
    ])
    csv("ch05-missing.csv", "case,kwh", [(0, f"{true:.1f}"), (1, f"{est_rand:.1f}"),
                                        (2, f"{est_day:.1f}"), (3, f"{filled:.1f}"),
                                        (4, f"{est_nonight:.1f}")])


def units_in_data() -> None:
    lines = ["normalising units with the unit-aware quantities of chapter 2:"]
    for val, unit, target in ((46.8, "km/h", "m/s"), (87.9, "kPa", "hPa"),
                              (12345.6, "kWh", "MWh"), (2.4, "GWh", "MWh")):
        lines.append(f"  {val} {unit} = {Q(val, unit).to(target):.4g}")
    e_reported = 97_300.0                                # MWh, but the column said kWh
    cf_wrong = e_reported * 1000 / (50 * 8760)           # treated as kWh -> MWh x 1000
    lines += [f"PV energy 97 300 in a column labelled 'MWh' but read as kWh x 1000: capacity "
              f"factor {cf_wrong:.0f} (impossible)",
              f"  read correctly: {e_reported / (50 * 8760):.3f} (plausible for PV)",
              "range checks catch slips of 10, 1000 or 3.6 when the plausible band is narrow"]
    emit("a_units", lines)


def quality_flags() -> None:
    path = datapack.raw_path("met_mast_10min_raw.csv")
    text = path.read_text(encoding="utf-8").splitlines()
    rows = list(csvmod.DictReader([ln for ln in text if not ln.startswith("#")]))
    ws80 = np.array([float(r["ws80_avg"]) for r in rows])
    ws60 = np.array([float(r["ws60_avg"]) for r in rows])
    t = np.array([float(r["t_air"]) for r in rows])
    p = np.array([float(r["p_air"]) for r in rows])
    wd = np.array([float(r["wd100_avg"]) for r in rows])
    tests = {
        "ws60 range 0..45 m/s": dataio.qc_range(ws60, 0, 45),
        "ws80 flat >= 6 records": dataio.qc_flat(ws80, 6),
        "t_air range -40..55 C": dataio.qc_range(t, -40, 55),
        "p_air range 800..950 hPa": dataio.qc_range(p, 800, 950),
        "wd range 0..360 deg": dataio.qc_range(wd, 0, 360),
        "ws80 step > 4 m/s": dataio.qc_step(ws80, 4.0),
    }
    lines = [f"raw logger file: {len(rows)} records; quality tests (True = fails):"]
    for name, mask in tests.items():
        first = rows[int(np.argmax(mask))]["timestamp"] if mask.any() else "-"
        lines.append(f"  {name:26s} {int(mask.sum()):3d} records, first at {first}")
    lines.append("flags: 0 valid, 1 adjusted (e.g. unit corrected), 2 suspect, 9 missing")
    emit("a_flags", lines)
    csv("ch05-stuck.csv", "k,ws80,ws60,flag",
        [(k, f"{ws80[k]:.2f}", f"{max(ws60[k], -1):.2f}",
          int(tests['ws80 flat >= 6 records'][k]))
         for k in range(len(rows)) if 150 <= k < 260])
    dirs = [350.0, 355.0, 5.0, 10.0]
    emit("a_direction", [
        f"directions {dirs}: arithmetic mean {sum(dirs) / 4:.1f} deg (points south!)",
        f"  vector mean {dataio.vector_mean_deg(dirs):.1f} deg (north, as it should)",
    ])


def metadata() -> None:
    raw = datapack.raw_path("met_mast_10min_raw.csv")
    header = [ln for ln in raw.read_text(encoding="utf-8").splitlines() if ln.startswith("#")]
    from plantp import records as rec
    emit("a_metadata", ["header block of the raw logger file (read, do not guess):"]
         + ["  " + h for h in header] + [
        f"SHA-256 of the raw file: {rec.file_sha256(raw)[:32]}...",
        "provenance: logger file -> validated 10-min table -> hourly table -> report;",
        "  every step records its input hash, software version and settings",
    ])


def dictionary_and_schema() -> None:
    import csv as c
    rows = list(c.DictReader((datapack.release_dir() / "data_dictionary.csv")
                             .read_text(encoding="utf-8").splitlines()))
    lines = ["data dictionary of the hourly file (data pack 1.1.0), four of its rows:"]
    for r in rows[1:5]:
        lines.append(f"  {r['column']:9s} {r['unit']:5s} {r['valid_range']:11s} "
                     f"{r['description'].split(';')[0]}")
    lines.append(f"  ({len(rows)} rows in all, one per column of every data file)")
    emit("a_dictionary", lines)
    schema = [dataio.Field("ws100_avg", float, "m/s", 0, 45),
              dataio.Field("t_air", float, "degC", -40, 55),
              dataio.Field("p_air", float, "hPa", 800, 950),
              dataio.Field("serial", str, required=False)]
    sample = [{"ws100_avg": "7.41", "t_air": "12.3", "p_air": "879.1", "serial": ""},
              {"ws100_avg": "-0.40", "t_air": "12.2", "p_air": "879.0", "serial": ""},
              {"ws100_avg": "7.8", "t_air": "-9999", "p_air": "87.9", "serial": ""},
              {"ws100_avg": "7,9", "t_air": "", "p_air": "879.2", "serial": "A-1"}]
    clean, issues = dataio.validate_rows(sample, schema)
    emit("a_schema", [f"{len(sample)} rows checked against a 4-field schema: "
                      f"{len(clean)} clean, {len(issues)} issue(s)"]
         + [f"  {i}" for i in issues])


if __name__ == "__main__":
    numbers_in_bits()
    floating_point()
    text_encodings()
    csv_pitfalls()
    time_and_zones()
    intervals()
    sampling()
    missing_values()
    units_in_data()
    quality_flags()
    metadata()
    dictionary_and_schema()
