"""Chapter 23 - Plant P's electrical system as data (teaching values
A-316 to A-320), built on the architecture basis D-022: twelve 5 MW
turbines on three radial 33 kV strings, ten 5 MW PV blocks on three
feeders, a 20 MW battery in four 5 MW blocks on two feeders, a split
33 kV bus, two 63 MVA 132/33 kV transformers, two station-service
transformers, a 132 kV overhead line of 7.06 km to the grid bay.

Statuses: confirmed (decided in D-012..D-025), provisional (a value to
design with until a maker or study confirms it) or open (an unknown).
Nothing here is a recommended design.
"""
from __future__ import annotations

from companion.ch23 import common  # noqa: F401  (puts plantp on the path)
from plantp import auxpower as ax
from plantp import oneline as ol

B, Br = ol.Bus, ol.Branch
P, C, O = "provisional", "confirmed", "open"

# [start: allocation]
SECTIONS = {   # 33 kV bus section -> feeders (A-316)
    "MV-A": {"WS1": 4, "WS2": 4, "PVF3": 3, "BESS-A": 2},
    "MV-B": {"WS3": 4, "PVF1": 4, "PVF2": 3, "BESS-B": 2},
}
UNIT_MW = {"WS": 5.0, "PVF": 5.0, "BESS": 5.0}   # per turbine/block/PCS
# [end: allocation]


def plant() -> ol.OneLine:
    g = ol.OneLine()
    g.add_bus(B("HV", 132.0, zone="Z-HV"),
              B("GRID", 132.0, owner="utility", zone="Z-GRID"),
              B("MV-A", 33.0, zone="Z-MVA"), B("MV-B", 33.0, zone="Z-MVB"),
              B("LV-A", 0.4, zone="Z-LVA"), B("LV-B", 0.4, zone="Z-LVB"))
    # export line and grid bay: the owner of the line is open (U-065)
    g.add_bus(B("E1", 132.0, zone="Z-L1"),
              B("LINE-P", 132.0, owner="open (U-065)", zone="Z-L1"),
              B("LINE-G", 132.0, owner="open (U-065)", zone="Z-L1"),
              B("GRID-BAY", 132.0, owner="utility", zone="Z-GRID"))
    g.add(Br("=E1-Q1", "breaker", "HV", "E1", zone="Z-L1",
             rating={"kv": 145, "ka": 31.5}, status={"ka": P},
             meter="revenue (option A)"),
          Br("=E1-Q9", "disconnector", "E1", "LINE-P", zone="Z-L1", isolation=True,
             test="plant and utility"),
          Br("=E1-W1", "line", "LINE-P", "LINE-G", owner="open (U-065)", zone="Z-L1",
             rating={"km": 7.06, "mva": 140}, status={"owner": O, "mva": P}),
          Br("=G1-Q9", "disconnector", "LINE-G", "GRID-BAY", owner="utility",
             zone="Z-GRID", isolation=True, test="utility"),
          Br("=G1-Q1", "breaker", "GRID-BAY", "GRID", owner="utility", zone="Z-GRID",
             meter="revenue (option B)"))
    for k, sec in ((1, "MV-A"), (2, "MV-B")):
        g.add_bus(B(f"T{k}-HV", 132.0, zone=f"Z-T{k}"),
                  B(f"T{k}-MV", 33.0, zone=f"Z-T{k}"),
                  B(f"A{k}-MV", 33.0, zone=f"Z-LV{'AB'[k - 1]}"))
        g.add(Br(f"=T{k}-Q1", "breaker", "HV", f"T{k}-HV", zone=f"Z-T{k}",
                 isolation=True, rating={"kv": 145}),
              Br(f"=T{k}", "transformer", f"T{k}-HV", f"T{k}-MV", zone=f"Z-T{k}",
                 rating={"mva": 63, "hv_kv": 132.0, "lv_kv": 33.0, "z_pu": 0.12,
                         "vector": "YNd11"},
                 status={"z_pu": P, "vector": P, "tap": O}),
              Br(f"=T{k}-Q2", "breaker", f"T{k}-MV", sec, zone=f"Z-T{k}",
                 isolation=True, rating={"a": 1250, "ka": 25}, status={"a": P}),
              Br(f"=A{k}-Q1", "breaker", sec, f"A{k}-MV", zone=f"Z-LV{'AB'[k - 1]}",
                 isolation=True, rating={"a": 630, "ka": 25}),
              Br(f"=A{k}-T1", "transformer", f"A{k}-MV", f"LV-{'AB'[k - 1]}",
                 zone=f"Z-LV{'AB'[k - 1]}",
                 rating={"kva": 250, "hv_kv": 33.0, "lv_kv": 0.4, "z_pu": 0.045},
                 status={"kva": P}))
    g.add(Br("=MV-Q0", "breaker", "MV-A", "MV-B", zone="Z-MVA", isolation=True,
             rating={"a": 2500, "ka": 25}, status={"ka": P}))
    for sec, feeders in SECTIONS.items():
        for f, n in feeders.items():
            kind = f.rstrip("AB0123456789-")
            head = f"{f}-0"
            g.add_bus(B(head, 33.0, zone=f"Z-{f}"))
            g.add(Br(f"={f}-Q1", "breaker", sec, head, zone=f"Z-{f}", isolation=True,
                     rating={"a": 630, "ka": 25}))
            prev = head
            for u in range(1, n + 1):
                node, lv = f"{f}-{u}", f"{f}-{u}-LV"
                kv_lv = {"WS": 0.69, "PVF": 0.6, "BESS": 0.69}[kind]
                g.add_bus(B(node, 33.0, zone=f"Z-{f}"),
                          B(lv, kv_lv, zone=f"Z-{f}-{u}"))
                g.add(Br(f"={f}-W{u}", "cable", prev, node, zone=f"Z-{f}",
                         rating={"mm2": 240, "km": 1.1 if kind == "WS" else 0.6},
                         status={"km": P}),
                      Br(f"={f}-{u}-T1", "transformer", node, lv, zone=f"Z-{f}-{u}",
                         rating={"mva": 5.6 if kind == "WS" else 5.5, "hv_kv": 33.0,
                                 "lv_kv": kv_lv, "z_pu": 0.07 if kind == "WS" else 0.06},
                         status={"z_pu": P}))
                prev = node
    return g


