"""Load the Plant P Reference Data Pack and check that it has not been altered.

    from plantp import datapack
    datapack.verify()                      # [] when every checksum matches
    hourly = datapack.load_hourly()        # 8760 rows, time-zone-aware index
    day = datapack.load_hourly("day_summer")
    s1 = datapack.load_scenario("S1")
    print(datapack.cite("S1"))             # the citation every example carries
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd
import yaml

from . import DATA_RELEASE

DATA_ROOT = Path(__file__).resolve().parent.parent / "plantp_data"

_SUBSETS = {
    None: "timeseries/plantp_hourly_8760.csv",
    "day_summer": "timeseries/subset_day_summer.csv",
    "day_winter": "timeseries/subset_day_winter.csv",
    "week_spring": "timeseries/subset_week_spring.csv",
}
_SCENARIOS = {"S0": "scenarios/S0-no-bess.yml", "S1": "scenarios/S1-bess.yml"}


def release_dir(release: str = DATA_RELEASE) -> Path:
    """Folder of one release; raises FileNotFoundError if it is not installed."""
    path = DATA_ROOT / release
    if not path.is_dir():
        raise FileNotFoundError(f"data pack release {release} not found in {DATA_ROOT}")
    return path


def load_manifest(release: str = DATA_RELEASE) -> dict:
    with open(release_dir(release) / "manifest.json", encoding="utf-8") as fh:
        return json.load(fh)


def verify(release: str = DATA_RELEASE) -> list[str]:
    """Compare every file with its SHA-256 in the manifest.

    Returns a list of problems; an empty list means the pack is intact.
    """
    root = release_dir(release)
    problems = []
    for rel, info in load_manifest(release)["files"].items():
        path = root / rel
        if not path.exists():
            problems.append(f"missing: {rel}")
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != info["sha256"]:
            problems.append(f"checksum differs: {rel}")
    return problems


def load_hourly(subset: str | None = None, release: str = DATA_RELEASE) -> pd.DataFrame:
    """Hourly time series, indexed by the time-zone-aware start of each hour.

    subset: None (the full 8760 hours), "day_summer", "day_winter" or "week_spring".
    """
    if subset not in _SUBSETS:
        raise ValueError(f"unknown subset {subset!r}; choose one of {list(_SUBSETS)}")
    frame = pd.read_csv(release_dir(release) / _SUBSETS[subset], parse_dates=["timestamp"])
    return frame.set_index("timestamp")


def load_power_curve(release: str = DATA_RELEASE) -> pd.DataFrame:
    """Power curve of the fictional WT-5.0-150 turbine (air density 1.225 kg/m3)."""
    return pd.read_csv(release_dir(release) / "equipment/wind_turbine_WT-5.0-150_power_curve.csv")


def load_seed_ratings(release: str = DATA_RELEASE) -> pd.DataFrame:
    return pd.read_csv(release_dir(release) / "seed_ratings.csv").set_index("id")


def load_assumptions(release: str = DATA_RELEASE) -> pd.DataFrame:
    return pd.read_csv(release_dir(release) / "assumptions.csv").set_index("id")


def load_yaml(relative_path: str, release: str = DATA_RELEASE) -> dict:
    with open(release_dir(release) / relative_path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_scenario(scenario_id: str, release: str = DATA_RELEASE) -> dict:
    """Scenario card: "S0" (no battery) or "S1" (with battery)."""
    if scenario_id not in _SCENARIOS:
        raise ValueError(f"unknown scenario {scenario_id!r}; choose one of {list(_SCENARIOS)}")
    return load_yaml(_SCENARIOS[scenario_id], release)


def cite(scenario_id: str, release: str = DATA_RELEASE) -> str:
    """The line each worked example prints to say which data it used."""
    name = load_scenario(scenario_id, release)["name"]
    return f"Plant P Reference Data Pack {release}, scenario {scenario_id} ({name})"


# ---- release 1.1.0 additions (chapter 5) ------------------------------------------------
def raw_path(name: str, release: str = DATA_RELEASE) -> Path:
    """Path of a raw sample file ("met_mast_10min_raw.csv", "pv_scada_export.csv", ...)."""
    path = release_dir(release) / "raw" / name
    if not path.exists():
        raise FileNotFoundError(f"{name} is not part of release {release} (added in 1.1.0)")
    return path


def load_register(rev: str = "A", release: str = DATA_RELEASE) -> list[dict]:
    """Synthetic asset register, revision "A" or "B", as a list of dictionaries."""
    import csv
    path = release_dir(release) / "assets" / f"asset_register_rev_{rev}.csv"
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def load_change_notice(release: str = DATA_RELEASE) -> list[dict]:
    import csv
    with open(release_dir(release) / "assets" / "change_notice.csv", encoding="utf-8",
              newline="") as fh:
        return list(csv.DictReader(fh))
