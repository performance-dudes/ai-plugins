#!/usr/bin/env python3
"""Score the terminal plugin's triggering evaluation suite.

Regime: DETERMINISTIC. The outcome per task is a single label (fires / does not
fire), so it is matched programmatically — no judge, no judge variance.

The object under test is the REAL skill: the prompt is built from
`skills/iterm-dynamic-profile/SKILL.md` at runtime, never from a copy pasted into
this harness. Change the skill and this measures the changed skill.

Usage
-----
    # 1. emit the prompt that presents the real skill + the locked tasks
    python3 score_triggering.py --emit-prompt > /tmp/prompt.txt

    # 2. run it through the agent harness, capture the transcript
    claude -p "$(cat /tmp/prompt.txt)" > /tmp/predictions.yaml

    # 3. score the transcript against the locked ground truth
    python3 score_triggering.py --predictions /tmp/predictions.yaml

    # self-check of the scorer itself (no model call, used by CI)
    python3 score_triggering.py --self-test
"""

import argparse
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
PLUGIN = HERE.parent.parent
CASES = PLUGIN / "evals" / "triggering" / "cases.yaml"
SKILL = PLUGIN / "skills" / "iterm-dynamic-profile" / "SKILL.md"


# --- tiny YAML reader ------------------------------------------------------
# Deliberately dependency-free: the case files use one fixed, flat shape, and a
# pip install would make the suite harder to run than the thing it measures.
def load_cases(path=CASES):
    section, cases = None, {"expected_fires": [], "expected_does_not_fire": []}
    cur = None
    for raw in path.read_text().splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if re.match(r"^expected_\w+:", raw):
            section = raw.split(":")[0]
            cur = None
            continue
        m = re.match(r"^\s*-\s*id:\s*(.+)$", raw)
        if m:
            cur = {"id": m.group(1).strip(), "prompt": "", "note": ""}
            cases[section].append(cur)
            continue
        m = re.match(r'^\s+prompt:\s*(.+)$', raw)
        if m and cur is not None:
            v = m.group(1).strip()
            if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
                v = v[1:-1]
            cur["prompt"] = v
    return cases


def ground_truth(cases):
    gt = {c["id"]: True for c in cases["expected_fires"]}
    gt.update({c["id"]: False for c in cases["expected_does_not_fire"]})
    return gt


def build_prompt(cases):
    """Present the REAL skill file, then ask for one label per task."""
    skill = SKILL.read_text()
    tasks = [(c["id"], c["prompt"]) for c in
             cases["expected_fires"] + cases["expected_does_not_fire"]]
    lines = [
        "You are deciding whether a Claude Code skill should activate.",
        "",
        "Below is the complete skill file. Judge ONLY from it — do not assume",
        "capabilities it does not describe.",
        "",
        "=== BEGIN SKILL FILE ===",
        skill,
        "=== END SKILL FILE ===",
        "",
        "For each task below, answer whether this skill should fire for that user",
        "request. Grade the OUTCOME, not a tool-call path.",
        "",
        "Output YAML only, one line per task, exactly:  <id>: fires | no",
        "",
    ]
    lines += [f"- {tid}: {prompt}" for tid, prompt in tasks]
    return "\n".join(lines)


def parse_predictions(text):
    preds = {}
    for line in text.splitlines():
        m = re.match(r"^\s*-?\s*([\w-]+)\s*:\s*(fires|no|true|false|yes)\s*$",
                     line.strip(), re.I)
        if m:
            preds[m.group(1)] = m.group(2).lower() in ("fires", "true", "yes")
    return preds


def score(gt, preds):
    tp = fp = tn = fn = 0
    missing = []
    for cid, expected in gt.items():
        if cid not in preds:
            missing.append(cid)
            continue
        got = preds[cid]
        if expected and got:
            tp += 1
        elif expected and not got:
            fn += 1
        elif not expected and got:
            fp += 1
        else:
            tn += 1
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    spec = tn / (tn + fp) if tn + fp else 0.0
    return {"tp": tp, "fp": fp, "tn": tn, "fn": fn, "precision": round(prec, 4),
            "recall": round(rec, 4), "f1": round(f1, 4),
            "specificity": round(spec, 4), "missing": missing}


def self_test():
    """Scorer sanity without a model call — CI runs this."""
    cases = load_cases()
    gt = ground_truth(cases)
    problems = []
    if len(cases["expected_fires"]) < 5:
        problems.append("too few positive tasks")
    if len(cases["expected_does_not_fire"]) < 3:
        problems.append("too few near-miss/clean tasks (precision unmeasurable)")
    for c in cases["expected_fires"] + cases["expected_does_not_fire"]:
        if not c["prompt"]:
            problems.append(f"task {c['id']} has no prompt")
    if not SKILL.exists():
        problems.append("skill file missing — the harness would measure nothing")
    # A perfect prediction set must score 1.0; an inverted one must score 0.0.
    if score(gt, dict(gt))["f1"] != 1.0:
        problems.append("scorer does not return f1=1.0 on a perfect prediction set")
    inverted = {k: not v for k, v in gt.items()}
    if score(gt, inverted)["f1"] != 0.0:
        problems.append("scorer does not return f1=0.0 on an inverted set")
    if score(gt, {})["missing"] != list(gt):
        problems.append("scorer does not report missing predictions")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit-prompt", action="store_true")
    ap.add_argument("--predictions")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()

    cases = load_cases()
    if a.emit_prompt:
        print(build_prompt(cases))
        return 0
    if a.self_test:
        problems = self_test()
        for p in problems:
            print(f"  x {p}", file=sys.stderr)
        n = len(cases["expected_fires"]) + len(cases["expected_does_not_fire"])
        print(f"  {'✔' if not problems else 'x'} self-test: {n} locked tasks, "
              f"{len(cases['expected_does_not_fire'])} of them near-miss/clean")
        return 1 if problems else 0
    if a.predictions:
        preds = parse_predictions(pathlib.Path(a.predictions).read_text())
        r = score(ground_truth(cases), preds)
        print(json.dumps(r, indent=2))
        if r["missing"]:
            print(f"WARNING: {len(r['missing'])} tasks unpredicted: "
                  f"{', '.join(r['missing'])}", file=sys.stderr)
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
