# workspace-context — die Prüfung des Index war nicht falsifizierbar

**Datum:** 21. August 2026
**Auslöser:** Einrichtung des Plugins auf einem privaten Produkt-Repository.

## Was passiert ist

Der Vertrag des Skills verlangt in Schritt 7, den Index über einen fokussierten
`ctx_search` zu prüfen. Genau das wurde getan — und die Prüfung hat **zweimal
hintereinander etwas anderes gemessen als gemeint war.**

Erst schlug sie fehl: Nach einem erfolgreichen Index (192 Dateien / 1.160
Abschnitte) lieferte `ctx_search` mit Quell-Etikett **keinen einzigen Treffer**.
Der Index war aber in Ordnung — die CLI (`context-mode search`, mit der
Projektwurzel als Arbeitsverzeichnis) fand die gesuchte Passage sofort, samt
Quellpfad.

Dann bestand sie, ohne etwas zu belegen: Ein Aufruf ohne Filter lieferte
inhaltlich passende Treffer — aber alle trugen `[current-session | … | batch:…]`
und stammten damit aus dem **Sitzungsgedächtnis**, nicht aus dem Dateiindex.
Inhalt richtig, Quelle falsch. Ohne den Blick auf die Herkunftszeile wäre das als
bestandene Prüfung durchgegangen.

## Ursachen

- **Falsch negativ.** Die erste Deutung — „ein Index, der nach dem Sitzungsstart
  entsteht, ist über MCP nicht erreichbar" — hielt dem Cold-Review nicht stand:
  CLI und `ctx_search` rufen dieselbe Suche auf derselben Datenbank auf, gewählt
  über das Projektverzeichnis. Ein CLI-Treffer ohne MCP-Treffer spricht für eine
  Sitzung in einem anderen Projektverzeichnis als dem indexierten. Nachgemessen
  ist das nicht; der Skill schreibt deshalb vor, die Sitzung an der indexierten
  Wurzel zu starten, statt einen Sitzungseffekt zu behaupten.
- **Falsch positiv.** `ctx_search` bedient Dateiindex und Sitzungsgedächtnis. Beide
  Treffer tragen `[current-session | … | <source>]`; unterscheiden lässt sie nur der
  Source-Teil (`batch:…` ist Gedächtnis). Mit Filter auf das Quell-Etikett fällt
  der Gedächtnistreffer weg.

Ein Prüfschritt, der auf einem gesunden Index scheitern und auf einem fehlenden
bestehen kann, ist kein Prüfschritt. Er ist schlimmer als keiner, weil er
Sicherheit vortäuscht.

## Was geändert wurde

Schritt 7 verweist jetzt auf einen eigenen Abschnitt **„Verifying the index"**, der
beide Effekte benennt und eine **falsifizierbare** Prüfung vorschreibt:

1. `context-mode search` mit dem Quell-Etikett; jeder Treffer muss die erwartete
   `Source:`-Zeile tragen — der Pfad entscheidet, nicht der Inhalt.
2. Im Workspace je ein Begriff aus mindestens zwei Geschwister-Repos.
3. Die Hook-Nutzlast getrennt prüfen — sie beantwortet eine andere Frage.

Dazu ein zweiter Abschnitt zur **Prüfung der Ausschlüsse**. Nachzuweisen, dass ein
Geheimnis nicht im Index steht, indem man danach sucht und nichts findet, ist
keine Prüfung: „kein Treffer" ist auch das Ergebnis einer kaputten Suche.
Falsifizierbar wird es erst mit einem Begriff, der in einer ausgeschlossenen
**und** in erlaubten Dateien vorkommt — die Suche muss die erlaubten liefern und
die ausgeschlossene nicht.

Der Cold-Review fand, dass auch diese Prüfung zunächst nicht falsifizierbar war:
`context-mode search` liefert ohne `--limit` 3 Treffer. Die „drei Quelldateien"
beim Einrichten waren genau dieses Limit; eine durchgerutschte Datei an Position
vier wäre unsichtbar geblieben (nachgestellt mit fünf erlaubten Dateien und einer
durchgerutschten). Jetzt: erlaubte Dateien vorab mit `rg -l` zählen, mit
`--limit 100` suchen, bestehen nur, wenn alle erlaubten erscheinen, die
Trefferzahl unter dem Limit bleibt und kein ausgeschlossener Pfad auftaucht.
`validate.sh` prüft die Bestandteile der Anweisung (AC-WC-2-4); das
Laufzeitverhalten von Context Mode selbst ist nicht live getestet.

## Nicht geändert

Der Rest des Vertrags trägt. Die Vorlagen, die Ausschlusslisten, der Fehlerpfad des
Hooks und die Sicherheitsregeln haben sich in der Anwendung bewährt — der Hook
meldete bei fehlendem `context-mode` sauber auf stderr und mit Exit 1.

**AC:** AC-WC-2-4 (neu) · **Spec:** `specs/workspace-context/0001_product_workspace-context_public.md`
