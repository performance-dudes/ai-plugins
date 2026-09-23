# 2026-09-23 — `image-toolkit`: Knowledge-Eval-Suite und Qualitätsregel (0.2.1)

Schließt #63. Bei #62 war die fehlende Eval-Suite bewusst zurückgestellt worden.

## Suite

`plugins/image-toolkit/evals/`, deterministisch: 41 gesperrte Fälle in acht Achsen. Der
Scorer liest `SKILL.md` und alle `references/*.md` zur Laufzeit. Zertifiziert nach der
Cold-Agent-Schleife aus `plugin-eval`.

## Ergebnis

| Lauf | Accuracy | pass^k |
|---|---|---|
| mit Skill, 3 Trials | 1,00 ± 0,00 | 41/41 |
| Baseline ohne Skill, Wahlzwang | 0,54 | — |
| trennscharf | | 19/41 |

## Was der Cold-Review gefunden hat — und was daraus wurde

Die erste Fassung (25 Fälle) meldete eine Baseline von 0,28. Der Review zeigte: Das war ein
Artefakt des Prompts. Die Baseline durfte `not-specified` wählen und lehnte alles ab, was sie
nicht sicher wusste — gemessen wurde Zurückhaltung. Mit Wahlzwang kam sie auf 0,72; nur 7 Fälle
trennten Skill von Vorwissen.

Die Lehren, jetzt im Harness verankert:

- **Baseline immer mit Wahlzwang** (außer auf der Decline-Achse). Der Selbsttest prüft, dass
  sie nicht ablehnen darf.
- **Antwortoptionen ohne Rateweg.** Die Baseline wählte beim Abschaltdatum das späteste, beim
  Lite-Preis den niedrigsten Wert und leitete `previous_interaction_id` aus dem API-Namen ab.
  Jetzt: alle Daten plausibel, alle Preise im selben Band, `previous_response_id` als Köder.
- **Verhalten statt Stichwort.** Die Größen-Fälle übernahmen den Wortlaut der neuen Tabelle.
  Umformuliert, und zwei `command`-Fälle verlangen den vollständigen Aufruf: Die Baseline traf
  `--size` aus dem Kontext, erfand aber `--aspect-ratio` und ließ `--prompt` weg.
- **Isolation belegt, nicht behauptet.** Ohne `ANTHROPIC_API_KEY` gibt es kein `--bare`;
  `--setting-sources ""` plus eigener System-Prompt ergibt ~460 Input-Tokens (Standard: ~740k).
- **`run.sh` scheitert laut:** nicht zertifiziert, Baseline > 0,65 oder < 15 trennscharfe Fälle.

Ein Fall (`lite-ga-date`) war falsch angelegt: Das GA-Datum steht nicht im Skill, der kalte
Agent lehnte korrekt ab. Er ist jetzt ein Decline-Fall — Google dokumentiert das Datum, der
Skill lässt es aus.

## Qualitätsregel in SKILL.md

Ohne `--size` rendert die API 1K. Damit ein Agent bei einem Endprodukt nicht bei
Entwurfsqualität landet, steht eine Tabelle in SKILL.md und im Command: Entwurf 1K,
Web/Social 2K (Retina, Zuschnitt), Druck 4K, höchste Qualität oder Text-lastig → Pro. Die
Kostenregel der Referenz ist darauf abgestimmt.
