# Adversarial accuracy review, 2026-11-18/19

A whole-book pass to find factual, physical, arithmetic and citation errors before publication.
Every finding below was checked against the source text, the companion outputs or an official
page before it was applied; the original files are backed up outside the project.

## Method

1. **Automated checks** (`numcheck.py`, `mathcheck.py` in this folder):
   - numbers in the 3,211 interpretation paragraphs («تفسیر») compared with the program output
     they interpret (569 flags, triaged by the reviewers: almost all were inputs or derived values);
   - about 1,950 purely numeric equalities written in LaTeX re-evaluated (2 real slips).
2. **Eighteen independent reviewers**, each with a narrow scope:
   - 15 chapter groups (ch 1-54, 58, 59, appendix B): formulas, physics, real-world facts, safety
     statements, hand checks («وارسی»), interpretation lines and answer keys;
   - 2 reviewers re-verified all 191 rows of `glossary/standards-register.csv` against official
     catalogues (IEC, ISO, IEEE, UL, NFPA, UNECE, NIST, IFC);
   - 1 reviewer re-checked the "verified" statements of the three country dossiers (ch 55-57).
3. Fixes applied by `apply_findings.py` (exact, unique find/replace) or by hand; companion code
   fixed where an output was wrong, outputs regenerated and diffed, dependent figures rebuilt.

## Findings (305 in total; `*.jsonl` here, one object per finding)

| File | Scope | Findings |
|---|---|---|
| OWN | automated arithmetic check | 2 |
| TA-TP | chapter groups | 179 |
| S1, S2 | standards register and edition citations | 113 |
| D1 | country dossiers | 11 |

The most consequential corrections:

- **ch 8** DFIG slip power violated the energy balance (P_stator = P_mech / (1 - s), not P_mech);
  code `plantp.machines.dfig_rotor_power`, outputs and answers corrected (1.6 -> 1.23 MW).
- **ch 43** winding eddy-loss ratio was half the true value (peak field squared averages to 1/3);
  `plantp.xfmrdesign.eddy_ratio` fixed (2.15 % -> 4.30 % for 2.5 mm strands).
- **ch 49** sediment-pond runoff volume halved by a triangular hydrograph (C i A t restored:
  1,655 -> 3,310 m3, pond 54 % -> 27 %).
- **ch 37** concurrent-outage availability counted excluded hours twice (99.460 -> 99.055 %).
- **ch 34** event-order simulation placed every first event at a bin start (96 % -> 50 %).
- **ch 10** string fuse aligned with ch 6/26 and IEC 62548 (1.5 Isc lower bound: 25 A, not 20 A).
- **ch 4** radiography crack orientation was reversed; **ch 2** 1e-4 MWh is 100 Wh.
- **ch 52** maintenance budget per MW used 150 MW instead of Plant P's 110 MW (23.8 k u/MW).
- **ch 28** IEC 60909 factor c applied twice in the teaching model: stated explicitly (~10 %
  conservative; 6.56 kA vs 7.21 kA at the POC).
- **ch 24** 132 kV dielectric loss used the MV loss tangent (now 0.001: 1.1 W/m, ~7 %).
- **Standards:** superseded editions updated (IEC 61400-4:2025, IEC 60909-0:2026,
  IEC TS 63102:2026, UL 9540A 6th ed. 2026, IEC 62933-5-2:2025, ISO 14025:2026,
  IEC 60034-1:2026, ISO 20816-1:2026, ISO/IEC/IEEE 12207:2026); 26 rows of the register
  corrected; chapter 58's register statistics regenerated (open items 46 -> 39).
- **Iran (ch 55):** the 1402/12/23 renewables bylaw is reported (news, Iran Daily and ANA) to
  have been replaced by bylaw 26073/T65655H of 1405/2/30, whose official text was not read.
  Nine statements and four approval steps that rested only on the replaced texts are now
  «نیازمندِ تأیید» (verified share 57 % -> 39 %); ch 56, 57, 59 and appendix X updated.
- About 60 cross-references to the wrong chapter (left from an older chapter numbering) fixed.

## Handled differently from the reviewer's proposal

- TJ-01/02 (ch 28 c factor): a stated-convention note instead of re-running the chapter's model.
- TE-10-03/05 (ch 10 fuse): code factor 1.4 -> 1.5 and the text rewritten by hand.
- TI-01/02 (ch 24): the code now uses a per-cable loss tangent; text rewritten by hand.
- TK-02 (ch 30 Scruton row): relabelled "tuned mass damper" instead of dropped.
- TP-09 (ch 53 sensitivity base row from different random draws): not changed; the
  conclusion is the same in every case.
- D1-08 (ch 55 IR-01/06 source): label corrected to the dastour.ir print; status kept
  verified (the print reproduces the law's text). Re-read at an official site when reachable.

## Not reachable during the review

STD-089 (iecre.org), STD-135, STD-141, STD-142, STD-191 (iso.org returned 403); several
Afghan government sites and the scanned 1405 Iranian EIA bylaw (no text layer).
