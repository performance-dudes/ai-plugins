#!/usr/bin/env python3
"""Knowledge suite for the image-toolkit skill — deterministic, stdlib only.

The object under test is the REAL skill: SKILL.md plus every file in references/,
read at run time. No copy lives in this harness.

    python3 score_knowledge.py --self-test                  # no model, runs in CI
    python3 score_knowledge.py --emit-prompt > prompt.txt   # skill + tasks
    python3 score_knowledge.py --emit-prompt --baseline     # tasks only, NO skill
    python3 score_knowledge.py --predictions t1.txt t2.txt t3.txt   # N trials

`run.sh` next to this directory drives the cold agent and the baseline.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import statistics
import sys

HERE = pathlib.Path(__file__).resolve().parent
PLUGIN = HERE.parent.parent
SKILL_DIR = PLUGIN / "skills" / "image-toolkit"
CASES = HERE.parent / "knowledge" / "cases.yaml"


def _unquote(s: str) -> str:
    s = s.strip()
    return s[1:-1] if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'" else s


def load_cases(path: pathlib.Path = CASES) -> list[dict]:
    """Minimal reader for this file's fixed, flat shape — dependency-free on purpose."""
    cases, cur, folding = [], None, False
    for raw in path.read_text().splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        m = re.match(r"^\s*-\s*id:\s*(.+)$", raw)
        if m:
            cur = {"id": m.group(1).strip(), "axis": "", "question": "", "options": [], "expect": ""}
            cases.append(cur); folding = False
            continue
        if cur is None:
            continue
        m = re.match(r"^\s+(axis|question|options|expect|note):\s*(.*)$", raw)
        if m:
            key, val = m.group(1), m.group(2).strip()
            folding = False
            if key == "question":
                if val in (">-", ">", "|"):
                    folding = True
                else:
                    cur["question"] = val
            elif key == "options":
                inner = val.strip()[1:-1]
                cur["options"] = [_unquote(o) for o in inner.split(",") if o.strip()]
            elif key in ("axis", "expect"):
                cur[key] = _unquote(val)
        elif folding:
            cur["question"] += (" " if cur["question"] else "") + raw.strip()
    return cases


def skill_text() -> str:
    parts = [f"=== FILE: SKILL.md ===\n{(SKILL_DIR / 'SKILL.md').read_text()}"]
    for ref in sorted((SKILL_DIR / "references").glob("*.md")):
        parts.append(f"=== FILE: references/{ref.name} ===\n{ref.read_text()}")
    return "\n\n".join(parts)


def build_prompt(cases: list[dict], baseline: bool = False) -> str:
    head = [
        "Answer each question below. For every question pick EXACTLY ONE of its listed",
        "options, copied verbatim.",
    ]
    if baseline:
        head += ["Answer from your own knowledge. If you do not know, choose `not-specified`."]
    else:
        head += [
            "Your ONLY source of truth is the skill documentation between the markers.",
            "Do not use outside knowledge. If the documentation does not state the answer,",
            "choose `not-specified` — never guess a value.",
            "", "=== BEGIN SKILL DOCUMENTATION ===", skill_text(), "=== END SKILL DOCUMENTATION ===",
        ]
    lines = head + ["", "QUESTIONS:", ""]
    for c in cases:
        lines.append(f"- {c['id']}: {c['question']}")
        lines.append(f"  options: {' | '.join(c['options'])}")
    lines += ["", "Output ONLY one line per question, nothing else:  <id>: <option>"]
    return "\n".join(lines)


def parse_predictions(text: str, cases: list[dict]) -> dict[str, str]:
    known = {c["id"]: {o.lower(): o for o in c["options"]} for c in cases}
    preds = {}
    for line in text.splitlines():
        m = re.match(r"^\s*[-*]?\s*`?([\w-]+)`?\s*:\s*(.+?)\s*$", line)
        if not m or m.group(1) not in known:
            continue
        val = _unquote(m.group(2).strip().strip("`"))
        preds[m.group(1)] = known[m.group(1)].get(val.lower(), val)
    return preds


