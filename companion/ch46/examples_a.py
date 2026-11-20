"""Chapter 46, lesson A: cable and connector product - loss and voltage
drop of one collector string (the handoff's worked example), conductor
resistance of drums corrected to 20 C, crimp pull tests of a lug lot, and
the length printed on the sheath against the drum label.

Run from the project root:   python -m companion.ch46.examples_a
Writes companion/ch46/expected/a_*.txt.
Teaching values (A-482 to A-484); no test voltages, no extrusion values.
"""
from __future__ import annotations

import math

from companion.ch24 import sources as s24
from companion.ch46 import sources as src
from companion.ch46.common import emit
from plantp import cablemfg as km
from plantp import cables as cb


# [start: string]
def string_loss(p_mw: float = 5.0, kv: float = 33.0, pf: float = 0.95,
                theta: float = 70.0) -> dict:
    """Loss and drop of collector string WS1 at full output: segment k
    carries the turbines beyond it."""
    rows = [r for r in src.schedule() if r["id"] in ("W001", "W002", "W003")]
    rows.append(dict(id="W004", size_mm2=240, length_m=1210))     # as meant
    n = len(rows)
    i_t = p_mw * 1e6 / (math.sqrt(3) * kv * 1e3 * pf)            # one turbine
    loss = drop = 0.0
    seg = []
    for k, r in enumerate(rows):
        i = (n - k) * i_t
        c = s24.MV_CABLES[int(r["size_mm2"])]
        rr = cb.r_at(c["r20"], theta, 0.00403)             # aluminium
        l_km = r["length_m"] / 1000
        lw = cb.loss_kw(i, rr, l_km)
        dp = cb.drop_pct(i, l_km, rr, c["x"], pf, kv)
        loss += lw
        drop += dp
        seg.append((r["id"], r["size_mm2"], r["length_m"], i, lw, dp))
    return dict(seg=seg, loss=loss, drop=drop, p=n * p_mw)
# [end: string]


def string_report() -> dict:
    r = string_loss()
    lines = ["collector string WS1 at full output, 4 x 5 MW, 33 kV, pf 0.95, "
             "conductor 70 C",
             "  segment  mm2   length m   current A   loss kW   drop %"]
    for cid, mm2, l, i, lw, dp in r["seg"]:
        lines.append(f"  {cid:7s} {mm2:4d}   {l:8.0f}   {i:9.0f}   {lw:7.1f}   "
                     f"{dp:6.3f}")
    big = max(r["seg"], key=lambda x: x[4])
    two = sum(x[4] for x in r["seg"][:2]) / r["loss"]
    lines += [f"  total loss {r['loss']:.0f} kW ({r['loss'] / (r['p'] * 1000):.2%} "
              f"of {r['p']:.0f} MW); drop to the far turbine {r['drop']:.2f} %",
              f"  the two segments nearest the switchgear make {two:.0%} of the",
              f"  loss (largest {big[0]}); their larger sections keep it from",
              "  growing with the square of the current - the grading of ch 24",
              "  - the schedule's slip of W004 (1.21 'm') was put back to",
              "  1,210 m before this sum; with the slip the loss would be",
              "  computed on a cable a thousand times too short"]
    emit("a_string", lines)
    return r


# ------------------------------------------------ drums
def drums() -> dict:
    lines = ["conductor resistance of 400 mm2 Al drums, corrected to 20 C;",
             f"  limit {src.R20_MAX} ohm/km",
             "  drum   measured ohm   at C   ohm/km at 20 C   verdict"]
    out = {}
    for d, l, r, t in src.DRUMS:
        r20 = km.r_to_20(r, t) / (l / 1000)
        ok = r20 <= src.R20_MAX
        out[d] = (r20, ok)
        lines.append(f"  {d}   {r:12.4f}   {t:4.0f}   {r20:14.4f}   "
                     f"{'ok' if ok else 'REJECT'}")
    raw_bad = [d for d, l, r, t in src.DRUMS if r / (l / 1000) > src.R20_MAX]
    rej = [d for d, (_, ok) in out.items() if not ok]
    wrong_out = [d for d in raw_bad if d not in rej]
    wrong_in = [d for d in rej if d not in raw_bad]
    lines += [f"  rejected after the correction: {', '.join(rej)}",
              f"  read raw, the limit would reject {', '.join(wrong_out)} (warm, "
              "good)",
              f"  and pass {', '.join(wrong_in)} (cold, high) - D404 is high at "
              "any temperature;",
              "  only the reading corrected to 20 C is compared, with the",
              "  temperature kept in the drum's record"]
    emit("a_drums", lines)
    return dict(out=out, raw_bad=raw_bad)


# ------------------------------------------------ crimps
def crimps(tools=("A", "A", "A", "A", "A", "A", "B", "A", "A", "A", "B", "A")) -> dict:
    bad = [(k + 1, f, t) for k, (f, t) in enumerate(zip(src.CRIMPS, tools))
           if f < src.CRIMP_MIN]
    lines = [f"pull test of {len(src.CRIMPS)} lugs on 240 mm2 Al, minimum "
             f"{src.CRIMP_MIN} kN (teaching)",
             "  forces kN: " + ", ".join(f"{f:.1f}" for f in src.CRIMPS),
             "  below the minimum: " + "; ".join(f"no {k} {f} kN (tool {t})"
                                                for k, f, t in bad),
             "  both low pulls come from tool B: the crimp tool, not the lug,",
             "  is the suspect - every lug made with tool B since its last",
             "  check is traced and re-made, and the tool goes to calibration",
             "  (ch 40 crimp capability, ch 24 terminations)"]
    emit("a_crimps", lines)
    return dict(bad=bad)


# ------------------------------------------------ sheath print against label
def print_length(label_m: float = 1000.0, first: float = 2012.0,
                 last: float = 2997.0) -> dict:
    printed = last - first
    short = label_m - printed
    lines = [f"drum D405: label {label_m:.0f} m; sheath print {first:.0f} m at the "
             f"inner end,",
             f"  {last:.0f} m at the outer end",
             f"  length by the print: {printed:.0f} m - {short:.0f} m short of "
             "the label",
             "  the print is the cable's own record of its length: the",
             "  receiving check reads both ends and the schedule's lengths",
             "  are cut from what is really on the drum"]
    emit("a_print", lines)
    return dict(printed=printed, short=short)


if __name__ == "__main__":
    string_report()
    drums()
    crimps()
    print_length()
