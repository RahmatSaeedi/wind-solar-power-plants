"""Tests of the chapter 5 programs: the construction sequence (steps 1-4),
the resource_tool package (step 5), the schema checker, the spreadsheet
auditor and the rule-based battery dispatch. Hand values in comments."""
import math
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from companion.ch05 import step1_convert as s1                  # noqa: E402
from companion.ch05 import step2_reader as s2                   # noqa: E402
from companion.ch05 import step3_model as s3                    # noqa: E402
from companion.ch05.resource_tool import model, rawdata  # noqa: E402
from companion.ch05.resource_tool import report, run     # noqa: E402
from plantp import datapack, dataio, dispatch, schema, sheet    # noqa: E402

RUN_S0 = ROOT / "companion/ch05/config/run_S0.yml"
RUN_BAD = ROOT / "companion/ch05/config/run_bad.yml"
RAW_MET = "met_mast_10min_raw.csv"
HOURLY = "timeseries/plantp_hourly_8760.csv"


# ---- step 1: unit converter -----------------------------------------------
@pytest.mark.parametrize("value, src, dst, expected", [
    (46.8, "km/h", "m/s", 13.0), (25, "degC", "K", 298.15),
    (32, "degF", "degC", 0.0), (2.4, "GWh", "MWh", 2400.0),
    (1, "bar", "hPa", 1000.0), (1, "knot", "km/h", 1.852)])
def test_convert_known_values(value, src, dst, expected):
    assert s1.convert(value, src, dst) == pytest.approx(expected)


@pytest.mark.parametrize("value, src, dst", [
    (5, "MW", "MWh"), (1, "furlong", "m"), (-300, "degC", "K"),
    (1, "m/s", "furlong")])
def test_convert_refuses(value, src, dst):
    with pytest.raises(s1.ConversionError):
        s1.convert(value, src, dst)


def test_convert_round_trip_and_cli(capsys):
    there = s1.convert(7.3, "m/s", "knot")
    assert s1.convert(there, "knot", "m/s") == pytest.approx(7.3)
    assert s1.main(["46.8", "km/h", "m/s"]) == 0
    assert "13 m/s" in capsys.readouterr().out
    assert s1.main(["5", "MW", "MWh"]) == 2


# ---- step 2: validated reader ---------------------------------------------
def test_reader_on_the_data_pack_sample():
    rows, issues = s2.read_scada(datapack.raw_path("pv_scada_export.csv"))
    assert len(rows) == 71 and len(issues) == 1
    assert "step 2:00:00" in issues[0]
    assert rows[0]["start"] == datetime(2023, 4, 2, 20, tzinfo=timezone.utc)
    assert all(r["energy_mwh"] <= 50.0 for r in rows)