def score(cases: list[dict], preds: dict[str, str]) -> dict:
    axes: dict[str, dict] = {}
    wrong, missing = [], []
    for c in cases:
        a = axes.setdefault(c["axis"], {"correct": 0, "total": 0})
        a["total"] += 1
        got = preds.get(c["id"])
        if got is None:
            missing.append(c["id"])
        elif got == c["expect"]:
            a["correct"] += 1
        else:
            wrong.append(f"{c['id']}: expected {c['expect']}, got {got}")
    correct = sum(a["correct"] for a in axes.values())
    return {
        "accuracy": round(correct / len(cases), 4) if cases else 0.0,
        "per_axis": {k: f"{v['correct']}/{v['total']}" for k, v in sorted(axes.items())},
        "wrong": wrong,
        "missing": missing,
    }


def aggregate(cases: list[dict], runs: list[dict[str, str]]) -> dict:
    per_run = [score(cases, p) for p in runs]
    accs = [r["accuracy"] for r in per_run]
    pass_all = [c["id"] for c in cases if all(p.get(c["id"]) == c["expect"] for p in runs)]
    return {
        "trials": len(runs),
        "accuracy_mean": round(statistics.mean(accs), 4),
        "accuracy_sd": round(statistics.stdev(accs), 4) if len(accs) > 1 else 0.0,
        "pass^k": f"{len(pass_all)}/{len(cases)}",
        "certified": len(pass_all) == len(cases),
        "runs": per_run,
    }


def self_test() -> list[str]:
    cases, problems = load_cases(), []
    if not (SKILL_DIR / "SKILL.md").exists():
        problems.append("SKILL.md missing — the harness would measure nothing")
    if len(cases) < 20:
        problems.append(f"only {len(cases)} tasks — plugin-eval asks for 20–50")
    ids = [c["id"] for c in cases]
    if len(ids) != len(set(ids)):
        problems.append("duplicate task ids")
    for c in cases:
        if not (c["axis"] and c["question"] and c["options"] and c["expect"]):
            problems.append(f"task {c['id']} incomplete")
        elif c["expect"] not in c["options"]:
            problems.append(f"task {c['id']}: expect '{c['expect']}' is not an option")
        elif "not-specified" not in c["options"]:
            problems.append(f"task {c['id']}: no `not-specified` option — declining impossible")
    axes = {c["axis"] for c in cases}
    if "decline" not in axes:
        problems.append("no decline (true-negative) task — hallucination goes unmeasured")
    if not any(c["expect"] == "yes" for c in cases):
        problems.append("no yes-case — an always-no answerer would pass the param axis")
    perfect = {c["id"]: c["expect"] for c in cases}
    if score(cases, perfect)["accuracy"] != 1.0:
        problems.append("scorer does not return 1.0 on a perfect prediction set")
    if len(score(cases, {})["missing"]) != len(cases):
        problems.append("scorer does not report missing predictions")
    echo = "\n".join(f"{c['id']}: {c['expect']}" for c in cases)
    if parse_predictions(echo, cases) != perfect:
        problems.append("parser does not round-trip `<id>: <option>` lines")
    if "=== FILE: references/gemini-image-api.md ===" not in build_prompt(cases):
        problems.append("prompt does not inject the real reference files")
    if "SKILL DOCUMENTATION" in build_prompt(cases, baseline=True):
        problems.append("baseline prompt leaks the skill")
    print(f"  {'✔' if not problems else 'x'} self-test: {len(cases)} locked tasks, "
          f"axes: {', '.join(sorted(axes))}")
    for p in problems:
        print(f"  x {p}", file=sys.stderr)
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit-prompt", action="store_true")
    ap.add_argument("--baseline", action="store_true", help="with --emit-prompt: tasks without the skill")
    ap.add_argument("--predictions", nargs="+", metavar="FILE", help="one file per trial")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    cases = load_cases()
    if a.emit_prompt:
        print(build_prompt(cases, baseline=a.baseline)); return 0
    if a.self_test:
        return 1 if self_test() else 0
    if a.predictions:
        runs = [parse_predictions(pathlib.Path(f).read_text(), cases) for f in a.predictions]
        print(json.dumps(aggregate(cases, runs), indent=2, ensure_ascii=False)); return 0
    ap.print_help(); return 2


if __name__ == "__main__":
    sys.exit(main())
