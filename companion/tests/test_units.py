"""Tests of plantp.units against hand calculations (chapter 2)."""
import math

import numpy as np
import pytest

from plantp.units import (Q, DimensionError, UnitError, check, convert, dimension_string,
                          format_sig, kelvin, parse_unit, round_sig)


def test_energy_from_power_and_time():
    e = (Q(60, "MW") * Q(8760, "h")).to("GWh")
    assert e.value == pytest.approx(525.6)


def test_speed_conversions():
    assert Q(5, "m/s").magnitude("km/h") == pytest.approx(18.0)
    assert convert(36, "km/h", "m/s") == pytest.approx(10.0)
    assert convert(10, "kn", "m/s") == pytest.approx(5.144444, rel=1e-6)


def test_prefixes_and_powers_of_prefixed_units():
    assert parse_unit("mm2")[0] == pytest.approx(1e-6)        # (mm)^2, not m(m^2)
    assert parse_unit("km^2")[0] == pytest.approx(1e6)
    assert parse_unit("kg")[0] == pytest.approx(1.0)
    assert parse_unit("hPa")[0] == pytest.approx(100.0)
    assert parse_unit("MWh")[0] == pytest.approx(3.6e9)
    assert parse_unit("m**3")[0] == pytest.approx(1.0)


def test_ambiguous_symbols_resolve_to_the_unit_not_a_prefix():
    assert parse_unit("min")[0] == 60.0                       # minute, not milli-inch
    assert parse_unit("cd")[1] == parse_unit("cd")[1]
    assert dimension_string(parse_unit("cd")[1]) == "J"       # candela, not centi-day
    assert dimension_string(parse_unit("Pa")[1]) == "L^-1 M T^-2"
    assert parse_unit("h")[0] == 3600.0                       # hour, not hecto
    assert parse_unit("T")[0] == 1.0                          # tesla
    assert parse_unit("TWh")[0] == pytest.approx(3.6e15)      # tera + Wh


def test_watt_is_kg_m2_per_s3():
    assert dimension_string(parse_unit("W")[1]) == "L^2 M T^-3"
    assert parse_unit("J/s")[1] == parse_unit("W")[1]
    assert parse_unit("V A")[1] == parse_unit("W")[1]
    assert parse_unit("N m/s")[1] == parse_unit("W")[1]


def test_adding_power_and_energy_is_refused():
    with pytest.raises(DimensionError):
        Q(1, "MW") + Q(1, "MWh")
    with pytest.raises(DimensionError):
        Q(1, "MW").to("MWh")


def test_bare_number_cannot_be_added_to_a_quantity():
    with pytest.raises(DimensionError):
        Q(3, "m") + 2


def test_wind_power_formula_is_dimensionally_a_power():
    p = 0.5 * Q(1.225, "kg/m3") * Q(17671.46, "m2") * Q(10, "m/s") ** 3
    check(p, "W")
    assert p.magnitude("MW") == pytest.approx(10.8238, rel=1e-4)


def test_check_reports_a_wrong_dimension():
    with pytest.raises(DimensionError, match="expected"):
        check(Q(5, "kWh"), "kW")
    with pytest.raises(DimensionError):
        check(5.0, "kW")


def test_percent_and_degree_are_dimensionless():
    assert float(Q(12, "%")) == pytest.approx(0.12)
    assert float(Q(180, "deg")) == pytest.approx(math.pi)


def test_celsius_is_refused_and_kelvin_works():
    with pytest.raises(UnitError):
        Q(25, "degC")
    assert kelvin(16.78) == pytest.approx(289.93)
    with pytest.raises(ValueError):
        kelvin(-300)


def test_ideal_gas_density_at_plant_p():
    rho = Q(877.67, "hPa") / (Q(287.05, "J/kg/K") * Q(kelvin(16.78), "K"))
    assert rho.magnitude("kg/m3") == pytest.approx(1.0546, rel=1e-4)


def test_arrays_carry_units():
    p = Q(np.array([10.0, 20.0, 30.0]), "MW")
    e = (p * Q(1, "h")).sum().to("MWh")
    assert e.value == pytest.approx(60.0)


def test_unknown_unit_and_bad_token():
    with pytest.raises(UnitError):
        parse_unit("furlong")
    with pytest.raises(UnitError):
        parse_unit("m^x")


def test_non_si_energy_units():
    assert convert(1, "toe", "MWh") == pytest.approx(11.63, rel=1e-4)
    assert convert(1, "kcal", "kJ") == pytest.approx(4.184)


def test_round_sig_and_format_sig():
    assert round_sig(289812.4371, 3) == 290000.0
    assert round_sig(0.0012345, 2) == pytest.approx(0.0012)
    assert format_sig(0.05, 3) == "0.0500"
    assert format_sig(9.996, 3) == "10.0"
    assert format_sig(289812, 4) == "289800"
    with pytest.raises(ValueError):
        round_sig(1.0, 0)
