"""Tests of the chapter 5 modules: dataio, assets, losses and the cash-flow helpers."""
import math
from datetime import datetime, timedelta, timezone

import pytest

from plantp import assets, dataio, losses, money

# ---- dataio -----------------------------------------------------------------------------
SCHEMA = [dataio.Field("ghi", float, "W/m2", 0, 1400), dataio.Field("flag", int, "", 0, 2),
          dataio.Field("note", str, required=False)]


def test_validate_rows_reports_every_problem():
    rows = [{"ghi": "500", "flag": "0", "note": ""}, {"ghi": "-5", "flag": "0", "note": "x"},
            {"ghi": "abc", "flag": "3", "note": ""}, {"ghi": "", "flag": "1", "note": ""}]
    clean, issues = dataio.validate_rows(rows, SCHEMA)
    assert len(clean) == 1 and clean[0]["ghi"] == 500.0 and clean[0]["note"] is None
    assert any("below" in i for i in issues)
    assert any("not float" in i for i in issues)
    assert any("above 2" in i for i in issues)
    assert any("empty" in i for i in issues)
    assert dataio.validate_rows([{"x": "1"}], SCHEMA)[1][0].startswith("missing column")


def test_read_csv_refuses_bom(tmp_path):
    p = tmp_path / "a.csv"
    p.write_bytes(b"\xef\xbb\xbfa,b\n1,2\n")
    with pytest.raises(ValueError):
        dataio.read_csv_rows(p)
    q = tmp_path / "b.csv"
    q.write_bytes(b"a,b\n1,2\n")
    assert dataio.read_csv_rows(q) == [{"a": "1", "b": "2"}]


def test_timestamps_detect_duplicates_gaps_and_offsets():
    stamps = ["2023-01-01T00:00:00+04:00", "2023-01-01T01:00:00+04:00",
              "2023-01-01T01:00:00+04:00", "2023-01-01T03:00:00+04:00",
              "2023-01-01T04:00:00", "2023-01-01T00:00:00+00:00"]
    parsed, issues = dataio.check_timestamps(stamps)
    text = " ".join(issues)
    assert "duplicate" in text and "gap" in text and "no UTC offset" in text
    assert "mixed UTC offsets" in text and "not increasing" in text
    assert parsed[0] == datetime(2022, 12, 31, 20, tzinfo=timezone.utc)


def test_aggregate_hourly_uses_interval_start_in_utc():
    t0 = datetime(2023, 1, 1, 0, 0, tzinfo=timezone(timedelta(hours=4)))
    times = [t0 + timedelta(minutes=10 * k) for k in range(12)]
    vals = [float(k) for k in range(12)]
    out = dataio.aggregate_hourly(times, vals)
    keys = list(out)
    assert keys[0] == datetime(2022, 12, 31, 20, tzinfo=timezone.utc)
    assert out[keys[0]] == (2.5, 6) and out[keys[1]] == (8.5, 6)
    assert len(dataio.aggregate_hourly(times[:4], vals[:4], min_count=5)) == 0
    with pytest.raises(ValueError):
        dataio.aggregate_hourly([datetime(2023, 1, 1)], [1.0])


def test_register_decoding():
    assert dataio.to_int16(0xFFFF) == -1 and dataio.to_int16(0x7FFF) == 32767
    with pytest.raises(ValueError):
        dataio.to_int16(70000)
    assert dataio.decode_float32(0x3F80, 0x0000) == 1.0
    assert dataio.decode_float32(0x4148, 0x0000) == 12.5


# ---- assets -----------------------------------------------------------------------------
def base_register():
    return [dict(tag="PLP-PLT-01", parent="", description="Plant P", criticality="A"),
            dict(tag="PLP-WTG-01", parent="PLP-PLT-01", description="Turbine 1",
                 criticality="A"),
            dict(tag="PLP-WTG-01-GEN", parent="PLP-WTG-01", description="Generator",
                 vendor="X", model="G5", serial="SN1", delivered="2025-03-01",
                 installed="2025-04-01", commissioned="2025-06-01", criticality="A")]


def test_valid_register_has_no_issues():
    assert assets.validate_register(base_register()) == []


def test_register_errors_are_found():
    reg = base_register() + [
        dict(tag="PLP-WTG-01", parent="PLP-PLT-01", description="dup", criticality="B"),
        dict(tag="WTG-2", parent="PLP-PLT-01", description="bad tag", criticality="B"),
        dict(tag="PLP-INV-03", parent="PLP-PVB-09", description="orphan", criticality="Z"),
        dict(tag="PLP-TRF-01-OIL", parent="PLP-PLT-01", description="", criticality="C",
             delivered="2025-05-01", installed="2025-04-01", commissioned="2025-07-01")]
    text = " | ".join(assets.validate_register(reg))
    for needle in ("duplicate tag", "does not follow", "parent PLP-PVB-09", "criticality 'Z'",
                   "description is missing", "installed 2025-04-01 is before delivered",
                   "without a serial"):
        assert needle in text


def test_diff_and_cmms_round_trip():
    old = base_register()
    new = [dict(r) for r in old]
    new[2]["serial"] = "SN2"
    new.append(dict(tag="PLP-MET-01", parent="PLP-PLT-01", description="Mast",
                    criticality="B"))
    d = assets.diff_registers(old, new)
    assert d["added"] == ["PLP-MET-01"] and d["removed"] == []
    assert d["changed"]["PLP-WTG-01-GEN"] == {"serial": ("SN1", "SN2")}
    long = base_register()
    long[0]["description"] = "x" * 50
    back = assets.from_cmms(assets.to_cmms(long))
    assert back[0]["description"] == "x" * 40            # truncated by the export
    assert back[2]["serial"] == "SN1"


# ---- losses and money -------------------------------------------------------------------
def test_losses_hand_case():
    p = math.sqrt(3) * 33 * 0.95
    assert float(losses.current_a(p, 33.0, 0.95)) == pytest.approx(1000.0)
    c = float(losses.cable_loss_mw(p, 33.0, 0.95, 0.1, 1.0, 0.0, 20.0))
    assert c == pytest.approx(3 * 1000 ** 2 * 0.1 / 1e6)
    t = float(losses.transformer_loss_mw(95.0, 0.95, 100.0, 0.05, 0.5))
    assert t == pytest.approx(0.55)
    s = losses.annual_losses([10, 10], [0.1, 0.1], [0.05, 0.05])
    assert s["cable_pct"] == pytest.approx(1.0) and s["trafo_pct"] == pytest.approx(0.5)


def test_npv_irr_and_cash_flow():
    assert money.npv(0.1, [-100, 110]) == pytest.approx(0.0)
    assert money.irr([-100, 110]) == pytest.approx(0.1, abs=1e-8)
    with pytest.raises(ValueError):
        money.irr([100, 100])
    cf = money.project_cash_flow(1000.0, 50.0, 100000.0, 10000.0, 3, 0.0, 0.5, 0.0, 2)
    assert cf["revenue"][1] == 50000.0 and cf["debt_service"][1] == pytest.approx(25000.0)
    assert cf["dscr"][1] == pytest.approx(40000 / 25000) and math.isnan(cf["dscr"][3])
    assert cf["equity_cash"][0] == -50000.0 and cf["equity_cash"][3] == 40000.0
