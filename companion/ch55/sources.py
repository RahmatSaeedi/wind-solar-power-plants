"""Chapter 55 sources: Iran, from the source research of 2026-11-17
(outline/research/ch55-iran-sources.md). Each fact keeps its status:
verified = official text read (the Majlis Research Center print of the
Cabinet or Majlis text, or the authority's own site); project-dependent;
to-confirm (incl. 'secondary' = news or unofficial summaries only).
Approval durations, the certificate and the Plant P data are TEACHING
values (A-552 to A-556); the institutions, laws and rules are as sourced.
"""
from __future__ import annotations

from datetime import date

COUNTRY = "Iran"
ACCESSED = date(2026, 11, 17)

MAJLIS = "Majlis Research Center print (via FAOLEX)"
DASTOUR = "dastour.ir print of the law (2016, via FAOLEX)"
REPLACED = ("1402/1403 text read; bylaw reported replaced by No. 26073/T65655H "
            "of 1405/2/30 (news) - re-read the new text")


def F(i, topic, text, status, src, doc=None, secondary=False, ask="project team"):
    return dict(id=f"IR-{i:02d}", topic=topic, text=text, status=status, source=src,
                doc_date=doc, secondary=secondary, ask=ask)


FACTS = [
    # A - authorities and approvals
    F(1, "A", "MoE buys renewable power under long-term guaranteed contracts",
      "verified", f"Law on Reform of Energy Consumption Pattern, Art 61; {DASTOUR}",
      date(2011, 2, 23)),
    F(2, "A", "SATBA is the counterparty of Art 61 contracts", "verified",
      f"Art 14 bylaw No. 142419/T61198H, 1402/8/10, Art 1; {MAJLIS}", date(2023, 11, 1)),
    F(3, "A", "SATBA's current official name (two forms in texts)", "to-confirm",
      "Nov 2024 amendment wording", date(2024, 11, 24), ask="SATBA"),
    F(4, "A", "Tavanir announces the export transmission tariff; upstream grid",
      "verified", f"Law 1401 Art 17 note; Art 4 bylaw Art 3(d); {MAJLIS}", date(2022, 11, 6)),
    F(5, "A", "IGMC issues grid-stability standards; all plants must comply",
      "verified", f"Art 4 bylaw No. 146796/T61218H, Art 6; {MAJLIS}", date(2023, 11, 7)),
    F(6, "A", "regional and distribution companies must take renewable power",
      "verified", f"Art 61 Note 2; {DASTOUR}", date(2011, 2, 23)),
    F(7, "A", "regional company CEOs issue permits with governorates", "to-confirm",
      "Mehr news, 5 Apr 2026", date(2026, 4, 5), secondary=True, ask="SATBA"),
    F(8, "A", "electricity market regulatory board: mandate not found", "to-confirm",
      "-", None, ask="Ministry of Energy"),
    F(9, "A", "bylaw on removing barriers to renewable plants, 1402/12/23",
      "verified", f"Cabinet No. 238700/T62054H; {MAJLIS}; text read", date(2024, 3, 13)),
    F(10, "A", "that bylaw lapsed ~Mar 2026; replaced 1405/2/30 (news)", "to-confirm",
      "Art 6 of the bylaw; ANA and Iran Daily reports", date(2026, 5, 20),
      secondary=True, ask="Cabinet secretariat / SATBA"),
    F(11, "A", "amended 1403/9/4 under Seventh Plan Art 46(a), aim 30,000 MW",
      "verified", f"No. 134137/T63365H, Gazette 23237; {MAJLIS}", date(2024, 11, 24)),
    F(12, "A", "regulatory framework of amendment Art 12: adopted?", "to-confirm",
      "amendment Art 12", date(2024, 11, 24), ask="Ministry of Energy"),
    F(13, "A", "SATBA construction permit; steps devolved to provinces", "to-confirm",
      "Taadol 7 Dec 2025; Mehr 20 Jul 2026", date(2026, 7, 20), secondary=True,
      ask="SATBA"),
    F(14, "A", "aviation obstacle rule for wind turbines not found", "to-confirm",
      "cao.ir unreachable (403)", None, ask="Civil Aviation Organization"),
    F(15, "A", "foreign investment through the investment organisation", "to-confirm",
      "FIPPA Art 5, unofficial translation", date(2002, 5, 31), secondary=True,
      ask="Organization for Investment (OIETAI)"),
    # B - grid, export, water, land
    F(16, "B", "industry plants: adjacent substation and line by developer",
      "project-dependent", f"Art 4 bylaw Art 3(d); {MAJLIS}", date(2023, 11, 7),
      ask="regional electricity company"),
    F(17, "B", "connection voltages 63/230/400 kV named; 132 kV not found",
      "to-confirm", "Mehr news, 21 Sep 2025", date(2025, 9, 21), secondary=True,
      ask="regional electricity company"),
    F(18, "B", "transmission open for sale/export; no transmission fees",
      "to-confirm", f"amendment Art 10(a),(c); {MAJLIS}; {REPLACED}", date(2024, 11, 24), ask="SATBA"),
    F(19, "B", "no published grid code or wind/PV connection document found",
      "to-confirm", "searches; sites unreachable", None, ask="IGMC"),
    F(20, "B", "metering, SCADA and 'visibility' rules: specification not found",
      "to-confirm", "ISNA/Tejarat News, 12 May 2026", date(2026, 5, 12), secondary=True,
      ask="IGMC"),
    F(21, "B", "groundwater and surface-water use need permits (WRM services)",
      "verified", "wrm.ir service list", None),
    F(22, "B", "which regional water company; water for cleaning", "project-dependent",
      "wrm.ir", None, ask="regional water company"),
    F(23, "B", "national land allocated for wind/solar via SATBA and Agri. Jihad",
      "to-confirm", f"renewables bylaw Arts 1-4; amendment Art 2; {MAJLIS}; {REPLACED}",
      date(2024, 11, 24), ask="SATBA"),
    F(24, "B", "lease capped at 20 % of land value; land back if idle 1 year",
      "to-confirm", f"renewables bylaw Arts 1, 4; {MAJLIS}; {REPLACED}", date(2024, 3, 13), ask="SATBA"),
    F(25, "B", "land directive No. 020/184659, 1403/7/29 (header read)", "verified",
      "Ministry of Agriculture Jihad (via FAOLEX)", date(2024, 10, 20)),
    F(26, "B", "foreign persons eligible for land allocation?", "to-confirm",
      "bylaw says 'Iranian persons'", date(2024, 3, 13), ask="local counsel"),
    # C - standards and evidence
    F(27, "C", "INSO is the national standards body", "verified", "inso.gov.ir", None),
    F(28, "C", "mandatory import list: solar inverters up to 5 kW", "verified",
      "INSO import list, Aban 1405", date(2026, 10, 23)),
    F(29, "C", "mandatory list: no PV module or wind turbine entry", "verified",
      "INSO lists (file of 30 Jun 2026)", date(2026, 6, 30)),
    F(30, "C", "mandatory: power transformers INSO 2620-1, MV cables 3569", "verified",
      "INSO mandatory standards list", date(2026, 6, 30)),
    F(31, "C", "national adoptions of IEC 61215/61730/62109/61400 not found",
      "to-confirm", "INSO catalogue did not load", None, ask="INSO"),
    F(32, "C", "MoE sets criteria for renewable equipment, domestic priority",
      "to-confirm", f"amendment Art 7(a); {MAJLIS}; {REPLACED}", date(2024, 11, 24), ask="SATBA"),
    F(49, "C", "mandatory: stationary VRLA (4868-22), lithium cells (6618-3)",
      "verified", "INSO mandatory standards list", date(2026, 6, 30)),
    # E - grid services
    F(33, "E", "no ancillary-service product for wind/PV published", "to-confirm",
      "searches", None, ask="IGMC"),
    F(34, "E", "green-electricity board on the Energy Exchange", "verified",
      f"Art 14 bylaw Art 6 note; amendment Art 10(b); {MAJLIS}", date(2024, 11, 24)),
    # F - finance and fiscal
    F(35, "F", "fuel saved paid as tradable crude-oil 'energy drafts'", "verified",
      f"Law of 1401/8/15 Art 14 and its bylaw; {MAJLIS}", date(2023, 11, 1)),
    F(36, "F", "output belongs to the investor; no mandated prices", "to-confirm",
      f"amendment Arts 9-10; {MAJLIS}; {REPLACED}", date(2024, 11, 24), ask="SATBA"),
    F(37, "F", "export licences for private renewables after domestic supply",
      "verified", f"Law 1401 Arts 4, 17; {MAJLIS}", date(2022, 11, 6)),
    F(38, "F", "utility-scale PPA term, currency, indexation, security", "to-confirm",
      "not found", None, ask="SATBA / local counsel"),
    F(39, "F", "FX and rial financing package; import orders to 30,000 MW",
      "to-confirm", f"amendment Arts 7-8; {MAJLIS}; {REPLACED}", date(2024, 11, 24), ask="SATBA"),
    F(40, "F", "US sanctions regulations (31 CFR 560), actions to Nov 2026",
      "verified", "OFAC Iran sanctions page", date(2026, 11, 9)),
    F(41, "F", "EU Regulation 2025/1975 amending 267/2012", "verified",
      "EUR-Lex", date(2025, 9, 29)),
    F(42, "F", "renewable tax and customs exemptions", "to-confirm", "not found", None,
      ask="local tax advisor"),
    # G - social and land
    F(43, "G", "wind/solar above 100 MW: no EIA study, DOE inquiry instead",
      "to-confirm", f"renewables bylaw Art 5 (text read); {MAJLIS}; {REPLACED}", date(2024, 3, 13), ask="SATBA"),
    F(44, "G", "new EIA bylaw 1405 lists wind/solar of 300 MW and above",
      "to-confirm", "scanned text via FAOLEX, not re-read", date(2026, 5, 25),
      ask="Department of Environment"),
    F(45, "G", "setbacks: gas, power, roads, heritage, passive defence",
      "to-confirm", f"renewables bylaw Art 3; {MAJLIS}; {REPLACED}", date(2024, 3, 13), ask="SATBA"),
    F(46, "G", "land applicant pays compensation and improvements", "to-confirm",
      f"renewables bylaw Art 1(3); {MAJLIS}; {REPLACED}", date(2024, 3, 13), ask="SATBA"),
    F(47, "G", "consultation or resettlement rule below 300 MW not found",
      "to-confirm", "-", None, ask="Department of Environment / counsel"),
    F(48, "G", "cultural-heritage clearance procedure", "to-confirm", "mcth.ir unreachable",
      None, ask="Ministry of Cultural Heritage"),
]

