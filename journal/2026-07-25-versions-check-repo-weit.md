# 2026-07-25 — Versions-Konsistenz repo-weit, eine Implementierung statt drei

Der Marketplace-Versions-Check gilt jetzt für **jedes** Plugin und existiert nur noch
einmal: `tests/lib/check-version-sync.sh`, aufgerufen von der repo-weiten Suite, den
Plugin-Suiten und der CI.

## Auslöser

Beim Ausliefern von `mechanic` 0.5.0 fiel `validate.yml` mit
`marketplace 0.3.0 != plugin.json 0.5.0`. Beim Nachsehen: der Job war **seit dem
6. Juli rot**, acht Runs in Folge. Ursache war `4334995` — `context-scout` auf
Sonnet 4.6 gepinnt, `context-aware`s `plugin.json` auf 0.1.1 gehoben, der
Marketplace-Eintrag nicht nachgezogen.

Beide Befunde waren Zufallsfunde. Aufgefallen ist es nur, weil ein Push zufällig
denselben Job auslöste und jemand hinsah.

## Zwei Ursachen, nicht eine

Der naheliegende Fix — Versionsnummer nachziehen — behebt das Symptom. Die Struktur
dahinter hatte zwei Defekte:

1. **Die Prüfung lag nur in der CI.** `run-all.sh` (und damit jeder lokale Lauf)
   kannte sie nicht. Wer lokal grün sah, hatte keinen Anlass, an die CI zu denken —
   die Rückmeldung kam erst nach dem Push, und dort ging sie im Dauer-Rot unter.
2. **Sie existierte als Kopie.** `validate.yml` trug seine eigene Inline-Fassung. Der
   erste Reflex war, eine zweite in `tests/mechanic/run.sh` zu bauen — das hätte das
   Auseinanderlaufen nur verdoppelt statt behoben.

## Entscheidung

Eine Implementierung in `tests/lib/check-version-sync.sh`, drei Aufrufer:

```
tests/lib/check-version-sync.sh  [<plugin>]
        ▲                ▲                ▲
        │                │                │
tests/structure/  tests/mechanic/  .github/workflows/
   check.sh          run.sh          validate.yml
  (alle Plugins)   (nur mechanic)   (alle, in CI)
```

Das ist dieselbe Doktrin, die im Repo für Evals gilt: **das reale Objekt aufrufen,
nie eine gepflegte Zweitfassung.** Eine Kopie driftet und misst irgendwann sich
selbst. Der Helper deckt drei Dinge ab, nicht nur die Version: jedes Plugin auf
Platte ist registriert (AC-4-1), die Versionen sind identisch und gesetzt (AC-4-2),
jeder `source` löst auf (AC-4-3).

Kein stiller Skip: fehlt ein JSON-Parser, terminiert der Helper mit Exit 2 und der
Aufrufer wertet das als Verstoß. Ein Check, der ungeprüft grün aussieht, ist
schlimmer als einer, der laut fehlt — genau der Fehlermodus, der hier drei Wochen
gekostet hat.

## Geliefert

- `tests/lib/check-version-sync.sh` — der Helper (`[<plugin>]` optional).
- `tests/structure/check.sh` — neuer Block US-conv-4, prüft alle Plugins.
- `tests/mechanic/run.sh` — eigene Kopie durch den Helper-Aufruf ersetzt.
- `.github/workflows/validate.yml` — Inline-Python durch denselben Helper ersetzt.
- Spec `repo-conventions`: **US-conv-4** mit AC-4-1…AC-4-4.
- Spec `mechanic`: AC-2-3 verweist auf die zentrale Implementierung.
- `tests/README.md`: neuer Abschnitt zu `tests/lib/`.

## Verifiziert

- Sauberer Zustand: `structure` und `mechanic` grün, `run-all.sh` grün.
- Drift bei **`ocr`** künstlich erzeugt → repo-weiter Check Exit 1, `mechanic`-Suite
  korrekt weiterhin 0 (fremdes Plugin, nicht ihre Zuständigkeit).
- Unregistriertes Plugin (`plugins/zztest/`) künstlich angelegt → repo-weit gefangen.
- Alle sieben Plugins aktuell konsistent; `context-aware` 0.1.0 → 0.1.1 nachgezogen.

## Offen

- `AC-1-3` der repo-conventions („jedes Plugin hat `specs/<plugin>/` oder ist als
  spec-frei dokumentiert") ist in `tests/structure/check.sh` **nicht** implementiert —
  beim Lesen der Datei aufgefallen, hier nicht angefasst.
- Der Node-Pfad im Helper ist nicht ausgeführt (Exit 2 mit Hinweis). Auf einem Runner
  ohne `python3`, aber mit `node`, liefe der Check damit nicht.
