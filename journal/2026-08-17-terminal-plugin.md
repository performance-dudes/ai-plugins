# 2026-08-17 — terminal-Plugin: ein Rezept, das nur auf einer Maschine existierte

## Was

Neues Plugin `terminal` (public, `0.1.0`): iTerm2-Dynamic-Profiles, die pro Projekt
automatisch umschalten und im Badge oben rechts den laufenden
Claude-Code-Session-Namen zeigen. Skill (das Rezept), Installer (das Werkzeug),
`performance-dudes.json` (ein gearbeitetes Beispiel), `/iterm-profile`.

Ausgangslage: dasselbe Rezept war **zehnmal von Hand** angewendet worden — PD,
VibeSkills, Stargate, Dropbox, kinavigator und weitere — und lag ausschließlich in
`~/Library/Application Support/iTerm2/DynamicProfiles/` auf einer Maschine. Der
Vergleich der zehn Profile war der eigentliche Erkenntnisschritt: invariant sind ein
gutes Dutzend Felder, variabel sind genau **sechs Werte** (Name, Emoji, Akzentfarbe,
Hintergrund, Icon, Pfad). Damit ist es template-fähig.

## Drei Dinge, die man beim Nachbauen nicht sieht

- **`Bound Hosts` nimmt trotz des Namens PFADE.** Das ist das einzige Feld, das aus
  einem Theme, das man auswählen muss, eines macht, das sich selbst schaltet. Wer den
  Namen wörtlich nimmt, sucht es gar nicht erst.
- **Badge und Tab teilen den Farbton, unterscheiden sich nur im Alpha** (0.5 gegen
  1.0). Der Badge liegt groß hinter dem Text und muss zurücktreten, der Tab ist klein
  und muss lesbar bleiben. Zwei verschiedene Farben zerreißen den Zusammenhang
  zwischen Tab und Fläche — es sieht dann nach zwei Dingen aus statt nach einem.
- **`\(session.name)` ist ein interpolierter String, kein Text.** In JSON muss der
  Backslash verdoppelt werden. Ein einfacher ergibt einen Badge, der wörtlich
  `\(session.name)` anzeigt — ein stummer Fehler, den man für einen Tippfehler hält.

## Warum ein Installer und kein kopierbares JSON

Das war die zentrale Design-Entscheidung. iTerm2 verlangt für Bild und Icon
**absolute** Pfade, löst nichts selbst auf und rendert einen toten Pfad
**kommentarlos ohne Bild**. Man sitzt vor einem leeren Terminal und bekommt keinen
Hinweis. Ein Template, das die Maschinengrenze überschreitet, trägt aber
zwangsläufig fremde Home-Pfade.

Also löst der Installer zur Installationszeit auf, prüft jedes Asset einzeln und
**lässt das Feld weg, statt es kaputt zu schreiben** — mit einer Meldung, woher das
Asset normalerweise stammt. Ein fehlender Hintergrund kostet den Hintergrund, nicht
das Profil.

Das trägt auch den Fall, dass Assets in einem Repo liegen, das nicht jeder klonen
kann: `performance-dudes/brand` ist privat, also nennt das Template es als Quelle
und fällt auf das öffentliche `website`-Repo zurück. Referenziert wird, nie kopiert.

## Die Tests haben zwei echte Defekte gefunden

Beide im Installer, beide erst durch das Schreiben der Suite sichtbar:

1. **`--dry-run` legte das Zielverzeichnis an.** `mkdir -p` lief vor der
   Dry-Run-Abzweigung. Ein Dry-Run, der ins Dateisystem schreibt, ist keiner.
2. **Fortschrittsmeldungen gingen auf stdout** und verschmutzten die JSON-Ausgabe.
   `--dry-run | python3 -m json.tool` schlug deshalb fehl. Die Warnungen lagen
   korrekt auf stderr, die Erfolgsmeldungen nicht — eine Asymmetrie, die man beim
   Draufschauen nicht bemerkt, weil im Terminal beides gleich aussieht.

Der zweite ist der lehrreichere: manuell getestet hatte ich den Dry-Run mehrfach und
für in Ordnung befunden. Sichtbar wurde der Fehler erst, als etwas anderes als ein
Mensch die Ausgabe gelesen hat.

## Entscheidungen

- **Public statt intern.** Die Mechanik ist markenneutral; nur das Template ist
  PD-spezifisch, und es referenziert Assets, statt sie mitzuliefern.
- **Akzentfarbe `#EA580C`** (Brand-Orange) statt des gewachsenen `#E43B2E`. Letzteres
  war in keinem Repo belegt — eine Abweichung, die im Template zementiert worden
  wäre.
