# 2026-09-23 — merge-gate: Rerun nach Marker-Kommentar scheiterte mit 403

Bei #62 wurde der Freigabe-Marker `[merge-gate: ok]` per Kommentar gesetzt. Der Job
`rerun-on-marker` fand den Marker, startete den merge-gate-Lauf des PR-Heads aber nicht
neu: `gh: Resource not accessible by integration (HTTP 403)`. Der Check blieb rot, bis er
von Hand neu gestartet wurde.

## Ursache

Der Workflow-Token hat ohne ausdrückliche Angabe kein `actions: write`, und das braucht
`POST …/runs/{id}/rerun-failed-jobs`. Die Vorlage im merge-gate-Plugin
(`ai-plugins-internal`, `plugins/merge-gate/ci/workflow.template.yml`) setzt den Block
bereits; die hier übernommene Kopie stammte aus der Zeit davor.

## Fix

Job-Block `permissions` für `rerun-on-marker` (`contents: read`, `pull-requests: read`,
`actions: write`). Der Job `merge-gate` bleibt unverändert, er läuft mit den Standardrechten
grün.

## Nachprüfen

Nach dem Merge greift der Fix beim nächsten Marker-Kommentar auf einem PR: `issue_comment`-Läufe
nutzen die Workflow-Datei des Default-Branch. Innerhalb dieses PRs lässt er sich daher nicht
belegen.

## Zweiter Fehler: nur der neueste Lauf wurde neu gestartet

Bei #65 lag der Marker korrekt vor, der Merge blieb trotzdem `BLOCKED`. Auf dem PR-Commit
gab es zwei merge-gate-Läufe: einen vom Push (`synchronize`), einen vom bearbeiteten PR-Text
(`edited`). Der Rerun-Job holte per `per_page=1` nur den neuesten; der andere blieb rot und
blockierte den Required-Check.

Fix: alle roten Läufe des Commits neu starten (`event != issue_comment`,
`conclusion == failure`). Gegen echte Historie geprüft: `3d15fb5` liefert den einen roten Lauf,
`e96de1b` (inzwischen grün) keinen. Die Vorlage in `ai-plugins-internal` hat denselben Fehler.
