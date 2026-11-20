"""Quantities that carry their units, and dimension checks (chapter 2; reused in chapter 5).

    from plantp.units import Q, DimensionError, kelvin
    p = Q(60, "MW")
    e = (p * Q(8760, "h")).to("GWh")      # 525.6 GWh
    Q(5, "m/s").to("km/h")                # 18 km/h
    Q(1, "MW") + Q(1, "MWh")              # raises DimensionError
    kelvin(16.78)                         # 289.93 (temperatures go through kelvin())

A quantity is stored as one number (or numpy array) in coherent SI units plus a
dimension: the exponents of the seven SI base quantities, in the order
length, mass, time, electric current, temperature, amount of substance,
luminous intensity. Two quantities can be added only if their dimensions are
equal; any two can be multiplied. This is the "dimension guard" of chapter 2.

Unit strings: factors separated by spaces, "*" or "."; everything after the
first "/" is in the denominator; integer exponents as "m2", "m^2" or "m**2"
(negative allowed: "s^-1"; a square root is taken with ** 0.5). SI prefixes from
quecto to quetta. "kWh" is k + Wh. Degrees Celsius are refused on purpose: an
absolute temperature in degC cannot be multiplied or divided meaningfully; use
kelvin() for temperatures and "K" for temperature differences.

Educational code: clear rather than fast, and not a replacement for a full
units library.
"""
from __future__ import annotations

import math
import re
from fractions import Fraction

import numpy as np

BASE_SYMBOLS = ("m", "kg", "s", "A", "K", "mol", "cd")
DIM_NAMES = ("L", "M", "T", "I", "Theta", "N", "J")


class DimensionError(ValueError):
    """Raised when quantities of different dimensions are added, compared or converted."""


class UnitError(ValueError):
    """Raised when a unit string cannot be read."""


def _d(L=0, M=0, T=0, I=0, Th=0, N=0, J=0):
    return tuple(Fraction(x) for x in (L, M, T, I, Th, N, J))


NONE = _d()

# symbol: (factor to coherent SI, dimension, may take a prefix)
UNITS: dict[str, tuple[float, tuple, bool]] = {
    # SI base units (the kilogram takes its prefixes on "g")
    "m": (1.0, _d(L=1), True),
    "g": (1e-3, _d(M=1), True),
    "s": (1.0, _d(T=1), True),
    "A": (1.0, _d(I=1), True),
    "K": (1.0, _d(Th=1), True),
    "mol": (1.0, _d(N=1), True),
    "cd": (1.0, _d(J=1), True),
    # derived units with special names
    "rad": (1.0, NONE, True),
    "sr": (1.0, NONE, True),
    "Hz": (1.0, _d(T=-1), True),
    "N": (1.0, _d(L=1, M=1, T=-2), True),
    "Pa": (1.0, _d(L=-1, M=1, T=-2), True),
    "J": (1.0, _d(L=2, M=1, T=-2), True),
    "W": (1.0, _d(L=2, M=1, T=-3), True),
    "C": (1.0, _d(T=1, I=1), True),
    "V": (1.0, _d(L=2, M=1, T=-3, I=-1), True),
    "F": (1.0, _d(L=-2, M=-1, T=4, I=2), True),
    "ohm": (1.0, _d(L=2, M=1, T=-3, I=-2), True),
    "Ω": (1.0, _d(L=2, M=1, T=-3, I=-2), True),
    "S": (1.0, _d(L=-2, M=-1, T=3, I=2), True),
    "Wb": (1.0, _d(L=2, M=1, T=-2, I=-1), True),
    "T": (1.0, _d(M=1, T=-2, I=-1), True),
    "H": (1.0, _d(L=2, M=1, T=-2, I=-2), True),
    "lm": (1.0, _d(J=1), True),
    "lx": (1.0, _d(L=-2, J=1), True),
    # names used for power in AC work: same dimension as W (chapter 7 explains why
    # they are kept apart in practice). "Wp" is W at standard test conditions.
    "VA": (1.0, _d(L=2, M=1, T=-3), True),
    "var": (1.0, _d(L=2, M=1, T=-3), True),
    "Wp": (1.0, _d(L=2, M=1, T=-3), True),
    "Wh": (3600.0, _d(L=2, M=1, T=-2), True),
    "VAh": (3600.0, _d(L=2, M=1, T=-2), True),
    "varh": (3600.0, _d(L=2, M=1, T=-2), True),
    "Ah": (3600.0, _d(T=1, I=1), True),
    # non-SI units accepted for use with the SI
    "min": (60.0, _d(T=1), False),
    "h": (3600.0, _d(T=1), False),
    "d": (86400.0, _d(T=1), False),
    "deg": (math.pi / 180.0, NONE, False),
    "°": (math.pi / 180.0, NONE, False),
    "ha": (1e4, _d(L=2), False),
    "L": (1e-3, _d(L=3), True),
    "t": (1e3, _d(M=1), True),
    "bar": (1e5, _d(L=-1, M=1, T=-2), True),
    "eV": (1.602176634e-19, _d(L=2, M=1, T=-2), True),
    "%": (0.01, NONE, False),
    "ppm": (1e-6, NONE, False),
    # units outside the SI that still appear in data sheets and old reports
    "ft": (0.3048, _d(L=1), False),
    "in": (0.0254, _d(L=1), False),
    "mi": (1609.344, _d(L=1), False),
    "nmi": (1852.0, _d(L=1), False),
    "kn": (1852.0 / 3600.0, _d(L=1, T=-1), False),
    "mph": (1609.344 / 3600.0, _d(L=1, T=-1), False),
    "lb": (0.45359237, _d(M=1), False),
    "lbf": (4.4482216152605, _d(L=1, M=1, T=-2), False),
    "psi": (6894.757293168361, _d(L=-1, M=1, T=-2), False),
    "cal": (4.184, _d(L=2, M=1, T=-2), True),
    "Btu": (1055.05585262, _d(L=2, M=1, T=-2), False),
    "toe": (41.868e9, _d(L=2, M=1, T=-2), False),
}

