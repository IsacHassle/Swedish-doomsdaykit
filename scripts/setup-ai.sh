#!/bin/bash
# Sets up the local AI (nothing leaves the Mac):
#   1. Ollama: downloads Gemma 4 26B, Gemma 4 E4B and bge-m3, and builds the "crisis" and
#      "crisis-small" models with the crisis instructions in config/AI-PROMPT.txt
#   2. AnythingLLM: uses Ollama, and gets a "Crisis" workspace that answers from the books
#   3. Loads every document in documents/ into that workspace (scripts/embed-documents.sh)
# Safe to re-run: finished steps are skipped.
set -eu
KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROMPT="$KIT/config/AI-PROMPT.txt"
A=http://localhost:3001/api
OLLAMA=$(command -v ollama || echo /Applications/Ollama.app/Contents/Resources/ollama)

wait_for() {   # url, seconds, what
  for _ in $(seq 1 "$2"); do curl -fs -o /dev/null "$1" && return 0; sleep 1; done
  echo "$3 did not start. Open it once by hand, then run this again."; exit 1
}

# 1. Ollama and the models.
open -g -a Ollama
wait_for http://127.0.0.1:11434/api/version 60 "Ollama"
for m in gemma4:26b gemma4:e4b bge-m3; do
  "$OLLAMA" show "$m" >/dev/null 2>&1 || { echo "Downloading AI model $m"; "$OLLAMA" pull "$m"; }
done
tmp=$(mktemp -d)
for pair in crisis:gemma4:26b crisis-small:gemma4:e4b; do
  name=${pair%%:*}; base=${pair#*:}
  printf 'FROM %s\nSYSTEM """\n%s\n"""\nPARAMETER temperature 0.3\n' "$base" "$(cat "$PROMPT")" > "$tmp/Modelfile"
  "$OLLAMA" create "$name" -f "$tmp/Modelfile" >/dev/null && echo "Model $name ready"
done
rm -rf "$tmp"

# 2. AnythingLLM.
open -g -a AnythingLLM
wait_for "$A/ping" 180 "AnythingLLM"
post() { curl -fsS -X POST "$A$1" -H 'Content-Type: application/json' -d "$2" >/dev/null; }
post /system/update-env '{"LLMProvider":"ollama","OllamaLLMBasePath":"http://127.0.0.1:11434","OllamaLLMModelPref":"gemma4:26b","OllamaLLMTokenLimit":"16384","DisableTelemetry":"true"}'
post /system/update-env '{"EmbeddingEngine":"ollama","EmbeddingBasePath":"http://127.0.0.1:11434","EmbeddingModelPref":"bge-m3:latest","EmbeddingModelMaxChunkLength":"8192","OllamaEmbeddingBatchSize":"32","TextSplitterChunkSize":"1200","TextSplitterChunkOverlap":"120"}'
if ! curl -fs "$A/workspace/crisis" | grep -q '"slug":"crisis"'; then
  post /workspace/new '{"name":"Crisis"}'
fi
python3 - "$A" "$PROMPT" <<'PY'
import json, sys, urllib.request
api, prompt = sys.argv[1], open(sys.argv[2]).read()
body = {"chatProvider": "ollama", "chatModel": "gemma4:26b", "topN": 6, "similarityThreshold": 0.25, "openAiPrompt": prompt}
req = urllib.request.Request(api + "/workspace/crisis/update", data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
urllib.request.urlopen(req, timeout=30)
print("AnythingLLM workspace Crisis ready")
PY

# 3. The books.
echo "Loading the documents into the AI (about 40 minutes the first time; progress: logs/embed.log)"
bash "$KIT/scripts/embed-documents.sh"
grep -E "embedded|to embed" "$KIT/logs/embed.log" | tail -1
echo "AI ready."
