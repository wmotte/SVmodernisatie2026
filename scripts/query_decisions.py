"""Zoek in `output/META/decisions.jsonl`.

Eenvoudige lokale query zonder verplichte index. Ranking is bewust
transparant: records met meer term-hits in subject/category/decision/evidence
komen bovenaan.

CLI:
    uv run python scripts/query_decisions.py "des Heeren" --book LUK
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PATH = PROJECT_ROOT / "output" / "META" / "decisions.jsonl"


def _load(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise SystemExit(f"FOUT: decisions-bestand bestaat niet: {path}. Draai scripts/extract_decisions.py.")
    records = []
    with path.open(encoding="utf-8") as fh:
        for line_no, raw in enumerate(fh, start=1):
            line = raw.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SystemExit(f"FOUT: ongeldige JSONL op regel {line_no}: {exc}") from exc
            if isinstance(record, dict):
                records.append(record)
    return records


def _haystack(record: dict[str, Any]) -> str:
    fields = [
        record.get("id"),
        record.get("category"),
        record.get("status"),
        record.get("subject"),
        record.get("decision"),
        record.get("evidence"),
        record.get("rule_reference"),
    ]
    return "\n".join(str(f) for f in fields if f is not None).lower()


def _score(record: dict[str, Any], terms: list[str], phrase: str) -> int:
    hay = _haystack(record)
    score = 0
    if phrase.lower() in hay:
        score += 5
    for term in terms:
        score += len(re.findall(r"\b" + re.escape(term.lower()) + r"\b", hay))
    return score


def _excerpt(text: str, terms: list[str], width: int = 180) -> str:
    if not text:
        return ""
    lower = text.lower()
    positions = [lower.find(t.lower()) for t in terms if lower.find(t.lower()) >= 0]
    pos = min(positions) if positions else 0
    start = max(0, pos - width // 3)
    end = min(len(text), start + width)
    return ("…" if start else "") + text[start:end].replace("\n", " ") + ("…" if end < len(text) else "")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("query", help="Zoekterm of frase.")
    parser.add_argument("--path", default=str(DEFAULT_PATH), help="Pad naar decisions.jsonl.")
    parser.add_argument("--book", help="Filter op boekcode.")
    parser.add_argument("--status", help="Filter op status, bv. rebuttal/fixed/note.")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    records = _load(Path(args.path))
    terms = [t for t in re.findall(r"[A-Za-zÀ-ÿ0-9]+", args.query) if t]
    scored = []
    for record in records:
        if args.book and record.get("book") != args.book:
            continue
        if args.status and record.get("status") != args.status:
            continue
        score = _score(record, terms, args.query)
        if score > 0:
            scored.append((score, record))
    scored.sort(key=lambda x: (-x[0], x[1].get("book") or "", x[1].get("chapter") or 0, x[1].get("verse") or 0))

    print(json.dumps({
        "query": args.query,
        "matches": len(scored),
        "results": [
            {
                "score": score,
                "id": record.get("id"),
                "book": record.get("book"),
                "chapter": record.get("chapter"),
                "verse": record.get("verse"),
                "category": record.get("category"),
                "status": record.get("status"),
                "subject": record.get("subject"),
                "decision_excerpt": _excerpt(str(record.get("decision") or ""), terms),
                "rule_reference": record.get("rule_reference"),
                "source": record.get("source"),
            }
            for score, record in scored[:args.limit]
        ],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
