# Skill — `run-greet`

## Was ist es?
Eine Fähigkeit, die **Claude selbst** startet, wenn deine Anfrage passt — *ohne*
dass du einen Befehl kennst. Claude liest dazu die `description` der Skill und
entscheidet, ob sie zur Anfrage passt.

## Datei & Format
- **Datei:** `skills/<name>/SKILL.md` (hier `skills/run-greet/SKILL.md`)
- **Format:** `.md` mit Frontmatter (`name`, `description`) + Anweisungstext.
- Wichtig: jede Skill liegt in ihrem **eigenen Unterordner**.

## Wann & von wo gelesen
**Bei Sitzungsstart** entdeckt. Die `description` ist entscheidend: Claude liest
sie laufend mit, um zu erkennen *wann* die Skill dran ist.

## Wer löst es aus
**Claude** — automatisch, wenn die Anfrage zur `description` passt.

## Command vs. Skill
- **Command** = du tippst `/greet`.
- **Skill** = du sagst normal „begrüße die Performance Dudes", Claude startet sie
  von allein.
Beide führen hier in **denselben** Workflow → eine Quelle der Wahrheit.

## Im example-Plugin
`skills/run-greet/SKILL.md` ruft denselben `workflows/greet.js` auf wie der Command.
