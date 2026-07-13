#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""Deterministic scorer for the `mechanic` plugin's ROUTING eval.

The plugin's promise is a SHARP routing decision: for each task, pick the right
execution tier — do it inline, or delegate to errand (Haiku), mechanic (Sonnet
4.6), or general-purpose (premium). That output is a LABEL, so this is the
STRUCTURED regime of the plugin-eval method: a matcher grades it, no model runs
here, zero judge-variance. It scores a captured routing run against the locked
ground truth.

Beyond plain accuracy it measures the two things that make routing quality
asymmetric:

  • UNDER-ROUTING rate — misroutes to a LESS capable tier (errand < mechanic <
    premium). These are the dangerous ones: the cheap model fails and the work
    must be retried at the right tier. The plugin's rule is "prefer one tier too
    EXPENSIVE over one too cheap," so this rate is called out separately.

  • COST — a transparent, parametrised estimate (assumptions in COST below) of
    (a) the BASELINE with no routing (everything at premium), (b) the IDEAL
    routed cost (every task at its ground-truth tier), and (c) the EFFECTIVE
    routed cost given the router's ACTUAL predictions, where a capability
    under-route pays for the failed cheap attempt PLUS the correct-tier retry.
    Savings % = 1 − routed / baseline. This answers "what's the F1?" and "how
    much do we save?" in one run — and shows how under-routing erodes the saving.

THE ONE RULE: this scores the PLUGIN (the errand/mechanic descriptions, the
routing guidance), never the cases. A mismatch is a plugin bug to fix at the
plugin — you do NOT edit a locked case to make the run pass. See evals/README.md.

Usage:
    uv run evals/scripts/score_routing.py \
        [--truth evals/routing/ground_truth.yaml] \
        [--pred  evals/routing/predictions.example.yaml] [--json]

