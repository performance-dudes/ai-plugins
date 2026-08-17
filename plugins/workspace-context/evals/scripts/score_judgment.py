#!/usr/bin/env python3
"""Score the workspace-context skill's setup-judgment suite.

Regime: DETERMINISTIC. Every task resolves to one label, so it is matched
programmatically — a judge would add variance without adding signal.

The object under test is the REAL skill file, read at runtime. There is no copy in
this harness; change the skill and this measures the changed skill.

    python3 score_judgment.py --emit-prompt > /tmp/p.txt
    claude -p "$(cat /tmp/p.txt)" > /tmp/pred.yaml
    python3 score_judgment.py --predictions /tmp/pred.yaml
    python3 score_judgment.py --self-test        # no model call; runs in CI
"""

import argparse, json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
PLUGIN = HERE.parent.parent
CASES = PLUGIN / "evals" / "setup-judgment" / "cases.yaml"
SKILL = PLUGIN / "skills" / "workspace-context" / "SKILL.md"


def load_cases(path=CASES):
    """Minimal reader for this file's fixed, flat shape — dependency-free on purpose."""
    out, section, cur, key = {"classification": [], "rejection": []}, None, None, None
    for raw in path.read_text().splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        m = re.match(r"^(classification|rejection):", raw)
        if m:
            section, cur = m.group(1), None
            continue
        m = re.match(r"^\s*-\s*id:\s*(.+)$", raw)
        if m:
            cur = {"id": m.group(1).strip(), "text": "", "expect": ""}
            out[section].append(cur); key = None
            continue
        if cur is None:
            continue
        m = re.match(r"^\s+(scenario|artefact|expect|reason_key|note):\s*(.*)$", raw)
        if m:
            key, val = m.group(1), m.group(2).strip()
            if key in ("scenario", "artefact"):
                cur["text"] = "" if val in (">-", ">", "|") else val
                key = "text" if val in (">-", ">", "|") else None
            elif key == "expect":
                cur["expect"] = val; key = None
            else:
                key = None
        elif key == "text":
            cur["text"] += (" " if cur["text"] else "") + raw.strip()
    return out


def build_prompt(cases):
    lines = [
        "You are applying a Claude Code skill's rules. Judge ONLY from the skill file",
        "below — do not add requirements it does not state.",
        "", "=== BEGIN SKILL FILE ===", SKILL.read_text(), "=== END SKILL FILE ===", "",
        "PART A — classify each root as `single-repo` or `workspace`:", "",
    ]
    lines += [f"- {c['id']}: {c['text']}" for c in cases["classification"]]
    lines += ["", "PART B — answer `accept` or `reject` for each proposed artefact:", ""]
    lines += [f"- {c['id']}: {c['text']}" for c in cases["rejection"]]
    lines += ["", "Output YAML only, one line per id:  <id>: <label>"]
    return "\n".join(lines)


def parse_predictions(text):
    preds = {}
    for line in text.splitlines():
        m = re.match(r"^\s*-?\s*([\w-]+)\s*:\s*(single-repo|workspace|accept|reject)\s*$",
                     line.strip(), re.I)
        if m:
            preds[m.group(1)] = m.group(2).lower()
    return preds


def score(cases, preds):
    res = {}
    for sec in ("classification", "rejection"):
        ok = wrong = missing = 0
        wrong_ids, missing_ids = [], []
        for c in cases[sec]:
            got = preds.get(c["id"])
            if got is None:
                missing += 1; missing_ids.append(c["id"])
            elif got == c["expect"]:
                ok += 1
            else:
                wrong += 1; wrong_ids.append(f"{c['id']}: expected {c['expect']}, got {got}")
        total = ok + wrong
        res[sec] = {"correct": ok, "wrong": wrong, "missing": missing,
                    "accuracy": round(ok / total, 4) if total else 0.0,
                    "wrong_ids": wrong_ids, "missing_ids": missing_ids}
    return res


def self_test():
    cases, problems = load_cases(), []
    if not SKILL.exists():
        problems.append("skill file missing — the harness would measure nothing")
    if len(cases["classification"]) < 4:
        problems.append("too few classification tasks")
    if not any(c["expect"] == "accept" for c in cases["rejection"]):
        problems.append("no clean case — over-rejection would go unmeasured")
    for sec in cases:
        for c in cases[sec]:
            if not c["text"] or not c["expect"]:
                problems.append(f"task {c['id']} incomplete")
    perfect = {c["id"]: c["expect"] for sec in cases for c in cases[sec]}
    if score(cases, perfect)["classification"]["accuracy"] != 1.0:
        problems.append("scorer does not return 1.0 on a perfect prediction set")
    if score(cases, {})["classification"]["missing"] != len(cases["classification"]):
        problems.append("scorer does not report missing predictions")
    n = sum(len(v) for v in cases.values())
    print(f"  {'✔' if not problems else 'x'} self-test: {n} locked tasks "
          f"({len(cases['classification'])} classification, {len(cases['rejection'])} rejection)")
    for p in problems:
        print(f"  x {p}", file=sys.stderr)
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit-prompt", action="store_true")
    ap.add_argument("--predictions")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    cases = load_cases()
    if a.emit_prompt:
        print(build_prompt(cases)); return 0
    if a.self_test:
        return 1 if self_test() else 0
    if a.predictions:
        r = score(cases, parse_predictions(pathlib.Path(a.predictions).read_text()))
        print(json.dumps(r, indent=2)); return 0
    ap.print_help(); return 2


if __name__ == "__main__":
    sys.exit(main())
