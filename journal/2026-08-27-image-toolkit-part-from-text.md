# 2026-08-27 — image-toolkit: der Aufruf, der nur im Edit-Pfad brach

## Was

`plugins/image-toolkit/scripts/generate_image.py`: `types.Part.from_text(prompt)`
wird zu `types.Part.from_text(text=prompt)`. Dazu ein Regressionstest
(`validate.sh` §6), der den positionalen Aufruf verbietet.

## Warum

`--edit` brach mit `TypeError: Part.from_text() takes 1 positional argument but
2 were given` ab. In `google-genai` ist `Part.from_text` keyword-only
(`def from_text(cls, *, text: str)`).

Das Verräterische steht eine Zeile darüber: `types.Part.from_bytes(data=…,
mime_type=…)` im selben Aufruf war von Anfang an korrekt mit Schlüsselwörtern
geschrieben. Beide Fabrikmethoden derselben Klasse, dieselbe Signatur-Konvention
— nur eine der beiden hielt sie ein. Eine Inkonsistenz innerhalb eines einzigen
`contents=[…]`-Blocks fällt beim Lesen nicht auf, weil das Auge die zweite Zeile
als Variation der ersten liest, nicht als Abweichung.

## Warum es niemandem auffiel

Die Bibliothek hat zwei Pfade, und nur einer war betroffen:

| Pfad | Was er tut | Betroffen |
|---|---|---|
| `--prompt` (Generierung) | reicht einen einfachen String als `contents` durch, fasst `Part` nie an | nein |
| `--edit` (Bearbeitung) | baut `contents` aus `Part`-Objekten | ja |

Der häufiger benutzte Pfad umgeht die Klasse komplett. Ein Fehler in `Part`
konnte deshalb beliebig lange unbemerkt liegen: Wer generiert, merkt nichts, und
wer bearbeitet, trifft ihn sofort und vollständig.

## Learnings

**Ein Regressionstest auf Quelltext muss echten Code von Prosa trennen.** Der
Test unter §6 sucht Zeilen mit `Part.from_text(`, die nicht `from_text(text=`
enthalten — und filtert Kommentarzeilen vorher aus. Ohne diesen Filter würde der
erklärende Kommentar über dem Aufruf, der den falschen Aufruf zwangsläufig
zitiert, den Test auf dem Fix rot und auf dem Bug grün werden lassen. Dieselbe
Falle ist am 04.09. schon einmal im transcribe-Plugin zugeschnappt
(`2026-09-04-transcribe-ffmpeg8-decoder.md`); sie gilt für jeden Ban-Wort-Test.

**Ein zweiter Pfad, der eine Klasse umgeht, ist kein Vorteil, sondern eine
blinde Stelle.** Dass `--prompt` ohne `Part` auskommt, hat den Fehler nicht
verhindert, sondern nur verzögert.
