#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Mechanischer Merge: yap-Transkript + FluidAudio-Diarisierung → Sprecher-attributiertes Transkript.

Reine Overlap-Berechnung, kein LLM. Deterministisch, byte-reproduzierbar.

Eingang:
    <stem>_yap.json   yap JSON (segments mit start/end/text + word-level words)
    <stem>_diar.json  FluidAudio ProcessingResult JSON (segments mit speakerId/startTimeSeconds/endTimeSeconds)

Ausgang:
    <stem>_merged.txt          flacher Block-Merge mit [MM:SS] Speaker: text
    <stem>_merged_raw.json     strukturierter Merge (für analyse.py)

Aufruf:
    uv run merge.py /pfad/<stem>
    uv run merge.py /pfad/<stem> --map SPEAKER_00=Alice SPEAKER_01=Bob
    uv run merge.py /pfad/<stem> --no-filter-hallucinations
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path


# Erweiterbare Halluzinations-Patterns. yap (Apple SpeechAnalyzer) halluziniert
# weniger als Whisper, aber bei Stille/Klick-Geräuschen tauchen ähnliche Floskeln auf.
HALLUCINATION_PATTERNS = [
    # Apple SpeechAnalyzer / yap fallback Halluzinationen
    "untertitelung des zdf",
    "untertitel im auftrag",
    "vielen dank fürs zuschauen",
    "swr 2020",
    "untertitel von stephanie geiges",
    # Whisper-spezifische End-of-Audio-Halluzinationen
    "thanks for watching",
    "thank you for watching",
    "please subscribe",
    "so, bye. so, bye",
    "bye. so, bye. so, bye",
    "tschuess. tschuess. tschuess",
    "♪",
    "[music]",
    "[musik]",
]


@dataclass
class YapSegment:
    start: float
    end: float
    text: str


@dataclass
class DiarSegment:
    start: float
    end: float
    speaker: str


@dataclass
class MergedBlock:
    start: float
    end: float
    speaker: str
    text: str


def load_yap(path: Path) -> list[YapSegment]:
    data = json.loads(path.read_text(encoding="utf-8"))
    out: list[YapSegment] = []
    for s in data.get("segments", []):
        text = (s.get("text") or "").strip()
        if not text:
            continue
        out.append(YapSegment(start=float(s["start"]), end=float(s["end"]), text=text))
    return out


def load_diarization(path: Path) -> list[DiarSegment]:
    data = json.loads(path.read_text(encoding="utf-8"))
    out: list[DiarSegment] = []
    for s in data.get("segments", []):
        out.append(
            DiarSegment(
                start=float(s["startTimeSeconds"]),
                end=float(s["endTimeSeconds"]),
                speaker=str(s["speakerId"]),
            )
        )
    return sorted(out, key=lambda x: x.start)


def assign_speaker(seg: YapSegment, diar: list[DiarSegment]) -> str:
    """Sprecher mit der größten zeitlichen Überlappung gewinnt.

    Fallback bei null Overlap (kurze Einwürfe, Boundary-Effekte):
    nimm den Sprecher des nächstgelegenen Diar-Segments (kleinste Gap).
    """
    overlap: dict[str, float] = {}
    for d in diar:
        o_start = max(seg.start, d.start)
        o_end = min(seg.end, d.end)
        if o_end > o_start:
            overlap[d.speaker] = overlap.get(d.speaker, 0.0) + (o_end - o_start)
    if overlap:
        return max(overlap, key=overlap.get)

    # Kein Overlap → Nearest-Neighbor nach zeitlichem Abstand zum yap-Mittelpunkt.
    if not diar:
        return "UNKNOWN"
    mid = (seg.start + seg.end) / 2.0
    nearest = min(diar, key=lambda d: min(abs(mid - d.start), abs(mid - d.end)))
    return nearest.speaker


