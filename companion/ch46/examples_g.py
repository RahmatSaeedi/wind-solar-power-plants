"""Chapter 46, lesson C (deeper): a trip matrix as designed against as
wired, wire markers at both ends, CT circuits searched for their earth
points, the panel shop's wiring hours, a FAT punch list against the
shipping rule, and FAT changes against the drawing revisions they need.

Run from the project root:   python -m companion.ch46.examples_g
Writes companion/ch46/expected/g_*.txt.
Teaching values (A-486, A-487); no test procedure, no live work.
"""
from __future__ import annotations

from companion.ch46 import sources as src
from companion.ch46.common import emit
from plantp import cablemfg as km

SECTION_A = src.PANELS[:5]                 # INC-A ... BESS-A, then BC
SECTION_B = src.PANELS[6:]                 # INC-B ... SST


# ------------------------------------------------ 1. trip matrix
TRIP_DESIGN = {   # (relay panel, function): breakers it trips
    ("WS1", "50/51"): {"WS1"}, ("WS1", "51N"): {"WS1"},
    ("WS1", "50BF"): {"INC-A", "BC"},
    ("BESS-A", "50/51"): {"BESS-A"}, ("BESS-A", "50BF"): {"INC-A", "BC"},
    ("WS3", "50/51"): {"WS3"}, ("WS3", "50BF"): {"INC-B", "BC"},
    ("INC-A", "51"): {"INC-A"}, ("INC-A", "87T"): {"INC-A", "HV-A"},
    ("INC-B", "51"): {"INC-B"}, ("INC-B", "87T"): {"INC-B", "HV-B"},
    ("BC", "51"): {"BC"},
}
TRIP_FAT = {k: set(v) for k, v in TRIP_DESIGN.items()}
TRIP_FAT[("WS1", "50BF")] = {"INC-B", "BC"}
TRIP_FAT[("INC-A", "87T")] = {"INC-A"}


def trip_matrix() -> list:
    diffs = []
    for k, want in TRIP_DESIGN.items():
        got = TRIP_FAT[k]
        if got != want:
            diffs.append((k, sorted(want - got), sorted(got - want)))
    lines = [f"trip matrix: {len(TRIP_DESIGN)} protection functions, designed "
             "against the FAT record",
             "  relay   function   should trip but does not   trips but should not"]
    for (p, f), miss, extra in diffs:
        lines.append(f"  {p:6s}  {f:8s}   {', '.join(miss) or '-':25s}  "
                     f"{', '.join(extra) or '-'}")
    lines += ["  WS1 sits on section A (with INC-A); its breaker-failure stage",
              "  opens section B's incomer instead, so a stuck WS1 breaker",
              "  leaves the fault fed through INC-A until a slower backup acts;",
              "  INC-A's transformer differential no longer opens the 132 kV",
              "  side - each function still 'works' in a functional test that",
              "  only watches its own breaker, so the whole matrix is checked"]
    emit("g_trips", lines)
    return diffs


# ------------------------------------------------ 2. wire markers
MARKERS = [(w, str(w), str(w)) for w in range(101, 119)]
MARKERS[6] = (107, "107", "170")           # transposed digits
MARKERS[11] = (112, "112", "")             # no marker at end B
MARKERS[15] = (116, "115", "116")          # wrong marker at end A


def markers() -> list:
    out = []
    seen: dict[str, list] = {}
    for w, a, b in MARKERS:
        for end, m in (("A", a), ("B", b)):
            if not m:
                out.append(f"wire {w}: no marker at end {end}")
            elif m != str(w):
                out.append(f"wire {w}: end {end} marked {m}")
            if m:
                seen.setdefault(m, []).append((w, end))
    for m, uses in sorted(seen.items()):
        wires = {w for w, _ in uses}
        if len(wires) > 1:
            out.append(f"marker {m} on wires {', '.join(str(w) for w in sorted(wires))}")
    lines = [f"wire markers of panel WS1: {len(MARKERS)} wires, both ends read"]
    lines += [f"  {x}" for x in out]
    lines += [f"  {len(out)} findings on 3 wires: a technician who follows marker",
              "  115 at site arrives at two places; a marker is the drawing's",
              "  address on the wire, and both ends are read at the FAT"]
    emit("g_markers", lines)
    return out


