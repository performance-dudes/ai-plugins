#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""Deterministic scorer for the example plugin's ROUTING eval.

This is the STRUCTURED regime of the plugin-eval method: the plugin's output on
each case is a label (which entrypoint should fire), so correctness is decided by
a matcher — cheap, reproducible, zero judge-variance. No model runs here; it
grades a captured run against the locked ground truth. (For the FREE-TEXT regime —
judging the greeting *wording* — see judge.py.)

What it measures: does a prompt route to the right place — 'greet' (the run-greet
skill / the /greet command) or 'none' (stay silent)? It builds a per-route
confusion matrix and reports precision / recall / F1 plus the specificity axis
(how often clean/near-miss prompts correctly stayed 'none').

THE ONE RULE: this scores the PLUGIN, never the cases. A mismatch is a plugin bug
(tune the skill description, the agent prompt, the workflow) — you do NOT edit a
locked case to make the run pass. See evals/README.md.

Usage:
    uv run evals/scripts/score_routing.py \
        [--truth evals/routing/ground_truth.yaml] \
        [--pred  evals/routing/predictions.example.yaml] [--json]

Exit code: 0 when every case matches its locked expectation, 1 on any mismatch
(a wrong route, or a clean/near-miss case that triggered). YAML or JSON in, JSON
summary out.
"""

import argparse
import json
import os
import sys

import yaml  # human-authored cases live in YAML (comments = calibration anchors)


def _load(path):
    """Load a case/prediction file. YAML is the default; .json still works
    (YAML is a JSON superset, so yaml.safe_load reads both)."""
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _rates(tp, fp, fn):
    prec = tp / (tp + fp) if (tp + fp) else 1.0
    rec = tp / (tp + fn) if (tp + fn) else 1.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return prec, rec, f1


def score(truth, pred):
    cases = {c["case"]: c for c in truth["cases"]}
    routes = truth.get("routes") or sorted({c["route"] for c in truth["cases"]})
    predicted = {p["case"]: p["route"] for p in pred["predictions"]}

    rows, mism, missing = [], [], []
    for cid, c in cases.items():
        exp = c["route"]
        got = predicted.get(cid)
        if got is None:
            missing.append(cid)
            got = "<none-predicted>"
        ok = got == exp
        if not ok:
            mism.append((cid, exp, got, c.get("clean", False), c.get("prompt", "")))
        rows.append((cid, exp, got, ok, c))

    # per-route confusion matrix (one-vs-rest over the label set)
    per_route = {}
    for r in routes:
        tp = sum(1 for _, e, g, _, _ in rows if e == r and g == r)
        fp = sum(1 for _, e, g, _, _ in rows if e != r and g == r)
        fn = sum(1 for _, e, g, _, _ in rows if e == r and g != r)
        tn = sum(1 for _, e, g, _, _ in rows if e != r and g != r)
        p, rc, f1 = _rates(tp, fp, fn)
        per_route[r] = {"tp": tp, "fp": fp, "fn": fn, "tn": tn,
                        "precision": round(p, 3), "recall": round(rc, 3), "f1": round(f1, 3)}

    total = len(rows)
    correct = sum(1 for _, _, _, ok, _ in rows if ok)
    accuracy = correct / total if total else 0.0
    macro_f1 = sum(per_route[r]["f1"] for r in routes) / len(routes) if routes else 0.0

    # specificity axis: clean/near-miss cases that MUST stay 'none'
    clean = [(cid, e, g) for cid, e, g, _, c in rows if c.get("clean")]
    clean_pass = sum(1 for _, e, g in clean if e == g)
    specificity = clean_pass / len(clean) if clean else 1.0

    return {
        "routes": routes, "per_route": per_route, "rows": rows,
        "total": total, "correct": correct, "accuracy": round(accuracy, 3),
        "macro_f1": round(macro_f1, 3),
        "clean_total": len(clean), "clean_pass": clean_pass,
        "specificity": round(specificity, 3),
        "mismatches": mism, "missing": missing,
        "verdict": "PASS" if not mism and not missing else "FAIL",
    }


def report(s):
    L = []
    L.append("routing eval — scoring the PLUGIN against locked ground truth")
    L.append("=" * 62)
    L.append(f"accuracy         : {s['accuracy']:.3f}  ({s['correct']}/{s['total']} cases routed as expected)")
    L.append(f"macro-F1         : {s['macro_f1']:.3f}  (unweighted mean over {len(s['routes'])} routes)")
    L.append(f"specificity      : {s['specificity']:.3f}  ({s['clean_pass']}/{s['clean_total']} clean/near-miss cases stayed 'none')")
    L.append("")
    L.append("per-route (one-vs-rest)")
    L.append("  route      TP  FP  FN  TN   prec   recall   f1")
    for r in s["routes"]:
        m = s["per_route"][r]
        L.append(f"  {r:<9} {m['tp']:>3} {m['fp']:>3} {m['fn']:>3} {m['tn']:>3}   "
                 f"{m['precision']:.2f}   {m['recall']:.2f}    {m['f1']:.2f}")
    if s["mismatches"]:
        L.append("")
        L.append("MISMATCHES — each is a PLUGIN bug to fix at the plugin, never a case to loosen:")
        for cid, exp, got, is_clean, prompt in s["mismatches"]:
            tag = " [clean/near-miss → false trigger]" if is_clean else ""
            L.append(f"  ✗ {cid}: expected '{exp}', got '{got}'{tag}")
            L.append(f"      prompt: {prompt}")
    if s["missing"]:
        L.append("")
        L.append("MISSING predictions (no captured route) — re-run the plugin to capture them:")
        for cid in s["missing"]:
            L.append(f"  ? {cid}")
    L.append("")
    L.append(f"VERDICT: {s['verdict']}")
    return "\n".join(L)


def main(argv=None):
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)  # evals/
    ap = argparse.ArgumentParser(description="Score the example plugin's routing eval.")
    ap.add_argument("--truth", default=os.path.join(root, "routing", "ground_truth.yaml"))
    ap.add_argument("--pred", default=os.path.join(root, "routing", "predictions.example.yaml"))
    ap.add_argument("--json", action="store_true", help="one-line JSON summary on stdout; report to stderr")
    args = ap.parse_args(argv)

    s = score(_load(args.truth), _load(args.pred))
    rep = report(s)
    if args.json:
        sys.stderr.write(rep + "\n")
        summary = {k: s[k] for k in ("accuracy", "macro_f1", "specificity",
                                     "correct", "total", "verdict")}
        summary["mismatches"] = [m[0] for m in s["mismatches"]]
        sys.stdout.write(json.dumps(summary, ensure_ascii=False) + "\n")
    else:
        sys.stdout.write(rep + "\n")
    return 0 if s["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
