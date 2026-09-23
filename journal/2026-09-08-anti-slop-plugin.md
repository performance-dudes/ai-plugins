# Public `anti-slop` plugin — 2026-09-08

**What** — Added a prose-editing plugin to the public marketplace: it finds LLM
slop in German and English, in business and narrative registers. One skill, three
term lists (1843 entries, 1836 distinct), a severity-override file and a flexion-aware checker
script, plus a deterministic eval that measures separation between generated and
human prose.

**How / decisions** —

*German needed a script, not a list.* The obvious approach — hand an English slop
list to a German draft — finds almost nothing, because German inflects: a
`\b`-anchored search for `entscheidend` misses `entscheidende`, `entscheidender`
and `entscheidendes`, which is how the word actually occurs. Entries ending in
`*` now match stem plus up to five suffix characters. That single change is what
makes the German list usable at all.

*Hard versus soft came from the language, not from taste.* `tapestry` is a tell
on its own; `zudem` and `nutzen` are ordinary German. Without a severity per
term, a German list produces noise instead of findings. The reported metric is
therefore hits per 1000 words, not the hit itself.

*The English list needed curation, not accumulation.* Three classes had to be
rejected: **descriptions** ("uniform paragraph
length") that read like terms but are not searchable strings, **slash
alternatives** (`cultivating/fostering`) that can never match as a literal, and
**names** treated as hard — `Chen`, `Reed` and `Kai` are real people's names.
32 dead entries were removed and stock names forced to soft.

**Learnings** —

*A bigger list is not a better one; measure the noise floor.* The merged list
scored **5.5** hard hits per 1000 words on 17 500 words of this repo's own
technical documentation. `aria` matched every `aria-label`; `transform`,
`manifest`, `key` and `dynamic` matched ordinary code prose. A checker at that
rate trains everyone to ignore it — the same failure mode the conventions spec
notes for a permanently red CI check. `severity-overrides.json` brought it to
**0.5** without losing a single genuine finding. The eval cases on literature (h05, h06)
go red first when the override file loses entries.

*The lists have gaps, so the prose outranks the data.* They store word forms
rather than lemmas: a list can carry an adverb (`collaboratively`) without its
adjective (`collaborative`). The category tables in the SKILL.md are therefore authoritative
and a miss in a data file is not an acquittal.

*The German list was written for this plugin.* Its 496 terms are curated rather
than frequency-measured — tracked as an open point in the spec.

*Eine englische Liste statt zweier Dateien.* Die englischen Terme liegen in
**einer** kuratierten Liste, nicht in mehreren nebeneinander. Getrennte Dateien
hätten zwei Formate im Loader bedeutet — eines mit `[term, category, severity]`,
eines ohne Kategorie und Severity — und genau diese Sonderbehandlung hat AC-2-3
zum Scheinbefund gemacht: ein Term ohne Severity-Spalte wurde pauschal hart
gewertet, womit die Universal-Regel für ihn nicht galt. Ein Format für alle
Listen macht die Regel ausnahmslos und den Loader um einen Zweig kürzer.

*Ein Wort ist nie Slop — eine Verteilung ist es.* Die schärfste Prüfung des
Plugins ist Text, der **älter ist als jedes Sprachmodell**: darin ist jeder harte
Treffer per Konstruktion ein Fehlalarm. Gemessen auf 1,04 Mio. Wörtern Literatur
vor 1926 (Austen, Dickens, Melville, Conrad, Fitzgerald · Goethe, Kant, Th. Mann,
Kafka): **0,5 bis 1,7** harte Treffer je 1000 Wörter, gegen 128–293 bei
generiertem Text. Die Trennung stimmte also, die Einzelurteile nicht.

Zwei Fehlerklassen kamen dabei heraus, mit zwei verschiedenen Reparaturen:

**Ein Eintrag muss so spezifisch sein wie der Tell.** `i cannot` stand als
Chatbot-Rest auf der Liste und traf allein bei Austen 83-mal — der Tell ist
`i cannot fulfill`, nicht die zwei Wörter. Dasselbe bei `here is`, wo `here is a`
und `here's` ohnehin schon als Override weich geführt wurden. Beide nackten
Einträge sind ersatzlos raus, vier spezifische Verweigerungsformeln dafür rein.

**Register-Marker gehören in die Overrides, nicht aus der Liste.** `profound`,
`charming`, `anchor`, `convey` · `mannigfaltig*`, `in der Tat`, `äußerst` sind
gewöhnliche Sprache, die literarisches oder akademisches Register markiert, nicht
Maschine. Sie bleiben auf den Listen und zählen weiter zur Dichte — sie
überführen nur nicht mehr allein. 27 Terme neu in `severity-overrides.json`
(45 → 72). Ergebnis: **0,0 bis 0,2** Fehlalarme je 1000 Wörter bei unveränderter
Eval (generiert weiterhin 128–293).

Kant liegt mit 1,7 an der Spitze, weil `das Mannigfaltige` bei ihm ein
Fachbegriff der transzendentalen Ästhetik ist und 237-mal vorkommt — der klarste
Beleg dafür, dass die Liste teils Register misst und nicht Herkunft. `murmelte`
und `stammelte` bleiben dagegen **hart**: dass sie in Erzählprosa von 1900 feuern,
ist Register, kein Fehler — es sind echte Dialog-Tells, für die der Skill eine
eigene Referenz führt.

*Ein Override, den niemand prüft, täuscht Entschärfung vor.* `severity-overrides.json`
führte den Schlüssel `robust`, die Liste den Eintrag `robust*` — der Abgleich läuft
exakt, also griff der Override nie. Folgenlos blieb es nur, weil `robust*` ohnehin
schon `soft` ist; bei einem harten Eintrag wäre es eine stille Fehlalarmquelle
gewesen. Schlüssel entfernt und **AC-4-6** eingezogen: jeder Override muss einen
Listeneintrag exakt treffen, inklusive `*`. Gegenprobe: Schlüssel zurückschieben →
`config-valid` rot.

Zwei neue Eval-Cases halten den Befund fest (`h05-literary-en`, `h06-literary-de`,
AC-3-4). Gegenprobe: nimmt man `charming` und `äußerst` aus den Overrides, gehen
beide rot (13,3 bzw. 17,9 je 1000 Wörter).

**Review-Runde** — Zwei Durchgänge vor dem Merge, beide mit Befund.

`spec:mechanic-verifier` fand drei Konsistenzabweichungen, alle in der Doku:
eine Zahl ohne Bezugsgröße (1343 eindeutige Terme gegen 1347 Einträge — beides
richtig, vier Platzhalter stehen bewusst doppelt), eine Kalibrierangabe, die wie
eine Schwelle las, und eine Spec-Formulierung, die strenger war als der Test, den
sie beschreibt.

Der **Cold-Review** fand zwei Blocker, die kein grüner Test gemeldet hatte:

*Ein Test kann grün sein und das Falsche messen.* `AC-2-3` sollte belegen, dass
die Universal-Liste vor den Sprachlisten geladen wird, und wurde an vier Stellen
als der schärfste Test des Plugins beschrieben. Der Reviewer drehte die
Ladereihenfolge um — die Suite blieb **grün**. Grund: `aria` stand gar nicht in
der Universal-Liste, sondern nur in einer Sprachliste, und wurde allein durch
`severity-overrides.json` entschärft. Die Reihenfolge hatte mit den
ausgelieferten Daten **keine** beobachtbare Wirkung; der Test maß den Override.
Die eigene Regel „stock names are always soft" galt für die betroffenen Namen
schlicht nicht. Behoben, indem sie in die Universal-Liste als `soft` aufgenommen
wurden — die Behauptung wurde wahr gemacht statt abgeschwächt.
Gegenprobe jetzt: Reihenfolge umdrehen → rot.

*Der Fix und der Modus, in dem er zählt, waren nicht dieselben.* Unter
`--hard-only` — dem Modus, den die Eval fährt — wurde ein weicher Term verworfen,
**bevor** er memoisiert war. Eine später geladene Liste konnte denselben Term als
hart wieder einbringen und damit genau die Regel kippen, die `AC-4-5` zusichert.
Folgenlos mit den heutigen Daten, verifiziert mit einem synthetischen Term.
Memoisieren geschieht jetzt vor dem Filtern.

**Learnings** —

*Mutieren, nicht nur laufen lassen.* Beide Blocker waren an grünen Tests
unsichtbar und wurden erst sichtbar, als jemand das Plugin absichtlich kaputt
machte und schaute, ob die Suite es merkt. Die Mutationstabelle steht jetzt in
`tests/anti-slop/coverage.md`; ein Test ohne gezeigten Rot-Fall ist eine
Behauptung, kein Nachweis.

*Eine Schwelle braucht Text, an dem sie greifen kann.* Bei 50-Wort-Cases ist
„höchstens 1,0 Treffer je 1000 Wörter" rechnerisch dasselbe wie „null Treffer" —
die Grenze war bei allen drei kurzen Menschen-Cases wirkungslos. Ein langer Case
(h04) macht sie zu einer echten Aussage; die Schwelle blieb, wo sie war.

*Der Prüfer schlug auf der eigenen Hausform an.* `learnings` ist die
Journal-Überschrift dieses Repos und stand hart auf der Liste — die Doku wäre mit
jedem Journal-Eintrag lauter geworden. Jetzt weich.

**Zweite Review-Runde** — Der Re-Review auf die Blocker-Fixes fand drei weitere
Punkte, einer davon durch den Fix selbst verursacht.

*Ein Fix kann einen Preis haben, den niemand aufschreibt.* Um AC-2-3 falsifizierbar
zu machen, wanderten 30 Namen als `soft` in die Universal-Liste. Dreizehn
davon sind erfundene **Orte** — `Eldoria`, `Whisperwood`, `Zephyria` —, für die die
Begründung von AC-4-5 („Stock-Namen sind auch reale Personennamen") schlicht nicht
gilt. Sie wurden mitdemotiert, weil sie in derselben Zeile standen. Eine Probe
kanonischer KI-Fiktion fiel dadurch von 211 auf **0** harte Treffer je 1000 Wörter,
und keine der acht Eval-Cases hat es gemerkt: Es gab keinen generierten englischen
*Erzähl*-Case. Orte stehen jetzt unter `stock-place` und bleiben hart, `g05` deckt
die Lücke ab, und ein eigener Check fängt die Rückmutation.

*Eine Spec kann sich selbst widersprechen, wenn man Zahlen an zwei Stellen führt.*
Der Fließtext sagte 1864 Terme, die Tabelle desselben Dokuments summierte auf 1894.
Beide Zahlen stammten aus derselben Datei, der Fix-Commit hatte nur die Tabelle
angefasst. Zusätzlich waren „Einträge" und „eindeutige Terme" wieder vermischt —
1894 gegen 1856.

*Eine ehrliche Rechtfertigung ist besser als eine, die sich gut liest.* Der lange
Eval-Case sollte belegen, dass die Schwelle „höchstens 1,0 je 1000" greift. Er hat
268 Wörter, nicht die behaupteten 320, und bei 268 Wörtern toleriert die Schwelle
weiterhin exakt null Treffer — ein einzelner ergäbe 3,7. Die Grenze wird erst ab
rund 1000 Wörtern zu einer eigenen Aussage. Statt einen unlesbar langen Case zu
bauen, steht die Einschränkung jetzt in der Case-Notiz, zusammen mit der Messung,
die die Schwelle tatsächlich trägt: 17.500 Wörter Repo-Doku bei 0,5 je 1000.

**Learnings** —

*Jeder Fix ist eine neue Änderung und verdient denselben Blick wie die erste.*
Beide Blocker der ersten Runde waren echt behoben — und die Behebung des einen
riss ein neues Loch, das die bestehenden Tests und Evals nicht sehen konnten. Ohne
zweite Runde wäre es gemergt worden.

*Eine Kategorie ist eine Behauptung.* `stock-name` trug die Begründung „das sind
auch reale Namen". Sobald etwas in der Kategorie liegt, für das die Begründung
nicht gilt, ist die Kategorie falsch — nicht die Regel. Die Antwort war eine zweite
Kategorie, nicht eine aufgeweichte erste.

**Dritte Review-Runde** — Der Cold-Review vor dem Merge fand, dass zwei der
Nachweise oben nicht mehr galten.

*AC-2-3 konnte wieder nicht rot werden.* Seit die englischen Listen zusammengelegt
sind, steht kein Term zugleich universal-weich und sprachlich-hart; die
Ladereihenfolge hatte keine beobachtbare Wirkung mehr, und die Suite blieb bei
umgedrehter Reihenfolge grün. Der Test läuft jetzt gegen eine Fixture
(`ANTI_SLOP_DATA`), in der nur die Reihenfolge entscheidet. Lehre: Ein Test, der
von der Zusammensetzung der Echtdaten abhängt, verliert seine Beweiskraft still,
sobald jemand die Daten umbaut — Invarianten des Codes gehören an Fixtures.

*Überlappende Einträge zählten mehrfach.* „is a testament to" ergab vier harte
Treffer (`testament`, `testament to`, `a testament to`, `is a testament to`).
Jetzt zählt jede Textstelle einmal; hart gewinnt vor lang, damit eine längere
weiche Phrase keinen harten Treffer verdeckt.

*Die Eval maß das Kernversprechen nicht.* Mit abgeschalteter Flexion blieb sie grün.
`g06-flexion-de` trifft nur über Stamm-Einträge (306 → 0 je 1000 Wörter ohne
Suffix), und die Eval läuft jetzt in `tests/anti-slop/run.sh` mit.

*Beschreibungen tarnen sich als Terme.* Elf Einträge waren Beschreibungen
(`contrastive negation: "it's not just x, it's y"`) und konnten nie treffen. Wo ein
echter Suchstring drinsteckte, wurde er gerettet (`one thing was certain`,
`the good news?`), der Rest entfernt; AC-4-3 fängt die Form jetzt ab.

Alle Mutationen der Coverage-Matrix sind in dieser Runde neu gemessen worden;
eine alte Zeile hatte eine Mutation beschrieben, die ins Leere lief.
