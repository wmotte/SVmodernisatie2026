"""Normaliseer SV1657-bijbelverwijzingen naar moderne notatie.

Vervangt elke `$...$` blok in een input-string. Idempotent: een al moderne
verwijzing blijft staan.

Twee-staps-lookup:
  1. oude afk (`Iudic`, `1.Chron`)  -> Full Name (Dutch)  via bible_book_references.csv
  2. Full Name (Dutch)              -> korte afk          via afkortingen.csv

Voorbeelden:
  $Iudic. 13.4.$            -> $Ri. 13:4$
  $1.Chron. 24.10.$         -> $1Kr. 24:10$
  $Exod. 30.7. Levit. 16.17.$ -> $Ex. 30:7; Lv. 16:17$
  $Iesa. 30.18. ende 41.9.$ -> $Js. 30:18; 41:9$
  $Hebr. 6.13, 17.$         -> $Hb. 6:13,17$
  $Psalm 45. vers 7.$       -> $Ps. 45:7$

Met `--include-kanttekeningen` worden óók loose refs binnen `<...>` blokken
genormaliseerd én gewrapt in `$...$`, zodat ze net als hoofdtekst-refs via
één regex te onderscheiden zijn:
  <Siet 1.Ioan. 1.1.>           -> <Zie $1Jh. 1:1$.>   (na modernisatie)
  <Siet Actor. 24.3. ende 26.25.> -> <Zie $Hd. 24:3; 26:25$.>

Bij parse-fouten: input blijft ongewijzigd (best-effort, idempotent).

CLI:
    python scripts/bibref.py normalize --current-book LUK "<tekst-met-$...$-blokken>"
"""

import argparse
import csv
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REFDATA = PROJECT_ROOT / "refdata"

# Aliassen voor full-name varianten die tussen de twee CSV's verschillen.
# bible_book_references.csv geeft "Rechters" voor "Iudic"; afkortingen.csv
# kent alleen "Richteren". Beide zijn dezelfde bijbelboek.
FULLNAME_ALIASES = {
    "Rechters": "Richteren",
    "Efeziërs": "Efeze",
}

# Welke 3-letterige projectcode hoort bij welke Full Name?
# Gebruikt door --current-book om impliciete refs ($H:V$ zonder boek) te resolven.
PROJECT_CODE_TO_FULLNAME = {
    "GEN": "Genesis",
    "EXO": "Exodus",
    "LEV": "Leviticus",
    "NUM": "Numeri",
    "DEU": "Deuteronomium",
    "JOS": "Jozua",
    "JDG": "Richteren",
    "RUT": "Ruth",
    "1SA": "1 Samuël",
    "2SA": "2 Samuël",
    "1KI": "1 Koningen",
    "2KI": "2 Koningen",
    "1CH": "1 Kronieken",
    "2CH": "2 Kronieken",
    "EZR": "Ezra",
    "NEH": "Nehemia",
    "EST": "Esther",
    "JOB": "Job",
    "PSA": "Psalmen",
    "PRO": "Spreuken",
    "ECC": "Prediker",
    "SNG": "Hooglied",
    "ISA": "Jesaja",
    "JER": "Jeremia",
    "LAM": "Klaagliederen",
    "EZK": "Ezechiël",
    "DAN": "Daniël",
    "HOS": "Hosea",
    "JOL": "Joël",
    "AMO": "Amos",
    "OBA": "Obadja",
    "JON": "Jona",
    "MIC": "Micha",
    "NAM": "Nahum",
    "HAB": "Habakuk",
    "ZEP": "Zefanja",
    "HAG": "Haggaï",
    "ZEC": "Zacharia",
    "MAL": "Maleachi",
    "MAT": "Mattheüs",
    "MRK": "Markus",
    "LUK": "Lukas",
    "JHN": "Johannes",
    "ACT": "Handelingen",
    "ROM": "Romeinen",
    "1CO": "1 Korinthe",
    "2CO": "2 Korinthe",
    "GAL": "Galaten",
    "EPH": "Efeze",
    "PHP": "Filippenzen",
    "COL": "Kolossenzen",
    "1TH": "1 Thessalonicenzen",
    "2TH": "2 Thessalonicenzen",
    "1TI": "1 Timotheüs",
    "2TI": "2 Timotheüs",
    "TIT": "Titus",
    "PHM": "Filemon",
    "HEB": "Hebreeën",
    "JAS": "Jakobus",
    "1PE": "1 Petrus",
    "2PE": "2 Petrus",
    "1JN": "1 Johannes",
    "2JN": "2 Johannes",
    "3JN": "3 Johannes",
    "JUD": "Judas",
    "REV": "Openbaring",
}


