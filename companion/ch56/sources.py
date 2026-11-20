"""Chapter 56 sources: Afghanistan, from the source research of 2026-11-17
(outline/research/ch56-afghanistan-sources.md). Statuses: verified =
official text or official page read (incl. pages of the current de facto
authorities); project-dependent; to-confirm (incl. 'secondary' sources,
and pre-2021 instruments whose text was read but whose current
application could not be established - the review of earlier laws has no
published outcome). Approval durations, the certificate, the equipment
options and the Plant P data are TEACHING values (A-557 to A-561).
"""
from __future__ import annotations

from datetime import date

COUNTRY = "Afghanistan"
ACCESSED = date(2026, 11, 17)


def F(i, topic, text, status, src, doc=None, secondary=False, ask="project team"):
    return dict(id=f"AF-{i:02d}", topic=topic, text=text, status=status, source=src,
                doc_date=doc, secondary=secondary, ask=ask)


LAW16 = "Power Services Regulation law, OG 1231 (2016), MEW translation"

FACTS = [
    # A - authorities and approvals
    F(1, "A", "ministry site active; calls itself Ministry of Water and Energy",
      "verified", "mew.gov.af (posts to 1405/8/26)", date(2026, 11, 17)),
    F(2, "A", "DABS is the utility and signs private generation contracts",
      "verified", "DPMEA pages node/1852, node/2580", date(2026, 2, 11)),
    F(3, "A", "approval chain: investment committee, Economic Commission, DABS",
      "verified", "DPMEA Committee8 (2023), node/2613 (2026)", date(2026, 3, 3)),
    F(4, "A", "no written procedure, criteria or timelines published", "to-confirm",
      "DPMEA pages", date(2026, 3, 3), ask="Economic Commission secretariat"),
    F(5, "A", "2016 law: regulator is a ministry department; none found working",
      "to-confirm", f"{LAW16}, Arts 5, 7 - text read, application unknown",
      date(2016, 10, 18), ask="Ministry of Water and Energy"),
    F(6, "A", "2016 law: licence + ministry contract; generation licence <= 25 yr",
      "to-confirm", f"{LAW16}, Arts 8-11 - text read, application unknown",
      date(2016, 10, 18), ask="Ministry of Water and Energy"),
    F(7, "A", "NEPA site active; issues environmental permits", "verified",
      "nepa.gov.af", date(2026, 11, 17)),
    F(8, "A", "standards body renamed ASQA (Nov 2025), site asqa.gov.af",
      "verified", "asqa.gov.af; rename from ISO member page", date(2026, 7, 15)),
    F(9, "A", "which body leases state land for energy projects", "to-confirm",
      "ministry of urban development / land (sites partly down)", None,
      secondary=True, ask="land ministry / counsel"),
    # B - grid, export, water, land
    F(10, "B", "no unified national grid; regional systems fed by imports",
      "to-confirm", "OSCE 2024 report", date(2024, 1, 1), secondary=True, ask="DABS"),
    F(11, "B", "220 kV and 110 kV in use (tender W-3184; Maimana line)",
      "verified", "MEW tender page; DPMEA", date(2026, 11, 14)),
    F(12, "B", "no source names 132 kV", "to-confirm", "searches", None, ask="DABS"),
    F(13, "B", "2016 law: connection request answered in 40 business days",
      "to-confirm", f"{LAW16}, Arts 32-34", date(2016, 10, 18), ask="DABS"),
    F(14, "B", "no grid code, VRE connection, metering or telemetry rules found",
      "to-confirm", "searches of MEW, DABS, DPMEA", None, ask="DABS"),
    F(15, "B", "domestic generation ~250 MW, imports ~800 MW (Aug 2025)",
      "to-confirm", "news citing DABS", date(2025, 8, 13), secondary=True, ask="DABS"),
    F(16, "B", "wind resource mostly in Herat, Farah, Nimroz; Farah unconnected",
      "to-confirm", "World Bank 2018", date(2018, 6, 26), secondary=True, ask="DABS"),
    F(17, "B", "water-use permit: guideline of the ministry (posted Mar 2026)",
      "verified", "MEW guideline for water usage permit", date(2026, 3, 1)),
    F(18, "B", "permit category for a power plant or cleaning water",
      "project-dependent", "same guideline (no category)", date(2026, 3, 1),
      ask="water affairs directorate"),
    F(19, "B", "Water Affairs Management Law, OG 1367 (2020): text read",
      "to-confirm", "OG PDF on MEW page; application unknown", date(2020, 2, 4),
      ask="Ministry of Water and Energy"),
    F(20, "B", "2016 law: state land leased by ministry, private by agreement",
      "to-confirm", f"{LAW16}, Arts 19, 21 - application unknown", date(2016, 10, 18),
      ask="counsel"),
    # C - standards and evidence
    F(21, "C", "2017: ~200 IEC standards adopted, IEC 61215/61730 not listed",
      "to-confirm", "GIZ/AREU/BSW-Solar report 2017", date(2017, 8, 1), secondary=True,
      ask="ASQA"),
    F(22, "C", "ASQA inspects imports; returned solar panels after lab tests",
      "to-confirm", "Pajhwok 22 Jul 2026; ASQA battery item", date(2026, 7, 22),
      secondary=True, ask="ASQA"),
    F(23, "C", "mandatory certification for PV, inverters, turbines", "to-confirm",
      "not found", None, ask="ASQA"),
    # E - grid services
    F(24, "E", "no published grid-service product or requirement", "to-confirm",
      "searches", None, ask="DABS"),
    # F - finance
    F(25, "F", "US General License 20 allows energy deals; blocked persons out",
      "verified", "OFAC Afghanistan-related sanctions page", date(2022, 2, 25)),
    F(26, "F", "UN, EU and UK sanctions regimes", "to-confirm", "not read", None,
      ask="sanctions counsel"),
    F(27, "F", "no access to international banking; fragile banks", "to-confirm",
      "World Bank 2026", date(2026, 4, 26), secondary=True, ask="local bank / counsel"),
    F(28, "F", "contracts in afghani urged; foreign-currency use banned 2021",
      "to-confirm", "news", date(2026, 7, 31), secondary=True, ask="local bank / counsel"),
    F(29, "F", "purchase tariffs of 2022-2026 contracts not published",
      "to-confirm", "DPMEA pages give MW, not prices", None, ask="DABS"),
    F(30, "F", "renewable tax or customs incentive not found", "to-confirm", "-", None,
      ask="local tax advisor"),
    F(31, "F", "private investment law (OG 869, 2005): status", "to-confirm",
      "UNCTAD navigator", date(2005, 12, 21), secondary=True, ask="counsel"),
    F(32, "F", "contracts signed 27 Mar 2025: 228.45 MW incl. 43.2 MW wind",
      "verified", "DPMEA node/1852 (re-read by the author)", date(2025, 3, 27)),
    F(33, "F", "contracts signed 11 Feb 2026: 845 MW, solar and coal",
      "verified", "DPMEA node/2580", date(2026, 2, 11)),
    # G - social and land
    F(34, "G", "ESIA regulation listed as current; categories 1 and 2",
      "verified", "NEPA permit pages (showDariPage/25, /56)", date(2026, 11, 17)),
    F(35, "G", "ESIA fees and 3-year authorisation (NEPA page)", "verified",
      "same pages", date(2026, 11, 17)),
    F(36, "G", "public participation detail of the ESIA regulation",
      "to-confirm", "summary only", None, ask="NEPA"),
    F(37, "G", "2016 law: resettlement plan with affected people", "to-confirm",
      f"{LAW16}, Art 23", date(2016, 10, 18), ask="counsel"),
    F(38, "G", "land acquisition law (OG 1258, 2017): status", "to-confirm",
      "law-firm list", date(2017, 3, 4), secondary=True, ask="counsel"),
    F(39, "G", "state-land declarations in 2026: title risk high",
      "to-confirm", "news, Aug 2026", date(2026, 8, 1), secondary=True,
      ask="counsel / social specialist"),
    F(40, "G", "heritage law (2004) and clearance procedure", "to-confirm",
      "WIPO Lex", date(2004, 1, 1), secondary=True, ask="counsel"),
]

