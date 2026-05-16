#!/usr/bin/env bash
# Synchroniseer gemoderniseerde JSONs naar de viewer-input-map en regenereer
# de SV2026-vs-SV2027 diff-bestanden.
#
# Gebruik:
#   bash docs/sync_outputs.sh
#
# Effect:
#   1. Spiegelt `output/<BOEK>/<BOEK>.<H>.json` naar
#      `docs/inputs/<BOEK>/<BOEK>.<H>.json` (viewer leest hieruit).
#   2. Schrijft `docs/inputs/manifest.json` met beschikbare boeken/hoofdstukken.
#   3. Werkt de hoofdstuk-maxima in de HTML-viewers bij op basis van het
#      manifest (MAX_CHAPTER in compare*.html, chapters in viewer.html), zodat
#      de menu's automatisch meegroeien met de beschikbare output.
#   4. Roept `scripts/compare_sv2027.py` aan voor elk hoofdstuk dat in
#      `initiatiefsv27/<BOEK>/` staat én waarvoor we in `output/` aan dat boek
#      werken — dit ververst `docs/diff_<BOEK>_<H>.json` (en `docs/diff.json`,
#      laatst-geschreven hoofdstuk).
#
# `docs/inputs/` wordt mee-gecommit zodat GitHub Pages de bestanden kan
# serveren; bron van waarheid blijft `output/`.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$REPO_ROOT/output"
DST="$REPO_ROOT/docs/inputs"
EXT="$REPO_ROOT/initiatiefsv27"

if [[ ! -d "$SRC" ]]; then
  echo "Geen output/-map gevonden op $SRC" >&2
  exit 1
fi

mkdir -p "$DST"

# Spiegel alle <BOEK>/<BOEK>.<H>.json bestanden.
find "$SRC" -mindepth 2 -maxdepth 2 -type f -name '*.json' | while read -r src_file; do
  rel="${src_file#$SRC/}"
  dst_file="$DST/$rel"
  mkdir -p "$(dirname "$dst_file")"
  cp "$src_file" "$dst_file"
done

# Genereer een manifest van beschikbare boeken + hoofdstukken zodat de viewer
# desgewenst dynamisch kan ontdekken wat er staat.
python3 - "$DST" <<'PY'
import json, os, re, sys
root = sys.argv[1]
manifest = {}
pat = re.compile(r"^([A-Z0-9]{3})\.(\d+)\.json$")
for book in sorted(os.listdir(root)):
    book_dir = os.path.join(root, book)
    if not os.path.isdir(book_dir):
        continue
    chapters = []
    for fn in os.listdir(book_dir):
        m = pat.match(fn)
        if m and m.group(1) == book:
            chapters.append(int(m.group(2)))
    if chapters:
        manifest[book] = sorted(chapters)
with open(os.path.join(root, "manifest.json"), "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)
print(f"manifest: {manifest}")
PY

# Werk de hardgecodeerde hoofdstuk-maxima in de HTML-viewers bij op basis van
# het zojuist geschreven manifest, zodat de menu's automatisch meegroeien met
# de beschikbare output (bv. LUK.17.json aanwezig → menu loopt t/m hoofdstuk 17).
python3 - "$DST" "$REPO_ROOT/docs" <<'PY'
import json, os, re, sys
dst, docs = sys.argv[1], sys.argv[2]
with open(os.path.join(dst, "manifest.json"), encoding="utf-8") as f:
    manifest = json.load(f)
maxch = {book: max(chs) for book, chs in manifest.items() if chs}

# compare.html / compare_hsv.html / compare_all.html: const MAX_CHAPTER = {...};
obj = "{ " + ", ".join(f"{b}: {c}" for b, c in sorted(maxch.items())) + " }"
for fn in ("compare.html", "compare_hsv.html", "compare_all.html"):
    p = os.path.join(docs, fn)
    src = open(p, encoding="utf-8").read()
    new = re.sub(r"const MAX_CHAPTER = \{[^}]*\};",
                 f"const MAX_CHAPTER = {obj};", src)
    if new != src:
        open(p, "w", encoding="utf-8").write(new)
        print(f"{fn}: MAX_CHAPTER -> {obj}")

# viewer.html: per-boek 'chapters: N' in de BIBLE_BOOKS-array.
p = os.path.join(docs, "viewer.html")
src = open(p, encoding="utf-8").read()
new = src
for book, mc in maxch.items():
    new = re.sub(rf"(\{{ abbr: '{book}',[^}}]*chapters: )\d+",
                 lambda m: m.group(1) + str(mc), new)
if new != src:
    open(p, "w", encoding="utf-8").write(new)
    print(f"viewer.html: chapters bijgewerkt -> {maxch}")
PY

echo "Sync voltooid: $DST"

# Regenereer diff-bestanden voor elk hoofdstuk dat in initiatiefsv27 staat,
# beperkt tot boeken waarvoor we in output/ ten minste 1 hoofdstuk hebben.
# Drie diff-scripts voeden drie verschillende viewers:
#   - compare_sv2027.py → docs/diff_<BOEK>_<H>.json     (compare.html)
#   - compare_hsv.py    → docs/diff_hsv_<BOEK>_<H>.json (compare_hsv.html)
#   - compare_all.py    → docs/diff_all_<BOEK>_<H>.json (compare_all.html)
# Alle drie moeten worden ververst, anders toont de bijhorende viewer
# een stale modernisatie. compare_*.py gebruiken relatieve paden, dus
# draaien vanuit REPO_ROOT.
cd "$REPO_ROOT"
for src_book_dir in "$SRC"/*/; do
  book="$(basename "$src_book_dir")"

  # Sla niet-boek-mappen over (bv. META): vereis <BOEK>.<H>.json patroon.
  if ! compgen -G "$src_book_dir$book.*.json" >/dev/null; then
    continue
  fi

  # compare.html (SV1657 vs SV2027) — alleen als initiatiefsv27 voor dit boek bestaat.
  if [[ -d "$EXT/$book" ]]; then
    for ext_file in "$EXT/$book/$book".*.json; do
      [[ -e "$ext_file" ]] || continue
      fn="$(basename "$ext_file")"
      chapter="${fn#$book.}"
      chapter="${chapter%.json}"
      python3 scripts/compare_sv2027.py "$book" "$chapter"
    done
  fi

  # compare_hsv.html — alleen als hsv/<BOEK>/ bestaat.
  if [[ -d "$REPO_ROOT/hsv/$book" ]]; then
    python3 scripts/compare_hsv.py "$book"
  fi

  # compare_all.html — werkt ook met alleen SV1657 + SV2026; altijd genereren.
  python3 scripts/compare_all.py "$book"
done
