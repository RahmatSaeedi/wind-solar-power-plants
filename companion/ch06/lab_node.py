"""Chapter 6 lab: solve a small DC network by computer and check it by hand.

Run from the project root:   python -m companion.ch06.lab_node
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plantp import dc  # noqa: E402

# [start: build]
# Nodes: 0 = reference, 1 = top of the 10 V source,
#        2 = the unknown node x, 3 = top of the 5 V source.
resistors = [
    (1, 2, 2.0),   # R1 between node 1 and node x
    (2, 3, 3.0),   # R3 between node x and node 3
    (2, 0, 4.0),   # R2 from node x to the reference
]
sources = [
    (1, 0, 10.0),  # V_s1: + at node 1, - at the reference
    (3, 0, 5.0),   # V_s2: + at node 3, - at the reference
]
sol = dc.solve_dc(4, resistors, sources)
v_x = sol.node_voltages[2]
# [end: build]

# [start: check]
by_hand = 80.0 / 13.0                    # from the node equation
i1 = (10.0 - v_x) / 2.0                  # into node x through R1
i3 = (5.0 - v_x) / 3.0                   # into node x through R3
i2 = v_x / 4.0                           # out of node x through R2
print(f"V_x by computer = {v_x:.6f} V, by hand = {by_hand:.6f} V")
print(f"I1 = {i1:.4f} A, I3 = {i3:.4f} A, I2 = {i2:.4f} A")
print(f"KCL at node x: I1 + I3 - I2 = {i1 + i3 - i2:.2e} A")
print(f"source currents: {sol.source_currents[0]:.4f} A, "
      f"{sol.source_currents[1]:.4f} A")
assert abs(v_x - by_hand) < 1e-9, "computer and hand disagree"
# [end: check]
