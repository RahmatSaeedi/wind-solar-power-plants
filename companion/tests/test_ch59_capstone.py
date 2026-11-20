"""Chapter 59 (capstone): pure helpers and data only - no function here writes
an `expected/` file."""
from __future__ import annotations

import pytest

from companion.ch59 import common  # noqa: F401  (path)
from companion.ch59 import sources as src
from companion.ch59 import dossier
from companion.ch59.cases import gamma_update
from plantp import appraisal


def test_every_decision_has_a_chapter():
    assert sorted(src.DECISION_CH) == list(range(1, 63))
    assert all(1 <= ch <= 58 for ch in src.DECISION_CH.values())
    assert len(src.decisions_of(list(range(1, 60)))) == 62


def test_decisions_of_a_part():
    # Part I (ch 1-5): D-001, D-004..D-009
    assert src.decisions_of([1, 2, 3, 4, 5]) == ["D-001", "D-004", "D-005", "D-006",
                                                 "D-007", "D-008", "D-009"]


def test_deliverable_sections_are_found():
    missing = [n for n in range(1, 60) if not src.records(n)["found"]]
    assert missing == []


def test_document_ids_follow_the_pattern():
    import re
    for n in (1, 21, 59):
        for d in src.records(n)["docs"]:
            assert re.fullmatch(r"PLP-[A-Z]{3}-[A-Z]{3}-\d{4}", d)


def test_gamma_update_by_hand():
    # prior worth 4 unit-years at 0.5 a year; 3 failures in 20 unit-years
    a, b = gamma_update(2.0, 4.0, 3, 20.0)
    assert (a, b) == (5.0, 24.0)
    assert a / b == pytest.approx(0.2083, abs=1e-4)


def test_schedule_critical_path():
    tasks = {k: (float(d), pre) for k, (d, pre) in dossier.TASKS.items()}
    total, crit, slack = appraisal.critical_path(tasks)
    assert total == pytest.approx(63.0)
    assert all(slack[k] == pytest.approx(0.0) for k in crit)


def test_longer_task_cannot_shorten_the_plan():
    tasks = {k: (float(d), pre) for k, (d, pre) in dossier.TASKS.items()}
    base = appraisal.critical_path(tasks)[0]
    for k in tasks:
        d, pre = tasks[k]
        longer = dict(tasks, **{k: (d + 1.0, pre)})
        assert appraisal.critical_path(longer)[0] >= base
