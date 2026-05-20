#!/usr/bin/env bash
# Copieer ruwe SV-input-JSONs (per boek-map) naar input.sv/.
# Reeds bestaande boek-mapjes in input.sv worden overgeslagen.
set -euo pipefail

SRC="/Users/wmotte/Desktop/projects/sv_xml2json/out.07.with.greek.text"
DST="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/input.sv"

mkdir -p "$DST"

for book_dir in "$SRC"/*/; do
    book="$(basename "$book_dir")"
    if [[ -e "$DST/$book" ]]; then
        echo "skip (bestaat al): $book"
        continue
    fi
    cp -R "$book_dir" "$DST/$book"
    echo "gekopieerd: $book"
done