PREFIXES = {
    "q": 1e-30, "r": 1e-27, "y": 1e-24, "z": 1e-21, "a": 1e-18, "f": 1e-15,
    "p": 1e-12, "n": 1e-9, "u": 1e-6, "µ": 1e-6, "μ": 1e-6, "m": 1e-3, "c": 1e-2,
    "d": 1e-1, "da": 1e1, "h": 1e2, "k": 1e3, "M": 1e6, "G": 1e9, "T": 1e12,
    "P": 1e15, "E": 1e18, "Z": 1e21, "Y": 1e24, "R": 1e27, "Q": 1e30,
}

_FACTOR = re.compile(r"^([A-Za-zΩµμ°%]+)\^?(-?\d+)?$")


def _symbol(sym: str) -> tuple[float, tuple]:
    if sym in ("degC", "°C", "℃", "degF", "°F"):
        raise UnitError(f"{sym!r}: degrees Celsius/Fahrenheit are an offset scale; "
                        "use kelvin() for a temperature and 'K' for a difference")
    if sym in UNITS:
        factor, dim, _ = UNITS[sym]
        return factor, dim
    for plen in (2, 1):                       # "da" before "d"
        prefix, rest = sym[:plen], sym[plen:]
        if prefix in PREFIXES and rest in UNITS and UNITS[rest][2]:
            if rest == "g" or prefix + rest not in UNITS:
                factor, dim, _ = UNITS[rest]
                return PREFIXES[prefix] * factor, dim
    raise UnitError(f"unknown unit symbol {sym!r}")


def parse_unit(text: str) -> tuple[float, tuple]:
    """Return (factor to coherent SI, dimension) of a unit string such as 'kWh/m2'."""
    if text is None:
        raise UnitError("unit is missing")
    text = text.strip().replace("**", "^")
    if text in ("", "1", "-"):
        return 1.0, NONE
    factor = 1.0
    dim = [Fraction(0)] * 7
    for side, part in enumerate(text.split("/")):
        sign = 1 if side == 0 else -1
        for token in re.split(r"[\s*·.]+", part.strip()):
            if token in ("", "1"):
                continue
            match = _FACTOR.match(token)
            if not match:
                raise UnitError(f"cannot read {token!r} in unit {text!r}")
            f, d = _symbol(match.group(1))
            exp = Fraction(match.group(2)) if match.group(2) else Fraction(1)
            factor *= f ** float(sign * exp)
            for i in range(7):
                dim[i] += sign * exp * d[i]
    return factor, tuple(dim)


