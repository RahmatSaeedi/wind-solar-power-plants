# Chapter 21 plan: Project economics and contracts (budget 110 pp; core chapter)

Handoff: 13 bullets + worked examples (compare alternatives under yield/financing/replacement
assumptions; illustrative cash-flow and debt-service schedule; DSCR/LLCR; downside stress; why
lowest capex, highest IRR or one P90 does not establish bankability); blueprint A-G; audit row 21
(theory: economics, finance, contracts, bankability, verified carbon assumptions; applied: compare
economics and finance structures under base/downside; design: sources/uses, funding, contract,
diligence and risk-allocation assumptions; calculation: NPV/IRR/LCOE limits, cash flow, DSCR/LLCR,
debt sizing, service revenue, carbon only verified or sensitivity; manufacturing: equipment cost,
warranty, quality, replacement, lender evidence; implementation: tested cash-flow/debt model,
diligence register, contract/finance risk matrix; no assumed market or carbon availability).

Safeguards: no legal advice (commercial concepts only); no universal thresholds (DSCR, gearing,
tenor, reserve months all labelled illustrative, A-304..); no tax law of any country (teaching tax
rate and straight-line depreciation only); carbon and service revenues only as labelled
sensitivities unless verified; Plant P figures teaching.

## Companion
- plantp/finance.py (new, name checked): escalation index and real/nominal conversion, capex
  phasing and IDC, straight-line depreciation and tax with loss carry-forward, working capital,
  CFADS, annuity and sculpted debt, debt sizing by DSCR and gearing, DSRA, DSCR/LLCR, equity
  IRR, LCOE (real/nominal), an independent DSCR check, break-even search. Tests test_ch21_finance.py.
- companion/ch21: sources (cost breakdown from A-287 + development, owner's costs, contingency;
  opex lines incl. water from ch18/ch10; replacements ch9/ch19; decommissioning; PPA; finance terms
  A-304..A-310), examples_a (costs, phasing, real vs nominal, FX), examples_b (NPV/IRR/LCOE,
  tariffs, curtailment, availability), examples_c (LDs, guarantees, risk matrix), lab_d (model +
  checks + alternatives + tornado), examples_e (revenue pathways, services, carbon sensitivity,
  payment security), lab_f (worked schedule DSCR/LLCR, sculpting vs annuity, sizing, covenants),
  lab_g (stress and break-even, CP register), integrated, worked.
