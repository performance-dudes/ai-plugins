#!/usr/bin/env bash
# Preflight for the transcribe plugin. Prints one line per dependency.
# Never installs anything — it only reports. Always exits 0 so the calling
# command can render the full checklist.
set -uo pipefail

ok()   { printf '  OK    %s\n' "$1"; }
miss() { printf '  MISS  %s — %s\n' "$1" "$2"; }

echo "transcribe-doctor — dependency check"

if command -v ffmpeg >/dev/null 2>&1; then
  ok "ffmpeg ($(ffmpeg -version 2>/dev/null | head -1 | awk '{print $3}'))"
else
  miss "ffmpeg" "brew install ffmpeg"
fi

if command -v uv >/dev/null 2>&1; then
  ok "uv ($(uv --version 2>/dev/null | awk '{print $2}'))"
else
  miss "uv" "brew install uv"
fi

if command -v node >/dev/null 2>&1; then
  major="$(node -p 'process.versions.node.split(".")[0]' 2>/dev/null || echo 0)"
  if [ "${major:-0}" -ge 20 ] 2>/dev/null; then
    ok "node ($(node -v))"
  else
    miss "node" "need >=20, have $(node -v) — brew install node"
  fi
else
  miss "node" "brew install node (the Workflow tool needs >=20; Bash fallback works without)"
fi

if command -v claude >/dev/null 2>&1; then
  ok "claude CLI"
else
  miss "claude CLI" "install Claude Code — needed for the Opus deliverable step"
fi

if [ -f "$HOME/.cache/huggingface/token" ]; then
  ok "HuggingFace token (~/.cache/huggingface/token)"
else
  miss "HuggingFace token" "pyannote needs it — see https://github.com/performance-dudes/ai-plugins/blob/main/docs/transcribe/SETUP.md"
fi

case "$(uname -m)" in
  arm64) ok "Apple Silicon (mlx-whisper supported)" ;;
  *)     miss "Apple Silicon" "mlx-whisper needs an arm64 Mac; this is $(uname -m)" ;;
esac

echo "done."
exit 0
