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

// DER VERTRAG: Der Marker zählt nur als **letzte nicht-leere Zeile** eines Beitrags
// (Body, Kommentar oder Review — jeder für sich). Übernommen aus der Fassung in
// ai-plugins-internal, wo sie aus einem realen Vorfall stammt: ein Body mit dem
// Marker in einem Codeblock plus dem Satz „ich habe noch KEINEN Cold-Review
// gemacht" lieferte hier allow=true. Diese Datei trug bis dahin die schwächere
// Variante (Treffer irgendwo im Text), womit sich dieselbe Aktion je nach Repo
// verschieden verhielt.
//
// WARUM NICHT Codeblöcke erkennen: dort bereits versucht und verworfen — es lief
// auf ein Wettrüsten hinaus (Inline-Zitat, ```, ~~~, verschachtelte ````, eingerückte
// Blöcke, HTML-Kommentare) und erzeugte falsche Blocks auf legitimem Input. Eine
// Heuristik, die echte Freigaben verwirft, ist schlimmer als eine, die ein Zitat
// durchlässt.
function letzteNichtLeereZeile(text) {
  const zeilen = String(text).split(/\r?\n/);
  for (let i = zeilen.length - 1; i >= 0; i--) {
    if (zeilen[i].trim() !== "") return zeilen[i];
  }
  return "";
}

// Teile des PR, in denen ein Marker stehen darf — je Beitrag einzeln bewertet.
function markerParts(pr) {
  const parts = [pr?.body || ""];
  for (const c of pr?.comments || []) parts.push(c?.body || "");
  for (const r of pr?.reviews || []) parts.push(r?.body || "");
  return parts;
}

export function markerInPr(pr) {
  return markerParts(pr).some((t) => MARKER_RE.test(letzteNichtLeereZeile(t)));
}

// Steht der Marker zwar irgendwo, aber nicht an der geforderten Stelle? Das ist der
// häufigste Fall und war bislang von "gar kein Marker" nicht unterscheidbar — die
// Meldung verlangte dann, etwas zu setzen, das sichtbar schon dastand.
export function markerMisplaced(pr) {
  if (markerInPr(pr)) return false;
  return markerParts(pr).some((t) => MARKER_RE.test(t));
}

export function approvalInPr(pr) {
  // GitHub lässt niemanden den EIGENEN PR approven → ein APPROVED-Review ist ein
  // zweites (menschliches) Augenpaar. Genau das soll das Gate überschreiben.
  return (pr?.reviews || []).some((r) => String(r?.state).toUpperCase() === "APPROVED");
}

// Kernentscheidung. Eingaben sind bereits extrahiert (testbar ohne gh).
export function decide({ files, hasMarker, hasApproval, misplaced }) {
  if (hasApproval) return { allow: true, reason: "menschliches Approval überschreibt das Gate" };
  if (!requiresMarker(files)) return { allow: true, reason: "kein Produkt-Touch (docs/specs/journal/…) — Gate nicht einschlägig" };
  if (hasMarker) return { allow: true, reason: "Freigabe-Marker [merge-gate: ok] vorhanden" };
  if (misplaced) {
    return {
      allow: false,
      misplaced: true,
      reason:
        "Freigabe-Marker gefunden, aber nicht an der geforderten Stelle: er muss die " +
        "LETZTE nicht-leere Zeile seines Beitrags sein (Body, Kommentar oder Review). " +
        "Steht Text darunter, zählt er nicht.",
    };
  }
  return {
    allow: false,
    reason:
      "Produkt-Änderung ohne Freigabe-Marker [merge-gate: ok] und ohne menschliches Approval.",
  };
}

// Bequemer Einstieg ab dem rohen PR-Objekt.
export function decidePr(pr) {
  return decide({
    files: filesOf(pr),
    hasMarker: markerInPr(pr),
    hasApproval: approvalInPr(pr),
    misplaced: markerMisplaced(pr),
  });
}
