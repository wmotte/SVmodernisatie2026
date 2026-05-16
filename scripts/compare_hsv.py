"""Genereer docs/diff_hsv_<BOEK>_<H>.json door HSV (extern) te mergen
met output/<BOEK>/<BOEK>.<H>.json (intern, onze modernisatie).

Spiegelt scripts/compare_sv2027.py voor HSV. Verschillen:
- HSV heeft geen aparte introduction/epilogue. Bij die velden krijgt de
  HSV-kant `null` en status "no_hsv_equivalent".
- HSV-tekst wordt schoon aangeleverd door fetch_hsv.py (geen leading
  versnummer-prefix), dus geen strip_verse_number_prefix nodig.
"""

import argparse
import json
import os
import sys


def load_json(path: str) -> dict | None:
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def chapter_range_for_book(book: str) -> list[int]:
    if book == "LUK":
        return list(range(1, 25))
    if book == "MRK":
        return list(range(1, 17))
    raise ValueError(f"Geen hoofdstuk-range bekend voor {book}")


def generate_diff(book: str, chapter: int) -> bool:
    external_path = f"hsv/{book}/{book}.{chapter}.json"
    internal_path = f"output/{book}/{book}.{chapter}.json"
    sv_input_path = f"input.sv/{book}/{book}.{chapter}.json"

    external = load_json(external_path)
    if external is None:
        print(f"Error: {external_path} niet gevonden — draai eerst fetch_hsv.py",
              file=sys.stderr)
        return False

    internal = load_json(internal_path) or {"verses": [], "introduction": {}, "epilogue": {}}
    # input.sv bevat de SV1657-bron; gebruik die als fallback voor "original"
    # bij verzen die nog niet door ons gemoderniseerd zijn (anders blijft de
    # SV1657-kolom leeg op pending hoofdstukken — onnodig informatieverlies).
    sv_input = load_json(sv_input_path) or {"verses": [], "introduction": {}, "epilogue": {}}
    sv_input_verses = {v["verse_number"]: v for v in sv_input.get("verses", [])}

    # Introduction: HSV heeft hier nooit een equivalent (geen apart intro-veld
    # op de HSV-pagina; wat HSV "Inleiding" noemt zijn gewoon verzen 1–4).
    intro_int = internal.get("introduction") or {}
    intro_sv_input_raw = sv_input.get("introduction")
    if isinstance(intro_sv_input_raw, str):
        intro_sv_input_text = intro_sv_input_raw
    elif isinstance(intro_sv_input_raw, dict):
        intro_sv_input_text = intro_sv_input_raw.get("text") or intro_sv_input_raw.get("original", "")
    else:
        intro_sv_input_text = ""
    intro_original = intro_int.get("original") or intro_sv_input_text
    intro_diff = {
        "status": "no_hsv_equivalent" if intro_int else ("pending" if intro_original else "no_hsv_equivalent"),
        "sv2026": intro_int.get("modernized", ""),
        "hsv": None,
        "original": intro_original,
    }

    # Verses
    internal_verses = {v["verse_number"]: v for v in internal.get("verses", [])}
    diff_verses: list[dict] = []
    for ext_v in external.get("verses", []):
        v_num = ext_v["verse_number"]
        int_v = internal_verses.get(v_num)
        sv_v = sv_input_verses.get(v_num)
        original = (int_v["original"] if int_v else None) or (sv_v.get("text") if sv_v else "")
        entry = {
            "verse_number": v_num,
            "status": "modernized" if int_v else "pending",
            "sv2026": int_v["modernized"] if int_v else "",
            "hsv": ext_v["modernized"],
            "original": original,
        }
        if int_v and int_v.get("notes"):
            entry["notes"] = int_v["notes"]
        diff_verses.append(entry)

    # Epilogue: zelfde patroon als intro — HSV heeft geen equivalent.
    epi_int = internal.get("epilogue") or {}
    epi_sv_input_raw = sv_input.get("epilogue")
    if isinstance(epi_sv_input_raw, str):
        epi_sv_input_text = epi_sv_input_raw
    elif isinstance(epi_sv_input_raw, dict):
        epi_sv_input_text = epi_sv_input_raw.get("text") or epi_sv_input_raw.get("original", "")
    else:
        epi_sv_input_text = ""
    epi_diff = None
    epi_original = (epi_int.get("original") if epi_int else "") or epi_sv_input_text
    if epi_int or epi_original:
        epi_diff = {
            "status": "no_hsv_equivalent",
            "sv2026": epi_int.get("modernized", "") if epi_int else "",
            "hsv": None,
            "original": epi_original,
        }

    output_data = {
        "book": book,
        "chapter": int(chapter),
        "introduction": intro_diff,
        "verses": diff_verses,
        "epilogue": epi_diff,
    }

    out_path = f"docs/diff_hsv_{book}_{chapter}.json"
    os.makedirs("docs", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"  → {out_path}  ({len(diff_verses)} verzen)")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Genereer HSV-vs-SV2026 diff JSON.")
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