# [start: pvblock]
def pv_block_detail(g: ol.OneLine, blk: str = "PVF1-1") -> ol.OneLine:
    """Add the DC side of one PV block for the trace: one string of 26
    modules, its combiner box, the DC main cable and the inverter."""
    dc = 1.5                                   # kV DC system class (D-013)
    g.add_bus(B(f"{blk}-S01", dc, zone=f"Z-{blk}-DC"),
              B(f"{blk}-CB01", dc, zone=f"Z-{blk}-DC"),
              B(f"{blk}-DC", dc, zone=f"Z-{blk}-DC"))
    g.add(Br(f"={blk}-S01-W1", "dc cable", f"{blk}-S01", f"{blk}-CB01",
             zone=f"Z-{blk}-DC", rating={"mm2": 6, "modules": 26},
             test="string checks (ch 10)"),
          Br(f"={blk}-CB01-Q1", "dc switch", f"{blk}-CB01", f"{blk}-DC",
             zone=f"Z-{blk}-DC", isolation=True,
             rating={"strings": 20, "fuse_a": 25}, status={"fuse_a": P}),
          Br(f"={blk}-U1", "inverter", f"{blk}-DC", f"{blk}-LV", zone=f"Z-{blk}",
             isolation=True, rating={"mva": 5.0, "ac_kv": 0.6},
             status={"firmware": O}, test="maker FAT, site tests"))
    return g
# [end: pvblock]


# [start: aux]
def L(tag, kw, pf, kind, ess, duty, prio, start=0.0):
    names = ("normal", "degraded", "emergency", "maintenance")
    return ax.Load(tag, kw, pf, kind, ess, dict(zip(names, duty)), prio, start)


CONT, INT = "continuous", "intermittent"
AUX = [  # station-service loads (A-317)
    # tag, kW, pf, kind, essential, duty (norm, degr, emer, maint),
    # priority, starting kVA
    L("DC chargers 110 V", 12, .90, CONT, True, (1, 1, 1, 1), 1),
    L("UPS: SCADA, PPC, telecom", 25, .95, CONT, True, (1, 1, 1, 1), 1),
    L("control room HVAC", 30, .85, INT, True, (.7, .7, .7, .5), 2, 120),
    L("switchgear room ventilation", 20, .85, INT, True,
      (.6, .6, .6, .4), 2, 80),
    L("on-load tap changer motors", 3, .80, INT, True, (.1, .1, .1, 0), 2),
    L("transformer cooling fans", 16, .85, INT, True, (.5, .5, 0, 0), 3, 40),
    L("substation lighting and security", 15, .95, CONT, True,
      (.5, .5, .5, 1), 3),
    L("drainage and sump pumps", 8, .85, INT, True, (.2, .2, .3, .2), 3, 40),
    L("water pumping and treatment", 40, .85, INT, False,
      (.4, .4, 0, .2), 6, 200),
    L("cleaning robots charging", 60, .95, INT, False, (.5, .5, 0, 0), 7),
    L("workshop and stores", 35, .90, INT, False, (.5, .5, 0, 1), 8),
    L("maintenance socket outlets", 30, .90, INT, False, (.1, .1, 0, 1), 8),
    L("staff facilities", 25, .95, INT, False, (.6, .6, 0, .6), 9),
]
DIVERSITY = 0.9
# [end: aux]

# [start: dc]
DC_DUTY = [  # 110 V DC system (A-318): (amps, minutes)
    (150.0, 1),       # first minute: trips of breakers, relays pick up
    (40.0, 238),      # standing load: relays, controls, indication
    (100.0, 1),       # last minute: closing and spring charging
]
DC_AUTONOMY_H = 4.0                  # teaching requirement
UPS_KW, UPS_MIN = 25.0, 60.0          # UPS load and autonomy
# [end: dc]
