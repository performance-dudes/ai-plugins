# 2026-07-25 — `mechanic`: Routing-Karte per `SessionStart`-Hook in den Context

Das Plugin bekommt seine erste Hook-Komponente: ein `SessionStart`-Hook injiziert die
Routing-Kaskade als `additionalContext`. Version 0.4.0 → 0.5.0.

## Motivation — die Regel war nie im Context

Beim Vergleich mit einem OpenCode-Harness (`opencode-team-harness`, TeamBank) fiel eine
strukturelle Lücke auf. OpenCode lädt über `instructions: ["…/AGENTS.md"]` bei **jedem**
Start eine Regeldatei ins Modell. Claude Code hat dafür kein Plugin-Äquivalent: ins
Modell kommt von einem Agent **nur** das Frontmatter-Feld `description:`.

Damit stand die eigentliche Kern-Promise des Plugins — die Kaskade, die `inline`-Route,
die Round-up-Asymmetrie — ausschließlich im README, und der wird **nie** geladen. Der
Orchestrator sah zwei Werkzeuge, aber nicht die Regel, wann welches. Besonders teuer:
Ohne die `inline`-Route lernt er nie, dass ein **einzelnes** triviales Item gar nicht
delegiert gehört — genau der häufigste reale Fehler.

Der einzige Plugin-Weg in den Claude-Code-Context ist ein Hook mit `additionalContext`.

## Entscheidungen

- **`SessionStart`, nicht `UserPromptSubmit`.** Einmal je Session-Abschnitt statt jeden
  Turn, und `SessionStart` feuert auch auf `compact` — die Regel überlebt damit die
  Verdichtung, die sie sonst als Erstes verlöre.
- **Injizieren, nicht duplizieren.** Das Script `cat`t `hooks/routing-card.md`; es hält
  keine eigene Kopie. Der Test prüft `additionalContext` **byte-identisch** gegen die
  Karte — Drift ist damit ausgeschlossen (Repo-Doktrin: das reale Objekt testen).
- **Context-Budget als AC (AC-4-8, < 1400 Zeichen).** Der Block liegt in **jedem**
  Session-Abschnitt jedes Nutzers — seine Länge ist Dauerlast. Erste Fassung: 2760
  Zeichen (~700 Tokens), viel zu teuer. Neu geschrieben **für ein LLM statt für
  Menschen**: nur Delta gegenüber dem, was ohnehin im Context steht. Die beiden
  Agent-Descriptions liefern bereits „was ist trivial" und „wann hand-back" — das
  gehört nicht noch einmal in die Karte. Ergebnis **1011 Zeichen (~252 Tokens)**, −64 %.
  Prosa und Begründung leben im README/docs. Über Budget → kürzen, nie Budget erhöhen.
- **Zero-dep, fail-open.** Reines bash (kein `jq`/`python`/`node`) — ein Hook, der nicht
  laufen kann, fällt still aus. JSON-Escaping per Parameter-Expansion. Fehlende oder
  unlesbare Karte → Exit 0, leere Ausgabe; eine Session darf daran nie scheitern.
