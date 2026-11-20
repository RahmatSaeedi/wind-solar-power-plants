"""Chapter 33, lab G (worked example 2): a hypothetical land-access and
livelihood case - the herders' grazing and their route to the spring -
from baseline to options, monitoring and closeout, with the questions
the governing framework, not this lab, must answer.

Run from the project root:   python -m companion.ch33.lab_g
Writes companion/ch33/expected/g_*.txt and diagrams/data/ch33-livelihood.csv.
Teaching values (A-381); the case is fictional. Whether any safeguard
(compensation, consent, a livelihood plan) is triggered is decided under
the governing framework with qualified local social and legal experts.
"""
from __future__ import annotations

from companion.ch33 import sources as src
from companion.ch33.common import csv, emit
from plantp import envsocial as es


def baseline() -> None:
    h = src.HERDERS
    income = es.livelihood_income(h["grazing_ha"], h["animals"] / h["grazing_ha"],
                                  h["income_per_animal"])
    lines = ["baseline of the herding families (survey, teaching values)",
             f"  households {h['households']}; animals {h['animals']}; customary grazing"
             f" {h['grazing_ha']:.0f} ha (Apr-Oct)",
             f"  grazing income supported: {income:.0f} k u a year",
             "  water: the spring, 1.2 km from the camp by the old route",
             "  other income: seasonal wage work, sale of dairy products",
             "  decision-makers: elders; women manage dairy and water",
             "  what the baseline must record before any works start:",
             "  incomes, animals, routes, seasons and who decides - so",
             "  that change can later be measured against it"]
    emit("g_baseline", lines)


def options() -> None:
    h = src.HERDERS
    loss_area = 3.1 / h["grazing_ha"]
    rows = [("A: do nothing (detour 3.5 km)", 0.0, 0.05 + loss_area, "worst for families"),
            ("B: gap in PV fence + trench crossing", 15.0, loss_area, "route restored"),
            ("C: new water point near the camp", 40.0, loss_area * 0.5, "less walking than before"),
            ("D: cash payment only", 60.0, 0.05 + loss_area, "income dips again later")]
    lines = ["options for the route and the grazing (teaching costs, k u)",
             "  option                                 cost   income loss"]
    base = src.HERDERS["animals"] * src.HERDERS["income_per_animal"]
    for o, c, frac, note in rows:
        lines += [f"  {o:38s} {c:5.0f}   {frac * base:8.1f}/yr", f"      {note}"]
    lines += ["  avoidance (B) restores the livelihood at the source for",
              "  less than paying for its loss (D), and C can leave the",
              "  families better off than before - the families choose",
              "  among options that are approved and funded; whether",
              "  compensation also applies is the framework's question"]
    emit("g_options", lines)


def monitoring() -> None:
    years = [0, 1, 2, 3]
    animals = [600, 590, 610, 620]
    income = [72.0, 69.0, 73.5, 74.4]
    satisfied = [None, 0.6, 0.8, 0.8]
    csv("ch33-livelihood.csv", "year,animals,income", list(zip(years, animals, income)))
    lines = ["livelihood monitoring of the families (synthetic results)",
             "  year   animals   income k u   families satisfied"]
    for y, a, i, s in zip(years, animals, income, satisfied):
        lines.append(f"  {y:4d}   {a:7d}   {i:10.1f}   {'-' if s is None else f'{s * 100:.0f} %':>18s}")
    lines += ["  closeout when incomes are back at the baseline (year 2)",
              "  and stay there (year 3), and when the families agree in",
              "  a final review - closure is evidence, not a date"]
    emit("g_monitoring", lines)


def questions() -> None:
    qs = ["is customary grazing a legal right under the governing law?",
          "does the framework class the fence as economic displacement?",
          "are the families an Indigenous or other protected group under it?",
          "if consultation or consent rules apply, what process and by whom?",
          "who may sign an agreement for the families - elders, all adults?",
          "what grievance and appeal route do they have outside the project?"]
    lines = ["questions the framework and local experts must answer (not this lab)"]
    lines += [f"  {k}. {q}" for k, q in enumerate(qs, 1)]
    lines += ["  the lab can show the impact and the options; it cannot",
              "  decide which rights apply - that needs qualified local",
              "  social and legal expertise, and no universal trigger is",
              "  assumed here"]
    emit("g_questions", lines)


if __name__ == "__main__":
    baseline()
    options()
    monitoring()
    questions()
