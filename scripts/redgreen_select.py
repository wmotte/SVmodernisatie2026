#!/usr/bin/env python3
"""Worst-first boekenpaar-selectie voor de red-green debat-skill.

Kiest twee **volledig afgeronde** NT-boeken die het meest gebaat zijn bij
een nieuwe debatronde. Ranking-signalen (hoog = eerst aan de beurt):

  * open/reopened issues in `output/<BOEK>/review.*.json`   (gewicht 5)
  * review-dekkingsgat: hoofdstukken zónder `review.<H>.json` (gewicht 3)
  * historisch aantal issues (contentie-proxy)               (gewicht 1)
  * debat-rotatie: vaker gedebatteerd → lagere prioriteit     (gewicht -4)

Alleen 100%-boeken (elke bronhoofdstuk aanwezig in output met alle verzen
`modernized` niet-leeg) doen mee — net als sv-meta-review pending overslaat.

Output: compacte JSON naar stdout, bv.
    {"pair": ["MAT", "MRK"], "round_no": 1, "reason": "...", "scores": {...}}

Gebruik:
    uv run python scripts/redgreen_select.py
    uv run python scripts/redgreen_select.py --state output/META/debate/state.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INPUT_DIR = REPO / "input.sv"
OUTPUT_DIR = REPO / "output"
DEFAULT_STATE = OUTPUT_DIR / "META" / "debate" / "state.json"

# Canonieke NT-volgorde (boekcodes, zoals progress_stats.py).
NT_BOOKS = [
    "MAT", "MRK", "LUK", "JHN", "ACT", "ROM", "1CO", "2CO", "GAL", "EPH",
    "PHP", "COL", "1TH", "2TH", "1TI", "2TI", "TIT", "PHM", "HEB", "JAS",
    "1PE", "2PE", "1JN", "2JN", "3JN", "JUD", "REV",
]

W_OPEN = 5
W_GAP = 3
W_TOTAL = 1
W_DEBATED = -4


def _read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _input_chapters(book: str) -> list[int]:
    d = INPUT_DIR / book
    if not d.is_dir():
        return []
    chs = []
    for f in d.glob(f"{book}.*.json"):
        try:
            chs.append(int(f.stem.split(".")[-1]))
        except ValueError:
            continue
    return sorted(chs)


def _book_complete(book: str) -> bool:
    """Boek is af als elk bronhoofdstuk een output heeft met alle verzen
    `modernized` niet-leeg."""
    chapters = _input_chapters(book)
    if not chapters:
        return False
    for ch in chapters:
        out = _read_json(OUTPUT_DIR / book / f"{book}.{ch}.json")
        if not out:
            return False
        verses = out.get("verses") or []
        if not verses:
            return False
        for v in verses:
            if not (v.get("modernized") or "").strip():
                return False
    return True


def _book_metrics(book: str) -> dict:
    chapters = _input_chapters(book)
    total_ch = len(chapters)
    reviewed = set()
    open_issues = 0
    total_issues = 0
    for ch in chapters:
        rv = _read_json(OUTPUT_DIR / book / f"review.{ch}.json")
        if rv is None:
            continue
        reviewed.add(ch)
        issues = rv.get("issues") or []
        total_issues += len(issues)
        for it in issues:
            if it.get("status") in ("open", "reopened"):
                open_issues += 1
    gap = total_ch - len(reviewed)
    return {
        "chapters": total_ch,
        "reviewed": len(reviewed),
        "review_gap": gap,
        "open_issues": open_issues,
        "total_issues": total_issues,
    }


def _score(metrics: dict, debated: int) -> int:
    return (
        W_OPEN * metrics["open_issues"]
        + W_GAP * metrics["review_gap"]
        + W_TOTAL * metrics["total_issues"]
        + W_DEBATED * debated
    )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--state", default=str(DEFAULT_STATE),
                    help="Pad naar debate/state.json (rotatie + ronde-cursor).")
    args = ap.parse_args()

    state = _read_json(Path(args.state)) or {}
    debate_count = state.get("debate_count", {})
    last_pair = (state.get("pairs") or [[]])[-1] if state.get("pairs") else []
    rounds_done = int(state.get("rounds_done", 0))

    ranked = []
    for book in NT_BOOKS:
        if not _book_complete(book):
            continue
        m = _book_metrics(book)
        s = _score(m, int(debate_count.get(book, 0)))
        ranked.append((s, book, m))

    # Hoogste score eerst; tie-break op canonieke volgorde (stabiel).
    ranked.sort(key=lambda r: (-r[0], NT_BOOKS.index(r[1])))

    if len(ranked) < 2:
        print(json.dumps({"error": "fewer than 2 completed books available",
                          "available": [b for _, b, _ in ranked]}))
        raise SystemExit(1)

    # Kies top-2; vermijd exact hetzelfde paar als de vorige ronde.
    pair = [ranked[0][1], ranked[1][1]]
    if sorted(pair) == sorted(last_pair) and len(ranked) >= 3:
        pair = [ranked[0][1], ranked[2][1]]

    chosen = {b: m for _, b, m in ranked if b in pair}
    reason = (
        f"worst-first: {pair[0]} (open={chosen[pair[0]]['open_issues']}, "
        f"gap={chosen[pair[0]]['review_gap']}, issues={chosen[pair[0]]['total_issues']}) "
        f"+ {pair[1]} (open={chosen[pair[1]]['open_issues']}, "
        f"gap={chosen[pair[1]]['review_gap']}, issues={chosen[pair[1]]['total_issues']})"
    )
    out = {
        "pair": pair,
        "round_no": rounds_done + 1,
        "reason": reason,
        "scores": {b: s for s, b, _ in ranked[:6]},
    }
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
