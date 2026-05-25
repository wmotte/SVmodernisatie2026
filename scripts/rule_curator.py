"""Dry-run curator voor regel- en scaffolding-drift.

Dit script wijzigt geen regelbestanden. Het schrijft alleen een rapport
naar `output/META/rule_curator_report.json` en signaleert:

  * korte/brede stoplist-items;
  * stoplist-items zonder inline motivatie;
  * blacklist-patronen zonder recente hits in output;
  * herhaalde rebuttal-categorieën uit decisions/review-memory.

CLI:
    uv run python scripts/rule_curator.py --book LUK --dry-run
    uv run python scripts/rule_curator.py --all --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from rules_data import ARCHAISM_BLACKLIST  # noqa: E402

DEFAULT_REPORT = PROJECT_ROOT / "output" / "META" / "rule_curator_report.json"
STOPLIST_PATH = PROJECT_ROOT / "scripts" / "stoplist.txt"
DECISIONS_PATH = PROJECT_ROOT / "output" / "META" / "decisions.jsonl"


def _read_stoplist() -> list[dict[str, Any]]:
    if not STOPLIST_PATH.exists():
        return []
    rows = []
    with STOPLIST_PATH.open(encoding="utf-8") as fh:
        for line_no, raw in enumerate(fh, start=1):
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                continue
            item, _, comment = stripped.partition("#")
            token = item.strip()
            if token:
                rows.append({"line": line_no, "token": token, "comment": comment.strip()})
    return rows


def _load_output_text(root: Path, book: str | None) -> str:
    parts: list[str] = []
    for path in sorted(root.glob("*/*.json")):
        if path.parent.name == "META":
            continue
        if book and path.parent.name != book:
            continue
        try:
            with path.open(encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict) or not data.get("verses"):
            continue
        for verse in data.get("verses", []):
            if isinstance(verse, dict):
                parts.append(verse.get("modernized", "") or "")
                notes = verse.get("notes") or []
                if isinstance(notes, str):
                    parts.append(notes)
                elif isinstance(notes, list):
                    parts.extend(str(n) for n in notes)
        for section_name in ("introduction", "epilogue"):
            section = data.get(section_name)
            if isinstance(section, dict):
                parts.append(section.get("modernized", "") or "")
            elif isinstance(section, str):
                parts.append(section)
    return "\n".join(parts)


def _scan_blacklist(text: str) -> list[dict[str, Any]]:
    findings = []
    for pattern in ARCHAISM_BLACKLIST:
        try:
            count = len(re.findall(pattern, text, flags=re.IGNORECASE))
        except re.error as exc:
            findings.append({"pattern": pattern, "issue": f"regex-error: {exc}"})
            continue
        if count == 0:
            findings.append({"pattern": pattern, "issue": "geen recente hits in gekozen output-scope"})
    return findings


def _load_decisions(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records = []
    with path.open(encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict):
                records.append(record)
    return records


def _repeated_rebuttals(records: list[dict[str, Any]], book: str | None) -> list[dict[str, Any]]:
    counter: Counter[tuple[str, str]] = Counter()
    examples: dict[tuple[str, str], list[str]] = defaultdict(list)
    for record in records:
        if book and record.get("book") != book:
            continue
        status = str(record.get("status") or "")
        if "rebut" not in status:
            continue
        key = (str(record.get("category") or "uncategorized"), str(record.get("rule_reference") or ""))
        counter[key] += 1
        if len(examples[key]) < 5:
            examples[key].append(str(record.get("id") or record.get("source")))
    out = []
    for (category, rule_reference), count in counter.most_common():
        if count < 3:
            continue
        out.append({
            "category": category,
            "rule_reference": rule_reference,
            "count": count,
            "examples": examples[(category, rule_reference)],
            "suggestion": "Overweeg een expliciete uitzondering of scanner-aanscherping als deze rebuttals inhoudelijk hetzelfde zijn.",
        })
    return out


def build_report(root: Path, book: str | None) -> dict[str, Any]:
    stoplist = _read_stoplist()
    broad_stoplist = [
        {
            "line": row["line"],
            "token": row["token"],
            "reason": "kort of breed token; kan echte archaïsmen maskeren",
        }
        for row in stoplist
        if len(row["token"]) <= 3 or row["token"].lower() in {"dat", "die", "den", "der", "des", "men", "wel"}
    ]
    undocumented_stoplist = [
        {"line": row["line"], "token": row["token"], "reason": "geen inline motivatie/commentaar"}
        for row in stoplist
        if not row["comment"]
    ]
    output_text = _load_output_text(root, book)
    decisions = _load_decisions(DECISIONS_PATH)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": {"root": str(root), "book": book or "ALL"},
        "mode": "dry-run",
        "summary": {
            "stoplist_items": len(stoplist),
            "broad_stoplist_items": len(broad_stoplist),
            "undocumented_stoplist_items": len(undocumented_stoplist),
            "blacklist_patterns_without_hits": len(_scan_blacklist(output_text)),
            "repeated_rebuttal_groups": len(_repeated_rebuttals(decisions, book)),
        },
        "findings": {
            "broad_stoplist_items": broad_stoplist,
            "undocumented_stoplist_items": undocumented_stoplist,
            "blacklist_patterns_without_recent_hits": _scan_blacklist(output_text),
            "repeated_rebuttals": _repeated_rebuttals(decisions, book),
        },
        "guardrail": "Rapportage-only; geen regelbestand of output is aangepast.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--book", help="Beperk analyse tot één boekcode.")
    scope.add_argument("--all", action="store_true", help="Analyseer alle output.")
    parser.add_argument("--root", default="output", help="Output-root.")
    parser.add_argument("--out", default=str(DEFAULT_REPORT), help="Rapportpad.")
    parser.add_argument("--dry-run", action="store_true", help="Verplicht: curator schrijft alleen rapport.")
    args = parser.parse_args()
    if not args.dry_run:
        raise SystemExit("FOUT: fase-1 curator ondersteunt alleen --dry-run.")

    report = build_report(Path(args.root), args.book)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(json.dumps({"ok": True, "out": str(out), "summary": report["summary"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
