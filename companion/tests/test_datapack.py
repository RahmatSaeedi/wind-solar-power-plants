"""The data pack is intact, well-formed and reproduces its published summary."""
import json

import numpy as np
import pandas as pd
import pytest

from plantp import DATA_RELEASE, datapack


def test_checksums_match_manifest():
    assert datapack.verify() == []


def test_hourly_series_is_one_complete_non_leap_year():
    hourly = datapack.load_hourly()
    assert len(hourly) == 8760
    assert hourly.index.is_unique
    steps = hourly.index.to_series().diff().dropna().unique()
    assert list(steps) == [pd.Timedelta(hours=1)]
    assert str(hourly.index[0]) == "2023-01-01 00:00:00+04:00"
    assert str(hourly.index[-1]) == "2023-12-31 23:00:00+04:00"
    assert not hourly.isna().any().any()
    assert (hourly["qc_flag"] == 0).all()


def test_values_stay_inside_the_data_dictionary_ranges():
    hourly = datapack.load_hourly()
    limits = {"ghi_wm2": (0, 1200), "dni_wm2": (0, 1050), "dhi_wm2": (0, 700),
              "t_air_c": (-25, 50), "ws_100m_ms": (0, 45), "ws_80m_ms": (0, 45),
              "ws_60m_ms": (0, 45), "wd_100m_deg": (0, 359), "p_hpa": (840, 920)}
    for column, (low, high) in limits.items():
        assert hourly[column].between(low, high).all(), column


def test_irradiance_components_are_physically_consistent():
    hourly = datapack.load_hourly()
    assert (hourly["dhi_wm2"] <= hourly["ghi_wm2"] + 0.051).all()      # diffuse never exceeds global
    night = hourly["ghi_wm2"] == 0
    assert (hourly.loc[night, ["dni_wm2", "dhi_wm2"]] == 0).all().all()
    assert 0.25 < night.mean() < 0.60                                   # about half the hours are dark


def test_expected_results_are_reproduced_independently():
    hourly = datapack.load_hourly()
    with open(datapack.release_dir() / "expected_results.json", encoding="utf-8") as fh:
        expected = json.load(fh)
    assert expected["release"] == DATA_RELEASE
    assert hourly["ghi_wm2"].sum() / 1000 == pytest.approx(expected["annual_ghi_kwh_m2"], abs=0.05)
    assert hourly["t_air_c"].mean() == pytest.approx(expected["mean_t_air_c"], abs=0.005)
    assert hourly["ws_100m_ms"].mean() == pytest.approx(expected["mean_ws_100m_ms"], abs=0.0005)
    assert hourly["ws_60m_ms"].mean() < hourly["ws_80m_ms"].mean() < hourly["ws_100m_ms"].mean()


@pytest.mark.parametrize("subset, rows", [("day_summer", 24), ("day_winter", 24), ("week_spring", 168)])
def test_subsets_are_slices_of_the_full_series(subset, rows):
    part = datapack.load_hourly(subset)
    full = datapack.load_hourly()
    assert len(part) == rows
    pd.testing.assert_frame_equal(part, full.loc[part.index])


def test_power_curve_shape():
    curve = datapack.load_power_curve()
    speed, power = curve["wind_speed_ms"].to_numpy(), curve["power_kw"].to_numpy()
    assert (power[speed < 3.0] == 0).all() and (power[speed > 25.0] == 0).all()
    working = (speed >= 3.0) & (speed <= 25.0)
    assert (np.diff(power[working]) >= 0).all()                         # never falls before cut-out
    assert power.max() == 5000
    assert (power[(speed >= 13.0) & (speed <= 25.0)] == 5000).all()


def test_seed_ratings_are_those_of_the_book_plan():
    ratings = datapack.load_seed_ratings()
    values = ratings["value"].to_dict()
    assert values == {"SR-01": 60, "SR-02": 50, "SR-03": 60, "SR-04": 33,
                      "SR-05": 132, "SR-06": 100, "SR-07": 20, "SR-08": 40}
    assert (ratings["status"] == "assumed").all()


def test_scenarios_state_every_bess_assumption():
    assert datapack.load_scenario("S0")["bess"] is None
    bess = datapack.load_scenario("S1")["bess"]
    for key in ("power_mw", "energy_mwh_nominal_bol", "soc_window_pct", "usable_energy_mwh_bol",
                "roundtrip_efficiency_ac_pct", "capacity_fade_pct_per_year", "reserve_mwh",
                "charging_source", "grid_charging_permitted"):
        assert key in bess, key
    low, high = bess["soc_window_pct"]
    assert bess["usable_energy_mwh_bol"] == pytest.approx(
        bess["energy_mwh_nominal_bol"] * (high - low) / 100)
    assert bess["grid_charging_permitted"] is False                     # never assumed silently


def test_unknown_names_are_rejected():
    with pytest.raises(ValueError):
        datapack.load_hourly("day_autumn")
    with pytest.raises(ValueError):
        datapack.load_scenario("S9")
    with pytest.raises(FileNotFoundError):
        datapack.release_dir("9.9.9")


def test_citation_names_release_and_scenario():
    assert datapack.cite("S1") == "Plant P Reference Data Pack 1.1.0, scenario S1 (BESS)"
    assert datapack.cite("S0", "1.0.0") == ("Plant P Reference Data Pack 1.0.0, "
                                            "scenario S0 (no-BESS)")


# ---- releases side by side (chapter 5) -------------------------------------------------
def test_old_release_is_intact_too():
    assert datapack.verify("1.0.0") == []


def test_minor_release_keeps_every_shared_file_identical():
    old = datapack.load_manifest("1.0.0")["files"]
    new = datapack.load_manifest("1.1.0")["files"]
    assert set(old) <= set(new)                                     # nothing removed
    changed = {f for f in old if old[f]["sha256"] != new[f]["sha256"]}
    assert changed == {"CHANGELOG.md", "README.md", "assumptions.csv",
                       "data_dictionary.csv", "expected_results.json"}
    assert all(f.startswith(("raw/", "assets/")) for f in set(new) - set(old))


def test_ledger_is_complete_and_ordered():
    led = datapack.load_assumptions()
    ids = list(led.index)
    assert ids == [f"A-{k:03d}" for k in range(1, len(ids) + 1)]
    assert ids[-1] == "A-099"
    assert set(led["status"]) <= {"assumed", "synthetic", "measured", "vendor", "verified"}
    old = datapack.load_assumptions("1.0.0")
    pd.testing.assert_frame_equal(led.loc[old.index], old)        # old rows unchanged


def test_raw_files_exist_only_in_the_new_release():
    assert datapack.raw_path("met_mast_10min_raw.csv").exists()
    with pytest.raises(FileNotFoundError):
        datapack.raw_path("met_mast_10min_raw.csv", "1.0.0")
    assert len(datapack.load_register("A")) == 77
