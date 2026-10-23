# ocr 0.1.4 — Textlayer behält Kyrillisch, `--redo` ersetzt kaputte OCR-Layer

## Was
- `searchbar._place()` bettete den unsichtbaren Textlayer in Base-14 `helv` ein (nur Latin-1).
  auge erkannte Kyrillisch korrekt, im PDF stand aber jeder Buchstabe als `·`.
- Neu: macOS `Helvetica.ttc` eingebettet + `subset_fonts()`; `durchsuchbar.py --redo`.
- Workflow-Syntaxcheck in vier Plugins parst den Skriptkörper als async-Funktion.

## Entscheidungen
- Font: PyMuPDF `china-s` verworfen (verliert ä ö ß „ beim Extrahieren), `Arial.ttf`
  verworfen (Leerzeichen als NBSP). Helvetica.ttc besteht den Round-Trip.
- `OCR_LANGS` unverändert: auge erkennt Kyrillisch mit `de-DE,en-US` gleich gut wie mit `ru-RU`.
- `--redo` nur für vollständig unsichtbaren Text; Redaction in ungedrehten Koordinaten
  (`page.rect * page.derotation_matrix`), Links werden neu gesetzt, Bildprüfung auf dem
  gespeicherten File über sortierte Hashes der dekodierten Streams. Links werden nur neu
  gesetzt, wenn die Redaction sie entfernt hat (Links außerhalb der Seitenbox überleben sie).
- Abbruch ohne Schreiben bei signierten/verschlüsselten PDFs, bei Text, der die Redaction
  überlebt (außerhalb der CropBox), und bei leerem OCR auf einer Seite mit altem Text.
- Temp-Datei per `mkstemp` im Zielordner, damit keine Nachbardatei überschrieben wird.

## Learnings
- `node --check` auf Node 24 erkennt Dateien mit `export` als ESM und lehnt das top-level
  `return` der Workflow-Skripte ab; unter Node 22 lief es noch durch.
- Eine Ganzseiten-Redaction mit `page.rect` lässt auf `/Rotate 90`-Seiten Text stehen und
  löscht Link-Annotationen.

## Follow-ups
- §9/§10 laufen auf dem Linux-Runner nicht (kein `uv`, kein Helvetica.ttc) — Issue #79.
- Inline-Images (`BI…EI`) prüft die Pixel-Kontrolle nicht; nur Bilder mit xref.
