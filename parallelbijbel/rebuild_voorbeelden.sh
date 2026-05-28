#!/usr/bin/env bash
# Rebuild parallel-bible PDFs for all books with output/.
# Updates build/<BOOK>.pdf and <BOOK>_voorbeeld.pdf at repo level.
set -euo pipefail

cd "$(dirname "$0")"

BOOKS=()
while IFS= read -r dir; do
  book="$(basename "${dir}")"
  if compgen -G "../output/${book}/${book}.*.json" > /dev/null; then
    BOOKS+=("${book}")
  fi
done < <(find ../output -mindepth 1 -maxdepth 1 -type d | sort)

for book in "${BOOKS[@]}"; do
  echo "=== Building ${book} ==="
  python3 build_book.py "${book}"
done

echo
echo "Done. Updated:"
for book in "${BOOKS[@]}"; do
  echo "  - build/${book}.pdf"
  echo "  - ${book}_voorbeeld.pdf"
done
