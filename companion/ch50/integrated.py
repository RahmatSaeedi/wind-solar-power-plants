"""Chapter 50, integrated Plant P examples: three numbers by hand, the
operational-acceptance verdict of block =PVF1-3 and the basis D-054.

Run from the project root:   python -m companion.ch50.integrated
Writes companion/ch50/expected/int_*.txt.
"""
from __future__ import annotations

from companion.ch50 import sources as src
from companion.ch50.common import emit
from plantp import commissioning as cm
from plantp import performance, protection


def by_hand() -> dict:
    c = src.STRING_COND
    voc, isc = cm.string_expected(c["n"], c["g"], c["t_cell"])
    t = protection.trip_time(5.0, 1.0, 0.25)
    used = [(h, e) for _, h, e, a in src.PR_DAYS if a >= 0.95]
    pr = performance.performance_ratio(sum(e for _, e in used) * 1000, src.PR_DC_KWP,
                                       sum(h for h, _ in used))
    lines = ["three numbers by hand, checked by the scripts",
             f"  one module short of 26 at {voc:,.0f} V: {voc / 26:.1f} V less, "
             f"{voc * 25 / 26:,.0f} V",
             f"  WS3 relay at 5 x pickup, TMS 0.25: 0.25 x 0.14 / (5^0.02 - 1) = {t:.2f} s",
             f"  PR of 9 days: {sum(e for _, e in used):,.0f} / (60 x "
             f"{sum(h for h, _ in used):.1f}) = {pr:.3f}"]
    emit("int_hand", lines)
    return dict(voc=voc, t=t, pr=pr)


def acceptance() -> dict:
    criteria = {
        "all A punch items closed": False,
        "B punch items with owner and date": True,
        "every requirement traced to a passed test or an accepted deviation": False,
        "PR test met (measured value, contract rule)": True,
        "auxiliary chains passed (transfer, autonomy, shedding, interlocks)": False,
        "fire cause-and-effect fully proven": False,
        "handover data imported without defects": False,
        "operators and authorised persons assessed": False,
        "emergency roles, contacts and drills complete": False,
        "spares received": False,
    }
    met = sum(criteria.values())
    lines = ["operational acceptance of Plant P (criteria of the contract, teaching)"]
    lines += [f"  [{'x' if v else ' '}] {k}" for k, v in criteria.items()]
    lines += [f"  {met} of {len(criteria)} met: the plant runs and exports in its",
              "  tests, but it is not handed over - each open criterion has",
              "  its record in this chapter, an owner and a date; handover",
              "  with a list of exceptions is a decision the owner signs,",
              "  not a default"]
    emit("int_accept", lines)
    return dict(met=met, total=len(criteria))


def basis() -> None:
    lines = ["D-054 commissioning, acceptance and handover basis",
             "  1 every energisation by a named authorised person, with a",
             "    permit and its prerequisites closed; instruments in date",
             "  2 progressive verification: each result against an expected",
             "    value and a written criterion (strings by the model, relays",
             "    by the settings file, controller by the requirement)",
             "  3 failed tests follow the disposition written in the pack",
             "    before the test; deviations decided by their owner",
             "  4 auxiliary systems accepted as chains; fire acceptance by",
             "    the full cause-and-effect matrix, never a live discharge",
             "  5 every grid requirement traced to a test, a type test or",
             "    an accepted declaration; a forecast score proves nothing",
             "  6 export energised in order, each step with its permission;",
             "    phasing proven before any parallel",
             "  7 handover data validated (fields, keys, references,",
             "    revisions), trial-imported and restored before acceptance",
             "  8 handover only with emergency roles, contacts and drills done",
             "  open: approved commissioning procedures and the network",
             "    operator's acceptance tests and witness plan (U-131)"]
    emit("int_basis", lines)


if __name__ == "__main__":
    by_hand()
    acceptance()
    basis()
