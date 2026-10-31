# 2026-10-31 — `image-toolkit`: Foto → Scan (0.2.3)

## Anlass

Der Skill kannte Zuschnitt und Formatwandel, aber keinen Weg vom Handyfoto eines Dokuments zu einem
scannerartigen Ergebnis. Der Ablauf entstand an acht Fotos von vier Vorlagen und liegt jetzt als
`references/photo-to-scan.md` vor. Die Referenz enthält nur Technik, keine Dokumentinhalte.

## Entscheidungen

- **Kein Gemini auf Dokumenten:** KI-Schärfen kann Ziffern, Stempel und Unterschriften erfinden.
- **OpenCV misst, ImageMagick bearbeitet:** Die Referenz nennt die Werte statt ein weiteres Skript
  mitzuliefern; ein Agent setzt die Messung mit `uv` in wenigen Zeilen um.
- **Rahmen statt Papierkante:** Papierkanten sind eingerissen und gewölbt, Druckzeilen nicht.
- **Registrierung für verdeckte Rahmen:** Liegt ein Beleg auf dem Formular, fehlen die äußeren Linien.
  Der Rahmen kommt dann per SIFT und RANSAC vom freien Foto.

## Gemessen

- Maske nur über Helligkeit und Sättigung nahm Holz und Bildschirmspiegelung mit und fraß verschattetes
  Papier an. Der Seed mit warmem Lab-`b` und GrabCut löste beides.
- Registrierung: rund 900 Inlier aus 1.600 bis 1.700 Treffern je Fotopaar.
- Unscharfe Fotos blieben trotz aller Filter schwach lesbar; neue Fotos brachten mehr als jede Einstellung.

## Nicht gemacht

Keine neuen Knowledge-Eval-Tasks und kein neuer Zertifizierungslauf. Die Änderung erweitert den Skill
um eine Referenz, die bestehenden Tasks sind unverändert. `tests/validate.sh` prüft nur, dass die Datei
vorhanden ist.
