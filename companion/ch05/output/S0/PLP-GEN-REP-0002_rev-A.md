# Plant P resource analysis - S0

Document PLP-GEN-REP-0002, revision A, status IFR. Synthetic teaching data; not a design.

## Inputs and provenance

- Data pack release 1.1.0; run PLP-CH05-S0
- Configuration SHA-256 `7b059c3879180fb4...`
- `timeseries/plantp_hourly_8760.csv` SHA-256 `0b179863ba8707a5...`
- `equipment/wind_turbine_WT-5.0-150_power_curve.csv` SHA-256 `672c82e3bfaee9a1...`
- Software: resource_tool 1.0.0, plantp 0.2.0, python 3.14.1, numpy 2.5.4

## Results

| quantity | value | unit |
|---|---:|---|
| PV energy | 96.43 | GWh/yr |
| wind energy | 177.08 | GWh/yr |
| export at the point of connection | 273.52 | GWh/yr |
| curtailed | 0.0 | MWh/yr |
| mean air density | 1.0559 | kg/m3 |

## Raw-data checks (met mast, 10 min)

- 428 records read, 427 kept; 1 duplicate(s), 1 out of order
- gaps: [['2023-04-03 14:00', 5]]; incomplete hours: 1 of 72
- flagged ghi: night offset -> 0: 6
- flagged p_air: kPa -> hPa: 6
- flagged t_air: sentinel: 1
- flagged wd100_avg: out of range: 1
- flagged ws60_avg: out of range: 1
- flagged ws80_avg: stuck: 12

## Limitations

- Horizontal irradiance on the array; NOCT temperature model;
  lumped losses (A-097; density by D-008).
  Chapters 10, 11 and 15 refine these models.
- Synthetic one-year series; no long-term correction (ch. 13).

## Checks and sign-off

| role | name | date |
|---|---|---|
| prepared |  |  |
| checked |  |  |
| approved |  |  |
