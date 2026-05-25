"""Scraper voor de GBS-editie van de Statenvertaling met kanttekeningen
(statenvertaling.nl, Gereformeerde Bijbelstichting).

Spiegelt scripts/fetch_hsv.py. Schrijft gbs/<BOEK>/<BOEK>.<H>.json met de
verstekst (kanttekening-markers als ⟦K⟧) en een aparte kanttekeningen-lijst.

Bron-HTML (tekst.php?bb=..&hf=..&ind=1) — relevante rijen in <table class='tekst'>:
- td.tekstinlhfdstk  -> hoofdstuk-inhoudsopgave (introduction-string)
- td.tekstparagr     -> sectiekop ("Inleiding", …) — overslaan
- td.tekstbreed      -> verstekst: <a name='versN'></a>N <tekst met <sup>K</sup>>
- td.kanttonder      -> kanttekening: <b>K</b> notetekst (verwijs-icoon strippen)
- tr[id^='tr']       -> uitgeklapte verwijstekst-popups (display:none) — overslaan

Kanttekening-nummering is doorlopend per hoofdstuk; <sup>K</sup> in de verstekst
verwijst naar kanttekening K.
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup, NavigableString, Tag

# OSIS-boekcode -> statenvertaling.nl bb-nummer. Minimaal LUK (=42); uitbreidbaar.
BOOK_TO_GBS_BB = {
    "LUK": 42,
}

# Aantal hoofdstukken per NT-boek (zelfde tabel als fetch_hsv.py).
BOOK_CHAPTER_COUNT = {
    "MAT": 28, "MRK": 16, "LUK": 24, "JHN": 21, "ACT": 28,
    "ROM": 16, "1CO": 16, "2CO": 13, "GAL": 6, "EPH": 6,
    "PHP": 4, "COL": 4, "1TH": 5, "2TH": 3, "1TI": 6,
    "2TI": 4, "TIT": 3, "PHM": 1, "HEB": 13, "JAS": 5,
    "1PE": 5, "2PE": 3, "1JN": 5, "2JN": 1, "3JN": 1,
    "JUD": 1, "REV": 22,
}


def gbs_url(book: str, chapter: int) -> str:
    bb = BOOK_TO_GBS_BB.get(book)
    if bb is None:
        raise ValueError(
            f"Geen GBS bb-nummer bekend voor boek {book!r}. Voeg toe aan BOOK_TO_GBS_BB."
        )
    return f"https://statenvertaling.nl/tekst.php?bb={bb}&hf={chapter}&ind=1"


def fetch_html(url: str, timeout: int = 15) -> str | None:
    headers = {"User-Agent": "Mozilla/5.0 (SVmodernisatie2026 fetch_gbs.py)"}
    try:
        r = requests.get(url, headers=headers, timeout=timeout)
        if r.status_code != 200:
            print(f"HTTP {r.status_code} for {url}", file=sys.stderr)
            return None
        r.encoding = r.apparent_encoding or "utf-8"
        return r.text
    except requests.RequestException as exc:
        print(f"Request error for {url}: {exc}", file=sys.stderr)
        return None


def _verse_text(td: Tag) -> str:
    """Bouw verstekst uit een td.tekstbreed; <sup>K</sup> -> ⟦K⟧, strip <a name>."""
    parts: list[str] = []
    for elem in td.contents:
        if isinstance(elem, NavigableString):
            parts.append(str(elem))
            continue
        if not isinstance(elem, Tag):
            continue
        if elem.name == "a" and elem.get("name"):
            continue  # <a name='versN'></a> anker
        if elem.name == "sup":
            num = elem.get_text(strip=True)
            parts.append(f"⟦{num}⟧")
            continue
        parts.append(elem.get_text())
    raw = "".join(parts)
    # Strip leidend versnummer ("1 NADEMAAL …" -> "NADEMAAL …").
    raw = re.sub(r"^\s*\d+\s+", "", raw)
    return re.sub(r"\s+", " ", raw).strip()


def _note_text(td: Tag) -> tuple[str | None, str, str]:
    """Parse een td.kanttonder; retourneer (label, kind, notetekst).

    GBS gebruikt twee marker-soorten: cijfers (kanttekeningen, verklarend) en
    letters (verwijzingen, bijbel-cross-refs). Het label staat in <b>…</b>.
    """
    # Verwijder verwijs-icoon-anchors (javascript:fverwijs(..)) volledig.
    for a in td.find_all("a", href=True):
        if "fverwijs" in a["href"]:
            a.decompose()
    b = td.find("b")
    label: str | None = None
    if b is not None:
        label = b.get_text(strip=True)
        b.extract()
    text = re.sub(r"\s+", " ", td.get_text()).strip()
    kind = "verwijzing" if (label and label.isalpha()) else "kanttekening"
    return label, kind, text


def fetch_gbs(book: str, chapter: int, debug: bool = False) -> dict | None:
    url = gbs_url(book, chapter)
    print(f"Fetching {url}…")
    html = fetch_html(url)
    if not html:
        return None

    if debug:
        debug_path = f"/tmp/gbs_debug_{book}_{chapter}.html"
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  (raw HTML opgeslagen: {debug_path})")

    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", class_="tekst")
    if table is None:
        print(f"Error: <table class='tekst'> niet gevonden op {url}", file=sys.stderr)
        return None

    introduction = ""
    verses: list[dict] = []
    current: dict | None = None

    for tr in table.find_all("tr", recursive=False):
        # Sla uitgeklapte verwijstekst-popups over (tr id='trN' display:none).
        if tr.get("id", "").startswith("tr"):
            continue
        cells = tr.find_all("td", recursive=False)
        if not cells:
            continue

        first_cls = cells[0].get("class") or []

        if "tekstinlhfdstk" in first_cls:
            introduction = re.sub(r"\s+", " ", cells[0].get_text()).strip()
            continue
        if "tekstparagr" in first_cls:
            continue  # sectiekop
        if "tekstbreed" in first_cls:
            text = _verse_text(cells[0])
            if not text:
                continue  # lege spacer-rij (&nbsp;)
            current = {"verse_number": None, "text": text, "kanttekeningen": []}
            # Versnummer uit <a name='versN'>.
            anchor = cells[0].find("a", attrs={"name": True})
            if anchor:
                m = re.match(r"vers(\d+)", anchor["name"])
                if m:
                    current["verse_number"] = int(m.group(1))
            verses.append(current)
            continue
        # Kanttekening-rij: td.tussenonder (leeg) + td.kanttonder.
        note_cell = next((c for c in cells if "kanttonder" in (c.get("class") or [])), None)
        if note_cell is not None and current is not None:
            label, kind, text = _note_text(note_cell)
            if text:
                current["kanttekeningen"].append({"label": label, "kind": kind, "text": text})

    verses = [v for v in verses if v["verse_number"] is not None]
    if not verses:
        print(f"Error: geen verzen geëxtraheerd uit {url}", file=sys.stderr)
        return None

    return {
        "book": book,
        "chapter": int(chapter),
        "source_url": url,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "introduction": introduction,
        "verses": verses,
    }


def write_output(data: dict, book: str, chapter: int) -> str:
    out_dir = f"gbs/{book}"
    os.makedirs(out_dir, exist_ok=True)
    out_path = f"{out_dir}/{book}.{chapter}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return out_path


def chapter_range_for_book(book: str) -> list[int]:
    n = BOOK_CHAPTER_COUNT.get(book)
    if n is None:
        raise ValueError(f"Geen hoofdstuk-range bekend voor {book}")
    return list(range(1, n + 1))


def main() -> int:
    parser = argparse.ArgumentParser(description="Scrape GBS-Statenvertaling met kanttekeningen per hoofdstuk.")
    parser.add_argument("book", nargs="?", default="LUK")
    parser.add_argument("chapter", nargs="?", default=None,
                        help="Specifiek hoofdstuk; leeg = alle hoofdstukken van het boek.")
    parser.add_argument("--debug", action="store_true",
                        help="Schrijf raw HTML naar /tmp/ bij parsing.")
    parser.add_argument("--sleep", type=float, default=1.0,
                        help="Sleep tussen requests (seconden).")
    args = parser.parse_args()

    chapters = [int(args.chapter)] if args.chapter else chapter_range_for_book(args.book)

    failures: list[int] = []
    for i, ch in enumerate(chapters):
        result = fetch_gbs(args.book, ch, debug=args.debug)
        if result is None:
            failures.append(ch)
            continue
        out_path = write_output(result, args.book, ch)
        n_notes = sum(len(v["kanttekeningen"]) for v in result["verses"])
        print(f"  {len(result['verses'])} verzen, {n_notes} kanttekeningen → {out_path}")
        if i < len(chapters) - 1:
            time.sleep(args.sleep)

    if failures:
        print(f"\nMislukt voor hoofdstukken: {failures}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
