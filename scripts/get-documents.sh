#!/bin/bash
# Gets the documents the AI reads and people open as PDFs (into documents/):
#   the Swedish government brochure "Om krisen eller kriget kommer" (MCF), in Swedish and English,
#   and the books inside the offline libraries (scripts/extract-documents.py).
# Run after the libraries are downloaded. Safe to re-run.
set -eu
KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
D="$KIT/documents"
mkdir -p "$D"

get() {   # url, file name
  [ -s "$D/$2" ] && return 0
  echo "Hämtar $2"
  curl -fsSL -o "$D/$2.part" "$1" && mv "$D/$2.part" "$D/$2"
}
get "https://rib.msb.se/filer/pdf/30828.pdf" "Om-krisen-eller-kriget-kommer.pdf"
get "https://rib.msb.se/filer/pdf/31523.pdf" "In-case-of-crisis-or-war.pdf"

# The kit's own guide, so the AI can explain how to use the kit.
cp "$KIT/README.md" "$D/Krislåda - guide.md"

"$KIT/tools/venv/bin/python" "$KIT/scripts/extract-documents.py"
echo "Dokumenten är klara."
