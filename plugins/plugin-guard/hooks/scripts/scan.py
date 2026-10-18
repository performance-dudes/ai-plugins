#!/usr/bin/env python3
"""plugin-guard — Start-Audit aller installierten Plugins (klassischer SessionStart-Hook).

Das Mod-Gate (hooks/register.ts) sieht nur Hooks-Module, die NACH ihm laden, und nur
JS/TS. Dieser Scan ergänzt beim Start den Rest: jedes Plugin unter den Plugin-Wurzeln
— Shell-Hooks, MCP-Server-Kommandos, Skripte, Module — gegen dieselbe rules/rules.json,
plus Änderungserkennung (neu / geändert seit letztem Start = Update).

Aufrufe:
  scan.py --hook            als SessionStart-Hook: stdin = Event-JSON, stdout = JSON mit
                            systemMessage (nur wenn es etwas zu melden gibt), immer Exit 0
  scan.py [--json] [ROOT…]  von Hand / in CI; --fail-at high|critical setzt Exit 1

Umgebung: PLUGIN_GUARD_ROOTS (Pfadliste), PLUGIN_GUARD_STATE_DIR, CLAUDE_PLUGIN_ROOT
(eigene Wurzel, wird übersprungen — rules.json und Tests enthalten die Muster selbst).
Nur Standardbibliothek.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT") or HERE.parent.parent).resolve()
RANK = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


def load_rules() -> dict:
    return json.loads((PLUGIN_ROOT / "rules" / "rules.json").read_text())


def default_roots() -> list[Path]:
    env = os.environ.get("PLUGIN_GUARD_ROOTS")
    if env:
        return [Path(p).expanduser() for p in env.split(os.pathsep) if p]
    roots = [Path.home() / ".claude" / "plugins"]
    roots += [Path(p).expanduser() for p in os.environ.get("CLAUDE_CODE_PLUGIN_DIRS", "").split(os.pathsep) if p]
    return roots


def discover(roots: list[Path]) -> list[Path]:
    """Jedes Verzeichnis mit .claude-plugin/plugin.json ist ein Plugin; darunter nicht weiter suchen."""
    found: list[Path] = []
    for root in roots:
        if not root.is_dir():
            continue
        for dirpath, dirnames, _ in os.walk(root):
            here = Path(dirpath)
            if (here / ".claude-plugin" / "plugin.json").is_file():
                found.append(here.resolve())
                dirnames[:] = []
                continue
            dirnames[:] = [d for d in dirnames if d not in (".git", "node_modules")]
    own = PLUGIN_ROOT
    return sorted({p for p in found if p != own and own not in p.parents})


def code_files(root: Path, rules: dict, findings: list[dict]) -> list[str]:
    exts = tuple(rules["codeExtensions"])
    skip_paths = set(rules["skipPaths"])
    skip_files = set(rules["skipFiles"])
    files: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        here = Path(dirpath)
        dirnames[:] = sorted(d for d in dirnames if (here / d).relative_to(root).as_posix() not in skip_paths)
        for d in dirnames:
            if (here / d).is_symlink():  # os.walk folgt nicht — ungeprüft wäre ein Versteck
                findings.append({"rule": "symlink", "severity": "medium", "why": "Link — Ziel liegt evtl. außerhalb des Plugins", "where": (here / d).relative_to(root).as_posix()})
        for name in sorted(filenames):
            path = here / name
            rel = path.relative_to(root).as_posix()
            if not name.endswith(exts) or rel in skip_files:
                continue
            if path.is_symlink():
                findings.append({"rule": "symlink", "severity": "medium", "why": "Link — Ziel liegt evtl. außerhalb des Plugins", "where": rel})
                continue
            if path.stat().st_size > rules["maxFileBytes"]:
                findings.append({"rule": "unscanned-large-file", "severity": "medium", "why": "zu groß zum Prüfen", "where": rel})
                continue
            if len(files) >= rules["maxFiles"]:
                findings.append({"rule": "too-many-files", "severity": "medium", "why": f"mehr als {rules['maxFiles']} Code-Dateien — Rest ungeprüft"})
                return sorted(files)
            files.append(rel)
    return sorted(files)


def surface(root: Path) -> list[str]:
    """Was das Plugin ausführen kann — zur Einordnung, kein Befund."""
    out: list[str] = []
    hooks = root / "hooks" / "hooks.json"
    if hooks.is_file():
        try:
            doc = json.loads(hooks.read_text())
            if doc.get("modules"):
                out.append(f"Mod-Module: {', '.join(doc['modules'])}")
            if doc.get("hooks"):
                out.append(f"Command-Hooks auf: {', '.join(sorted(doc['hooks']))}")
        except (ValueError, OSError):
            out.append("hooks.json nicht lesbar")
    for mcp in (root / ".mcp.json", root / ".claude-plugin" / "plugin.json"):
        try:
            servers = json.loads(mcp.read_text()).get("mcpServers") if mcp.is_file() else None
        except (ValueError, OSError):
            servers = None
        if isinstance(servers, dict) and servers:
            out.append(f"MCP-Server: {', '.join(sorted(servers))}")
    return out


def scan_plugin(root: Path, rules: dict) -> dict:
    findings: list[dict] = []
    files = code_files(root, rules, findings)
    compiled = [(r, re.compile(r["pattern"], re.IGNORECASE if r.get("flags") == "i" else 0)) for r in rules["sourceRules"]]
    digest = hashlib.sha256()
    for rel in files:
        text = (root / rel).read_text(encoding="utf-8", errors="replace")
        digest.update(f"{rel}\0{text}\0".encode())
        for rule, rx in compiled:
            m = rx.search(text)
            if m:
                line = text.count("\n", 0, m.start()) + 1
                findings.append({"rule": rule["id"], "severity": rule["severity"], "why": rule["why"], "where": f"{rel}:{line}"})
    findings.sort(key=lambda f: -RANK[f["severity"]])
    try:
        manifest = json.loads((root / ".claude-plugin" / "plugin.json").read_text())
    except (ValueError, OSError):
        manifest = {}
    level = max((f["severity"] for f in findings), key=lambda s: RANK[s], default="none")
    return {
        "root": str(root),
        "name": manifest.get("name", root.name),
        "version": manifest.get("version"),
        "hash": digest.hexdigest(),
        "level": level,
        "surface": surface(root),
        "findings": findings,
    }


def diff_state(results: list[dict], state_file: Path) -> tuple[list[str], list[str], list[str]]:
    try:
        old = json.loads(state_file.read_text())
    except (ValueError, OSError):
        old = None
    now = {r["root"]: {"hash": r["hash"], "name": r["name"], "version": r["version"], "level": r["level"]} for r in results}
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(now, indent=2))
    if old is None:  # erster Lauf: alles ist „neu", das wäre Rauschen
        return [], [], []
    new = [r for r in now if r not in old]
    changed = [r for r in now if r in old and old[r]["hash"] != now[r]["hash"]]
    removed = [r for r in old if r not in now]
    return new, changed, removed


def render(results: list[dict], new: list[str], changed: list[str], removed: list[str], verbose: bool) -> str:
    lines: list[str] = []
    for r in sorted(results, key=lambda r: -RANK[r["level"]]):
        flag = " (NEU)" if r["root"] in new else " (GEÄNDERT seit letztem Start)" if r["root"] in changed else ""
        serious = [f for f in r["findings"] if RANK[f["severity"]] >= RANK["medium"]]
        if not verbose and not flag and RANK[r["level"]] < RANK["high"]:
            continue
        lines.append(f"[{r['level']}] {r['name']}@{r['version'] or '?'}{flag} — {r['root']}")
        for f in serious[:6]:
            lines.append(f"    {f['severity']:<8} {f['rule']}: {f['why']}" + (f" — {f['where']}" if f.get("where") else ""))
        if verbose:
            for s in r["surface"]:
                lines.append(f"    · {s}")
    for root in removed:
        lines.append(f"[entfernt] {root}")
    if not lines:
        return ""
    worst = max((r["level"] for r in results), key=lambda s: RANK[s], default="none")
    head = f"plugin-guard: {len(results)} Plugins geprüft, höchster Befund: {worst}"
    if new or changed:
        head += f", {len(new)} neu, {len(changed)} geändert"
    return "\n".join([head, *lines])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("roots", nargs="*", type=Path)
    ap.add_argument("--hook", action="store_true", help="als SessionStart-Hook laufen")
    ap.add_argument("--json", action="store_true", help="Ergebnis als JSON")
    ap.add_argument("--fail-at", choices=["medium", "high", "critical"], help="Exit 1 ab dieser Schwere")
    ap.add_argument("--state-dir", type=Path, default=Path(os.environ.get("PLUGIN_GUARD_STATE_DIR") or Path.home() / ".claude" / "plugin-guard"))
    args = ap.parse_args()

    if args.hook:
        try:
            sys.stdin.read()  # Event-JSON; wir brauchen nur den Anlass
        except OSError:
            pass

    rules = load_rules()
    results = [scan_plugin(p, rules) for p in discover(args.roots or default_roots())]
    new, changed, removed = diff_state(results, args.state_dir / "state.json")
    (args.state_dir / "last-scan.json").write_text(json.dumps({"plugins": results, "new": new, "changed": changed, "removed": removed}, indent=2))

    if args.hook:
        text = render(results, new, changed, removed, verbose=False)
        if text:
            print(json.dumps({"systemMessage": text + f"\nDetails: {args.state_dir / 'last-scan.json'} · Mod-Urteile: /plugin-guard"}))
        return 0
    if args.json:
        print(json.dumps({"plugins": results, "new": new, "changed": changed, "removed": removed}, indent=2))
    else:
        print(render(results, new, changed, removed, verbose=True) or f"plugin-guard: {len(results)} Plugins geprüft, keine Befunde.")
    worst = max((r["level"] for r in results), key=lambda s: RANK[s], default="none")
    return 1 if args.fail_at and RANK[worst] >= RANK[args.fail_at] else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 — ein Audit darf die Session nie stören
        if "--hook" in sys.argv:
            print(json.dumps({"systemMessage": f"plugin-guard: Start-Audit fehlgeschlagen ({exc.__class__.__name__}: {exc}) — Mod-Gate bleibt aktiv."}))
            sys.exit(0)
        raise
