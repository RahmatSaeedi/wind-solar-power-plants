"""Generate appendices/A-glossary-notation.qmd from glossary/terms-fa-en.csv
and glossary/notation.md (run from the project root)."""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
rows = list(csv.DictReader(open(ROOT / "glossary/terms-fa-en.csv", encoding="utf-8")))

ALPHA = "آابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی"
NAMES = {"آ": "الف", "ا": "الف", "ب": "ب", "پ": "پ", "ت": "ت", "ث": "ث", "ج": "ج",
         "چ": "چ", "ح": "ح", "خ": "خ", "د": "د", "ذ": "ذ", "ر": "ر", "ز": "ز", "ژ": "ژ",
         "س": "س", "ش": "ش", "ص": "ص", "ض": "ض", "ط": "ط", "ظ": "ظ", "ع": "ع", "غ": "غ",
         "ف": "ف", "ق": "ق", "ک": "ک", "گ": "گ", "ل": "ل", "م": "م", "ن": "ن", "و": "و",
         "ه": "ه", "ی": "ی"}
NORM = {"أ": "ا", "إ": "ا", "ۀ": "ه", "ة": "ه", "ئ": "ی", "ؤ": "و", "ي": "ی", "ك": "ک"}
DROP = "\u200c\u0650\u0654\u064b\u064c\u064d\u064e\u064f\u0651\u0652«»"


def norm(s: str) -> str:
    s = "".join(NORM.get(c, c) for c in s if c not in DROP)
    return s.strip()


def key(s: str):
    out = []
    for c in norm(s):
        if c in ALPHA:
            out.append((1, ALPHA.index(c)))
        elif c == " ":
            out.append((0, 0))
        else:
            out.append((2, ord(c.lower())))
    return out


def first_letter(s: str) -> str:
    for c in norm(s):
        if c in NAMES:
            return NAMES[c]
        if c.isalnum():
            return "LATIN"
    return "LATIN"


def esc_en(s: str) -> str:
    for a, b in [("\\", "\\\\"), ("[", "\\["), ("]", "\\]"), ("*", "\\*"), ("_", "\\_"),
                 ("|", "\\|"), ("<", "\\<"), (">", "\\>"), ("#", "\\#"), ("$", "\\$"),
                 ("`", "\\`")]:
        s = s.replace(a, b)
    return s


LAT = re.compile(r"[A-Za-z][A-Za-z0-9./+&-]*(?: [A-Za-z0-9][A-Za-z0-9./+&-]*)*")


def fa_cell(s: str) -> str:
    s = s.replace("|", "/")
    return LAT.sub(lambda m: f"[{esc_en(m.group(0))}]{{.ltr}}", s)


def fa_digits(n: str) -> str:
    return n.translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))


out = ["""# واژه‌نامهٔ فارسی–انگلیسی، نمادها و کوته‌نوشت‌ها {#sec-app-a}

این پیوست از دو پروندهٔ کتاب ساخته می‌شود: واژه‌نامهٔ کنترل‌شده (`glossary/terms-fa-en.csv`) و دفترِ نمادها (`glossary/notation.md`). هر واژه یک بار در این دو پرونده تعریف شده و همه‌جای کتاب همان به کار رفته است. ستونِ «فصل» شمارهٔ فصلی است که واژه نخستین بار در آن آمده. اگر دو صورت برای یک مفهوم دیده شود، در پاکسازیِ پایانیِ کتاب یکی می‌شوند.

## قراردادهای نگارش {#sec-app-a-conventions}

- فارسیِ فنیِ معیارِ ایران، با کسرهٔ اضافه‌ای که خواندن را روشن می‌کند (مانندِ «افتِ ولتاژ») و نیم‌فاصله در جای خود.
- اصطلاحِ انگلیسی در نخستین کاربرد در پرانتز می‌آید. نام‌های لاتین، شناسه‌ها و یکاها چپ‌به‌راست نوشته می‌شوند.
- شمارش‌های سادهٔ متن با رقمِ فارسی‌اند و کمیت‌های دارای یکا با رقمِ لاتین و یکای [SI]{.ltr}، مانندِ [60 MW]{.ltr}.
- نمادِ کمیت مورب و یکا ایستاده است. زیرنویسی که واژه است ایستاده و زیرنویسی که شمارنده است مورب.
- گونه‌های دری و تاجیکی فقط وقتی آمده‌اند که درستی‌شان روشن بود (@sec-app-a-variants).

## واژه‌نامهٔ فارسی به انگلیسی {#sec-app-a-fa}

"""]

