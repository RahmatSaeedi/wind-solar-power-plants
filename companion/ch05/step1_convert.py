"""Step 1 of the construction sequence: a command-line unit converter.

    python -m companion.ch05.step1_convert 46.8 km/h m/s
    python -m companion.ch05.step1_convert 25 degC K

Exit code 0 on success and 2 on a usage or unit error (argparse uses 2 too).
"""
from __future__ import annotations

import argparse
import sys

# [start: table]
# each unit: (dimension, factor to the SI unit of that dimension)
UNITS = {
    "m/s": ("speed", 1.0), "km/h": ("speed", 1 / 3.6),
    "knot": ("speed", 1852 / 3600),
    "W": ("power", 1.0), "kW": ("power", 1e3), "MW": ("power", 1e6),
    "J": ("energy", 1.0), "kWh": ("energy", 3.6e6), "MWh": ("energy", 3.6e9),
    "GWh": ("energy", 3.6e12),
    "Pa": ("pressure", 1.0), "hPa": ("pressure", 100.0),
    "kPa": ("pressure", 1e3), "bar": ("pressure", 1e5),
}
# temperatures: kelvin = value * a + b  (an offset, not only a factor)
TEMPERATURES = {"K": (1.0, 0.0), "degC": (1.0, 273.15),
                "degF": (5 / 9, 459.67 * 5 / 9)}
# [end: table]


class ConversionError(ValueError):
    """The value cannot be converted between the two units."""


# [start: convert]
def convert(value, src, dst):
    """value in unit src -> value in unit dst; refuses mixed dimensions."""
    if src in TEMPERATURES and dst in TEMPERATURES:
        a, b = TEMPERATURES[src]
        kelvin = value * a + b
        if kelvin < 0:
            raise ConversionError(f"{value} {src} is below absolute zero")
        a2, b2 = TEMPERATURES[dst]
        return (kelvin - b2) / a2
    for unit in (src, dst):
        if unit not in UNITS:
            raise ConversionError(f"unknown unit {unit!r}")
    dim1, f1 = UNITS[src]
    dim2, f2 = UNITS[dst]
    if dim1 != dim2:
        raise ConversionError(
            f"cannot convert {dim1} ({src}) to {dim2} ({dst})")
    return value * f1 / f2
# [end: convert]


# [start: cli]
def main(argv=None):
    ap = argparse.ArgumentParser(description="Convert a value between units.")
    ap.add_argument("value", type=float, help="the number to convert")
    ap.add_argument("src", help="unit of the value, e.g. km/h")
    ap.add_argument("dst", help="wanted unit, e.g. m/s")
    args = ap.parse_args(argv)
    try:
        result = convert(args.value, args.src, args.dst)
    except ConversionError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    print(f"{args.value:g} {args.src} = {result:.6g} {args.dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
# [end: cli]
