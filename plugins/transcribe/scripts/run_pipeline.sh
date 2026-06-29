#!/usr/bin/env bash
# Transkribiere — Phasen 1–3 für ein einzelnes Audio-File (Quality-First).
#
# Eingang: beliebiges Audio/Video (m4a, mp3, mkv, wav, ...).
# Ausgang im selben Ordner:
#   <base>.wav                    16 kHz mono PCM
#   <base>_whisper_turbo.json     mlx-whisper Large-v3-Turbo Volltext
#   <base>_yap.json               Symlink auf _whisper_turbo.json (Eingang für merge.py)
#   <base>_diar.json              pyannote-community-1 Speaker-Segmente
#
# Nutzung:
#   ./run_pipeline.sh "/pfad/zur/aufnahme.m4a" [num-speakers]
#
# Wenn num-speakers nicht angegeben: pyannote bestimmt selbst (kann ungenau sein).
# Wenn bekannt: immer angeben.

set -euo pipefail

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <audio-file> [num-speakers]" >&2
    echo "  num-speakers: bekannte Anzahl Personen im Gespraech (empfohlen)" >&2
    exit 1
fi

INPUT="$1"
NUM_SPEAKERS="${2:-}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ ! -f "$INPUT" ]]; then
    echo "❌ Datei nicht gefunden: $INPUT" >&2
    exit 1
fi
if [[ ! -f ~/.cache/huggingface/token ]]; then
    echo "❌ HuggingFace-Token fehlt unter ~/.cache/huggingface/token" >&2
    echo "   Setup-Anleitung: siehe CLAUDE.md Abschnitt 'HuggingFace-Token'" >&2
    exit 1
fi

DIR="$(cd "$(dirname "$INPUT")" && pwd)"
BASE="$(basename "$INPUT")"
STEM="${BASE%.*}"
WAV="$DIR/${STEM}.wav"
WHISPER_JSON="$DIR/${STEM}_whisper_turbo.json"
YAP_JSON_LINK="$DIR/${STEM}_yap.json"
DIAR_JSON="$DIR/${STEM}_diar.json"

echo "🎯 Pipeline fuer: $INPUT"
[[ -n "$NUM_SPEAKERS" ]] && echo "   Sprecher: $NUM_SPEAKERS" || echo "   Sprecher: auto"
echo

# Phase 1 — Audio → WAV 16 kHz mono
if [[ ! -f "$WAV" || "$WAV" -ot "$INPUT" ]]; then
    echo "🎞️  Phase 1: ffmpeg → 16 kHz mono PCM"
    ffmpeg -y -loglevel error -i "$INPUT" -ar 16000 -ac 1 -c:a pcm_s16le "$WAV"
else
    echo "🎞️  Phase 1: WAV bereits da, ueberspringe"
fi

# Phase 2 — Whisper Large-v3-Turbo Transkription (mlx-whisper, Apple MLX nativ)
if [[ ! -f "$WHISPER_JSON" || "$WHISPER_JSON" -ot "$WAV" ]]; then
    echo "🧠 Phase 2: mlx-whisper Large-v3-Turbo"
    "$SCRIPT_DIR/transcribe_whisper_mlx.py" "$WAV" --turbo
else
    echo "🧠 Phase 2: Transkript bereits da, ueberspringe"
fi

# merge.py erwartet historisch <stem>_yap.json — auf Whisper-Output verlinken
ln -sf "$(basename "$WHISPER_JSON")" "$YAP_JSON_LINK"

# Phase 3 — pyannote community-1 Diarisierung
if [[ ! -f "$DIAR_JSON" || "$DIAR_JSON" -ot "$WAV" ]]; then
    echo "🔊 Phase 3: pyannote community-1 (MPS, on-device)"
    if [[ -n "$NUM_SPEAKERS" ]]; then
        TRANSKRIBIERE_NUM_SPEAKERS="$NUM_SPEAKERS" "$SCRIPT_DIR/diarize_pyannote.py" "$WAV"
    else
        "$SCRIPT_DIR/diarize_pyannote.py" "$WAV"
    fi
else
    echo "🔊 Phase 3: Diarisierung bereits da, ueberspringe"
fi

echo
echo "✅ Fertig. Outputs:"
echo "   $WAV"
echo "   $WHISPER_JSON   (Whisper Volltext)"
echo "   $YAP_JSON_LINK  (Symlink fuer merge.py)"
echo "   $DIAR_JSON       (pyannote Speaker-Segmente)"
echo
echo "Weiter mit:"
echo "   uv run merge.py \"$DIR/$STEM\""
echo "   (Erst _merged.txt pruefen, dann --map SPEAKER_00=Name ... ergaenzen)"
