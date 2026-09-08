# Slop in deutscher Prosa

Gilt für Mail, Angebot, LinkedIn, Blog, Kolumne, Doku — und für Kapitel, Szenen,
Dialog. Die Wortliste dazu: `data/slop-list-de.json`, geprüft mit
`scripts/check-slop.py`.

Deutsche Slop ist nicht die Übersetzung englischer Slop. Drei Unterschiede
bestimmen alles Weitere:

| | Englisch | Deutsch |
|---|---|---|
| Wortform | `tapestry` steht so im Text | `entscheidend` erscheint als `entscheidende`, `entscheidenden`, `entscheidendes` |
| Verdächtigkeit | `delve` ist immer ein Tell | `zudem`, `nutzen`, `besonders` sind normale Wörter — erst die Häufung verrät |
| Herkunft | LLM-Eigenheit | Verwaltungs- und Wirtschaftsdeutsch, das die Modelle gelernt haben |

Daraus folgt die Härte-Unterscheidung in der Liste: **hart** = raus, sofern nicht
Zitat oder Fachbegriff. **weich** = einzeln legitim, im Cluster ein Befund.
Ein weicher Treffer allein ist kein Argument.

## Die Kategorien und ihr Ersatz

### Eröffnungen — die stärkste Trefferlage

Der erste Satz trägt den deutlichsten Tell. Streichen ist meist der ganze Fix.

| Nie | Stattdessen |
|---|---|
| „In der heutigen digitalen Welt …" | die Jahreszahl, oder nichts |
| „In einer Zeit, in der X immer wichtiger wird" | das konkrete Ereignis: „seit die API im März brach" |
| „Lassen Sie uns eintauchen" / „Tauchen wir ein" | mit dem Befund anfangen |
| „Grundsätzlich lässt sich sagen, dass …" | den Satz danach als ersten Satz nehmen |
| „Immer mehr Menschen fragen sich …" | wer genau, wie viele |

### Verb-Inflation

| Nie | Stattdessen |
|---|---|
| nutzbar machen, entfesseln | nutzen, starten |
| das volle Potenzial ausschöpfen | was genau danach möglich ist |
| auf das nächste Level heben | von 40 auf 90 Prozent |
| spielt eine entscheidende Rolle für | verursacht, ermöglicht, blockiert |
| einen Beitrag leisten | was beigetragen wurde |
| implementieren, realisieren, adressieren | einbauen, bauen, lösen |

### Hype-Adjektive

Verboten, solange kein Beleg auf derselben Seite steht.

`revolutionär` · `bahnbrechend` · `wegweisend` · `zukunftsweisend` · `nahtlos` ·
`transformativ` · `ganzheitlich` · `tiefgreifend` · `maßgeschneidert` ·
`atemberaubend` · `hochmodern` · `ultimativ`

Weich, aber im Cluster verräterisch: `umfassend` · `innovativ` · `robust` ·
`nachhaltig` · `signifikant` · `fundiert` · `spannend` · `präzise`.

### Füllverstärker

Jeder ist ein Loch, in das eine Zahl gehört.

> „zahlreiche Kunden" → „elf Kunden"
> „akribische Prüfung" → „wir haben alle 340 Zeilen geprüft"
> „eine Vielzahl an Optionen" → „drei Optionen"
> „äußerst wichtig" → „wichtig" (das Adverb trägt nichts)

### Zusammenfassungs- und Redaktionsformeln

`Zusammenfassend lässt sich sagen` · `Abschließend bleibt festzuhalten` ·
`Alles in allem` · `Letzten Endes` · `Es ist wichtig zu beachten` ·
`Es ist erwähnenswert` · `An dieser Stelle sei darauf hingewiesen` ·
`Wie bereits erwähnt`

Ein Schlussabsatz, der den gelesenen Text zusammenfasst, ist selbst der Tell.
Schließen mit der Position oder dem nächsten Schritt.

### Hedges — das Absichern ohne Aussage

Modelle schwächen ab, weil abgeschwächte Behauptungen seltener falsch sind. Das
Ergebnis sind Sätze, die nichts mehr behaupten.

`in gewisser Weise` · `im großen und ganzen` · `je nach Kontext` ·
`in vielen Fällen` · `nicht selten` · `durchaus denkbar` · `es empfiehlt sich` ·
`es bietet sich an`

> „Es empfiehlt sich, die Konfiguration zu prüfen" → „Prüf die Konfiguration."

Weich, aber im Cluster verräterisch: `in der Regel` · `unter Umständen` ·
`möglicherweise` · `tendenziell` · `grundsätzlich`.

### Werbesprache

Deutsche Modelle fallen in Agentur- und Broschürendeutsch, sobald das Thema
irgendwie nach Kunde riecht.

`Ihr Partner für` · `aus einer Hand` · `individuell auf Sie zugeschnitten` ·
`kompetent und zuverlässig` · `schnell und unkompliziert` ·
`Ihre Vorteile auf einen Blick` · `höchste Qualität` · `mit langjähriger
Erfahrung` · `marktführend` · `erstklassig`

