#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11,<3.13"
# dependencies = [
#   "pyannote.audio>=3.3",
#   "torch>=2.2",
#   "torchaudio>=2.2",
#   "huggingface-hub>=0.24",
# ]
# ///
"""
Speaker-Diarisierung mit pyannote community-1 (2026 SOTA Open-Source).

Eingang:  <stem>.wav (16 kHz mono empfohlen, pyannote resampled wenn noetig)
Ausgang:  <stem>_diar.json (Segments mit speakerId/startTimeSeconds/endTimeSeconds)
          Format absichtlich kompatibel mit historischem FluidAudio-Output,
          damit merge.py unveraendert konsumieren kann.

Nutzung:
    diarize_pyannote.py <audio.wav>

Optional:
    TRANSKRIBIERE_NUM_SPEAKERS=N (env)
    TRANSKRIBIERE_MIN_SPEAKERS=N TRANSKRIBIERE_MAX_SPEAKERS=M (env, alternative)

Setup einmalig:
    1. License akzeptieren auf
       https://huggingface.co/pyannote/segmentation-3.0
       https://huggingface.co/pyannote/speaker-diarization-community-1
    2. Token in ~/.cache/huggingface/token speichern
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import torch
import torchaudio
from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook


MODEL = "pyannote/speaker-diarization-community-1"
TOKEN_FILE = Path.home() / ".cache" / "huggingface" / "token"


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: diarize_pyannote.py <audio.wav>", file=sys.stderr)
        return 1

    audio = Path(sys.argv[1]).resolve()
    if not audio.exists():
        print(f"FEHLT: {audio}", file=sys.stderr)
        return 1
    if not TOKEN_FILE.exists():
        print(f"FEHLT: HF-Token in {TOKEN_FILE}", file=sys.stderr)
        return 1

    out = audio.with_name(audio.stem + "_diar.json")

    num_speakers = os.environ.get("TRANSKRIBIERE_NUM_SPEAKERS")
    min_speakers = os.environ.get("TRANSKRIBIERE_MIN_SPEAKERS")
    max_speakers = os.environ.get("TRANSKRIBIERE_MAX_SPEAKERS")

    token = TOKEN_FILE.read_text().strip()
    print(f"loading pipeline: {MODEL}", flush=True)
    pipeline = Pipeline.from_pretrained(MODEL, token=token)

    device = torch.device("mps") if torch.backends.mps.is_available() else torch.device("cpu")
    print(f"device: {device}", flush=True)
    pipeline.to(device)

    print(f"loading audio: {audio}", flush=True)
    waveform, sr = torchaudio.load(str(audio))
    print(f"  shape={tuple(waveform.shape)}, sr={sr}", flush=True)

    kwargs: dict = {}
    if num_speakers:
        kwargs["num_speakers"] = int(num_speakers)
        print(f"  num_speakers (forced): {num_speakers}", flush=True)
    else:
        if min_speakers:
            kwargs["min_speakers"] = int(min_speakers)
        if max_speakers:
            kwargs["max_speakers"] = int(max_speakers)
        if min_speakers or max_speakers:
            print(f"  speakers range: min={min_speakers} max={max_speakers}", flush=True)
        else:
            print("  speakers: auto (use TRANSKRIBIERE_NUM_SPEAKERS for better results)", flush=True)

    t0 = time.time()
    with ProgressHook() as hook:
        diarization = pipeline({"waveform": waveform, "sample_rate": sr}, hook=hook, **kwargs)
    print(f"diarization done in {time.time()-t0:.1f}s", flush=True)

    # community-1 liefert DiarizeOutput; exclusive_speaker_diarization hat saubere Timestamps
    ann = getattr(diarization, "exclusive_speaker_diarization", None) or diarization.speaker_diarization

    segments = []
    for turn, _, speaker in ann.itertracks(yield_label=True):
        segments.append({
            "speakerId": str(speaker),
            "startTimeSeconds": float(turn.start),
            "endTimeSeconds": float(turn.end),
        })

    out.write_text(json.dumps({"segments": segments}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {len(segments)} segments -> {out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
