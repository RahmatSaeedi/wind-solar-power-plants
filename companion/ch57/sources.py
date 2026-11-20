"""Chapter 57 sources: Tajikistan, from the source research of 2026-11-17
(outline/research/ch57-tajikistan-sources.md) with the author's spot-checks
of the Sughd RFQ (2024) and of Government Resolution No. 449 (01.07.2026).
Statuses: verified = official text or official page read (laws read in the
FAOLEX / UN-ESCAP repositories count, because the national legal portals
were unreachable on the day); project-dependent; to-confirm (incl.
'secondary' sources: press, IFI reports, unofficial translations). The
approval durations, the certificate, the equipment options, the site
values and the Plant P data are TEACHING values (A-562 to A-566).
"""
from __future__ import annotations

from datetime import date

COUNTRY = "Tajikistan"
ACCESSED = date(2026, 11, 17)


def F(i, topic, text, status, src, doc=None, secondary=False, ask="project team"):
    return dict(id=f"TJ-{i:02d}", topic=topic, text=text, status=status, source=src,
                doc_date=doc, secondary=secondary, ask=ask)


R449 = "Gov. Resolution 449 (01.07.2026), RES entry and sale rules"
RFQ = "MEWR Sughd 200 MW solar RFQ (21.08.2024)"
RD = date(2026, 7, 1)
QD = date(2024, 8, 21)

