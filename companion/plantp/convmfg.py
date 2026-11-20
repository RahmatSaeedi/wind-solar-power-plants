"""Converter manufacture and test arithmetic (chapter 44): the thermal
stack with its interface layer, current sharing of parts with spread,
solder-joint fatigue, defect escape through an inspection line, a
configuration fingerprint, a stress-derating check, and an educational,
non-deployable simulation of a converter's start-up state machine.

Teaching relations. Nothing here is firmware or a control procedure;
real limits come from the parts' makers and the converter's maker.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field


# ------------------------------------------------------------ thermal stack
def tim_r(thickness_um: float, k_w_mk: float, area_cm2: float,
          void: float = 0.0) -> float:
    """Thermal resistance (K/W) of an interface layer; voids remove area."""
    a = area_cm2 * 1e-4 * (1.0 - void)
    return thickness_um * 1e-6 / (k_w_mk * a)


def tj(p_w: float, r_jc: float, r_tim: float, r_hs: float, t_cool: float) -> float:
    """Junction temperature through a series stack to the coolant."""
    return t_cool + p_w * (r_jc + r_tim + r_hs)


# ------------------------------------------------------------ sharing
def shares(values) -> list[float]:
    """Share of a common current taken by parallel branches of
    resistance-like values (r or ESR): proportional to 1/value."""
    inv = [1.0 / v for v in values]
    s = sum(inv)
    return [x / s for x in inv]


# ------------------------------------------------------------ solder fatigue
# [start: solder]
def solder_strain(length_mm: float, d_alpha_ppm: float, delta_t: float,
                  height_mm: float) -> float:
    """Shear strain range of a solder joint between a part and its board:
    distance from the neutral point x CTE mismatch x temperature swing,
    over the joint height."""
    return length_mm * d_alpha_ppm * 1e-6 * delta_t / height_mm


def cycles_to_failure(strain: float, eps_f: float = 0.325, c: float = -0.442):
    """Coffin-Manson in a simplified Engelmaier form (teaching constants):
    N_f = 0.5 (strain / (2 eps_f))^(1/c)."""
    return 0.5 * (strain / (2 * eps_f)) ** (1 / c)
# [end: solder]


# ------------------------------------------------------------ inspection line
def escapes(defects_ppm: dict, detect: dict) -> dict:
    """Defects per million boards left after a line of inspections: each
    station finds a share of each defect type (independent stations)."""
    out = {}
    for kind, ppm in defects_ppm.items():
        left = ppm
        for station, finds in detect.items():
            left *= 1 - finds.get(kind, 0.0)
        out[kind] = left
    return out


# ------------------------------------------------------------ configuration
def fingerprint(config: dict) -> str:
    """SHA-256 of a parameter set in a canonical text form: the same
    settings always give the same 16-character fingerprint."""
    text = json.dumps(config, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode()).hexdigest()[:16]


# ------------------------------------------------------------ derating
def derating(rows, rules: dict) -> list[tuple[str, float, float, bool]]:
    """(part, stress ratio, allowed ratio, ok) for each part: stress over
    rating against the derating rule of its kind."""
    out = []
    for part, kind, stress, rating in rows:
        ratio = stress / rating
        allowed = rules[kind]
        out.append((part, ratio, allowed, ratio <= allowed))
    return out


# ------------------------------------------------------------ state machine
# [start: sm]
@dataclass
class ConverterSim:
    """Educational start-up sequence of a grid inverter (not firmware).
    States: OFF, PRECHARGE, READY, SYNC, RUN, FAULT. Faults latch until
    a reset in a safe state; every transition is logged."""
    state: str = "OFF"
    log: list = field(default_factory=list)
    v_dc: float = 0.0
    t_pre: float = 0.0
    fault: str = ""
    PRECHARGE_MAX_S = 10.0
    VDC_MIN, VDC_MAX = 850.0, 1300.0

    def _go(self, new: str, why: str) -> str:
        self.log.append((self.state, new, why))
        self.state = new
        return new

    def event(self, ev: str, **kw) -> str:
        if ev == "fault":
            self.fault = kw.get("kind", "unknown")
            return self._go("FAULT", self.fault)
        if self.state == "FAULT":
            if ev == "reset" and kw.get("cause_cleared", False):
                self.fault = ""
                return self._go("OFF", "reset")
            return self.state
        if ev == "stop":
            return self._go("OFF", "stop")
        if ev == "tick" and self.state != "OFF":
            self.v_dc = kw.get("v_dc", self.v_dc)
            if self.v_dc > self.VDC_MAX:
                return self.event("fault", kind="DC overvoltage")
        if self.state == "OFF" and ev == "start":
            self.t_pre = 0.0
            return self._go("PRECHARGE", "start")
        if self.state == "PRECHARGE" and ev == "tick":
            self.t_pre += kw.get("dt", 1.0)
            if self.v_dc >= self.VDC_MIN:
                return self._go("READY", "DC link charged")
            if self.t_pre > self.PRECHARGE_MAX_S:
                return self.event("fault", kind="precharge timeout")
            return self.state
        if self.state == "READY" and ev == "grid_ok":
            return self._go("SYNC", "grid present")
        if self.state == "SYNC" and ev == "synced":
            return self._go("RUN", "in phase")
        if self.state == "RUN" and ev == "grid_lost":
            return self.event("fault", kind="grid lost")
        return self.state
# [end: sm]
