#!/usr/bin/env bash
# Scrape de HSV voor alle 27 NT-boeken via scripts/fetch_hsv.py.
#
# Gebruik:
#   scripts/fetch_hsv_nt.sh                 # alle NT-boeken
#   scripts/fetch_hsv_nt.sh MAT MRK LUK     # alleen genoemde boeken
#   SLEEP=2 scripts/fetch_hsv_nt.sh         # tragere requests
#
# Per boek wordt fetch_hsv.py zonder hoofdstuk-argument aangeroepen, zodat het
# script zelf alle hoofdstukken van het boek ophaalt (BOOK_CHAPTER_COUNT).
set -euo pipefail

cd "$(dirname "$0")/.."

PY="${PYTHON:-python3}"
SLEEP="${SLEEP:-1.0}"

# OSIS-codes in canonieke NT-volgorde.
NT_BOOKS=(
  MAT MRK LUK JHN ACT
  ROM 1CO 2CO GAL EPH PHP COL
  1TH 2TH 1TI 2TI TIT PHM
  HEB JAS 1PE 2PE 1JN 2JN 3JN JUD REV
)

books=("$@")
[ ${#books[@]} -eq 0 ] && books=("${NT_BOOKS[@]}")

failed=()
for book in "${books[@]}"; do
  echo "=== $book ==="
  if "$PY" scripts/fetch_hsv.py "$book" --sleep "$SLEEP"; then
    :
  else
    echo "!! mislukt: $book" >&2
    failed+=("$book")
  fi
done

if [ ${#failed[@]} -gt 0 ]; then
  echo "" >&2
  echo "Mislukte boeken: ${failed[*]}" >&2
  exit 1
fi
echo "Klaar — alle boeken gescraped."
