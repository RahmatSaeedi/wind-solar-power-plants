"""Chapter 38 lab: the checks find exactly the planted defects."""
from companion.ch38 import lab_d, sources as src
from plantp import docctl as dc


def test_register_defects():
    bad_id = [d["id"] for d in src.DOCS if not dc.id_ok(d["id"])]
    bad_rev = [d["id"] for d in src.DOCS if not dc.rev_ok(d["rev"], d["status"])]
    assert len(bad_id) == 2 and len(bad_rev) == 3
    illegal = [k for k, h in src.HISTORY.items()
               if any(not dc.transition_ok(a, b) for a, b in zip(h, h[1:]))]
    assert sorted(illegal) == ["PLP-CTL-DWG-0103", "PLP-ELE-CAL-0101"]


def test_crosscheck_and_references():
    found = lab_d.crosscheck()
    assert len(found) == 5
    assert {f[1] for f in found} == {"=T1-Q2", "=PVF2-3-T1", "=WS1-2-T1", "=PVF2-W1",
                                      "=PVF2-Q1"}
    assert len(dc.stale_references(src.CURRENT, src.REFS)) == 3


def test_change_reaches_fat():
    hit = dc.impacted(src.DEPENDS, "unit transformer rating")
    assert "FAT procedure" in hit and len(hit) == 13
    assert sum(src.REWORK_H[h] for h in hit) == 102
