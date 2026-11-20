"""Chapter 35 lab D: the validating consumer refuses what it must and
accepts what it should (synthetic records only)."""
from companion.ch35 import lab_d


def good(t=1.0):
    return {"tag": "PLP-E1-VT.Voltage", "value": 132.0, "unit": "kV",
            "quality": "good", "t": t}


def test_accepts_a_good_record():
    assert lab_d.validate(good(), {}) == []


def test_refusals():
    assert "missing quality" in lab_d.validate({k: v for k, v in good().items()
                                                if k != "quality"}, {})
    bad_tag = dict(good(), tag="plp-e1-vt.voltage")
    assert "unknown or malformed tag" in lab_d.validate(bad_tag, {})
    assert "wrong unit" in lab_d.validate(dict(good(), unit="V"), {})
    assert "value not a number" in lab_d.validate(dict(good(), value="hot"), {})
    assert "unknown quality" in lab_d.validate(dict(good(), quality="fine"), {})
    last = {"PLP-E1-VT.Voltage": 5.0}
    assert "time not increasing" in lab_d.validate(good(t=5.0), last)


def test_planted_faults_found():
    log, refused = lab_d.consume(lab_d.produce())
    assert sum(refused.values()) == 3
    assert any(r["quality"] == "bad" for r in log)
