"""Chapter 3 laboratory 3 — harmonic amplitudes from a sampled current: window length,
window shape and synchronisation.

Run from the project root:   python -m companion.ch03.lab_spectrum
A synthetic inverter current (A-040: 1.0 pu fundamental, 0.04 pu 5th, 0.03 pu 7th) at a
grid frequency of 49.8 Hz (assumed) is sampled at 10 kHz. Harmonic amplitudes are read
from the FFT of (a) a 200 ms window with a rectangular shape, (b) the same window with a
Hann shape, (c) a window of exactly ten periods of the actual frequency.
Writes companion/ch03/expected/lab_spectrum.txt.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np

OUT = Path(__file__).resolve().parent / "expected" / "lab_spectrum.txt"


# [start: spectrum]
def harmonic_peaks(x, fs, f1, orders, window="rect"):
    """Peak amplitude near each harmonic h * f1 from the FFT of x."""
    n = len(x)
    w = np.hanning(n) if window == "hann" else np.ones(n)
    spec = np.abs(np.fft.rfft(x * w)) * 2 / w.sum()   # amplitude scale
    freqs = np.fft.rfftfreq(n, 1 / fs)
    out = []
    for h in orders:
        k = int(np.argmin(np.abs(freqs - h * f1)))     # nearest bin
        out.append(spec[k - 1:k + 2].max())           # largest of 3 bins
    return np.array(out)
# [end: spectrum]


def signal(t, f):
    return (np.sin(2 * math.pi * f * t) + 0.04 * np.sin(2 * math.pi * 5 * f * t + 0.5)
            + 0.03 * np.sin(2 * math.pi * 7 * f * t - 0.8))


def main() -> None:
    fs, f_true, orders = 10_000.0, 49.8, (1, 5, 7)
    t200 = np.arange(2000) / fs                        # 200 ms: ten periods at 50 Hz
    n_sync = int(round(10 / f_true * fs))              # ten periods at 49.8 Hz
    t_sync = np.arange(n_sync) / fs
    cases = [("200 ms, rectangular", harmonic_peaks(signal(t200, f_true), fs, 50.0, orders)),
             ("200 ms, Hann", harmonic_peaks(signal(t200, f_true), fs, 50.0, orders, "hann")),
             (f"{n_sync} samples = 10 periods",
              harmonic_peaks(signal(t_sync, f_true), fs, f_true, orders))]
    lines = ["true amplitudes (pu): 1.000, 0.040, 0.030; THD 5.00 %; grid at 49.8 Hz",
             "  window                         A1      A5      A7    THD (%)"]
    for name, a in cases:
        thd = math.sqrt(a[1] ** 2 + a[2] ** 2) / a[0]
        lines.append(f"  {name:28s} {a[0]:6.3f}  {a[1]:6.4f}  {a[2]:6.4f}  {100 * thd:6.2f}")
    lines.append("the synchronised window recovers the amplitudes; a fixed 200 ms window")
    lines.append("    leaks, and the Hann shape reduces the error at the cost of resolution")
    text = "\n".join(lines) + "\n"
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(text)


if __name__ == "__main__":
    main()
