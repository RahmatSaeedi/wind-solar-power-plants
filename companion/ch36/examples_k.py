"""Chapter 36, lesson K (procurement and supply chain): security
requirements written into a purchase, a supplier scorecard, provenance
checks on receipt, support periods against the plant's life, and how to
review a vendor's network design without exposing site details.

Run from the project root:   python -m companion.ch36.examples_k
Writes companion/ch36/expected/k_*.txt.
Teaching values (A-406); defensive only.
"""
from __future__ import annotations

from companion.ch36 import sources as src
from companion.ch36.common import emit
from plantp import ot_security as ot


def requirements() -> None:
    rows = [("secure development process of the maker", "STD-159"),
            ("component security capabilities declared", "STD-160"),
            ("integrator's and service provider's programme", "STD-161"),
            ("security notices and patches for N years", "contract"),
            ("list of software components and versions", "contract"),
            ("signed firmware; hashes published", "contract"),
            ("no default passwords; unique per device", "contract"),
            ("remote access only through the owner's path", "contract")]
    lines = ["security requirements written into a purchase (teaching list)",
             "  requirement                                        basis"]
    for r, b in rows:
        lines.append(f"  {r:50s} {b}")
    lines += ["  what is not asked for in the purchase is hard to get",
              "  later; each requirement is tested in the factory test",
              "  or checked on delivery, not trusted from a brochure"]
    emit("k_requirements", lines)


def scorecard() -> None:
    lines = ["supplier scorecard (0-5, teaching weights)",
             "  supplier  " + "  ".join(f"{k[:10]:>10s}" for k in src.SUPPLIER_WEIGHTS)
             + "   score"]
    lines.append("  weight    " + "  ".join(f"{w:10d}" for w in src.SUPPLIER_WEIGHTS.values()))
    for s, sc in src.SUPPLIERS.items():
        lines.append(f"  {s:8s}  " + "  ".join(f"{sc[k]:10d}" for k in src.SUPPLIER_WEIGHTS)
                     + f"   {ot.weighted_score(sc, src.SUPPLIER_WEIGHTS):5.2f}")
    lines += ["  S-C leads on secure development and provenance though its",
              "  patch support is short - a gap to close in the contract;",
              "  S-B has the best local service and the weakest security",
              "  practice; the weights say what matters more for a plant",
              "  that must be patched for 25 years, and the scores come",
              "  from evidence asked for in the tender"]
    emit("k_scorecard", lines)


def provenance() -> None:
    received, checked = 34, 34
    lines = ["provenance checks on delivery of 34 switches (teaching)",
             "  serial numbers against the maker's shipment list    34 of 34",
             "  firmware signature verified, hash against notice   34 of 34",
             "  seals and packaging intact                          33 of 34",
             "  one switch with a broken seal: held, not installed, the",
             "  maker asked to confirm the serial and reflash from the",
             "  signed image on the test bench",
             f"  {checked} of {received} checked: every device, because one",
             "  counterfeit or altered switch sits inside the ring"]
    emit("k_provenance", lines)


def support_life() -> None:
    life = 25
    lines = ["maker's support against the plant's life (teaching)",
             "  support promised   generations of a device in 25 years"]
    for yrs in (5, 7, 10, 15):
        lines.append(f"  {yrs:16d} y   {-(-life // yrs):17d}")
    lines += ["  each generation is a purchase, a test and an outage; a",
              "  longer support period is worth paying for in the tender,",
              "  and the end-of-support dates enter the inventory (lesson C)"]
    emit("k_support", lines)


def vendor_review() -> None:
    share = [("zones, conduits and purposes", "yes"),
             ("device kinds and counts", "yes"),
             ("required availability and recovery times", "yes"),
             ("addresses, names of real hosts", "no"),
             ("credentials, keys, firewall rules as running", "no"),
             ("site location and access routes", "no")]
    lines = ["reviewing a vendor's network design without exposing the site",
             "  shared with the vendor                          "]
    for a, b in share:
        lines.append(f"  {a:46s} {b}")
    lines += ["  the vendor designs against a sanitised model of the plant",
              "  under a confidentiality agreement; the review checks the",
              "  design against the conduit table and the targets, and",
              "  the owner fills in the real details after acceptance"]
    emit("k_vendor", lines)


if __name__ == "__main__":
    requirements()
    scorecard()
    provenance()
    support_life()
    vendor_review()
