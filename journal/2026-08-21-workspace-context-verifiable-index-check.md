# workspace-context — die Prüfung des Index war nicht falsifizierbar

**Datum:** 21. August 2026
**Auslöser:** Einrichtung des Plugins auf einem echten Repository (`closer`,
rund 7.000 Zeilen Prosa in Specs, Plänen, Review und Katalog).

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

## Warum das kein Anwendungsfehler ist

Beides sind Eigenschaften der Laufzeit:

- Ein Index, der **nach** dem Sitzungsstart entsteht, ist in dieser Sitzung über
  MCP nicht erreichbar. Genau deshalb existiert der `sessionStart`-Hook — er läuft,
  bevor der MCP-Server den Inhalt braucht.
- `ctx_search` bedient zwei Speicher. Beide sind nützlich, aber nur der Dateiindex
  ist vollständig und aktuell.

Ein Prüfschritt, der auf einem gesunden Index scheitern und auf einem fehlenden
bestehen kann, ist kein Prüfschritt. Er ist schlimmer als keiner, weil er
Sicherheit vortäuscht.

## Was geändert wurde

Schritt 7 verweist jetzt auf einen eigenen Abschnitt **„Verifying the index"**, der
beide Effekte benennt und eine **falsifizierbare** Prüfung vorschreibt:

1. Ein Begriff, der in einer Datei steht und **nie im Sitzungskontext war** —
   etwas, das ein Kollege oder ein Subagent geschrieben hat. Wer mit einem Begriff
   prüft, über den er gerade geredet hat, prüft sein eigenes Gedächtnis.
2. Suche über die **CLI**, und die `Source:`-Zeile bestätigen. Diese Zeile ist das
   einzige, was einen Datei- von einem Gedächtnistreffer unterscheidet.
3. Die Hook-Nutzlast getrennt prüfen — sie beantwortet eine andere Frage.

Dazu ein zweiter Abschnitt zur **Prüfung der Ausschlüsse**. Nachzuweisen, dass ein
Geheimnis nicht im Index steht, indem man danach sucht und nichts findet, ist
keine Prüfung: „kein Treffer" ist auch das Ergebnis einer kaputten Suche.
Falsifizierbar wird es erst mit einem Begriff, der in einer ausgeschlossenen
**und** in einer erlaubten Datei vorkommt — die Suche muss die erlaubten liefern
und die ausgeschlossene nicht. Beim Einrichten fand die Suche nach einem
Schlüsselnamen drei Quelldateien und nicht `.env.local`; erst diese Fassung sagt
etwas aus.

## Nicht geändert

Der Rest des Vertrags trägt. Die Vorlagen, die Ausschlusslisten, der Fehlerpfad des
Hooks und die Sicherheitsregeln haben sich in der Anwendung bewährt — der Hook
meldete bei fehlendem `context-mode` sauber auf stderr und mit Exit 1.

**AC:** AC-WC-2-4 (neu) · **Spec:** `specs/workspace-context/0001_product_workspace-context_public.md`
