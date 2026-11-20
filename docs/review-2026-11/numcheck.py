"""Flag numbers in interpretation paragraphs that do not appear in the included output.

For every include of companion/.../expected/*.txt in a .qmd file, take the text
that follows it up to the end of the enclosing block (next ':::' at line start,
next include, or next heading) and pull out numbers written in [..]{.ltr} spans
or inline math. A number "matches" if some number of the output file (or of the
block's own question text) rounds to it at the number's written precision,
also after scaling by 100, 1/100, 1000, 1/1000.
Output: TSV of file, line, number, sentence snippet.
"""
import re, sys, os, glob, math

ROOT = r"J:\Claude\hybrid wind-solar power plants\Hybrid_Plant_Book"
PDIG = str.maketrans("۰۱۲۳۴۵۶۷۸۹٫٬", "0123456789.,")
INC = re.compile(r'include="(companion/[^"]*expected/[^"]+)"')
NUM = re.compile(r'(?<![\w.\-])(-?\d{1,3}(?:,\d{3})+(?:\.\d+)?|-?\d+(?:\.\d+)?)(?![\w])')
SKIP_CTX = re.compile(r'(?:[A-Z]{1,4}-\d{2,4}|E\d\d|P\d\d|M\d\d|ch\s?\d+|STD-\d+|ISO|IEC|IEEE|NFPA|UL|EN)\s*$')

def nums(text):
    out = []
    for m in NUM.finditer(text):
        s = m.group(1)
        pre = text[max(0, m.start()-8):m.start()]
        if SKIP_CTX.search(pre):
            continue
        try:
            v = float(s.replace(",", ""))
        except ValueError:
            continue
        dec = len(s.split(".")[1]) if "." in s else 0
        out.append((s, v, dec, m.start()))
    return out

def candidates(vals):
    c = set()
    for v in vals:
        for k in (1, 100, 0.01, 1000, 0.001, -1):
            c.add(v * k)
    return c

def matches(v, dec, cands):
    tol = 0.5 * 10 ** (-dec) + 1e-9
    for c in cands:
        if abs(c - v) <= tol:
            return True
        # allow 'about' rounding to 2 significant digits
        if v != 0 and abs(c - v) / abs(v) < 0.02 and dec == 0 and abs(v) >= 20:
            return True
    return False

def span_numbers(par):
    """numbers inside ltr spans and inline math only"""
    bits = re.findall(r'\[([^\[\]]*)\]\{\.ltr\}', par) + re.findall(r'\$([^$]+)\$', par)
    return " ; ".join(bits)

def main():
    files = sorted(glob.glob(os.path.join(ROOT, "chapters", "*", "_*.qmd")))
    files += sorted(glob.glob(os.path.join(ROOT, "chapters", "*.qmd")))
    files += sorted(glob.glob(os.path.join(ROOT, "appendices", "*.qmd")))
    rows = []
    stats = [0, 0, 0]
    for f in files:
        lines = open(f, encoding="utf-8").read().splitlines()
        for i, line in enumerate(lines):
            m = INC.search(line)
            if not m:
                continue
            out_path = os.path.join(ROOT, m.group(1))
            if not os.path.exists(out_path):
                rows.append((f, i + 1, "MISSING-OUTPUT", m.group(1)))
                continue
            out_text = open(out_path, encoding="utf-8", errors="replace").read()
            # block start: look back to the opening ':::' of the example
            j0 = i
            while j0 > 0 and not lines[j0].startswith(":::") and i - j0 < 60:
                j0 -= 1
            pre_text = "\n".join(lines[j0:i]).translate(PDIG)
            # text after the include
            j = i + 1
            if j < len(lines) and lines[j].startswith("```"):
                j += 1
            seg = []
            while j < len(lines) and len(seg) < 40:
                L = lines[j]
                if L.startswith(":::") or INC.search(L) or L.startswith("#"):
                    break
                seg.append((j + 1, L))
                j += 1
            ref_vals = [n[1] for n in nums(out_text)] + [n[1] for n in nums(span_numbers(pre_text))]
            # earlier sentences of the same paragraph also count as references
            cands = candidates(ref_vals)
            stats[0] += 1
            for ln, L in seg:
                t = span_numbers(L.translate(PDIG))
                for s, v, dec, pos in nums(t):
                    if abs(v) < 2 and dec == 0:
                        continue
                    stats[1] += 1
                    if matches(v, dec, cands):
                        continue
                    stats[2] += 1
                    rows.append((os.path.relpath(f, ROOT), ln, s, L.strip()[:160]))
                # numbers written later in the paragraph are also references
                cands |= candidates([n[1] for n in nums(t)])
    with open(sys.argv[1], "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write("\t".join(str(x) for x in r) + "\n")
    print("includes", stats[0], "numbers", stats[1], "unmatched", stats[2])

main()
