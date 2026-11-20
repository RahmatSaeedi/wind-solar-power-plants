"""Chapter 58: standards-register helpers on small hand-made cases."""
from datetime import date

from plantp import stdreg

CAT = {"IEC 62548-1": [(2023, "IEC 62548-1:2023", "edition"),
                       (2025, "Amd 1:2025", "amendment")],
       "IEC 60076-2": [(1993, "IEC 60076-2:1993", "edition"),
                       (2011, "IEC 60076-2:2011", "edition")]}


def test_resolve_dated_and_undated():
    assert stdreg.resolve("IEC 62548-1:2023", CAT) == ["IEC 62548-1:2023"]
    assert stdreg.resolve("IEC 62548-1", CAT) == ["IEC 62548-1:2023", "Amd 1:2025"]
    assert stdreg.resolve("IEC 60076-2", CAT) == ["IEC 60076-2:2011"]
    assert stdreg.resolve("IEC 60076-2:1993", CAT) == ["IEC 60076-2:1993"]


def test_verbal_forms():
    assert stdreg.verbal_form("The meter shall be class 0.5S.")[0] == "requirement"
    assert stdreg.verbal_form("Cables shall not be buried.")[0] == "prohibition"
    assert stdreg.verbal_form("The tester may use a clamp.")[0] == "permission"
    k, vague = stdreg.verbal_form("Earthing shall be adequate.")
    assert k == "requirement" and vague == ["adequate"]
    assert stdreg.verbal_form("The plant exports power.")[0] == "statement"


def test_completeness_and_open():
    rows = [dict(id="S1", designation="X", title="t", issuing_body="IEC", edition="2020",
                 adoption_or_legal_status="s", official_source="u", discipline="PV",
                 applicability_in_book="ch10", date_verified="2026-11-01", note=""),
            dict(id="S2", designation="Y", title="", issuing_body="IEC",
                 edition="2019; confirm", adoption_or_legal_status="s", official_source="",
                 discipline="wind", applicability_in_book="ch11", date_verified="", note="")]
    c = stdreg.completeness(rows)
    assert c["incomplete"] == ["S2"] and c["missing"]["title"] == 1
    assert stdreg.open_items(rows) == ["S2"]


def test_replaced_series_clause():
    assert stdreg.replaced_year(dict(edition="Edition 2.0 2021; replaces the 2016 edition")) == 2016
    assert stdreg.replaced_year(dict(edition="Replaces ISO 9060:1990")) == 1990
    assert stdreg.replaced_year(dict(edition="2016; replaces 485-2010")) == 2010
    assert stdreg.replaced_year(dict(edition="Replaces ISO 1940 parts")) is None
    assert stdreg.replaced_year(dict(edition="2024; replaces EN 1997-2")) is None
    assert stdreg.series("IEC 61400-24:2019") == "IEC 61400"
    assert stdreg.series("IEC TS 62804-1:2025") == "IEC 62804"
    assert stdreg.series("IEEE Std 80-2013") is None
    c = stdreg.clause("PV modules", "IEC 61215-2:2021")
    kind, vague = stdreg.verbal_form(c)
    assert kind == "requirement" and vague == [] and "IEC 61215-2:2021" in c


def test_topic_year_chapters():
    r = dict(designation="IEC 60076-2:2011", title="Power transformers", discipline="Power transformers",
             edition="Edition 3.0", applicability_in_book="ch43 ch25")
    assert stdreg.topic(r) == "transformers"
    assert stdreg.edition_year(r) == 2011
    assert stdreg.chapters(r) == {25, 43}
    assert stdreg.age_years(r, date(2026, 11, 18)) == 15
    assert stdreg.in_scope(["IEC 62109-1:2010"], "IEC 62109-1:2010")
    assert not stdreg.in_scope(["IEC 62109-1:2010"], "IEC 62109-1:2025")