FACTS += [   # local capability, logistics, climate (all secondary)
    F(41, "B", "Pakistan crossings closed since Oct 2025; Iran, Uzbek routes used",
      "to-confirm", "RFE/RL 4 Oct 2026; Pajhwok 2026", date(2026, 10, 4), secondary=True,
      ask="logistics forwarder"),
    F(42, "B", "retail solar market, products mainly from China; no utility O&M",
      "to-confirm", "Xinhua via The Star, 2 Aug 2026", date(2026, 8, 2), secondary=True,
      ask="market survey"),
    F(43, "B", "Herat wind phase 1 described as the first wind turbines",
      "to-confirm", "Afghanistan International, Jun 2025", date(2025, 6, 8), secondary=True,
      ask="DABS / developer"),
    F(44, "B", "GHI about 6.5 kWh/m2/day, higher in the south and west",
      "to-confirm", "World Bank 2018", date(2018, 6, 26), secondary=True,
      ask="site measurement (ch 12)"),
]

APPROVALS = {   # teaching durations in months
    "S1": dict(what="proposal to the inter-ministerial investment committee",
               who="investment committee", months=2.0, after=[], status="verified"),
    "S2": dict(what="Economic Commission approval", who="Economic Commission",
               months=2.0, after=["S1"], status="verified"),
    "S3": dict(what="contract with DABS", who="DABS", months=3.0, after=["S2"],
               status="verified"),
    "S4": dict(what="licence and contract under the 2016 law", who="ministry",
               months=2.0, after=["S2"], status="to-confirm"),
    "S5": dict(what="ESIA screening and environmental permit", who="NEPA",
               months=4.0, after=["S1"], status="verified"),
    "S6": dict(what="state-land lease", who="land authority (which?)",
               months=4.0, after=["S2"], status="to-confirm"),
    "S7": dict(what="water-use permit", who="water affairs regulation",
               months=2.0, after=["S6"], status="verified"),
    "S8": dict(what="connection request and agreement", who="DABS",
               months=3.0, after=["S3"], status="to-confirm"),
    "S9": dict(what="import inspection of equipment", who="ASQA",
               months=2.0, after=["S3"], status="project-dependent"),
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
    "island or import system the POC belongs to": "value",
}
GRID_GIVEN = {"connection voltage and substation bay": "value"}
GRID_REQUEST_TO = "DABS (dispatch and transmission), in writing"

