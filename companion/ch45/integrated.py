"""Chapter 45 - three integrated Plant P examples: usable energy, C-rate,
round-trip efficiency and degradation of the S1 battery by hand; the
acceptance of one container's evidence; and the battery manufacturing and
evidence basis D-049.

Run from the project root:   python -m companion.ch45.integrated
Writes companion/ch45/expected/int_*.txt.
"""
from __future__ import annotations

from companion.ch45 import sources as src
from companion.ch45.common import emit
from plantp import storage as st

C, B = src.CELL, src.BUILD


# [start: hand]
def by_hand(window=(0.10, 0.90), rt_ac: float = 0.86, fade: float = 0.02,
            years=(0, 10, 20)) -> dict:
    n = B["s_module"] * B["m_rack"] * B["r_container"] * B["containers"]
    e_nom = n * C["q_ah"] * C["v_nom"] / 1e6                 # MWh
    usable = e_nom * (window[1] - window[0])
    p_mw = B["pcs"] * B["pcs_mw"]
    c_rate = p_mw / e_nom
    e_out = usable * rt_ac ** 0.5                            # discharge side
    # [end: hand]
    lines = ["the S1 battery by hand (ch 19 build, teaching values)",
             f"  {n:,} cells x {C['q_ah']:.0f} Ah x {C['v_nom']} V = "
             f"{e_nom:.2f} MWh nominal",
             f"  window {window[0]:.0%}-{window[1]:.0%}: {usable:.2f} MWh usable "
             "at the cells",
             f"  {p_mw:.0f} MW of PCS: C-rate {c_rate:.2f} on the nominal energy",
             f"  round trip {rt_ac:.0%} at AC: about {e_out:.1f} MWh delivered "
             "from a full window",
             f"  fade {fade:.0%} a year (linear, teaching):",
             "  year   health   usable MWh"]
    out = {}
    for y in years:
        h = 1 - fade * y
        out[y] = usable * h
        lines.append(f"  {y:4d}   {h:6.0%}   {usable * h:10.2f}")
    lines += ["  check: 40 MWh nominal at 20 MW is a two-hour battery, and",
              "  the window keeps a fifth of it unused; the linear fade is a",
              "  teaching line - ch 19 restores the usable energy by",
              "  augmentation in years 8 and 13 (D-023)"]
    emit("int_hand", lines)
    _ = st
    return dict(n=n, e_nom=e_nom, usable=usable, c_rate=c_rate, out=out)


def acceptance() -> dict:
    from companion.ch45 import examples_b as eb
    from companion.ch45 import lab_d
    g = eb.grading()
    w = eb.welds()
    b = eb.bms()
    soc = lab_d.soc_day()
    lines = ["evidence for container C5 before it ships, summarised",
             f"  cell lot L4506: {len(g['f_k'])} leakers removed at a 14-day rest "
             "(file read);",
             "    lot L4507's file accepted without reading its rest time -",
             "    the trail of lab D starts here",
             f"  module welds: {len(w['bad'])} cold welds in one module - rework "
             "and re-measure",
             f"  BMS configuration: {', '.join(b['bad'])} above the cell limit -",
             "    correct it, record the new fingerprint",
             f"  SOC simulator v1 (training model): invariant error {soc['err']:.0e}"
             " Ah",
             "  missing: OCV spread after a rest at site acceptance - added",
             "  decision: C5 ships after the weld rework and the BMS fix;",
             "  the site test plan gains the OCV check; the cell maker's rest",
             "  time becomes a contract item with its record"]
    emit("int_accept", lines)
    return dict(bad_bms=b["bad"], welds=len(w["bad"]))


def basis() -> None:
    lines = ["D-049 battery manufacturing and evidence basis",
             "  1 coating weight, dry-room dew point, formation and rest",
             "    records of the cell maker delivered with each lot",
             "  2 every cell graded (capacity, resistance, K-value) and",
             "    matched; bins and IDs recorded per module",
             "  3 every weld's resistance measured and kept; torque and",
             "    insulation of each module and rack recorded",
             "  4 BMS limits checked against the cell data with margins;",
             "    the configuration fingerprinted at factory and site",
             "  5 OCV spread after a rest at site acceptance; balancing",
             "    duty by module exported to monitoring",
             "  6 transport SOC, isolation by division, replacement modules",
             "    brought to the rack's SOC; take-back route in the contract",
             "  7 later findings: lot files checked before use; lots kept",
             "    together; BMS rules for alarm-before-trip; a site rest check",
             "    sees strong leakers only (weeks), the duty signal the weak;",
             "    standby drain of a waiting container; contactor and",
             "    insulation trends in the rack record; a second cell factory",
             "    is a product change",
             "  open: the cell maker's qualification and lot data for the",
             "    exact cell, the integrator's BMS records (U-126)"]
    emit("int_basis", lines)


if __name__ == "__main__":
    by_hand()
    acceptance()
    basis()
