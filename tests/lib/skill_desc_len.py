#!/usr/bin/env python3
"""Länge der `description` einer SKILL.md in ZEICHEN (oder -1). stdlib-only.

Geteilte Quelle für den repo-weiten description-Guard (tests/structure/check.sh)
und etwaige Plugin-Suiten. Deckt inline, gequotet UND YAML-Block-Scalars
(>, >-, >+, |, |-, |+) ab.

Hintergrund: ein früherer Guard extrahierte per `^description:\\s*(.*)$` und fing
bei einem Folded Scalar (`description: >-`) nur die zwei Zeichen ">-" statt des
Bodys auf den Folgezeilen — er war damit bei JEDEM Folded Scalar blind, meldete
grün und schützte das 1024-Loader-Limit faktisch nicht. Diese Extraktion ist
gegen echtes YAML-Parsing (pyyaml) validiert und liefert für inline wie folded
dieselbe Länge. Einzige Ausnahme, bewusst konservativ: bei Clip-Scalars (`>`, `|`)
zählt der Zeilenumbruch am Ende mit. Striktes YAML behält ihn, sobald nach der
description noch ein Key folgt; ob ein Loader ihn am Blockende abschneidet, ist
nicht garantiert — die obere Schranke ist die sichere.

Aufruf: `python3 skill_desc_len.py <pfad/zu/SKILL.md>` → Länge auf stdout.
"""
import re
import sys


def description_length(path: str) -> int:
    lines = open(path, encoding="utf-8").read().splitlines()
    if not lines or lines[0].strip() != "---":
        return -1
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return -1
    fm = lines[1:end]
    desc = None
    for i, ln in enumerate(fm):
        m = re.match(r"^description:\s*(.*)$", ln)
        if not m:
            continue
        rest = m.group(1).strip()
        if rest in (">", ">-", ">+", "|", "|-", "|+"):          # Block-Scalar
            cont = []
            for cl in fm[i + 1:]:
                if cl.strip() == "":
                    cont.append("")
                    continue
                if not cl.startswith((" ", "\t")):              # nächster Top-Level-Key
                    break
                cont.append(cl)
            indents = [len(c) - len(c.lstrip()) for c in cont if c.strip()]
            ind = min(indents) if indents else 0
            body = [c[ind:] if len(c) >= ind else c for c in cont]
            if rest.startswith(">"):                            # folded: NL im Absatz -> Space
                paras, cur = [], []
                for c in body:
                    if c == "":
                        if cur:
                            paras.append(" ".join(cur))
                            cur = []
                    else:
                        cur.append(c)
                if cur:
                    paras.append(" ".join(cur))
                desc = "\n".join(paras)
            else:                                               # literal: NL bleibt
                desc = "\n".join(body).rstrip("\n")
            if rest in (">", "|"):                              # Clip: EIN NL am Ende zählt mit
                desc += "\n"
        else:                                                   # inline (ggf. gequotet)
            v = rest
            if len(v) >= 2 and v[0] in "\"'" and v[-1] == v[0]:
                v = v[1:-1]
            desc = v
        break
    return len(desc) if desc is not None else -1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: skill_desc_len.py <SKILL.md>", file=sys.stderr)
        sys.exit(2)
    print(description_length(sys.argv[1]))