- **Wallpaper `teams-bg-speed-lines.jpg`**: dasselbe Motiv, das als Teams-Hintergrund
  dient. Laut dem README in `brand/backgrounds/teams/` die ruhigste der drei
  Varianten — für eine Fläche unter laufendem Text die richtige Wahl. Der Skill
  verweist auf die anderen beiden.
- **Deterministische Eval statt Judge.** Der Output je Task ist ein Label, also wird
  gematcht. Ein Judge hätte hier nur Varianz addiert.
- **Keine Bild-Assets im Plugin.** Sie würden dupliziert und hingen am versionierten
  Cache-Pfad — dasselbe Problem, das die Statusleiste des cockpit-Plugins bereits
  hat und das dort mit „kopieren, nicht verlinken" gelöst werden musste.

## Was schiefging — und was daraus folgt

Der erste Anlauf ging **ohne Spec, Tests, Evals und Journal** als PR raus und lief
in beide CI-Gates (`conventions`, `merge-gate`). Ursache war nicht Unwissen über die
Regeln, sondern dass `ai-plugins/CLAUDE.md` nie im Kontext war: die Session lief im
Workspace-Root, und Claude Code lädt CLAUDE.md beim Start nur aus dem
Arbeitsverzeichnis und den Ebenen **darüber**. Ein Sub-Repo liegt darunter und lädt
bestenfalls „on demand", wenn dort eine bestehende Datei gelesen wird — `Write` auf
neue Dateien und `Bash` mit `cat`/`rg` genügen dafür offenbar nicht.

Das Gate war also nicht zu streng, sondern hat exakt das gefangen, wofür es gebaut
ist. Ohne es wäre ein ungetestetes Plugin in einen öffentlichen Marketplace
gewandert. Die Konsequenz ist im Workspace-Repo gelandet: die Regel „Sub-Repos nie
von hier aus verändern" trägt jetzt das Warum und den einen Befehl, der sie
entschärft (`cat <sub-repo>/CLAUDE.md`, bevor dort geschrieben wird).

## Nachtrag — was das Review gefunden hat

Ein Tandem-Review (zwei unabhängige Reviewer) hat zwei weitere Defekte gefunden, beide
im Installer, beide von meiner Suite nicht abgedeckt:

- **`abspath()` scheiterte still.** `cd "$(dirname "$p")"` bei nicht existierendem
  Elternverzeichnis lieferte eine leere Substitution — übrig blieb `/<basename>`. Ein
  Tippfehler im `--background`-Pfad wäre als plausibel aussehender absoluter Pfad auf
  die Dateisystemwurzel im Profil gelandet, und iTerm2 hätte ihn kommentarlos ohne Bild
  gerendert. Jetzt: Abbruch mit Meldung (AC-term-2-4, §15).
- **Ein bestehendes Profil wurde bedingungslos überschrieben.** `existed` steuerte nur
  den Text der Erfolgsmeldung, geschrieben wurde immer. Wer sein Profil angepasst hatte,
  verlor die Arbeit wortlos. Jetzt bricht der Installer bei abweichendem Inhalt ab,
  `--force` erzwingt (AC-term-4-4, §16).

Der zweite ist der lehrreichere, weil ich ihn selbst plausibel wegargumentiert hatte:
mein Test prüfte **Idempotenz** — „ein zweiter Lauf erzeugt keine zweite Datei" — und
war grün. Das ist aber eine andere Zusage als „deine Anpassungen überleben". Idempotenz
schützt vor Duplikaten, nicht vor Datenverlust. Ein grüner Test zur benachbarten Frage
hat die eigentliche Lücke verdeckt.

Dazu ein dritter Punkt, der keine Codefrage war: mein Freigabe-Kommentar behauptete, die
Paraphrase der privaten README sei aus dem Template entfernt. War sie nicht ganz — eine
Zeile stand noch. Wer eine Bereinigung meldet, sollte sie nachzählen statt sie zu
erinnern.

## Follow-ups

- **E2E-Lücke:** dass `Bound Hosts` korrekt im Profil steht, ist statisch geprüft;
  dass iTerm2 daraufhin umschaltet, nicht. Bräuchte eine GUI-Sitzung mit
  Shell-Integration. Als Issue tracken.
- **AC-term-5-3 ohne Test:** dass der Skill die stummen Fehlerbilder benennt, prüft
  kein Test — ein Grep auf Prosa würde die Formulierung einfrieren statt die Aussage
  zu messen.
- **Der Flag-Modus erzeugt keine Light/Dark-Varianten**, das Template schon. Wer ein
  Profil per Flags baut, bekommt bei einem OS-Themenwechsel unpassende Vordergrundfarben.
- **Zweites Template** (VibeSkills o. ä.) wäre der Beweis, dass die Template-Ebene
  wirklich generisch ist und nicht bloß den einen Fall abbildet.
