"""Chapter 54 compliance helpers against hand-made cases."""
from datetime import date

from plantp import compliance as cp


def test_rank_order():
    assert cp.rank("law") < cp.rank("grid code") < cp.rank("contract")
    assert cp.rank("owner specification") < cp.rank("project procedure")


def test_conflicts():
    reqs = [dict(id="a", source_type="grid code", parameter="pf", kind="min", value=0.95),
            dict(id="b", source_type="contract", parameter="pf", kind="min", value=0.93),
            dict(id="c", source_type="utility rule", parameter="pf", kind="max", value=1.0)]
    r = cp.conflicts(reqs, "pf")
    assert r["lo"] == 0.95 and r["hi"] == 1.0 and r["feasible"]
    reqs.append(dict(id="d", source_type="owner specification", parameter="pf", kind="max",
                     value=0.94))
    assert not cp.conflicts(reqs, "pf")["feasible"]


def test_applies():
    req = dict(scope=dict(v_min=66, v_max=230, ownership=["private"]))
    assert cp.applies(req, dict(voltage_kv=132, ownership="private", location="x",
                                technology="pv"))
    assert not cp.applies(req, dict(voltage_kv=33, ownership="private", location="x",
                                    technology="pv"))
    assert not cp.applies(req, dict(voltage_kv=132, ownership="public", location="x",
                                    technology="pv"))


def test_freshness_and_trace():
    req = dict(document="GC", edition="2019", verified=date(2028, 1, 1), official_source="")
    p = cp.freshness(req, date(2029, 6, 1), 365, {"GC": "2024"})
    assert "verification stale" in p and "no official source" in p
    assert any("superseded" in x for x in p)
    assert cp.trace_gaps({"source": "x", "design": "y"}) == list(cp.STAGES[2:])
    assert cp.trace_gaps({s: "ok" for s in cp.STAGES}) == []


def test_consolidated_and_diff():
    cl = {"6.2": [(date(2024, 1, 1), "base", "a"), (date(2025, 7, 1), "A1", "b")],
          "9.9": [(date(2030, 1, 1), "A5", "later")]}
    assert cp.consolidated(cl, date(2025, 1, 1)) == {"6.2": ("base", "a")}
    assert cp.consolidated(cl, date(2026, 1, 1)) == {"6.2": ("A1", "b")}
    d = cp.register_diff({"R1": {"v": 1}, "R2": {"v": 2}},
                         {"R2": {"v": 3}, "R3": {"v": 4}})
    assert d["added"] == ["R3"] and d["removed"] == ["R1"]
    assert d["changed"] == [("R2", "v", 2, 3)]


def test_ageing_and_impact():
    req = [("Q1", date(2029, 1, 1), None), ("Q2", date(2029, 5, 20), None),
           ("Q3", date(2029, 1, 1), date(2029, 2, 1))]
    assert cp.clarification_ageing(req, date(2029, 6, 1), 30) == [("Q1", 151)]
    links = {"R1": ("GC", ["calc", "test"]), "R2": ("PERMIT", ["plan"])}
    assert cp.edition_impact(links, "GC") == [("R1", "calc"), ("R1", "test")]