FACTS = [
    # A - authorities and approvals
    F(1, "A", "MEWR is the ministry that tenders solar IPPs", "verified",
      f"mewr.tj; {RFQ}", QD),
    F(2, "A", "Barqi Tojik: generation, market operator directorate; PPA buyer",
      "verified", f"barqitojik.tj; {RFQ}", QD),
    F(3, "A", "SIB transmission company (Res. 330, 2019); the TSO in the RFQ",
      "verified", f"shib.tj; {RFQ}", QD),
    F(4, "A", "STB distribution company: tariffs, billing", "verified",
      "STB site", date(2026, 11, 17)),
    F(5, "A", "no separate system operator; one planned with single buyer 2027",
      "to-confirm", "Asia-Plus 24.12.2025", date(2025, 12, 24), secondary=True,
      ask="MEWR"),
    F(6, "A", "tariffs set by the Government on the antimonopoly body's proposal",
      "verified", "Energy Law No. 33, Art 15 (FAOLEX); Law 1909 (2022)", date(2022, 7, 19)),
    F(7, "A", "state energy supervision approves RES supply designs > 15 kW",
      "verified", f"{R449}, items 16, 25, 45", RD),
    F(8, "A", "Tajikstandart: standards, metrology, certification", "verified",
      "standard.tj", date(2026, 11, 17)),
    F(9, "A", "environmental protection committee: site and remit", "to-confirm",
      "egov.tj listing; no own site found", None, secondary=True,
      ask="environment committee"),
    F(10, "A", "State Committee on Investments signs investment agreements",
      "verified", f"investcom.tj; {RFQ}", QD),
    F(11, "A", "does generation need a permit under Law 1968 (2023), from whom",
      "to-confirm", "Permit System Law No. 1968 (FAOLEX); list not read",
      date(2023, 6, 22), ask="MEWR / counsel"),
    F(12, "A", "> 1 MW: price by competition; PPA >= 15 yr with the single buyer",
      "verified", f"{R449}, items 7, 34", RD),
    F(13, "A", "the single buyer is not yet designated", "project-dependent",
      f"{R449} (defines the role)", RD, ask="MEWR"),
    F(14, "A", "Sughd: 25-yr PPA with Barqi Tojik, USD tariff paid in somoni",
      "verified", f"{RFQ}, 2.4 (re-read by the author)", QD),
    F(15, "A", "award of the Sughd tender", "to-confirm", "shortlist in the press",
      None, secondary=True, ask="MEWR"),
    F(16, "A", "investment agreement Jan 2026 for two 250 MW solar plants",
      "to-confirm", "Khovar 13.01.2026", date(2026, 1, 13), secondary=True,
      ask="State Committee on Investments"),
    F(17, "A", "state energy-expertise conclusion before design approval",
      "verified", "Energy Saving Law amendment No. 1911 (FAOLEX)", date(2022, 7, 19)),
    F(18, "A", "which body issues the energy-expertise conclusion", "to-confirm",
      "not stated in the amendment", None, ask="MEWR"),
    F(19, "A", "a new Energy Law was ordered in 2025; none adopted found",
      "to-confirm", "press, Jan 2025", date(2025, 1, 15), secondary=True, ask="MEWR"),
    # B - grid, export, water, land, site
    F(20, "B", "two 220 kV lines cross the Sughd site; Khujand substation 18 km",
      "verified", f"{RFQ} (re-read by the author)", QD),
    F(21, "B", "transmission 500/220/110 kV; distribution 35 kV and below",
      "to-confirm", "ADB TA report with the 2018 draft grid code", date(2019, 5, 1),
      secondary=True, ask="SIB"),
    F(22, "B", "no adopted grid code; the 2018 code is a consultant draft",
      "to-confirm", "ADB TA report (draft)", date(2019, 5, 1), ask="SIB"),
    F(23, "B", "technical conditions free in 30 working days; 50 Hz, anti-islanding",
      "verified", f"{R449}, items 14-19", RD),
    F(24, "B", "> 1 MW: SCADA, real-time data, remote curtailment, hourly forecast",
      "verified", f"{R449}, items 20-21, 39-41", RD),
    F(25, "B", "metering > 15 kW: class 1.0 or 0.5S at the boundary, ASKUE, register",
      "verified", f"{R449}", RD),
    F(26, "B", "curtailment allowed; rules: no breach; model PPA: lost profit paid",
      "verified", f"{R449} and its model PPA (inconsistent)", RD),
    F(27, "B", "hydro is ~98 % of energy; output falls in autumn and winter",
      "to-confirm", "press and IFI reports", date(2026, 11, 12), secondary=True,
      ask="Barqi Tojik"),
    F(28, "B", "installed > 6,700 MW; 2025 generation 24 TWh", "to-confirm",
      "Interfax 12.11.2026", date(2026, 11, 12), secondary=True, ask="Barqi Tojik"),
    F(29, "B", "south-west back in CAPS June 2024; north expected 2026",
      "to-confirm", "press", date(2024, 6, 15), secondary=True, ask="SIB"),
    F(30, "B", "CASA-1000: 1,300 MW summer export; Afghan section by 2027",
      "to-confirm", "press", date(2026, 6, 1), secondary=True, ask="SIB"),
    F(31, "B", "Water Code 1688 (2020): special water use needs a permit",
      "to-confirm", "unofficial translation", date(2020, 4, 2), secondary=True,
      ask="water-management body"),
    F(32, "B", "model PPA: low water / national water deficit is force majeure",
      "verified", f"{R449}, model PPA", RD),
    F(33, "B", "Sughd site: flood embankments; a decommissioned 500 kV line",
      "verified", f"{RFQ}", QD),
    F(34, "B", "SNiP RT 22-07-2018 seismic zones 7-9+ MSK-64; Khujand 8, Dushanbe 9",
      "verified", "SNiP RT 22-07-2018, Annex 2 (copy hosted by KazNIISA)",
      date(2018, 7, 1)),
    F(35, "B", "mudflow warnings for the Sughd foothills, Oct-Nov 2026", "verified",
      "khf.tj", date(2026, 10, 31)),
    F(36, "B", "land is state property; foreign persons get use rights only",
      "to-confirm", "Land Code (unofficial 2012 translation)", date(2012, 1, 1),
      secondary=True, ask="counsel"),
    F(37, "B", "heavy-load routes and logistics for blades and transformers",
      "to-confirm", "not found", None, ask="logistics forwarder"),
    F(38, "B", "wind O&M capability in the country", "to-confirm", "not found", None,
      ask="market survey"),
    F(39, "B", "a national EPC (TGEM) builds the Ayon plants and Rogun works",
      "to-confirm", "Interfax", date(2026, 8, 20), secondary=True, ask="market survey"),
    # C - standards and evidence
    F(40, "C", "rules cite GOST 32144-2013; model PPA cites old GOST 13109-97",
      "verified", f"{R449} and model PPA (inconsistent)", RD),
    F(41, "C", "which edition of the PUE is in force", "to-confirm",
      "cited without edition", None, ask="state energy supervision"),
    F(42, "C", "Tajikistan takes part in the interstate (EASC) standards system",
      "to-confirm", "easc.by", None, secondary=True, ask="Tajikstandart"),
    F(43, "C", "imports certified by Tajikstandart; regulations mostly unpublished",
      "to-confirm", "US Commercial Guide 21.01.2026", date(2026, 1, 21),
      secondary=True, ask="Tajikstandart"),
    F(44, "C", "GOST IEC adoption of PV and wind standards", "to-confirm",
      "not found", None, ask="Tajikstandart"),
    F(45, "C", "RES law: conformity certificate for RES energy and products",
      "to-confirm", "RES Law 587, Arts 17-18 (2010 text); 2022 effect unread",
      date(2010, 1, 12), ask="Tajikstandart"),
    F(46, "C", "PV equipment must be on the Tier-1 list", "verified",
      f"{R449}, item 19", RD),
    # E - grid services
    F(47, "E", "no reserve, ancillary or grid-forming product published",
      "to-confirm", f"searches; {R449} 'recommends' storage response", None,
      ask="SIB"),
    # F - finance
    F(48, "F", "retail tariffs incl. VAT: homes 0.4137, industry 0.9465 TJS/kWh",
      "verified", "barqitojik.tj/tariffs (decision 29.12.2025)", date(2025, 12, 29)),
    F(49, "F", "paid in somoni in 10 banking days, <= 30 days after month-end",
      "verified", f"{R449} and model PPA", RD),
    F(50, "F", "late payment: founder may 'engage state guarantees' (undefined)",
      "verified", f"{R449}", RD),
    F(51, "F", "convertibility: IMF Article VIII (2004); repatriation guarantees",
      "to-confirm", "IMF documents; Law 1299 not read", date(2024, 1, 1),
      secondary=True, ask="counsel / bank"),
    F(52, "F", "VAT exemption for renewable equipment to 2031 (Dec 2025)",
      "to-confirm", "press", date(2025, 12, 20), secondary=True, ask="tax advisor"),
    F(53, "F", "RFQ lists investment, PPP, arbitration, tax and land laws",
      "verified", f"{RFQ} (laws listed, not read)", QD),
    F(54, "F", "World Bank Group supports the Sughd tender", "verified", f"{RFQ}", QD),
    F(55, "F", "power-sector programme 2026-2030: 1,500 MW solar", "to-confirm",
      "press 25.11.2025 (number unknown)", date(2025, 11, 25), secondary=True,
      ask="MEWR"),
    # G - social and land
    F(56, "G", "Environmental Code No. 2299 (2026) adopted; in force when?",
      "to-confirm", "Spinform listing", date(2026, 10, 21), secondary=True,
      ask="environment committee"),
    F(57, "G", "ecological expertise and EIA rules (Law 818, Res. 532, 697)",
      "to-confirm", f"{RFQ} lists them; status after the 2026 Code unknown",
      date(2018, 11, 1), ask="environment committee"),
    F(58, "G", "the new Code has EIA chapters with public participation",
      "to-confirm", "table of contents only", date(2026, 10, 21), secondary=True,
      ask="environment committee"),
    F(59, "G", "heritage law, last revised 2017", "to-confirm", "listing",
      date(2017, 5, 30), secondary=True, ask="counsel"),
    F(60, "G", "compensation and resettlement rules", "to-confirm", "not found", None,
      ask="counsel / social specialist"),
    F(61, "G", "Sughd: a Key Biodiversity Area between site and substation",
      "verified", f"{RFQ}", QD),
]