by_letter = {}
for r in sorted(rows, key=lambda r: key(r["fa"])):
    by_letter.setdefault(first_letter(r["fa"]), []).append(r)
order = [NAMES[c] for c in ALPHA]
seen = []
for name in order + ["LATIN"]:
    if name in seen or name not in by_letter:
        continue
    seen.append(name)
    title = "واژه‌هایی که با حرفِ لاتین آغاز می‌شوند" if name == "LATIN" else f"حرفِ «{name}»"
    out.append(f"### {title}\n\n")
    out.append("| فارسی | انگلیسی | فصل |\n|------------------------------|----------------------------------------|------|\n")
    for r in by_letter[name]:
        out.append(f"| {fa_cell(r['fa'])} | [{esc_en(r['en'])}]{{.ltr}} | "
                   f"{fa_digits(r['first_chapter'])} |\n")
    out.append("\n")

out.append("## نمایهٔ انگلیسی به فارسی {#sec-app-a-en}\n\n"
           "برای یافتنِ معادلِ فارسیِ یک اصطلاحِ انگلیسی. ترتیب الفبایی انگلیسی است.\n\n")
by_en = {}
for r in sorted(rows, key=lambda r: r["en"].lower()):
    c = r["en"][0].upper()
    by_en.setdefault(c if c.isalpha() else "#", []).append(r)
for c in sorted(by_en):
    out.append(f"### [{c}]{{.ltr}}\n\n")
    out.append("| انگلیسی | فارسی |\n|----------------------------------------|------------------------------|\n")
    for r in by_en[c]:
        out.append(f"| [{esc_en(r['en'])}]{{.ltr}} | {fa_cell(r['fa'])} |\n")
    out.append("\n")

# variants
var = [r for r in rows if r["dari"] or r["tajik"]]
out.append("## گونه‌های دری و تاجیکی {#sec-app-a-variants}\n\n"
           "این گونه‌ها برای خوانندگانِ افغانستان و تاجیکستان آمده‌اند و فقط وقتی ثبت شده‌اند که درستی‌شان روشن بود. "
           "صورتِ تاجیکی به خطِ سیریلیک است و صورتِ فارسیِ آن در پرانتز آمده.\n\n"
           "| فارسیِ ایران | دری | تاجیکی | انگلیسی |\n|--------------------|--------------------|--------------------|--------------------|\n")
for r in var:
    tj = r["tajik"]
    m = re.match(r"^(.*?)\s*\((.*)\)$", tj)
    tj_cell = (f"[{esc_en(m.group(1))}]{{.ltr}} ({m.group(2)})" if m
               else (f"[{esc_en(tj)}]{{.ltr}}" if tj else "–"))
    out.append(f"| {fa_cell(r['fa'])} | {fa_cell(r['dari']) or '–'} | {tj_cell} | "
               f"[{esc_en(r['en'])}]{{.ltr}} |\n")
out.append("\n: گونه‌های دری و تاجیکیِ واژه‌ها {#tbl-app-a-variants}\n\n")

# abbreviations
ab = {}
for r in rows:
    for m in re.finditer(r"\(([A-Z][A-Za-z0-9/&-]{1,11})\)", r["en"]):
        a = m.group(1)
        if sum(ch.isupper() for ch in a) >= 2:
            ab.setdefault(a, (re.sub(r"\s*\(" + re.escape(a) + r"\)", "", r["en"]), r["fa"]))
    n = r["notes"].strip()
    if re.fullmatch(r"[A-Z][A-Z0-9/&-]{1,9}", n):
        ab.setdefault(n, (r["en"], r["fa"]))
out.append("## کوته‌نوشت‌ها {#sec-app-a-abbrev}\n\n"
           "کوته‌نوشت‌های انگلیسی که در متن و برنامه‌ها آمده‌اند، با صورتِ کامل و معادلِ فارسی.\n\n"
           "| کوته‌نوشت | صورتِ کامل | فارسی |\n|------------|------------------------------|------------------------------|\n")