APPROVALS = {   # teaching durations in months; statuses from the facts
    "S1": dict(what="eligibility and technical competence (SATBA)", who="SATBA",
               months=2.0, after=[], status="verified"),
    "S2": dict(what="national land allocation and land-use change", who="SATBA, Agri. Jihad",
               months=4.0, after=["S1"], status="to-confirm"),
    "S3": dict(what="DOE inquiry after allocation (one week)", who="Department of Environment",
               months=0.5, after=["S2"], status="to-confirm"),
    "S4": dict(what="construction permit", who="SATBA / province",
               months=2.0, after=["S2", "S3"], status="to-confirm"),
    "S5": dict(what="connection application and studies", who="regional company / IGMC",
               months=6.0, after=["S1"], status="to-confirm"),
    "S6": dict(what="connection agreement or commitment letter", who="Tavanir / regional",
               months=2.0, after=["S5"], status="to-confirm"),
    "S7": dict(what="water-use permit for construction and cleaning", who="regional water co.",
               months=3.0, after=["S2"], status="project-dependent"),
    "S8": dict(what="sale route: Art 61 contract, green board or bilateral",
               who="SATBA / Energy Exchange", months=3.0, after=["S4"], status="to-confirm"),
    "S9": dict(what="import-order registration and FX allocation", who="MIMT / Central Bank",
               months=2.0, after=["S4"], status="to-confirm"),
}

