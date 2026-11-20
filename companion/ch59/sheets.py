"""Chapter 59: write the 14 dossier item sheets (chapters/59/_59-k-sheets.qmd)
from the chapters' deliverable sections - decisions, documents, unknowns
and assumptions per item. Run after any chapter changes:

    python -m companion.ch59.sheets
"""
from __future__ import annotations

import re

from companion.ch59 import sources as src

TITLES = {   # short Persian titles of the decisions (from each chapter's decision record)
    1: "خطِ مبنای نیروگاهِ [P]{.ltr}", 2: "پایهٔ مدار و ایمنیِ [DC]{.ltr}",
    3: "شرط‌های کارِ آزمایشگاهیِ فصلِ ۶",
    4: "مدل‌های پروژه", 5: "قراردادهای برگهٔ محاسبه", 6: "بازنگریِ برگهٔ محاسبه",
    7: "وارسیِ مدل‌های ریاضی", 8: "پایهٔ محاسبه‌های انرژی", 9: "استفاده از بستهٔ داده",
    10: "قراردادِ علامت‌ها", 11: "پیشرانهٔ گیربکس‌دار با مبدّلِ کامل",
    12: "ولتاژِ [AC]{.ltr} اینورترها",
    13: "چیدمانِ آرایه", 14: "مبنای شستشو", 15: "مبنای انرژیِ باد", 16: "مبنای منبعِ خورشیدی",
    17: "مبنای منبعِ باد", 18: "چیدمانِ مقدماتی", 19: "مبنای انرژی", 20: "مبنای عدمِ قطعیت",
    21: "خطِ مبنای الزام‌ها", 22: "مبنای معماری", 23: "مبنای باتری", 24: "مبنای کنترل",
    25: "مبنای مالی", 26: "انتخابِ ساختگاه و ادامهٔ توسعه", 27: "نمودارِ تک‌خطی و برقِ داخلی",
    28: "مبنای مدارها", 29: "ترانسفورماتورها و پست", 30: "حفاظت، زمین و صاعقه",
    31: "کیفیتِ برق و خدمات", 32: "مبنای مطالعهٔ شبکه", 33: "عمران و آب", 34: "سازه‌ها",
    35: "حمل", 36: "ایمنی، آتش و اضطرار", 37: "محیطِ زیست و جامعه", 38: "ابزار دقیق و کنترل",
    39: "اسکادا و ارتباطات", 40: "امنیتِ سامانه‌های عملیاتی", 41: "پایشِ عملکرد",
    42: "طراحیِ تفصیلی و اطلاعات", 43: "تدارکات", 44: "کیفیتِ ساخت", 45: "ساخت و پذیرشِ ماژول",
    46: "کیفیتِ قطعه‌های توربین", 47: "بازبینیِ طرح و آزمونِ کارخانهٔ ترانسفورماتور",
    48: "ساخت و پذیرشِ مبدّل", 49: "ساخت و شاهدِ باتری", 50: "کابل، تابلو و پنل",
    51: "ساختِ سازه و ردیاب", 52: "سخت‌افزارِ ابزار، کنتور و شبکه", 53: "ساخت و نصب",
    54: "راه‌اندازی، پذیرش و تحویل", 55: "مبنای بهره‌برداری", 56: "نگهداری و قابلیتِ اطمینان",
    57: "مبنای عمر", 58: "روشِ انطباق", 59: "پروندهٔ ایران", 60: "پروندهٔ افغانستان",
    61: "پروندهٔ تاجیکستان", 62: "مبنای استانداردها",
}

