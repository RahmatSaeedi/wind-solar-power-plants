"""Chapter 15 - the Plant P hourly energy model (model version 15.1): every
step of the wind and PV chains as hourly series (MW), built from the
data-pack year and the bases of chapters 10-14, plus a synthetic archive
of day-ahead forecasts for the forecast labs.

Model settings (ModelConfig) are versioned: every output names the
version and the settings it used. Bases: D-013/D-014 PV array and
cleaning, D-015/D-018 wake model and layout W2b, D-016/D-017 long-term
resource and hub density; teaching values A-267 .. A-276.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache

import numpy as np

from companion.ch15 import common  # noqa: F401  (puts plantp on the path)
from companion.ch10 import pvyear10
from companion.ch10.integrated import EFF_POINTS
from companion.ch11 import lab_d as l11
from companion.ch13 import sources as s13
from companion.ch14 import examples_b as eb, lab_d as l14
from plantp import datapack, pe, wind as w, yieldmodel as ym

VERSION = "15.1"


# [start: config]
@dataclass(frozen=True)
class ModelConfig:
    """Settings of the energy model; change one, change the version."""
    lt_wind: float = 191.87 / 186.69        # D-017 long-term energy factor
    lt_pv: float = 0.988                    # D-016 long-term PV energy factor
    av_wind: float = 0.981                  # energy-based availability (ch 11)
    av_pv: float = 0.990                    # (A-275)
    soiling: float = 0.0143                 # D-014 truck at 4 % trigger
    shading: float = 0.0007                 # ch 10 row shading
    degr_y1: float = 0.005                  # first-year PV degradation (A-275)
    noload_mw: float = 0.10                 # transformers' no-load losses
    loadloss: float = 0.015                 # load losses at 100 MW, ~P^2
    aux_pv: float = 0.003                   # PV own use, share of output
    aux_wind_mw: float = 12 * 168.2 / 8760  # ch 11, mean own use of 12 WTGs
    export_mw: float = 100.0
    grid_outage_h: int = 12                 # grid-outage hours a year (A-275)
    seed: int = 151
# [end: config]


def settings_line(cfg: ModelConfig) -> str:
    d = asdict(cfg)
    return "model " + VERSION + ": " + ", ".join(f"{k}={v:.4g}" if isinstance(v, float)
                                                 else f"{k}={v}" for k, v in d.items())


@lru_cache(maxsize=1)
def wind_tables():
    """Farm power (MW) of layout W2b for each (2-degree direction bin, 0.5 m/s
    density-equivalent speed bin): free stream on flat ground, with the
    terrain speed-up, and with speed-up and wakes."""
    xy = l14.layouts()["W2b plain, adjusted"]
    s = eb.speedups(xy)
    vg, _, _, ctg = l11.rotor.curve_arrays()
    flat, terr, wake = {}, {}, {}
    for (a, b) in eb.wind_table():
        v = 0.5 * b
        flat[(a, b)] = 12 * float(l11.pack_power(v)) / 1e3
        terr[(a, b)] = float(l11.pack_power(v * (1 + s)).sum()) / 1e3
        if v >= 2.5:
            ct = float(np.interp(v, vg, ctg))
            vs = w.farm_speeds(xy, v, 2.0 * a + 1.0, ct, eb.D)
            wake[(a, b)] = float(l11.pack_power(vs * (1 + s)).sum()) / 1e3
        else:
            wake[(a, b)] = terr[(a, b)]
    return flat, terr, wake


@lru_cache(maxsize=1)
def hourly_inputs():
    h = datapack.load_hourly()
    v = h["ws_100m_ms"].to_numpy(float)
    wd = h["wd_100m_deg"].to_numpy(float)
    p, t = h["p_hpa"].to_numpy(float), h["t_air_c"].to_numpy(float)
    month = h.index.month.to_numpy() - 1
    return h, v, wd, p, t, month


@lru_cache(maxsize=4)
def plant_year(cfg: ModelConfig = ModelConfig()) -> dict:
    """Every step of the chain as an hourly series in MW (data year,
    long-term factors applied as named steps)."""
    h, v, wd, p, t, month = hourly_inputs()
    rng = np.random.default_rng(cfg.seed)
    # ---- wind
    w_gross = 12 * l11.pack_power(v) / 1e3                      # 1.225 kg/m3, flat
    rho = s13.hub_density(p, t)
    veq = w.density_equivalent_speed(v, rho)
    flat, terr, wake = wind_tables()
    keys = list(zip((np.floor(wd / 2.0) % 180).astype(int), np.round(veq / 0.5).astype(int)))
    w_dens = np.array([flat.get(k, 12 * float(l11.pack_power(0.5 * k[1])) / 1e3) for k in keys])
    w_terr = np.array([terr.get(k, 0.0) for k in keys])
    w_wake = np.array([wake.get(k, 0.0) for k in keys])
    w_lt = w_wake * cfg.lt_wind
    w_av = w_lt * cfg.av_wind
    # ---- PV
    c0, c1, c2 = pe.fit_loss_coeffs(EFF_POINTS)
    poa = pvyear10.poa()["poa"]
    pv_stc = 60.06 * np.asarray(poa) / 1000.0                    # MW at STC efficiency
    s = pvyear10.strings()
    pv_dc_gross = s["p_string"] * 4200 / 1e6
    pv_dc = pvyear10.dc_power() / 1e6
    x = pv_dc / 50.0
    y = ym.ac_from_dc(x, (c0, c1, c2))
    pv_inv = y * 50.0
    pv_clip = np.minimum(pv_inv, 50.0 * 0.98)
    pv_soil = pv_clip * (1 - cfg.soiling) * (1 - cfg.shading)
    pv_lt = pv_soil * cfg.lt_pv
    pv_deg = pv_lt * (1 - cfg.degr_y1)
    pv_av = pv_deg * cfg.av_pv
    # ---- plant
    mv = w_av + pv_av
    loss = cfg.noload_mw + cfg.loadloss * cfg.export_mw * (mv / cfg.export_mw) ** 2
    after_el = mv - loss
    aux = cfg.aux_wind_mw + cfg.aux_pv * pv_av
    poc = after_el - aux
    delivered, curtailed = np.minimum(poc, cfg.export_mw), np.clip(poc - cfg.export_mw, 0, None)
    outage = np.zeros(8760, bool)
    outage[rng.choice(8760, cfg.grid_outage_h, replace=False)] = True
    net = np.where(outage, np.minimum(delivered, 0.0), delivered)
    return {"month": month, "w_gross": w_gross, "w_dens": w_dens, "w_terr": w_terr,
            "w_wake": w_wake, "w_lt": w_lt, "w_av": w_av, "pv_stc": pv_stc,
            "pv_dc_gross": pv_dc_gross, "pv_dc": pv_dc, "pv_inv": pv_inv,
            "pv_clip": pv_clip, "pv_soil": pv_soil, "pv_lt": pv_lt, "pv_deg": pv_deg,
            "pv_av": pv_av, "mv": mv, "el_loss": loss, "after_el": after_el, "aux": aux,
            "poc": poc, "delivered": delivered, "curtailed": curtailed, "outage": outage,
            "net": net}
