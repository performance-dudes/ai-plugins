#!/usr/bin/env bash
# Tests der vendored Merge-Gate-Entscheidungslogik (.github/merge-gate/).
#
# Warum es diese Suite gibt: die Logik entscheidet über JEDEN Merge in diesem Repo
# und war bis 2026-08-17 ungetestet. In der Zeit ist sie unbemerkt von der Fassung
# in ai-plugins-internal abgedriftet — derselbe Marker galt hier, dort nicht. Ein
# Test des Vertrags hätte das beim ersten Lauf gezeigt.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
fail=0
ok()  { printf '  ✔ %s\n' "$1"; }
bad() { printf '  x %s\n' "$1"; fail=1; }

printf '\n=== merge-gate: Entscheidungsvertrag ===\n'

node --check "$ROOT/.github/merge-gate/decide.mjs" && ok "decide.mjs parst" || bad "decide.mjs kaputt"
node --check "$ROOT/.github/merge-gate/check.mjs"  && ok "check.mjs parst"  || bad "check.mjs kaputt"

node --input-type=module -e "
import { decidePr, markerInPr, markerMisplaced } from '$ROOT/.github/merge-gate/decide.mjs';
const P = [{ path: 'plugins/x/skills/y/SKILL.md' }];          // Produkt-Touch
const D = [{ path: 'docs/a.md' }, { path: 'journal/b.md' }];  // reiner Prozess-Touch
const R = [{ path: 'plugins/x/README.md' }];                  // README zählt nicht als Produkt

const cases = [
  // [Name, PR, erwartet allow, erwartet misplaced]
  ['Marker allein im Body',          { files: P, body: '[merge-gate: ok]' }, true, false],
  ['Begründung, Marker am Ende',     { files: P, body: 'Review gemacht.\n\n[merge-gate: ok]' }, true, false],
  ['Marker im Kommentar am Ende',    { files: P, body: '', comments: [{ body: 'x\n[merge-gate: ok]' }] }, true, false],
  ['Marker im Review am Ende',       { files: P, body: '', reviews: [{ body: '[merge-gate: ok]' }] }, true, false],
  // Der Fall, der am 17.08. Zeit gekostet hat: natürlichste Schreibweise, zählt nicht.
  ['Marker oben, Text darunter',     { files: P, body: '[merge-gate: ok]\n\nBegründung…' }, false, true],
  // Der reale Vorfall vom 02.08., gegen den der Vertrag gebaut wurde.
  ['Marker im Codeblock + Dementi',  { files: P, body: '\`\`\`\n[merge-gate: ok]\n\`\`\`\nNoch KEIN Review gemacht.' }, false, true],
  // Zeilenverankert: inline im Fließtext ist gar kein Marker, also auch nicht
  // 'misplaced' — sonst würde die Meldung jemanden auf eine Stelle hinweisen, die
  // nie als Freigabe gemeint war ('ich habe KEIN [merge-gate: ok] gesetzt').
  ['Marker inline im Fließtext',     { files: P, body: 'habe kein [merge-gate: ok] gesetzt' }, false, false],
  ['gar kein Marker',                { files: P, body: 'nur Text' }, false, false],
  ['Approval sticht alles',          { files: P, body: '', reviews: [{ state: 'APPROVED' }] }, true, false],
  ['kein Produkt-Touch',             { files: D, body: '' }, true, false],
  ['nur README im Plugin',           { files: R, body: '' }, true, false],
  ['leerer PR',                      { files: [], body: '' }, true, false],
];

let bad = 0;
for (const [name, pr, wantAllow, wantMisplaced] of cases) {
  const v = decidePr(pr);
  const gotMis = Boolean(v.misplaced);
  if (v.allow !== wantAllow || gotMis !== wantMisplaced) {
    console.log(\`  x \${name}: allow=\${v.allow} (erwartet \${wantAllow}), misplaced=\${gotMis} (erwartet \${wantMisplaced})\`);
    bad++;
  } else {
    console.log(\`  ✔ \${name}\`);
  }
}

// Die Begründung eines Fehlschlags muss die verletzte Bedingung benennen, sonst
// sucht der Mensch am falschen Ende — genau der Defekt, den diese Runde behoben hat.
const mis = decidePr({ files: P, body: '[merge-gate: ok]\nText' });
if (!/LETZTE/i.test(mis.reason)) { console.log('  x misplaced-reason nennt die Bedingung nicht'); bad++; }
else console.log('  ✔ misplaced-reason nennt die Bedingung');

process.exit(bad ? 1 : 0);
" && ok "Entscheidungsvertrag hält (12 Fälle)" || bad "Entscheidungsvertrag verletzt"

printf '\n=== merge-gate: Workflow-Trigger ===\n'
WF="$ROOT/.github/workflows/merge-gate.yml"
for t in "pull_request" "pull_request_review" "issue_comment"; do
  grep -q "^  $t:" "$WF" && ok "Trigger $t verdrahtet" || bad "Trigger $t fehlt"
done
# 'edited' deckt den Marker im PR-Body ab; ohne ihn bliebe der Check dort stumm.
grep -qE 'types:.*edited' "$WF" && ok "pull_request: edited (Marker im Body)" \
  || bad "pull_request: edited fehlt"

printf '\n=== conventions: Base-Ref fail-closed ===\n'
CV="$ROOT/.github/workflows/conventions.yml"
# Nur echte Aufrufe prüfen — der Erklär-Kommentar im Workflow nennt --depth=0
# absichtlich und darf den Test nicht auslösen.
grep -qE '^[[:space:]]*git fetch .*--depth=0' "$CV" && bad "ungültiges --depth=0 in einem git-Aufruf" \
  || ok "kein git fetch mit --depth=0 mehr"
grep -q 'rev-parse --verify' "$CV" && ok "Base-Ref wird verifiziert (fail-closed)" \
  || bad "Base-Ref wird nicht verifiziert — Check könnte gegen unvollständige Historie laufen"

printf '\n'
[ "$fail" = 0 ] && { printf 'merge-gate: ALL CHECKS PASSED\n'; exit 0; }
printf 'merge-gate: FAILURES ABOVE\n'; exit 1
