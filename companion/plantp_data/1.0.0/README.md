# Plant P Reference Data Pack — release 1.0.0

Synthetic, non-geolocated teaching data for the fictional hybrid wind–solar
plant "Plant P" of the book. Nothing here describes a real site, grid or
product, and nothing here is a recommended design.

| Path | Content |
|---|---|
| `manifest.json` | release id, seed, site assumptions, SHA-256 of every file |
| `seed_ratings.csv` | the plant's seed ratings (60 MWp / 50 MW PV, 60 MW wind, 33/132 kV, 100 MW export, optional 20 MW / 40 MWh BESS) |
| `assumptions.csv` | the assumptions ledger: id, value, unit, status, source, chapter |
| `scenarios/S0-no-bess.yml`, `scenarios/S1-bess.yml` | the two named scenarios |
| `timeseries/plantp_hourly_8760.csv` | one non-leap year of hourly irradiance, temperature, wind and pressure |
| `timeseries/subset_*.csv` | one summer day, one winter day and one spring week for hand calculation |
| `equipment/` | fictional PV module and wind turbine data |
| `data_dictionary.csv` | every column: unit, meaning, valid range, status |
| `expected_results.json` | summary values the test-suite reproduces |
| `CHANGELOG.md` | what changed, why, and which book artefacts depend on it |

Status labels used everywhere: `synthetic`, `assumed`, `measured`, `vendor`, `verified`.
Timestamps mark the START of each hour, local standard time, fixed offset +04:00.

Regenerate or verify: `python companion/plantp_data/generate_release.py [--check]`.

---

**فارسی.** این بسته، دادهٔ **ساختگی** و بدونِ مختصاتِ جغرافیاییِ «نیروگاهِ P» است و فقط برای
آموزش ساخته شده است؛ هیچ ساختگاه، شبکه یا محصولِ واقعی را توصیف نمی‌کند. هر مثالِ کتاب
شمارهٔ انتشارِ این بسته و نامِ سناریو (S0 بدونِ باتری، S1 با باتری) را ذکر می‌کند.