INTRO = {
    1: "پایهٔ همهٔ پرونده: بستهٔ داده با شمارهٔ انتشار، دفترِ الزام‌ها، دفترِ فرض‌ها و دفترِ تغییرها.",
    2: "برنامهٔ اندازه‌گیریِ منبع و کیفیتِ داده: ایستگاه‌ها، دکل و لیدار، آزمون‌های کیفیت و همبستگیِ بلندمدت.",
    3: "قیدهای ساختگاه، پیمایش‌ها، چیدمانِ مقدماتی، ترازِ آب و برنامهٔ نگهداشتِ آن.",
    4: "مدلِ تولید با تلف‌ها، و بیانیهٔ عدمِ قطعیت با [P50]{.ltr} و [P90]{.ltr}.",
    5: "منطقِ معماری و انتخابِ تجهیز: فتوولتائیک، توربین، اینورتر و باتری.",
    6: "نمودارهای تک‌خطیِ اصلی و برقِ داخلی، فهرست‌های بار و جدول‌های تجهیز.",
    7: "پایهٔ عمران، مکانیک، محیطِ زیست، حفاظت‌های اجتماعی، رفاهِ کارگران، سلامت و ایمنیِ جامعه، امنیتِ فیزیکی و اضطرار.",
    8: "برنامهٔ مطالعهٔ شبکه، مرزِ جمع‌آوری و صادرات، پایهٔ پیش‌بینی و اعزام، و دفترِ انطباقِ خدماتِ شبکه.",
    9: "مشخصاتِ خرید و برنامهٔ کیفیتِ هر تجهیز، تا آزمونِ کارخانه.",
    10: "برنامه‌های ساخت، بازرسی، راه‌اندازی و تحویلِ اطلاعاتِ دارایی.",
    11: "روش‌های بهره‌برداری، نگهداری، یدک‌ها و راهبردِ حاکمیتِ دادهٔ دارایی و پیکربندی.",
    12: "پایهٔ قابلیتِ اطمینان، دسترس‌پذیری و نگهداشت‌پذیری، دفترِ تجهیزاتِ بحرانی و برنامهٔ داده و راستی‌آزمایی.",
    13: "اقتصادِ عمر، مدلِ مالی و حالت‌های پایین، دفترِ ریسک، ردپا و رویکردِ پایانِ عمر.",
    14: "پیوست‌های جدای ایران، افغانستان و تاجیکستان برای انطباق و حفاظت‌های زمین و جامعه.",
}


EXTRA = {   # chapters without a basis output: their integrated outputs instead
    2: ["int_statement.txt"], 3: ["int_energy.txt"], 4: ["int_wind.txt"], 5: ["e_register.txt"],
    7: ["i_poc.txt"], 8: ["i_spec.txt"], 9: ["i_budget.txt"],
    10: ["i_accept.txt"], 11: ["i_farm.txt"], 12: ["i_plan.txt"], 13: ["i_longterm.txt"],
    14: ["i_register.txt"], 15: ["i_statement.txt"], 16: ["i_memo.txt"],
    17: ["i_baseline.txt", "d_register.txt"],
}


def fa(x) -> str:
    return str(x).translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))


def ltr_list(ids: list[str], per_line: int = 6) -> str:
    if not ids:
        return "—"
    return "، ".join(f"[{i}]{{.ltr}}" for i in ids)


def main() -> None:
    out = ["## ذ. برگه‌های پرونده {#sec-ch59-k}\n\n",
           "هر بندِ پرونده یک برگه دارد. برگه‌ها را برنامهٔ [sheets]{.ltr} از بخشِ «تحویل‌دادنیِ نیروگاهِ P» فصل‌ها می‌سازد: "
           "تصمیم‌ها با عنوانِ کوتاهشان، سندها و ناشناخته‌ها. هر فصلی که سندی بیفزاید یا ناشناخته‌ای ببندد، "
           "با اجرای دوبارهٔ برنامه در برگه دیده می‌شود. وضعیتِ هر بند از شمارِ ناشناخته‌های بازش می‌آید.\n\n"]
    shown = {}
    for n, title, chs in src.ITEMS:
        docs = sorted({d for c in chs for d in src.records(c)["docs"]})
        unk = sorted({u for c in chs for u in src.records(c)["unknowns"]})
        dec = [int(d[2:]) for d in src.decisions_of(chs)]
        out.append(f"### بندِ {fa(n)}: {INTRO[n].split(':')[0].split('،')[0].rstrip('.')} {{#sec-ch59-k-{n}}}\n\n")
        out.append(INTRO[n] + f" فصل‌ها: {'، '.join(fa(c) for c in chs)}.\n\n")
        out.append("| تصمیم | عنوان | فصل |\n|----------|------------------------------|----------|\n")
        for k in dec:
            out.append(f"| [D-{k:03d}]{{.ltr}} | {TITLES[k]} | {fa(src.DECISION_CH[k])} |\n")
        out.append(f"\n: تصمیم‌های بندِ {fa(n)} {{#tbl-ch59-k-{n}}}\n\n")
        out.append(f"**سندها ({fa(len(docs))}):** {ltr_list(docs)}\n\n")
        out.append(f"**ناشناخته‌های نام‌برده ({fa(len(unk))}):** {ltr_list(unk)}\n\n")
        verdict = ("بی ناشناختهٔ نام‌برده" if not unk else
                   "با شرط: ناشناخته‌ها صاحب و تاریخ دارند" if len(unk) <= 10 else
                   "با شرط‌های زیاد: ناشناخته‌ها پیش از دروازهٔ بعد اولویت‌بندی می‌شوند")
        out.append(f"**وضعیت:** {verdict}.\n\n")
        bases = []
        for c in chs:
            for name in EXTRA.get(c, []):
                f = src.ROOT / "companion" / f"ch{c:02d}" / "expected" / name
                if f.exists():
                    bases.append((c, f"companion/ch{c:02d}/expected/{name}"))
            for name in ("int_basis.txt", "i_basis.txt"):
                f = src.ROOT / "companion" / f"ch{c:02d}" / "expected" / name
                if f.exists():
                    bases.append((c, f"companion/ch{c:02d}/expected/{name}"))
                    break
        again = sorted({c for c, _ in bases if c in shown})
        bases = [(c, path) for c, path in bases if c not in shown]
        for c, _ in bases:
            shown[c] = n
        if again:
            out.append("**مبنای فصل‌هایی که در بندِ پیشین آمد:** "
                       + "، ".join(f"فصلِ {fa(c)} (بندِ {fa(shown[c])})" for c in again) + ".\n\n")
        if bases:
            out.append("**مبنای تصمیم‌ها، از خروجیِ آزموده‌شدهٔ هر فصل:** "
                       + "، ".join(f"فصلِ {fa(c)}" for c in dict.fromkeys(c for c, _ in bases))
                       + ".\n\n")
            for c, path in bases:
                out.append(f"```{{.text include=\"{path}\"}}\n```\n\n")
    out.append("::: {.callout-tip}\n## خودآزمایی «ذ»\n"
               "1. برگه‌ها از کجا ساخته می‌شوند و چرا دستی نوشته نمی‌شوند؟\n"
               "2. کدام بندها بیش از ده ناشناخته دارند؟\n"
               "3. یک سند را از برگه تا فصلِ خودش دنبال کنید.\n:::\n")
    p = src.ROOT / "chapters" / "59" / "_59-k-sheets.qmd"
    p.write_text("".join(out), encoding="utf-8", newline="\n")
    print("sheets written:", len(src.ITEMS))
    findings()


