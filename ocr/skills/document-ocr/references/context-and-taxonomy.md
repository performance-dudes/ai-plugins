# The CONTEXT block — generic, user-supplied

The plugin ships **no** names, document types or taxonomy. The single biggest
quality lever is the CONTEXT you provide per run. Copy this template, fill it in
for your situation, and pass it as `context` (workflow) or `--context-file`
(klassifiziere.py).

```text
PEOPLE (for person assignment — note easy mix-ups):
- <Name / label> = <who they are, which documents are theirs>
- <Name / label> = <...>   (NOT to be confused with <similar name>)

DOCUMENT TYPES that typically occur:
- <IDs / certificates / tax / contracts / medical / invoices / private ...>

TARGET TAXONOMY (zielordner = relative path under the documents root):
- IDs/            identity, certificates
- Tax/            tax statements, returns, assessments
- Certificates/   registration, study, insurance confirmations
- Contracts/      contracts & insurance
- Medical/        medical records
- Invoices/       receipts, warranties
- Private/        photos, drawings, keepsakes without filing value
  (adapt these folder names to your own archive)

NAMING CONVENTION for sprechender_name (without extension):
  YYYY-MM-DD_Type_Person[_Detail]
  - date = the DOCUMENT date, not the scan date. Year only -> "YYYY".
  - no date determinable -> omit the date part.
  - umlauts allowed, no slashes.
```

## Why it matters

The classifier corrects names and picks folders **only** from this context. A
rich context yields precise type/person/folder assignments; an empty context
still produces a proposal, but conservative (person/date → "unbekannt",
zielordner possibly empty, lower confidence).

Keep it up to date as new people, document types or folders appear.