def dimension_string(dim: tuple) -> str:
    """'L^2 M T^-3' style text of a dimension; '1' for a dimensionless quantity."""
    parts = []
    for name, exp in zip(DIM_NAMES, dim):
        if exp == 0:
            continue
        parts.append(name if exp == 1 else f"{name}^{exp}")
    return " ".join(parts) or "1"


def si_unit_string(dim: tuple) -> str:
    """Coherent SI unit made of base units, e.g. 'm^2 kg s^-3' for watt."""
    parts = []
    for sym, exp in zip(BASE_SYMBOLS, dim):
        if exp == 0:
            continue
        parts.append(sym if exp == 1 else f"{sym}^{exp}")
    return " ".join(parts) or "1"


class Quantity:
    """A number (or numpy array) with a unit. Q is a short alias."""

    __array_priority__ = 1000                # numpy arrays defer to Quantity

    def __init__(self, value, unit: str = ""):
        factor, dim = parse_unit(unit)
        self.si = np.asarray(value, dtype=float) * factor if np.ndim(value) else float(value) * factor
        self.dim = dim
        self.unit = unit.strip()

    @classmethod
    def _from_si(cls, si, dim, unit=None):
        q = cls.__new__(cls)
        q.si, q.dim = si, dim
        q.unit = unit if unit is not None else si_unit_string(dim)
        return q

    # ---- reading the value ---------------------------------------------------------
    @property
    def value(self):
        """The number expressed in this quantity's own unit."""
        factor, _ = parse_unit(self.unit) if self.unit != si_unit_string(self.dim) else (1.0, None)
        return self.si / factor

    def to(self, unit: str) -> "Quantity":
        """The same quantity expressed in another unit of the same dimension."""
        factor, dim = parse_unit(unit)
        if dim != self.dim:
            raise DimensionError(f"cannot convert {self.unit or '1'} "
                                 f"[{dimension_string(self.dim)}] to {unit} "
                                 f"[{dimension_string(dim)}]")
        return Quantity._from_si(self.si, dim, unit.strip())

    def magnitude(self, unit: str):
        """The bare number in the given unit: Q(1, 'km').magnitude('m') -> 1000.0"""
        return self.to(unit).value

    @property
    def dimensionless(self) -> bool:
        return self.dim == NONE

    def dimension(self) -> str:
        return dimension_string(self.dim)

    # ---- arithmetic ------------------------------------------------------------------
    def _coerce(self, other) -> "Quantity":
        if isinstance(other, Quantity):
            return other
        return Quantity._from_si(np.asarray(other, dtype=float) if np.ndim(other) else float(other),
                                 NONE, "")

    def _same(self, other, op: str) -> "Quantity":
        other = self._coerce(other)
        if other.dim != self.dim:
            raise DimensionError(f"cannot {op} {self.unit or '1'} [{dimension_string(self.dim)}] "
                                 f"and {other.unit or '1'} [{dimension_string(other.dim)}]")
        return other

    def __add__(self, other):
        other = self._same(other, "add")
        return Quantity._from_si(self.si + other.si, self.dim, self.unit)

    __radd__ = __add__

    def __sub__(self, other):
        other = self._same(other, "subtract")
        return Quantity._from_si(self.si - other.si, self.dim, self.unit)

    def __rsub__(self, other):
        other = self._same(other, "subtract")
        return Quantity._from_si(other.si - self.si, self.dim, self.unit)

    def __neg__(self):
        return Quantity._from_si(-self.si, self.dim, self.unit)

    @staticmethod
    def _join(a: str, b: str, op: str) -> str | None:
        if not a and not b:
            return ""
        if not b:
            return a
        if not a:
            return b if op == "*" else None
        if op == "*":
            return f"{a} {b}" if "/" not in a and "/" not in b else None
        return f"{a}/{b}" if "/" not in a and "/" not in b and " " not in b else None

    def __mul__(self, other):
        other = self._coerce(other)
        dim = tuple(x + y for x, y in zip(self.dim, other.dim))
        return Quantity._from_si(self.si * other.si, dim, self._join(self.unit, other.unit, "*"))

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = self._coerce(other)
        dim = tuple(x - y for x, y in zip(self.dim, other.dim))
        return Quantity._from_si(self.si / other.si, dim, self._join(self.unit, other.unit, "/"))

    def __rtruediv__(self, other):
        return self._coerce(other) / self

    def __pow__(self, exponent):
        exp = Fraction(exponent).limit_denominator(12)
        dim = tuple(x * exp for x in self.dim)
        return Quantity._from_si(self.si ** float(exp), dim, None)

    def sqrt(self):
        return self ** Fraction(1, 2)

    # ---- comparison ------------------------------------------------------------------
    def __eq__(self, other):
        other = self._same(other, "compare")
        return np.isclose(self.si, other.si, rtol=1e-12, atol=0.0)

    def __lt__(self, other):
        return self.si < self._same(other, "compare").si

    def __le__(self, other):
        return self.si <= self._same(other, "compare").si

    def __gt__(self, other):
        return self.si > self._same(other, "compare").si

    def __ge__(self, other):
        return self.si >= self._same(other, "compare").si

    def __float__(self):
        if not self.dimensionless:
            raise DimensionError(f"{self.unit} [{self.dimension()}] is not dimensionless; "
                                 "use .magnitude(unit) to get a bare number")
        return float(self.si)

    def __len__(self):
        return len(self.si)

    def __getitem__(self, item):
        return Quantity._from_si(self.si[item], self.dim, self.unit)

    def sum(self):
        return Quantity._from_si(np.sum(self.si), self.dim, self.unit)

    def mean(self):
        return Quantity._from_si(np.mean(self.si), self.dim, self.unit)

    def __format__(self, spec: str) -> str:
        if np.ndim(self.si):
            return f"{np.array2string(np.asarray(self.value), precision=4)} {self.unit}".strip()
        return f"{format(self.value, spec or 'g')} {self.unit}".strip()

    def __repr__(self) -> str:
        return f"Q({self.value!r}, {self.unit!r})"

    def __str__(self) -> str:
        return format(self, "")


