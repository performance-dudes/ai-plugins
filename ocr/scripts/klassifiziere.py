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

Throughput: documents are classified with a bounded thread pool (--jobs, default
4) and each `claude -p` call retries with exponential backoff on transient
server rate limits / overload. The default is intentionally modest — a wide
fan-out (e.g. dozens of parallel Opus calls) trips server-side rate limiting; a
handful of workers is fast yet stays under that ceiling.

Output:
  <ocr-dir>/_vorschlag.json   machine-readable  -> input for anwenden.py
  <ocr-dir>/_vorschlag.md     review table for a human

NOTHING is moved or renamed. A human reviews _vorschlag.md (and corrects
_vorschlag.json if needed), then runs anwenden.py.

Usage:
  uv run klassifiziere.py <ocr-dir> [--context-file ctx.txt] [--model opus|sonnet] [--limit N] [--jobs N]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

PROMPT_FILE = Path(__file__).with_name("classify_prompt.md")
CLAUDE_TIMEOUT_S = 600
# Substrings that mark a transient, retryable server condition (not a usage cap).
TRANSIENT_HINTS = (
    "temporarily limiting", "rate limit", "rate_limit", "ratelimit",
    "overloaded", "529", "503", "502", "timeout", "timed out",
)


def call_claude(prompt: str, model: str = "opus", retries: int = 5) -> str:
    """Run `claude -p`, retrying transient rate-limit/overload errors with backoff."""
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    delay = 5.0
    last = ""
    for attempt in range(retries + 1):
        transient = False
        try:
            r = subprocess.run(
                ["claude", "-p", "--model", model, "--output-format", "text"],
                input=prompt, capture_output=True, text=True,
                timeout=CLAUDE_TIMEOUT_S, encoding="utf-8", env=env,
            )
            if r.returncode == 0:
                return r.stdout.strip()
            last = (r.stderr or "")[:1000]
            transient = any(h in last.lower() for h in TRANSIENT_HINTS)
        except subprocess.TimeoutExpired:
            last = f"timeout after {CLAUDE_TIMEOUT_S}s"
            transient = True
        if attempt < retries and transient:
            time.sleep(delay)
            delay = min(delay * 2, 90.0)
            continue
        break
    raise RuntimeError(f"claude failed after {retries + 1} attempts: {last}")


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
    ap.add_argument("--jobs", type=int, default=4,
                    help="parallel claude workers (default 4; keep modest to avoid rate limits)")
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

    jobs = max(1, args.jobs)
    print(f"{len(txts)} documents -> classify via claude ({args.model}, {jobs} parallel)")

    results: list[dict | None] = [None] * len(txts)
    lock = threading.Lock()
    progress = {"done": 0}

    def classify_one(idx: int, txt: Path) -> tuple[int, dict]:
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
        with lock:
            progress["done"] += 1
            print(f"   {progress['done']}/{len(txts)} {txt.stem}: "
                  f"{obj.get('dokumenttyp', '?')} [{obj.get('konfidenz', '?')}] "
                  f"{time.time() - t0:.1f}s")
        return idx, obj

    with ThreadPoolExecutor(max_workers=jobs) as ex:
        futs = [ex.submit(classify_one, i, txt) for i, txt in enumerate(txts)]
        for fut in as_completed(futs):
            idx, obj = fut.result()
            results[idx] = obj

    results = [r for r in results if r is not None]

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
