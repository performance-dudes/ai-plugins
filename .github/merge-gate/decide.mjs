// Geteilte Entscheidungslogik des Merge-Gates (SPEC-merge-gate, US-4/US-6/US-7).
// Pur, zero-dep — von BEIDEN Durchsetzungsstellen importiert (dem lokalen
// PreToolUse-Hook und dem CI-Check), damit ihre Regel nie auseinanderdriftet.
//
// Regel (in dieser Reihenfolge):
//   1. Menschliches Approval im PR  → durchlassen (Approval sticht alles).
//   2. Kein Produkt-Touch (nur docs/specs/journal/plans/Root/Tests/CI) → Gate
//      nicht einschlägig, durchlassen.
//   3. Produkt-Touch + Marker [merge-gate: ok] → durchlassen.
//   4. Produkt-Touch ohne Marker und ohne Approval → BLOCKEN.

export const MARKER_RE = /^[ \t]*\[merge-gate:[ \t]*ok\][ \t]*$/m;

// Produkt = Datei unter plugins/<x>/ … die KEINE README ist. Spiegelt die
// Produkt/Prozess-Trennung aus tests/spec-touch-check.sh: nur der Plugin-Runtime
// zählt als Produkt; specs/docs/journal/plans, Root-Dateien, tests/, .github/
// sind Prozess/Scaffolding und brauchen kein Review-Gate.
const PRODUCT_RE = /^plugins\/[^/]+\/.+/;
const README_RE = /(^|\/)README\.md$/;

export function requiresMarker(files) {
  return (files || []).some((f) => PRODUCT_RE.test(f) && !README_RE.test(f));
}

// --- Extraktion aus dem `gh pr view --json body,comments,reviews,files`-JSON ---
export function filesOf(pr) {
  return (pr?.files || []).map((f) => (typeof f === "string" ? f : f.path)).filter(Boolean);
}

export function markerInPr(pr) {
  const parts = [pr?.body || ""];
  for (const c of pr?.comments || []) parts.push(c?.body || "");
  for (const r of pr?.reviews || []) parts.push(r?.body || "");
  return MARKER_RE.test(parts.join("\n"));
}

export function approvalInPr(pr) {
  // GitHub lässt niemanden den EIGENEN PR approven → ein APPROVED-Review ist ein
  // zweites (menschliches) Augenpaar. Genau das soll das Gate überschreiben.
  return (pr?.reviews || []).some((r) => String(r?.state).toUpperCase() === "APPROVED");
}

// Kernentscheidung. Eingaben sind bereits extrahiert (testbar ohne gh).
export function decide({ files, hasMarker, hasApproval }) {
  if (hasApproval) return { allow: true, reason: "menschliches Approval überschreibt das Gate" };
  if (!requiresMarker(files)) return { allow: true, reason: "kein Produkt-Touch (docs/specs/journal/…) — Gate nicht einschlägig" };
  if (hasMarker) return { allow: true, reason: "Freigabe-Marker [merge-gate: ok] vorhanden" };
  return {
    allow: false,
    reason:
      "Produkt-Änderung ohne Freigabe-Marker [merge-gate: ok] und ohne menschliches Approval.",
  };
}

// Bequemer Einstieg ab dem rohen PR-Objekt.
export function decidePr(pr) {
  return decide({ files: filesOf(pr), hasMarker: markerInPr(pr), hasApproval: approvalInPr(pr) });
}