# ------------------------------------------------ 3. CT circuits and earths
CT_WIRES = [   # terminal to terminal; PE: an earth bar
    ("WS1/T1.1:S2", "WS1/X1:6"), ("WS1/X1:6", "WS1/F11:N"), ("WS1/X1:6", "PE:WS1"),
    ("WS1/T1.2:S2", "WS1/X1:12"), ("WS1/X1:12", "RR/MTR1:N"),
    ("WS1/X1:12", "PE:WS1"), ("RR/MTR1:N", "PE:RR"),
    ("PVF2/T1.1:S2", "PVF2/X1:6"), ("PVF2/X1:6", "PVF2/F11:N"),
    ("BESS-A/T1.1:S2", "BESS-A/X1:6"), ("BESS-A/X1:6", "BESS-A/F11:N"),
    ("BESS-A/X1:6", "PE:BESS-A"),
]


def ct_earths() -> list:
    # the earth bars are all joined through the plant's earth, so they are
    # left out of the search and each wire to a bar counts as one earth point
    def is_pe(t):
        return t.startswith("PE:")

    groups = km.circuits([(a, b) for a, b in CT_WIRES
                          if not is_pe(a) and not is_pe(b)])
    lines = ["CT star-point circuits searched from the wire list for earth points",
             "  circuit (CT terminal)      earths   verdict"]
    out = []
    for g in groups:
        ct = [t for t in g if ":S2" in t]
        if not ct:
            continue
        pe = sorted(b if is_pe(b) else a for a, b in CT_WIRES
                    if (is_pe(a) and b in g) or (is_pe(b) and a in g))
        v = "ok" if len(pe) == 1 else ("NOT EARTHED" if not pe else "TWO EARTHS")
        out.append((ct[0], len(pe), v))
        lines.append(f"  {ct[0]:25s}  {len(pe):6d}   {v}")
    lines += ["  a CT circuit is earthed at one point: none leaves it floating",
              "  at an unknown voltage; two (here the panel and the relay",
              "  room's meter) close a loop through the earth grid, and a",
              "  fault elsewhere drives current through it that the relay",
              "  reads as a fault of its own - found by searching the wire",
              "  list, not by a test"]
    emit("g_ctearth", lines)
    return out


# ------------------------------------------------ 4. wiring hours
WIRES_PER = {"incomer": 140, "feeder": 95, "coupler": 80, "station": 70}
KIND = {p: ("incomer" if p.startswith("INC") else "coupler" if p == "BC" else
            "station" if p == "SST" else "feeder") for p in src.PANELS}


def wiring_hours(min_wire: float = 9.0, min_check: float = 1.5,
                 wirers: int = 2, shift_h: float = 7.5) -> dict:
    wires = sum(WIRES_PER[KIND[p]] for p in src.PANELS)
    build = wires * min_wire / 60
    check_hand = wires * min_check / 60
    check_auto = len(src.PANELS) * 0.5
    days = (build + check_hand) / (wirers * shift_h)
    days_auto = (build + check_auto) / (wirers * shift_h)
    lines = [f"panel shop load for the {len(src.PANELS)} control cabinets of the "
             "line-up (teaching)",
             f"  wires: {wires}; build {min_wire:.0f} min a wire: {build:.0f} h",
             f"  point-to-point by hand, {min_check} min a wire: {check_hand:.0f} h; "
             f"with a tester: {check_auto:.0f} h",
             f"  {wirers} wirers on one shift: {days:.0f} working days by hand, "
             f"{days_auto:.0f} with the tester",
             f"  the check is {check_hand / (build + check_hand):.0%} of the work "
             "by hand; the tester saves",
             f"  {days - days_auto:.0f} days and checks every wire the same way "
             "(ch 40's automatic",
             "  wiring tester) - and its file becomes the panel's record"]
    emit("g_hours", lines)
    return dict(wires=wires, build=build, days=days, days_auto=days_auto)


