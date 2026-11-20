#!/usr/bin/env python3
"""Check that no topic of the book plan has been skipped.

    python tools/check_coverage.py          # all chapters
    python tools/check_coverage.py 1 6      # only these chapters
    python tools/check_coverage.py --list 6 # print the chapter's items and where each is covered

outline/coverage.yml lists, per chapter, every item the plan
(../Hybrid_Wind_Solar_Power_Plant_Book_Plan_Handoff.md) requires:

    chapters:
      6:
        - {id: ch06-b1, kind: bullet,    text: "charge, current, ...", sections: [sec-ch06-a-ohm]}
        - {id: ch06-A,  kind: blueprint, text: "Circuit foundations",  sections: [sec-ch06-a]}
        - {id: ch06-x1, kind: audit,     text: "Manufacturing: N/A ...", sections: [sec-ch06-mfg]}

kind: bullet (chapter bullet), blueprint (lettered item A, B, ...), example
(a worked example / lab / case the plan names), audit (a cell of the
six-dimension table), pattern (a part of the standard chapter pattern).

Rules:
  * a chapter whose status in outline/chapters.yml is `written` or `verified`
    must have a coverage list, and every item must name at least one section
    label that exists in the chapter's sources      -> otherwise exit 1
  * for chapters still `planned` / `drafting` the same problems are reported
    as information only
  * every lettered blueprint item (A, B, C ...) the handoff gives a chapter
    must have a `blueprint` item chNN-X in the coverage list (a chapter can
    otherwise pass with a letter folded into another section)
"""
from __future__ import annotations

import argparse
import os
import re
import sys

import yaml

import booklib

COVERAGE = os.path.join(booklib.ROOT, "outline", "coverage.yml")
KINDS = {"bullet", "blueprint", "example", "audit", "pattern"}
HANDOFF = os.path.join(os.path.dirname(booklib.ROOT),
                       "Hybrid_Wind_Solar_Power_Plant_Book_Plan_Handoff.md")


def handoff_letters() -> dict[int, list[str]]:
    """{chapter: [A, B, ...]} from the handoff's blueprint section."""
    if not os.path.exists(HANDOFF):
        return {}
    with open(HANDOFF, encoding="utf-8") as fh:
        text = fh.read()
    parts = re.split(r"^### Chapter (\d+) ", text, flags=re.M)
    out = {}
    for k in range(1, len(parts), 2):
        body = parts[k + 1].split("\n## ")[0]
        out[int(parts[k])] = re.findall(r"^- \*\*([A-Z])\. ", body, flags=re.M)
    return out


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("chapters", nargs="*", type=int)
    ap.add_argument("--list", action="store_true", help="print every item and its sections")
    args = ap.parse_args()

    with open(COVERAGE, encoding="utf-8") as fh:
        coverage = (yaml.safe_load(fh) or {}).get("chapters") or {}
    outline = booklib.load_outline()
    letters = handoff_letters()
    if not letters:
        print(f"note: handoff not found ({HANDOFF}); blueprint letters not checked")
    all_labels = {label for path in booklib.all_source_files(outline)
                  for label, _ in booklib.labels_in(path)}

    failures = 0
    for ch in booklib.chapters(outline):
        n = int(ch["n"])
        if args.chapters and n not in args.chapters:
            continue
        done = ch.get("status") in ("written", "verified")
        items = coverage.get(n) or []
        problems = []
        if not items:
            problems.append("no coverage list")
        seen = set()
        for item in items:
            ident = item.get("id", "?")
            if ident in seen:
                problems.append(f"{ident}: duplicate id")
            seen.add(ident)
            if item.get("kind") not in KINDS:
                problems.append(f"{ident}: kind must be one of {sorted(KINDS)}")
            sections = item.get("sections") or []
            if not sections:
                problems.append(f"{ident}: not mapped to any section -- {item.get('text', '')[:70]}")
            for label in sections:
                if label not in all_labels:
                    problems.append(f"{ident}: label @{label} does not exist in the sources")
        have = {m.group(1) for i in items if i.get("kind") == "blueprint"
                for m in [re.match(rf"ch0*{n}-([A-Z])$", i.get("id", ""))] if m}
        for letter in letters.get(n, []):
            if letter not in have:
                problems.append(f"ch{n:02d}-{letter}: blueprint {letter} of the handoff "
                                "has no coverage item")
        mapped = sum(1 for i in items if i.get("sections")
                     and all(s in all_labels for s in i["sections"]))
        state = "FAIL" if (problems and done) else ("todo" if problems else "ok")
        if state != "todo" or args.chapters:
            print(f"ch {n:2d} [{ch.get('status', '?'):8s}] {mapped:3d}/{len(items):3d} items covered  {state}")
        if problems and (done or args.chapters):
            for p in problems[:40]:
                print("      " + p)
            if len(problems) > 40:
                print(f"      ... and {len(problems) - 40} more")
        if problems and done:
            failures += 1
        if args.list:
            for item in items:
                print(f"      {item['id']:10s} {item['kind']:9s} -> {', '.join(item.get('sections') or ['-'])}")

    written = [c for c in booklib.chapters(outline) if c.get("status") in ("written", "verified")]
    print(f"\n{len(written)} of {len(booklib.chapters(outline))} chapters written; "
          f"{failures} with coverage failures")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
