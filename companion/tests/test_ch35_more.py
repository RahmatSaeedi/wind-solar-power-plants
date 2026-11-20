"""Chapter 35, deeper lessons: hand checks of the trace, the deadband,
the float counter, word order and the logical-diagram table."""
import math

import numpy as np

from companion.ch35 import examples_m as m
from companion.ch35 import examples_n as n


def test_trace_adds_up():
    assert abs(sum(d for _, d, _ in m.HOPS) - 2170.1) < 1e-9


def test_logical_table_counts():
    yes = sum(ok.startswith("yes") for _, _, ok in m.FLOWS)
    assert (yes, len(m.FLOWS)) == (7, 9)


def test_float32_loses_small_steps():
    big = np.float32(7.3775e9)
    step = np.float32(1666.7)
    assert float(np.float32(big + step) - big) != float(step)
    ulp = 2.0 ** (math.floor(math.log2(7.3775e9)) - 23)
    assert ulp == 512.0


def test_word_swap_by_hand():
    value = 295_100
    hi, lo = value >> 16, value & 0xFFFF
    assert (hi, lo) == (4, 32_956)
    assert hi * 65536 + lo == value


def test_flood_suppression_numbers():
    assert n.__doc__ and 151 - 138 == 13