def findings() -> None:
    """The register of findings that chapters sent back to other chapters
    (chapters that end their integrated example with that list)."""
    rows = []
    for n in range(1, 59):
        t = src.chapter_text(n)
        m = re.search(r"یافته‌هایی که به فصل‌های دیگر برمی‌گردند:\s*\n\n((?:- \*\*[^\n]+\n)+)", t)
        if m:
            for to, text in re.findall(r"- \*\*([^*]+)\*\*\s*([^\n]+)", m.group(1)):
                rows.append((n, to.rstrip(":").strip(), text.strip()))
    by_from = {}
    for n, _, _ in rows:
        by_from[n] = by_from.get(n, 0) + 1
    out = ["## ر. دفترِ یافته‌های میانِ فصل‌ها {#sec-ch59-l}\n\n",
           f"فصل‌های پایانیِ کتاب هر کدام مثالِ یکپارچه‌شان را با فهرستِ «یافته‌هایی که به فصل‌های دیگر برمی‌گردند» "
           f"بستند. برنامهٔ [sheets]{{.ltr}} این فهرست‌ها را می‌خواند: {fa(len(rows))} یافته از "
           f"{fa(len(by_from))} فصل. هر یافته تصمیمی را در فصلی پیشین باز می‌کند و باید از مسیرِ تغییر بگذرد "
           "(@sec-ch38). یافته‌ای که پاسخ نگیرد، در پرونده ناسازگاریِ آشکار می‌ماند.\n\n",
           "| از فصل | به | یافته |\n|----------|------------------|----------------------------------------|\n"]
    for n, to, text in rows:
        out.append(f"| {fa(n)} | {to} | {text} |\n")
    out.append("\n: دفترِ یافته‌هایی که فصل‌ها به فصل‌های پیشین برگرداندند {#tbl-ch59-findings}\n\n")
    out.append("::: {#exm-ch59-findings}\n## یافته‌ها، مسیرِ بازگشت\n\n"
               "**پرسش.** کدام فصل‌ها بیشترین یافته را به فصل‌های پیشین برگرداندند و با این یافته‌ها چه می‌شود؟\n\n"
               "**پاسخ.** " + "، ".join(f"فصلِ {fa(k)}: {fa(v)}" for k, v in sorted(by_from.items()))
               + ".\n\n**تفسیر.** هر یافته یک درخواستِ تغییر است: سندی که باید بازنگری شود، تصمیمی که باید دوباره گرفته شود، "
               "یا عددی که در مدلِ دیگری تغییر می‌کند. پرونده آن‌ها را در دفترِ تغییرها (بندِ ۱) نگه می‌دارد. "
               "پاسخِ هر یافته پیش از دروازهٔ بعد ثبت می‌شود: پذیرفته، رد شده با دلیل، یا به تعویق افتاده با تاریخ.\n:::\n\n")
    p = src.ROOT / "chapters" / "59" / "_59-l-findings.qmd"
    p.write_text("".join(out), encoding="utf-8", newline="\n")
    print("findings written:", len(rows))


if __name__ == "__main__":
    main()
