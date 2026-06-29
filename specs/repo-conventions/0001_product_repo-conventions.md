# Product-Spec: Plugin-Repo-Konventionen (Struktur, Tests, Methodik)

Spec-ID: `SPEC-repo-conventions` · Status: Entwurf · Datum: 2026-06-29 ·
Autor: Felix (mit Claude)

Gilt für die **Marketplace-Repos** `ai-plugins-internal` und `ai-plugins`.
Referenzen: `ai-plugins` `example` (PR #35) und `context-aware` (PR #38) bauen die
Struktur bereits vor; die PD-Methodik lebt in den Skills `craft/spec-driven-tdd`,
`craft/plugin-hygiene`, `knowledge/docs`, `knowledge/journal`.

---

## 1. Thema

Ein Marketplace-Repo enthält **mehrere Plugins** als Unterordner plus die
**Meta-/Prozess-Artefakte** (Specs, Docs, Journal, Pläne, Tests). Diese Spec legt
**einheitlich** fest: wo was liegt, wo Tests je Produktart liegen, wie Coverage
nachgewiesen wird, und dass die Arbeitsweise (Spec-Driven TDD) **verpflichtend**
ist. Ziel: jedes Plugin ist für sich verständlich, beweisbar gesund, und kein
PR driftet (Code ohne Spec/Docs/Journal).

## 2. Warum (Begründung)

- **Plugin-Ordner müssen rein bleiben.** Jede `.md` in `commands/`/`agents/` wird
  als **echtes** Command/Agent geladen — Doku/Specs/Tests im Plugin erzeugen
  Geister-Komponenten und brechen das Plugin. Meta-Artefakte gehören daher auf
  **Repo-Top-Level**, neben die Plugins.
- **specs/ nie in docs/.** Absicht (Felix): Spec = Intent/„was & warum", Docs =
  Erklärung der Komponenten. Vermischt man sie, verliert man beides.
- **Drift verhindern.** Code ohne Spec-/Doc-/Journal-Anpassung „darf nicht
  passieren" — sonst weiß niemand, wie weit die Umsetzung ist.

## 3. Struktur (Soll)

```
<marketplace-repo>/
  README.md
  <plugin>/                 # NUR Runtime-Vertrag (.claude-plugin/, skills/, commands/,
                            #   agents/, hooks/, mcp/, output-styles/, themes/, workflows/, monitors/)
  specs/
    <plugin>/               # benannte Specs, z. B. 0001_product_<plugin>_<topic>.md
    <cross-cutting>/        # repo-weite Specs (z. B. diese)
  docs/
    <plugin>/               # eine Seite pro Komponente; übergreifendes an der docs-Wurzel
  journal/                  # YYYY-MM-DD-<slug>.md, flach — eine Zeitachse fürs Repo
  plans/                    # aktive Mehr-Schritt-Pläne; nach Abschluss gelöscht
  tests/                    # Aggregator run-all.sh + tests/<plugin>/ (siehe §5)
```

Regeln: **specs/ nie in docs/** · Plugins bleiben rein · `specs`/`docs` mit
Plugin-Unterordner · `journal`/`plans` flach.

**Spec-Benennung — am Namen als product/tech erkennbar.** Schema
`<NNNN>_<type>_<plugin>[_<topic>].md`:
- `<NNNN>` — Laufnummer (z. B. `0001`), ordnet/identifiziert.
- `<type>` — **`product`** oder **`tech`**; macht die Spec **am Dateinamen
  erkennbar** (Pflicht).
- `<plugin>` und optional `<topic>` — beschreibend.

Beispiel: `0001_product_agent-sync_teammates.md`. Ob flach (`specs/<datei>`) oder je
Plugin (`specs/<plugin>/<datei>`) ist **fast egal** — solange der Name die Spec
klar als product/tech ausweist. Eine Spec-Datei **ohne** `_product_`/`_tech_`-Token
ist ein Verstoß (vom Struktur-Test erzwungen, §8 AC-1-4). `README.md` ist
ausgenommen.

## 4. Methodik ist Pflicht (Spec-Driven TDD)

Die Schleife aus `craft/spec-driven-tdd` ist **verbindlich**, nicht optional:
**(1)** Spec schreiben/erweitern + PR sofort öffnen → **(2)** Tests für die neuen
Acceptance Criteria → **(3)** Plan in `plans/` bei Mehr-Schritt-Arbeit → **(4)**
implementieren bis **Spec + Tests + Code + Docs + Context (CLAUDE.md/README)** in
sync sind → **(5)** Plan löschen, Journal-Eintrag, Docs/Context finalisieren →
**(6)** Merge **nur** auf Freigabe.

Harte Regeln:
- **Kein Code-PR ohne Spec-Anpassung.** Gleiches für Docs, Context, Journal — je
  nachdem, was die Änderung berührt.
- **Vor Start prüfen, ob ein PD-Skill/Plugin die Aufgabe abdeckt** — laden, keinen
  Prozess erfinden.
- **Umsetzungsstand muss sichtbar sein:** `plans/` aktuell halten; offene Punkte
  einer Spec, die beim Merge noch offen sind, **müssen als GitHub-Issue** existieren,
  bevor gemergt wird.
- Ist etwas nach dieser Vorgabe **nicht sinnvoll/möglich**, wird das **im PR
  begründet** (statt still abzuweichen).

## 5. Tests — nach Produktart, als Pyramide

„Das Plugin ist das Produkt" → getestet wird das **ganze** Plugin, nicht nur Code.
**Wo** die Tests liegen, richtet sich nach der **Produktart** (ein- oder
zweiteilig, je nachdem was sinnvoll ist) und wird **dokumentiert** (`tests/README.md`
+ `tests/<plugin>/README.md`: wo sie liegen, wie man sie nutzt).

**Testpyramide** (unten breit/billig, oben schmal/teuer):
1. **Statisch/Config** (Basis): JSON/JS valide, Frontmatter wohlgeformt, Referenzen
   auflösbar, Skript-Syntax (`bash -n`, `node --check`).
2. **Unit:** Hook-/Skript-Logik gegen Beispiel-Inputs; MCP-Unit (Build-Subprojekt).
3. **Integration:** Hook-Verhalten, MCP-Integration, Skill-Verhalten.
4. **E2E** (Spitze, wenige): echte Claude-Session übt das Plugin (z. B. Hook-
   Enforcement real geblockt).

**Ablage je Produktart:**
- **Einteilig** (Skills/Hooks/Commands ohne Build): alles unter `tests/<plugin>/`
  (Top-Level) + im `run-all.sh`.
- **Zweiteilig** (Plugin mit Build-Subprojekt, z. B. TS-MCP): **Unit-Tests
  code-nah** beim Build (`<plugin>/mcp/test/`), **Plugin-Ebene/Integration/E2E**
  unter `tests/<plugin>/`. `run-all.sh` ruft beide.
- Maßgeblich ist **Best Practice der jeweiligen Produktart**; die Wahl wird in
  `tests/<plugin>/README.md` begründet.

## 6. Coverage-Nachweis (drei Achsen)

Test-**Typen** je Plugin: `config-valid` · `script-run` · `skill-lint` ·
`hook-behavior` · `mcp-unit` · `mcp-integration` · `e2e`.

Traceability-Matrix (`tests/<plugin>/coverage.md`, später generierbar):
- **spec : code** — jede Acceptance Criterion → umsetzende Komponente(n).
- **spec : test (pro Typ)** — jede AC → prüfender Test, je Typ.
- **code : tests (pro Typ)** — jede Komponente → abdeckende Tests, je Typ.

Lücken in der Matrix sind **Merge-Gate-relevant**: entweder geschlossen oder als
Issue getrackt (siehe §4).

## 7. Erzwingung (drei Hebel)

1. **Skills schärfen:** `craft/spec-driven-tdd` als Default-Regel; `plugin-hygiene`
   aktiviert craft+knowledge pro Projekt; „erst Skill prüfen" als Vorbedingung.
2. **Workflow** (in `craft`): ein „ship"-Workflow, der die Schleife abfährt und
   **PR-Vollständigkeit** prüft (Spec/Tests/Docs/Journal berührt? Plan aktuell?
   offene Spec-Punkte → Issue?).
3. **CI-Gate:** `tests/run-all.sh` grün **und** ein „Spec-Touch"-Check (Code-Diff
   ohne Spec/Doc/Journal-Diff → rot, mit Begründungs-Ausnahme via PR-Label/Marker).

## 8. User Stories & Acceptance Criteria

### US-conv-1 — Struktur vorhanden & rein
| AC | Soll | Test |
|----|------|------|
| AC-1-1 | Repo hat Top-Level `specs/ docs/ journal/ plans/ tests/`; kein Plugin-Ordner enthält `specs/`/`docs/`/`journal/`/`plans/`. | `tests/structure/*` (config-valid) |
| AC-1-2 | Keine `specs/` unterhalb von `docs/` (repo-weit). | `tests/structure/*` |
| AC-1-3 | Jedes Plugin hat einen Eintrag in `specs/<plugin>/` **oder** ist als „spec-frei" dokumentiert. | `tests/structure/*` |
| AC-1-4 | Jede Spec-Datei unter `specs/` (außer `README.md`) trägt im Namen einen `_product_`- oder `_tech_`-Token (am Namen als product/tech erkennbar). | `tests/structure/check.sh` |

### US-conv-2 — Tests dokumentiert & lauffähig
| AC | Soll | Test |
|----|------|------|
| AC-2-1 | `tests/run-all.sh` existiert, läuft offline grün und ruft alle Plugin-Test-Suites. | `tests/run-all.sh` (self) |
| AC-2-2 | `tests/README.md` beschreibt Pyramide + Ablage-Regel; je Plugin `tests/<plugin>/README.md` nennt Ort & Nutzung. | review |

### US-conv-3 — Methodik erzwungen
| AC | Soll | Test |
|----|------|------|
| AC-3-1 | CI-Gate schlägt fehl, wenn ein Code-Diff ohne Spec/Doc/Journal-Diff kommt (ohne Begründungs-Marker). | CI |
| AC-3-2 | `craft`-Workflow prüft PR-Vollständigkeit und meldet fehlende Artefakte. | workflow self-test |

## 9. Phasen (Rollout)

- **PR 1 (diese):** Konventions-Spec + Top-Level-Struktur + Fix der Spec-in-docs-
  Verletzung (agent-sync) + Plan + Journal. Struktur-Tests (config-valid).
- **PR 2:** Erzwingung — Skills schärfen, `craft`-„ship"-Workflow, CI-Gate.
- **PR 3+:** Migration je Plugin (Docs/Specs/Tests nach Konvention) + Angleich
  `ai-plugins` (mit `example`/`context-aware` als Vorlage).

## 10. Offen / im PR zu begründen

- Genaue Form des „Spec-Touch"-CI-Checks (Pfad-Heuristik vs. PR-Label-Ausnahme).
- Coverage-Matrix zunächst **handgepflegt**; Generator später (begründet, wenn
  Tooling fehlt).
