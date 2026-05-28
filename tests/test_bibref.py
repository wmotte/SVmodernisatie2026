"""Golden-tests voor `scripts/bibref.py`.

Borgt de tweetraps CSV-lookup (oldAbbr → fullName → modAbbr) tegen
regressie: een typefout in `refdata/` of de `PROJECT_CODE_TO_FULLNAME`-
mapping zou hier direct opvallen. De cases spiegelen de voorbeeldtabel in
`.agents/skills/sv-bibref/SKILL.md`.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import bibref  # noqa: E402


# (input, current_book_code, verwacht) — hoofdtekst, pure bibref-normalisatie.
HOOFDTEKST_CASES = [
    ("$Iudic. 13.4.$", "LUK", "$Ri. 13:4$"),
    ("$1.Chron. 24.10.$", "LUK", "$1Kr. 24:10$"),
    ("$Exod. 30.7. Levit. 16.17.$", "LUK", "$Ex. 30:7; Lv. 16:17$"),
    ("$Iesa. 30.18. ende 41.9. ende 54.5.$", "LUK", "$Js. 30:18; 41:9; 54:5$"),
    ("$Hebr. 6.13, 17.$", "LUK", "$Hb. 6:13,17$"),
    ("$Psalm 45. vers 7.$", "LUK", "$Ps. 45:7$"),
    ("$Malach. cap. 4. vers 6.$", "LUK", "$Ml. 4:6$"),
]


@pytest.mark.parametrize("text, book, expected", HOOFDTEKST_CASES)
def test_hoofdtekst_normalisatie(text: str, book: str, expected: str) -> None:
    assert bibref.normalize(text, book) == expected


@pytest.mark.parametrize("_, book, modern", HOOFDTEKST_CASES)
def test_idempotent(_: str, book: str, modern: str) -> None:
    # Al-moderne notatie blijft ongewijzigd na nogmaals normaliseren.
    assert bibref.normalize(modern, book) == modern


def test_impliciete_ref_krijgt_huidig_boek() -> None:
    # Bare ref zonder boeknaam erft het huidige boek (modAbbr).
    assert bibref.normalize("$3:1$", "LUK") == "$Lk. 3:1$"


def test_impliciete_ref_range_en_keten() -> None:
    assert bibref.normalize("$3:1-3$", "LUK") == "$Lk. 3:1-3$"
    assert bibref.normalize("$3:1; 5:2$", "LUK") == "$Lk. 3:1; 5:2$"


def test_al_modern_blijft_gelijk() -> None:
    assert bibref.normalize("$Lk. 3:1$", "LUK") == "$Lk. 3:1$"


def test_impliciete_ref_zonder_current_book_blijft_gelijk() -> None:
    # Geen current-book → niets te prefixen; ongewijzigd.
    assert bibref.normalize("$3:1$", None) == "$3:1$"


def test_losse_ref_in_kanttekening_wordt_gewrapt() -> None:
    # Met --include-kanttekeningen worden losse refs binnen <...> in $...$ gezet.
    out = bibref.normalize(
        "<Actor. 24.3. ende 26.25.>", "LUK", include_kanttekeningen=True
    )
    assert out == "<$Hd. 24:3; 26:25$.>"


def test_kanttekening_ref_blijft_los_zonder_flag() -> None:
    # Zonder de flag raakt bibref de losse ref binnen <...> niet aan.
    text = "<Actor. 24.3. ende 26.25.>"
    assert bibref.normalize(text, "LUK") == text
