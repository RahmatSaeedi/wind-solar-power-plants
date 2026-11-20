# resource_tool 1.0.0 - Plant P resource analysis (teaching tool)

Turns the Plant P Reference Data Pack into checked energy figures and a
report.
Educational software for the fictional Plant P: never connect it to a plant.

## Install and check (once)

    python -m pip install numpy pandas pyyaml   # versions: see report
    python -m companion.ch05.check_all          # ends "release may proceed"

## Run procedure (every time, from the project root)

1. python -m companion.ch05.resource_tool validate-raw
   checks the 10-min logger file; writes companion/ch05/output/qc.json
2. python -m companion.ch05.resource_tool run companion/ch05/config/run_S0.yml
   writes results.json and hourly.csv to the folder named in the run file
3. python -m companion.ch05.resource_tool report companion/ch05/output/S0
   writes PLP-GEN-REP-0002_rev-A.md next to the results

Exit codes: 0 done; 1 done, but the data have problems (see the report);
2 not done (bad arguments, configuration or missing file).

## Inputs

- run file (YAML): checked against plantp.schema.RUN_SCHEMA before
  anything runs
- data pack release named in the run file: checksums verified first

## Outputs

- results.json: energies, release, SHA-256 of inputs and run file, versions
- hourly.csv: PV, wind and export power for 8760 hours
- report (Markdown): inputs, results, raw-data checks, limitations, sign-off

## Limits

Horizontal irradiance on the array; NOCT cell temperature; lumped losses
(A-097); wind power curve at site density by the equivalent speed (D-008);
one synthetic year. Chapters 10, 11, 13 and 15 replace these models.
