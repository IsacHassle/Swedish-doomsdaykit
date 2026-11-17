# Swedish-doomsdaykit: design

Date: 2026-11-17

## Goal

Publish the offline crisis kit built on one Mac as a public repository anyone in Sweden can
download and install, and make the owner's own kit the same version as everyone else's.

## Decisions

- **One version, about 45 GB.** Medicine libraries in full, survival and emergency guides,
  Swedish Wikipedia (opening sections), all of Sweden on the map at street level, map search for
  every town, street and address in Sweden, the books for the AI, and both AI models (Gemma 4 26B and
  E4B). English Wikipedia, repair guides and Q&A sites are optional extras in `config/libraries.txt`.
- **The repository holds only code.** `install.sh` downloads everything from the original sources
  (Kiwix, Protomaps, MSB/MCF, Ollama), checks each library against its published SHA-256, and is
  safe to re-run. Nothing third-party is redistributed except small, permissively licensed map
  assets and the map search files (OpenStreetMap, ODbL) attached to the GitHub release.
- **The repository folder is the kit.** Downloaded data lives in folders git ignores (whitelist
  `.gitignore`), so personal documents can never be committed. Scripts find the kit folder from
  their own location; nothing assumes `~/Crisis`.
- **Mac with Apple Silicon only**, like the original. `--no-ai` for smaller machines.
- **Privacy:** no personal paths, addresses or emails in the files; commits use the GitHub noreply address.

## Install steps (each its own script, each idempotent)

1. `get-tools.sh`: kiwix-serve, pmtiles, a Python venv with libzim.
2. `download-library.sh`: libraries from `config/libraries.txt`, checksum-verified, resumable.
3. `get-maps.sh`: world and Sweden PMTiles from the newest Protomaps daily build; map search from the release.
4. `get-documents.sh`: MCF brochures; `extract-documents.py` takes the books out of the libraries.
5. `setup-ai.sh`: Ollama models and the `crisis` / `crisis-small` models; AnythingLLM settings,
   the Crisis workspace, then `embed-documents.sh`.

## Testing

- Run the installer against the owner's existing kit: every step should skip.
- Run it in an empty folder with a small library list to exercise download, checksum and extraction.
- Start the kit from the repository and re-test the AI page and the map.
