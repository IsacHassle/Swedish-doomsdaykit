#!/bin/bash
# Starts the crisis kit: the offline library, the start page, the map, the
# documents and the AI page, shared with every phone and laptop on the same Wi-Fi.
# No internet needed. This is what "Start Crisis Kit.command" runs.
#
# Run:  bash scripts/share-library.sh
# Stop: Ctrl+C (stops everything)
#
# The first time, macOS may ask whether kiwix-serve and Python may accept
# incoming connections. Click Allow, or other devices cannot connect.

KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"   # the kit folder (where this repo is)
LIB="$KIT/library"
SERVE="$KIT/tools/kiwix-tools/kiwix-serve"
LIB_PORT=8090
WEB_PORT=8091

shopt -s nullglob
zims=("$LIB"/*.zim)
if [ ${#zims[@]} -eq 0 ]; then
  echo "No library files found in $LIB yet. Run download-library.sh first."
  exit 1
fi

# Stop any copy that is already running, so ports are free.
pkill -f "kiwix-serve --port=$LIB_PORT" 2>/dev/null
pkill -f "serve-web.py $WEB_PORT" 2>/dev/null
sleep 1

"$SERVE" --port="$LIB_PORT" "${zims[@]}" >/dev/null 2>&1 &
LIB_PID=$!
python3 "$KIT/scripts/serve-web.py" "$WEB_PORT" >/dev/null 2>&1 &
WEB_PID=$!
trap 'kill $LIB_PID $WEB_PID 2>/dev/null; echo; echo "  Stopped."' EXIT

for i in $(seq 1 30); do curl -sf -o /dev/null "http://localhost:$LIB_PORT/catalog/v2/entries" && break; sleep 1; done
python3 "$KIT/scripts/build-home.py" >/dev/null

IP=$(ipconfig getifaddr en0 || ipconfig getifaddr en1)
echo ""
echo "  KRISLÅDA / CRISIS KIT is running (${#zims[@]} libraries)."
echo ""
echo "  On this Mac:            http://localhost:$WEB_PORT"
[ -n "$IP" ] && echo "  On phones (same Wi-Fi): http://$IP:$WEB_PORT"
echo ""
echo "  Ask the AI:              http://localhost:$WEB_PORT/ai/"
[ -n "$IP" ] && echo "  Ask the AI from a phone: http://$IP:$WEB_PORT/ai/"
echo ""
echo "  Keep this window open. Press Ctrl+C to stop."
echo ""
[ "${1:-}" = "--open" ] && open "http://localhost:$WEB_PORT"
wait $LIB_PID
