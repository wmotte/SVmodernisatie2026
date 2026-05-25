"""Genereer docs/diff_gbs_<BOEK>_<H>.json door de GBS-editie (extern, met
kanttekeningen) te mergen met output/<BOEK>/<BOEK>.<H>.json (onze modernisatie)
en input.sv/<BOEK> (SV1657-origineel).

Spiegelt scripts/compare_hsv.py. Verschillen:
- De GBS-tekst draagt aparte kanttekeningen (lijst), niet inline. Wij koppelen
  ze op volgorde aan de inline <…>-annotaties uit onze modernisatie, zodat de
  viewer per kanttekening een GBS↔SV2026-diff kan kleuren.
- Intro: GBS heeft een inhoudsopgave-string; SV2026/origineel hun eigen intro.
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


def chapter_range_for_book(book: str) -> list[int]:
    if book == "LUK":
        return list(range(1, 25))
    raise ValueError(f"Geen hoofdstuk-range bekend voor {book}")


def extract_annotations(text: str) -> list[str]:
    """Haal inline <…>-kanttekeningen op volgorde uit een SV2026-tekst."""
    if not text:
        return []
    return [m.strip() for m in re.findall(r"<([^<>]*)>", text)]


def extract_verwijzingen(text: str) -> list[str]:
    """Haal inline $…$-bijbelverwijzingen op volgorde uit een SV2026-tekst."""
    if not text:
        return []
    return [m.strip() for m in re.findall(r"\$([^$]*)\$", text)]


def pair_kanttekeningen(gbs_notes: list[dict], sv2026_text: str) -> list[dict]:
    """Koppel GBS-noten aan SV2026-markers, gescheiden per soort.

    GBS-noten met een cijfer-label (kind 'kanttekening') koppelen aan de inline
    <…>-annotaties; letter-labels (kind 'verwijzing') aan de $…$-verwijzingen.
    Beide stromen lopen op volgorde. Niet-gekoppelde markers verschijnen los.
    """
    sv_kant = extract_annotations(sv2026_text)
    sv_verw = extract_verwijzingen(sv2026_text)
    ik = iv = 0
    pairs: list[dict] = []

    for note in gbs_notes:
        kind = note.get("kind") or "kanttekening"
        if kind == "verwijzing":
            sv = sv_verw[iv] if iv < len(sv_verw) else ""
            iv += 1
        else:
            sv = sv_kant[ik] if ik < len(sv_kant) else ""
            ik += 1
        pairs.append({"label": note.get("label"), "kind": kind, "gbs": note["text"], "sv2026": sv})

    # Resterende SV2026-markers zonder GBS-tegenhanger los toevoegen.
    while ik < len(sv_kant):
        pairs.append({"label": None, "kind": "kanttekening", "gbs": "", "sv2026": sv_kant[ik]})
        ik += 1
    while iv < len(sv_verw):
        pairs.append({"label": None, "kind": "verwijzing", "gbs": "", "sv2026": sv_verw[iv]})
        iv += 1

    return pairs


def intro_text(raw) -> str:
    if isinstance(raw, str):
        return raw
    if isinstance(raw, dict):
        return raw.get("modernized") or raw.get("text") or raw.get("original", "")
    return ""


def generate_diff(book: str, chapter: int) -> bool:
    gbs_path = f"gbs/{book}/{book}.{chapter}.json"
    internal_path = f"output/{book}/{book}.{chapter}.json"
    sv_input_path = f"input.sv/{book}/{book}.{chapter}.json"

    gbs = load_json(gbs_path)
    if gbs is None:
        print(f"Error: {gbs_path} niet gevonden — draai eerst fetch_gbs.py",
              file=sys.stderr)
        return False

    internal = load_json(internal_path) or {"verses": [], "introduction": {}, "epilogue": {}}
    sv_input = load_json(sv_input_path) or {"verses": [], "introduction": {}, "epilogue": {}}
    sv_input_verses = {v["verse_number"]: v for v in sv_input.get("verses", [])}
    internal_verses = {v["verse_number"]: v for v in internal.get("verses", [])}

    # Introduction: origineel (SV1657) | GBS (inhoudsopgave) | SV2026.
    intro_int = internal.get("introduction") or {}
    intro_original = intro_int.get("original") or intro_text(sv_input.get("introduction"))
    intro_diff = {
        "original": intro_original,
        "gbs": gbs.get("introduction", ""),
        "sv2026": intro_int.get("modernized", ""),
    }

    diff_verses: list[dict] = []
    for gbs_v in gbs.get("verses", []):
        v_num = gbs_v["verse_number"]
        int_v = internal_verses.get(v_num)
        sv_v = sv_input_verses.get(v_num)
        original = (int_v["original"] if int_v else None) or (sv_v.get("text") if sv_v else "")
        sv2026 = int_v["modernized"] if int_v else ""
        entry = {
            "verse_number": v_num,
            "status": "modernized" if int_v else "pending",
            "original": original,
            "gbs_text": gbs_v.get("text", ""),
            "sv2026": sv2026,
            "kanttekeningen": pair_kanttekeningen(gbs_v.get("kanttekeningen", []), sv2026),
        }
        if int_v and int_v.get("notes"):
            entry["notes"] = int_v["notes"]
        diff_verses.append(entry)

    output_data = {
        "book": book,
        "chapter": int(chapter),
        "introduction": intro_diff,
        "verses": diff_verses,
    }

    out_path = f"docs/diff_gbs_{book}_{chapter}.json"
    os.makedirs("docs", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    print(f"  → {out_path}  ({len(diff_verses)} verzen)")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Genereer GBS-vs-SV2026 diff JSON.")
    parser.add_argument("book", nargs="?", default="LUK")
    parser.add_argument("chapter", nargs="?", default=None)
    args = parser.parse_args()

    chapters = [int(args.chapter)] if args.chapter else chapter_range_for_book(args.book)

    failures: list[int] = []
    for ch in chapters:
        if not generate_diff(args.book, ch):
            failures.append(ch)

    if failures:
        print(f"\nMislukt: {failures}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
