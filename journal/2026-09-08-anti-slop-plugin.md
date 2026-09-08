# Public `anti-slop` plugin — 2026-09-08

**What** — Added a prose-editing plugin to the public marketplace: it finds LLM
slop in German and English, in business and narrative registers. One skill, four
term lists (1894 entries, 1856 distinct), a severity-override file and a flexion-aware checker
script, plus a deterministic eval that measures separation between generated and
human prose. The repo also gained its first `LICENSE` (Apache-2.0) and a `NOTICE`
crediting the third-party term sources.

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

*Merging public corpora needed curation, not a union.* Four sources contributed
810 terms. Three classes had to be rejected: **descriptions** ("uniform paragraph
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
**0.5** without losing a single genuine finding. The regression test that catches
this (`AC-2-3`, `aria` must not appear under `--hard-only`) hangs on the override
file *and* on universal-list load order, so it is the first thing to go red.

*The upstream list has gaps, so the prose outranks the data.* `slop-list.json`
stores word forms rather than lemmas: it carries `seamlessly` but not `seamless`,
although the skill bans both. The category tables in the SKILL.md are therefore
authoritative and a miss in the data file is not an acquittal.

*There is no public German slop list.* GitHub code search, gist search and web
research turned up several English corpora and nothing comparable in German. The
496 German terms were written for this plugin, which also means they are curated
rather than frequency-measured — tracked as an open point in the spec.

**Licensing** — Apache-2.0 for the repo, and that was not a preference. Two of
the four upstreams are Apache-2.0, and Apache material cannot be relicensed under
MIT without dropping the patent grant and the section 4 obligations. MIT flows
into Apache-2.0, not the other way round, so Apache-2.0 is the only licence that
carries all four sources. MIT was never actually on the table.

The CC BY-SA question is a separate one and the first draft of `NOTICE` answered
it twice, in opposite directions: the intro called the terms individually
unprotectable, the next paragraph said part of `data/` *originates in* CC BY-SA
material. The second reading concedes that ShareAlike attaches — and CC BY-SA 4.0
has no outbound compatibility with Apache-2.0 (only with GPLv3), so it would have
put `slop-list-de.json` outside the repo licence. The position now stated is the
first one: individual words and short phrases are not protectable, the category
structure taken from the German page is an idea rather than an expression, so no
adapted material arises and ShareAlike never attaches. The two Wikipedia pages
(56 of 1347 curated entries; four placeholders sit in two lists on purpose, so
1343 are distinct) are credited for provenance, not to discharge an obligation.

What *does* travel with its licence is `slop-list.json` — it is carried over as a
whole collection, and a collection is protectable where its entries are not (as a
compilation, and in the EU under the sui generis database right). That is the
line `NOTICE` now draws. Benny's call on both.

**Review-Runde** — Zwei Durchgänge vor dem Merge, beide mit Befund.

`spec:mechanic-verifier` fand vier Konsistenzabweichungen, alle in der Doku:
eine Zahl ohne Bezugsgröße (1343 eindeutige Terme gegen 1347 Einträge — beides
richtig, vier Platzhalter stehen bewusst doppelt), eine Kalibrierangabe, die wie
eine Schwelle las, eine fehlende Quellenangabe und eine Spec-Formulierung, die
strenger war als der Test, den sie beschreibt.

Der **Cold-Review** fand zwei Blocker, die kein grüner Test gemeldet hatte:

*Ein Test kann grün sein und das Falsche messen.* `AC-2-3` sollte belegen, dass
die Universal-Liste vor den Sprachlisten geladen wird, und wurde an vier Stellen
als der schärfste Test des Plugins beschrieben. Der Reviewer drehte die
Ladereihenfolge um — die Suite blieb **grün**. Grund: `aria` stand gar nicht in
der Universal-Liste, sondern nur in der Upstream-Datei, und wurde allein durch
`severity-overrides.json` entschärft. Die Reihenfolge hatte mit den
ausgelieferten Daten **keine** beobachtbare Wirkung; der Test maß den Override.
Die eigene Regel „stock names are always soft" galt für die 30 Upstream-Namen
schlicht nicht, weil `slop-list.json` keine Severity-Spalte hat und pauschal als
hart gewertet wird. Behoben, indem die Namen in die Universal-Liste als `soft`
aufgenommen wurden — die Behauptung wurde wahr gemacht statt abgeschwächt.
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
zu machen, wanderten 30 Upstream-Namen als `soft` in die Universal-Liste. Dreizehn
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
