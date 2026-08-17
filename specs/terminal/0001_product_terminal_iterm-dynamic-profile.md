# Product-Spec: terminal — Terminal-Identität pro Projekt (iTerm2 Dynamic Profiles)

| | |
|---|---|
| Plugin | `terminal` |
| Status | umgesetzt, Erst-Release `0.1.0` |
| Marketplace | `ai-plugins` (public) |
| Verwandt | SPEC-repo-conventions §3–§6 |

## 1. Thema

Wer mehrere Projekte parallel in Terminals offen hat, verliert Zeit an der Frage
„in welchem Projekt bin ich hier gerade". Das Plugin macht die Antwort **sichtbar,
bevor eine Zeile Text gelesen wird**: pro Projekt ein iTerm2-Dynamic-Profile mit
eigenem Hintergrundbild, eigener Akzentfarbe und einem Badge oben rechts, das den
laufenden Claude-Code-Session-Namen zeigt. Das Profil schaltet **selbsttätig** um,
sobald das Arbeitsverzeichnis im Projekt liegt.

Das Plugin liefert drei Dinge: das **Wissen** (Skill), ein **Werkzeug** (Installer)
und ein **Beispiel** (Template).

## 2. Warum (Begründung)

**Warum überhaupt ein Plugin und kein Wiki-Eintrag?** Das Rezept war zehnmal von
Hand angewendet worden und existierte nur auf einer Maschine. Es besteht aus
wenigen invarianten Feldern und genau sechs variablen Werten — damit ist es
template-fähig, und Template plus Erklärung gehören zusammen ausgeliefert.

**Warum ein Installer und kein kopierbares JSON?** iTerm2 verlangt für Hintergrund
und Icon **absolute** Pfade und löst nichts selbst auf. Ein Profil, das auf einer
anderen Maschine erzeugt wurde, trägt fremde Home-Pfade — und iTerm2 rendert einen
toten Pfad **kommentarlos ohne Bild**. Der Nutzer sieht ein leeres Terminal und
bekommt keinen Hinweis auf die Ursache. Ein Installer, der zur Installationszeit
auflöst und pro fehlendem Asset warnt, ist deshalb kein Komfort, sondern die
einzige Form, in der ein Template die Maschinengrenze überlebt.

**Warum public?** Die Mechanik ist markenneutral. Nur das mitgelieferte Template
ist PD-spezifisch, und es referenziert Assets, statt sie zu kopieren.

**Warum degradieren statt scheitern?** Das Beispiel-Template zieht sein Wallpaper
aus einem **privaten** Repo. Ein Nutzer ohne Zugang soll Farbe, Badge und Icon
trotzdem bekommen — mit einer klaren Meldung, was fehlt und woher es käme. Ein
Profil ohne Wallpaper ist ein Teilerfolg; ein unerklärt leeres Terminal ist ein
Support-Fall.

## 3. Nicht-Ziele

- Keine Unterstützung anderer Terminal-Emulatoren (Ghostty, WezTerm, Alacritty) —
  deren Konfigurationsmodell ist zu verschieden für eine gemeinsame Abstraktion.
- Keine Verwaltung/Änderung bestehender, von Hand gepflegter Profile außer dem
  gleichnamigen.
