#!/usr/bin/env python3
"""Loader-Limit für ALLE descriptions eines Marketplace-Repos prüfen. stdlib-only.

Geprüft wird jede Stelle, die ein Plugin-Loader als `description` liest:

- `.claude-plugin/marketplace.json` — je Plugin-Eintrag
- `plugins/*/.claude-plugin/plugin.json`
- Frontmatter von `skills/*/SKILL.md`, `agents/*.md`, `commands/*.md`

Regeln:

1. Länge ≤ 1024 ZEICHEN (nicht Bytes). Claude Code toleriert mehr, die Copilot
   CLI verweigert das ganze Plugin. Das Limit gilt also, auch wenn Claude grün ist.
2. Eine inline, ungequotete Frontmatter-description darf kein `": "` enthalten.
   Striktes YAML liest das als verschachteltes Mapping und bricht ab; Claude Code
   lädt den Skill trotzdem, strengere Loader nicht. Fix: quoten oder `>-`.

Aufruf: `python3 check_descriptions.py <repo-root>` → je Verstoß eine Zeile
`FAIL <pfad>: <grund>` auf stdout, Exit 1; sonst `OK <anzahl>`, Exit 0.
"""
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from skill_desc_len import description_length  # noqa: E402

LIMIT = 1024


def unquoted_colon(path: pathlib.Path) -> bool:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return False
    for ln in lines[1:]:
        if ln.strip() == "---":
            return False
        m = re.match(r"^description:\s*(.*)$", ln)
        if m:
            v = m.group(1).strip()
            if v[:1] in ("'", '"', ">", "|") or not v:
                return False
            return ": " in v or v.endswith(":")
    return False


def main(root: pathlib.Path) -> int:
    fails, checked = [], 0

    def check_len(label: str, desc: str) -> None:
        nonlocal checked
        checked += 1
        if len(desc) > LIMIT:
            fails.append(f"{label}: description {len(desc)} > {LIMIT} Zeichen")

    mp = root / ".claude-plugin" / "marketplace.json"
    if mp.is_file():
        for e in json.loads(mp.read_text(encoding="utf-8")).get("plugins", []):
            check_len(f"marketplace.json[{e.get('name')}]", e.get("description", ""))

    for pj in sorted(root.glob("plugins/*/.claude-plugin/plugin.json")):
        check_len(str(pj.relative_to(root)), json.loads(pj.read_text(encoding="utf-8")).get("description", ""))

    md = sorted(
        list(root.glob("plugins/*/skills/*/SKILL.md"))
        + list(root.glob("plugins/*/agents/*.md"))
        + list(root.glob("plugins/*/commands/*.md"))
    )
    for f in md:
        if "node_modules" in f.parts:
            continue
        rel = str(f.relative_to(root))
        n = description_length(str(f))
        if n < 0:
            continue  # ohne Frontmatter-description: nicht Sache dieses Checks
        checked += 1
        if n > LIMIT:
            fails.append(f"{rel}: description {n} > {LIMIT} Zeichen")
        if unquoted_colon(f):
            fails.append(f"{rel}: ungequotete description enthält ': ' (striktes YAML bricht)")

    for line in fails:
        print(f"FAIL {line}")
    if not fails:
        print(f"OK {checked}")
    return 1 if fails else 0


def self_test() -> int:
    """Negativ-Fixture: ein Agent > 1024 und ein ungequoteter Doppelpunkt MÜSSEN
    beide gemeldet werden — sonst ist der Guard blind und färbt fälschlich grün."""
    import contextlib
    import io
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        r = pathlib.Path(tmp)
        (r / "plugins/neg/agents").mkdir(parents=True)
        (r / "plugins/neg/skills/s").mkdir(parents=True)
        (r / "plugins/neg/agents/a.md").write_text("---\nname: a\ndescription: " + "x" * 1100 + "\n---\n")
        (r / "plugins/neg/skills/s/SKILL.md").write_text('---\nname: s\ndescription: Baut das Sheet "A: B" neu\n---\n')
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            main(r)
    n = buf.getvalue().count("FAIL ")
    if n == 2:
        print("OK Negativ-Selbsttest: Agent-Überlauf und ungequoteter Doppelpunkt erkannt")
        return 0
    print(f"FAIL Negativ-Selbsttest: 2 Verstöße erwartet, {n} gemeldet")
    return 1


if __name__ == "__main__":
    if sys.argv[1:2] == ["--self-test"]:
        sys.exit(self_test())
    sys.exit(main(pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")))
