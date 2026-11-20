"""Procurement and supplier-evaluation arithmetic for chapter 39.

compliance           share of requirements met, and the critical ones missed
evaluated_price      offer price + priced deviations + capitalised losses +
                     delivery liquidated damages + currency allowance
ld_amount            liquidated damages for a delay, with the cap
annuity              present value factor of a level yearly amount
allocate_availability  equal split of a series availability target
audit_score          weighted capability score; any critical item below
                     its floor fails the audit
schedule_completeness  share of required data items delivered and valid
interface_gaps       requirements in one contract with no matching term in
                     another

Teaching tools; the contract and the owner's procedures decide.
"""
from __future__ import annotations

# [start: evaluate]
def compliance(answers: dict[str, str],
               critical: set[str]) -> tuple[float, list]:
    """answers: requirement -> 'comply', 'deviate' or 'no'. Returns the
    share fully complied and the critical requirements not complied."""
    n = len(answers)
    ok = sum(1 for a in answers.values() if a == "comply")
    missed = sorted(r for r in critical if answers.get(r) != "comply")
    return ok / n if n else 1.0, missed


def evaluated_price(price: float, deviations: float, loss_cost: float,
                    delay_weeks: float, ld_per_week: float,
                    foreign_share: float, fx_allowance: float) -> float:
    """Price used to compare offers (k u): the offer, the priced
    deviations, the capitalised losses, the cost of a late delivery and an
    allowance for the currency risk on the foreign share."""
    return (price + deviations + loss_cost + delay_weeks * ld_per_week
            + price * foreign_share * fx_allowance)
# [end: evaluate]


# [start: contract]
def ld_amount(delay_weeks: float, rate_per_week: float, price: float,
              cap_share: float) -> tuple[float, bool]:
    """Delay damages and whether the cap was reached."""
    raw = delay_weeks * rate_per_week * price
    cap = cap_share * price
    return min(raw, cap), raw >= cap


def annuity(rate: float, years: int) -> float:
    return (1 - (1 + rate) ** -years) / rate


def allocate_availability(target: float, n: int) -> float:
    """Equal availability of n parts in series that meets the target."""
    return target ** (1.0 / n)
# [end: contract]


# [start: supplier]
def audit_score(scores: dict[str, float], weights: dict[str, float],
                floors: dict[str, float]) -> tuple[float, list]:
    """Weighted score 0-5 and the items below their floor (a fail)."""
    w = sum(weights.values())
    s = sum(scores[k] * weights[k] for k in weights) / w
    fails = sorted(k for k, f in floors.items() if scores.get(k, 0.0) < f)
    return s, fails


def schedule_completeness(required: list[str],
                          delivered: dict[str, bool]) -> tuple:
    """delivered: item -> valid? Share delivered and valid, and what is
    missing or invalid."""
    good = [r for r in required if delivered.get(r) is True]
    bad = [r for r in required if delivered.get(r) is not True]
    return len(good) / len(required), bad


def interface_gaps(needs: dict[str, set[str]],
                   terms: dict[str, set[str]]) -> dict:
    """needs: contract -> topics it relies on another contract for;
    terms: contract -> topics it covers. Returns the uncovered topics."""
    covered = set().union(*terms.values()) if terms else set()
    return {c: sorted(t - covered) for c, t in needs.items() if t - covered}
# [end: supplier]
