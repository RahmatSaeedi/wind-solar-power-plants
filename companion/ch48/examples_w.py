"""Chapter 48, round w: spare I/O channels by card type, the plant's energy
reconciled from turbine and inverter meters to the revenue meter, devices
never staged at the network FAT, a calibration traceability chain and its
uncertainty, and the SCADA licence against the tag count.

Run from the project root:   python -m companion.ch48.examples_w
Writes companion/ch48/expected/w_*.txt and diagrams/data/ch48-*.csv.
Teaching values (A-498 to A-505); defensive administration only.
"""
from __future__ import annotations

import math

from companion.ch48.common import csv, emit

# ------------------------------------------------ 1. spare I/O channels
IO = {   # card type: (installed channels, used)
    "analogue in": (96, 88), "digital in": (192, 151), "digital out": (64, 61),
    "RTD in": (32, 24),
}


def io_spares(rule: float = 0.15) -> list:
    bad = [k for k, (n, u) in IO.items() if (n - u) / n < rule]
    lines = [f"spare channels in the RTU by card type (teaching rule {rule:.0%})"]
    lines += [f"  {k:12s} {n:4d} channels, {u:4d} used, {(n - u) / n:4.0%} spare"
              for k, (n, u) in IO.items()]
    lines += [f"  below the rule: {', '.join(bad)} - the next breaker added to",
              "  the substation needs analogue and output channels the RTU no",
              "  longer has; a card added later needs a slot, power and a",
              "  configuration change - spares are bought with the RTU"]
    emit("w_io", lines)
    return bad


# ------------------------------------------------ 2. energy reconciliation
def reconcile(wind=194.11, pv=108.36, losses=3.29, own=2.34, meter=295.14) -> dict:
    expected = wind + pv - losses - own
    gap = expected - meter
    u = math.sqrt((0.01 * wind) ** 2 + (0.005 * pv) ** 2 + (0.0035 * meter) ** 2
                  + (0.1 * losses) ** 2)
    steps = [(0, wind), (wind, wind + pv), (wind + pv, wind + pv - losses),
             (wind + pv - losses, expected), (0, meter)]
    csv("ch48-reconcile.csv", "k,base,height",
        [(k + 1, round(min(a, b), 2), round(abs(b - a), 2))
         for k, (a, b) in enumerate(steps)])
    lines = ["the year's energy from the turbine and inverter meters to the POC",
             "  meter (GWh; ch 15 losses and own use)",
             f"  turbines {wind:.2f} + PV {pv:.2f} - losses {losses:.2f} - own use "
             f"{own:.2f} = {expected:.2f}",
             f"  revenue meter {meter:.2f}: gap {gap:.2f} GWh ({gap / meter:.2%})",
             f"  explained by the chain's uncertainty: +/-{u:.2f} GWh (turbine meters",
             "  1 %, inverter meters 0.5 %, revenue chain 0.35 %, loss model 10 %)",
             "  the gap is inside what the meters can explain - not a finding;",
             "  the largest term is the turbine meters: if the monthly gap",
             "  grows past it, they are the first to be checked (ch 37)"]
    emit("w_reconcile", lines)
    return dict(expected=expected, gap=gap, u=u)


# ------------------------------------------------ 3. devices never staged
STAGED = {"SW-T01", "SW-T02", "SW-T03", "SW-T04", "SW-T05", "SW-T06", "SW-T07",
          "SW-T08", "SW-T10", "SW-T11", "SW-T12", "SW-SUB", "GW-PV1", "RTU-1", "CLK-1"}
INSTALLED = STAGED - {"SW-T10"} | {"SW-T09", "GW-PV2", "CLK-2", "SW-T10"}


def staging() -> dict:
    never = sorted(INSTALLED - STAGED)
    lines = [f"network FAT on a staging rack: {len(STAGED)} devices staged, "
             f"{len(INSTALLED)} installed",
             f"  installed but never staged: {', '.join(never)}",
             "  SW-T09 is the switch replaced at site (lesson C, older",
             "  firmware); GW-PV2 and the second clock arrived late and went",
             "  straight in - their configuration and firmware were never",
             "  proven on the rack; they get the staging tests at site",
             "  before the SAT, with the same records"]
    emit("w_staging", lines)
    return dict(never=never)


# ------------------------------------------------ 4. calibration chain
CHAIN = [   # level, standard uncertainty (k=1) added at that level, %
    ("national reference", 0.10), ("accredited laboratory standard", 0.25),
    ("laboratory transfer to the instrument", 0.45),
]


def cal_chain(tolerance: float = 1.5, k: float = 2.0) -> dict:
    u = math.sqrt(sum(x * x for _, x in CHAIN))
    big_u = k * u
    tur = tolerance / big_u
    lines = ["traceability chain of a pyranometer's calibration (teaching values)",
             "  level                                  adds u %   chain u %"]
    acc = 0.0
    for name, x in CHAIN:
        acc = math.sqrt(acc ** 2 + x ** 2)
        lines.append(f"  {name:37s}  {x:8.2f}   {acc:9.2f}")
    lines += [f"  expanded (k = {k:.0f}): {big_u:.2f} %; the instrument's tolerance "
              f"+/-{tolerance} %",
              f"  ratio tolerance / uncertainty: {tur:.1f} (ch 40 asks for 4)",
              "  the last step adds the most: a calibration whose own",
              "  uncertainty is two thirds of the tolerance cannot tell a",
              "  good sensor from a marginal one - the certificate's",
              "  uncertainty is read before its 'pass'"]
    emit("w_chain", lines)
    return dict(u=u, U=big_u, tur=tur)


# ------------------------------------------------ 5. licence and tag count
def licence(tags_now: int = 4200, per_block: int = 120, blocks: int = 10,
            battery: int = 600, pack: int = 5000) -> dict:
    later = tags_now + per_block * blocks + battery
    lines = [f"SCADA licence of {pack:,} tags against the tag database",
             f"  today {tags_now:,}; a later PV extension of ten blocks "
             f"(+{per_block * blocks:,}, teaching) and a",
             f"  battery augmentation (+{battery}): {later:,} tags",
             f"  the licence runs out at {pack:,}: {'enough' if later <= pack else 'short by ' + format(later - pack, ',')}",
             "  the licence is sized from the tag database's growth, not",
             "  today's count - a full licence blocks the next tag on the day",
             "  the extension is commissioned (ch 18 kept room to expand)"]
    emit("w_licence", lines)
    return dict(later=later, short=max(0, later - pack))


if __name__ == "__main__":
    io_spares()
    reconcile()
    staging()
    cal_chain()
    licence()
