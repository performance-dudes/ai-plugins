# Hooks — automatische Ereignis-Programme

## Was ist es?
Ein **Hook** ist ein kleines Programm, das **automatisch** läuft, wenn in Claude
Code ein bestimmtes **Ereignis** passiert (z.B. „bevor ein Werkzeug benutzt wird").
Damit kann man mitprotokollieren, Kontext hinzufügen oder eine Aktion **blocken**.

## Datei & Format
- **Konfig:** `hooks/hooks.json` — sagt, *welches Ereignis* welches Programm startet.
- **Programm:** meist eine `.sh` in `hooks/scripts/` — das wird **ausgeführt**.
- Im example liegen beide als sichere Vorlage: `hooks/hooks.json.example` +
  `hooks/scripts/example-pretooluse.sh`.

## Wie ein Hook „spricht" (das Wichtigste)
Ein Hook bekommt die Ereignis-Infos als **JSON über die Standardeingabe (stdin)**
und antwortet über seinen **Exit-Code**:

| Exit-Code | Bedeutung |
|---|---|
| `0` | alles ok (erlauben) — optional JSON auf stdout für Zusatz-Infos |
| `2` | **blocken** — die stderr-Meldung geht als Begründung zurück |
| andere | nicht-blockierender Fehler (wird nur protokolliert) |

Manche Ereignisse erlauben zusätzlich eine **JSON-Antwort** auf stdout, z.B. beim
`PreToolUse`: `permissionDecision` = `allow` / `deny` / `ask`, oder `updatedInput`
um die Werkzeug-Eingabe umzuschreiben.

## Wann & von wo gelesen
`hooks/hooks.json` wird **bei Sitzungsstart** gelesen (und bei Datei-Änderung
automatisch neu). Die Hook-Programme laufen dann **automatisch** beim jeweiligen
Ereignis — deshalb im example als `.example` entschärft.

## Die Ereignis-Typen (es gibt 24+)
Das example zeigt nur **einen** (`PreToolUse`). Hier die ganze Familie, gruppiert:

| Gruppe | Ereignisse | Wann |
|---|---|---|
| **Sitzung** | `SessionStart`, `SessionEnd`, `Setup` | Start / Ende der Sitzung |
| **Eingabe** | `UserPromptSubmit`, `UserPromptExpansion` | du schickst etwas / ein `/`-Befehl wird aufgelöst |
| **Werkzeuge** | `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, `PermissionRequest`, `PermissionDenied` | rund um jeden Werkzeug-Aufruf |
| **Antwort** | `Stop`, `StopFailure`, `MessageDisplay` | Claude beendet eine Antwort / zeigt Text |
| **Helfer & Tasks** | `SubagentStart`, `SubagentStop`, `TaskCreated`, `TaskCompleted`, `TeammateIdle` | Subagenten und Aufgaben |
| **Dateien & Umgebung** | `FileChanged`, `CwdChanged`, `ConfigChange`, `InstructionsLoaded` | Datei/Ordner/Konfig ändert sich |
| **Worktrees** | `WorktreeCreate`, `WorktreeRemove` | Git-Arbeitskopien |
| **Kontext** | `PreCompact`, `PostCompact` | bevor/nachdem der Verlauf zusammengefasst wird |
| **MCP-Formulare** | `Elicitation`, `ElicitationResult` | ein MCP-Server fragt nach Eingabe |
| **Hinweise** | `Notification` | Claude Code zeigt eine Benachrichtigung |

Die wichtigsten zum Einsteigen: **`PreToolUse`** (vor einem Werkzeug — kann
blocken), **`PostToolUse`** (danach — kann Kontext ergänzen), **`UserPromptSubmit`**
(bevor Claude deine Eingabe sieht), **`SessionStart`** (Sitzung beginnt).

## Im example-Plugin
`hooks/scripts/example-pretooluse.sh` ist ein harmloses Beispiel: Es meldet auf
stderr „PreToolUse-Hook hat einen Bash-Aufruf gesehen" und beendet mit `0`
(erlaubt). So testest du ihn ohne Claude:

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"ls"}}' \
  | bash example/hooks/scripts/example-pretooluse.sh ; echo "exit=$?"
```
