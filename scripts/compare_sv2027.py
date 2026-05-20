import json
import os
import sys
import difflib
import re

def clean_markers(text):
    """Removes markers for a clean text comparison if needed."""
    return re.sub(r'<.*?>|\$.*?\$', '', text).strip()

def strip_verse_number_prefix(text):
    # SV2027 prefixt elk vers met het versnummer (bv. "1 AANGEZIEN ...",
    # "12-13 En ..."). SV2026 doet dat niet, dus zonder strip wordt het
    # nummer in de side-by-side diff als toevoeging gemarkeerd.
    if not text:
        return text
    return re.sub(r'^\s*\d+(?:[-,]\d+)?\s+', '', text)

def generate_diff(book, chapter):
    external_path = f"initiatiefsv27/{book}/{book}.{chapter}.json"
    internal_path = f"output/{book}/{book}.{chapter}.json"
    sv_input_path = f"input.sv/{book}/{book}.{chapter}.json"

    external_data = None
    if os.path.exists(external_path):
        with open(external_path, 'r', encoding='utf-8') as f:
            external_data = json.load(f)
    else:
        print(f"Note: External SV2027 file {external_path} not found — generating placeholder diff.")

    internal_data = {"verses": [], "introduction": {}, "epilogue": {}}
    if os.path.exists(internal_path):
        with open(internal_path, 'r', encoding='utf-8') as f:
            internal_data = json.load(f)

    sv_input_data = {"verses": [], "introduction": {}, "epilogue": {}}
    if os.path.exists(sv_input_path):
        with open(sv_input_path, 'r', encoding='utf-8') as f:
            sv_input_data = json.load(f)
    sv_input_verses = {v["verse_number"]: v for v in sv_input_data.get("verses", [])}

    if external_data is None:
        # No SV2027 available — use SV1657 input as verse skeleton so the
        # viewer can still show our modernization vs. a "geen SV2027"-kolom.
        external_data = {
            "verses": [{"verse_number": v["verse_number"], "modernized": ""} for v in sv_input_data.get("verses", [])],
            "introduction": {"modernized": ""},
            "epilogue": {"modernized": ""},
        }
    
    diff_results = []
    
    # Compare Introduction
    intro_diff = {
        "status": "modernized" if internal_data.get("introduction", {}).get("modernized") else "pending",
        "sv2026": internal_data.get("introduction", {}).get("modernized", ""),
        "sv2027": external_data.get("introduction", {}).get("modernized", ""),
        "original": internal_data.get("introduction", {}).get("original", "")
    }

    # Compare Verses
    internal_verses = {v['verse_number']: v for v in internal_data.get('verses', [])}
    for ext_verse in external_data['verses']:
        v_num = ext_verse['verse_number']
        int_verse = internal_verses.get(v_num)
        sv_v = sv_input_verses.get(v_num)

        status = "modernized" if int_verse else "pending"
        original = (int_verse['original'] if int_verse else None) or (sv_v.get("text") if sv_v else "")

        entry = {
            "verse_number": v_num,
            "status": status,
            "sv2026": int_verse['modernized'] if int_verse else "",
            "sv2027": strip_verse_number_prefix(ext_verse['modernized']),
            "original": original,
        }
        if int_verse and int_verse.get("notes"):
            entry["notes"] = int_verse["notes"]
        diff_results.append(entry)
    
    # Compare Epilogue
    epi_diff = None
    if internal_data.get("epilogue") or external_data.get("epilogue"):
        epi_diff = {
            "status": "modernized" if internal_data.get("epilogue", {}).get("modernized") else "pending",
            "sv2026": internal_data.get("epilogue", {}).get("modernized", ""),
            "sv2027": external_data.get("epilogue", {}).get("modernized", ""),
            "original": internal_data.get("epilogue", {}).get("original", "")
        }

    output_data = {
        "book": book,
        "chapter": int(chapter),
        "introduction": intro_diff,
        "verses": diff_results,
        "epilogue": epi_diff
    }

    # Save versioned and default
    paths = [f"docs/diff_{book}_{chapter}.json", "docs/diff.json"]
    for p in paths:
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"Comparison generated: {paths[0]} and {paths[1]}")


def chapter_range_for_book(book):
    if book == "LUK":
        return range(1, 25)
    if book == "MRK":
        return range(1, 17)
    raise ValueError(f"Geen hoofdstuk-range bekend voor {book}")


if __name__ == "__main__":
    book = sys.argv[1] if len(sys.argv) > 1 else "LUK"
    chapter = sys.argv[2] if len(sys.argv) > 2 else None
    if chapter is None:
        for ch in chapter_range_for_book(book):
            generate_diff(book, ch)
    else:
        generate_diff(book, chapter)
