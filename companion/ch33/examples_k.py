"""Chapter 33, lesson K: supplier environmental data - verified supplier
declarations against generic factors, when two declarations can be
compared, and how data quality sets the uncertainty a study carries.

Run from the project root:   python -m companion.ch33.examples_k
Writes companion/ch33/expected/k_*.txt.
Teaching values (A-383); declarations follow ISO 14025 (STD-145) and the
product category rules that apply.
"""
from __future__ import annotations

from companion.ch33 import sources as src
from companion.ch33.common import emit


def module_data() -> None:
    kwp = src.LCA["PV modules (kWp)"][0]
    rows = [("generic factor (database)", 450.0, "generic", 0.30),
            ("supplier S1, verified declaration", 350.0, "verified", 0.10),
            ("supplier S2, self-declared", 300.0, "unverified", 0.30)]
    lines = ["PV module footprint: generic factor or supplier data? (kg CO2e/kWp)",
             "  source                              value   quality     cov   t CO2e"]
    for s, v, q, c in rows:
        lines.append(f"  {s:35s} {v:5.0f}   {q:10s}  {c:4.2f}   {v * kwp / 1000:6,.0f}")
    lines += ["  S2's lower number cannot be used as if it were S1's: it is",
              "  unverified, and its uncertainty stays as wide as a generic",
              "  factor's. Verified supplier data narrows the study and can",
              "  be written into the purchase contract (ch 38-40)"]
    emit("k_modules", lines)


def comparability() -> None:
    checks = [("same functional unit (1 kWp of modules at the gate)", True),
              ("same product category rules", True),
              ("same system boundary (cradle to gate)", True),
              ("same reference year and grid of manufacture", False),
              ("both verified by a third party", False)]
    lines = ["can the two module declarations be compared? (teaching checklist)"]
    for c, ok in checks:
        lines.append(f"  {'yes' if ok else 'NO ':3s}  {c}")
    lines += ["  two failed conditions: the comparison is not valid as it",
              "  stands - the manufacturing grid alone can move a module's",
              "  footprint by a third; the buyer asks for updated, verified",
              "  declarations before ranking suppliers on carbon"]
    emit("k_compare", lines)


def data_quality() -> None:
    inv = {k: a * f for k, (a, f, _c) in src.LCA.items()}
    tot = sum(inv.values())
    groups = {"modules": ["PV modules (kWp)"], "turbines": ["turbines excl. tower (MW)"],
              "towers": ["towers, steel (t)"],
              "foundations": ["foundations, concrete (m3)", "rebar (t)"],
              "cables": ["cables, aluminium (t)", "cables, copper (t)"]}
    used = {k for v in groups.values() for k in v}
    shares = {g: sum(inv[k] for k in ks) / tot for g, ks in groups.items()}
    shares["others"] = sum(v for k, v in inv.items() if k not in used) / tot
    covs = {"modules": 0.10, "turbines": 0.30, "towers": 0.20, "foundations": 0.25,
            "cables": 0.30, "others": 0.40}
    items = [(g, covs[g], shares[g]) for g in covs]
    combined = sum((share * cov) ** 2 for _, cov, share in items) ** 0.5
    lines = ["how data quality sets the study's uncertainty (shares of the total)",
             "  item          cov    share   contribution to variance"]
    var = [(share * cov) ** 2 for _, cov, share in items]
    for (n, cov, share), v in zip(items, var):
        lines.append(f"  {n:12s} {cov:5.2f}   {share:5.2f}   {v / sum(var) * 100:24.0f} %")
    lines += [f"  combined coefficient of variation: {combined * 100:.0f} %",
              "  with verified module data, the turbines and the mixed",
              "  'others' (structures, inverters, diesel, transport) carry",
              "  most of the variance: better data there narrows the",
              "  result most - effort goes where the variance is"]
    emit("k_quality", lines)


if __name__ == "__main__":
    module_data()
    comparability()
    data_quality()
