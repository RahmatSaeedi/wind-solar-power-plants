"""Re-evaluate purely numeric equalities written in LaTeX math across the book.

Finds '$...$' and '$$...$$' segments, splits on '=' (also \approx), and for each
adjacent pair (lhs, rhs) where lhs is a pure numeric expression and rhs is a plain
number (optionally followed by a unit), checks lhs against rhs at rhs's precision.
"""
import re, glob, os, math, sys

ROOT = r"J:\Claude\hybrid wind-solar power plants\Hybrid_Plant_Book"
BS = chr(92)


def strip_units(s):
    s = re.sub(r"\\(?:text|mathrm|mathit|operatorname)\{[^{}]*\}", " ", s)
    s = re.sub(r"\\(?:,|;|!|quad|qquad| )", " ", s)
    return s


def to_py(s):
    s = s.strip()
    s = s.replace("\\left", "").replace("\\right", "")
    s = s.replace("\\times", "*").replace("\\cdot", "*").replace("\\div", "/")
    s = s.replace("\\tfrac", "\\frac").replace("\\dfrac", "\\frac")
    # \frac{a}{b}
    for _ in range(6):
        s2 = re.sub(r"\\frac\{([^{}]*)\}\{([^{}]*)\}", r"((\1)/(\2))", s)
        if s2 == s:
            break
        s = s2
    for _ in range(4):
        s = re.sub(r"\\sqrt\{([^{}]*)\}", r"math.sqrt(\1)", s)
    s = re.sub(r"\\ln\b", "math.log", s)
    s = re.sub(r"\\exp\b", "math.exp", s)
    s = re.sub(r"\\log_\{?10\}?", "math.log10", s)
    s = re.sub(r"\^\{([^{}]*)\}", r"**(\1)", s)
    s = re.sub(r"\^(-?\d+(?:\.\d+)?)", r"**\1", s)
    s = s.replace("{", "(").replace("}", ")")
    s = s.replace("\\pi", "math.pi")
    s = re.sub(r"(?<=\d)\s+(?=\d{3}\b)", "", s)  # 17 671 -> 17671
    s = s.replace("−", "-")
    return s


NUMONLY = re.compile(r"^[\d\s\.\*\+\-/\(\)]*$|^.*math\.")
ALLOWED = re.compile(r"^[\d\s\.\*\+\-/\(\)a-z_\.]*$")


def evaluate(expr):
    py = to_py(strip_units(expr))
    if not ALLOWED.match(py):
        return None
    if re.search(r"[a-z]", py.replace("math.sqrt", "").replace("math.log10", "").replace("math.log", "").replace("math.exp", "").replace("math.pi", "")):
        return None
    if not re.search(r"[\*\+/\-]|math\.", py.strip().lstrip("-")):
        return None  # a bare number is not a computation
    try:
        return eval(py, {"math": math, "__builtins__": {}})
    except Exception:
        return None


def rhs_number(s):
    s = strip_units(s).strip()
    s = re.sub(r"(?<=\d)\s+(?=\d{3}\b)", "", s)
    m = re.match(r"^(-?\d+(?:\.\d+)?)\s*(\\%|%|[A-Za-z°\^\{\}\(\)/\s\\]*)$", s)
    if not m:
        return None
    num = m.group(1)
    dec = len(num.split(".")[1]) if "." in num else 0
    pct = "%" in m.group(2)
    return float(num), dec, pct


def main():
    files = sorted(glob.glob(os.path.join(ROOT, "chapters", "**", "*.qmd"), recursive=True))
    files += sorted(glob.glob(os.path.join(ROOT, "appendices", "*.qmd")))
    out = []
    n_checked = 0
    for f in files:
        text = open(f, encoding="utf-8").read()
        lines = text.split("\n")
        segs = []
        for i, L in enumerate(lines):
            for m in re.finditer(r"(?<!\$)\$([^$]+)\$(?!\$)", L):
                segs.append((i + 1, m.group(1)))
        for m in re.finditer(r"\$\$(.*?)\$\$", text, re.S):
            ln = text[:m.start()].count("\n") + 1
            for k, part in enumerate(re.split(r"\\\\", m.group(1))):
                segs.append((ln, part.replace("&", "")))
        for ln, seg in segs:
            parts = re.split(r"=|\\approx", seg)
            for a, b in zip(parts, parts[1:]):
                r = rhs_number(b)
                if r is None:
                    continue
                v = evaluate(a)
                if v is None or isinstance(v, complex):
                    continue
                num, dec, pct = r
                n_checked += 1
                cands = [v, v * 100] if pct else [v]
                tol = 0.5 * 10 ** (-dec) * 1.02 + 1e-12
                ok = any(abs(c - num) <= tol for c in cands)
                # allow 3-significant-figure rounding for large integers
                if not ok and dec == 0 and abs(num) >= 1000:
                    ok = any(abs(c - num) / abs(num) < 0.005 for c in cands)
                if not ok:
                    flat = " ".join(seg.split())
                    out.append(f"{os.path.relpath(f, ROOT)}\t{ln}\t{v:.6g}\t{num}\t{flat[:220]}")
    open(sys.argv[1], "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("checked", n_checked, "mismatches", len(out))


main()
