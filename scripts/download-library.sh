#!/bin/bash
# Downloads the offline libraries listed in config/libraries.txt into library/.
# Safe to re-run at any time: finished files are skipped, partial ones resume,
# and every file is checked against Kiwix's published SHA-256 before it is kept.
#
# Run:   bash scripts/download-library.sh [list-file]
# Watch: tail -f logs/download.log

set -u
KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"   # the kit folder (where this repo is)
DIR="$KIT/library"
LIST="${1:-$KIT/config/libraries.txt}"
LOG="$KIT/logs/download.log"
mkdir -p "$DIR" "$(dirname "$LOG")"

fetch() {
  url="$1"
  name=$(basename "$url")
  f="$DIR/$name"
  if [ -f "$f" ]; then echo "SKIP $name (already downloaded)"; return 0; fi

  want=$(curl -sSL --fail "$url.sha256" 2>/dev/null | awk '{print $1}')

  if [ -f "$f.part" ] && [ -n "$want" ] && [ "$(shasum -a 256 "$f.part" | awk '{print $1}')" = "$want" ]; then
    mv "$f.part" "$f"; echo "OK   $name"; return 0
  fi

  echo "GET  $name"
  for attempt in 1 2 3 4 5; do
    curl -sSL --fail -C - --retry 5 --retry-delay 15 -o "$f.part" "$url" && break
    echo "RETRY $name (attempt $attempt)"; sleep 30
  done

  got=$(shasum -a 256 "$f.part" 2>/dev/null | awk '{print $1}')
  if [ -n "$want" ] && [ "$got" = "$want" ]; then
    mv "$f.part" "$f"; echo "OK   $name"
  else
    rm -f "$f.part"; echo "FAIL $name (checksum mismatch or download error, re-run to retry)"
  fi
}
export -f fetch
export DIR

echo "=== START $(date)" >> "$LOG"
sed 's/#.*//' "$LIST" | awk '{print $1}' | grep . | xargs -P 3 -I{} bash -c 'fetch "$1"' _ {} 2>&1 | tee -a "$LOG"
echo "=== DONE $(date)" >> "$LOG"
