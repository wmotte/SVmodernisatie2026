"""Extraheer expliciete review-beslissingen naar JSONL.

Schrijft standaard `output/META/decisions.jsonl`. De input blijft
ongewijzigd. Beslissingen komen uit:

  * `output/<BOEK>/review.<H>.json` issues met status/rebuttal/proposed_fix;
  * optioneel uit output-verse `notes` als adviserend note-record.

CLI:
    uv run python scripts/extract_decisions.py --root output
    uv run python scripts/extract_decisions.py --root output --book LUK
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = PROJECT_ROOT / "output" / "META" / "decisions.jsonl"


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        with path.open(encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def _status_kind(status: str, has_rebuttal: bool = False) -> str:
    s = (status or "").lower()
    if has_rebuttal or "rebut" in s:
        return "rebuttal"
    if "fix" in s:
        return "fixed"
    if "open" in s:
        return "open"
    return s or "recorded"


def _review_decisions(path: Path, data: dict[str, Any]) -> list[dict[str, Any]]:
    book = data.get("book") or path.parent.name
    chapter = data.get("chapter")
    created_at = data.get("reviewed_at") or datetime.now(timezone.utc).isoformat()
    decisions: list[dict[str, Any]] = []
    for idx, issue in enumerate(data.get("issues", []) or [], start=1):
        if not isinstance(issue, dict):
            continue
        status = issue.get("status") or ""
        decision_text = issue.get("rebuttal") or issue.get("proposed_fix") or issue.get("explanation")
        if not status and not decision_text:
            continue
        issue_id = issue.get("id") or f"{book}-{chapter}-issue-{idx:03d}"
        decisions.append({
            "id": str(issue_id),
            "book": book,
            "chapter": chapter,
            "verse": issue.get("verse"),
            "source": str(path),
            "category": issue.get("category"),
            "status": _status_kind(status, bool(issue.get("rebuttal"))),
            "subject": issue.get("quote_modernized") or issue.get("location") or issue.get("category"),
            "decision": decision_text or status,
            "evidence": issue.get("explanation") or issue.get("verified_at") or "",
            "rule_reference": issue.get("rule_reference") or "",
            "created_at": issue.get("verified_at") or created_at,
        })
    return decisions


def _note_decisions(path: Path, data: dict[str, Any]) -> list[dict[str, Any]]:
    book = data.get("book") or path.parent.name
    chapter = data.get("chapter")
    created_at = data.get("generated_at") or datetime.now(timezone.utc).isoformat()
    decisions: list[dict[str, Any]] = []
    for verse_obj in data.get("verses", []) or []:
        if not isinstance(verse_obj, dict):
            continue
        verse = verse_obj.get("verse_number")
        notes = verse_obj.get("notes") or []
        if isinstance(notes, str):
            notes = [notes]
        for idx, note in enumerate(notes, start=1):
            note_text = _text(note).strip()
            if not note_text:
                continue
            decisions.append({
                "id": f"{book}-{chapter}-{verse}-note-{idx:03d}",
                "book": book,
                "chapter": chapter,
                "verse": verse,
                "source": str(path),
                "category": "output-note",
                "status": "note",
                "subject": f"{book} {chapter}:{verse}",
                "decision": note_text,
                "evidence": "",
                "rule_reference": "",
                "created_at": verse_obj.get("generated_at") or created_at,
            })
    return decisions


def collect_decisions(root: Path, book_filter: str | None, include_notes: bool) -> list[dict[str, Any]]:
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"FOUT: --root bestaat niet of is geen directory: {root}")
    records: list[dict[str, Any]] = []
    for path in sorted(root.glob("*/*.json")):
        if path.parent.name == "META":
            continue
        if book_filter and path.parent.name != book_filter:
            continue
        data = _read_json(path)
        if not data:
            continue
        if path.name.startswith("review."):
            records.extend(_review_decisions(path, data))
        elif include_notes and data.get("verses"):
            records.extend(_note_decisions(path, data))
    records.sort(key=lambda r: (r.get("book") or "", r.get("chapter") or 0, r.get("verse") or 0, r.get("id") or ""))
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default="output", help="Output-root met <BOEK>/*.json.")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="JSONL-uitvoerpad.")
    parser.add_argument("--book", help="Beperk tot één boekcode.")
    parser.add_argument("--no-notes", action="store_true", help="Indexeer geen output-verse notes.")
    args = parser.parse_args()

    records = collect_decisions(Path(args.root), args.book, not args.no_notes)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    print(json.dumps({"ok": True, "out": str(out), "records": len(records)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
