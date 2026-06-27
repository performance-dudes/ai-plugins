#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = [
#   "mlx-whisper>=0.4",
# ]
# ///
"""
Transkription mit mlx-whisper (Apple MLX nativ) - Whisper Large-v3 / Turbo.

Eingang:  <stem>.wav (oder beliebiges Audio)
Ausgang:  <stem>_whisper_large_v3.json  (default)
          <stem>_whisper_turbo.json     (mit --turbo)

Format ist segments[].{start, end, text, ...} - kompatibel mit merge.py.

Nutzung:
    transcribe_whisper_mlx.py <audio.wav>           # Large-v3 (genauer, langsamer)
    transcribe_whisper_mlx.py <audio.wav> --turbo   # Large-v3-Turbo (~2x schneller, vergleichbare Quality)

Quality-Hinweise:
- Kein initial_prompt: in Tests bringt er mehr Halluzination als Nutzen.
  Spezial-Begriffe (Eigennamen, Codenames, Fachbegriffe) werden besser im
  claude-clean_transcript-Schritt mit dem CONTEXT-Block korrigiert.
- condition_on_previous_text=True: bessere Konsistenz ueber Chunks hinweg.
- word_timestamps=True: noetig fuer fein-granularen Merge mit Diarisierung.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import mlx_whisper


REPO_LARGE = "mlx-community/whisper-large-v3-mlx"
REPO_TURBO = "mlx-community/whisper-large-v3-turbo"


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: transcribe_whisper_mlx.py <audio.wav> [--turbo]", file=sys.stderr)
        return 1

    audio = Path(sys.argv[1]).resolve()
    if not audio.exists():
        print(f"FEHLT: {audio}", file=sys.stderr)
        return 1

    use_turbo = "--turbo" in sys.argv
    repo = REPO_TURBO if use_turbo else REPO_LARGE
    suffix = "_whisper_turbo.json" if use_turbo else "_whisper_large_v3.json"
    out = audio.with_name(audio.stem + suffix)

    print(f"model: {repo}", flush=True)
    print(f"audio: {audio}", flush=True)
    t0 = time.time()
    result = mlx_whisper.transcribe(
        str(audio),
        path_or_hf_repo=repo,
        word_timestamps=True,
        verbose=False,
        condition_on_previous_text=True,
        no_speech_threshold=0.6,
    )
    dt = time.time() - t0
    print(f"done in {dt:.1f}s  ({len(result.get('segments', []))} segments)", flush=True)

    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