def test_reader_reports_malformed_lines(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("time_utc;energy_kwh;availability_pct\n"
                   "2023-04-03T08:00:00Z;12,5;100\n"
                   "2023-04-03T09:00:00Z;abc;100\n"
                   "2023-04-03T10:00:00+04:00;5;100\n"
                   "2023-04-03T11:00:00Z;99999;100;extra\n"
                   "2023-04-03T12:00:00Z;-1;140\n", encoding="utf-8")
    rows, issues = s2.read_scada(bad)
    text = " | ".join(issues)
    for needle in ("could not convert", "is not UTC", "4 fields",
                   "out of range"):
        assert needle in text
    assert rows[0]["energy_mwh"] == pytest.approx(0.0125)     # 12,5 kWh
    head = tmp_path / "header.csv"
    head.write_text("time;kwh\n", encoding="utf-8")
    rows, issues = s2.read_scada(head)
    assert rows == [] and issues[0].startswith("header")


# ---- step 3 / model: pure functions, hand cases ----------------------------
def test_pv_hand_cases():
    # T_air = 25 - 25/800 x 1000 = -6.25 C puts the cell at exactly 25 C
    p = float(s3.pv_ac_mw(1000, -6.25, dc_mwp=40))
    assert p == pytest.approx(40 * 0.90 * 0.98)              # 35.28 MW
    assert float(s3.pv_ac_mw(1000, -6.25)) == 50.0           # inverter limit
    assert float(s3.pv_ac_mw(0, 20)) == 0.0
    hot = float(s3.pv_ac_mw(800, 35, dc_mwp=40))             # T_cell 60 C
    assert hot == pytest.approx(40 * 0.8 * (1 - 0.0035 * 35) * 0.9 * 0.98)
    with pytest.raises(ValueError):
        s3.pv_ac_mw(-1, 20)


def test_wind_hand_cases():
    curve = datapack.load_power_curve()
    v, p = curve["wind_speed_ms"], curve["power_kw"]
    farm = float(s3.wind_farm_mw(8.0, 1.225, v, p))
    assert farm == pytest.approx(2522 * 12 / 1000 * 0.88)   # 26.63 MW
    assert float(s3.wind_farm_mw(8.0, 1.05, v, p)) < farm
    rho = float(s3.air_density(1013.25, 15.0))
    assert rho == pytest.approx(1.2250, abs=1e-3)
    with pytest.raises(ValueError):
        s3.wind_farm_mw(-0.1, 1.2, v, p)


def test_refactor_did_not_change_the_numbers():
    h = datapack.load_hourly("week_spring")
    g, t, p = h["ghi_wm2"], h["t_air_c"], h["p_hpa"]
    np.testing.assert_array_equal(s3.pv_ac_mw(g, t), model.pv_ac_mw(g, t))
    np.testing.assert_array_equal(s3.air_density(p, t),
                                  model.air_density(p, t))


def test_export_never_exceeds_the_limit_and_balances():
    rng = np.random.default_rng(1)
    pv, wind = rng.uniform(0, 50, 1000), rng.uniform(0, 60, 1000)
    exp, cut = s3.export_mw(pv, wind, 100)
    assert (exp <= 100 + 1e-12).all() and (cut >= 0).all()
    np.testing.assert_allclose(exp + cut, pv + wind)


# ---- schema ---------------------------------------------------------------
def test_schema_accepts_good_and_lists_every_bad_entry():
    import yaml
    good = yaml.safe_load(RUN_S0.read_text("utf-8"))
    assert schema.check(good, schema.RUN_SCHEMA) == []
    bad = yaml.safe_load(RUN_BAD.read_text("utf-8"))
    assert len(schema.check(bad, schema.RUN_SCHEMA)) == 10
    first = schema.check([1, 2], schema.RUN_SCHEMA)[0]
    assert first.startswith("top level")
    msg = schema.check({"x": True}, {"x": {"type": float}})[0]
    assert msg.startswith("x: expected")                     # bool != number


# ---- step 5: raw data, run and report -------------------------------------
def test_raw_validation_finds_every_planted_defect():
    table, s = rawdata.validate(datapack.raw_path(RAW_MET))
    assert s["duplicates"] == 1 and s["out_of_order"] == 1        # D1, D7
    assert s["gaps"] == [("2023-04-03 14:00", 5)]                 # D2
    flags = s["flags"]
    assert flags["ws60_avg: out of range"] == 1                   # D3
    assert flags["ws80_avg: stuck"] == 12                         # D4
    assert flags["t_air: sentinel"] == 1                          # D5
    assert flags["p_air: kPa -> hPa"] == 6                        # D6
    assert flags["ghi: night offset -> 0"] == 6                   # D8
    assert flags["wd100_avg: out of range"] == 1                  # D9
    assert s["incomplete_hours"] == 1


def test_clean_hours_reproduce_the_reference_series():
    import pandas as pd
    table, _ = rawdata.validate(datapack.raw_path(RAW_MET))
    ref = datapack.load_hourly()
    for hour, row in table.items():
        r = ref.loc[pd.Timestamp(hour).tz_convert("+04:00")]
        if not math.isnan(row["ws100_avg"]):
            assert row["ws100_avg"] == pytest.approx(r["ws_100m_ms"],
                                                     abs=0.01)
        if not math.isnan(row["p_air"]):
            assert row["p_air"] == pytest.approx(r["p_hpa"], abs=0.05)


def test_vector_mean_across_north():
    assert rawdata.vector_mean([350, 10]) == pytest.approx(0.0, abs=1e-9)
    assert dataio.vector_mean_deg([80, 100]) == pytest.approx(90.0)


def test_configured_run_is_reproducible():
    cfg = run.load_config(RUN_S0)
    r1, _ = run.run(cfg)
    r2, _ = run.run(cfg)
    assert r1 == r2
    energies = (r1["pv_gwh"], r1["wind_gwh"], r1["export_gwh"])
    assert energies == (96.43, 177.08, 273.52)
    files = datapack.load_manifest()["files"]
    assert r1["inputs"][HOURLY] == files[HOURLY]["sha256"]


def test_stage1_and_stage2_agree():
    """Refactoring must not change a single reported number."""
    import json
    import subprocess
    subprocess.run([sys.executable, "-m", "companion.ch05.project_stage1"],
                   cwd=ROOT, capture_output=True, check=True)
    out = ROOT / "companion/ch05/output/stage1/result.json"
    stage1 = json.loads(out.read_text(encoding="utf-8"))
    stage2, _ = run.run(run.load_config(RUN_S0))
    for key in ("pv_gwh", "wind_gwh", "export_gwh"):
        assert stage1[key] == stage2[key], key


def test_report_names_its_evidence():
    r, _ = run.run(run.load_config(RUN_S0))
    text = report.render(r)
    for needle in ("PLP-GEN-REP-0002", r["data_release"],
                   r["config_sha256"][:16], f"{r['export_gwh']:.2f}",
                   "Limitations", "approved"):
        assert needle in text


# ---- time-zone edge cases ------------------------------------------------
def test_hourly_aggregation_across_a_clock_change():
    import zoneinfo
    berlin = zoneinfo.ZoneInfo("Europe/Berlin")
    start = datetime(2023, 3, 26, 0, 0, tzinfo=berlin).astimezone(timezone.utc)
    times = [start + timedelta(minutes=10 * k) for k in range(18)]  # 3 h
    out = dataio.aggregate_hourly(times, [1.0] * 18)
    assert len(out) == 3 and all(n == 6 for _, n in out.values())
    local_hours = {h.astimezone(berlin).hour for h in out}
    assert local_hours == {0, 1, 3}             # 02:00 does not exist there


# ---- spreadsheet auditor -------------------------------------------------
def test_sheet_values_and_findings():
    sh = sheet.Sheet({"B2": 60, "B3": 0.85, "B4": "=B2*B3",
                      "B5": "=SUM(B2:B4)", "C1": "=C2", "C2": "=C1",
                      "D1": "=B2*1000", "D2": "=E9"}, names={"cap": "B2"})
    assert sh.value("B4") == pytest.approx(51.0)
    assert sh.value("B5") == pytest.approx(111.85)
    found = " | ".join(sheet.audit(sh))
    for needle in ("circular", "number 1000", "empty cell E9"):
        assert needle in found
    with pytest.raises(ValueError):                  # no code in formulas
        sheet.Sheet({"A1": "=__import__('os')"}).value("A1")


# ---- rule-based battery dispatch: invariants ------------------------------
def test_rule_based_dispatch_invariants():
    rng = np.random.default_rng(7)
    eta = math.sqrt(0.86)
    for _ in range(20):                       # 20 random weeks of generation
        gen = rng.uniform(0, 110, 24 * 7)
        r = dispatch.rule_based_shift(gen, range(9, 15), range(18, 22),
                                      20, 32, 0.86, 100)
        ch, dis, soc = r.charge_mw, r.discharge_mw, r.soc_mwh
        assert (ch <= np.minimum(gen, 20) + 1e-9).all()  # no grid charging
        assert (dis <= 20 + 1e-9).all()
        assert (soc >= -1e-9).all() and (soc <= 32 + 1e-9).all()
        assert (r.export_mw <= 100 + 1e-9).all()
        kept = ch.sum() * eta - dis.sum() / eta          # energy balance
        assert kept == pytest.approx(soc[-1], abs=1e-6)
        assert not ((ch > 0) & (dis > 0)).any()
