"""Scraper voor de Herziene Statenvertaling (herzienestatenvertaling.nl).

Spiegelt scripts/fetch_sv2027.py voor HSV. Schrijft hsv/<BOEK>/<BOEK>.<H>.json
met dezelfde structuur die compare_hsv.py verwacht.

Mappings die we toepassen tijdens parsing:
- <span class="add">…</span>      -> [ … ]   (translator-additie, zoals SV1657)
- <span class="f">…</span>        -> <HSV: lemma — note>
- <span class="x">…</span>        -> $Ref1; Ref2$ (bijbel-cross-refs)
- <span class="x xType2">…</span> -> <HSV-aant: …>   (HSV-editoriale aantekening)

Sectie-koppen (<p class="s">) en het hoofdstuknummer (<h2 class="c">) worden
overgeslagen — wij hebben in onze JSON geen sectie-headers en SV2027 doet het
ook niet, dus consistentie.
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup, Comment, NavigableString, Tag

BOOK_TO_HSV_SLUG = {
    "LUK": "lukas",
    "MRK": "markus",
    "PHM": "filemon",
    "ROM": "romeinen",
}


def hsv_url(book: str, chapter: int) -> str:
    slug = BOOK_TO_HSV_SLUG.get(book)
    if not slug:
        raise ValueError(
            f"Geen HSV-slug bekend voor boek {book!r}. Voeg toe aan BOOK_TO_HSV_SLUG."
        )
    return f"https://herzienestatenvertaling.nl/teksten/{slug}/{chapter}"


def fetch_html(url: str, timeout: int = 15) -> str | None:
    headers = {"User-Agent": "Mozilla/5.0 (SVmodernisatie2026 fetch_hsv.py)"}
    try:
        r = requests.get(url, headers=headers, timeout=timeout)
        if r.status_code != 200:
            print(f"HTTP {r.status_code} for {url}", file=sys.stderr)
            return None
        return r.text
    except requests.RequestException as exc:
        print(f"Request error for {url}: {exc}", file=sys.stderr)
        return None


def parse_verse_paragraph(p_tag: Tag) -> tuple[int | None, str]:
    """Parse één <p class="p"> uit de HSV-pagina; retourneer (verse_number, text)."""

    v_num: int | None = None
    parts: list[str] = []

    for elem in p_tag.contents:
        if isinstance(elem, Comment):
            continue
        if isinstance(elem, NavigableString):
            # Stray witruimte tussen tags — laat staan voor leesbaarheid
            s = str(elem)
            if s.strip() == "":
                if s and (not parts or not parts[-1].endswith(" ")):
                    parts.append(" ")
            else:
                parts.append(s)
            continue
        if not isinstance(elem, Tag):
            continue

        if elem.name == "i":
            # FontAwesome icoon (preCommentNote / preCommentRef) — overslaan
            continue

        cls = elem.get("class") or []

        if "verse-span" in cls:
            # Mogelijk de versnummer-wrapper of de gewone tekst-wrapper.
            v_marker = elem.find("span", class_="v")
            if v_marker is not None:
                if v_num is None:
                    try:
                        v_num = int(v_marker.get_text().strip())
                    except ValueError:
                        pass
                continue
            parts.append(elem.get_text())
            continue

        if "add" in cls:
            inner = elem.get_text().strip()
            if inner:
                parts.append(f" [{inner}] ")
            continue

        if "f" in cls:
            fq = elem.find("span", class_="fq")
            ft = elem.find("span", class_="ft")
            fq_text = fq.get_text().strip() if fq else ""
            ft_text = ft.get_text().strip() if ft else ""
            ft_text = ft_text.lstrip("-").strip()
            if fq_text and ft_text:
                parts.append(f" <HSV: {fq_text} — {ft_text}> ")
            elif ft_text:
                parts.append(f" <HSV: {ft_text}> ")
            elif fq_text:
                parts.append(f" <HSV: {fq_text}> ")
            continue

        if "x" in cls:
            if "xType2" in cls:
                xt = elem.find("span", class_="xt")
                ann = (xt.get_text(" ", strip=True) if xt else elem.get_text(" ", strip=True))
                if ann:
                    parts.append(f" <HSV-aant: {ann}> ")
                continue
            anchors = elem.find_all("a")
            refs = [a.get_text().strip() for a in anchors if a.get_text().strip()]
            if refs:
                parts.append(f" ${'; '.join(refs)}$ ")
            continue

        # Fallback: andere onverwachte tag — pak gewone tekst
        text = elem.get_text()
        if text:
            parts.append(text)

    raw = "".join(parts)
    cleaned = re.sub(r"\s+", " ", raw).strip()
    return v_num, cleaned


def fetch_hsv(book: str, chapter: int, debug: bool = False) -> dict | None:
    url = hsv_url(book, chapter)
    print(f"Fetching {url}…")
    html = fetch_html(url)
    if not html:
        return None

    if debug:
        debug_path = f"/tmp/hsv_debug_{book}_{chapter}.html"
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  (raw HTML opgeslagen: {debug_path})")

    soup = BeautifulSoup(html, "html.parser")
    container = soup.find("div", class_="bible-content")
    if container is None:
        print(f"Error: <div class='bible-content'> niet gevonden op {url}", file=sys.stderr)
        return None

    verses: dict[int, str] = {}
    for p in container.find_all("p", class_="p", recursive=True):
        v_num, text = parse_verse_paragraph(p)
        if v_num is None or not text:
            continue
        if v_num in verses:
            verses[v_num] += " " + text
        else:
            verses[v_num] = text

    if not verses:
        print(f"Error: geen verzen geëxtraheerd uit {url}", file=sys.stderr)
        return None

    data = {
        "book": book,
        "chapter": int(chapter),
        "source_url": url,
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "verses": [
            {"verse_number": v, "modernized": verses[v]}
            for v in sorted(verses.keys())
        ],
    }
    return data


def write_output(data: dict, book: str, chapter: int) -> str:
    out_dir = f"hsv/{book}"
    os.makedirs(out_dir, exist_ok=True)
    out_path = f"{out_dir}/{book}.{chapter}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return out_path


def chapter_range_for_book(book: str) -> list[int]:
    if book == "LUK":
        return list(range(1, 25))
    if book == "MRK":
        return list(range(1, 17))
    if book == "ROM":
        return list(range(1, 17))
    raise ValueError(f"Geen hoofdstuk-range bekend voor {book}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Scrape Herziene Statenvertaling per hoofdstuk.")
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
        result = fetch_hsv(args.book, ch, debug=args.debug)
        if result is None:
            failures.append(ch)
            continue
        out_path = write_output(result, args.book, ch)
        print(f"  {len(result['verses'])} verzen → {out_path}")
        if i < len(chapters) - 1:
            time.sleep(args.sleep)

    if failures:
        print(f"\nMislukt voor hoofdstukken: {failures}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
