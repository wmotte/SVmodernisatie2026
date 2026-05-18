#!/usr/bin/env bash
# Rebuild parallel-bible PDFs for LUK and MRK.
# Updates build/<BOOK>.pdf and <BOOK>_voorbeeld.pdf at repo level.
set -euo pipefail

cd "$(dirname "$0")"

BOOKS=(LUK MRK PHM)

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