APPROVALS = {   # teaching durations in months (A-562)
    "S1": dict(what="competitive procedure (qualification, bid, award)", who="MEWR",
               months=6.0, after=[], status="verified"),
    "S2": dict(what="investment agreement with the Government",
               who="State Committee on Investments", months=3.0, after=["S1"],
               status="verified"),
    "S3": dict(what="PPA with the single buyer (>= 15 years)", who="single buyer",
               months=3.0, after=["S1"], status="verified"),
    "S4": dict(what="technical conditions for connection", who="network company",
               months=1.5, after=["S1"], status="verified"),
    "S5": dict(what="grid connection agreement", who="SIB", months=3.0,
               after=["S4"], status="verified"),
    "S6": dict(what="ecological expertise / EIA conclusion", who="environment committee",
               months=6.0, after=["S1"], status="to-confirm"),
    "S7": dict(what="land use right and lease", who="land authority / Barqi Tojik",
               months=4.0, after=["S2"], status="project-dependent"),
    "S8": dict(what="state energy-expertise conclusion", who="(issuer to confirm)",
               months=2.0, after=["S5", "S6"], status="to-confirm"),
    "S9": dict(what="design approval, state energy supervision", who="supervision agency",
               months=2.0, after=["S8"], status="verified"),
    "S10": dict(what="permit under Law 1968, if any", who="(to confirm)", months=2.0,
                after=["S2"], status="to-confirm"),
    "S11": dict(what="special water-use permit", who="water-management body",
                months=2.0, after=["S7"], status="to-confirm"),
}

GRID_NEED = {
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
    "seasonal hydro and export pattern": "value",
}
GRID_GIVEN = {"revenue metering specification": "value",
              "curtailment and dispatch rules": "value"}
GRID_REQUEST_TO = "SIB (transmission) and the single buyer, in writing"

