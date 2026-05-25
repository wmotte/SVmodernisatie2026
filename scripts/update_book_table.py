#!/usr/bin/env python3
"""Regenereer docs/nt_boeken_hoofdstukken.md uit de feitelijke repo-staat.

Totalen (hoofdstukken + verzen) per NT-boek komen uit het bronkorpus
`input.sv/<BOEK>/<BOEK>.<H>.json`. Gedaan-tellingen komen uit
`output/<BOEK>/<BOEK>.<H>.json`: een hoofdstuk telt als gedaan zodra het
evenveel verzen heeft als de bron én elk vers een niet-lege `modernized`.

De tabel wordt gesorteerd op (hoofdstukken ↑, verzen ↑, canonieke volgorde),
zodat de uitvoer reproduceerbaar is.

Gebruik:  python3 scripts/update_book_table.py [--check]
  --check  schrijf niets; exit 1 als het bestand niet up-to-date is.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INPUT_DIR = REPO / "input.sv"
OUTPUT_DIR = REPO / "output"
MD_OUT = REPO / "docs" / "nt_boeken_hoofdstukken.md"

# Canonieke NT-volgorde + Nederlandse boeknaam zoals weergegeven in de tabel.
NT_BOOKS: list[tuple[str, str]] = [
    ("MAT", "Matteüs"),
    ("MRK", "Marcus"),
    ("LUK", "Lucas"),
    ("JHN", "Johannes"),
    ("ACT", "Handelingen"),
    ("ROM", "Romeinen"),
    ("1CO", "1 Korintiërs"),
    ("2CO", "2 Korintiërs"),
    ("GAL", "Galaten"),
    ("EPH", "Efeze"),
    ("PHP", "Filippenzen"),
    ("COL", "Kolossenzen"),
    ("1TH", "1 Tessalonicenzen"),
    ("2TH", "2 Tessalonicenzen"),
    ("1TI", "1 Timoteüs"),
    ("2TI", "2 Timoteüs"),
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


def _src_words_by_verse(path: Path) -> dict[int, int]:
    """Map verse_number → woordtelling van de bron-`text` (incl. kanttekeningen)."""
    try:
        verses = json.loads(path.read_text()).get("verses", [])
    except (json.JSONDecodeError, OSError):
        return {}
    return {
        int(v.get("verse_number", i)): len(str(v.get("text", "")).split())
        for i, v in enumerate(verses)
    }


def _done_verse_numbers(path: Path) -> set[int]:
    """verse_number's met niet-lege `modernized` in een output-hoofdstuk."""
    try:
        verses = json.loads(path.read_text()).get("verses", [])
    except (json.JSONDecodeError, OSError):
        return set()
    return {
        int(v.get("verse_number", i))
        for i, v in enumerate(verses)
        if str(v.get("modernized", "")).strip()
    }


def gather(code: str) -> dict[str, int]:
    """Tel hoofdstukken/verzen (bron) en gedaan-hoofdstukken/-verzen (output)."""
    src = INPUT_DIR / code
    out = OUTPUT_DIR / code
    tot_ch = tot_v = tot_w = done_ch = done_v = done_w = 0
    for f in sorted(src.glob(f"{code}.*.json")):
        src_words = _src_words_by_verse(f)
        n_src = len(src_words)
        if n_src == 0:
            continue
        tot_ch += 1
        tot_v += n_src
        tot_w += sum(src_words.values())
        of = out / f.name
        if not of.exists():
            continue
        done_nums = _done_verse_numbers(of)
        done_v += len(done_nums)
        done_w += sum(src_words.get(n, 0) for n in done_nums)
        if len(done_nums) >= n_src:
            done_ch += 1
    return {
        "chapters": tot_ch,
        "verses": tot_v,
        "words": tot_w,
        "done_chapters": done_ch,
        "done_verses": done_v,
        "done_words": done_w,
    }


def pct(done: int, total: int) -> str:
    if total == 0:
        return "0%"
    return f"{round(done / total * 100)}%"


def nl(x: float) -> str:
    """Eén decimaal met Nederlandse komma."""
    return f"{x:.1f}".replace(".", ",")


def nl_int(n: int) -> str:
    """Geheel getal met Nederlands duizendtalpunt (1234 → 1.234)."""
    return f"{n:,}".replace(",", ".")


def render() -> str:
    rows = []
    for code, name in NT_BOOKS:
        s = gather(code)
        rows.append((code, name, s))

    # Sorteer op hoofdstukken ↑, verzen ↑, canonieke index (stabiel).
    order = {code: i for i, (code, _) in enumerate(NT_BOOKS)}
    rows.sort(key=lambda r: (r[2]["chapters"], r[2]["verses"], order[r[0]]))

    lines = [
        "# NT-boeken gesorteerd op aantal hoofdstukken (laag → hoog)",
        "",
        "| # | Bijbelboek | Hoofdstukken | Verzen | Woorden | Gedaan (hfst) | % gedaan |",
        "|---|------------|--------------|--------|---------|---------------|----------|",
    ]
    for i, (_code, name, s) in enumerate(rows, 1):
        lines.append(
            f"| {i} | {name} | {s['chapters']} | {s['verses']} | "
            f"{nl_int(s['words'])} | "
            f"{s['done_chapters']} | {pct(s['done_chapters'], s['chapters'])} |"
        )

    tot_ch = sum(s["chapters"] for _, _, s in rows)
    tot_v = sum(s["verses"] for _, _, s in rows)
    tot_w = sum(s["words"] for _, _, s in rows)
    done_ch = sum(s["done_chapters"] for _, _, s in rows)
    done_v = sum(s["done_verses"] for _, _, s in rows)
    done_w = sum(s["done_words"] for _, _, s in rows)

    lines += [
        "",
        "## Voortgang",
        "",
        "| Eenheid | Gedaan | Totaal | % |",
        "|---------|--------|--------|---|",
        f"| Hoofdstukken | {done_ch} | {tot_ch} | {nl(done_ch / tot_ch * 100)}% |",
        f"| Verzen | {done_v} | {tot_v} | {nl(done_v / tot_v * 100)}% |",
        f"| Woorden | {nl_int(done_w)} | {nl_int(tot_w)} | {nl(done_w / tot_w * 100)}% |",
        "",
    ]

    gedaan = [
        f"{name} ({s['done_chapters']} hfst / {s['done_verses']} v)"
        for _code, name, s in rows
        if s["done_chapters"] > 0
    ]
    if gedaan:
        lines.append("Gedaan: " + ", ".join(gedaan) + ".")
        lines.append("")
    lines += [
        f"Totaal woorden in de bron: {nl_int(tot_w)} (incl. kanttekeningen in `<...>`).",
        "Totalen (hoofdstukken/verzen) geteld uit `input.sv/` (SV1657).",
        "Gedaan-tellingen uit `output/`: een hoofdstuk telt als gedaan zodra elk",
        "vers een gemoderniseerde tekst heeft. Gegenereerd met",
        "`scripts/update_book_table.py`.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    new = render()
    check = "--check" in sys.argv[1:]
    current = MD_OUT.read_text() if MD_OUT.exists() else ""
    if check:
        if current == new:
            print("nt_boeken_hoofdstukken.md is up-to-date.")
            return 0
        print("nt_boeken_hoofdstukken.md is VEROUDERD; draai zonder --check.",
              file=sys.stderr)
        return 1
    MD_OUT.write_text(new)
    print(f"Geschreven: {MD_OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
