# 2026-08-17 — Das Gate war nicht zu streng, es war kaputt

## Der Anlass

Ein PR mit korrekt gesetztem Freigabe-Marker blieb rot. Die Meldung verlangte, den
Marker zu setzen — er stand sichtbar im PR. Aus dieser einen Beobachtung wurde die
Frage, ob die Merge-Gates „zu stark" seien. Sie sind es nicht. Sie hatten vier
Defekte, von denen drei genau diesen Eindruck erzeugen.

## 1. Der Trigger fehlte — der vorgesehene Freigabeweg wirkte nicht

Der Workflow hörte auf `pull_request` und `pull_request_review`, nicht auf
`issue_comment`. Ein nachträglich gesetzter Marker löste also **nie** einen neuen
Lauf aus: die Bedingung war erfüllt, der Check blieb rot, bis jemand von Hand neu
startete. Wer das nicht weiß, hält das Gate für unerfüllbar.

Der Kommentar im Workflow benannte die Lücke unfreiwillig selbst — er begründete
`pull_request_review` damit, dass „ein nachträgliches Approval den Check erneut
auslöst". Für den zweiten Freigabeweg wurde dieselbe Überlegung nie zu Ende geführt.

**Nicht trivial zu beheben:** Ein `issue_comment`-Lauf hat keinen PR-Kontext. Er
checkt den Default-Branch aus, und sein Check-Run landet auf dessen SHA — in der
PR-Checkliste taucht er gar nicht auf, für die Branch-Protection ist er unsichtbar.
Ein zweiter Job entscheidet deshalb nichts selbst, sondern startet den **echten**
Lauf des PR-Heads neu. Er prüft vorher, ob der Kommentar den Marker überhaupt
zeilenverankert trägt — sonst löste jeder Wortbeitrag einen CI-Lauf aus.

Dazu `pull_request: edited`, damit auch ein Marker im PR-Body zieht.

## 2. Die Meldung nannte die verletzte Bedingung nicht

Für **jeden** Fehlerfall stand dieselbe Zeile da: „ohne Freigabe-Marker … → den
Marker in den PR schreiben". Auch dann, wenn der Marker sichtbar im PR stand und
bloß an der falschen Stelle. Das ist die teuerste Sorte Fehlermeldung — sie
beschreibt den Sollzustand und verschweigt, woran es hakt.

Die Suche ging deshalb der Reihe nach durch Zeitstempel, CRLF-Zeilenenden und einen
Version-Bump-Check, bevor die eigentliche Bedingung gefunden war. `decide()`
unterscheidet jetzt „kein Marker" von „Marker vorhanden, aber nicht als letzte
Zeile" und sagt im zweiten Fall genau das.

## 3. Zwei Repos, zwei Fassungen derselben Logik

`ai-plugins` prüfte den Marker im **gesamten** Text, `ai-plugins-internal` nur in der
**letzten nicht-leeren Zeile** jedes Beitrags. Dieselbe Aktion, zwei Ergebnisse.

Die Ironie: Der Kommentar in `ai-plugins` sagt ausdrücklich, die Logik sei „von BEIDEN
Durchsetzungsstellen importiert, damit ihre Regel nie auseinanderdriftet". Zwischen
den *Repos* ist genau das passiert — die geteilte Datei wurde vendored, und die Kopie
altert.

**Die strengere Fassung gewinnt**, und zwar nicht aus Vorsicht: Sie stammt aus einem
realen Vorfall vom 02.08., bei dem ein Body mit dem Marker in einem Codeblock plus dem
Satz „ich habe noch KEINEN Cold-Review gemacht" fälschlich `allow=true` lieferte. Die
naheliegende Alternative — Codeblöcke erkennen — war dort bereits versucht und
verworfen worden, weil sie auf ein Wettrüsten hinauslief und auf legitimem Input
falsche Blocks erzeugte. Der Vertrag „letzte nicht-leere Zeile" hat beide Probleme
nicht und braucht keinen Markdown-Parser.

## 4. `git fetch --depth=0` brach ab, und niemand merkte es

Im `conventions`-Workflow stand `git fetch origin "$BASE" --depth=0 || true`.
`--depth=0` ist kein gültiges git-Argument (`fatal: depth 0 is not a positive
number`); gemeint war „volle Tiefe", die `actions/checkout` mit `fetch-depth: 0`
ohnehin schon herstellt. Das `|| true` schluckte den Abbruch, und der Spec-Touch-Check
lief anschließend gegen eine womöglich unvollständige Historie — er konnte grün
melden, ohne den echten Diff gesehen zu haben.

Jetzt ohne `--depth`, ohne `|| true`, und mit einer expliziten Prüfung, dass die
Base-Ref auflösbar ist. Fail-closed: lieber ein roter Check als ein grüner, der
nichts geprüft hat.

## Was daraus folgt

**Die Logik, die über jeden Merge entscheidet, war ungetestet.** `tests/merge-gate/`
schließt das: zwölf Fälle über den Entscheidungsvertrag, inklusive der beiden
historischen Vorfälle (Codeblock-Freigabe, Marker mit Text darunter), plus Prüfungen,
dass die Trigger verdrahtet sind und der `--depth=0`-Fehler nicht zurückkehrt.

Beim Schreiben dieser Tests fielen zwei falsche Erwartungen von mir auf — ein
zeilenverankerter Marker inline im Fließtext ist gar kein Marker und damit auch nicht
„misplaced", und der erste Grep traf den eigenen Erklär-Kommentar statt eines echten
Aufrufs. Beides Testfehler, keine Codefehler; beide hätten als falsches Grün
durchlaufen können.

**Die übergreifende Lehre:** Drei der vier Defekte machten das Gate nicht strenger,
sondern nur undurchschaubar. Ein Kontrollmechanismus, dessen vorgesehener Freigabeweg
nicht funktioniert und der beim Fehlschlag die Bedingung verschweigt, wird als
Schikane erlebt und irgendwann umgangen. Das ist der eigentliche Schaden — nicht die
verlorene Zeit.

## Offen

- Dieselben Defekte 1–3 stecken in `ai-plugins-internal`, wo `merge-gate` als Plugin
  lebt (mit Skill, Hook und CI-Template). Dort gehören Spec, Tests und Version-Bump
  dazu; separat nachzuziehen.
- Das Vendoring bleibt die strukturelle Ursache für Defekt 3. Solange die Datei
  kopiert statt bezogen wird, driftet sie wieder. Ein Sync-Test, der beide Fassungen
  vergleicht, wäre die billigste Absicherung.
