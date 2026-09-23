#!/usr/bin/env python3
"""Knowledge suite for the image-toolkit skill — deterministic, stdlib only.

The object under test is the REAL skill: SKILL.md plus every file in references/,
read at run time. No copy lives in this harness.

    python3 score_knowledge.py --self-test                     # no model, runs in CI
    python3 score_knowledge.py --emit-prompt > prompt.txt      # skill + tasks
    python3 score_knowledge.py --emit-prompt --baseline        # tasks only, forced choice
    python3 score_knowledge.py --predictions t1 t2 t3 [--baseline-predictions b --min-discriminating 15]
    python3 score_knowledge.py --baseline-predictions b --max-accuracy 0.6

Exit codes: with --predictions, 1 unless every task passes in every trial (certified).
With only --baseline-predictions, 1 if the baseline scores above --max-accuracy.
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
DECLINE = "not-specified"


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
            cur = {"id": m.group(1).strip(), "axis": "", "question": "", "options": [],
                   "expect": "", "expect_regex": "", "example": ""}
            cases.append(cur); folding = False
            continue
        if cur is None:
            continue
        m = re.match(r"^\s+(axis|question|options|expect|expect_regex|example|note):\s*(.*)$", raw)
        if m:
            key, val = m.group(1), m.group(2).strip()
            folding = False
            if key == "question":
                if val in (">-", ">", "|"):
                    folding = True
                else:
                    cur["question"] = val
            elif key == "options":
                cur["options"] = [_unquote(o) for o in val.strip()[1:-1].split(",") if o.strip()]
            elif key in ("axis", "expect", "example"):
                cur[key] = _unquote(val)
            elif key == "expect_regex":
                cur[key] = _unquote(val).replace("\\\\", "\\")
        elif folding:
            cur["question"] += (" " if cur["question"] else "") + raw.strip()
    return cases


def is_command(c: dict) -> bool:
    return bool(c["expect_regex"])


def options_for(c: dict, baseline: bool) -> list[str]:
    """The baseline may not decline outside the decline axis — forced choice."""
    if baseline and c["axis"] != "decline":
        return [o for o in c["options"] if o != DECLINE]
    return c["options"]


def skill_text() -> str:
    parts = [f"=== FILE: SKILL.md ===\n{(SKILL_DIR / 'SKILL.md').read_text()}"]
    for ref in sorted((SKILL_DIR / "references").glob("*.md")):
        parts.append(f"=== FILE: references/{ref.name} ===\n{ref.read_text()}")
    return "\n\n".join(parts)


def build_prompt(cases: list[dict], baseline: bool = False) -> str:
    head = ["Answer each question below."]
    if baseline:
        head += [
            "Answer from your own knowledge. For a question with options you MUST pick the",
            "single most likely option, copied verbatim, even when unsure — give your best guess.",
        ]
    else:
        head += [
            "Your ONLY source of truth is the skill documentation between the markers.",
            "Do not use outside knowledge. For a question with options pick EXACTLY ONE option,",
            f"copied verbatim. If the documentation does not state the answer, choose `{DECLINE}`",
            "— never guess a value.",
            "", "=== BEGIN SKILL DOCUMENTATION ===", skill_text(), "=== END SKILL DOCUMENTATION ===",
        ]
    lines = head + ["", "QUESTIONS:", ""]
    for c in cases:
        lines.append(f"- {c['id']}: {c['question']}")
        if is_command(c):
            lines.append("  answer: the complete shell command on ONE line")
        else:
            lines.append(f"  options: {' | '.join(options_for(c, baseline))}")
    lines += ["", "Output ONLY one line per question, nothing else:  <id>: <option or command>"]
    return "\n".join(lines)


_LINE = re.compile(r"^[\s|>]*(?:[-*+]|\d+[.)])?\s*(?:\*\*|`)?([\w-]+)(?:\*\*|`)?\s*[:|]\s*(.+?)[\s|]*$")


def parse_predictions(text: str, cases: list[dict]) -> dict[str, str]:
    """Accepts `id: x`, bullets, numbered lists, **bold**/`code` ids and table rows."""
    by_id = {c["id"]: c for c in cases}
    preds = {}
    for line in text.splitlines():
        m = _LINE.match(line)
        if not m or m.group(1) not in by_id:
            continue
        c, val = by_id[m.group(1)], m.group(2).strip()
        if is_command(c):
            preds[c["id"]] = val
            continue
        val = _unquote(val.strip("`*").strip())
        known = {o.lower(): o for o in c["options"]}
        preds[c["id"]] = known.get(val.lower(), val)
    return preds


def passes(c: dict, got: str | None) -> bool:
    if got is None:
        return False
    if is_command(c):
        return re.search(c["expect_regex"], got) is not None
    return got == c["expect"]


def score(cases: list[dict], preds: dict[str, str]) -> dict:
    axes: dict[str, list[int]] = {}
    wrong, missing = [], []
    for c in cases:
        a = axes.setdefault(c["axis"], [0, 0])
        a[1] += 1
        got = preds.get(c["id"])
        if got is None:
            missing.append(c["id"])
        elif passes(c, got):
            a[0] += 1
        else:
            want = f"/{c['expect_regex']}/" if is_command(c) else c["expect"]
            wrong.append(f"{c['id']}: expected {want}, got {got[:120]}")
    correct = sum(a[0] for a in axes.values())
    return {
        "accuracy": round(correct / len(cases), 4) if cases else 0.0,
        "per_axis": {k: f"{v[0]}/{v[1]}" for k, v in sorted(axes.items())},
        "wrong": wrong,
        "missing": missing,
    }


def aggregate(cases: list[dict], runs: list[dict[str, str]], baseline: dict[str, str] | None = None) -> dict:
    per_run = [score(cases, p) for p in runs]
    accs = [r["accuracy"] for r in per_run]
    pass_all = [c for c in cases if all(passes(c, p.get(c["id"])) for p in runs)]
    out = {
        "trials": len(runs),
        "accuracy_mean": round(statistics.mean(accs), 4),
        "accuracy_sd": round(statistics.stdev(accs), 4) if len(accs) > 1 else 0.0,
        "pass^k": f"{len(pass_all)}/{len(cases)}",
        "certified": len(pass_all) == len(cases),
        "runs": per_run,
    }
    if baseline is not None:
        b = score(cases, baseline)
        disc = [c["id"] for c in pass_all if not passes(c, baseline.get(c["id"]))]
        out["baseline"] = {"accuracy": b["accuracy"], "per_axis": b["per_axis"]}
        out["discriminating"] = {"count": f"{len(disc)}/{len(cases)}", "ids": disc}
    return out


def self_test() -> list[str]:
    cases, problems = load_cases(), []
    closed = [c for c in cases if not is_command(c)]
    if not (SKILL_DIR / "SKILL.md").exists():
        problems.append("SKILL.md missing — the harness would measure nothing")
    if len(cases) < 20:
        problems.append(f"only {len(cases)} tasks — plugin-eval asks for 20–50")
    ids = [c["id"] for c in cases]
    if len(ids) != len(set(ids)):
        problems.append("duplicate task ids")
    for c in cases:
        if not (c["axis"] and c["question"]):
            problems.append(f"task {c['id']} incomplete")
        elif is_command(c):
            try:
                if not re.search(c["expect_regex"], c["example"]):
                    problems.append(f"task {c['id']}: its own `example` fails `expect_regex`")
            except re.error as e:
                problems.append(f"task {c['id']}: bad regex ({e})")
        elif not c["options"] or c["expect"] not in c["options"]:
            problems.append(f"task {c['id']}: expect '{c['expect']}' is not an option")
        elif DECLINE not in c["options"]:
            problems.append(f"task {c['id']}: no `{DECLINE}` option — declining impossible")
        elif c["axis"] != "decline" and c["expect"] == DECLINE:
            problems.append(f"task {c['id']}: only decline tasks may expect `{DECLINE}`")
    axes = {c["axis"] for c in cases}
    for need in ("decline", "recent", "command"):
        if need not in axes:
            problems.append(f"no `{need}` axis")
    if not any(c["expect"] == "yes" for c in closed):
        problems.append("no yes-case — an always-no answerer would pass the param axis")

    # Scorer: perfect, one wrong, nothing.
    perfect = {c["id"]: (c["example"] if is_command(c) else c["expect"]) for c in cases}
    if not aggregate(cases, [perfect])["certified"]:
        problems.append("a perfect prediction set is not certified")
    one_wrong = dict(perfect); one_wrong[closed[0]["id"]] = DECLINE
    if aggregate(cases, [perfect, one_wrong])["certified"]:
        problems.append("one wrong answer in one trial still certifies")
    if len(score(cases, {})["missing"]) != len(cases):
        problems.append("scorer does not report missing predictions")

    # Shortcut answerers must fail clearly.
    always_decline = {c["id"]: DECLINE for c in cases}
    if score(cases, always_decline)["accuracy"] > 0.2:
        problems.append("an always-`not-specified` answerer scores > 0.2")
    first = {c["id"]: (c["options"][0] if c["options"] else "") for c in cases}
    if score(cases, first)["accuracy"] > 0.5:
        problems.append("an always-first-option answerer scores > 0.5")
    always_no = {c["id"]: ("no" if "no" in c["options"] else (c["options"] or [""])[0]) for c in cases}
    if score(cases, always_no)["accuracy"] > 0.5:
        problems.append("an always-no answerer scores > 0.5")
    for c in (c for c in cases if is_command(c)):
        no_size = re.sub(r"\s--size[ =]\S+", "", c["example"])
        invented = c["example"].replace("--aspect", "--aspect-ratio")
        if passes(c, no_size):
            problems.append(f"{c['id']}: a command without --size passes")
        if passes(c, invented):
            problems.append(f"{c['id']}: a command with the invented --aspect-ratio passes")

    # Parser: the formats models actually emit.
    c0 = closed[0]
    for fmt in ("{i}: {v}", "- {i}: {v}", "1. {i}: {v}", "**{i}**: {v}", "`{i}`: `{v}`",
                "| {i} | {v} |", "{i}: \"{v}\""):
        if parse_predictions(fmt.format(i=c0["id"], v=c0["expect"]), cases).get(c0["id"]) != c0["expect"]:
            problems.append(f"parser misses format {fmt!r}")

    # Prompt: real skill injected; baseline neither sees the skill nor may decline.
    if "=== FILE: references/gemini-image-api.md ===" not in build_prompt(cases):
        problems.append("prompt does not inject the real reference files")
    base = build_prompt(cases, baseline=True)
    if "SKILL DOCUMENTATION" in base:
        problems.append("baseline prompt leaks the skill")
    for c in closed:
        if c["axis"] != "decline" and DECLINE in options_for(c, baseline=True):
            problems.append(f"baseline may decline on {c['id']} — measures reluctance, not knowledge")
    print(f"  {'✔' if not problems else 'x'} self-test: {len(cases)} locked tasks, "
          f"axes: {', '.join(sorted(axes))}")
    for p in problems:
        print(f"  x {p}", file=sys.stderr)
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit-prompt", action="store_true")
    ap.add_argument("--baseline", action="store_true", help="with --emit-prompt: no skill, forced choice")
    ap.add_argument("--predictions", nargs="+", metavar="FILE", help="one file per trial with the skill")
    ap.add_argument("--baseline-predictions", metavar="FILE", help="answers of the no-skill baseline")
    ap.add_argument("--max-accuracy", type=float, help="baseline gate: fail if the baseline scores above")
    ap.add_argument("--min-discriminating", type=int,
                    help="with --predictions + --baseline-predictions: fail if fewer tasks separate skill from baseline")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    cases = load_cases()
    if a.emit_prompt:
        print(build_prompt(cases, baseline=a.baseline)); return 0
    if a.self_test:
        return 1 if self_test() else 0
    base = parse_predictions(pathlib.Path(a.baseline_predictions).read_text(), cases) \
        if a.baseline_predictions else None
    if a.predictions:
        runs = [parse_predictions(pathlib.Path(f).read_text(), cases) for f in a.predictions]
        result = aggregate(cases, runs, base)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        if not result["certified"]:
            return 1
        if a.min_discriminating is not None and base is not None:
            n = len(result["discriminating"]["ids"])
            if n < a.min_discriminating:
                print(f"only {n} discriminating tasks < {a.min_discriminating}: the suite measures priors",
                      file=sys.stderr)
                return 1
        return 0
    if base is not None:
        b = score(cases, base)
        print(json.dumps(b, indent=2, ensure_ascii=False))
        if a.max_accuracy is not None and b["accuracy"] > a.max_accuracy:
            print(f"baseline {b['accuracy']} > {a.max_accuracy}: the suite measures priors, not the skill",
                  file=sys.stderr)
            return 1
        return 0
    ap.print_help(); return 2


if __name__ == "__main__":
    sys.exit(main())