Q = Quantity


def check(quantity: Quantity, unit: str) -> Quantity:
    """Dimension guard: return the quantity if it has the dimension of `unit`,
    otherwise raise DimensionError naming both dimensions."""
    if not isinstance(quantity, Quantity):
        raise DimensionError(f"expected a quantity in {unit}, got a bare number {quantity!r}")
    _, dim = parse_unit(unit)
    if quantity.dim != dim:
        raise DimensionError(f"expected [{dimension_string(dim)}] ({unit}), "
                             f"got [{quantity.dimension()}] ({quantity.unit})")
    return quantity


def convert(value, from_unit: str, to_unit: str):
    """Bare-number conversion: convert(36, 'km/h', 'm/s') -> 10.0"""
    return Quantity(value, from_unit).magnitude(to_unit)


def kelvin(t_celsius):
    """Absolute temperature in kelvin from degrees Celsius (raises below absolute zero)."""
    t = np.asarray(t_celsius, dtype=float) + 273.15
    if np.any(t < 0):
        raise ValueError("temperature below absolute zero")
    return t if np.ndim(t_celsius) else float(t)


def round_sig(x: float, digits: int) -> float:
    """Round to a number of significant figures: round_sig(289812.4, 3) -> 290000.0"""
    if digits < 1:
        raise ValueError("at least one significant figure")
    if x == 0 or not math.isfinite(x):
        return x
    return round(x, digits - 1 - int(math.floor(math.log10(abs(x)))))


def format_sig(x: float, digits: int) -> str:
    """Text with exactly `digits` significant figures, trailing zeros kept:
    format_sig(0.0500, 3) -> '0.0500'; format_sig(289812, 3) -> '290000'"""
    if x == 0:
        return "0" if digits == 1 else "0." + "0" * (digits - 1)
    exponent = int(math.floor(math.log10(abs(round_sig(x, digits)))))
    decimals = max(digits - 1 - exponent, 0)
    return f"{round_sig(x, digits):.{decimals}f}"