def _load_oldabbr_to_fullname() -> dict[str, str]:
    """oldAbbreviation (genormaliseerd, lowercase, geen punten) -> Full Name (Dutch)."""
    mapping: dict[str, str] = {}
    path = REFDATA / "bible_book_references.csv"
    with path.open(encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader, None)  # header
        for row in reader:
            if len(row) < 4:
                continue
            old_abbr, _modern_dutch, _modern_eng, full_name_dutch, _ = row[:5]
            key = _normalize_book_key(old_abbr)
            mapping[key] = full_name_dutch.strip()
            # Stuur ook de Full Name terug op zichzelf (idempotent).
            mapping[_normalize_book_key(full_name_dutch)] = full_name_dutch.strip()
    return mapping


def _load_fullname_to_modabbr() -> dict[str, str]:
    """Full Name (Dutch) -> korte afk (bv. 'Lukas' -> 'Lk.')."""
    mapping: dict[str, str] = {}
    path = REFDATA / "afkortingen.csv"
    with path.open(encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 2:
                continue
            full_name, abbr = row[0].strip(), row[1].strip()
            mapping[full_name] = abbr
    # Aliassen erbij zodat alternatieve full names ook resolven.
    for alias, canonical in FULLNAME_ALIASES.items():
        if canonical in mapping:
            mapping[alias] = mapping[canonical]
    return mapping


_DIACRITIC_FOLD = str.maketrans("ëéèêüúùûïíìîöóòôäáàâ", "eeeeuuuuiiiiooooaaaa")


def _normalize_book_key(s: str) -> str:
    """Normaliseer boeknaam-key voor lookup: lowercase, geen punten, geen spaties,
    diakrieten gevouwen (Ioël → ioel, Hosée → hosee). De refdata gebruikt soms
    de diakriet-vorm en soms niet; vouwen voorkomt mismatches."""
    return re.sub(r"[\s\.]", "", s).lower().translate(_DIACRITIC_FOLD)


# Match een hele bijbelref-uitdrukking binnen een $...$ blok.
# Onderdelen:
#   sameboek-marker (lege string als het volgde op 'ende'/'en')
#   optionele boeknaam: (1.) Naam (.)
#   optionele 'cap.'
#   hoofdstuk-cijfer
#   separator (`.` of `,`) tussen hoofdstuk en vers
#   optionele 'vers'
#   verzen-lijst: digit (`,` digit)*
_REF_RE = re.compile(
    r"""
    (?P<sameboek>@SAMEBOOK@\s+)?
    (?:
        (?P<book>(?:\d\s*\.?\s*)?[A-Z][a-zëéü]+\.?)
        \s+
    )?
    (?:cap\.\s*)?
    (?P<chapter>\d+)
    \s*[\.,]\s*
    (?:vers\s*)?
    (?P<verses>\d+(?:\s*,\s*\d+)*)
    """,
    re.VERBOSE,
)


def _resolve_modabbr(
    book_token: str,
    old_to_full: dict[str, str],
    full_to_abbr: dict[str, str],
) -> str | None:
    """Probeer een boeknaam-token om te zetten naar moderne korte afk."""
    key = _normalize_book_key(book_token)
    full = old_to_full.get(key)
    if full is None:
        return None
    abbr = full_to_abbr.get(full)
    if abbr is None:
        # Probeer alias-genormaliseerde versie.
        full_alias = FULLNAME_ALIASES.get(full)
        if full_alias:
            abbr = full_to_abbr.get(full_alias)
    return abbr


def _normalize_inner(content: str, current_book_full: str | None,
                     old_to_full: dict[str, str],
                     full_to_abbr: dict[str, str]) -> str:
    """Normaliseer de inhoud tussen `$...$`."""
    # Als de inhoud al lijkt op moderne notatie ('Lk. 3:1'), laat staan (idempotent).
    if re.fullmatch(r"\s*[\dA-Za-zëéü\.\s,;:\-]+\s*", content) and ":" in content:
        return content.strip()

    # Pre-processing: 'ende'/'en' → marker, normaliseer whitespace.
    s = " ".join(content.split())
    s = re.sub(r"\b(ende|en)\b", "@SAMEBOOK@", s)

    parts: list[str] = []
    last_modabbr: str | None = None
    last_emitted_modabbr: str | None = None
    if current_book_full is not None:
        last_modabbr = full_to_abbr.get(current_book_full) or full_to_abbr.get(
            FULLNAME_ALIASES.get(current_book_full, ""), None
        )

    matched = False
    for m in _REF_RE.finditer(s):
        matched = True
        book_token = m.group("book")
        sameboek = m.group("sameboek") is not None
        chapter = m.group("chapter")
        verses_raw = m.group("verses")
        # Hervorm verzen: comma-list zonder spaties.
        verses = ",".join(v.strip() for v in verses_raw.split(","))

        if sameboek or not book_token:
            modabbr = last_modabbr
        else:
            modabbr = _resolve_modabbr(book_token, old_to_full, full_to_abbr)
            if modabbr is None:
                # Fallback: behoud oude naam met punt (best-effort, geen crash).
                modabbr = book_token.rstrip(".") + "."
            last_modabbr = modabbr

        if modabbr is None:
            # Geen current_book én geen book_token → kunnen niets zinnigs maken.
            return content

        # Boeknaam alleen herhalen als die wijzigt — modern compact format.
        if modabbr == last_emitted_modabbr:
            parts.append(f"{chapter}:{verses}")
        else:
            parts.append(f"{modabbr} {chapter}:{verses}")
            last_emitted_modabbr = modabbr

    if not matched:
        return content

    return "; ".join(parts)


# Loose-ref detectie binnen kanttekeningen: een 'atom' is een boekafkorting
# (eindigend op `.`) gevolgd door hoofdstuk en verzen. Accepteert zowel
# oude vorm (`Iudic. 13.4`) als moderne vorm (`Jh. 1:1`, `Jh. 1:1-3`). We
# zoeken alleen atomen waarvan het boek bekend is — oud uit
# `bible_book_references.csv` of modern uit `afkortingen.csv` — dat
# voorkomt valse positieven in normale tekst.
# Trailing punt na boeknaam is optioneel: SV gebruikt soms Latijnse genitieven
# zonder afkortings-punt (`Luce 19.8.`, `Esaie 40.3.`). De `all_book_keys`-check
# in `_normalize_loose_refs` filtert false-positives — random hoofdletter-woorden
# gevolgd door cijfers worden gewoon overgeslagen als de key niet bekend is.
_ATOM_WITH_BOOK_RE = re.compile(
    r"(?P<book>(?:\d\s*\.?\s*)?[A-Z][a-zëéüíéëïöóôú]+\.?)"
    r"\s+(?:cap\.\s*)?"
    r"(?P<chapter>\d+)"
    r"\s*[\.,:]\s*"
    r"(?:vers\s*)?"
    r"(?P<verses>\d+(?:\s*[-,]\s*\d+)*)"
)
# Continuation: zelfde boek via `ende`/`en` (oude vorm) of `;` (moderne vorm).
_ENDE_CHAIN_RE = re.compile(
    r"(?:\.?\s+(?:ende|en)|\s*;)\s*(?:cap\.\s*)?"
    r"\d+\s*[\.,:]\s*(?:vers\s*)?\d+(?:\s*[-,]\s*\d+)*"
)
# Continuation: nieuwe boek (na optionele leidende `.` of `;`). Trailing punt
# na boeknaam ook hier optioneel.
_NEW_BOOK_CONTINUATION_RE = re.compile(
    r"(?:\.?\s+|\s*;\s*)(?P<book>(?:\d\s*\.?\s*)?[A-Z][a-zëéüíéëïöóôú]+\.?)"
    r"\s+(?:cap\.\s*)?"
    r"\d+\s*[\.,:]\s*(?:vers\s*)?\d+(?:\s*[-,]\s*\d+)*"
)


def _load_all_book_keys() -> set[str]:
    """Set van genormaliseerde keys voor alle bekende boekafkortingen
    — oud (Iudic.) én modern (Ri., 1Sm., 1Kor.) — én volle namen."""
    keys: set[str] = set(_load_oldabbr_to_fullname().keys())
    full_to_abbr = _load_fullname_to_modabbr()
    for full, abbr in full_to_abbr.items():
        keys.add(_normalize_book_key(abbr))
        keys.add(_normalize_book_key(full))
    return keys


def _normalize_loose_refs(content: str, current_full: str | None,
                          old_to_full: dict[str, str],
                          full_to_abbr: dict[str, str]) -> str:
    """Normaliseer loose bibrefs binnen één kanttekening-stuk content en
    wrap ze in `$...$`.

    Loose = niet gewrapt in `$...$`. Zoekt clusters van atoms waarvan het
    eerste atom een bekende boekafkorting heeft. Een cluster mag verlengd
    worden via `ende`/`en` (zelfde boek) of via een direct volgende nieuwe
    bekende boekafkorting. De cluster-tekst gaat door `_normalize_inner`,
    waarna de output in `$...$` wordt gewrapt zodat regex-consumers ref van
    omliggende kant-tekst kunnen onderscheiden.

    Idempotent: refs die al in `$...$` staan (modern formaat met `:`) worden
    door `_ATOM_WITH_BOOK_RE` niet als loose herkend, dus niet dubbel gewrapt.
    """
    all_book_keys = _load_all_book_keys()
    out: list[str] = []
    pos = 0
    while pos < len(content):
        m = _ATOM_WITH_BOOK_RE.search(content, pos)
        if not m:
            out.append(content[pos:])
            break
        # Sla over als de match binnen een bestaand $...$ blok valt.
        if _is_inside_dollar(content, m.start()):
            out.append(content[pos:m.end()])
            pos = m.end()
            continue
        book = m.group("book").rstrip(".")
        if _normalize_book_key(book) not in all_book_keys:
            # Geen bekende afkorting — sla over en zoek verder.
            out.append(content[pos:m.end()])
            pos = m.end()
            continue

        cluster_start = m.start()
        cluster_end = m.end()
        # Greedy verlengen met chains.
        while True:
            chain_m = _ENDE_CHAIN_RE.match(content, cluster_end)
            if chain_m and not _is_inside_dollar(content, chain_m.start()):
                cluster_end = chain_m.end()
                continue
            new_m = _NEW_BOOK_CONTINUATION_RE.match(content, cluster_end)
            if new_m and not _is_inside_dollar(content, new_m.start()):
                book2 = new_m.group("book").rstrip(".")
                if _normalize_book_key(book2) in all_book_keys:
                    cluster_end = new_m.end()
                    continue
            break

        out.append(content[pos:cluster_start])
        cluster_text = content[cluster_start:cluster_end]
        normalized = _normalize_inner(cluster_text, current_full, old_to_full, full_to_abbr)
        out.append(f"${normalized}$")
        pos = cluster_end
    return "".join(out)


def _is_inside_dollar(text: str, idx: int) -> bool:
    """True als `idx` binnen een `$...$` blok valt."""
    # Tel openings-`$` vóór idx; oneven = binnen blok.
    return text.count("$", 0, idx) % 2 == 1


def find_loose_refs(text: str) -> list[str]:
    """Geef alle loose bibrefs in `text` terug (snippets, niet gewrapt in `$...$`).

    Een 'loose ref' is een sequence die `_ATOM_WITH_BOOK_RE` matcht waarvan
    het boek bekend is in `bible_book_references.csv`, en die niet binnen een
    `$...$` blok valt. Refs die al gewrapt zijn worden overgeslagen.

    Bedoeld voor de validator: na bibref.normalize(...) hoort er geen loose
    ref meer te bestaan in de tekst — als wel, dan is dat een hard issue.
    """
    all_book_keys = _load_all_book_keys()
    found: list[str] = []
    pos = 0
    while pos < len(text):
        m = _ATOM_WITH_BOOK_RE.search(text, pos)
        if not m:
            break
        if _is_inside_dollar(text, m.start()):
            pos = m.end()
            continue
        book = m.group("book").rstrip(".")
        if _normalize_book_key(book) not in all_book_keys:
            pos = m.end()
            continue

        cluster_end = m.end()
        while True:
            chain_m = _ENDE_CHAIN_RE.match(text, cluster_end)
            if chain_m and not _is_inside_dollar(text, chain_m.start()):
                cluster_end = chain_m.end()
                continue
            new_m = _NEW_BOOK_CONTINUATION_RE.match(text, cluster_end)
            if new_m and not _is_inside_dollar(text, new_m.start()):
                book2 = new_m.group("book").rstrip(".")
                if _normalize_book_key(book2) in all_book_keys:
                    cluster_end = new_m.end()
                    continue
            break

        found.append(text[m.start():cluster_end])
        pos = cluster_end
    return found


def normalize(text: str, current_book_code: str | None = None,
              include_kanttekeningen: bool = False) -> str:
    """Vervang elke `$...$` in `text` door moderne notatie.

    `current_book_code` is een 3-letterige code (LUK, MAT, ...). Wordt gebruikt
    als de ref geen boeknaam bevat (`$3:1$` → `$Lk. 3:1$` met current=LUK).

    Met `include_kanttekeningen=True` worden óók loose refs binnen `<...>`
    blokken genormaliseerd én gewrapt in `$...$`, zodat ze net als
    hoofdtekst-refs via één regex te onderscheiden zijn van omliggende
    kant-tekst. Voorkomt handwerk voor SV1657-kanttekeningen die
    `1.Cor. 14. vers 19.` schrijven.
    """
    old_to_full = _load_oldabbr_to_fullname()
    full_to_abbr = _load_fullname_to_modabbr()
    current_full = (
        PROJECT_CODE_TO_FULLNAME.get(current_book_code.upper())
        if current_book_code
        else None
    )

    def _repl(m: re.Match) -> str:
        inner = m.group(1)
        normalized = _normalize_inner(inner, current_full, old_to_full, full_to_abbr)
        return f"${normalized}$"

    result = re.sub(r"\$([^$]+)\$", _repl, text)

    if include_kanttekeningen:
        def _kant_repl(m: re.Match) -> str:
            inner = m.group(1)
            normalized = _normalize_loose_refs(inner, current_full, old_to_full, full_to_abbr)
            return f"<{normalized}>"

        result = re.sub(r"<([^>]+)>", _kant_repl, result)

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("normalize", help="Normaliseer alle $...$ refs in de input.")
    sp.add_argument(
        "--current-book",
        default=None,
        help="3-letterige projectcode (LUK, MAT, ...) voor impliciete refs.",
    )
    sp.add_argument(
        "--include-kanttekeningen",
        action="store_true",
        help="Ook loose refs binnen <...> blokken normaliseren (geen $-wrap).",
    )
    sp.add_argument("text", help="Input-string met $...$ blokken.")

    args = parser.parse_args()
    if args.cmd == "normalize":
        sys.stdout.write(normalize(
            args.text, args.current_book,
            include_kanttekeningen=args.include_kanttekeningen,
        ))
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
