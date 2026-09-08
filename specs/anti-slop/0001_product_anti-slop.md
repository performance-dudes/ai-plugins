# Product-Spec: anti-slop — LLM-Slop in deutscher und englischer Prosa finden

Spec-ID: `SPEC-anti-slop` · Status: Entwurf · Datum: 2026-09-08 ·
Autor: Benny (mit Claude)

## 1. Thema

Ein Plugin, das den **maschinellen Beiklang** aus Prosa entfernt: die Wörter,
Wendungen und Kadenzen, die in generiertem Text statistisch überrepräsentiert
sind und einen Text als KI-geschrieben lesbar machen — unabhängig davon, ob er
es ist. Zwei Register (Geschäftsprosa, Erzählprosa), zwei Sprachen (Deutsch,
Englisch), plus sprachneutrale Artefakte.

Ausgeliefert werden ein Skill (`anti-slop`), vier Termlisten, eine
Severity-Override-Datei und ein Prüfskript.

## 2. Warum (Begründung)

- **Wortlisten allein reichen im Deutschen nicht.** Deutsch flektiert: eine
  `\b`-verankerte Suche nach `entscheidend` findet `entscheidende`,
  `entscheidender`, `entscheidendes` **nicht** — also genau die Formen, in denen
  das Wort vorkommt. Ein Grep über eine englische Liste findet in deutschem Text
  nahezu nichts. Das Prüfskript löst das über Stamm-plus-Endung.
- **Deutsche Slop ist nicht übersetzte englische Slop.** `tapestry` ist immer ein
  Tell; `zudem`, `nutzen` und `besonders` sind gewöhnliche deutsche Wörter, die
  erst in der Häufung überführen. Ohne diese Unterscheidung produziert eine
  deutsche Liste Rauschen statt Befunde.
- **Es gibt keine brauchbare öffentliche deutsche Liste.** Recherche über
  GitHub-Code-Suche, Gists und Web ergab englische Korpora in mehreren Varianten,
  aber nichts Vergleichbares auf Deutsch. Die deutsche Liste ist für dieses
  Plugin entstanden.
- **Listen gehören nicht in den Kontext.** 1894 Einträge (1856 eindeutige
  Terme) sind ein Datenbestand, kein
  Prompt. Geprüft wird per Skript, nicht durch Einlesen.

## 3. Struktur

```
plugins/anti-slop/
  .claude-plugin/plugin.json
  README.md
  skills/anti-slop/
    SKILL.md                      Einstieg + Index
    data/
      slop-list.json              517  upstream EQ-Bench, unverändert
      slop-list-en-extra.json     772  kuratiert englisch
      slop-list-de.json           496  kuratiert deutsch
      slop-list-universal.json    109  sprachneutral
      severity-overrides.json      45  hard -> soft
    references/                   business-prose · narrative-prose · german-prose
    scripts/check-slop.py         Prüfer
  evals/detection/                deterministische Trennschärfe-Messung
```

## 4. Begriffe

| Begriff | Bedeutung |
|---|---|
| **hart** | Tell für sich allein — `bahnbrechend`, `delve`. Raus, sofern nicht Zitat oder Fachbegriff. |
| **weich** | einzeln legitim — `zudem`, `umfassend`. Befund erst im Cluster. |
| **Dichte** | harte Treffer je 1000 Wörter. Die Kennzahl, die entscheidet — nicht der Einzeltreffer. |
| **Stamm-Eintrag** | Term mit `*` am Ende; matcht Stamm plus bis zu fünf Endungszeichen. |
| **Override** | Term, der trotz Listeneintrag als weich gewertet wird (Fachvokabular). |

## 5. User Stories & Acceptance Criteria

### US-slop-1 — Deutsche Flexion wird gefunden

Als Autor deutscher Texte will ich, dass der Prüfer die Formen findet, in denen
ein Wort tatsächlich vorkommt — sonst meldet er auf jedem deutschen Text null.

| AC | Soll | Test |
|----|------|------|
| AC-1-1 | Ein Stamm-Eintrag (`entscheidend*`) matcht `entscheidende`, `entscheidender`, `entscheidendes`. | `script-run` |
| AC-1-2 | Ein Eintrag ohne `*` matcht nur die Literalform. | `script-run` |
| AC-1-3 | Terme mit Satzzeichen am Rand (`Selbstverständlich!`) matchen trotz fehlender `\b`-Grenze. | `script-run` |

### US-slop-2 — Sprache und sprachneutrale Tells

