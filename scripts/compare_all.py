"""Merge alle vier de bronnen (SV1657, SV2027, HSV, SV2026) per hoofdstuk
naar docs/diff_all_<BOEK>_<H>.json voor compare_all.html.

Bronnen:
- input.sv/<BOEK>/<BOEK>.<H>.json    -> SV1657 origineel (fallback voor pending)
- output/<BOEK>/<BOEK>.<H>.json      -> Onze modernisatie (SV2026) + originele SV1657 met
                                       gemoderniseerde kanttekening-formatting
- initiatiefsv27/<BOEK>/...           -> Initiatief SV2027 (extern)
- hsv/<BOEK>/...                      -> Herziene Statenvertaling (extern)
"""

import argparse
import json
import os
import re
import sys


def load_json(path: str) -> dict | None:
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def strip_verse_number_prefix(text: str) -> str:
    if not text:
        return text
    return re.sub(r"^\s*\d+(?:[-,]\d+)?\s+", "", text)


BOOK_CHAPTERS = {
    "LUK": 24,
    "MRK": 16,
}


def chapter_range_for_book(book: str) -> list[int]:
    n = BOOK_CHAPTERS.get(book)
    if n is None:
        raise ValueError(f"Geen hoofdstuk-range bekend voor {book}")
    return list(range(1, n + 1))


def extract_intro_text(raw) -> str:
    if isinstance(raw, str):
        return raw
    if isinstance(raw, dict):
        return raw.get("text") or raw.get("original") or ""
    return ""


def generate_diff(book: str, chapter: int) -> bool:
    paths = {
        "internal": f"output/{book}/{book}.{chapter}.json",
        "sv2027": f"initiatiefsv27/{book}/{book}.{chapter}.json",
        "hsv": f"hsv/{book}/{book}.{chapter}.json",
        "sv_input": f"input.sv/{book}/{book}.{chapter}.json",
    }

    internal = load_json(paths["internal"]) or {"verses": [], "introduction": {}, "epilogue": {}}
    sv2027 = load_json(paths["sv2027"]) or {"verses": [], "introduction": {}}
    hsv = load_json(paths["hsv"]) or {"verses": []}
    sv_input = load_json(paths["sv_input"]) or {"verses": [], "introduction": {}, "epilogue": {}}

    # Bouw lookup-tabellen
    internal_verses = {v["verse_number"]: v for v in internal.get("verses", [])}
    sv2027_verses = {v["verse_number"]: v for v in sv2027.get("verses", [])}
    hsv_verses = {v["verse_number"]: v for v in hsv.get("verses", [])}
    sv_input_verses = {v["verse_number"]: v for v in sv_input.get("verses", [])}

    # Verzameling van alle versnummers die ergens voorkomen
    all_v_nums = sorted(set(internal_verses) | set(sv2027_verses) | set(hsv_verses) | set(sv_input_verses))

    # Introduction
    intro_int = internal.get("introduction") or {}
    intro_sv2027_text = (sv2027.get("introduction") or {}).get("modernized", "")
    intro_sv1657 = intro_int.get("original") or extract_intro_text(sv_input.get("introduction"))
    intro_diff = {
        "sv2026": intro_int.get("modernized", ""),
        "sv2027": intro_sv2027_text,
        "hsv": None,
        "original": intro_sv1657,
    }

    # Verzen
    diff_verses: list[dict] = []
    for v_num in all_v_nums:
        int_v = internal_verses.get(v_num)
        sv27_v = sv2027_verses.get(v_num)
        hsv_v = hsv_verses.get(v_num)
        sv_in_v = sv_input_verses.get(v_num)

        original = (int_v.get("original") if int_v else None) or (sv_in_v.get("text") if sv_in_v else "")

        entry = {
            "verse_number": v_num,
            "status": "modernized" if int_v else "pending",
            "sv2026": int_v["modernized"] if int_v else "",
            "sv2027": strip_verse_number_prefix(sv27_v["modernized"]) if sv27_v else "",
            "hsv": hsv_v["modernized"] if hsv_v else "",
            "original": original,
        }
        if int_v and int_v.get("notes"):
            entry["notes"] = int_v["notes"]
        diff_verses.append(entry)

    # Epilogue
    epi_int = internal.get("epilogue") or {}
    epi_sv1657 = (epi_int.get("original") if epi_int else "") or extract_intro_text(sv_input.get("epilogue"))
    epi_sv2027 = (sv2027.get("epilogue") or {}).get("modernized", "")
    epi_diff = None
    if epi_int or epi_sv1657 or epi_sv2027:
        epi_diff = {
            "sv2026": epi_int.get("modernized", "") if epi_int else "",
            "sv2027": epi_sv2027,
            "hsv": None,
            "original": epi_sv1657,
        }

    output_data = {
        "book": book,
        "chapter": int(chapter),
        "introduction": intro_diff,
        "verses": diff_verses,
        "epilogue": epi_diff,
    }

    out_path = f"docs/diff_all_{book}_{chapter}.json"
    os.makedirs("docs", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"  → {out_path}  ({len(diff_verses)} verzen)")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge SV1657 + SV2027 + HSV + SV2026 per hoofdstuk.")
    parser.add_argument("book", nargs="?", default="LUK")
    parser.add_argument("chapter", nargs="?", default=None)
    args = parser.parse_args()

    chapters = [int(args.chapter)] if args.chapter else chapter_range_for_book(args.book)

    failures: list[int] = []
    for ch in chapters:
        ok = generate_diff(args.book, ch)
        if not ok:
            failures.append(ch)

    if failures:
        print(f"\nMislukt: {failures}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
