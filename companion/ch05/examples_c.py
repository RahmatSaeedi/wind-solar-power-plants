"""Chapter 5, section C - the engineering-software workflow: requirements and
traceability, logging, choosing an architecture, a database, edge cases,
mutation testing, versions, reviewing generated code, and a CAE convergence study.

Run from the project root:   python -m companion.ch05.examples_c
"""
from __future__ import annotations

import ast
import io
import logging
import math
import sqlite3
from pathlib import Path

import numpy as np

from companion.ch05.common import HERE, csv, emit
from plantp import datapack, dataio, materials as mt

TESTS = HERE.parents[0] / "tests" / "test_ch05_tool.py"

# ---- requirements and traceability -------------------------------------------------------
REQUIREMENTS = {
    "R-01": ("convert between units and refuse mixed dimensions",
             ["test_convert_known_values", "test_convert_refuses"]),
    "R-02": ("read the SCADA export and report every malformed line",
             ["test_reader_on_the_data_pack_sample", "test_reader_reports_malformed_lines"]),
    "R-03": ("find every defect of the raw logger file", ["test_raw_validation_finds_every_planted_defect"]),
    "R-04": ("never export more than the connection limit",
             ["test_export_never_exceeds_the_limit_and_balances"]),
    "R-05": ("results repeat exactly and name their inputs", ["test_configured_run_is_reproducible"]),
    "R-06": ("aggregate correctly across a clock change",
             ["test_hourly_aggregation_across_a_clock_change"]),
    "R-07": ("battery never charges from the grid", ["test_rule_based_dispatch_invariants"]),
    "R-08": ("report states its limitations", ["test_report_names_its_evidence"]),
    "R-09": ("warn when a run uses an outdated data pack", []),
}


def traceability() -> None:
    tree = ast.parse(TESTS.read_text(encoding="utf-8"))
    tests = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)
             and n.name.startswith("test_")}
    lines = ["requirement -> tests (found in test_ch05_tool.py):"]
    missing = []
    for rid, (text, names) in REQUIREMENTS.items():
        ok = [n for n in names if n in tests]
        status = "covered" if names and len(ok) == len(names) else "NOT COVERED"
        if status != "covered":
            missing.append(rid)
        lines.append(f"  {rid} {status:11s} {text}")
    used = {n for _, ns in REQUIREMENTS.values() for n in ns}
    lines.append(f"{len(tests)} tests in the file; {len(tests - used)} not linked to a "
                 "requirement (helpers or extra checks)")
    lines.append(f"requirements without a test: {', '.join(missing) or 'none'}")
    emit("c_trace", lines)


# ---- logging --------------------------------------------------------------------------
def logging_demo() -> None:
    stream = io.StringIO()
    log = logging.getLogger("resource_tool.demo")
    log.setLevel(logging.INFO)
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(levelname)-8s %(name)s: %(message)s"))
    log.addHandler(handler)
    log.debug("not shown: below the chosen level")
    log.info("data pack 1.1.0 verified (22 files)")
    log.warning("hour 2023-04-03 14:00 has 1 of 6 values; excluded")
    log.error("configuration rejected: export_limit_mw missing")
    log.removeHandler(handler)
    emit("c_logging", stream.getvalue().rstrip("\n").splitlines())


# ---- choosing an application structure ---------------------------------------------------
def architecture() -> None:
    cases = {   # consequence, users, data volume, audit need, years to maintain (1..5)
        "first-pass yield estimate": (2, 1, 2, 3, 1),
        "monthly performance report": (3, 3, 4, 4, 4),
        "asset register and maintenance": (4, 4, 3, 5, 5),
        "plant power controller": (5, 2, 4, 5, 5),
    }
    lines = ["case                              C U D A M  -> structure"]
    for name, (c, u, d, a, m) in cases.items():
        if c == 5 and name.endswith("controller"):
            choice = "control-system software (certified platform, ch. 34-36)"
        elif u >= 4 and a >= 5:
            choice = "database-backed system of record"
        elif d >= 4 and m >= 4:
            choice = "command-line batch tool + database + report"
        elif c <= 2 and u == 1:
            choice = "calculator, notebook or spreadsheet with checks"
        else:
            choice = "command-line batch tool"
        lines.append(f"{name:33s} {c} {u} {d} {a} {m}  -> {choice}")
    lines.append("C consequence of an error, U users, D data volume, A auditability, "
                 "M years of maintenance (1 low .. 5 high)")
    emit("c_architecture", lines)