CERT = dict(what="maker's type certificate of the 5.5 MVA PV inverter (ch 44)",
            model="PCI-5500", standard="IEC 62109-1:2010",
            tests=["safety", "EMC", "unit fault ride-through"],
            ambient_max_c=45, altitude_m=1000, valid_to=date(2029, 6, 30),
            accreditation="test lab accredited (scope listed)")
CERT_NEED = dict(model="PCI-5500", standard="IEC 62109-1:2010",
                 tests=["safety", "EMC", "unit fault ride-through",
                        "import inspection (ASQA)"],
                 ambient_max_c=48, altitude_m=1800, delivery=date(2028, 1, 15),
                 plant_level=["reactive power at the POC", "plant ride-through"])
CERT_NATIONAL = ("ASQA inspects imports (AF-22); which standards it applies to"
                 " large inverters, modules and turbines is to-confirm (AF-23)")

TRACES = {
    "AF-17": ("water-use permit for construction and cleaning", {
        "source": "MEW guideline for water usage permit (posted Mar 2026)",
        "design": "monthly water balance and cleaning plan (appendix H)",
        "procurement": "well drilling and meter in the civil works scope",
        "construction": "meter installed on the well before use",
        "test": "not applicable: a permit (meter reading checked)",
        "approval": "committee survey, ministry agreement, permit issued",
        "retained": "permit, survey report, monthly meter records"}),
    "AF-14": ("connection technical requirements", {
        "source": "none published (AF-14) - a request to DABS",
        "design": None, "procurement": None, "construction": None, "test": None,
        "approval": None, "retained": None}),
}

SERVICES = [
    ("energy sale to DABS", "verified", "AF-02, AF-32: contracts with DABS"),
    ("reactive power / voltage control", "to-confirm", "AF-14: no rule found"),
    ("frequency response and reserve", "to-confirm", "AF-24: no product found"),
    ("ride-through", "to-confirm", "AF-14: no rule found"),
    ("operation within an island system", "to-confirm", "AF-10: grid structure"),
    ("curtailment compensation", "to-confirm", "AF-29: contract terms unpublished"),
]

FINANCE = [
    ("offtaker and contract form (DABS)", "official pages", "verified", "counsel"),
    ("tariff, term, indexation, security", "not published", "to-confirm", "counsel"),
    ("currency of payment and convertibility", "news", "to-confirm", "bank, counsel"),
    ("banking channel for payments", "World Bank (secondary)", "to-confirm", "bank"),
    ("US General License 20", "OFAC page", "verified", "sanctions counsel"),
    ("UN, EU, UK regimes", "not read", "to-confirm", "sanctions counsel"),
    ("tax and customs incentives", "not found", "to-confirm", "tax advisor"),
    ("investment law and protections", "secondary", "to-confirm", "counsel"),
    ("land lease cost and security", "2016 law text", "to-confirm", "counsel"),
]

# equipment against local service capability (teaching constraints; None = unknown)
OPTIONS = {
    "central inverters 5.5 MVA": {"service techs in country": None,
                                  "spare lead time weeks": 16,
                                  "ambient rating C": 50, "max part mass t": 12},
    "string inverters 0.3 MVA": {"service techs in country": 1,
                                 "spare lead time weeks": 2,
                                 "ambient rating C": 50, "max part mass t": 0.1},
    "wind 5 MW, 150 m rotor": {"service techs in country": None,
                               "spare lead time weeks": 26,
                               "ambient rating C": 45, "max part mass t": 90},
    "wind 3 MW, 120 m rotor": {"service techs in country": None,
                               "spare lead time weeks": 20,
                               "ambient rating C": 45, "max part mass t": 60},
}
CONSTRAINTS = {"service techs in country": ("min", 1),
               "spare lead time weeks": ("max", 8),
               "ambient rating C": ("min", 48),
               "max part mass t": ("max", 70)}
