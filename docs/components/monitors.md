# Monitors — Hintergrund-Prozesse  *(experimentell)*

## Was ist es?
Ein **Monitor** ist ein **dauerlaufender Hintergrund-Prozess**, dessen Ausgaben zu
Benachrichtigungen werden. Echte Monitore beobachten z.B. Logs oder ein Deployment.

## Datei & Format
- **Konfig:** `monitors/monitors.json` (im example als `.example`)
- **Programm:** meist eine `.sh` in `monitors/scripts/`, die dauerhaft läuft.
- **Format der Konfig:** `.json` (eine Liste von Monitor-Einträgen).

## Wann & wo ausgeführt
**Bei Sitzungsstart** (nur in interaktiven Sitzungen) — oder gezielt erst bei einem
Ereignis, z.B. `when: "on-skill-invoke:run-greet"`. Da es ein Dauer-Prozess ist,
liegt es im example als `.example` entschärft.

## Wer löst es aus
**Automatisch** beim Laden (oder beim angegebenen Ereignis).

## Status
**Experimentell** (ab Claude Code v2.1.105). In öffentlichen Plugins vorsichtig
einsetzen.

## Im example-Plugin
`monitors/monitors.json.example` + `monitors/scripts/heartbeat.sh` — der Beispiel-
Monitor gibt alle 30 Sekunden eine „heartbeat"-Zeile aus.
