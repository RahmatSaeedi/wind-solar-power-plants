# Changelog — Plant P Reference Data Pack

## 1.1.0 — 2026-11-15
- Added: the full assumptions ledger A-014..A-099 (chapters 2 to 6 and 5);
  raw/met_mast_10min_raw.csv with its defect key; raw/pv_scada_export.csv;
  assets/asset_register_rev_A.csv, assets/asset_register_rev_B.csv,
  assets/change_notice.csv; data-dictionary rows for the new files.
- Unchanged: every time series, subset, equipment file, scenario and seed
  rating is byte-identical to 1.0.0 (same SHA-256): no result changes.
- Reason: chapter 5 (data validation and asset-information laboratories).
- Version rule: additions only, backwards compatible -> minor release.
- Dependent artefacts: chapters 1-4 and 6 keep citing 1.0.0 (still valid);
  chapter 5 and later cite 1.1.0.

## 1.0.0 — 2026-11-14
- First release: seed ratings, assumptions ledger A-001..A-013, scenarios S0 and S1,
  synthetic hourly resource year (seed 20260101), three hand-calculation subsets,
  fictional PV module PVM-550 and wind turbine WT-5.0-150 with power curve.
- Reason: baseline for the book's worked examples.
- Dependent artefacts: none yet.