GRID_NEED = {   # ch 28 study inputs: item -> quality needed
    "fault levels max and min at the POC": "model",
    "network equivalent for dynamic studies": "model",
    "connection voltage and substation bay": "value",
    "substation and line capacity available": "value",
    "remote-end protection and reclosing": "value",
    "background harmonics and allocation": "measured",
    "reactive power requirement": "value",
    "fault ride-through requirement": "value",
    "frequency response requirement": "value",
    "telemetry list and protocol": "value",
    "revenue metering specification": "value",
    "curtailment and dispatch rules": "value",
}
GRID_GIVEN = {"connection voltage and substation bay": "value",
              "curtailment and dispatch rules": "value"}
GRID_REQUEST_TO = "IGMC and the regional company, in writing"

CERT = dict(what="maker's type certificate of the 5.5 MVA PV inverter (ch 44)",
            model="PCI-5500", standard="IEC 62109-1:2010",
            tests=["safety", "EMC", "unit fault ride-through"],
            ambient_max_c=45, altitude_m=1000, valid_to=date(2029, 6, 30),
            accreditation="test lab accredited (scope listed)")
CERT_NEED = dict(model="PCI-5500", standard="IEC 62109-1:2010",
                 tests=["safety", "EMC", "unit fault ride-through",
                        "national requirement (if any)"],
                 ambient_max_c=50, altitude_m=1500, delivery=date(2028, 1, 15),
                 plant_level=["reactive power at the POC", "plant ride-through"])
