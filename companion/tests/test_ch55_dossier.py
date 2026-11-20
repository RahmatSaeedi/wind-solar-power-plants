"""Country-dossier helpers (chapters 55-57) against hand-made cases."""
from datetime import date

from plantp import dossier as ds


def test_status_and_stale():
    facts = [dict(id="F1", topic="grid", status="verified", doc_date=date(2025, 1, 1)),
             dict(id="F2", topic="grid", status="to-confirm", doc_date=None),
             dict(id="F3", topic="land", status="verified", doc_date=date(2015, 6, 1))]
    s = ds.status_by(facts)
    assert s["grid"]["verified"] == 1 and s["grid"]["to-confirm"] == 1
    st = ds.stale(facts, date(2026, 11, 17), 3)
    assert ("F2", None) in st and st[1][0] == "F3" and st[1][1] > 11


def test_cert_review():
    cert = dict(model="INV-5500", standard="IEC 62109-1:2010", tests=["safety"],
                ambient_max_c=45, altitude_m=1000, valid_to=date(2028, 1, 1),
                accreditation="")
    need = dict(model="INV-5500", standard="IEC 62109-1:2010", tests=["safety", "EMC"],
                ambient_max_c=50, altitude_m=1200, delivery=date(2027, 6, 1),
                plant_level=["reactive power at the POC"])
    rows = {r[0]: r[1] for r in ds.cert_review(cert, need)}
    assert rows["model"] == "shown" and rows["test: EMC"] == "NOT SHOWN"
    assert rows["site ambient"] == "NOT SHOWN" and rows["valid on delivery"] == "shown"
    assert rows["reactive power at the POC"] == "NOT SHOWN"


def test_gaps_and_compare():
    g = ds.data_gaps({"a": "value", "b": "measured"},
                     {"a": "measured", "b": "model", "c": "value"})
    assert g["missing"] == ["c"] and g["weak"] == [("a", "value", "measured")]
    assert abs(g["complete"] - 1 / 3) < 1e-9
    r = ds.compare({"X": {"t": 50, "s": None}, "Y": {"t": 40, "s": 3}},
                   {"t": ("min", 45), "s": ("max", 5)})
    assert r["X"]["verdicts"]["s"] == "unknown" and r["X"]["ok"] == 1
    assert r["Y"]["fails"] == 1 and r["Y"]["ok"] == 1
