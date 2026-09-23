#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Score the anti-slop detector against the locked cases (SPEC-anti-slop US-slop-3).

Deterministic scorer — no LLM judge. The observable output is a density (hard
hits per 1000 words), which is objective; a judge would only add variance.

Runs the SHIPPING check-slop.py against the SHIPPING lists. Nothing about the
term lists is duplicated into the eval.

    uv run plugins/anti-slop/evals/scripts/score_detection.py
    uv run .../score_detection.py --json     # machine-readable

Exit 0 when every case passes, 1 otherwise.
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys
import tempfile

import yaml

HERE = pathlib.Path(__file__).resolve().parent
PLUGIN = HERE.parents[1]
CHECK = PLUGIN / "skills/anti-slop/scripts/check-slop.py"
CASES = PLUGIN / "evals/detection/cases.yaml"

# From SPEC-anti-slop US-slop-3. Frozen: a failing case is a plugin bug.
MAX_HUMAN = 1.0
MIN_GENERATED = 50.0


def density(text, lang):
    """Hard hits per 1000 words, as the shipping script reports them."""
    with tempfile.NamedTemporaryFile("w", suffix=".md", encoding="utf-8", delete=False) as fh:
        fh.write(text)
        tmp = fh.name
    try:
        out = subprocess.run(
            [sys.executable, str(CHECK), "--lang", lang, "--hard-only", tmp],
            capture_output=True, text=True).stdout
    finally:
        pathlib.Path(tmp).unlink(missing_ok=True)
    if "Keine Treffer" in out:
        return 0.0, out
    m = re.search(r"([\d.]+) pro 1000 Wörter", out)
    if not m:
        raise SystemExit(f"unparsbare Ausgabe von check-slop.py:\n{out}")
    return float(m.group(1)), out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    cases = yaml.safe_load(CASES.read_text(encoding="utf-8"))
    results, tp = [], 0
    fp = fn = tn = 0

    for c in cases:
        d, _ = density(c["text"], c["lang"])
        if c["origin"] == "human":
            ok = d <= MAX_HUMAN
            bound = f"<= {MAX_HUMAN}"
            tn, fp = (tn + 1, fp) if ok else (tn, fp + 1)
        else:
            ok = d >= MIN_GENERATED
            bound = f">= {MIN_GENERATED}"
            tp, fn = (tp + 1, fn) if ok else (tp, fn + 1)
        results.append({"name": c["name"], "origin": c["origin"], "lang": c["lang"],
                        "density": d, "bound": bound, "outcome": "PASS" if ok else "FAIL"})

    def ratio(a, b):
        return round(a / (a + b), 4) if (a + b) else None

    metrics = {
        "precision": ratio(tp, fp),      # gemeldeter Slop, der wirklich Slop ist
        "recall": ratio(tp, fn),         # erkannter Anteil des echten Slops
        "specificity": ratio(tn, fp),    # Menschentext, der in Ruhe gelassen wird
        "confusion": {"tp": tp, "fp": fp, "fn": fn, "tn": tn},
        "separation": None,
    }
    hum = [r["density"] for r in results if r["origin"] == "human"]
    gen = [r["density"] for r in results if r["origin"] == "generated"]
    if hum and gen and max(hum) > 0:
        metrics["separation"] = round(min(gen) / max(hum), 1)
    elif hum and gen:
        metrics["separation"] = "inf"  # kein einziger Treffer auf Menschentext

    failed = [r for r in results if r["outcome"] == "FAIL"]
    if args.json:
        print(json.dumps({"results": results, "metrics": metrics,
                          "outcome": "PASS" if not failed else "FAIL"}, indent=2))
    else:
        print(f"anti-slop detection — {len(results)} locked cases\n")
        for r in results:
            print(f"  {r['outcome']:<4} {r['name']:<18} {r['origin']:<9} "
                  f"{r['density']:>7.1f} / 1000  (soll {r['bound']})")
        print(f"\n  precision {metrics['precision']}  recall {metrics['recall']}  "
              f"specificity {metrics['specificity']}")
        print(f"  confusion {metrics['confusion']}")
        sep = metrics["separation"]
        print("  separation (min generated / max human): "
              + ("kein Treffer auf Menschentext" if sep == "inf" else f"{sep}x"))
        print(f"\n=== detection: {'PASS' if not failed else 'FAIL'} ===")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
