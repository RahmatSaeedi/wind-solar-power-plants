# Chapter 44 plan: power converters, inverters and control-electronics manufacturing (budget 95 pp, plan for ~105)

Handoff: 8 bullets (theory; product decomposition; design process; manufacturing/assembly; quality
and testing; software implementation - non-deployable simulations of MPPT and state machines with
boundary tests and fault injection; integration; worked examples - loss budget, MPPT on a synthetic
curve, thermal-resistance script, automated tests of a simulated state machine). Blueprint A-D
(checked by tools/check_coverage.py). Audit row 44.

Running product: Plant P's PV central inverter of ch 9 (fictional PCI-5500: 5.5 MVA, four NPC stacks
of 1.375 MVA, 600 V AC, 1000 V DC, 3 kHz, 24 IGBT modules a stack, liquid cooled), ten units for the
ten PV blocks, built in a fictional factory; the turbine converter and the BESS PCS are named where
the factory evidence differs.

Overlap rule: ch 9 has the converter theory and design: topologies, PWM, losses (closed form and
switched), NPC, Foster thermal, cycle life, efficiency fits, derating, LCL, DC link, FRT, gate drive,
busbar overshoot, cooling heat, FIT reliability, capacitor life, EMC common-mode currents, MPPT
algorithms. Ch 44 reuses those numbers and goes to the factory: thermal interface and mounting,
parallel-module sharing with part spread, capacitor ripple sharing, solder-joint fatigue, insulation
distances as a design-for-manufacture check, PCB assembly flow and defect escape, firmware and
parameter configuration control, serialisation, end-of-line tests, non-live functional test as a
simulated state machine with fault injection, MPPT efficiency as test evidence, supplier evidence.

Safeguards: no field-ready firmware or control code, no live or energised procedures, no process
recipes (reflow profiles, solder alloys' temperatures, conformal-coat cure); IPC and IEC standards
named only when registered (STD-044..054; IPC-A-610J, J-STD-001J, IPC-6012F to register).

## Sections (files)
- `_44-a-architecture.qmd` A. product and electrical architecture: product tree with masses, costs,
  FIT (ch 9); power stage, semiconductors, DC link, magnetics, busbars, sensors, gate drive, control
  board, firmware, cooling, protection; interfaces to PV, transformer, PPC, SCADA.
- `_44-b-dfm.qmd` B. design for manufacture and reliability: thermal stack with TIM and voids,
  parallel modules with Vce spread, capacitor ripple sharing by ESR, solder fatigue from the daily
  cycle, insulation distances (teaching values), component stress derating check, busbar joints,
  rework limits, configuration baseline.
- `_44-c-factory.qmd` C. factory build and verification: PCB assembly flow and defect escape,
  module mounting record, firmware load with hash, serialisation and genealogy, end-of-line tests,
  environmental and EMC qualification by purpose, supplier evidence and counterfeits.
- `_44-d-lab.qmd` D. integration lab: loss/thermal budget with factory spread (Monte Carlo), non-live
  functional test sequence as a simulated state machine with fault injection and tests, MPPT
  efficiency on a synthetic curve, interface trace to PV/wind/transformer/PPC/SCADA.
- `_44-y-plantp.qmd`, `_44-z-assessment.qmd`.

## Companion
Module `plantp/convmfg.py`; chapter scripts `companion/ch44/` (sources, examples_a/b/c, lab_d,
integrated, worked, rounds as needed); tests `test_ch44_convmfg.py`.

## Ledgers
D-048 converter manufacturing and acceptance basis; assumptions from A-466; unknown U-125 (maker's
qualification evidence and firmware release records); documents (check the register).
