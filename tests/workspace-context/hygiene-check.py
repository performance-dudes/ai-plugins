#!/usr/bin/env python3
"""Hygiene check: no client names or internal identifiers in the public plugin.

Why hashes instead of the words themselves
------------------------------------------
The obvious implementation — a `rg` pattern listing the forbidden words — has to
put those words into this file, in a public repository. The usual workaround is to
break them with string concatenation so the check does not match itself. That
"works" and is precisely the problem: it defeats grep, it defeats this very check,
and it defeated an automated reviewer that reported the terms as absent. It does
not defeat anyone who opens the file.

So the terms live here only as SHA-256 prefixes. The check still finds them, the
repository no longer contains them in any form, and nobody has to be careful about
how they write about it.

How the scan works
------------------
The terms have known lengths. For each line of each scanned file we hash every
substring of exactly those lengths (lowercased) and look the digest up. That finds
a term regardless of what surrounds it — inside a path, an identifier, a compound
word — where a word-boundary match would miss it.

Adding a term:  python3 hygiene-check.py --hash "<term>"   then paste the output.
"""

import hashlib
import pathlib
import sys

# SHA-256 prefixes (12 hex chars) of the lowercased forbidden terms.
FORBIDDEN = {
    "50b752d57a22",
    "00315d60ca19",
    "137344713b79",
    "33b3fb69005f",
    "3101aac36baf",
}
LENGTHS = sorted({8, 9, 17, 26})
SKIP_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".zip"}


def digest(s: str) -> str:
    return hashlib.sha256(s.lower().encode()).hexdigest()[:12]


def scan_text(text: str):
    """Yield (line_no, length) for every forbidden substring found."""
    for lineno, line in enumerate(text.splitlines(), 1):
        low = line.lower()
        for n in LENGTHS:
            for i in range(len(low) - n + 1):
                if digest(low[i:i + n]) in FORBIDDEN:
                    yield lineno, n


def main() -> int:
    if len(sys.argv) >= 3 and sys.argv[1] == "--hash":
        print(f'    "{digest(sys.argv[2])}",   # length {len(sys.argv[2])}')
        return 0
    if len(sys.argv) < 2:
        print("usage: hygiene-check.py <directory> | --hash <term>", file=sys.stderr)
        return 2

    root = pathlib.Path(sys.argv[1])
    if not root.exists():
        print(f"hygiene: no such directory: {root}", file=sys.stderr)
        return 2

    hits = []
    for f in sorted(root.rglob("*")):
        if not f.is_file() or f.suffix.lower() in SKIP_SUFFIXES:
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue          # binary or unreadable — nothing textual to leak
        for lineno, n in scan_text(text):
            hits.append(f"{f}:{lineno} (term of length {n})")

    if hits:
        print("hygiene: forbidden term(s) found — client names and internal "
              "identifiers must not appear in the public plugin:", file=sys.stderr)
        for h in hits:
            print(f"  {h}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