for a in sorted(ab, key=str.lower):
    en, fa = ab[a]
    out.append(f"| [{esc_en(a)}]{{.ltr}} | [{esc_en(en)}]{{.ltr}} | {fa_cell(fa)} |\n")
out.append("\n: کوته‌نوشت‌ها {#tbl-app-a-abbrev}\n\n")

# symbols: RTL tables (symbol in math; meaning and unit as English LTR text
# with the LaTeX turned into plain Unicode, since math may not sit inside an
# LTR span and an LTR block mis-places tables in the PDF)
GREEK = {"alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε",
         "varepsilon": "ε", "zeta": "ζ", "eta": "η", "theta": "θ", "vartheta": "ϑ",
         "kappa": "κ", "lambda": "λ", "mu": "μ", "nu": "ν", "xi": "ξ", "pi": "π",
         "rho": "ρ", "sigma": "σ", "tau": "τ", "phi": "φ", "varphi": "φ", "chi": "χ",
         "psi": "ψ", "omega": "ω", "Gamma": "Γ", "Delta": "Δ", "Theta": "Θ",
         "Lambda": "Λ", "Sigma": "Σ", "Phi": "Φ", "Psi": "Ψ", "Omega": "Ω"}
SYMS = {"times": "×", "cdot": "·", "le": "≤", "leq": "≤", "ge": "≥", "geq": "≥",
        "approx": "≈", "pm": "±", "infty": "∞", "partial": "∂", "sum": "Σ",
        "mid": "|", "vert": "|", "circ": "°", "to": "→", "propto": "∝", "sim": "~",
        "ldots": "...", "dots": "...", "neq": "≠", "in": "∈", "angle": "∠",
        "prime": "′", "ast": "*", "star": "*", "min": "min", "max": "max",
        "ln": "ln", "log": "log", "exp": "exp", "sin": "sin", "cos": "cos",
        "tan": "tan", "Pr": "Pr", "lvert": "|", "rvert": "|", "lVert": "‖",
        "rVert": "‖", "hbar": "ħ", "ell": "ℓ", "nabla": "∇", "int": "∫",
        "sqrt": "√", "langle": "⟨", "rangle": "⟩", "dagger": "†"}


