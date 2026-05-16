"""Lint alle output op archaïsmen — retroactief tegen de huidige
ARCHAISM_BLACKLIST uit `validate.py`. Vangt verzen die geldig waren
onder een eerdere blacklist maar niet onder de huidige.

Wanneer gebruiken: na elke uitbreiding van de blacklist (in
`validate.py`). Vanaf dat moment kunnen al-gemoderniseerde verzen die
het nieuwe archaïsme bevatten her-modernisatie nodig hebben — deze
lint laat zien welke.

Hoofdtekst en kanttekening-inhoud worden apart gescand. Beide tellen
als hard issue: kanttekeningen worden in dit project ook
gemoderniseerd (geen citaten van het SV-origineel), dus archaïsmen
horen er ook niet in.

CLI:
    uv run python scripts/lint_archaismen.py lint --output output/LUK/LUK.1.json
    uv run python scripts/lint_archaismen.py lint --root output/

Exit-code 0 = schoon, 1 = minstens één archaïsme.
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate import ARCHAISM_BLACKLIST  # noqa: E402


def _split_hoofdtekst_kanttekeningen(text: str) -> tuple[str, str]:
    """Split modernized text in hoofdtekst (zonder <...>) en kant-inhoud."""
    kant_inner = " ".join(re.findall(r"<([^>]+)>", text))
    hoofdtekst = re.sub(r"<[^>]+>", " ", text)
    return hoofdtekst, kant_inner


def _scan(text: str) -> list[dict]:
    """Geef alle archaïsme-matches in deze tekst."""
    matches: list[dict] = []
    for pattern in ARCHAISM_BLACKLIST:
        for m in re.finditer(pattern, text, flags=re.IGNORECASE):
            matches.append({"pattern": pattern, "match": m.group(0)})
    return matches


def _scan_verse(verse: dict) -> dict:
    mod = verse.get("modernized", "")
    hoofdtekst, kant = _split_hoofdtekst_kanttekeningen(mod)
    return {
        "verse_number": verse.get("verse_number"),
        "hoofdtekst": _scan(hoofdtekst),
        "kanttekeningen": _scan(kant),
    }


def _scan_section(name: str, section: object) -> dict:
    """Scan introduction/epilogue. Section kan dict of str zijn."""
    if isinstance(section, dict):
        text = section.get("modernized", "") or ""
    elif isinstance(section, str):
        text = section
    else:
        text = ""
    return {"section": name, "matches": _scan(text)}


def _scan_file(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)

    verse_results = []
    for v in data.get("verses", []):
        r = _scan_verse(v)
        if r["hoofdtekst"] or r["kanttekeningen"]:
            verse_results.append(r)

    section_results = []
    for sec_name in ("introduction", "epilogue"):
        if data.get(sec_name):
            sr = _scan_section(sec_name, data[sec_name])
            if sr["matches"]:
                section_results.append(sr)

    return {
        "file": str(path),
        "book": data.get("book"),
        "chapter": data.get("chapter"),
        "verses_with_issues": verse_results,
        "sections_with_issues": section_results,
    }


def cmd_lint(args: argparse.Namespace) -> int:
    if args.output:
        files = [Path(args.output)]
    elif args.root:
        files = sorted(Path(args.root).rglob("*.json"))
    else:
        print(json.dumps({"error": "geef --output of --root"}), file=sys.stderr)
        return 2

    results = []
    n_issues = 0
    n_scanned = 0
    for fp in files:
        if not fp.exists():
            continue
        n_scanned += 1
        r = _scan_file(fp)
        if r["verses_with_issues"] or r["sections_with_issues"]:
            n_issues += sum(
                len(v["hoofdtekst"]) + len(v["kanttekeningen"])
                for v in r["verses_with_issues"]
            )
            n_issues += sum(len(s["matches"]) for s in r["sections_with_issues"])
            results.append(r)

    if args.terse:
        if n_issues == 0:
            print(f"archaismen 0 (scanned {n_scanned} files)")
        else:
            lines = [f"archaismen {n_issues} in {len(results)}/{n_scanned} files"]
            for r in results:
                book = r["book"]
                chapter = r["chapter"]
                parts = []
                for v in r["verses_with_issues"]:
                    words = sorted({m["match"] for m in v["hoofdtekst"] + v["kanttekeningen"]})
                    parts.append(f"v{v['verse_number']}:[{','.join(words)}]")
                for s in r["sections_with_issues"]:
                    words = sorted({m["match"] for m in s["matches"]})
                    parts.append(f"{s['section']}:[{','.join(words)}]")
                lines.append(f"{book} {chapter}: " + " ".join(parts))
            print("\n".join(lines))
        return 0 if n_issues == 0 else 1

    summary = {
        "blacklist_size": len(ARCHAISM_BLACKLIST),
        "files_scanned": n_scanned,
        "files_with_issues": len(results),
        "total_archaismen_found": n_issues,
        "details": results,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if n_issues == 0 else 1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser(
        "lint",
        help="Scan output JSON('s) op archaïsmen tegen huidige ARCHAISM_BLACKLIST.",
    )
    sp.add_argument("--output", default=None, help="Pad naar één output JSON.")
    sp.add_argument("--root", default=None, help="Directory recursief scannen.")
    sp.add_argument("--terse", action="store_true",
                    help="Compacte tekstuele output ipv. JSON.")
    sp.set_defaults(func=cmd_lint)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
