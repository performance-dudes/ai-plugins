# Product-Spec: anti-slop — LLM-Slop in deutscher und englischer Prosa finden

Spec-ID: `SPEC-anti-slop` · Status: Entwurf · Datum: 2026-09-08 ·
Autor: Benny (mit Claude)

## 1. Thema

Ein Plugin, das den **maschinellen Beiklang** aus Prosa entfernt: die Wörter,
Wendungen und Kadenzen, die in generiertem Text statistisch überrepräsentiert
sind und einen Text als KI-geschrieben lesbar machen — unabhängig davon, ob er
es ist. Zwei Register (Geschäftsprosa, Erzählprosa), zwei Sprachen (Deutsch,
Englisch), plus sprachneutrale Artefakte.

Ausgeliefert werden ein Skill (`anti-slop`), drei Termlisten, eine
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
- **Die deutsche Liste ist für dieses Plugin entstanden.** Sie ist kuratiert,
  nicht frequenzgemessen (siehe §7).
- **Listen gehören nicht in den Kontext.** 1843 Einträge (1836 eindeutige
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
      slop-list-en-extra.json    1190  kuratiert englisch
      slop-list-de.json           496  kuratiert deutsch
      slop-list-universal.json    157  sprachneutral
      severity-overrides.json      71  hard -> soft
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
| AC-1-4 | Überlappende Einträge zählen **einmal**: „is a testament to" ist ein Treffer, nicht vier. Bei Überlappung gewinnt ein harter Treffer vor einem längeren weichen, danach der längste. | `script-run` |
| AC-1-5 | Exit-Code 0 = kein Treffer, 1 = mindestens ein Treffer (auch weich), 2 = Entwurf nicht lesbar (fehlt, kein UTF-8) — ohne Traceback. | `script-run` |

### US-slop-2 — Sprache und sprachneutrale Tells

| AC | Soll | Test |
|----|------|------|
| AC-2-1 | Ohne `--lang` wird die Sprache aus dem Text erkannt (deutscher Text → `de`). | `script-run` |
| AC-2-2 | `slop-list-universal.json` wird bei **jedem** Lauf geladen, unabhängig von der Sprache. | `script-run` |
| AC-2-3 | Die Universal-Liste wird **vor** den Sprachlisten geladen, damit ihre Severity gewinnt (Namen bleiben weich) — auch unter `--hard-only`. Geprüft an einer Fixture (`ANTI_SLOP_DATA`), in der derselbe Term universal-weich und sprachlich-hart steht: In den echten Listen hätte die Reihenfolge keine beobachtbare Wirkung. | `script-run` |

### US-slop-3 — Trennschärfe

Als Nutzer will ich, dass ein Treffer etwas bedeutet: schlägt der Prüfer auf
normaler Fachprosa an, lerne ich, ihn zu überlesen.

| AC | Soll | Test |
|----|------|------|
| AC-3-1 | Von Menschen geschriebene Fachprosa erzeugt **höchstens 1,0** harte Treffer je 1000 Wörter. | `eval` |
| AC-3-2 | Generierter Slop-Text erzeugt **mindestens 50** harte Treffer je 1000 Wörter. | `eval` |
| AC-3-3 | Die Eval misst beide Richtungen und meldet Precision, Recall und Specificity. | `eval` |
| AC-3-4 | Literatur, die vor 1926 erschienen ist, erzeugt **höchstens 1,0** harte Treffer je 1000 Wörter — je ein Case pro Sprache. | `eval` |
| AC-3-5 | Ein generierter deutscher Case trifft **ausschließlich über Flexion**: Ohne Stamm-Suffix fällt er unter die Schwelle. | `eval` |

**Warum eine eigene AC.** Die erste Fassung der zusammengeführten Liste erzeugte
auf 17 500 Wörtern technischer Dokumentation **5,5** harte Treffer je 1000 Wörter:
`aria` traf jedes `aria-label`, dazu `transform`, `manifest`, `key`, `dynamic`.
Ein Prüfer mit dieser Rate ist wertlos, weil niemand seine Meldungen mehr liest.
`severity-overrides.json` senkte den Wert auf **0,5**, ohne einen echten Befund zu
verlieren. Rot heißt handeln, nicht gewöhnen.

**Der zweite Messpunkt: Literatur vor 1926.** Ein Text, der älter ist als jedes
Sprachmodell, kann keinen KI-Slop enthalten — jeder harte Treffer darin ist per
Konstruktion ein Fehlalarm. Auf 1,04 Mio. Wörtern (Austen, Dickens, Melville,
Conrad, Fitzgerald · Goethe, Kant, Th. Mann, Kafka) lag die Rate bei **0,5 bis
1,7**, am höchsten bei Kant, dessen `Mannigfaltige` ein Fachbegriff und keine
Floskel ist. Nach den Register-Overrides: **0,0 bis 0,2**, bei unveränderter
Trennschärfe (generierter Text 128–293). AC-3-4 hält diesen Messpunkt fest, damit
er nicht stillschweigend zurückfällt.

Beide Messungen waren einmalig; Korpus und Messskript liegen nicht im Repo. Im Repo
reproduzierbar sind nur die Eval-Cases (h05/h06 als Literatur-Stichprobe).

### US-slop-4 — Datenintegrität

| AC | Soll | Test |
|----|------|------|
| AC-4-1 | Jede Listendatei ist valides JSON; jeder Eintrag ist ein Array mit String an Position 0. | `config-valid` |
| AC-4-2 | Kuratierte Listen führen `[term, category, severity]` mit `severity` aus {`hard`,`soft`}. | `config-valid` |
| AC-4-3 | Keine toten Einträge: keine Slash-Alternativen, Auslassungspunkte oder eckigen Klammern außerhalb der Kategorie `placeholder`, und keine Beschreibungen statt Suchstrings (Anführungszeichen, `label: …`, Platzhalter `x`/`y`/`z`) — sie können als Literal nie matchen. Ausgenommen sind URL-Artefakte (`utm_source=chatgpt.com`), deren Schrägstrich Teil des gesuchten Strings ist. | `config-valid` |
| AC-4-4 | Keine Duplikate innerhalb einer Liste. | `config-valid` |
| AC-4-5 | Jeder Eintrag der Kategorie `stock-name` ist `soft` — Stock-Namen sind auch reale Personennamen. Erfundene **Orte** stehen deshalb unter `stock-place` und dürfen hart bleiben: `Eldoria` und `Whisperwood` gehören niemandem. | `config-valid` |
| AC-4-6 | Jeder Schlüssel in `severity-overrides.json` trifft einen Listeneintrag **exakt**, inklusive `*`. Ein Schlüssel ohne Entsprechung ist wirkungslos und täuscht eine Entschärfung vor, die es nicht gibt. | `config-valid` |

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
