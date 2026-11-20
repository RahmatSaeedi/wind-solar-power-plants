"""Chapter 28 - registers for the study of Plant P's proposed POC:
requirements (placeholders for the operator's code, U-102), study inputs
with owner and status, models with versions, and approval boundaries.

Every requirement text is a TEACHING placeholder ("REQ-G.."), not a
country requirement. Values come from the operator once U-102 closes.
"""
from __future__ import annotations

from dataclasses import dataclass

# [start: requirement]
@dataclass(frozen=True)
class Requirement:
    rid: str
    topic: str
    study: str        # which study shows it ('' = none yet)
    model: str        # which model the study uses
    test: str         # which test proves it on site ('' = none yet)
    evidence: str     # the record that closes it
# [end: requirement]


REQUIREMENTS = (
    Requirement("REQ-G01", "reactive capability at the POC", "B-reactive, F-envelope",
                "load flow + unit P-Q", "P-Q capability test", "test report vs model"),
    Requirement("REQ-G02", "voltage control at the POC", "C-vcontrol", "plant controller RMS",
                "voltage step test", "step metrics (ch 27)"),
    Requirement("REQ-G03", "power-factor and Q modes", "B-reactive", "plant controller RMS",
                "mode change test", "test report"),
    Requirement("REQ-G04", "low-voltage ride-through", "C-frt", "unit + plant RMS, EMT",
                "unit type test", "type test + validated model"),
    Requirement("REQ-G05", "high-voltage ride-through", "C-frt", "unit + plant RMS, EMT",
                "unit type test", "type test + validated model"),
    Requirement("REQ-G06", "reactive current in dips", "C-frt", "unit RMS", "unit type test",
                "type test report"),
    Requirement("REQ-G07", "active power recovery", "C-frt", "unit + plant RMS", "unit type test",
                "type test + recorded event"),
    Requirement("REQ-G08", "frequency range of operation", "C-freq", "unit data", "",
                "maker's declaration"),
    Requirement("REQ-G09", "over-frequency power reduction", "C-freq", "plant controller RMS",
                "frequency injection test", "test report"),
    Requirement("REQ-G10", "under-frequency response, contracted", "F-envelope",
                "plant controller + BESS RMS", "frequency injection test", "test + headroom record"),
    Requirement("REQ-G11", "RoCoF withstand", "C-freq", "unit RMS", "", "maker's declaration"),
    Requirement("REQ-G12", "loss of mains / intertrip", "C-islanding", "protection scheme",
                "intertrip function test", "end-to-end test record"),
    Requirement("REQ-G13", "reconnection after a trip", "C-restore", "plant controller RMS",
                "reconnection test", "test report"),
    Requirement("REQ-G14", "ramp-rate limits", "C-restore", "plant controller RMS",
                "set-point ramp test", "SCADA record"),
    Requirement("REQ-G15", "active power set-point following", "C-restore",
                "plant controller RMS", "set-point test", "SCADA record"),
    Requirement("REQ-G16", "export limit at the POC", "B-cases, G-export", "load flow",
                "metering check", "revenue meter record"),
    Requirement("REQ-G17", "telemetry signals and latency", "C-restore", "", "end-to-end test",
                "signal list + latency record"),
    Requirement("REQ-G18", "short-circuit contribution data", "B-sc", "short-circuit model", "",
                "study report"),
    Requirement("REQ-G19", "protection coordination", "B-protection", "protection model",
                "secondary injection, end-to-end", "settings record (ch 26)"),
    Requirement("REQ-G20", "harmonic emission and flicker", "ch 27 studies", "harmonic model",
                "PQ measurement", "PQ report (ch 27)"),
    Requirement("REQ-G21", "validated simulation models", "F-versions", "all", "",
                "validation report, versions"),
    Requirement("REQ-G22", "stable at minimum grid strength", "E-weak", "EMT", "",
                "study report"),
    Requirement("REQ-G23", "compliance tests at commissioning", "C-tests", "", "test programme",
                "operator's acceptance"),
    Requirement("REQ-G24", "fast frequency response, contracted", "F-envelope",
                "plant controller + BESS RMS", "", ""),
)