CERT_NATIONAL = ("INSO's mandatory import list names solar inverters up to 5 kW"
                 " (IR-28); a 5.5 MVA unit is not on it - whether another"
                 " national rule applies is to-confirm (IR-31)")

TRACES = {
    "IR-30": ("power transformers to the mandatory national standard", {
        "source": "INSO mandatory list: power transformers, INSO 2620-1",
        "design": "ch 25/43 rating and losses calc; one-line PLP-ELE-DWG-0005",
        "procurement": "order clause: INSO conformity certificate before shipping",
        "construction": "certificate checked at receipt, before the transformer is set",
        "test": "factory tests (ch 43) plus any national test INSO requires",
        "approval": "INSO certificate; customs clearance; owner's acceptance",
        "retained": "certificate, test reports, receipt record (ch 50 handover)"}),
    "IR-43": ("DOE inquiry instead of an EIA study (wind/solar > 100 MW)", {
        "source": "renewables bylaw Art 5, 1402/12/23 (text read 2026-11-17)",
        "design": "layout outside the setbacks (IR-45); habitat screen (ch 33)",
        "procurement": "E&S consultant scope: inquiry file, not a full EIA",
        "construction": "works start only after the inquiry answer or silence",
        "test": "not applicable: a permit, not a technical test",
        "approval": "DOE answer, or a week of silence (amendment)",
        "retained": "inquiry letter, delivery proof, answer or silence date"}),
    "IR-05": ("comply with IGMC grid-stability standards", {
        "source": "Art 4 bylaw Art 6 - but WHICH standards? (IR-19 to-confirm)",
        "design": None, "procurement": None, "construction": None, "test": None,
        "approval": None, "retained": None}),
}

SERVICES = [
    ("export within network capacity", "verified", "IR-18: transmission open, no fees"),
    ("green-board sales", "verified", "IR-34: Energy Exchange board"),
    ("reactive power / voltage control", "to-confirm", "IR-19: no document found"),
    ("frequency response and reserve", "to-confirm", "IR-33: no product found"),
    ("ride-through", "to-confirm", "IR-19: no published value"),
    ("curtailment compensation", "to-confirm", "IR-38: contract terms not found"),
]

FINANCE = [
    ("Art 61 guaranteed purchase (contract form)", "law + bylaw", "verified", "SATBA, counsel"),
    ("fuel-saving energy drafts", "law 1401 Art 14 + bylaw", "verified", "counsel"),
    ("sale by green board or bilateral contract", "amended bylaw", "verified", "counsel"),
    ("PPA term, currency, indexation, security", "not found", "to-confirm", "counsel"),
    ("FX package and import orders", "amended bylaw", "verified", "bank, counsel"),
    ("repatriation of profit (FIPPA)", "unofficial translation", "to-confirm", "counsel"),
    ("tax and customs exemptions", "not found", "to-confirm", "tax advisor"),
    ("US and EU sanctions", "OFAC, EUR-Lex", "verified", "sanctions counsel"),
    ("land lease and compensation cost", "renewables bylaw", "verified", "counsel"),
]
