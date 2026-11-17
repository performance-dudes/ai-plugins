#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6"]
# ///
"""Deterministic scorer for the token-guard OFFLOAD eval (AC-tg-5-3).

STRUCTURED regime: the detector returns a boolean, so a matcher grades it — no
model, no judge variance. The object under test is injected, not copied: the
scorer imports the REAL isOffloadAsk from hooks/lib/guard.mjs via node.

Runs K trials (default 3) and reports pass^k: a case passes only if ALL trials
match. For a deterministic detector the trials must agree; disagreement would
itself be a bug.

Exit 0 only when pass^k = 100 % on every case.
"""
import json
import subprocess
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
PLUGIN = HERE.parent.parent
CASES = HERE.parent / "offload" / "ground_truth.yaml"
GUARD = PLUGIN / "hooks" / "lib" / "guard.mjs"
K = int(sys.argv[1]) if len(sys.argv) > 1 else 3

JS = (
    "const g = await import(process.argv[1]);"
    "let raw=''; for await (const c of process.stdin) raw += c;"
    "process.stdout.write(JSON.stringify(JSON.parse(raw).map(t => g.isOffloadAsk(t))));"
)


def predict(texts):
    r = subprocess.run(
        ["node", "--input-type=module", "-e", JS, GUARD.as_uri()],
        input=json.dumps(texts), capture_output=True, text=True, check=True,
    )
    return json.loads(r.stdout)


def main():
    cases = yaml.safe_load(CASES.read_text(encoding="utf-8"))["cases"]
    texts = [c["text"] for c in cases]
    trials = [predict(texts) for _ in range(K)]
    fails, by_family = [], {}
    tp = fp = fn = tn = 0
    for i, c in enumerate(cases):
        preds = [t[i] for t in trials]
        ok = all(p == c["expected"] for p in preds)
        fam = by_family.setdefault(c["family"], [0, 0])
        fam[0] += ok
        fam[1] += 1
        p = preds[0]
        tp += p and c["expected"]
        fp += p and not c["expected"]
        fn += (not p) and c["expected"]
        tn += (not p) and not c["expected"]
        if not ok:
            fails.append((c["id"], c["expected"], preds))
    n = len(cases)
    print(f"offload eval — {n} cases, k={K}")
    print(f"pass^{K}: {n - len(fails)}/{n} = {100 * (n - len(fails)) / n:.0f} %")
    prec = tp / (tp + fp) if tp + fp else 1.0
    rec = tp / (tp + fn) if tp + fn else 1.0
    print(f"precision {prec:.2f} · recall {rec:.2f} · TP {tp} FP {fp} FN {fn} TN {tn}")
    for fam, (good, tot) in sorted(by_family.items()):
        print(f"  {fam:10s} {good}/{tot}")
    for cid, exp, preds in fails:
        print(f"  MISS {cid}: expected {exp}, got {preds}")
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main()