# ------------------------------------------------ 5. FAT punch list
PUNCH = [   # item, panel, category, closed before the shipping date?
    ("trip coils swapped", "WS1", "A", True),
    ("CT wire X1:5 missing", "WS1", "A", True),
    ("extra link X4:3-X4:4", "WS1", "A", True),
    ("two wires on X1:3", "WS1", "A", True),
    ("relay tms 0.25", "PVF2", "A", True),
    ("relay firmware 7.1", "SST", "A", False),
    ("pole L2 resistance", "PVF1", "A", True),
    ("pole L2 timing", "WS3", "A", False),
    ("CT 400/1 fitted", "PVF3", "A", True),
    ("CT core 2 reversed", "BESS-B", "A", True),
    ("arrester set missing", "WS2", "B", False),
    ("redlines not in drawings", "WS1", "B", False),
    ("label text faded", "BC", "C", False),
    ("paint scratch", "INC-B", "C", False),
]


def punch() -> dict:
    hold = sorted({p for _, p, c, ok in PUNCH if c == "A" and not ok})
    open_b = [(i, p) for i, p, c, ok in PUNCH if c == "B" and not ok]
    lines = [f"FAT punch list of the line-up: {len(PUNCH)} items (A: before "
             "shipment, B: dated", "  plan to close at site, C: when convenient)",
             "  category   items   open on the shipping date"]
    for c in "ABC":
        n = sum(1 for _, _, cc, _ in PUNCH if cc == c)
        o = sum(1 for _, _, cc, ok in PUNCH if cc == c and not ok)
        lines.append(f"  {c:8s}   {n:5d}   {o}")
    lines += [f"  panels held at the factory (open A items): {', '.join(hold)}",
              "  the line-up ships as transport sections; a held panel holds",
              "  its section, so the A items decide the date - the open B",
              "  items travel with a dated plan and an owner"]
    emit("g_punch", lines)
    return dict(hold=hold, open_b=open_b)


# ------------------------------------------------ 6. FAT changes and drawings
CHANGES = [   # change, kind, drawing, revision issued?
    ("C-01 trip coils rewired to the drawing", "to drawing", "TD-WS1-03", None),
    ("C-02 X1:3/X1:4 rewired to the drawing", "to drawing", "TD-WS1-02", None),
    ("C-03 link X4:3-X4:4 removed", "to drawing", "TD-WS1-04", None),
    ("C-04 interposing relay K5 added for intertrip", "design", "TD-WS1-03", False),
    ("C-05 CT of PVF3 replaced, 600/1", "to drawing", "TD-PVF3-02", None),
    ("C-06 two cable positions on BESS-A/B", "design", "TD-BESS-05", False),
    ("C-07 VT terminal drawing created", "design", "TD-WS1-06", True),
]


def redlines() -> list:
    gaps = [(c, d) for c, k, d, rev in CHANGES if k == "design" and not rev]
    lines = [f"{len(CHANGES)} changes made at the FAT, and the drawings they need",
             "  change                                        kind        revised"]
    for c, k, d, rev in CHANGES:
        r = "-" if rev is None else ("yes" if rev else "NO")
        lines.append(f"  {c:45s} {k:10s}  {r}")
    lines += ["  gaps: " + "; ".join(f"{d}" for _, d in gaps),
              "  a fix that brings the panel back to its drawing needs no",
              "  revision; a change of design does, or the as-built package",
              "  describes a panel nobody built - the redlines are carried",
              "  into revisions before the panel's records are accepted (ch 38)"]
    emit("g_redlines", lines)
    return gaps


if __name__ == "__main__":
    trip_matrix()
    markers()
    ct_earths()
    wiring_hours()
    punch()
    redlines()