# [start: inputs]
INPUTS = (   # (id, item, owner, status, quality, needed by)
    ("IN-01", "short-circuit level at POC, max/min", "operator", "received", "B", "B E"),
    ("IN-02", "X/R at POC", "operator", "received", "B", "B"),
    ("IN-03", "network model around the POC", "operator", "requested", "-", "B C E G"),
    ("IN-04", "steady-state voltage range at POC", "operator", "received", "B", "B"),
    ("IN-05", "frequency ranges and durations", "operator", "assumed", "C", "C"),
    ("IN-06", "fault clearing, auto-reclose times", "operator", "requested", "-", "C"),
    ("IN-07", "protection settings at the grid end", "operator", "requested", "-", "B"),
    ("IN-08", "background harmonics at POC (U-101)", "operator", "missing", "-", "ch27"),
    ("IN-09", "emission allocation (U-100)", "operator", "missing", "-", "ch27"),
    ("IN-10", "applicable code, version (U-102)", "operator", "missing", "-", "all"),
    ("IN-11", "neighbouring plants and their size", "operator", "requested", "-", "E"),
    ("IN-12", "one-line diagram (D-027)", "plant", "received", "A", "all"),
    ("IN-13", "main transformer guaranteed data", "plant", "received", "B", "B"),
    ("IN-14", "main transformer test data (FAT)", "plant", "missing", "-", "B"),
    ("IN-15", "33 kV cable lengths and sections", "plant", "received", "B", "B"),
    ("IN-16", "132 kV line conductor and route", "plant", "received", "B", "B G"),
    ("IN-17", "line measured impedance", "plant", "missing", "-", "B G"),
    ("IN-18", "unit data sheets (wind, PV, BESS)", "OEM", "received", "B", "B"),
    ("IN-19", "unit P-Q capability vs voltage", "OEM", "received", "B", "B F"),
    ("IN-20", "unit RMS models with versions", "OEM", "received", "B", "C E F"),
    ("IN-21", "unit EMT models with versions", "OEM", "requested", "-", "E"),
    ("IN-22", "unit type tests (ride-through)", "OEM", "received", "A", "C"),
    ("IN-23", "plant controller model and settings", "OEM", "received", "C", "C F"),
    ("IN-24", "BESS PCS model and limits (S1)", "OEM", "requested", "-", "F"),
    ("IN-25", "auxiliary loads (ch 23)", "plant", "received", "B", "B"),
    ("IN-26", "earthing and neutral data", "plant", "received", "B", "B"),
    ("IN-27", "metering point and class", "operator", "received", "B", "G"),
    ("IN-28", "telemetry signal list", "operator", "requested", "-", "C"),
    ("IN-29", "weather data for line rating", "plant", "received", "B", "G"),
    ("IN-30", "outage rates of plant elements", "plant", "assumed", "C", "G"),
)
# [end: inputs]

MODELS = (   # (model, kind, owner, version in study, version on site / plan)
    ("wind converter", "RMS generic", "OEM / plant", "G-4.0 (61400-27-1)", "G-4.0"),
    ("wind converter", "EMT vendor", "OEM", "W-EMT 7.2", "W-EMT 7.3"),
    ("PV inverter", "RMS vendor", "OEM", "PV-RMS 2.3 / FW 4.1.7", "FW 4.2.0"),
    ("PV inverter", "EMT vendor", "OEM", "PV-EMT 5.0 / FW 4.1.7", "FW 4.2.0"),
    ("BESS PCS", "RMS vendor", "OEM", "not received", "FW 2.0.3"),
    ("plant controller", "RMS vendor", "OEM / plant", "PPC 1.4, settings 7a91",
     "settings 7a91"),
    ("collector network", "aggregated", "plant", "rev C (this chapter)", "rev C"),
    ("132 kV line", "pi model", "plant", "calculated", "to be measured"),
)

APPROVALS = (   # (item, prepares, reviews, approves)
    ("study scope and cases", "plant study engineer", "operator", "operator"),
    ("input data", "data owner", "study engineer", "data owner signs"),
    ("unit and controller models", "OEM", "study engineer (validation)", "operator accepts"),
    ("study results", "study engineer", "independent checker", "licensed engineer + operator"),
    ("protection settings", "protection engineer", "operator", "operator (interface)"),
    ("test programme", "plant", "operator", "operator"),
    ("compliance statement", "plant", "operator", "operator (operating notice)"),
)
