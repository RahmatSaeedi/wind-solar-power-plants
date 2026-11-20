#!/usr/bin/env python3
"""Render one volume of the print and e-book editions into _volumes/volN/.

    python tools/build_volume.py 2              # volume 2: PDF + EPUB
    python tools/build_volume.py 2 --to pdf     # one format only
    python tools/build_volume.py 1 2            # several volumes, one after the other
    python tools/build_volume.py 2 --no-render  # only write the profile and report pages

The website is always the whole book (tools/build_all.py -> _book/). The PDF
and EPUB editions are split into the volumes listed under `volumes:` in
outline/chapters.yml. This tool writes the scratch profile _quarto-vol.yml
(the volume's parts and chapters, its subtitle, output-dir _volumes/volN and
the `bookvolume` metadata) and runs `quarto render --profile vol`. The filter
theme/volume-xref.lua then prints a reference into another volume as plain
text ("فصلِ ۴، جلدِ ۱") instead of an unresolved "?@sec-...".

This is the Part-end check while the book is being written; the full
build_all.py runs once at the end. Never run it at the same time as another
render (both use .quarto/).
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import shutil
import subprocess
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import check_env  # noqa: E402

PROFILE = os.path.join(ROOT, "_quarto-vol.yml")
FA = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
ORDINAL = {1: "یکم", 2: "دوم", 3: "سوم", 4: "چهارم", 5: "پنجم", 6: "ششم",
           7: "هفتم", 8: "هشتم", 9: "نهم", 10: "دهم"}


def outline() -> dict:
    with open(os.path.join(ROOT, "outline", "chapters.yml"), encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def volume_ranges(out: dict) -> tuple[dict[int, tuple[int, int]], int]:
    """{volume: (first chapter, last chapter)} and the appendix volume."""
    ranges, app_vol = {}, None
    for v in out["volumes"]:
        m = re.match(r"\s*(\d+)\s*-\s*(\d+)", str(v["chapters"]))
        if not m:
            sys.exit(f"build_volume: cannot read the chapter range of volume {v['n']}")
        ranges[int(v["n"])] = (int(m.group(1)), int(m.group(2)))
        if "append" in str(v["chapters"]):
            app_vol = int(v["n"])
    return ranges, app_vol or max(ranges)


def write_profile(n: int) -> list[dict]:
    out = outline()
    ranges, app_vol = volume_ranges(out)
    if n not in ranges:
        sys.exit(f"build_volume: no volume {n} in outline/chapters.yml")
    first, last = ranges[n]
    lines = ["# scratch profile written by tools/build_volume.py -- safe to delete",
             "project:", f"  output-dir: _volumes/vol{n}",
             "book:",
             f'  subtitle: "جلدِ {ORDINAL.get(n, str(n))}: فصل‌های {str(first).translate(FA)}'
             f' تا {str(last).translate(FA)}"',
             "  chapters:", "    - index.qmd"]
    chosen = []
    for part in out["parts"]:
        chs = [c for c in part["chapters"] if first <= int(c["n"]) <= last]
        if not chs:
            continue
        lines.append(f'    - part: "{part["title_fa"]}"')
        lines.append("      chapters:")
        for c in chs:
            lines.append(f"        - chapters/{int(c['n']):02d}-{c['slug']}.qmd")
            chosen.append(c)
    if n == app_vol:
        lines.append("  appendices:")
        lines += [f"    - appendices/{a['id']}-{a['slug']}.qmd"
                  for a in out.get("appendices") or []]
    vmap = ";".join(f"{v}:{a}-{b}" for v, (a, b) in sorted(ranges.items()))
    lines += ["bookvolume:", f"  n: {n}", f'  map: "{vmap}"', f"  appendices: {app_vol}"]
    with open(PROFILE, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    return chosen


def keep_output(n: int, fmt: str) -> None:
    """Quarto empties the output folder on every render, so the second
    format would delete the first: move each result to _volumes/ at once."""
    found = glob.glob(os.path.join(ROOT, "_volumes", f"vol{n}", f"*.{fmt}"))
    if not found:
        print(f"build_volume: no {fmt} in _volumes/vol{n}/")
        return
    dest = os.path.join(ROOT, "_volumes", f"hybrid-plant-book-vol{n}.{fmt}")
    shutil.copy2(found[0], dest)
    print(f"build_volume: kept {os.path.relpath(dest, ROOT)}")


def page_report(n: int) -> None:
    import pymupdf
    pdfs = glob.glob(os.path.join(ROOT, "_volumes", f"hybrid-plant-book-vol{n}.pdf"))
    if not pdfs:
        print(f"build_volume: no PDF for volume {n} in _volumes/")
        return
    doc = pymupdf.open(pdfs[0])
    print(f"\n=== volume {n}: {doc.page_count} pages ({os.path.basename(pdfs[0])}) ===")
    for level, title, page in doc.get_toc():
        if level <= 2:
            print(f"  {'  ' * (level - 1)}p. {page:4d}  {title}")
    unresolved = sum(page.get_text().count("?@") for page in doc)
    print(f"  unresolved references ('?@'): {unresolved}")


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("volumes", nargs="+", type=int)
    ap.add_argument("--to", help="one format only: pdf or epub")
    ap.add_argument("--no-render", action="store_true")
    args = ap.parse_args()
    env = check_env.tex_env()
    quarto = shutil.which("quarto", path=env.get("PATH")) or "quarto"
    for n in args.volumes:
        write_profile(n)
        if not args.no_render:
            formats = [args.to] if args.to else ["pdf", "epub"]
            for fmt in formats:
                cmd = [quarto, "render", "--profile", "vol", "--to", fmt]
                print("$ " + " ".join(["quarto"] + cmd[1:]), flush=True)
                code = subprocess.run(cmd, cwd=ROOT, env=env).returncode
                if code != 0:
                    sys.exit(f"build_volume: quarto render of volume {n} ({fmt}) failed")
                keep_output(n, fmt)
        page_report(n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