# ---- a small relational database -------------------------------------------------------
def database() -> None:
    reg = datapack.load_register("A")
    db = sqlite3.connect(":memory:")
    db.executescript("""
        CREATE TABLE asset (tag TEXT PRIMARY KEY, parent TEXT REFERENCES asset(tag),
                            description TEXT NOT NULL, serial TEXT,
                            commissioned TEXT, criticality TEXT CHECK (criticality IN ('A','B','C')));
        CREATE TABLE test_record (id INTEGER PRIMARY KEY, tag TEXT NOT NULL REFERENCES asset(tag),
                                  test TEXT NOT NULL, result TEXT CHECK (result IN ('pass','fail')),
                                  done TEXT NOT NULL);
    """)
    db.executemany("INSERT INTO asset VALUES (?,?,?,?,?,?)",
                   [(r["tag"], r["parent"] or None, r["description"], r["serial"] or None,
                     r["commissioned"] or None, r["criticality"]) for r in reg])
    tests = [(f"PLP-INV-{k:02d}", "insulation resistance", "pass", "2025-07-20")
             for k in range(1, 11) if k != 4]
    tests += [("PLP-TRF-01", "ratio and vector group", "pass", "2025-06-01"),
              ("PLP-WTG-03", "functional", "fail", "2025-06-25")]
    db.executemany("INSERT INTO test_record (tag, test, result, done) VALUES (?,?,?,?)", tests)
    db.commit()
    q1 = db.execute("SELECT substr(tag, 5, 3) AS sys, count(*) FROM asset "
                    "GROUP BY sys ORDER BY count(*) DESC").fetchall()
    q2 = db.execute("SELECT a.tag FROM asset a LEFT JOIN test_record t ON a.tag = t.tag "
                    "WHERE a.tag LIKE 'PLP-INV-%' AND t.id IS NULL").fetchall()
    q3 = db.execute("SELECT tag, test, done FROM test_record WHERE result = 'fail'").fetchall()
    lines = ["assets per system: " + ", ".join(f"{s} {n}" for s, n in q1),
             f"inverters without any test record: {[t for (t,) in q2]}",
             f"failed tests: {q3}"]
    try:
        with db:                                             # one transaction
            db.execute("INSERT INTO test_record (tag, test, result, done) VALUES "
                       "('PLP-INV-04', 'insulation resistance', 'pass', '2025-07-21')")
            db.execute("INSERT INTO asset (tag, description, criticality) VALUES "
                       "('PLP-INV-11', 'spare', 'D')")       # violates the CHECK
    except sqlite3.IntegrityError as e:
        lines.append(f"transaction rolled back: {e}")
    n = db.execute("SELECT count(*) FROM test_record WHERE tag = 'PLP-INV-04'").fetchone()[0]
    lines.append(f"  test records for PLP-INV-04 after the rollback: {n}")
    backup = sqlite3.connect(":memory:")
    db.backup(backup)
    lines.append(f"backup copy holds {backup.execute('SELECT count(*) FROM asset').fetchone()[0]}"
                 " assets (sqlite3 backup API)")
    emit("c_database", lines)


# ---- edge cases -------------------------------------------------------------------------
def edge_cases() -> None:
    from companion.ch05 import step3_model as m
    from companion.ch05.basics import capacity_factor
    cases = [
        ("capacity_factor(100, 0)", lambda: capacity_factor(100, 0)),
        ("capacity_factor(-5, 60)", lambda: capacity_factor(-5, 60)),
        ("pv_ac_mw([], [])", lambda: m.pv_ac_mw([], [])),
        ("np.sum([1.0, nan])", lambda: np.sum([1.0, math.nan])),
        ("np.nansum([1.0, nan])", lambda: np.nansum([1.0, math.nan])),
        ("np.mean([])", lambda: np.mean(np.array([]))),
        ("check_timestamps(['2023-01-01T00:00'])",
         lambda: dataio.check_timestamps(["2023-01-01T00:00"])[1]),
        ("1e308 * 10", lambda: 1e308 * 10),
        ("float('nan') == float('nan')", lambda: math.nan == math.nan),
    ]
    import warnings
    lines = []
    for text, func in cases:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                res = func()
                lines.append(f"  {text:38s} -> {res!r}")
            except Exception as e:                     # noqa: BLE001 (we show it)
                lines.append(f"  {text:38s} -> {type(e).__name__}: {e}")
    emit("c_edges", ["inputs at the edges, and what the code does:"] + lines)


