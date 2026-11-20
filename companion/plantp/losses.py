"""Cable and transformer loss calculator, chapter 5 (refined in 24, 25, 15).

    cable_loss_mw        three-phase I^2 R, resistance at conductor temperature
    transformer_loss_mw  no-load loss plus load loss scaled by (S / S_rated)^2
    annual_losses        hourly series in, energy and percentages out

Teaching model: resistance at a stated conductor temperature, balanced
phases, no harmonics; the formal calculation follows the rating methods of
chapters 24 and 25.
"""
from __future__ import annotations

import math

import numpy as np


def current_a(p_mw, v_kv: float, pf: float):
    """Line current (A) of a balanced three-phase circuit."""
    p = np.asarray(p_mw, dtype=float)
    return p * 1e6 / (math.sqrt(3) * v_kv * 1e3 * pf)


def cable_loss_mw(p_mw, v_kv: float, pf: float, r20_ohm_per_km: float,
                  length_km: float, alpha: float = 0.00403,
                  t_c: float = 70.0):
    """3 I^2 R with R = R20 L (1 + alpha (T - 20)); result in MW."""
    r = r20_ohm_per_km * length_km * (1 + alpha * (t_c - 20.0))
    return 3 * current_a(p_mw, v_kv, pf) ** 2 * r / 1e6


def transformer_loss_mw(p_mw, pf: float, s_rated_mva: float,
                        p0_mw: float, pk_mw: float):
    """P0 + Pk (S / S_rated)^2 with S = P / pf; result in MW."""
    s = np.asarray(p_mw, dtype=float) / pf
    return p0_mw + pk_mw * (s / s_rated_mva) ** 2


def annual_losses(p_mw, cable_mw, trafo_mw) -> dict:
    """Energies (MWh for hourly series) and losses as percent of energy."""
    p, c, t = (np.asarray(x, dtype=float) for x in (p_mw, cable_mw, trafo_mw))
    e = p.sum()
    return {"energy_mwh": float(e), "cable_mwh": float(c.sum()),
            "trafo_mwh": float(t.sum()),
            "cable_pct": float(100 * c.sum() / e),
            "trafo_pct": float(100 * t.sum() / e)}
