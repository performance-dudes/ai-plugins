#!/usr/bin/env bash
# Preflight for the ocr plugin. Prints one line per dependency.
# Never installs anything — it only reports. Always exits 0 so the calling
# command can render the full checklist.
set -uo pipefail

ok()   { printf '  OK    %s\n' "$1"; }
miss() { printf '  MISS  %s — %s\n' "$1" "$2"; }

echo "ocr-doctor — dependency check"

if command -v auge >/dev/null 2>&1; then
  ok "auge ($(auge --release 2>/dev/null | head -1 | tr -d '\n' | cut -c1-40))"
else
  miss "auge" "brew tap Arthur-Ficial/tap && brew install auge"
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
  miss "claude CLI" "install Claude Code — needed for the classification step"
fi

# PDF text-layer embedding uses auge + PyMuPDF (pymupdf), pulled by uv on first
# use via the scripts' PEP-723 headers — no extra system tool to install.

prod="$(sw_vers -productVersion 2>/dev/null || echo 0)"
major_os="${prod%%.*}"
if [ "${major_os:-0}" -ge 26 ] 2>/dev/null; then
  ok "macOS $prod (Apple Vision / auge baseline)"
else
  miss "macOS >=26 (Tahoe)" "auge needs macOS 26; this is $prod"
fi

case "$(uname -m)" in
  arm64) ok "Apple Silicon" ;;
  *)     miss "Apple Silicon" "auge / Apple Vision needs an arm64 Mac; this is $(uname -m)" ;;
esac

echo "done."
exit 0