Der Test ist immer derselbe: Steht auf derselben Seite eine Zahl, die den
Anspruch belegt? Wenn nicht, ist der Satz eine Behauptung über sich selbst.

### Vage Autoritäten

`Studien zeigen` · `Untersuchungen belegen` · `Experten sind sich einig` ·
`Branchenberichte` · `Einige Kritiker argumentieren`

Entweder die Quelle nennen oder als eigene Einschätzung schreiben.

### Chatbot-Reste

Bleiben in unredigiertem Output stehen und sind der eindeutigste Beweis:
`Selbstverständlich!` · `Natürlich!` als Antwortanfang · `Als KI-Sprachmodell` ·
`Ich hoffe, das hilft` · `Möchten Sie, dass ich …` · `Stand meines letzten
Wissensupdates` · `Ich hoffe, diese Nachricht erreicht Sie wohlauf`.

## Was keine Wortliste findet

Diese fünf Muster sind im Deutschen mindestens so verräterisch wie das
Vokabular — sie brauchen ein Auge, keinen Grep.

1. **„Nicht A, sondern B."** Die deutlichste Stil-Signatur aktueller Modelle,
   in beiden Formen: „Es geht nicht um schöne Bilder, sondern um messbare
   Ergebnisse" und „nicht nur X, sondern auch Y". Die Aussage steht in B; A ist
   Beiwerk. Fix: nur B schreiben.
2. **Trikolon.** Drei Adjektive, drei Halbsätze, drei Bullets — die Dreierregel
   in jedem Abschnitt. Menschliche Aufzählungen sind unregelmäßig: zwei hier,
   fünf dort.
3. **Partizip-I-Anhängsel.** „…, die Bedeutung unterstreichend", „gewährleistend,
   dass …". Im Deutschen unüblich, eine direkte Übersetzung der englischen
   `-ing`-Form. Fix: eigener Hauptsatz oder streichen.
4. **Nominalstil.** „Die Ermöglichung einer ganzheitlichen Betrachtung" statt
   „damit sieht man das Ganze". Erkennbar an der Häufung von `-ung`, `-heit`,
   `-keit`, `-ierung` und an Komposita, die es vorher nicht gab
   (`Digitalisierungsreise`, `Innovationskraft`, `Zukunftsfähigkeit`).
5. **Gleichförmige Satzlängen.** Laut lesen. Wenn jeder Satz gleich lang
   atmet, ist die Maschine am Werk — unabhängig vom Wortschatz.

Dazu die Formatierungs-Tells: übermäßiger Fettdruck, Emojis vor Überschriften,
jeder Bullet nach dem Schema **Schlagwort:** plus zwei Sätze, Abschnitte immer
gleicher Länge.

## Narrative Prosa auf Deutsch

Zusätzlich zu `references/narrative-prose.md`, dessen Kategorien unverändert
gelten.

**Dialog:** `sagte` ist unsichtbar und richtig. Jeder Ersatz zieht die
Aufmerksamkeit auf den Tag: `murmelte` · `hauchte` · `raunte` · `stammelte` ·
`kicherte` · `gluckste` · `presste sie hervor`.

**Körpersprache-Klischees:** `kaum mehr als ein Flüstern` · `ein Schauer lief
ihr über den Rücken` · `die Luft knisterte` · `ihre Augen funkelten` · `mit
einer Mischung aus X und Y` · `hin- und hergerissen` · `wider Willen` · `eine
gefühlte Ewigkeit` · `die Zeit schien stillzustehen`.

**Kapitelenden:** `Vielleicht, nur vielleicht` · `Für den Moment war das genug` ·
`Das Leben würde nie wieder dasselbe sein` · `Das war erst der Anfang` ·
`Was sie nicht wusste` · `In diesem Moment wurde ihr klar`.
Fix: einen Satz früher aufhören — die Slop-Kadenz ist fast immer der Satz nach
dem eigentlichen Ende.

**Namen:** Die englischen Stocknamen (Elara, Aria, Kael, Eldoria) tauchen auch
in deutschen Entwürfen auf. Deutsche Modelle bauen zusätzlich Ortsnamen aus
Natur plus `-hain`, `-stein`, `-bach`, `-heim`, `-au` zusammen. Prüfen gegen die
Quelle, nie gegen die Erfindung.

## Was im Deutschen kein Slop ist

Zusätzlich zu den drei Fällen in der SKILL.md (Fachbedeutung, Zitat, tragendes
Wort):

- **Pflichtregister.** In Rechtstexten, Verträgen und Behördenschreiben sind
  `gemäß`, `hinsichtlich`, `seitens` und `vorgenannt` vorgeschrieben oder
  eingeführt. Dort bleiben sie.
- **Etablierte Komposita.** `Nachhaltigkeitsbericht` als Dokumententyp ist ein
  Name, kein Buzzword. Der Verdacht gilt der Neubildung, nicht dem Begriff.
- **Übergangswörter mit Funktion.** `Zudem` ist verdächtig, wenn es „und"
  meint. Trägt es eine echte Steigerung, bleibt es.
