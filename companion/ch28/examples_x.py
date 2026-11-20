"""Chapter 28 - expansion round 13: the intertrip channel's own
availability and the exposure it leaves, and the timing budget of the
intertrip against the line's reclose.

Run from the project root:   python -m companion.ch28.examples_x
Writes companion/ch28/expected/x_*.txt. Teaching values.
"""
from __future__ import annotations

from companion.ch28.common import emit


def channel() -> None:
    ndz_hours = 1760.0                       # lesson C: passive relays blind
    lines = ["the intertrip channel's availability and the exposure it leaves",
             "  channel availability   hours/yr without it   blind hours/yr left"]
    for a in (0.99, 0.999, 0.9999):
        out = (1 - a) * 8760
        left = (1 - a) * ndz_hours
        lines.append(f"  {100 * a:19.2f} %   {out:19.1f}   {left:19.2f}")
    lines += ["  the intertrip closes the islanding gap only while its",
              "  channel works: a duplicated or supervised channel (an",
              "  alarm when it fails, export held back until it returns)",
              "  makes the residual exposure a matter of hours, written in",
              "  the study and agreed with the operator"]
    emit("x_channel", lines)


def timing() -> None:
    parts = {"grid-end protection operates": 30, "grid-end breaker opens": 50,
             "intertrip send and channel": 20, "plant breaker opens": 50}
    total = sum(parts.values())
    lines = ["intertrip timing budget (ms, teaching)"]
    for k, v in parts.items():
        lines.append(f"  {k:34s} {v:4d}")
    lines += [f"  plant off after about {total} ms; with the fastest reclose of",
              f"  300 ms the margin is {300 - total} ms (lesson B, reclose) - the",
              "  channel's latency is a requirement of its own, tested end",
              "  to end before energisation (ch 26, 50)"]
    emit("x_timing", lines)


if __name__ == "__main__":
    channel()
    timing()
