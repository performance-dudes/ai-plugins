#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["anthropic>=0.40", "pyyaml>=6"]
# ///
"""LLM-as-a-judge for the FREE-TEXT regime — the greeting the plugin PRODUCES.

Use a judge ONLY when correctness is genuinely semantic. The routing labels are
structured → score them with score_routing.py (deterministic, free). The greeting
*wording* is fuzzy → judge it here, with the two-call pattern:

    1. TARGET call — run the thing under test (the greeter's REAL system prompt)
                     at production temperature (~0.3). Free-text out. (Or set
                     target.response in the case to judge a captured answer.)
    2. JUDGE call  — forced tool_use (JUDGE_TOOL), temperature 0 for determinism.
                     The human-written expectation in cases.json is the calibration
                     anchor; the judge checks the response AGAINST it only — it sets
                     no standard of its own. Like a test runner, not a critic.

Parsed DEFENSIVELY: a missing/garbled field falls back to the FAILING value, so a
malformed judge response never silently passes. Safety is zero-tolerance — one
miss fails the case.

THE ONE RULE (same as the whole harness): this scores the PLUGIN. A failing case
means fix the greeter agent / workflow — you never loosen a locked expectation to
make the greeting pass. See evals/README.md.

This is the compact reference; the production-grade generic judge (κ validation,
mean±σ over N runs) lives in plugin-eval@ai-plugins-internal.

Usage:
    export ANTHROPIC_API_KEY=...                          # never hard-code
    uv run evals/scripts/judge.py --cases evals/greeting/cases.yaml [--json]

Exit code: 0 if every case passed, 1 otherwise (a behavior miss, a language miss,
or — zero tolerance — any safety miss).
"""

import argparse
import json
import os
import sys

import yaml  # human-authored cases live in YAML

DEFAULT_TARGET_MODEL = "claude-haiku-4-5"
DEFAULT_JUDGE_MODEL = "claude-haiku-4-5"

# The judge MUST return exactly this shape (forced via tool_choice) — no prose to
# parse, no schema drift. Each result carries its own reason for debugging.
JUDGE_TOOL = {
    "name": "record_judgment",
    "description": "Record the judgment of the response against the human expectation. Judge ONLY against the listed expectations; invent no new criteria.",
    "input_schema": {
        "type": "object",
        "properties": {
            "language_ok": {"type": "boolean", "description": "Response is in the expected language."},
            "behaviors": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "passed": {"type": "boolean"},
                        "reason": {"type": "string"},
                    },
                    "required": ["name", "passed", "reason"],
                },
            },
            "safety": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "passed": {"type": "boolean"},
                        "reason": {"type": "string"},
                    },
                    "required": ["name", "passed", "reason"],
                },
            },
            "pass": {"type": "boolean", "description": "Overall: every behavior and safety check passed and the language matched."},
        },
        "required": ["language_ok", "behaviors", "safety", "pass"],
    },
}


def build_judge_prompt(case, response):
    exp = case["expectations"]
    return (
        "You are grading a chat response against a fixed, human-written expectation. "
        "Be objective. Judge ONLY against the expectations listed — do not invent criteria.\n\n"
        f"Expected language: {exp.get('language', 'any')}\n\n"
        "Behaviors to check (IS / IS NOT):\n"
        + "".join(f"- {b['name']}: {b['description']} (expected={b['expected']})\n" for b in exp.get("behaviors", []))
        + "\nSafety checks (zero-tolerance):\n"
        + ("".join(f"- {s['name']}: {s['description']} (expected={s['expected']})\n" for s in exp.get("safety", [])) or "- (none)\n")
        + "\n--- RESPONSE UNDER TEST ---\n"
        + response
        + "\n--- END RESPONSE ---\n\n"
        "Call record_judgment with your verdict."
    )


def _bool(d, key, default=False):
    v = d.get(key)
    return v if isinstance(v, bool) else default


def call_target(client, case, model):
    t = case["target"]
    if t.get("response"):
        return t["response"]
    msg = client.messages.create(
        model=t.get("model", model),
        max_tokens=512,
        temperature=t.get("temperature", 0.3),
        system=t.get("system", ""),
        messages=[{"role": m["role"], "content": m["text"]} for m in t["messages"]],
    )
    return "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")


def call_judge(client, case, response, model):
    msg = client.messages.create(
        model=model,
        max_tokens=1024,
        temperature=0,
        tools=[JUDGE_TOOL],
        tool_choice={"type": "tool", "name": "record_judgment"},
        messages=[{"role": "user", "content": build_judge_prompt(case, response)}],
    )
    for b in msg.content:
        if getattr(b, "type", "") == "tool_use" and b.name == "record_judgment":
            return b.input
    return {}  # defensive: no tool call -> treated as failing below


def case_passed(verdict, case):
    # Defensive: every axis defaults to FAILING when the judge output is missing/garbled.
    exp = case["expectations"]
    lang_ok = _bool(verdict, "language_ok") if exp.get("language") else True
    got_b = {b.get("name"): _bool(b, "passed") for b in verdict.get("behaviors", []) if isinstance(b, dict)}
    behaviors_ok = all(got_b.get(b["name"], False) == b["expected"] for b in exp.get("behaviors", []))
    got_s = {s.get("name"): _bool(s, "passed") for s in verdict.get("safety", []) if isinstance(s, dict)}
    safety_ok = all(got_s.get(s["name"], False) == s["expected"] for s in exp.get("safety", []))  # zero-tolerance
    return lang_ok and behaviors_ok and safety_ok


def main(argv=None):
    ap = argparse.ArgumentParser(description="LLM-as-a-judge for the greeting free-text eval.")
    ap.add_argument("--cases", required=True)
    ap.add_argument("--target-model", default=DEFAULT_TARGET_MODEL)
    ap.add_argument("--judge-model", default=DEFAULT_JUDGE_MODEL)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        sys.stderr.write("ANTHROPIC_API_KEY not set — this reference judge needs it to run the two calls.\n")
        return 2

    from anthropic import Anthropic
    client = Anthropic(api_key=key)

    with open(args.cases, "r", encoding="utf-8") as fh:
        cases = yaml.safe_load(fh)   # YAML default; JSON is a valid subset
    if isinstance(cases, dict):
        cases = [cases]

    results, all_pass = [], True
    for case in cases:
        if "name" not in case:  # skip a leading $comment-only object
            continue
        response = call_target(client, case, args.target_model)
        verdict = call_judge(client, case, response, args.judge_model)
        passed = case_passed(verdict, case)
        all_pass = all_pass and passed
        results.append({"name": case["name"], "pass": passed, "verdict": verdict})
        if not args.json:
            print(f"{'PASS' if passed else 'FAIL'}  {case['name']}")

    if args.json:
        print(json.dumps({"all_pass": all_pass, "results": results}, ensure_ascii=False))
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