def plain(m: str) -> str:
    """LaTeX math -> readable plain text (approximate, for table cells)."""
    s = m
    for _ in range(4):
        s = re.sub(r"\\(?:text|mathrm|mathbf|mathsf|mathit|operatorname|textrm|"
                   r"boldsymbol|mathcal)\{([^{}]*)\}", r"\1", s)
        s = re.sub(r"\\(?:bar|overline)\{([^{}]*)\}", lambda m: m.group(1) + "\u0304", s)
        s = re.sub(r"\\(?:hat|widehat)\{([^{}]*)\}", lambda m: m.group(1) + "\u0302", s)
        s = re.sub(r"\\(?:dot)\{([^{}]*)\}", lambda m: m.group(1) + "\u0307", s)
        s = re.sub(r"\\(?:tilde|widetilde)\{([^{}]*)\}", lambda m: m.group(1) + "\u0303", s)
        s = re.sub(r"\\[dt]?frac\{([^{}]*)\}\{([^{}]*)\}", r"(\1)/(\2)", s)
        s = re.sub(r"\\sqrt\{([^{}]*)\}", r"√(\1)", s)
    s = re.sub(r"\\(?:bar|hat|dot|tilde)\s*([A-Za-z])", lambda m: m.group(1) + "\u0304", s)
    s = re.sub(r"\\([A-Za-z]+)", lambda mm: GREEK.get(mm.group(1),
               SYMS.get(mm.group(1), "")), s)
    s = s.replace("\\,", " ").replace("\\ ", " ").replace("\\;", " ").replace("\\!", "")
    s = s.replace("\\{", "{").replace("\\}", "}").replace("\\%", "%").replace("\\|", "‖")
    sup = str.maketrans("0123456789-+", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺")
    s = re.sub(r"\^\{([0-9+-]+)\}", lambda m: m.group(1).translate(sup), s)
    s = re.sub(r"\^([0-9])", lambda m: m.group(1).translate(sup), s)
    s = re.sub(r"\^\{([^{}]*)\}", r"^(\1)", s)
    s = re.sub(r"_\{([^{}]*)\}", r"\1", s)
    s = re.sub(r"_(\S)", r"\1", s)
    s = s.replace("{", "").replace("}", "")
    return re.sub(r"\s+", " ", s).strip()


def esc_plain(s: str) -> str:
    """Escape for an LTR span without backslashes (the lint forbids them):
    square brackets become parentheses, markup characters are dropped."""
    s = s.replace("[", "(").replace("]", ")").replace("*", "×").replace("`", "")
    s = s.replace("_", " ").replace("|", "/").replace("<", "‹").replace(">", "›")
    s = s.replace("#", "No. ").replace("$", "").replace("\\", "")
    return s


def ltr_text(t: str) -> str:
    """English text with $..$ math -> one LTR span of plain text."""
    t = re.sub(r"\$([^$]*)\$", lambda mm: plain(mm.group(1)), t).strip()
    if re.fullmatch(r"\d+", t):
        return fa_digits(t)
    return f"[{esc_plain(t)}]{{.ltr}}" if t and t not in ("–", "-") else "–"


def sym_cell(t: str) -> str:
    t = t.strip()
    t = re.sub(r"\$([^$]*)\$", lambda mm: "$" + mm.group(1).replace("|", r"\vert{}") + "$", t)
    # text outside math (e.g. "FF", "PR") goes LTR
    parts = re.split(r"(\$[^$]*\$)", t)
    return "".join(p if p.startswith("$") else
                   (f"[{esc_en(p.strip())}]{{.ltr}}" if p.strip(" ,;") else p)
                   for p in parts)


note = (ROOT / "glossary/notation.md").read_text(encoding="utf-8")
body = []
notes = []
for ln in note.splitlines():
    if ln.startswith("## "):
        if notes:
            body += ["", "یادداشت‌ها:", ""] + notes + [""]
            notes = []
        title = ln[3:].strip()
        body += ["", f"**{ltr_text(title)}**", "",
                 "| نماد | معنا | یکا | فصل |",
                 "|--------------------|----------------------------------------|--------------|------|"]
        continue
    if ln.startswith("|") and not ln.startswith("| Symbol") and not ln.startswith("|---"):
        cells = [c for c in re.split(r"(?<!\\) \| ", ln.strip().strip("|").strip())]
        if len(cells) < 4:
            continue
        sym, meaning, unit, first = cells[0], cells[1], cells[2], cells[3]
        lead = re.match(r"\s*(\d+)", first)        # chapter number only; the
        first = lead.group(1) if lead else first   # notes keep the detail
        body.append(f"| {sym_cell(sym)} | {ltr_text(meaning)} | {ltr_text(unit)} | "
                    f"{ltr_text(first)} |")
        continue
    if ln.startswith("- "):
        notes.append(f"- {ltr_text(ln[2:])}")
        continue
if notes:
    body += ["", "یادداشت‌ها:", ""] + notes
out.append("## نمادها و نمادگذاریِ کتاب {#sec-app-a-symbols}\n\n"
           "دفترِ نمادهای کتاب به انگلیسی نگه داشته می‌شود، چون نمادها در برنامه‌های همراه هم همان‌اند. "
           "هر نماد در هر فصل یک معنا دارد. جایی که یک حرف در دو فصل دو معنا گرفته، یادداشتِ زیرِ جدولِ آن فصل مرز را می‌گوید. "
           "در ستونِ معنا، رابطه‌ها به صورتِ متنِ ساده آمده‌اند. صورتِ دقیقِ هر رابطه در فصلِ نخستین کاربردِ آن است. "
           "یکاها [SI]{.ltr} هستند (@sec-app-b).\n\n")
out.append("\n".join(body).strip() + "\n")

p = ROOT / "appendices/A-glossary-notation.qmd"
p.write_text("".join(out), encoding="utf-8", newline="\n")
print("rows", len(rows), "letters", len(seen), "abbrev", len(ab), "lines", sum(1 for _ in out))
