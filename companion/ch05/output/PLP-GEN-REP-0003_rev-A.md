# Plant P data-pack verification - release 1.1.0

Document PLP-GEN-REP-0003, revision A, status IFR. Synthetic teaching data.

## Inputs

- `timeseries/plantp_hourly_8760.csv` SHA-256 `0b179863ba8707a5aa76ecc9e2f4d7792313781a01f12f9fa4a9ec1366287de2`
- `equipment/wind_turbine_WT-5.0-150_power_curve.csv` SHA-256 `672c82e3bfaee9a11cee89cc26c63673098b956f919ca59b0f1dbf0f8cb045ab`
- `scenarios/S0-no-bess.yml` SHA-256 `1bbe995db7e158fa1fbc5439dab6d010e1e2c04980914cc8435bfb3d7c10e9ef`
- `scenarios/S1-bess.yml` SHA-256 `876cf7179ee86d134a70d066095b6e49b7aecdac827ec76847b5009f6410ff73`

## Checks

- PASS: columns = data dictionary
- PASS: values inside the dictionary ranges
- PASS: one UTC offset (+04:00)
- PASS: one-hour steps, 8760 unique stamps
- PASS: no missing values
- PASS: pressure in hPa (not Pa or kPa)
- PASS: irradiance consistent (DHI <= GHI)
- PASS: provenance: generator and seed recorded
- PASS: scenario cards: S0 no battery, S1 battery
- PASS: unknown scenario refused
- PASS: ledger A-001..A-099 complete

## Reproduced results (chapter 1 model)

| quantity | value |
|---|---:|
| pv_gwh | 97.3 |
| wind_gwh | 192.5 |
| export_gwh | 289.8 |
| curtailed_mwh | 13.8 |
| s1_delivered_mwh | 11.8 |

Citation: Plant P Reference Data Pack 1.1.0, scenario S0 (no-BESS); Plant P Reference Data Pack 1.1.0, scenario S1 (BESS)
