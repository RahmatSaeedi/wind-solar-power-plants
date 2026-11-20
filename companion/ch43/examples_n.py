"""Chapter 43, an eleventh round: the hot-spot factor read from fibre-optic
sensors in the heat run, the tested losses fed back to the energy model,
and the weighed shipping mass against the estimate and the road limit.

Run from the project root:   python -m companion.ch43.examples_n
Writes companion/ch43/expected/n_*.txt.
Teaching values (A-462, A-464).
"""
from __future__ import annotations

from companion.ch43 import sources as src
from companion.ch43.common import emit

M, T = src.MAIN_B, src.TESTS


# ------------------------------------------------ hot-spot factor from sensors
def hotspot_factor(sensor_c=(98.0, 103.5, 101.2, 96.4)) -> dict[str, float]:
    top = T["ambient_c"] + T["top_oil_rise"]
    grad = 66.5 - T["oil_avg_rise"]
    hs = max(sensor_c)
    h = (hs - top) / grad
    lines = ["fibre-optic sensors in the HV winding during the heat run",
             "  readings C: " + ", ".join(f"{x:.1f}" for x in sensor_c),
             f"  top oil {top:.0f} C; winding gradient {grad:.1f} K (lesson C)",
             f"  hot-spot factor H = ({hs:.1f} - {top:.0f}) / {grad:.1f} = {h:.2f}",
             "  the loading guide's hot spot is top oil + H x gradient; a",
             "  measured H replaces the assumed one (ch 25) in every later",
             "  thermal calculation - the sensors' positions come from the",
             "  maker's thermal design, where the hottest disc is expected"]
    emit("n_hotspot", lines)
    return dict(h=h, hs=hs, top=top, grad=grad)


# ------------------------------------------------ tested losses to the energy model
def energy_model(llf: float = 0.128) -> dict[str, float]:
    dp0, dpk = 42.2 - M["p0_kw"], 298.0 - M["pk_kw"]
    mwh = (dp0 * 8760 + dpk * llf * 8760) / 1000
    lines = ["T1's tested losses against the guarantees in the energy model",
             f"  no-load +{dp0:.1f} kW all year; load +{dpk:.1f} kW at loss load "
             f"factor {llf}",
             f"  extra loss {mwh:.1f} MWh a year for this unit",
             "  about ten MWh against 295 GWh (ch 15): negligible for the",
             "  yield, but the model uses the tested values from now on -",
             "  a plant change is announced to the model's owner (ch 37)"]
    emit("n_energy", lines)
    return dict(mwh=mwh)


# ------------------------------------------------ weighed shipping mass
def weighed(active_t: float = 45.1, tank_t: float = 15.6, bracing_t: float = 2.0):
    ship = active_t + tank_t + bracing_t
    est = 62.0
    lines = ["weighed at the factory before shipment (report values)",
             f"  active part {active_t} t, tank {tank_t} t, bracing {bracing_t} t: "
             f"{ship:.1f} t",
             f"  estimate of lesson B {est:.0f} t; road limit {M['transport_t']:.0f} t: "
             f"margin {M['transport_t'] - ship:.1f} t",
             "  the weighed figure, not the estimate, goes to the route",
             "  plan and the crane plan (ch 31) - with the centre of",
             "  gravity marked on the tank"]
    emit("n_weighed", lines)
    return dict(ship=ship, margin=M["transport_t"] - ship)


if __name__ == "__main__":
    hotspot_factor()
    energy_model()
    weighed()
