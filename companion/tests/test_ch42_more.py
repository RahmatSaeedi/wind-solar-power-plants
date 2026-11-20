"""Checks of the chapter 42 expansion helpers (Darcy fill, off-axis ply
modulus, Chvorinov, process FMEA order, root-bolt fatigue, winding rise)."""
import math

from companion.ch42 import examples_s as es
from companion.ch42 import examples_t as et
from companion.ch42 import examples_u as eu
from companion.ch42 import examples_w as ew
from plantp import quality as qa
from plantp import structures as st


def test_darcy_fill_grows_with_length_squared():
    assert math.isclose(es.fill_time(2.0) / es.fill_time(1.0), 4.0)
    # t = mu phi L^2 / (2 K dP) by hand for 1 m
    assert math.isclose(es.fill_time(1.0), 0.25 * 0.45 / (2 * 2e-10 * 0.9e5))


def test_offaxis_modulus_ends():
    assert math.isclose(et.e_theta(0.0), et.E1, rel_tol=1e-9)
    assert math.isclose(et.e_theta(90.0), et.E2, rel_tol=1e-9)
    assert et.e_theta(45.0) < et.e_theta(30.0) < et.e_theta(0.0)


def test_chvorinov_square_law():
    assert math.isclose(eu.solid_time(0.1) / eu.solid_time(0.05), 4.0)


def test_process_fmea_severity_first():
    rows = [dict(step=a, mode=b, effect=c, s=s, o=o, d=d)
            for a, b, c, s, o, d in ew.PFMEA]
    ranked = qa.fmea_rank(rows)
    assert ranked[0]["mode"] == "bond-line gap"
    # RPN alone ties the bond-line gap with the ply off its angle
    rpns = {r["mode"]: qa.rpn(r["s"], r["o"], r["d"]) for r in rows}
    assert rpns["bond-line gap"] == rpns["ply off its angle"] == 120


def test_preload_lost_bolt_damage():
    closed = 1e8 / st.sn_life(0.15 * 120e3 / 1120, 50.0)
    opened = 1e8 / st.sn_life(1.0 * 120e3 / 1120, 50.0)
    assert closed < 1.0 < opened
    assert opened / closed > 1000


def test_hertz_by_hand():
    from companion.ch42 import examples_y as ey
    b, p, z, tau = ey.hertz_line(2500.0, 40.0)
    assert math.isclose(b, math.sqrt(4 * 2500 * 40 / (math.pi * 115e3)))
    assert math.isclose(p, 2 * 2500 / (math.pi * b))
    # the shear profile peaks near 0.786 b at 0.300 p
    zs = [i / 1000 for i in range(1, 3000)]
    peak = max(zs, key=ey.shear_profile)
    assert abs(peak - 0.786) < 0.002
    assert abs(ey.shear_profile(peak) - 0.300) < 0.001


def test_circle_fit_exact():
    import numpy as np
    from companion.ch42 import examples_z as ez
    ang = np.linspace(0, 2 * math.pi, 12, endpoint=False)
    x = 3.0 + 5.0 * np.cos(ang)
    y = -1.0 + 5.0 * np.sin(ang)
    xc, yc, r = ez.fit_circle(x, y)
    assert math.isclose(xc, 3.0, abs_tol=1e-9)
    assert math.isclose(yc, -1.0, abs_tol=1e-9)
    assert math.isclose(r, 5.0, rel_tol=1e-12)


def test_saddles_meet_the_target():
    from companion.ch42 import examples_z as ez
    for pos in ([30.0, 50.0, 68.0], [15.0, 28.0, 40.0, 52.0, 62.0, 70.0]):
        f, m = ez.saddle_forces(pos)
        assert (f >= -1e-9).all()
        assert (m >= ez.target(ez.STATIONS) - 1e-9).all()


def test_tightening_passes_converge():
    from companion.ch42 import examples_m as em
    fs = em.tighten(list(range(96)), 96, passes=4)
    mins = [float(f.min()) for f in fs]
    assert mins[0] < mins[1] < mins[2] <= mins[3] <= 1.0
    assert mins[3] > 0.999


def test_airgap_first_harmonic_recovers_offset():
    import numpy as np
    from companion.ch42 import examples_m as em
    th = np.arange(8) * 2 * math.pi / 8
    ex, ey = 0.2, -0.1
    g = 4.0 - ex * np.cos(th) - ey * np.sin(th)
    e_x, e_y = em.gap_offset(g)
    assert math.isclose(e_x, ex, abs_tol=1e-12)
    assert math.isclose(e_y, ey, abs_tol=1e-12)


def test_winding_rise_by_resistance():
    r1, t1 = 0.0152, 20.0
    r2 = r1 * (234.5 + 102.0) / (234.5 + t1)
    t2 = r2 / r1 * (234.5 + t1) - 234.5
    assert math.isclose(t2, 102.0)
