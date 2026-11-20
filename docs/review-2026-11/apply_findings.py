"""Review and apply adversarial-review findings.

  python apply_findings.py list  TA            # compact table of one reviewer's findings
  python apply_findings.py check TA            # validate old-string uniqueness
  python apply_findings.py apply accept.txt    # apply accepted ids (one per line, optional
                                               #   override lines: ID<TAB>new-text)
Backups go to scratchpad/bak_adv/<relpath> (first copy wins).
"""
import json, os, sys, shutil, glob

ROOT = r"J:\Claude\hybrid wind-solar power plants\Hybrid_Plant_Book"
SP = os.path.dirname(os.path.abspath(__file__))
BAK = os.path.join(SP, "bak_adv")


def load(tag=None):
    out = []
    for f in sorted(glob.glob(os.path.join(SP, "findings", "*.jsonl"))):
        if tag and os.path.basename(f) != tag + ".jsonl":
            continue
        for n, line in enumerate(open(f, encoding="utf-8"), 1):
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError as e:
                print("BAD JSON", f, n, e)
                continue
            out.append(d)
    return out


def target(d):
    return os.path.join(ROOT, d["file"].replace("/", os.sep))


def status(d):
    if not d.get("old"):
        return "no-old"
    p = target(d)
    if not os.path.exists(p):
        return "no-file"
    text = open(p, encoding="utf-8").read()
    if d.get("row"):
        lines = [l for l in text.split("\n") if l.startswith(d["row"] + ",")]
        if len(lines) != 1:
            return "row?"
        c = lines[0].count(d["old"])
    else:
        c = text.count(d["old"])
    return "ok" if c == 1 else f"count={c}"


def cmd_list(tag):
    for d in load(tag):
        if d.get("id", "").endswith("summary"):
            print(d["id"], "summary:", json.dumps({k: v for k, v in d.items() if k != "id"},
                                                    ensure_ascii=False)[:600])
            continue
        print(f'{d["id"]} [{d.get("severity")}/{d.get("category")}/{d.get("confidence")}] '
              f'{d.get("file")}:{d.get("line", d.get("row", ""))} {status(d)}')
        print("   why:", d.get("why", "")[:400])
        print("   ev :", str(d.get("evidence", ""))[:300])
        if d.get("old"):
            print("   old:", d["old"][:300].replace("\n", " / "))
            print("   new:", d["new"][:300].replace("\n", " / "))


def backup(p):
    rel = os.path.relpath(p, ROOT)
    b = os.path.join(BAK, rel)
    if not os.path.exists(b):
        os.makedirs(os.path.dirname(b), exist_ok=True)
        shutil.copy2(p, b)


def cmd_apply(listfile):
    allf = {d["id"]: d for d in load()}
    wanted = []
    for line in open(listfile, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip() or line.startswith("#"):
            continue
        if "\t" in line:
            i, new = line.split("\t", 1)
            wanted.append((i.strip(), new))
        else:
            wanted.append((line.strip(), None))
    done = 0
    for i, new in wanted:
        d = allf[i]
        p = target(d)
        st = status(d)
        if st != "ok":
            print("SKIP", i, st)
            continue
        backup(p)
        text = open(p, encoding="utf-8", newline="").read()
        rep = d["new"] if new is None else new
        old = d["old"]
        if "\r\n" in text:
            old = old.replace("\r\n", "\n").replace("\n", "\r\n")
            rep = rep.replace("\r\n", "\n").replace("\n", "\r\n")
        d = dict(d, old=old)
        if d.get("row"):
            parts = text.split("\n")
            k = [n for n, l in enumerate(parts) if l.startswith(d["row"] + ",")][0]
            assert parts[k].count(d["old"]) == 1
            parts[k] = parts[k].replace(d["old"], rep)
            text = "\n".join(parts)
        else:
            assert text.count(d["old"]) == 1
            text = text.replace(d["old"], rep)
        open(p, "w", encoding="utf-8", newline="").write(text)
        done += 1
        print("APPLIED", i)
    print("applied", done, "of", len(wanted))


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "list":
        cmd_list(sys.argv[2] if len(sys.argv) > 2 else None)
    elif c == "check":
        for d in load(sys.argv[2] if len(sys.argv) > 2 else None):
            print(d.get("id"), status(d))
    elif c == "apply":
        cmd_apply(sys.argv[2])