Exit code: 0 when every case matches its locked expectation, 1 on any mismatch.
"""

import argparse
import json
import os
import sys

import yaml  # human-authored cases live in YAML (comments = calibration anchors)

# ── Cost model (ILLUSTRATIVE, parametrised — order-of-magnitude, not billing) ──
# Blended $/1M tokens per tier, and representative token volume per task by
# `volume`. The batch figure is the whole point: cheap-model savings amortise
# over volume. Tune these to your real mix; the RELATIVE story is what matters.
#
# DELEGATION OVERHEAD is charged for any DELEGATED route (errand/mechanic/
# general-purpose) and NOT for `inline`: spawning a subagent costs spawn +
# context-transfer + result-reintegration on the premium orchestrator. Anthropic
# reports agent runs use ~4× the tokens of a plain chat turn, multi-agent ~15×
# (anthropic.com/engineering/multi-agent-research-system). For a SINGLE small
# task that fixed overhead outweighs the cheap-token saving → inline wins; for a
# BATCH the volume dwarfs it → the cheap subagent wins. That is exactly why a
# lone trivial task must NOT be delegated.
COST = {
    "price_per_mtok": {          # blended input+output, USD / 1M tokens
        "errand": 2.0,           # Haiku 4.5     (~$1 in / $5 out)
        "mechanic": 8.0,         # Sonnet 4.6    (~$3 in / $15 out)
        "inline": 20.0,          # premium orchestrator model (Opus / Sonnet 5)
        "general-purpose": 20.0,  # premium
    },
    "tokens": {"single": 20_000, "batch": 1_500_000},
    "delegation_overhead_tokens": 12_000,  # coordinator spawn + handoff + reintegrate
    "baseline_tier": "general-purpose",  # no-plugin world: everything at premium
}
CAPABILITY = {"errand": 1, "mechanic": 2, "inline": 3, "general-purpose": 3}
DELEGATED = {"errand", "mechanic", "general-purpose"}  # inline is NOT delegated


def _load(path):
    """YAML by default; .json still works (YAML is a JSON superset)."""
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _rates(tp, fp, fn):
    prec = tp / (tp + fp) if (tp + fp) else 1.0
    rec = tp / (tp + fn) if (tp + fn) else 1.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return prec, rec, f1


def _task_cost(route, volume):
    """Cost of one task at `route`: the tier's tokens×price, PLUS the
    delegation overhead (charged at premium) for any delegated route. inline
    pays no overhead — that is what makes it the right call for a lone task."""
    toks = COST["tokens"].get(volume, COST["tokens"]["single"])
    cost = toks / 1_000_000 * COST["price_per_mtok"][route]
    if route in DELEGATED:
        cost += (COST["delegation_overhead_tokens"] / 1_000_000
                 * COST["price_per_mtok"]["inline"])
    return cost


def _cost_analysis(rows):
    """Baseline (all premium) vs ideal (ground-truth tiers) vs effective
    (predicted tiers, with a retry penalty when the router under-routes on
    capability). Returns dollar totals + savings percentages."""
    base = ideal = eff = 0.0
    retries = 0
    for _cid, exp, got, _ok, c in rows:
        vol = c.get("volume", "single")
        base += _task_cost(COST["baseline_tier"], vol)
        ideal += _task_cost(exp, vol)
        if got in CAPABILITY and CAPABILITY[got] < CAPABILITY[exp]:
            # under-capability: the cheap attempt fails → pay it AND retry correct
            eff += _task_cost(got, vol) + _task_cost(exp, vol)
            retries += 1
        elif got in CAPABILITY:
            eff += _task_cost(got, vol)   # over/lateral route: succeeds, just (maybe) pricier
        else:
            eff += _task_cost(exp, vol)   # no prediction captured → assume ideal
    saved = lambda x: round(1 - x / base, 3) if base else 0.0
    return {
        "baseline_usd": round(base, 2), "ideal_usd": round(ideal, 2),
        "effective_usd": round(eff, 2),
        "ideal_savings_pct": saved(ideal), "effective_savings_pct": saved(eff),
        "retry_count": retries,
    }


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
        if got != exp:
            mism.append((cid, exp, got, c))
        rows.append((cid, exp, got, got == exp, c))

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

    # asymmetric error split: under-capability (dangerous) vs over/lateral (wasteful)
    under = [(cid, e, g) for cid, e, g, ok, _ in rows
             if not ok and g in CAPABILITY and CAPABILITY[g] < CAPABILITY[e]]
    over = [(cid, e, g) for cid, e, g, ok, _ in rows
            if not ok and g in CAPABILITY and CAPABILITY[g] > CAPABILITY[e]]
    lateral = [(cid, e, g) for cid, e, g, ok, _ in rows
               if not ok and g in CAPABILITY and CAPABILITY[g] == CAPABILITY[e]]

    return {
        "routes": routes, "per_route": per_route, "rows": rows,
        "total": total, "correct": correct, "accuracy": round(accuracy, 3),
        "macro_f1": round(macro_f1, 3),
        "under_routes": under, "over_routes": over, "lateral_routes": lateral,
        "under_routing_rate": round(len(under) / total, 3) if total else 0.0,
        "cost": _cost_analysis(rows),
        "mismatches": mism, "missing": missing,
        "verdict": "PASS" if not mism and not missing else "FAIL",
    }


def report(s):
    c = s["cost"]
    L = []
    L.append("mechanic routing eval — scoring the PLUGIN against locked ground truth")
    L.append("=" * 70)
    L.append(f"accuracy            : {s['accuracy']:.3f}  ({s['correct']}/{s['total']} tasks routed as expected)")
    L.append(f"macro-F1            : {s['macro_f1']:.3f}  (unweighted mean over {len(s['routes'])} routes)")
    L.append(f"under-routing rate  : {s['under_routing_rate']:.3f}  "
             f"({len(s['under_routes'])} sent to a TOO-CHEAP tier — the dangerous kind)")
    L.append("")
    L.append("per-route (one-vs-rest)")
    L.append("  route             TP  FP  FN  TN   prec   recall   f1")
    for r in s["routes"]:
        m = s["per_route"][r]
        L.append(f"  {r:<16} {m['tp']:>3} {m['fp']:>3} {m['fn']:>3} {m['tn']:>3}   "
                 f"{m['precision']:.2f}   {m['recall']:.2f}    {m['f1']:.2f}")
    L.append("")
    L.append("cost model (illustrative — assumptions in scripts/score_routing.py COST)")
    L.append(f"  baseline (no routing, all premium) : ${c['baseline_usd']:>8.2f}")
    L.append(f"  ideal routed (ground-truth tiers)  : ${c['ideal_usd']:>8.2f}   "
             f"→ saves {c['ideal_savings_pct']*100:.1f}%")
    L.append(f"  effective (this run's routes+retry): ${c['effective_usd']:>8.2f}   "
             f"→ saves {c['effective_savings_pct']*100:.1f}%   ({c['retry_count']} under-route retries)")
    if s["under_routes"]:
        L.append("")
        L.append("UNDER-ROUTES — too-cheap tier, will fail & retry (PLUGIN bug: sharpen the description):")
        for cid, e, g in s["under_routes"]:
            L.append(f"  ↓ {cid}: expected '{e}', got '{g}'  [capability {CAPABILITY[g]} < {CAPABILITY[e]}]")
    if s["over_routes"] or s["lateral_routes"]:
        L.append("")
        L.append("OVER / LATERAL routes — safe but wasteful (still a mismatch to fix at the plugin):")
        for cid, e, g in s["over_routes"]:
            L.append(f"  ↑ {cid}: expected '{e}', got '{g}'  [over-provisioned]")
        for cid, e, g in s["lateral_routes"]:
            L.append(f"  ↔ {cid}: expected '{e}', got '{g}'  [wrong tier, same capability]")
    if s["missing"]:
        L.append("")
        L.append("MISSING predictions (no captured route) — re-run the router to capture them:")
        for cid in s["missing"]:
            L.append(f"  ? {cid}")
    L.append("")
    L.append(f"VERDICT: {s['verdict']}")
    return "\n".join(L)


def main(argv=None):
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)  # evals/
    ap = argparse.ArgumentParser(description="Score the mechanic plugin's routing eval.")
    ap.add_argument("--truth", default=os.path.join(root, "routing", "ground_truth.yaml"))
    ap.add_argument("--pred", default=os.path.join(root, "routing", "predictions.example.yaml"))
    ap.add_argument("--json", action="store_true", help="one-line JSON summary on stdout; report to stderr")
    args = ap.parse_args(argv)

    s = score(_load(args.truth), _load(args.pred))
    rep = report(s)
    if args.json:
        sys.stderr.write(rep + "\n")
        summary = {k: s[k] for k in ("accuracy", "macro_f1", "under_routing_rate",
                                     "correct", "total", "verdict")}
        summary["cost"] = s["cost"]
        summary["mismatches"] = [m[0] for m in s["mismatches"]]
        sys.stdout.write(json.dumps(summary, ensure_ascii=False) + "\n")
    else:
        sys.stdout.write(rep + "\n")
    return 0 if s["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
