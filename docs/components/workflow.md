# Workflow-Technik — `greet.js`

## Was ist es?
Ein **kleines Programm in mehreren Schritten** („Fließband"). Hier nimmt es einen
Namen, fragt ein kleines Modell nach einer Begrüßung und gibt ein Ergebnis zurück.

## Wichtig: kein „Auto-Baustein", sondern eine Technik
Anders als Command/Skill/Agent wird ein Workflow-Script **nicht** automatisch
entdeckt. Ein Plugin **legt das Script in `workflows/` ab** und ruft es **per Pfad**
auf — aus einem Command oder einer Skill:

```js
Workflow({ scriptPath: "${CLAUDE_PLUGIN_ROOT}/workflows/greet.js", args: "$ARGUMENTS" })
```

`${CLAUDE_PLUGIN_ROOT}` = der Ordner, in dem das Plugin installiert wurde. Dadurch
wird das Script **egal wo** gefunden.

## Datei & Format
- **Datei:** `workflows/<name>.js`
- **Format:** `.js` (JavaScript) → wird von der Workflow-Maschine **ausgeführt**.

## Wann & wo ausgeführt
Erst **wenn ein Command oder eine Skill es per `scriptPath` startet**. Es läuft im
Hintergrund und liefert am Ende ein Ergebnis (hier `{ who, greeting }`).

## Im example-Plugin
`workflows/greet.js`: liest `args` (den Namen), ruft `agent(...)` mit einem kleinen,
schnellen Modell und gibt `{ who, greeting }` zurück. Command **und** Skill nutzen
genau dieses eine Script.
