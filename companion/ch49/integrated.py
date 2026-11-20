"""Chapter 49, integrated Plant P examples: three numbers by hand, the
readiness gate of the next package and the construction basis D-053.

Run from the project root:   python -m companion.ch49.integrated
Writes companion/ch49/expected/int_*.txt.
"""
from __future__ import annotations

from companion.ch49 import sources as src
from companion.ch49.common import emit
from plantp import construction as con
from companion.ch29 import sources as s29


def by_hand() -> dict:
    d = s29.DEMAND
    prog = con.rules_of_credit(src.CREDIT, {"received and inspected": 1.0, "mounted": 0.8,
                                            "clamps torqued": 0.6, "serial captured": 0.55,
                                            "inspected": 0.3})
    t12 = src.SITE_TEAM["mobilise_min"] + src.FRONTS["T12 erection"] / src.SITE_TEAM[
        "road_kmh"] * 60
    dust = d["dust_l_m2_day"] * d["road_area_m2"] / 1000 * d["dust_days"] / 18
    lines = ["three numbers by hand, checked by the scripts",
             f"  progress: 0.05x1 + 0.55x0.8 + 0.15x0.6 + 0.05x0.55 + 0.20x0.3 = {prog:.3f}",
             f"  response to T12: 6 + 9.4 / 25 x 60 = {t12:.1f} min",
             f"  dust water a month: 1.5 L/m2 x 168,000 m2 x 300 / 18 days = {dust:,.0f} m3"]
    emit("int_hand", lines)
    return dict(prog=prog, t12=t12, dust=dust)


def gate(package: str = "WP14 MV terminations") -> dict:
    checks = {
        "approved method statement": src.METHODS["MV terminations"][1] == "approved",
        "drawings issued for construction": all(s == "IFC" for _, _, s in
                                                src.DRAWINGS[package]),
        "competent crew (certificates in date)": all(
            u is None or u >= src.TODAY for _, _, u in src.ROSTER["jointer"]),
        "permits and approvals for the front": True,
        "predecessors released (station set, backfill)": True,
        "response time to the front within target": src.SITE_TEAM["mobilise_min"]
        + src.FRONTS["PV block PVF1-3"] / src.SITE_TEAM["road_kmh"] * 60
        <= src.SITE_TEAM["target_min"],
    }
    lines = [f"readiness gate before issuing {package}"]
    lines += [f"  [{'x' if v else ' '}] {k}" for k, v in checks.items()]
    n = sum(checks.values())
    lines += [f"  {n} of {len(checks)}: not issued - three readiness items fail",
              "  together (method, drawing, jointer); the package is a",
              "  bundle of its prerequisites, and a crew sent without them",
              "  works on what is not ready"]
    emit("int_gate", lines)
    return checks


def basis() -> None:
    lines = ["D-053 construction and installation basis",
             "  1 a package is issued only through its readiness gate:",
             "    approvals, method statement, competent crew, drawings IFC,",
             "    predecessors released, emergency response in reach",
             "  2 packages sequenced with crews and hold points; booking the",
             "    package that can start first; ready work only in the",
             "    six-week look-ahead",
             "  3 installation records name the tool, the inspector and the",
             "    value: positions, torque, as-laid, terminations, continuity",
             "  4 turnover by subsystem: A sheets complete, no open A punch,",
             "    the package listing what is still missing",
             "  5 asset data captured at receipt, installation, test and",
             "    turnover; reconciled with the design register (tags,",
             "    serials, positions within 2 m)",
             "  6 auxiliary, fire and export systems turned over as their own",
             "    packages; fire impairments with measure, notice and end",
             "  7 construction water metered apart from the plant's; tickets",
             "    checked against the meter weekly",
             "  8 social-plan records reported as they are: grievances,",
             "    hiring, village traffic, chance finds",
             "  open: the contractor's method statements, permits and",
             "    approved plans (U-130)"]
    emit("int_basis", lines)


if __name__ == "__main__":
    by_hand()
    gate()
    basis()
