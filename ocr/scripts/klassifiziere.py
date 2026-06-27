#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
klassifiziere.py — phase 3 of the OCR flow: raw OCR text -> document proposal.

Reads the .txt files from ocr.py, sends each document's text together with a
user-provided CONTEXT block and the generic classification prompt
(classify_prompt.md, next to this script) through `claude -p`, and produces a
structured proposal per document: type, person, date, speaking filename, target
folder, confidence, reasoning.

Generic: this script ships NO personal data. All domain knowledge — who is who,
the document types, the target taxonomy and the naming convention — comes from
the CONTEXT you pass with --context-file (or --context). With no context it still
classifies, just more conservatively.

Output:
  <ocr-dir>/_vorschlag.json   machine-readable  -> input for anwenden.py
  <ocr-dir>/_vorschlag.md     review table for a human

NOTHING is moved or renamed. A human reviews _vorschlag.md (and corrects
_vorschlag.json if needed), then runs anwenden.py.

Usage:
  uv run klassifiziere.py <ocr-dir> [--context-file ctx.txt] [--model opus|sonnet] [--limit N]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

PROMPT_FILE = Path(__file__).with_name("classify_prompt.md")
CLAUDE_TIMEOUT_S = 600


def call_claude(prompt: str, model: str = "opus") -> str:
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    r = subprocess.run(
        ["claude", "-p", "--model", model, "--output-format", "text"],
        input=prompt, capture_output=True, text=True,
        timeout=CLAUDE_TIMEOUT_S, encoding="utf-8", env=env,
    )
    if r.returncode != 0:
        sys.stderr.write(f"claude exit {r.returncode}: {r.stderr[:1000]}\n")
        r.check_returncode()
    return r.stdout.strip()


def parse_json(text: str) -> dict:
    """Extract the first JSON object from the model answer (robust against preamble)."""
    s = text.find("{")
    e = text.rfind("}")
    if s == -1 or e == -1:
        raise ValueError(f"no JSON in answer: {text[:200]}")
    return json.loads(text[s:e + 1])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("ocr_dir", type=Path)
    ap.add_argument("--context-file", type=Path, default=None,
                    help="file with the CONTEXT block (who-is-who, types, taxonomy, naming)")
    ap.add_argument("--context", default=None, help="inline CONTEXT (overrides --context-file)")
    ap.add_argument("--model", default="opus")
    ap.add_argument("--limit", type=int, default=0, help="only first N (test run)")
    args = ap.parse_args()

    task = PROMPT_FILE.read_text(encoding="utf-8")
    if args.context is not None:
        context = args.context
    elif args.context_file is not None:
        context = args.context_file.read_text(encoding="utf-8")
    else:
        context = "(Kein Kontext angegeben. Ordne konservativ ein; person/datum im Zweifel 'unbekannt'.)"

    txts = sorted(p for p in args.ocr_dir.glob("*.txt") if not p.name.startswith("_"))
    if args.limit:
        txts = txts[:args.limit]
    if not txts:
        print(f"no *.txt in {args.ocr_dir} — run ocr.py first.", file=sys.stderr)
        return 1

    print(f"{len(txts)} documents -> classify via claude ({args.model})")
    results = []
    for i, txt in enumerate(txts, 1):
        content = txt.read_text(encoding="utf-8").strip()
        prompt = (
            f"KONTEXT:\n{context}\n\n"
            f"OCR-TEXT eines gescannten Dokuments (Datei-ID: {txt.stem}):\n"
            f"---\n{content[:8000]}\n---\n\n{task}"
        )
        t0 = time.time()
        try:
            obj = parse_json(call_claude(prompt, args.model))
        except Exception as e:  # noqa: BLE001
            obj = {"dokumenttyp": "ERROR", "konfidenz": "niedrig",
                   "ist_muell": False, "begruendung": str(e)[:200]}
        obj["session"] = txt.stem
        obj["ocr_zeichen"] = len(content)
        results.append(obj)
        print(f"   {i}/{len(txts)} {txt.stem}: {obj.get('dokumenttyp', '?')} "
              f"[{obj.get('konfidenz', '?')}] {time.time() - t0:.1f}s")

    out_json = args.ocr_dir / "_vorschlag.json"
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    md = ["# OCR classification proposal", "",
          f"Source: `{args.ocr_dir}` · {len(results)} documents · model: {args.model}", "",
          "> Review, correct `_vorschlag.json` if needed, then `uv run anwenden.py`.", "",
          "| ID | Type | Person | Date | -> speaking name | Target folder | Conf. | Trash |",
          "|---|---|---|---|---|---|---|---|"]
    for r in results:
        md.append("| {session} | {dokumenttyp} | {person} | {datum} | {sprechender_name} "
                  "| {zielordner} | {konfidenz} | {muell} |".format(
                      session=r.get("session", ""), dokumenttyp=r.get("dokumenttyp", ""),
                      person=r.get("person", ""), datum=r.get("datum", ""),
                      sprechender_name=r.get("sprechender_name", ""),
                      zielordner=r.get("zielordner", ""), konfidenz=r.get("konfidenz", ""),
                      muell="x" if r.get("ist_muell") else ""))
    lowconf = [r for r in results if r.get("konfidenz") == "niedrig"]
    if lowconf:
        md += ["", f"## {len(lowconf)} low confidence (check manually)", ""]
        for r in lowconf:
            md.append(f"- **{r['session']}**: {r.get('begruendung', '')}")
    (args.ocr_dir / "_vorschlag.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"\n{out_json}\n{args.ocr_dir / '_vorschlag.md'}  <- review now")
    return 0


if __name__ == "__main__":
    sys.exit(main())
