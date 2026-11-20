"""Cable, connector, switchgear and panel manufacture checks (chapter 46):
conductor resistance corrected to 20 C, a cable-schedule validator,
an interlock state machine explored for forbidden states, a point-to-
point check of a wiring list, terminal-plan consistency, pole-timing and
contact-resistance checks.

Teaching relations. Nothing here is a test procedure or a test value
for live equipment; limits come from the makers and the standards.
"""
from __future__ import annotations

from itertools import product


# ------------------------------------------------------------ conductor
def r_to_20(r_meas: float, theta: float, alpha: float = 0.00403) -> float:
    """Resistance measured at theta C corrected to 20 C (Al by default)."""
    return r_meas / (1 + alpha * (theta - 20.0))


# ------------------------------------------------------------ cable schedule
# [start: schedule]
REQUIRED = ["id", "from", "to", "type", "size_mm2", "length_m", "cores"]


def check_schedule(rows: list[dict], known_ends: set[str],
                   sizes: set[int]) -> list[tuple[str, str]]:
    """Return (cable id, problem) for missing fields, unit slips, unknown
    ends, duplicate ids and sizes not in the design range."""
    out, seen = [], set()
    for r in rows:
        cid = r.get("id") or "?"
        for f in REQUIRED:
            if r.get(f) in (None, ""):
                out.append((cid, f"missing {f}"))
        if cid in seen:
            out.append((cid, "duplicate id"))
        seen.add(cid)
        length = r.get("length_m")
        if isinstance(length, (int, float)) and 0 < length < 10:
            out.append((cid, "length looks like km, not m"))
        size = r.get("size_mm2")
        if isinstance(size, str):
            out.append((cid, f"size as text '{size}'"))
        elif isinstance(size, (int, float)) and size not in sizes:
            out.append((cid, f"size {size} not a design size"))
        for end in ("from", "to"):
            if r.get(end) and r[end] not in known_ends:
                out.append((cid, f"unknown {end} '{r[end]}'"))
    return out
# [end: schedule]


# ------------------------------------------------------------ interlocks
# [start: interlock]
def allowed(state: tuple[int, int, int], op: str,
            faulty: bool = False) -> bool:
    """Interlock rules of a feeder bay (CB, disconnector DS, earth switch
    ES; 1 = closed). DS moves only with CB open; ES closes only with DS
    open; DS closes only with ES open. The faulty version forgets the
    last rule (a planted error)."""
    cb, ds, es = state
    if op in ("ds_open", "ds_close") and cb:
        return False
    if op == "es_close" and ds:
        return False
    if op == "ds_close" and es and not faulty:
        return False
    return True


def apply(state, op):
    cb, ds, es = state
    return {"cb_close": (1, ds, es), "cb_open": (0, ds, es),
            "ds_close": (cb, 1, es), "ds_open": (cb, 0, es),
            "es_close": (cb, ds, 1), "es_open": (cb, ds, 0)}[op]


def reachable(start=(0, 0, 0), faulty: bool = False) -> set:
    """All states reachable from start through allowed operations."""
    ops = ["cb_close", "cb_open", "ds_close", "ds_open", "es_close", "es_open"]
    seen, todo = {start}, [start]
    while todo:
        s = todo.pop()
        for op in ops:
            if allowed(s, op, faulty):
                n = apply(s, op)
                if n not in seen:
                    seen.add(n)
                    todo.append(n)
    return seen
# [end: interlock]


FORBIDDEN = {(cb, 1, 1) for cb in (0, 1)}          # DS and ES closed together


def all_states() -> list:
    return list(product((0, 1), repeat=3))


# ------------------------------------------------------------ wiring
def point_to_point(design: set[frozenset], measured: set[frozenset]) -> dict:
    """Compare designed connections with measured continuity."""
    return dict(missing=sorted(tuple(sorted(c)) for c in design - measured),
                extra=sorted(tuple(sorted(c)) for c in measured - design))


def terminal_check(wires: list[tuple[str, str, str]]) -> list[str]:
    """wires: (wire no, end A terminal, end B terminal). Report terminals
    used twice and wires with an empty end."""
    out, used = [], {}
    for w, a, b in wires:
        for t in (a, b):
            if not t:
                out.append(f"wire {w}: an end has no terminal")
            else:
                used.setdefault(t, []).append(w)
    for t, ws in sorted(used.items()):
        if len(ws) > 1:
            out.append(f"terminal {t} carries wires {', '.join(ws)}")
    return out


# ------------------------------------------------------------ mechanism, contacts
def pole_spread(times_ms) -> float:
    """Largest difference between the poles' operating times."""
    return max(times_ms) - min(times_ms)


# ------------------------------------------------------------ cable field
# [start: field]
def field_kv_mm(u0_kv: float, r_mm: float, rc_mm: float,
                ri_mm: float) -> float:
    """Field in a coaxial insulation at radius r (between the conductor
    screen rc and the insulation screen ri): E = U0 / (r ln(ri / rc))."""
    import math
    return u0_kv / (r_mm * math.log(ri_mm / rc_mm))
# [end: field]


# ------------------------------------------------------------ contact spots
# [start: holm]
def holm_r(force_n: float, rho_ohm_m: float, hardness_pa: float,
           spots: int = 1) -> float:
    """Constriction resistance of n equal contact spots sharing the force
    (Holm): spot radius a = sqrt(F / (n pi H)), R = rho / (2 n a)."""
    import math
    a = math.sqrt(force_n / (spots * math.pi * hardness_pa))
    return rho_ohm_m / (2 * spots * a)
# [end: holm]


# ------------------------------------------------------------ trends
def trend(x, y) -> tuple[float, float]:
    """Least-squares slope of y on x and its standard error."""
    import math
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((a - mx) ** 2 for a in x)
    b = sum((a - mx) * (c - my) for a, c in zip(x, y)) / sxx
    res = [c - my - b * (a - mx) for a, c in zip(x, y)]
    s2 = sum(e * e for e in res) / (n - 2)
    return b, math.sqrt(s2 / sxx)


# ------------------------------------------------------------ circuits
# [start: circuits]
def circuits(wires: list[tuple[str, str]]) -> list[set[str]]:
    """Group terminals joined by wires into circuits (union-find)."""
    parent: dict[str, str] = {}

    def root(t: str) -> str:
        parent.setdefault(t, t)
        while parent[t] != t:
            parent[t] = parent[parent[t]]
            t = parent[t]
        return t

    for a, b in wires:
        parent[root(a)] = root(b)
    groups: dict[str, set[str]] = {}
    for t in list(parent):
        groups.setdefault(root(t), set()).add(t)
    return sorted(groups.values(), key=lambda g: sorted(g)[0])
# [end: circuits]
