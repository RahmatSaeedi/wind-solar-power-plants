"""Chapter 39 lesson J: environmental data on one boundary, by hand."""
import math

import pytest

from companion.ch39 import examples_j as ej


def test_materials_and_transport_by_hand():
    # U-B: 7.4 x 2.2 + 2.9 x 3.4 + 3.8 x 0.9 + 3.5 x 1.8 + 0.8 x 2.5
    assert ej.materials("U-B") == pytest.approx(37.86)
    # U-A: 17.5 t over 5,000 km by sea and 600 km by road
    assert ej.transport("U-A") == pytest.approx(17.5 * (60 + 54) / 1000)
    assert ej.transport("U-B") == pytest.approx(18.4 * 900 * 0.09 / 1000)


def test_one_boundary_and_uncertainty():
    total, unc, parts = ej.to_site("U-A")
    assert total == pytest.approx(41.0 + ej.transport("U-A"))
    assert unc == pytest.approx(math.hypot(4.1, 0.3 * ej.transport("U-A")))
    assert [p[2] for p in parts] == ["declared", "estimate"]
    t_c, _, parts_c = ej.to_site("U-C")
    assert all(p[2] == "estimate" for p in parts_c)
    assert t_c == pytest.approx(ej.materials("U-C") + 1.6 * 5.6
                                + ej.transport("U-C"))


def test_no_pair_differs_beyond_uncertainty():
    vals = {o: ej.to_site(o)[:2] for o in ej.DECLARED}
    assert ej.decide(vals) == []
    assert ej.decide({"a": (10.0, 1.0), "b": (14.0, 1.0)}) == ["a-b"]


def test_quality_counts():
    q = ej.quality()
    assert q == {"U-A": 8, "U-B": 3, "U-C": 1}
