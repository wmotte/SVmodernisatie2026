#!/usr/bin/env python3
"""Tel woorden in het NT-broncorpus (input.sv/) per bijbelboek.

Drie categorieën per boek (en als totaal onderaan):
  * hoofdtekst    — de versproza, zonder kanttekeningen <…> en zonder
                    bijbelverwijzingen $…$.
  * kanttekeningen — alle tekst binnen <…>-blokken in de verzen.
  * introductie   — de `introduction`- en `epilogue`-velden
                    (hoofdstuksamenvatting + boekepiloog) per hoofdstuk,
                    eveneens zonder <…> en $…$.

Een "woord" is een aaneengesloten reeks letters/cijfers (apostrof inbegrepen).
Uitvoer: een Markdown-tabel op stdout, geschikt om in
`docs/projectoverzicht.md` te plakken.

Gebruik:
    python3 scripts/count_words.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

INPUT_DIR = Path(__file__).resolve().parent.parent / "input.sv"

# Canonieke NT-volgorde + volledige Nederlandse boeknaam.
NT_BOOKS: list[tuple[str, str]] = [
    ("MAT", "Mattheüs"),
    ("MRK", "Markus"),
    ("LUK", "Lukas"),
    ("JHN", "Johannes"),
    ("ACT", "Handelingen"),
    ("ROM", "Romeinen"),
    ("1CO", "1 Korinthe"),
    ("2CO", "2 Korinthe"),
    ("GAL", "Galaten"),
    ("EPH", "Efeze"),
    ("PHP", "Filippenzen"),
    ("COL", "Kolossenzen"),
    ("1TH", "1 Thessalonicenzen"),
    ("2TH", "2 Thessalonicenzen"),
    ("1TI", "1 Timotheüs"),
    ("2TI", "2 Timotheüs"),
    ("TIT", "Titus"),
    ("PHM", "Filemon"),
    ("HEB", "Hebreeën"),
    ("JAS", "Jakobus"),
    ("1PE", "1 Petrus"),
    ("2PE", "2 Petrus"),
    ("1JN", "1 Johannes"),
    ("2JN", "2 Johannes"),
    ("3JN", "3 Johannes"),
    ("JUD", "Judas"),
    ("REV", "Openbaring"),
]

ANNOTATION_RE = re.compile(r"<[^>]*>")
REFERENCE_RE = re.compile(r"\$[^$]*\$")
WORD_RE = re.compile(r"[0-9A-Za-zÀ-ÿ’']+")
# Losse bijbelplaats binnen een $…$-blok: hoofdstuk.vers (bv. `30.18`)…
CHAPTER_VERSE_RE = re.compile(r"\d+\.\d+")
# …plus komma-continuaties die extra verzen in hetzelfde hoofdstuk opsommen
# (bv. `6.13, 17` -> verzen 13 én 17).
EXTRA_VERSE_RE = re.compile(r",\s*\d+")


def count_words(text: str) -> int:
    return len(WORD_RE.findall(text))


def count_references(text: str) -> tuple[int, int]:
    """Geef (aantal $…$-blokken, geschat aantal losse verwijzingen) terug."""
    blocks = REFERENCE_RE.findall(text)
    singles = 0
    for block in blocks:
        singles += len(CHAPTER_VERSE_RE.findall(block))
        singles += len(EXTRA_VERSE_RE.findall(block))
    return len(blocks), singles


def split_annotations(text: str) -> tuple[str, str]:
    """Geef (hoofdtekst, kanttekeningen-tekst) terug.

    Kanttekeningen = alles binnen <…>. Hoofdtekst = de rest, met de
    $…$-verwijzingen verwijderd.
    """
    annotations = " ".join(ANNOTATION_RE.findall(text))
    main = ANNOTATION_RE.sub(" ", text)
    main = REFERENCE_RE.sub(" ", main)
    return main, annotations


def count_book(book: str) -> tuple[int, int, int, int, int]:
    """Tel per boek: (hoofdtekst, kanttekeningen, introductie,
    $…$-blokken, losse verwijzingen)."""
    book_dir = INPUT_DIR / book
    main_total = annot_total = intro_total = 0
    ref_blocks = ref_singles = 0
    for chapter_file in book_dir.glob(f"{book}.*.json"):
        data = json.loads(chapter_file.read_text(encoding="utf-8"))
        intro = (data.get("introduction") or "") + " " + (data.get("epilogue") or "")
        intro = REFERENCE_RE.sub(" ", ANNOTATION_RE.sub(" ", intro))
        intro_total += count_words(intro)
        for verse in data.get("verses", []):
            text = verse.get("text", "")
            main, annotations = split_annotations(text)
            main_total += count_words(main)
            annot_total += count_words(annotations)
            blocks, singles = count_references(text)
            ref_blocks += blocks
            ref_singles += singles
    return main_total, annot_total, intro_total, ref_blocks, ref_singles


def fmt(n: int) -> str:
    """Duizendtallen met punt, zoals elders in projectoverzicht.md."""
    return f"{n:,}".replace(",", ".")


def main() -> None:
    rows: list[tuple[str, int, int, int, int, int]] = []
    g_main = g_annot = g_intro = g_blocks = g_singles = 0
    for book, name in NT_BOOKS:
        if not (INPUT_DIR / book).is_dir():
            continue
        main, annot, intro, blocks, singles = count_book(book)
        rows.append((f"{name} ({book})", main, annot, intro, blocks, singles))
        g_main += main
        g_annot += annot
        g_intro += intro
        g_blocks += blocks
        g_singles += singles

    print(
        "| Boek | Hoofdtekst | Kanttekeningen | Introductie | Woorden totaal "
        "| Verwijzingen ($…$) | Losse refs |"
    )
    print("|---|---:|---:|---:|---:|---:|---:|")
    for name, main, annot, intro, blocks, singles in rows:
        words = main + annot + intro
        print(
            f"| {name} | {fmt(main)} | {fmt(annot)} | {fmt(intro)} | {fmt(words)} "
            f"| {fmt(blocks)} | {fmt(singles)} |"
        )
    g_words = g_main + g_annot + g_intro
    print(
        f"| **Totaal NT** | **{fmt(g_main)}** | **{fmt(g_annot)}** "
        f"| **{fmt(g_intro)}** | **{fmt(g_words)}** | **{fmt(g_blocks)}** "
        f"| **{fmt(g_singles)}** |"
    )


if __name__ == "__main__":
    main()
