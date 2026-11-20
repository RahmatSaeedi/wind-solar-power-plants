"""Chapter 34, lesson F: the interface between the fire system and the
plant control, kept apart from dispatch - the signal list and its
checks, who may acknowledge and who may reset, the fire panel's own
standby supply, hard-wired life-safety actions independent of the PLC,
behaviour when the interface fails, and the availability of a
hard-wired against a networked path.

Run from the project root:   python -m companion.ch34.examples_f
Writes companion/ch34/expected/f_*.txt.
Teaching values (A-390); the fire strategy, the fire-system designer and
the authority decide the real interfaces (ch 32, U-110). No suppression
or detection design is prescribed here.
"""
from __future__ import annotations

from companion.ch34 import sources as src
from companion.ch34.common import emit
from plantp import instrumentation as ic


# [start: firecheck]
def check_fire(rows) -> list[str]:
    """Rules: alarms to the plant are normally-closed contacts; commands
    are hard-wired, never over the serial link; only the fire panel
    resets."""
    errs = []
    for sig, direc, kind, fail, reset in rows:
        if direc == "fire -> plant" and kind.startswith("hardwired") \
                and "NC" not in kind:
            errs.append(f"{sig}: alarm contact not fail-safe")
        if ("command" in sig or "request" in sig) and "serial" in kind:
            errs.append(f"{sig}: command over the serial link")
        if reset not in ("fire panel", "n/a"):
            errs.append(f"{sig}: reset outside the fire panel")
    return errs
# [end: firecheck]


def signals() -> None:
    draft = [list(r) for r in src.FIRE]
    draft[0][2] = "hardwired NO"                         # planted: open on alarm only
    draft[4][2] = "serial"                               # planted: command over serial
    draft[2][4] = "plant HMI"                            # planted: reset at the plant
    lines = ["fire-system interface signals and their checks (teaching)",
             "  signal                              path                failure state"]
    for sig, direc, kind, fail, reset in src.FIRE:
        lines.append(f"  {sig:35s} {kind:19s} {fail}")
    e_draft = check_fire([tuple(r) for r in draft])
    lines += [f"  draft findings ({len(e_draft)}):"] + [f"    {e}" for e in e_draft]
    lines += [f"  the list above: {len(check_fire(src.FIRE))} findings",
              "  the alarm contacts open on alarm and on a broken wire, so",
              "  a cut cable looks like an alarm, not like silence; the",
              "  serial link only adds detail and carries no command"]
    emit("f_signals", lines)


def authority() -> None:
    rows = [("see the alarm on the plant HMI", "operator", "plant HMI"),
            ("acknowledge the HMI alarm display", "operator", "plant HMI"),
            ("silence or reset the fire panel", "authorised person", "fire panel"),
            ("isolate a zone or an output", "authorised, permit", "fire panel"),
            ("restart a PCS after a fire alarm", "operator, after reset", "plant HMI"),
            ("override a fire stop for dispatch", "nobody", "-")]
    lines = ["who may do what at the fire interface (teaching)",
             "  action                              who                     where"]
    for a, w, p in rows:
        lines.append(f"  {a:35s} {w:23s} {p}")
    lines += ["  acknowledging a screen is not resetting a fire system:",
              "  the plant HMI shows and acknowledges, the fire panel",
              "  resets, and no dispatch instruction or revenue reason",
              "  can override a life-safety stop"]
    emit("f_authority", lines)


def standby() -> None:
    i_standby, h_standby = 1.2, 24.0         # A, h (teaching; the fire code sets the hours)
    i_alarm, h_alarm = 4.0, 0.5
    ah = i_standby * h_standby + i_alarm * h_alarm
    sized = ah * 1.25
    lines = ["the fire panel's own standby battery (teaching currents and times)",
             f"  standby {i_standby} A x {h_standby:.0f} h + alarm {i_alarm} A x"
             f" {h_alarm} h = {ah:.1f} Ah",
             f"  with 25 % for ageing: {sized:.1f} Ah -> next size 40 Ah",
             "  the hours come from the fire code and the fire strategy;",
             "  the point is independence: the fire panel does not borrow",
             "  the plant's 110 V battery or UPS, so a plant blackout",
             "  cannot silence it (lesson E)"]
    emit("f_standby", lines)


def independence() -> None:
    p = src.PLC
    t_plc = ic.response_budget(p["input_ms"], p["scan_ms"], p["output_ms"], p["comms_ms"])
    lines = ["BESS container fire: HVAC off and PCS stop - by which path?",
             f"  hard-wired from the fire panel: relay about 20 ms",
             f"  through the plant PLC: up to {t_plc:.0f} ms",
             "  both are fast enough; the reason for the hard-wired path",
             "  is independence: a PLC that is stopped, being programmed",
             "  or faulty cannot block a life-safety action; the PLC gets",
             "  a copy of the signal to log and display, and its own",
             "  stop of the PCS is a second, not the only, path"]
    emit("f_indep", lines)


def failures() -> None:
    rows = [("alarm wire cut", "alarm at the plant (NC opens)", "T-32"),
            ("serial link lost", "detail stale, alarm; no action", "T-33"),
            ("plant PLC stopped", "fire actions still happen", "T-34"),
            ("fire panel power lost", "fault contact opens: alarm", "T-35"),
            ("plant 'healthy' to fire panel lost", "fault shown on fire panel", "T-36")]
    lines = ["behaviour when the interface itself fails (teaching design intent)",
             "  failure                              behaviour                        test"]
    for a, b, t in rows:
        lines.append(f"  {a:36s} {b:32s} {t}")
    lines += ["  every failure ends in an alarm someone sees, never in a",
              "  silent loss; none of them starts or stops generation by",
              "  itself except the fire panel's own commands"]
    emit("f_failures", lines)


def path_availability() -> None:
    a_hw = ic.availability(500_000.0, 4.0)                 # relay contacts and wiring
    a_sw = ic.availability(200_000.0, 4.0)                 # one network switch
    a_plc = ic.availability(src.PLC["mtbf_h"], src.PLC["mttr_h"])
    a_net = a_sw * a_sw * a_plc
    lines = ["availability of the alarm path to the plant (teaching rates)",
             f"  hard-wired contact path: {(1 - a_hw) * 8760:.3f} h a year unavailable",
             f"  two switches and the PLC in series: {(1 - a_net) * 8760:.2f} h a year",
             "  the networked path is also good, but it fails with every",
             "  network or PLC fault, the ones a fire may cause; the",
             "  hard-wired path is short, supervised and independent"]
    emit("f_avail", lines)


if __name__ == "__main__":
    signals()
    authority()
    standby()
    independence()
    failures()
    path_availability()
