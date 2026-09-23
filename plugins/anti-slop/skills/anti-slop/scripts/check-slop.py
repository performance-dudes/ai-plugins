#!/usr/bin/env python3
"""Grep a draft against the slop lists (EN + DE).

The German list needs more than a literal match: German inflects. A plain
\b-anchored search for "entscheidend" misses "entscheidende", "entscheidender",
"entscheidendes" — which is how the word actually appears. Entries ending in "*"
therefore match the stem plus a short suffix.

Usage:
    check-slop.py draft.md                 # auto-detect language
    check-slop.py --lang de draft.md       # force one list
    check-slop.py --lang both draft.md
    check-slop.py --hard-only draft.md     # skip terms that are legitimate in isolation
    check-slop.py --context draft.md       # show the line each hit sits on

Exit code: 0 = no hit, 1 = at least one hit (soft included), 2 = draft unreadable.
ANTI_SLOP_DATA=<dir> points the checker at another data directory (tests use it
for fixtures; production never sets it).
"""
import argparse
import json
import os
import pathlib
import re
import sys
from collections import defaultdict

DATA = pathlib.Path(os.environ.get("ANTI_SLOP_DATA") or
                    pathlib.Path(__file__).resolve().parent.parent / "data")
LISTS = {
    "en": [DATA / "slop-list-en-extra.json"],
    "de": [DATA / "slop-list-de.json"],
    # Always loaded: stock names, chatbot artifacts and unfilled placeholders do
    # not depend on the language of the surrounding text.
    "universal": [DATA / "slop-list-universal.json"],
}

# Function words that are common in German and rare-to-absent in English.
DE_MARKERS = re.compile(
    r"\b(?:der|die|das|und|nicht|ist|sich|auch|eine|einen|werden|wurde|dass|für|"
    r"mit|von|dem|den|des|aber|noch|schon|wir|sie|ich)\b"
)
# Suffix budget for a "*" entry: German endings are short (-e, -en, -sten, -ungen).
STEM_SUFFIX = r"\w{0,5}"


def overrides():
    """Terms demoted to soft: technical vocabulary and ordinary English that the
    lists rightly flag as over-represented but that cannot convict on its own."""
    f = DATA / "severity-overrides.json"
    return set(json.loads(f.read_text(encoding="utf-8"))["soft"]) if f.exists() else set()


def load(lang):
    """Return [(term, category, severity), ...] for every list of `lang`."""
    out = []
    for path in LISTS[lang]:
        for entry in json.loads(path.read_text(encoding="utf-8")):
            term = entry[0].strip()
            if not term:
                continue
            out.append((term, entry[1], entry[2]))
    return out


def pattern(term):
    stem = term[:-1] if term.endswith("*") else term
    body = re.escape(stem).replace(r"\ ", r"\s+")
    tail = STEM_SUFFIX if term.endswith("*") else ""
    # \b fails after "!" or "…"; anchor on a non-word lookaround instead.
    lead = r"\b" if stem[:1].isalnum() else r"(?<!\w)"
    trail = r"\b" if (stem[-1:].isalnum() or term.endswith("*")) else r"(?!\w)"
    return re.compile(lead + body + tail + trail, re.IGNORECASE)


def detect(text):
    words = max(len(re.findall(r"\w+", text)), 1)
    return "de" if len(DE_MARKERS.findall(text.lower())) / words > 0.04 else "en"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("draft")
    ap.add_argument("--lang", choices=["de", "en", "both", "auto"], default="auto")
    ap.add_argument("--hard-only", action="store_true")
    ap.add_argument("--context", action="store_true")
    args = ap.parse_args()

    try:
        text = pathlib.Path(args.draft).read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"{args.draft}: Datei nicht gefunden", file=sys.stderr)
        return 2
    except UnicodeDecodeError:
        print(f"{args.draft}: kein UTF-8-Text", file=sys.stderr)
        return 2
    lines = text.splitlines()
    n_words = len(re.findall(r"\w+", text))
    words = max(n_words, 1)  # density divisor only

    lang = detect(text) if args.lang == "auto" else args.lang
    langs = ["en", "de"] if lang == "both" else [lang]

    candidates = []  # (start, end, term, cat, sev, match)
    gesehen = set()
    soft_override = overrides()
    # universal first: a stock name must stay soft even when a language list
    # would rank it higher.
    for lg in ["universal"] + langs:
        for term, cat, sev in load(lg):
            if term in soft_override:
                sev = "soft"
            # Memoise BEFORE the --hard-only filter. Dropping a soft term without
            # remembering it lets a later list re-introduce the same term as hard,
            # which would break the "universal wins" rule in exactly the mode the
            # eval runs in.
            if term in gesehen:
                continue
            gesehen.add(term)
            if args.hard_only and sev != "hard":
                continue
            for h in pattern(term).finditer(text):
                candidates.append((h.start(), h.end(), term, cat, sev, h))

    # Overlapping entries count once: "is a testament to" must not also score
    # "a testament to", "testament to" and "testament". A hard match wins over a
    # soft one (a longer soft phrase must not hide a hard tell), then the longest.
    taken, kept = [], defaultdict(list)
    for start, end, term, cat, sev, h in sorted(candidates, key=lambda c: (c[4] != "hard", c[0] - c[1], c[0])):
        if any(start < e and s < end for s, e in taken):
            continue
        taken.append((start, end))
        kept[(cat, sev, term)].append(h)
    found = defaultdict(list)
    for (cat, sev, term), hits in kept.items():
        found[(cat, sev)].append((term, sorted(hits, key=lambda h: h.start())))
    total = len(taken)

    print(f"{args.draft}: {n_words} Wörter, Liste(n): universal + {', '.join(langs)}")
    if not found:
        print("Keine Treffer.")
        return 0

    print(f"{total} Treffer, {total / words * 1000:.1f} pro 1000 Wörter\n")
    for (cat, sev) in sorted(found, key=lambda k: (k[1] != "hard", k[0])):
        mark = "!!" if sev == "hard" else "? "
        print(f"{mark} {cat} ({sev})")
        for term, hits in sorted(found[(cat, sev)]):
            # Ein Treffer über einen Zeilenumbruch trägt das "\n" in group(0);
            # ungefiltert bricht die Ausgabe nach dem ersten Wort ab.
            forms = sorted({re.sub(r"\s+", " ", h.group(0).lower()) for h in hits})
            shown = ", ".join(forms[:4]) + (" …" if len(forms) > 4 else "")
            print(f"     {term:<45} {len(hits)}x  → {shown}")
            if args.context:
                for h in hits[:3]:
                    ln = text.count("\n", 0, h.start())
                    print(f"       L{ln + 1}: {lines[ln].strip()[:100]}")
        print()

    print("Jeder Treffer ist eine Frage, kein Urteil. '!!' = raus, sofern nicht")
    print("Zitat oder Fachbegriff. '?' = einzeln legitim, im Cluster verdächtig.")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