| AC | Soll | Test |
|----|------|------|
| AC-2-1 | Ohne `--lang` wird die Sprache aus dem Text erkannt (deutscher Text → `de`). | `script-run` |
| AC-2-2 | `slop-list-universal.json` wird bei **jedem** Lauf geladen, unabhängig von der Sprache. | `script-run` |
| AC-2-3 | Die Universal-Liste wird **vor** den Sprachlisten geladen, damit ihre Severity gewinnt (Namen bleiben weich). | `script-run` |

### US-slop-3 — Trennschärfe

Als Nutzer will ich, dass ein Treffer etwas bedeutet: schlägt der Prüfer auf
normaler Fachprosa an, lerne ich, ihn zu überlesen.

| AC | Soll | Test |
|----|------|------|
| AC-3-1 | Von Menschen geschriebene Fachprosa erzeugt **höchstens 1,0** harte Treffer je 1000 Wörter. | `eval` |
| AC-3-2 | Generierter Slop-Text erzeugt **mindestens 50** harte Treffer je 1000 Wörter. | `eval` |
| AC-3-3 | Die Eval misst beide Richtungen und meldet Precision, Recall und Specificity. | `eval` |

**Warum eine eigene AC.** Die erste Fassung der zusammengeführten Liste erzeugte
auf 17 500 Wörtern technischer Dokumentation **5,5** harte Treffer je 1000 Wörter:
`aria` traf jedes `aria-label`, dazu `transform`, `manifest`, `key`, `dynamic`.
Ein Prüfer mit dieser Rate ist wertlos, weil niemand seine Meldungen mehr liest.
`severity-overrides.json` senkte den Wert auf **0,5**, ohne einen echten Befund zu
verlieren. Rot heißt handeln, nicht gewöhnen.

### US-slop-4 — Datenintegrität

| AC | Soll | Test |
|----|------|------|
| AC-4-1 | Jede Listendatei ist valides JSON; jeder Eintrag ist ein Array mit String an Position 0. | `config-valid` |
| AC-4-2 | Kuratierte Listen führen `[term, category, severity]` mit `severity` aus {`hard`,`soft`}. | `config-valid` |
| AC-4-3 | Keine toten Einträge: keine Slash-Alternativen, Auslassungspunkte oder eckigen Klammern außerhalb der Kategorie `placeholder` — sie können als Literal nie matchen. Ausgenommen sind URL-Artefakte (`utm_source=chatgpt.com`), deren Schrägstrich Teil des gesuchten Strings ist. | `config-valid` |
| AC-4-4 | Keine Duplikate innerhalb einer Liste. | `config-valid` |
| AC-4-5 | Jeder Eintrag der Kategorie `stock-name` ist `soft` — Stock-Namen sind auch reale Personennamen. Erfundene **Orte** stehen deshalb unter `stock-place` und dürfen hart bleiben: `Eldoria` und `Whisperwood` gehören niemandem. | `config-valid` |

### US-slop-5 — Herkunft nachvollziehbar

| AC | Soll | Test |
|----|------|------|
| AC-5-1 | `NOTICE` im Repo-Root nennt jede Fremdquelle mit Lizenz und URL. | `config-valid` |
| AC-5-2 | Die SKILL.md nennt je Listendatei ihre Quelle. | review |

## 6. Nicht-Ziele

- **Kein KI-Detektor.** Das Plugin bewertet Prosa, nicht Urheberschaft. Ein
  hoher Wert heißt „liest sich generisch", nicht „von einer KI geschrieben".
- **Kein Find-and-Replace.** Jeder Treffer ist eine Frage. Der Fix ist der
  konkrete Sachverhalt, nicht ein Synonym.
- **Keine Formatierungsprüfung.** Gleichförmige Satzlängen, Fettdruck-Muster und
  Emoji-Gliederung sind Beschreibungen, keine Suchstrings; sie stehen in den
  Referenzen, nicht in den Listen.
- **Kein Em-Dash-Verbot.** Der Gedankenstrich gilt vielen als KI-Merkmal, steht
  aber auf keiner Liste hier — das ist eine Hausstil-, keine Slop-Frage.

## 7. Offen

- Weitere Sprachen (fr/es) — erst wenn ein Bedarf da ist; die Struktur trägt sie.
- Die deutschen Terme sind kuratiert, nicht gemessen. Ein Korpus-Vergleich
  (deutscher LLM-Output gegen deutschen Menschentext) würde sie mit Frequenzen
  unterlegen. Als Issue zu tracken, nicht Merge-blockierend.