# ---- mutation testing ---------------------------------------------------------------------
SOURCE = '''
def capacity_factor(energy_mwh, rated_mw, hours=8760):
    if rated_mw <= 0 or hours <= 0:
        raise ValueError("bad input")
    return energy_mwh / (rated_mw * hours)
'''
MUTATIONS = [("<= 0 or", "< 0 or"), ("hours=8760", "hours=8784"), ("/ (rated_mw", "* (rated_mw"),
             ("or hours <= 0", "and hours <= 0"), ("raise ValueError", "return 0.0  #")]


def weak_tests(f):
    assert abs(f(192_500, 60) - 0.366) < 0.01


def strong_tests(f):
    assert abs(f(192_500, 60) - 0.36625) < 1e-4
    assert abs(f(3_100, 60, hours=168) - 0.30754) < 1e-4
    for bad in ((100, 0), (100, 60, 0), (100, -1)):
        try:
            f(*bad)
        except ValueError:
            continue
        raise AssertionError("no error for " + repr(bad))


def mutation() -> None:
    lines = ["mutant                               weak tests   strong tests"]
    for old, new in MUTATIONS:
        src = SOURCE.replace(old, new, 1)
        env: dict = {}
        exec(src, env)                                   # our own source text only
        res = []
        for suite in (weak_tests, strong_tests):
            try:
                suite(env["capacity_factor"])
                res.append("survived")
            except (AssertionError, ZeroDivisionError):
                res.append("killed")
        lines.append(f"  {old!r:16s} -> {new!r:18s} {res[0]:12s} {res[1]}")
    emit("c_mutation", lines)


# ---- versions --------------------------------------------------------------------------
def versions() -> None:
    tags = ["1.10.0", "1.9.0", "1.1.0", "2.0.0", "1.0.0"]
    as_text = sorted(tags)
    as_numbers = sorted(tags, key=lambda v: tuple(int(x) for x in v.split(".")))

    def bump(v, part):
        a, b, c = (int(x) for x in v.split("."))
        return {"major": f"{a + 1}.0.0", "minor": f"{a}.{b + 1}.0", "patch": f"{a}.{b}.{c + 1}"}[part]
    emit("c_versions", [
        f"sorted as text:    {as_text}",
        f"sorted as numbers: {as_numbers}",
        f"from 1.0.0: bug fix -> {bump('1.0.0', 'patch')}; new files only -> "
        f"{bump('1.0.0', 'minor')}; changed series -> {bump('1.0.0', 'major')}",
        "data pack 1.0.0 -> 1.1.0: files added, none changed in meaning -> minor",
    ])


# ---- reviewing generated or copied code ------------------------------------------------------
SUGGESTED = '''
def annual_capacity_factor(df, rated_mw):
    """Capacity factor of a plant from hourly power in MW."""
    hours = 8784
    df["hour"] = df.index.hour
    return df["p_mw"].mean() * hours / (rated_mw * hours)
'''


def review_generated() -> None:
    import pandas as pd
    env: dict = {}
    exec(SUGGESTED, env)
    f = env["annual_capacity_factor"]
    idx = pd.date_range("2023-01-01", periods=8760, freq="h", tz="+04:00")
    df = pd.DataFrame({"p_mw": np.full(8760, 30.0)}, index=idx)
    cf = f(df, 60)
    gaps = df.drop(df.index[4000:4500])
    cf_gaps = f(gaps.copy(), 60)
    true_low = 30.0 * (8760 - 500) / (60 * 8760)
    lines = [f"constant 30 MW all year on 60 MW: expected 0.500, function gives {cf:.3f}",
             f"same data with 500 missing hours: {cf_gaps:.3f} (mean hides the gap);",
             f"  if the plant really produced nothing then: {true_low:.3f} - only the",
             "  data owner can say, so the gap must be reported, not averaged away",
             f"side effect: caller's table gained columns {sorted(set(df.columns) - {'p_mw'})}",
             "findings: 8784 is a leap year but cancels; missing hours not reported;",
             "  input table modified; no units, no checks -> rewrite with tests"]
    emit("c_review", lines)


# ---- CAE: mesh convergence and validation ---------------------------------------------------
def beam_frequency(n_el: int, length: float, ei: float, m_per_l: float, tip_mass: float) -> float:
    """First natural frequency (Hz) of a clamped-free beam with Hermite elements."""
    le = length / n_el
    k_e = ei / le ** 3 * np.array([[12, 6 * le, -12, 6 * le], [6 * le, 4 * le ** 2, -6 * le, 2 * le ** 2],
                                   [-12, -6 * le, 12, -6 * le], [6 * le, 2 * le ** 2, -6 * le, 4 * le ** 2]])
    m_e = m_per_l * le / 420 * np.array([[156, 22 * le, 54, -13 * le], [22 * le, 4 * le ** 2, 13 * le, -3 * le ** 2],
                                         [54, 13 * le, 156, -22 * le], [-13 * le, -3 * le ** 2, -22 * le, 4 * le ** 2]])
    dof = 2 * (n_el + 1)
    k, m = np.zeros((dof, dof)), np.zeros((dof, dof))
    for e in range(n_el):
        s = slice(2 * e, 2 * e + 4)
        k[s, s] += k_e
        m[s, s] += m_e
    m[-2, -2] += tip_mass
    k, m = k[2:, 2:], m[2:, 2:]                         # clamp the base
    lam = np.linalg.eigvals(np.linalg.solve(m, k)).real
    return float(math.sqrt(min(lam[lam > 0])) / (2 * math.pi))


