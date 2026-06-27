# Dateiformate: warum `.json`, `.md`, `.sh`, `.yml`?

Die Endung einer Datei verrät dir **wer sie liest und wie**. Das ist der Schlüssel
zur ganzen Plugin-Architektur.

| Endung | Was es ist | Wer liest/führt aus | Beispiele |
|---|---|---|---|
| `.json` | strenge **Daten** (Schlüssel→Wert) | ein **Programm** liest es als Einstellung | `plugin.json`, `marketplace.json`, `themes/*.json`, `.mcp.json` |
| `.md` | **Text/Anweisungen** in normaler Sprache | das **Modell (Claude)** liest und befolgt es | `commands/greet.md`, `SKILL.md`, `agents/greeter.md` |
| `.sh` | ein **ausführbares Programm** (Terminal-Befehle) | das **Betriebssystem** *führt es aus* | `hooks/scripts/*.sh`, `tests/validate.sh` |
| `.yml` | Daten wie JSON, nur menschenfreundlicher | hier: **GitHub** für die Auto-Prüfung | `.github/workflows/validate.yml` |
| `.js` | **JavaScript**-Programm | die **Workflow-Maschine** führt es aus | `workflows/greet.js` |
| `.example` | *keine* Sorte — ein **Aus-Schalter** | niemand, bis du die Endung entfernst | `hooks.json.example` |

## Die große Regel

> `.json` / `.yml` → ein **Programm** liest **Daten**.
> `.md` → das **Modell** liest **Anweisungen**.
> `.sh` / `.js` → etwas wird **ausgeführt**.

Deshalb ist ein **Command** eine `.md` (Claude liest deine Anweisung in Worten),
aber ein **Theme** eine `.json` (das Programm braucht exakte Farbwerte). **Das
Format folgt der Aufgabe** — nicht umgekehrt.

## Was ist Frontmatter?

Viele `.md`-Dateien beginnen mit einem Block zwischen `---`:

```markdown
---
name: greeter
description: ...
---
(ab hier normaler Text für das Modell)
```

Der `---`-Block sind die wenigen **maschinen-lesbaren Felder** (Name, Beschreibung).
Darunter folgt der **Anweisungstext** fürs Modell. So steckt in *einer* `.md`-Datei
beides: ein bisschen Daten (oben) und Anweisung (unten).