- **Kein Enforcement.** Nur Kontext, kein `PreToolUse`-Veto, kein Umschreiben von
  Aufrufen. Die Entscheidung trifft weiter der Aufrufer — jetzt informiert statt blind.
  §3 der Spec wurde entsprechend präzisiert (vorher: „keine Hooks" pauschal).

## Neu: Parallelisierung

Bis 0.4.0 sagte weder Description noch README etwas dazu, **wie** ein Batch abgearbeitet
wird. Die Karte ergänzt es: N Agents in **einem** Message-Block statt sequenziell; ein
Agent je unabhängigem Chunk, nie mehr Agents als Chunks; Read-only-Fan-out immer sicher;
**schreibender** Fan-out nur mit **disjunkten** Datei-Mengen (sonst sequenziell);
parallelisieren innerhalb einer Stufe, abhängige Stufen warten.

Die Disjunktheits-Bedingung ist die einzige Regel mit Korrektheits-, nicht nur
Kostenwirkung: zwei Agents auf derselben Datei verlieren Updates.

## Geliefert

- `plugins/mechanic/hooks/routing-card.md` — die Karte, einzige Quelle (1020 Byte Datei,
  1011 Zeichen injiziert; AC-4-8 misst die Datei gegen 1400).
- `plugins/mechanic/hooks/sessionstart-routing.sh` — zero-dep, fail-open.
- `plugins/mechanic/hooks/hooks.json` — `SessionStart`-Registrierung via `${CLAUDE_PLUGIN_ROOT}`.
- Spec: §2 (Begründung), §3 (Nicht-Ziele präzisiert), **US-mech-4** mit AC-4-1…AC-4-8, §5, §6.
- `tests/mechanic/run.sh` — neue Tiers `script-run` + `hook-behavior`: Hook real
  ausführen, JSON prüfen, Drift gegen die Karte, Budget, Zero-dep, Fail-open.
- README, `docs/mechanic/mechanic.md`, plugin.json 0.5.0.

## Verifiziert

- `bash tests/mechanic/run.sh` → PASS (21 Checks, davon 9 neu).
- `bash tests/run-all.sh` → PASS (gesamtes Repo).
- Hook aus dem **installierten** Cache-Pfad gegen alle vier Quellen (`startup`,
  `resume`, `clear`, `compact`) → je valides JSON, 1011 Zeichen.
- Fehlende Karte → Exit 0, leere Ausgabe.
- **AC-4-7 (e2e) bestätigt** — frische Session nach der Installation: die Karte liegt
  als `SessionStart hook additional context` im Modell-Context, vollständig und
  wörtlich (alle vier Routen inkl. `INLINE`, Round-up-Regel, Parallelisierungs-Block).
  Damit ist die Kette end-to-end belegt: `hooks.json` → Script → Karte → Host → Modell.
- **Gegenprobe nach `/compact` bestanden** — die Karte ist nach der Verdichtung erneut
  vollständig im Context. Das war die eigentliche Wette hinter der Wahl von
  `SessionStart` (feuert auf `source: "compact"`) statt `UserPromptSubmit`: die Regel
  überlebt genau das Ereignis, das sie sonst als Erstes verlöre. Jetzt gemessen statt
  nur konstruiert.

## Nachtrag — Versions-Drift, von der CI gefangen

Der erste Push lief lokal grün, aber `validate.yml` schlug fehl:
`marketplace 0.3.0 != plugin.json 0.5.0`. Der Bump war nur an **einem** der beiden
Orte passiert. Beides war schon vor diesem Commit inkonsistent (0.3.0 ↔ 0.4.0), der
Bump hat den Abstand nur vergrößert.

Die eigentliche Lehre ist die Test-Lücke: AC-2-1 prüfte, **ob** `mechanic` im
Marketplace registriert ist — nicht, **mit welcher Version**. Damit konnte die lokale
Suite grün sein, während die Auslieferung eine andere Version gezogen hätte als die
getestete. Neu: **AC-2-3** koppelt beide Versionen und ist in `tests/mechanic/run.sh`
in beide Richtungen verifiziert (künstlich erzeugter Drift → Exit 1).

Dabei fiel auf: `validate.yml` war **seit dem 6. Juli** (`4334995`) rot, nicht erst
seit diesem Commit — dort wurde `context-scout` auf Sonnet 4.6 gepinnt und
`context-aware`s plugin.json auf 0.1.1 gehoben, ohne den Marketplace-Eintrag
nachzuziehen. Acht Runs in Folge rot. Das ist die zweite Lehre neben der Test-Lücke:
ein dauerhaft roter Check verliert seine Signalwirkung, weil alle lernen, ihn zu
überlesen — der Fund war reiner Zufall, weil dieser Push zufällig denselben Job
auslöste.

Nach Rückfrage separat nachgezogen (`13cd7ec`): der Code-Change lag ohnehin seit drei
Wochen auf main, das Anheben der Versionsnummer ist Buchhaltung, kein neuer Release.
Seither sind **alle sieben** Plugins konsistent und `validate.yml` ist grün.

## Offen
- **Die Evals messen die Karte noch nicht.** `evals/routing/build_router_prompt.py`
  injiziert nur die Agent-Descriptions, nicht die Karte — die gemessene pass³ = 1.0
  gilt also für den Zustand *ohne* Hook. Ob die Karte die Trefferquote weiter hebt, ist
  offen; die Suite steht ohnehin am Deckeneffekt. Für **Parallelisierung** gibt es
  bislang **gar keine** Cases — das ist die nächste sinnvolle Erweiterung.
- Lokal installiert nach `cache/ai-plugins/mechanic/0.5.0` (Registry-Backup unter
  `installed_plugins.json.bak.20260725-004607`) — dort wurde auch e2e verifiziert.
  Nutzer der Marketplace-Version ziehen 0.5.0 erst mit dem nächsten
  `claude plugin marketplace update` plus **frischer Session** (Agent- und
  Hook-Registry werden bei Session-Start gelesen, nicht hot-reloaded).
