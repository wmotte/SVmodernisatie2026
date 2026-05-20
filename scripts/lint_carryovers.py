"""Carry-over linter — vind woorden die letterlijk ongewijzigd door­lopen
van SV-origineel naar moderne tekst.

Doel: borderline-archaïsmen vangen die de validator-blacklist mist.
Voorbeeld: "Doch" stond niet op de blacklist en passeerde stilletjes;
deze lint had het bij LUK 1:1 al gerapporteerd. Dit is een **lint-tool**,
geen hard-validatie — output is een ranglijst die menselijk oordeel
vraagt: échte archaïsmen → naar de blacklist + archaïsme-tabel; legitieme
carry-overs (eigennamen, theologische termen) → naar de stoplist of
laat staan.

Methode:
1. Tokenize originele tekst + moderne tekst (>= 4 tekens, alfabetisch,
   markup gestript).
2. Vind tokens die in beide voorkomen (case-insensitive).
3. Filter via STOPLIST (gewone NL woorden, eigennamen, theologische
   termen die terecht ongewijzigd zijn).
4. Aggregeer over de gevraagde verzen, rangschik op frequentie.

Werkrichtlijn: run dit ná een batch-modernisatie. Top-N candidates
zijn geen fouten maar gespreksstof: per woord een keuze maken.

CLI:
    python scripts/lint_carryovers.py lint --output output/LUK/LUK.1.json
    python scripts/lint_carryovers.py lint --output output/LUK/LUK.1.json --verses 1,2,3
    python scripts/lint_carryovers.py lint --output output/LUK/LUK.1.json --top 10
"""

import argparse
import json
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from rules_data import STOPLIST
_TOKEN_RE = re.compile(r"[A-Za-zëéüïöäÀ-ÿ']+")


def tokens(text: str) -> list[str]:
    """Lowercase content-tokens >= 4 tekens, met markup gestript."""
    cleaned = re.sub(r"\$[^$]+\$", " ", text)              # strip $bibrefs$
    cleaned = re.sub(r"\[([^\]]+)\]", r"\1", cleaned)       # houd [SV-toevoegingen] inhoud
    cleaned = re.sub(r"[<>]", " ", cleaned)                 # strip kant-haken (houd inhoud)
    return [t.lower() for t in _TOKEN_RE.findall(cleaned) if len(t) >= 4]


def _load_dynamic_stoplist() -> set[str]:
    """Laad alle unieke modernisatie-tokens uit verses.db."""
    db_path = PROJECT_ROOT / "memory" / "verses.db"
    if not db_path.exists():
        return set()
    try:
        conn = sqlite3.connect(str(db_path), timeout=5.0)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='verses'")
        if not cursor.fetchone():
            conn.close()
            return set()
        cursor.execute("SELECT modernisatie FROM verses")
        rows = cursor.fetchall()
        conn.close()
        
        dynamic_words = set()
        for (text,) in rows:
            dynamic_words.update(tokens(text))
        return dynamic_words
    except Exception as e:
        print(f"Waarschuwing: kon dynamische stoplijst niet laden: {e}", file=sys.stderr)
        return set()


def find_carryovers(orig: str, mod: str) -> set[str]:
    """Tokens die zowel in origineel als modern voorkomen (case-insensitive)."""
    return set(tokens(orig)) & set(tokens(mod))


def cmd_lint(args: argparse.Namespace) -> int:
    out_path = Path(args.output)
    if not out_path.exists():
        print(json.dumps({"error": f"output niet gevonden: {out_path}"}))
        return 2

    with out_path.open(encoding="utf-8") as f:
        data = json.load(f)

    target = None
    if args.verses:
        target = {int(v) for v in args.verses.split(",")}

    active_stoplist = set(STOPLIST) | _load_dynamic_stoplist()

    counter: Counter[str] = Counter()
    where: dict[str, set[int]] = {}
    n_checked = 0

    for v in data.get("verses", []):
        vn = v["verse_number"]
        if target is not None and vn not in target:
            continue
        n_checked += 1
        carries = find_carryovers(v.get("original", ""), v.get("modernized", ""))
        carries -= active_stoplist
        for w in carries:
            counter[w] += 1
            where.setdefault(w, set()).add(vn)

    items = [
        (w, c) for w, c in sorted(counter.items(), key=lambda x: (-x[1], x[0]))
        if c >= args.min_occurrences
    ]
    if args.top:
        items = items[: args.top]

    if args.terse:
        if not items:
            print(f"lint 0 candidates ({n_checked} verses)")
        else:
            parts = []
            for w, _ in items:
                vs = ",".join(f"v{v}" for v in sorted(where[w]))
                parts.append(f"{w}({vs})")
            print(f"lint {len(items)} candidates: " + " ".join(parts))
        return 0

    result = {
        "checked_verses": n_checked,
        "stoplist_size": len(active_stoplist),
        "static_stoplist_size": len(STOPLIST),
        "candidates": [
            {"word": w, "occurrences": c, "verses": sorted(where[w])}
            for w, c in items
        ],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    # Lint-tool — geen hard-fail. Exit 0 zelfs bij candidates; exit 1
    # alleen bij IO-fout (hierboven al).
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("lint", help="Vind carry-over woorden in modernisatie.")
    sp.add_argument("--output", required=True,
                    help="Pad naar output/<BOEK>/<BOEK>.<H>.json")
    sp.add_argument("--verses", default=None,
                    help="Komma-gescheiden vers-nummers (default: alle in output)")
    sp.add_argument("--min-occurrences", type=int, default=1,
                    help="Toon alleen woorden met >= N occurrences (default 1)")
    sp.add_argument("--top", type=int, default=30,
                    help="Toon top-N candidates (default 30)")
    sp.add_argument("--terse", action="store_true",
                    help="Compacte tekstuele output ipv. JSON.")
    sp.set_defaults(func=cmd_lint)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