def is_hallucinated(text: str) -> bool:
    low = text.lower()
    return any(p in low for p in HALLUCINATION_PATTERNS)


def merge_blocks(segments: list[YapSegment], diar: list[DiarSegment]) -> list[MergedBlock]:
    """yap-Segmente nach Sprecher-Wechsel zu Blöcken zusammenfassen."""
    blocks: list[MergedBlock] = []
    current: MergedBlock | None = None
    for seg in segments:
        spk = assign_speaker(seg, diar)
        if current is None or current.speaker != spk:
            if current is not None:
                blocks.append(current)
            current = MergedBlock(start=seg.start, end=seg.end, speaker=spk, text=seg.text)
        else:
            current.end = seg.end
            sep = "" if current.text.endswith(("-", "—")) else " "
            current.text = current.text + sep + seg.text
    if current is not None:
        blocks.append(current)
    return blocks


def fmt_ts(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def parse_map(items: list[str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for it in items:
        if "=" not in it:
            print(f"⚠️  Ungültiges --map item (erwartet K=V): {it!r}", file=sys.stderr)
            continue
        k, v = it.split("=", 1)
        mapping[k.strip()] = v.strip()
    return mapping


def normalise_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def main() -> int:
    ap = argparse.ArgumentParser(description="Mechanischer Merge yap + FluidAudio.")
    ap.add_argument("stem", type=Path, help="Pfad-Stem (ohne Suffix). Bsp: /tmp/test2")
    ap.add_argument(
        "--map",
        nargs="*",
        default=[],
        metavar="ID=Name",
        help="Sprecher-Mapping. Bsp: --map SPEAKER_00=Alice SPEAKER_01=Bob",
    )
    ap.add_argument(
        "--no-filter-hallucinations",
        action="store_true",
        help="Halluzinations-Filter deaktivieren.",
    )
    args = ap.parse_args()

    stem: Path = args.stem
    yap_path = stem.with_name(stem.name + "_yap.json")
    diar_path = stem.with_name(stem.name + "_diar.json")
    out_txt = stem.with_name(stem.name + "_merged.txt")
    out_json = stem.with_name(stem.name + "_merged_raw.json")

    if not yap_path.exists():
        print(f"❌ Fehlt: {yap_path}", file=sys.stderr)
        return 1
    if not diar_path.exists():
        print(f"❌ Fehlt: {diar_path}", file=sys.stderr)
        return 1

    yap_segs = load_yap(yap_path)
    diar = load_diarization(diar_path)
    speaker_map = parse_map(args.map)

    blocks = merge_blocks(yap_segs, diar)

    # Halluzinations-Filter
    if not args.no_filter_hallucinations:
        filtered: list[MergedBlock] = []
        dropped = 0
        for b in blocks:
            if is_hallucinated(b.text):
                dropped += 1
                continue
            filtered.append(b)
        if dropped:
            print(f"🧹 {dropped} halluzinierte Blöcke gefiltert", file=sys.stderr)
        blocks = filtered

    # Speaker-Mapping anwenden
    for b in blocks:
        b.speaker = speaker_map.get(b.speaker, b.speaker)
        b.text = normalise_whitespace(b.text)

    # Plain text output
    lines = []
    for b in blocks:
        lines.append(f"[{fmt_ts(b.start)}] {b.speaker}: {b.text}")
    out_txt.write_text("\n\n".join(lines) + "\n", encoding="utf-8")

    # JSON output (für analyse.py)
    out_json.write_text(
        json.dumps([asdict(b) for b in blocks], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Stats
    speakers = sorted({b.speaker for b in blocks})
    total_speech = sum(b.end - b.start for b in blocks)
    print(f"✅ {len(blocks)} Blöcke, {len(speakers)} Sprecher: {', '.join(speakers)}")
    print(f"   Gesamt-Sprechzeit: {total_speech:.1f}s")
    print(f"   {out_txt}")
    print(f"   {out_json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
