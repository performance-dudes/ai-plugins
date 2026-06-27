#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Chunk a merged transcript into context-sized windows for the strict
clean-transcript pass.

Input is the ``<stem>_merged_raw.json`` produced by ``merge.py`` — a JSON list
of blocks ``{"start": <seconds>, "speaker": "SPEAKER_00", "text": "..."}``.
For each chunk this writes one ``chunk_NN.txt`` (the formatted raw transcript)
plus a ``manifest.json`` carrying the anchors every strict prompt needs:
turn count, first/last timestamp+speaker, and the 85 % output-length floor.

Deterministic, stdlib only, no network — so it is unit-testable without audio.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def fmt_ts(seconds: float) -> str:
    secs = int(seconds)
    h, m = divmod(secs, 3600)
    m, s = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def parse_map(pairs: list[str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for pair in pairs or []:
        if "=" in pair:
            key, value = pair.split("=", 1)
            mapping[key.strip()] = value.strip()
    return mapping


def chunk_blocks(blocks: list[dict], max_chars: int) -> list[list[dict]]:
    """Greedy char-budget chunking that never splits a single block."""
    chunks: list[list[dict]] = []
    current: list[dict] = []
    current_chars = 0
    for block in blocks:
        size = len(block.get("text", ""))
        if current and current_chars + size > max_chars:
            chunks.append(current)
            current, current_chars = [], 0
        current.append(block)
        current_chars += size
    if current:
        chunks.append(current)
    return chunks


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("merged_raw", type=Path, help="<stem>_merged_raw.json from merge.py")
    ap.add_argument("--map", nargs="*", default=[], metavar="SPEAKER_00=Name",
                    help="speaker-id to real-name mapping (optional)")
    ap.add_argument("--out", type=Path, default=None,
                    help="output dir for the chunks/ folder (default: next to merged_raw)")
    ap.add_argument("--max-chars", type=int, default=60000,
                    help="max transcript chars per chunk (default 60000, ~one strict pass)")
    args = ap.parse_args()

    if not args.merged_raw.exists():
        print(f"missing: {args.merged_raw}", file=sys.stderr)
        return 1

    blocks = json.loads(args.merged_raw.read_text(encoding="utf-8"))
    if not isinstance(blocks, list) or not blocks:
        print("merged_raw.json is empty or not a list of blocks", file=sys.stderr)
        return 1

    mapping = parse_map(args.map)
    for block in blocks:
        block["speaker"] = mapping.get(block["speaker"], block["speaker"])

    out_dir = (args.out or args.merged_raw.parent) / "chunks"
    out_dir.mkdir(parents=True, exist_ok=True)

    chunks = chunk_blocks(blocks, args.max_chars)
    manifest: list[dict] = []
    for i, chunk in enumerate(chunks):
        lines = [f"[{fmt_ts(b['start'])}] {b['speaker']}: {b['text']}" for b in chunk]
        chunk_file = out_dir / f"chunk_{i:02d}.txt"
        chunk_file.write_text("\n\n".join(lines) + "\n", encoding="utf-8")
        input_chars = sum(len(b.get("text", "")) for b in chunk)
        manifest.append({
            "index": i,
            "file": str(chunk_file),
            "turn_count": len(chunk),
            "first_ts": fmt_ts(chunk[0]["start"]),
            "first_speaker": chunk[0]["speaker"],
            "last_ts": fmt_ts(chunk[-1]["start"]),
            "last_speaker": chunk[-1]["speaker"],
            "input_chars": input_chars,
            "min_output_chars": int(input_chars * 0.85),
        })

    manifest_file = out_dir / "manifest.json"
    manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    # Single-line JSON summary on stdout so an orchestrator can parse it directly.
    print(json.dumps({
        "chunks": len(chunks),
        "manifest": str(manifest_file),
        "total_turns": len(blocks),
        "speakers": sorted({b["speaker"] for b in blocks}),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