- Kein Ausliefern von Bild-Assets im Plugin (siehe §2, „referenzieren statt kopieren").

## 4. Komponenten

| Komponente | Zweck |
|---|---|
| `skills/iterm-dynamic-profile/SKILL.md` | Das Rezept: Feld-Anatomie, Auto-Switch, Badge-Escaping, Blend-Werte, Fehlerbilder |
| `scripts/install-iterm-profile.sh` | Installer: Pfad-Auflösung, Asset-Prüfung, idempotentes Schreiben |
| `templates/performance-dudes.json` | Gearbeitetes Beispiel inkl. privatem Asset-Repo-Fall |
| `commands/iterm-profile.md` | `/iterm-profile` — geführter Ablauf |

## 5. User Stories & Acceptance Criteria

### US-term-1 — Ein Projekt bekommt eine erkennbare Terminal-Identität

Als jemand mit mehreren parallelen Projekten will ich am Terminal sofort sehen,
welches Projekt ich vor mir habe.

- **AC-term-1-1** — Das erzeugte Profil enthält `Bound Hosts` mit dem **absoluten**
  Projektpfad. (Dies ist das Feld, das den automatischen Wechsel auslöst; ohne es
  ist das Profil nur manuell wählbar.)
- **AC-term-1-2** — Das Profil enthält `Badge Text` in der Form
  `<emoji> \(session.name)`, wobei der Backslash im JSON verdoppelt ist
  (`"\\(session.name)"`). Ein einfacher Backslash ergibt einen literalen,
  unaufgelösten Badge.
- **AC-term-1-3** — `Badge Color` und `Tab Color` tragen **denselben** Farbton;
  `Badge Color` hat `Alpha Component` 0.5, `Tab Color` 1.0.
- **AC-term-1-4** — `Guid` ist stabil und aus dem Profilnamen ableitbar, damit ein
  erneuter Lauf dasselbe Profil trifft statt ein zweites anzulegen.

### US-term-2 — Ein Template überlebt die Maschinengrenze

Als jemand, der ein Template von einem Kollegen bekommt, will ich es installieren
können, ohne dessen Verzeichnisstruktur zu haben.

- **AC-term-2-1** — Ein Template enthält **keine** absoluten Home-Pfade, sondern den
  Platzhalter `{{HOME}}`.
- **AC-term-2-2** — Der Installer löst `{{HOME}}` in allen Feldern auf, nicht nur in
  den Asset-Kandidaten.
- **AC-term-2-3** — Bleibt nach der Auflösung ein `{{…}}`-Token in `Bound Hosts` oder
  `Working Directory` stehen, bricht der Installer mit einer Meldung ab, statt ein
  unbrauchbares Profil zu schreiben.
- **AC-term-2-4** — Lässt sich ein relativer Pfad nicht auflösen (Elternverzeichnis
  existiert nicht), bricht der Installer mit Meldung ab. Er darf **nicht** still
  `/<basename>` erzeugen: das ist ein plausibel aussehender absoluter Pfad auf die
  Dateisystemwurzel, und iTerm2 rendert ihn kommentarlos ohne Bild.

### US-term-3 — Fehlende Assets kosten nur das Asset

Als jemand ohne Zugang zum privaten Asset-Repo will ich das Profil trotzdem nutzen.

- **AC-term-3-1** — Für jedes Asset prüft der Installer eine **Kandidatenliste** und
  nimmt den ersten existierenden Pfad.
- **AC-term-3-2** — Existiert keiner, wird das betreffende Feld **weggelassen** (nicht
  mit einem toten Pfad geschrieben) und eine Warnung ausgegeben, die benennt, woher
  das Asset normalerweise stammt.
- **AC-term-3-3** — Begleitfelder, die ohne das Asset bedeutungslos sind, werden
  mitentfernt (konkret: `Icon` bei fehlendem `Custom Icon Path` — der Wert wählt
  „custom icon" und zeigte sonst ins Leere).
- **AC-term-3-4** — Das Profil wird in diesem Fall trotzdem installiert.

### US-term-4 — Wiederholtes Ausführen ist gefahrlos

- **AC-term-4-1** — Ein erneuter Lauf überschreibt das Profil gleichen Namens
  in-place und legt kein zweites an.
- **AC-term-4-2** — `--dry-run` schreibt nichts und gibt das resultierende JSON aus.
- **AC-term-4-3** — Das erzeugte JSON ist valide und von iTerm2 ladbar (Top-Level
  `Profiles`-Array).
- **AC-term-4-4** — Existiert am Ziel bereits ein Profil, dessen Inhalt vom zu
  schreibenden **abweicht**, wird es **nicht** überschrieben; der Installer bricht mit
  Hinweis ab, `--force` erzwingt das Ersetzen. Bei identischem Inhalt bleibt der Lauf
  ein stiller No-op. Begründung: iTerm2 markiert diese Profile `Rewritable`, Handarbeit
  daran ist also vorgesehen — Idempotenz ist nicht dasselbe Versprechen wie
  „deine Anpassungen überleben".

### US-term-5 — Das Wissen ist auffindbar, wenn es gebraucht wird

- **AC-term-5-1** — Der Skill triggert bei Anfragen nach Terminal-Theming pro
  Projekt, Session-Badge, Wallpaper im Terminal und automatischem Profilwechsel —
  auf Deutsch und Englisch.
- **AC-term-5-2** — Der Skill triggert **nicht** bei benachbarten, aber anderen
  Themen (Statuszeile, Shell-Prompt, Farbschema eines Editors, andere Terminals).
- **AC-term-5-3** — Der Skill benennt die drei Fehlerbilder, die iTerm2 **stumm**
  lässt: unaufgelöster Badge, totes Hintergrundbild, nicht schaltendes Profil.

## 6. Tests (Zuordnung siehe `tests/terminal/coverage.md`)

- `config-valid` — Manifest, Template-JSON, Marketplace-Eintrag, `bash -n`
- `script-run` — Installer im `--dry-run` gegen Template und Flags
- `skill-lint` — Frontmatter, Pflichtfelder, Badge-Escaping im Template
- Degradations-Pfad als eigener Fall (HOME auf ein leeres Verzeichnis gebogen)

## 7. Evals

Suite `triggering`, Regime **deterministisch** (STRUCTURED: es wird ein Label
vorhergesagt — feuert der Skill oder nicht). Ground Truth in
`plugins/terminal/evals/triggering/cases.yaml`, gemischt de/en, mit
Near-Miss-Fällen als Precision-Anker (AC-term-5-2).

## 8. Offen / Follow-ups

- **Verifikation des Auto-Switch ist nicht automatisiert.** `Bound Hosts` lässt sich
  statisch prüfen, das tatsächliche Umschalten nur in einer echten iTerm2-Sitzung.
  Als E2E-Lücke bewusst offen (SPEC-repo-conventions §6: Lücke benannt statt
  stillschweigend gelassen).
- **Nur macOS/iTerm2.** Andere Terminals siehe §3.
- **Light/Dark-Farben** werden vom Template getragen, vom Flag-Modus nicht — dort
  entsteht ein Profil ohne getrennte Hell/Dunkel-Werte.
