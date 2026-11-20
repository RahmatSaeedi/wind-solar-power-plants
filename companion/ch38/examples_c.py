"""Chapter 38, lesson C (the engineering drawing system): what each drawing
type communicates and where it comes from, the identifiers a drawing must
carry, the three linked drawings of one subsystem (PV block B07), and
the ambiguity errors that a title-block and cross-reference check finds.

Run from the project root:   python -m companion.ch38.examples_c
Writes companion/ch38/expected/c_*.txt.
Teaching examples (A-418).
"""
from __future__ import annotations

from companion.ch38.common import emit

TYPES = [  # drawing, what it answers, source model
    ("concept block diagram", "which functions and flows", "architecture"),
    ("energy-flow diagram", "where energy goes, is lost", "yield model"),
    ("site layout", "where everything stands", "GIS"),
    ("one-line diagram", "how power is connected", "network model"),
    ("circuit schematic", "how one circuit works", "design tool"),
    ("wiring / termination", "which wire to which terminal", "cable database"),
    ("grounding layout", "earth conductors, joints", "earthing study"),
    ("protection zones", "which relay covers what", "settings"),
    ("control architecture", "who commands what", "control design"),
    ("physical network", "cables, ports, switches", "network database"),
    ("logical network", "subnets, flows, services", "network database"),
    ("zones and conduits", "allowed paths between zones", "security design"),
    ("panel arrangement", "where devices sit", "panel design"),
    ("assembly / exploded", "how parts fit together", "3D model"),
    ("fabrication drawing", "how one part is made", "3D model"),
    ("as-built drawing", "what was actually built", "redlines, survey")]


def drawing_types() -> None:
    lines = ["sixteen drawing types and the one question each answers",
             "  drawing                 answers                        source"]
    for a, b, c in TYPES:
        lines.append(f"  {a:22s}  {b:29s}  {c}")
    lines += ["  a one-line says how power is connected, not which wire",
              "  goes where; a wiring diagram says which wire, not how the",
              "  network is built - none can stand in for another"]
    emit("c_types", lines)


def b07_linked() -> None:
    items = [("=PVF2-Q1", "one-line", "feeder breaker 630 A", "protection zone Z-PVF2"),
             ("=PVF2-3-T1", "one-line", "unit transformer 5.6 MVA", "zone Z-PVF2-3"),
             ("=PVF2-3-U1", "control", "inverter, set points P, Q", "port SW-PV2:7"),
             ("SW-PV2", "network", "field switch, PV ring 2", "zone field-pv"),
             ("PPC", "control", "plant controller", "control zone")]
    lines = ["PV block PVF2-3 in three linked drawings (tags shared, teaching)",
             "  tag          drawing    shows                         links to"]
    for a, b, c, d in items:
        lines.append(f"  {a:12s} {b:9s}  {c:28s}  {d}")
    lines += ["  the same tag appears in every drawing that shows the item;",
              "  each drawing lists the drawings it continues on, with",
              "  their revision. The one-line shows the breaker, the",
              "  control drawing the command, the network drawing the",
              "  port the command travels through"]
    emit("c_b07", lines)


def title_blocks() -> None:
    blocks = [  # drawing, (number, rev, status, scale, legend, refs, checker)
        ("one-line", (1, 1, 1, 1, 1, 1, 1)),
        ("wiring B07", (1, 1, 1, 0, 1, 1, 1)),       # 'NTS' missing on a schematic
        ("network ring 2", (1, 1, 1, 1, 0, 0, 1)),   # no legend, no continuation refs
        ("foundation B07", (1, 0, 1, 1, 1, 1, 0)),   # no revision, no checker
        ("panel PPC", (1, 1, 1, 1, 1, 0, 1))]
    fields = ["number", "revision", "status", "scale", "legend", "references", "checker"]
    lines = ["title-block and reference check of five drawings (planted gaps)",
             "  drawing           missing"]
    total = 0
    for name, flags in blocks:
        miss = [f for f, ok in zip(fields, flags) if not ok]
        total += len(miss)
        lines.append(f"  {name:16s}  {', '.join(miss) if miss else '-'}")
    lines += [f"  {total} gaps in five drawings; a drawing without a revision",
              "  cannot be matched to the register, one without a legend",
              "  makes its reader guess what a symbol means, one without",
              "  continuation references leaves a line that ends nowhere"]
    emit("c_titles", lines)


def ambiguity() -> None:
    rows = [("'see detail' without the drawing number", "which detail?"),
            ("a tag that differs by one character", "two items or one?"),
            ("'existing' without a survey date", "existing when?"),
            ("units missing on a dimension", "mm or m?"),
            ("a cloud with no revision triangle", "which change?"),
            ("'by others' without naming the party", "nobody's scope")]
    lines = ["six common ambiguities and the question each leaves",
             "  ambiguity                                  question"]
    for a, b in rows:
        lines.append(f"  {a:42s} {b}")
    lines += ["  each one costs a technical query, a site stop or a wrong",
              "  installation; the checker's list asks for each by name"]
    emit("c_ambiguity", lines)


if __name__ == "__main__":
    drawing_types()
    b07_linked()
    title_blocks()
    ambiguity()
