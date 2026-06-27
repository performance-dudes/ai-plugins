# Spec: Feature „Begrüßen" (greet)

**Thema:** Das Plugin kann jemanden mit **einer** kurzen Zeile begrüßen — entweder
über einen getippten Befehl **oder** von allein über eine Skill. Beide Wege nutzen
**denselben** Workflow.

---

## US-GREET-1 — Begrüßen per Befehl `/greet`
> Als **Nutzer** will ich `/greet <Name>` tippen und eine kurze Begrüßung
> bekommen.

| AC | Kriterium | Test-Referenz |
|----|-----------|---------------|
| AC-GREET-1-1 | `/greet <Name>` startet den gebündelten Workflow per `scriptPath`. | headless `claude -p "/greet Felix"` |
| AC-GREET-1-2 | Der Workflow gibt strukturiert `{ who, greeting }` zurück. | `Workflow({ scriptPath: ".../greet.js", args: "Felix" })` |
| AC-GREET-1-3 | Ohne Namen wird `world` begrüßt. | `claude -p "/greet"` → Begrüßung an „world" |

---

## US-GREET-2 — Begrüßen ohne Befehl (Skill startet von allein)
> Als **Nutzer** will ich, dass eine Begrüßung auch ohne Befehl klappt, wenn ich
> es normal formuliere.

| AC | Kriterium | Test-Referenz |
|----|-----------|---------------|
| AC-GREET-2-1 | Die Skill `run-greet` startet denselben Workflow, wenn die Anfrage passt. | Trigger-Prompt `claude -p "begrüße die Performance Dudes"` |
| AC-GREET-2-2 | Befehl und Skill nutzen dasselbe `greet.js` (eine Quelle der Wahrheit). | informativ (beide rufen `scriptPath .../greet.js`) |
