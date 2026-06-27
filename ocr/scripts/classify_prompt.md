AUFGABE: Ordne den OCR-Text eines gescannten Dokuments ein. Nutze AUSSCHLIESSLICH
den oben bereitgestellten KONTEXT (wer ist wer, Dokumenttypen, Ziel-Taxonomie,
Benennungs-Konvention). Erfinde keine Personen, Ordner oder Daten, die der KONTEXT
nicht hergibt.

REGELN:
- person: ein Name/Label aus dem KONTEXT. Passt niemand eindeutig → "unbekannt".
  Verwechsle ähnlich klingende Personen nicht; im Zweifel "unbekannt".
- datum: das DOKUMENT-Datum (nicht das Scan-Datum). Nur Jahr bekannt → "YYYY".
  Kein Datum ermittelbar → "unbekannt".
- sprechender_name: Dateiname OHNE Endung nach der KONTEXT-Konvention (Default,
  falls KONTEXT keine nennt: YYYY-MM-DD_Typ_Person[_Detail]). Keine Slashes.
- zielordner: ein relativer Ordner aus der KONTEXT-Taxonomie (z. B. "Steuer/").
  Passt keiner → "" (leer) und konfidenz herabstufen.
- ist_muell: true NUR bei leerer Seite / unbrauchbarem Scan / reinem Foto ohne
  Aktenwert. Solche Dokumente werden NICHT gelöscht, nur beiseitegelegt.
- konfidenz: "hoch|mittel|niedrig". Bei wenig/rauschigem Text → "niedrig" und
  person/datum "unbekannt", begruendung sagt warum.
- Minimale Offenlegung: gib in der begruendung keine sensiblen Inhalte (Finanz-,
  Ausweis-, Gesundheitsdaten) breiter wieder als für die Einordnung nötig.

Antworte AUSSCHLIESSLICH mit EINEM JSON-Objekt (kein Markdown, kein Vorspann):
{
  "dokumenttyp": "<kurz, z. B. Lohnsteuerbescheinigung>",
  "person": "<Name/Label aus KONTEXT | unbekannt>",
  "datum": "<YYYY-MM-DD | YYYY | unbekannt>",
  "sprechender_name": "<Dateiname ohne Endung nach Konvention>",
  "zielordner": "<relativer Ordner aus der Taxonomie | \"\">",
  "konfidenz": "<hoch|mittel|niedrig>",
  "ist_muell": <true|false>,
  "begruendung": "<1 Satz, worauf die Einordnung beruht>"
}