CERT = dict(what="maker's type certificate of the 5.5 MVA PV inverter (ch 44)",
            model="PCI-5500", standard="IEC 62109-1:2010",
            tests=["safety", "EMC", "unit fault ride-through"],
            ambient_max_c=45, altitude_m=1000, valid_to=date(2029, 6, 30),
            accreditation="test lab accredited (scope listed)")
CERT_NEED = dict(model="PCI-5500", standard="IEC 62109-1:2010",
                 tests=["safety", "EMC", "unit fault ride-through",
                        "conformity certificate (Tajikstandart)",
                        "seismic qualification, zone 8 MSK-64"],
                 ambient_max_c=44, altitude_m=600, delivery=date(2028, 1, 15),
                 plant_level=["reactive power at the POC", "plant ride-through"])
CERT_NATIONAL = ("imports are certified by Tajikstandart or approved bodies (TJ-43);"
                 " which standards apply to inverters is to-confirm (TJ-44)")

TRACES = {
    "TJ-25": ("revenue metering at the ownership boundary", {
        "source": "Resolution 449: class 1.0 or 0.5S, ASKUE, State Register",
        "design": "metering one-line with class 0.5S cores (ch 48)",
        "procurement": "meter type checked on the State Register",
        "construction": "meters installed and sealed at the boundary",
        "test": "accuracy certificates and ASKUE link test",
        "approval": "acceptance by the network company",
        "retained": "register entry, seal records, certificates"}),
    "TJ-24": ("SCADA and real-time data above 1 MW", {
        "source": "Resolution 449 items 20-21, 39-41",
        "design": "PPC and SCADA gateway (ch 34, 35)",
        "procurement": "gateway and protocol in the SCADA order",
        "construction": "links to the dispatch centre",
        "test": None, "approval": None, "retained": None}),
    "TJ-22": ("fault ride-through and reactive requirements", {
        "source": "none adopted (TJ-22) - a request to SIB",
        "design": None, "procurement": None, "construction": None, "test": None,
        "approval": None, "retained": None}),
}

SERVICES = [
    ("energy sale to the single buyer", "verified", "TJ-12: PPA >= 15 years"),
    ("remote curtailment and hourly forecasts", "verified", "TJ-24: obligation > 1 MW"),
    ("reactive power / power-factor control", "project-dependent",
     "TJ-23: 'recommended'; value in the technical conditions"),
    ("frequency response and reserve", "to-confirm", "TJ-47: no product found"),
    ("ride-through", "to-confirm", "TJ-22: no adopted code"),
    ("curtailment compensation", "to-confirm", "TJ-26: rules and model PPA differ"),
]

FINANCE = [
    ("offtaker and PPA form (model PPA)", "Resolution 449", "verified", "counsel"),
    ("price by competitive procedure", "Resolution 449", "project-dependent", "bid team"),
    ("currency: USD-fixed, paid in somoni", "Sughd RFQ (one tender)",
     "project-dependent", "counsel, bank"),
    ("payment within 10 banking days", "Resolution 449", "verified", "counsel"),
    ("assignment to lenders", "model PPA", "verified", "lenders' counsel"),
    ("late-payment remedy ('state guarantees')", "Resolution 449, undefined",
     "to-confirm", "counsel"),
    ("convertibility and repatriation", "IMF (secondary); Law 1299 unread",
     "to-confirm", "counsel, bank"),
    ("VAT exemption for equipment", "press", "to-confirm", "tax advisor"),
    ("investment agreement and arbitration law", "listed in the RFQ, not read",
     "to-confirm", "counsel"),
]

# equipment against local constraints (teaching values; None = unknown)
OPTIONS = {
    "central inverters 5.5 MVA": {"seismic zone qualified": None,
                                  "min ambient rating C": -25,
                                  "max part mass t": 12,
                                  "service techs in country": None},
    "string inverters 0.3 MVA": {"seismic zone qualified": 9,
                                 "min ambient rating C": -30,
                                 "max part mass t": 0.1,
                                 "service techs in country": 1},
    "wind 5 MW, 150 m rotor": {"seismic zone qualified": 8,
                               "min ambient rating C": -20,
                               "max part mass t": 90,
                               "service techs in country": None},
    "wind 3 MW, 120 m rotor": {"seismic zone qualified": 8,
                               "min ambient rating C": -30,
                               "max part mass t": 60,
                               "service techs in country": None},
}
CONSTRAINTS = {"seismic zone qualified": ("min", 8),
               "min ambient rating C": ("max", -25),
               "max part mass t": ("max", 70),
               "service techs in country": ("min", 1)}
