"""Chapter 23 - the one-line diagram as data.

Buses and branches carry a tag, a voltage, an owner, a protection zone
and the status of every parameter (confirmed, provisional or open), so a
program can trace a source to the point of connection, list every
interface it crosses, build the equipment schedule and run the design
checks a reviewer would run by eye.

Teaching code: real one-lines come from the design tools of the
project, drawn and checked by licensed engineers.
"""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

STATUS = ("confirmed", "provisional", "open")


# [start: model]
@dataclass
class Bus:
    tag: str
    kv: float
    owner: str = "plant"
    zone: str = ""                 # protection zone that covers the bus


@dataclass
class Branch:
    tag: str
    kind: str                      # transformer, cable, line, breaker, ...
    a: str                         # bus tags at the two ends
    b: str
    owner: str = "plant"
    zone: str = ""
    rating: dict = field(default_factory=dict)    # name -> value
    status: dict = field(default_factory=dict)    # name -> STATUS
    isolation: bool = False        # a point that can be opened and earthed
    meter: str = ""                # "revenue", "check" or ""
    test: str = ""                 # test boundary: who tests what

    def open_items(self) -> list[str]:
        return [k for k, s in self.status.items() if s != "confirmed"]


class OneLine:
    def __init__(self) -> None:
        self.buses: dict[str, Bus] = {}
        self.branches: list[Branch] = []

    def add_bus(self, *buses: Bus) -> "OneLine":
        for b in buses:
            self.buses[b.tag] = b
        return self

    def add(self, *branches: Branch) -> "OneLine":
        self.branches += branches
        return self

    def neighbours(self, bus: str):
        for br in self.branches:
            if br.a == bus:
                yield br, br.b
            elif br.b == bus:
                yield br, br.a
# [end: model]

    # [start: trace]
    def path(self, start: str, end: str) -> list[Branch]:
        """Branches on the shortest path from bus start to bus end
        (breadth-first search; a radial plant has exactly one)."""
        prev: dict[str, tuple[str, Branch] | None] = {start: None}
        queue = deque([start])
        while queue:
            bus = queue.popleft()
            if bus == end:
                break
            for br, nxt in self.neighbours(bus):
                if nxt not in prev:
                    prev[nxt] = (bus, br)
                    queue.append(nxt)
        if end not in prev:
            raise ValueError(f"no path from {start} to {end}")
        out, bus = [], end
        while prev[bus] is not None:
            bus, br = prev[bus]
            out.append(br)
        return out[::-1]

    def crossings(self, start: str, end: str) -> list[str]:
        """Every interface on the path: voltage changes, owner changes,
        protection zones entered, isolation points, meters, tests."""
        notes, bus = [], start
        zone = self.buses[start].zone
        for br in self.path(start, end):
            nxt = br.b if br.a == bus else br.a
            b0, b1 = self.buses[bus], self.buses[nxt]
            if b1.kv != b0.kv:
                notes.append(f"{br.tag}: voltage {b0.kv:g} -> {b1.kv:g} kV")
            if b1.owner != b0.owner or br.owner != b0.owner:
                notes.append(f"{br.tag}: owner {b0.owner} -> {b1.owner}")
            if br.zone and br.zone != zone:
                notes.append(f"{br.tag}: protection zone {br.zone}")
                zone = br.zone
            if br.isolation:
                notes.append(f"{br.tag}: isolation point")
            if br.meter:
                notes.append(f"{br.tag}: {br.meter} meter")
            if br.test:
                notes.append(f"{br.tag}: test boundary ({br.test})")
            bus = nxt
        return notes
    # [end: trace]

    # [start: checks]
    def checks(self) -> list[str]:
        """Design checks a reviewer runs on a one-line."""
        out = []
        for br in self.branches:
            for end in (br.a, br.b):
                if end not in self.buses:
                    out.append(f"{br.tag}: bus {end} not defined")
            if br.kind == "transformer":
                hv, lv = br.rating.get("hv_kv"), br.rating.get("lv_kv")
                ends = {self.buses[e].kv for e in (br.a, br.b)
                        if e in self.buses}
                if {hv, lv} != ends:
                    out.append(f"{br.tag}: windings {hv}/{lv} kV do not match"
                               f" buses {sorted(ends)}")
            elif (br.kind != "inverter" and br.a in self.buses
                  and br.b in self.buses):
                if self.buses[br.a].kv != self.buses[br.b].kv:
                    out.append(f"{br.tag}: {br.kind} joins two voltages")
            if not br.zone:
                out.append(f"{br.tag}: in no protection zone")
            a_own = self.buses.get(br.a, Bus("", 0)).owner
            b_own = self.buses.get(br.b, Bus("", 0)).owner
            if a_own != b_own and not br.isolation:
                out.append(f"{br.tag}: owner boundary without isolation point")
        return out
    # [end: checks]

    def schedule(self, kinds=None) -> list[tuple]:
        """(tag, kind, owner, rating text, open items) per branch."""
        rows = []
        for br in self.branches:
            if kinds and br.kind not in kinds:
                continue
            txt = ", ".join(f"{k} {v}" for k, v in br.rating.items())
            rows.append((br.tag, br.kind, br.owner, txt, br.open_items()))
        return rows