def cae() -> None:
    sec = mt.tube_section(4.50, 0.045)                   # chapter 4 second try (A-050)
    ei, mpl, length = 210e9 * sec.second_moment, 7850 * sec.area, 100.0
    from scipy.optimize import brentq as root
    beta = root(lambda b: math.cos(b) * math.cosh(b) + 1, 1.5, 2.5, xtol=1e-14)
    exact = beta ** 2 / (2 * math.pi) * math.sqrt(ei / (mpl * length ** 4))
    lines = [f"tower without top mass; exact f1 = beta^2/(2 pi) sqrt(EI/(m L^4)), beta = {beta:.6f}"
             f" (root of cos b cosh b = -1): {exact:.6f} Hz",
             "  elements  frequency (Hz)  error"]
    rows = []
    for n in (1, 2, 4, 8, 16):
        f = beam_frequency(n, length, ei, mpl, 0.0)
        lines.append(f"  {n:8d}  {f:.6f}        {100 * (f - exact) / exact:+.2e} %")
        rows.append((n, f"{abs(100 * (f - exact) / exact):.3e}"))
    csv("ch05-convergence.csv", "n,err", rows)
    f_top = [beam_frequency(n, length, ei, mpl, 350e3) for n in (4, 8, 16)]
    measured = 0.221                                     # synthetic commissioning test
    lines += [f"with the 350 t top mass: {f_top[0]:.4f}, {f_top[1]:.4f}, {f_top[2]:.4f} Hz "
              "(4, 8, 16 elements)",
              f"synthetic 'measured' frequency {measured} Hz: model is "
              f"{100 * (f_top[2] - measured) / measured:+.1f} % high",
              "  a converged mesh does not make a model right: the clamped base ignores",
              "  foundation and soil flexibility (chapter 30) - calibrate, then re-check"]
    from scipy.optimize import brentq
    log_k = brentq(lambda x: beam_frequency_spring(16, length, ei, mpl, 350e3, 10 ** x)
                   - measured, 10.0, 14.0, xtol=1e-6)
    lines.append(f"  a rotational base spring of {10 ** log_k / 1e9:.0f} GN m/rad reproduces "
                 "the measurement (one fitted parameter)")
    lines.append("  check the calibrated model against a SECOND measurement before trusting it")
    emit("c_cae", lines)


def beam_frequency_spring(n_el, length, ei, m_per_l, tip_mass, k_rot) -> float:
    """As beam_frequency, but the base can rotate against a spring k_rot (N m/rad)."""
    le = length / n_el
    k_e = ei / le ** 3 * np.array([[12, 6 * le, -12, 6 * le], [6 * le, 4 * le ** 2, -6 * le, 2 * le ** 2],
                                   [-12, -6 * le, 12, -6 * le], [6 * le, 2 * le ** 2, -6 * le, 4 * le ** 2]])
    m_e = m_per_l * le / 420 * np.array([[156, 22 * le, 54, -13 * le], [22 * le, 4 * le ** 2, 13 * le, -3 * le ** 2],
                                         [54, 13 * le, 156, -22 * le], [-13 * le, -3 * le ** 2, -22 * le, 4 * le ** 2]])
    dof = 2 * (n_el + 1)
    k, m = np.zeros((dof, dof)), np.zeros((dof, dof))
    for e in range(n_el):
        s = slice(2 * e, 2 * e + 4)
        k[s, s] += k_e
        m[s, s] += m_e
    m[-2, -2] += tip_mass
    k[1, 1] += k_rot
    k, m = k[1:, 1:], m[1:, 1:]                         # base displacement fixed only
    lam = np.linalg.eigvals(np.linalg.solve(m, k)).real
    return float(math.sqrt(min(lam[lam > 0])) / (2 * math.pi))


if __name__ == "__main__":
    traceability()
    logging_demo()
    architecture()
    database()
    edge_cases()
    mutation()
    versions()
    review_generated()
    cae()
