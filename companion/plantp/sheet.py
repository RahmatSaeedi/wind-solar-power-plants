"""A very small spreadsheet model and auditor, chapter 5.

A sheet is a dictionary {cell: content}. Content is a number, a text, or a formula
string that starts with "=". Formulas may use + - * / ^, parentheses, cell references
(B7, $B$7), ranges inside SUM / MIN / MAX / AVERAGE (C2:C13), and defined names.

    sh = Sheet({"B2": 60, "B3": 0.85, "B4": "=B2*B3"}, names={"dc_mwp": "B2"})
    sh.value("B4")          # 51.0
    audit(sh)               # list of findings, one string each

The auditor looks for the classic spreadsheet failure modes: numbers typed inside
formulas, references to empty cells, circular references, a formula that breaks the
pattern of its column, a typed number among formulas (an overwritten formula), and
SUM ranges that stop one cell short of a block. Teaching code, not a spreadsheet engine.
"""
from __future__ import annotations

import ast
import re

REF = re.compile(r"\$?([A-Z]{1,2})\$?(\d+)")
RANGE = re.compile(r"\$?([A-Z]{1,2})\$?(\d+):\$?([A-Z]{1,2})\$?(\d+)")
FUNCS = {"SUM": sum, "MIN": min, "MAX": max,
         "AVERAGE": lambda xs: sum(xs) / len(xs)}


class CircularReference(ValueError):
    pass


def col_index(letters: str) -> int:
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n


def col_letters(n: int) -> str:
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def split(cell: str) -> tuple[int, int]:
    m = REF.fullmatch(cell)
    if not m:
        raise ValueError(f"not a cell reference: {cell}")
    return col_index(m.group(1)), int(m.group(2))


def expand(rng: str) -> list[str]:
    m = RANGE.fullmatch(rng)
    c1, r1, c2, r2 = col_index(m.group(1)), int(m.group(2)), col_index(m.group(3)), int(m.group(4))
    return [f"{col_letters(c)}{r}" for c in range(c1, c2 + 1) for r in range(r1, r2 + 1)]


class Sheet:
    def __init__(self, cells: dict, names: dict | None = None):
        self.cells = dict(cells)
        self.names = dict(names or {})

    def is_formula(self, cell: str) -> bool:
        v = self.cells.get(cell)
        return isinstance(v, str) and v.startswith("=")

    def _python(self, formula: str) -> str:
        """Formula text -> Python expression text (refs become _c('B7'), ranges lists)."""
        text = formula[1:]
        for name, target in sorted(self.names.items(), key=lambda kv: -len(kv[0])):
            text = re.sub(rf"\b{name}\b", target, text)
        text = RANGE.sub(lambda m: "[" + ",".join(f"_c('{c}')" for c in expand(m.group(0)))
                         + "]", text)
        text = re.sub(r"(?<![A-Za-z_'])\$?([A-Z]{1,2})\$?(\d+)(?![\d(])",
                      lambda m: f"_c('{m.group(1)}{m.group(2)}')", text)
        return text.replace("^", "**")

    def value(self, cell: str, _stack: tuple = ()):
        if cell in _stack:
            raise CircularReference(" -> ".join(_stack + (cell,)))
        v = self.cells.get(cell)
        if not self.is_formula(cell):
            return 0.0 if v is None or v == "" else v
        expr = self._python(v)
        tree = ast.parse(expr, mode="eval")
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
                                     ast.Call, ast.Name, ast.Load, ast.List, ast.operator,
                                     ast.unaryop)):
                raise ValueError(f"{cell}: unsupported element {type(node).__name__}")
            if isinstance(node, ast.Name) and node.id not in FUNCS and node.id != "_c":
                raise ValueError(f"{cell}: unknown name {node.id}")
        env = dict(FUNCS)
        env["_c"] = lambda c: self.value(c, _stack + (cell,))
        return eval(compile(tree, cell, "eval"), {"__builtins__": {}}, env)

    def references(self, cell: str) -> list[str]:
        if not self.is_formula(cell):
            return []
        return re.findall(r"_c\('([A-Z]{1,2}\d+)'\)", self._python(self.cells[cell]))


# [start: relative]
def relative_form(sheet: Sheet, cell: str) -> str:
    """Formula with each reference written as an offset from the cell (R1C1
    style): copies of one formula down a column all give the same text."""
    col, row = split(cell)
    text = sheet.cells[cell]

    def rel(m):
        c, r = col_index(m.group(1)), int(m.group(2))
        absolute = m.group(0).startswith("$")
        return f"R{r}C{c}" if absolute else f"R[{r - row}]C[{c - col}]"
    return REF.sub(rel, text)
# [end: relative]


def audit(sheet: Sheet, allowed_literals=(0, 1)) -> list[str]:
    findings: list[str] = []
    formulas = [c for c in sheet.cells if sheet.is_formula(c)]
    for c in formulas:
        body = REF.sub("", sheet.cells[c][1:])
        for lit in re.findall(r"(?<![A-Za-z])\d+\.?\d*(?:[eE][-+]?\d+)?", body):
            if float(lit) not in allowed_literals:
                findings.append(f"{c}: number {lit} typed inside the formula")
        for ref in sheet.references(c):
            if sheet.cells.get(ref) in (None, ""):
                findings.append(f"{c}: refers to empty cell {ref}")
        try:
            sheet.value(c)
        except CircularReference as e:
            findings.append(f"{c}: circular reference {e}")
        except ZeroDivisionError:
            findings.append(f"{c}: division by zero (#DIV/0!)")
    by_col: dict[int, list[str]] = {}
    for c in sheet.cells:
        by_col.setdefault(split(c)[0], []).append(c)
    for col, cells in by_col.items():
        cells.sort(key=lambda x: split(x)[1])
        forms = [c for c in cells if sheet.is_formula(c)
                 and not RANGE.search(sheet.cells[c])]          # aggregates are not a pattern
        if len(forms) >= 3:
            pattern = {}
            for c in forms:
                pattern.setdefault(relative_form(sheet, c), []).append(c)
            common = max(pattern, key=lambda k: len(pattern[k]))
            if len(pattern[common]) >= 3:
                rows = [split(c)[1] for c in pattern[common]]
                for k, members in pattern.items():
                    r = split(members[0])[1]
                    if k != common and len(members) == 1 and min(rows) - 1 <= r <= max(rows) + 1:
                        findings.append(f"{members[0]}: breaks the pattern of column "
                                        f"{col_letters(col)} ({sheet.cells[members[0]]})")
                for c in cells:
                    r = split(c)[1]
                    if (not sheet.is_formula(c) and isinstance(sheet.cells[c], (int, float))
                            and min(rows) < r < max(rows)):
                        findings.append(f"{c}: typed number {sheet.cells[c]} among formulas "
                                        "(overwritten formula?)")
    for c in formulas:
        for m in RANGE.finditer(sheet.cells[c]):
            block = expand(m.group(0))
            (c1, _), (c2, r2) = split(block[0]), split(block[-1])
            if c1 != c2:
                continue
            nxt = f"{col_letters(c1)}{r2 + 1}"
            content = sheet.cells.get(nxt)
            holds_data = isinstance(content, (int, float)) or sheet.is_formula(nxt)
            if nxt != c and holds_data:
                findings.append(f"{c}: range {m.group(0)} stops before {nxt}, which holds data")
    return findings
