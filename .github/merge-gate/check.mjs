#!/usr/bin/env node
// CI-Check des Merge-Gates (SPEC-merge-gate, US-6) — die unumgehbare,
// server-seitige Grenze. Anders als der lokale Hook ist er FAIL-CLOSED: lässt
// sich der PR nicht beurteilen, wird der Check rot (kein Merge im Zweifel).
//
// Teilt die Entscheidung mit dem Hook über ./decide.mjs:
//   menschliches Approval sticht alles · kein Produkt-Touch → durch ·
//   Produkt-Touch braucht den Marker [merge-gate: ok].
//
// Als Required-Check in der Branch-Protection verdrahtet, kann ihn auch ein
// Merge über Web-UI / `gh api` nicht umgehen. PR-Nummer aus argv[2] oder
// $PR_NUMBER. Braucht `gh` mit $GH_TOKEN (in GitHub Actions: github.token).

import { execFileSync } from "node:child_process";
import { decidePr } from "./decide.mjs";

const prNum = process.argv[2] || process.env.PR_NUMBER;
if (!prNum) {
  console.error("merge-gate-check: keine PR-Nummer (argv[2] oder $PR_NUMBER)");
  process.exit(2);
}

let pr;
try {
  const args = ["pr", "view", String(prNum), "--json", "body,comments,reviews,files"];
  pr = JSON.parse(execFileSync("gh", args, { encoding: "utf8" }));
} catch (e) {
  console.error(`merge-gate-check: \`gh pr view ${prNum}\` fehlgeschlagen — ${e.message}`);
  process.exit(2); // fail-closed: nicht beurteilbar → Check rot
}

const v = decidePr(pr);
console.log(`merge-gate: ${v.allow ? "PASS" : "FAIL"} — ${v.reason}`);
if (!v.allow) {
  console.error(
    "→ Entweder den Cold-Review mit `[merge-gate: ok]` in den PR schreiben, " +
      "oder ein menschliches Approval einholen (überschreibt das Gate).",
  );
}
process.exit(v.allow ? 0 : 1);
