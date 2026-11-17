#!/bin/bash
# Swedish-doomsdaykit installer.
#
#   ./install.sh           everything (about 45 GB, a few hours)
#   ./install.sh --no-ai   without the AI (about 15 GB)
#
# Needs a Mac with Apple Silicon and an internet connection while installing.
# After that, everything works with no internet. Re-run any time: it carries on
# where it stopped and skips what is already done.
set -eu
KIT="$(cd "$(dirname "$0")" && pwd)"
cd "$KIT"
AI=1
[ "${1:-}" = "--no-ai" ] && AI=0
step() { printf '\n\033[1m==> %s\033[0m\n' "$*"; }

if [ "$(uname -s)" != Darwin ] || [ "$(uname -m)" != arm64 ]; then
  echo "This kit needs a Mac with Apple Silicon (M1 or newer)."; exit 1
fi
free_gb=$(df -g "$KIT" | awk 'NR==2 {print $4}')
need=$([ $AI = 1 ] && echo 50 || echo 22)
if [ ! -f "$KIT/maps/sweden.pmtiles" ] && [ "$free_gb" -lt "$need" ]; then
  echo "Only $free_gb GB free here; the kit needs about $need GB. Free up space, then run this again."; exit 1
fi
chmod +x "$KIT"/scripts/*.sh "$KIT/Start Crisis Kit.command"

install_app() {   # name, dmg url
  [ -d "/Applications/$1.app" ] && return 0
  step "Installing $1"
  tmp=$(mktemp -d)
  curl -fL --progress-bar -o "$tmp/app.dmg" "$2"
  vol=$(hdiutil attach -nobrowse -readonly "$tmp/app.dmg" | awk -F'\t' '/\/Volumes\// {print $NF; exit}')
  cp -R "$vol/$1.app" /Applications/
  hdiutil detach -quiet "$vol"
  rm -rf "$tmp"
}

step "1/5 Tools"
bash scripts/get-tools.sh

step "2/5 Offline libraries (about 14 GB; progress also in logs/download.log)"
bash scripts/download-library.sh
if tail -n 60 logs/download.log | grep -q "^FAIL"; then
  echo "Some libraries failed to download. Run ./install.sh again to retry them."
fi

step "3/5 Maps of Sweden and the world (about 4.5 GB)"
bash scripts/get-maps.sh

step "4/5 Documents and books"
bash scripts/get-documents.sh

if [ $AI = 1 ]; then
  step "5/5 Local AI (about 27 GB of models, then the books are loaded into it)"
  install_app Ollama "https://ollama.com/download/Ollama.dmg"
  install_app AnythingLLM "https://cdn.anythingllm.com/latest/AnythingLLMDesktop-Silicon.dmg"
  bash scripts/setup-ai.sh
else
  step "5/5 Local AI skipped (--no-ai)"
fi

ln -sfn "$KIT" "$HOME/Desktop/Crisis Kit"
step "Done"
cat <<EOF
The kit is installed in $KIT (shortcut on the Desktop: "Crisis Kit").

  Start it:  double-click "Start Crisis Kit.command"
  Then open: http://localhost:8091  (phones on the same Wi-Fi: the address it prints)

Print "Krislåda - guide to print.pdf" and keep it with your emergency supplies.
Test it once a month with Wi-Fi turned off.
EOF
