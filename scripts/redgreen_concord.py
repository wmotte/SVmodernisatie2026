#!/usr/bin/env python3
"""Bounded concordantie-seed voor het red team (between-book consistentie).

Voor twee boeken: bouw een inverted index van Griekse brontokens
(`source_text`) → verzen, en rapporteer tokens die in BEIDE boeken
voorkomen waar de Nederlandse `modernized`-renderingen uiteenlopen.
Dit is een *seed*, geen oordeel: het red team verifieert elke kandidaat
in context.

De output is begrensd (top-K, default 25) zodat de context van het red
team klein blijft.

Heuristiek (lexicaal, geen lemmatizer):
  * Griekse tokens = aaneengesloten reeksen Grieks-Unicode, lengte ≥ 4.
  * Per token: verzamel per boek de set Nederlandse inhoudswoorden uit de
    bijbehorende `modernized`-verzen.
  * Divergentie-signaal = de twee boeken delen het token maar de
    dominante NL-inhoudswoorden overlappen niet → kandidaat-inconsistentie.
  * Rangschik op (gedeelde frequentie) zodat zinvolle, frequente tokens
    bovenaan staan.

Gebruik:
    uv run python scripts/redgreen_concord.py --books MAT MRK
    uv run python scripts/redgreen_concord.py --books MAT MRK --top 25 \\
        --out output/META/debate/concord_1.json
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INPUT_DIR = REPO / "input.sv"
OUTPUT_DIR = REPO / "output"

GREEK_RE = re.compile(r"[Ͱ-Ͽἀ-῿]+")
NL_WORD_RE = re.compile(r"[A-Za-zÀ-ÿ’']+")

# Nederlandse functiewoorden — uit de NL-inhoudswoord-set houden.
NL_STOP = {
    "de", "het", "een", "en", "van", "in", "op", "te", "ten", "ter", "tot",
    "die", "dat", "dit", "deze", "is", "zijn", "was", "waren", "wordt",
    "werd", "worden", "heeft", "hebben", "had", "met", "voor", "door",
    "aan", "bij", "om", "als", "maar", "ook", "niet", "geen", "wel", "want",
    "dan", "dus", "toen", "u", "hij", "zij", "ze", "wij", "we", "ik", "gij",
    "hem", "haar", "hun", "zich", "men", "er", "daar", "hier", "naar", "uit",
    "over", "onder", "want", "of", "want", "zo", "al", "nog", "weer", "want",
    "hen", "mij", "me", "jij", "je", "zal", "zult", "zou", "kan", "moet",
    "want", "zeer", "want", "want",
}


def _read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _content_words(text: str) -> set[str]:
    return {
        w.lower() for w in NL_WORD_RE.findall(text or "")
        if len(w) >= 4 and w.lower() not in NL_STOP
    }


def _index_book(book: str) -> dict[str, list[dict]]:
    """Griekse token → lijst van {chapter, verse, modern_words, modern_excerpt}."""
    index: dict[str, list[dict]] = defaultdict(list)
    bdir = OUTPUT_DIR / book
    if not bdir.is_dir():
        return index
    for f in sorted(bdir.glob(f"{book}.*.json")):
        data = _read_json(f)
        if not data:
            continue
        chapter = data.get("chapter")
        for v in data.get("verses") or []:
            src = v.get("source_text") or ""
            modern = v.get("modernized") or ""
            if not src or not modern:
                continue
            words = _content_words(modern)
            entry = {
                "chapter": chapter,
                "verse": v.get("verse_number"),
                "modern_words": words,
                "modern_excerpt": modern[:160],
            }
            for tok in set(GREEK_RE.findall(src)):
                if len(tok) >= 4:
                    index[tok].append(entry)
    return index


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--books", nargs=2, required=True, metavar=("BOOK1", "BOOK2"))
    ap.add_argument("--top", type=int, default=25, help="Max aantal kandidaten.")
    ap.add_argument("--out", default=None,
                    help="JSON-uitvoerpad (default: stdout-samenvatting + geen file).")
    args = ap.parse_args()

    b1, b2 = args.books
    idx1 = _index_book(b1)
    idx2 = _index_book(b2)
    shared = set(idx1) & set(idx2)

    candidates = []
    for tok in shared:
        occ1, occ2 = idx1[tok], idx2[tok]
        words1: set[str] = set().union(*(e["modern_words"] for e in occ1)) if occ1 else set()
        words2: set[str] = set().union(*(e["modern_words"] for e in occ2)) if occ2 else set()
        overlap = words1 & words2
        # Divergentie = beide boeken renderen, maar geen gedeeld inhoudswoord.
        if words1 and words2 and not overlap:
            freq = len(occ1) + len(occ2)
            candidates.append({
                "greek_token": tok,
                "shared_frequency": freq,
                f"{b1}_examples": [
                    {"chapter": e["chapter"], "verse": e["verse"],
                     "excerpt": e["modern_excerpt"]}
                    for e in occ1[:2]
                ],
                f"{b2}_examples": [
                    {"chapter": e["chapter"], "verse": e["verse"],
                     "excerpt": e["modern_excerpt"]}
                    for e in occ2[:2]
                ],
                f"{b1}_words": sorted(words1)[:8],
                f"{b2}_words": sorted(words2)[:8],
            })

    candidates.sort(key=lambda c: -c["shared_frequency"])
    candidates = candidates[: args.top]

    result = {
        "books": [b1, b2],
        "shared_greek_tokens": len(shared),
        "divergence_candidates": len(candidates),
        "note": "Lexicale seed; geen oordeel. Verifieer elke kandidaat in context.",
        "candidates": candidates,
    }

    if args.out:
        outp = Path(args.out)
        outp.parent.mkdir(parents=True, exist_ok=True)
        outp.write_text(json.dumps(result, ensure_ascii=False, indent=2),
                        encoding="utf-8")
        print(json.dumps({"out": str(outp), "books": [b1, b2],
                          "shared_greek_tokens": len(shared),
                          "divergence_candidates": len(candidates)},
                         ensure_ascii=False))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
