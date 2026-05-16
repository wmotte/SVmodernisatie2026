"""Consistency-check voor de twee refdata-CSVs.

Voor elke `oldAbbreviation` in `bible_book_references.csv` controleert dit
script of de chain `oldAbbr → fullName(Dutch) → modAbbr` zonder gaten
oplost. Een typo in `afkortingen.csv` (zoals 'Johannnes' i.p.v. 'Johannes')
zou anders pas opvallen wanneer iemand probeert een specifiek bijbelboek
te normaliseren — soms na maanden.

Daarnaast: voor elke 3-letter projectcode in `bibref.PROJECT_CODE_TO_FULLNAME`
checkt het script dat de fullName ook resolved naar een modAbbr.

CLI:
    python scripts/check_refdata.py
    # exit 0 = alles OK; exit 1 = minstens één gat in een chain
"""

import csv
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REFDATA = PROJECT_ROOT / "refdata"

sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from bibref import FULLNAME_ALIASES, PROJECT_CODE_TO_FULLNAME  # noqa: E402


def _load_oldabbr_to_fullname() -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    path = REFDATA / "bible_book_references.csv"
    with path.open(encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if len(row) < 4:
                continue
            old_abbr, _, _, full_name_dutch, _ = row[:5]
            rows.append((old_abbr.strip(), full_name_dutch.strip()))
    return rows


def _load_fullname_to_modabbr() -> dict[str, str]:
    mapping: dict[str, str] = {}
    path = REFDATA / "afkortingen.csv"
    with path.open(encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 2:
                continue
            mapping[row[0].strip()] = row[1].strip()
    return mapping


def _resolve_fullname(full: str, full_to_abbr: dict[str, str]) -> str | None:
    if full in full_to_abbr:
        return full_to_abbr[full]
    alias = FULLNAME_ALIASES.get(full)
    if alias and alias in full_to_abbr:
        return full_to_abbr[alias]
    return None


def main() -> int:
    old_to_full = _load_oldabbr_to_fullname()
    full_to_abbr = _load_fullname_to_modabbr()

    issues: list[str] = []

    seen_full: set[str] = set()
    for old_abbr, full in old_to_full:
        seen_full.add(full)
        modabbr = _resolve_fullname(full, full_to_abbr)
        if modabbr is None:
            issues.append(
                f"  - '{old_abbr}' → fullName='{full}' is niet in afkortingen.csv"
            )

    for code, full in PROJECT_CODE_TO_FULLNAME.items():
        modabbr = _resolve_fullname(full, full_to_abbr)
        if modabbr is None:
            issues.append(
                f"  - projectcode '{code}' → fullName='{full}' is niet in afkortingen.csv"
            )

    unused_full = [f for f in full_to_abbr if f not in seen_full]
    unused_full = [f for f in unused_full if f not in FULLNAME_ALIASES.values()]

    if issues:
        print(f"refdata-check FAIL — {len(issues)} ontbrekende chain(s):")
        for line in issues:
            print(line)
        if unused_full:
            print(f"\n(info: {len(unused_full)} entries in afkortingen.csv worden door geen "
                  f"oldAbbr of projectcode geraakt — niet noodzakelijk fout)")
            for f in unused_full:
                print(f"  - {f}")
        return 1

    print(f"refdata-check OK — {len(old_to_full)} oldAbbr-chains, "
          f"{len(PROJECT_CODE_TO_FULLNAME)} projectcodes, alles resolved.")
    if unused_full:
        print(f"\n(info: {len(unused_full)} entries in afkortingen.csv ongebruikt — "
              f"niet noodzakelijk fout)")
        for f in unused_full:
            print(f"  - {f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
