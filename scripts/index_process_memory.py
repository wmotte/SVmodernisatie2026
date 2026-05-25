"""Indexeer procesgeheugen uit output-JSONs in een lokale FTS5 database.

Fase-1 Hermes-inspiratie: read-only t.o.v. bestaande output. Dit script
schrijft alleen `memory/process.db` en indexeert:

  * `output/<BOEK>/review.<H>.json` issues, rebuttals en pass-samenvattingen;
  * `notes` in `output/<BOEK>/<BOEK>.<H>.json` verzen.

CLI:
    uv run python scripts/index_process_memory.py --root output --rebuild
    uv run python scripts/index_process_memory.py --query "concordantie drift"
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "memory" / "process.db"


@dataclass(frozen=True)
class ProcessDocument:
    source: str
    doc_type: str
    book: str | None
    chapter: int | None
    verse: int | None
    key: str
    title: str
    content: str
    mtime: float
    sha256: str


def _connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            source    TEXT NOT NULL,
            doc_type  TEXT NOT NULL,
            book      TEXT,
            chapter   INTEGER,
            verse     INTEGER,
            key       TEXT NOT NULL,
            title     TEXT NOT NULL,
            mtime     REAL NOT NULL,
            sha256    TEXT NOT NULL,
            UNIQUE(source, doc_type, key)
        )
        """
    )
    conn.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS search USING fts5(
            doc_id UNINDEXED,
            source UNINDEXED,
            doc_type UNINDEXED,
            book UNINDEXED,
            chapter UNINDEXED,
            verse UNINDEXED,
            key UNINDEXED,
            title,
            content,
            tokenize='unicode61 remove_diacritics 2'
        )
        """
    )
    conn.commit()
    return conn


def _read_json(path: Path) -> Any | None:
    try:
        with path.open(encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"WAARSCHUWING: skip {path}: {exc}", file=sys.stderr)
        return None


def _stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _text_from_parts(*parts: Any) -> str:
    out: list[str] = []
    for part in parts:
        if part is None:
            continue
        if isinstance(part, str):
            if part.strip():
                out.append(part.strip())
        elif isinstance(part, (list, tuple)):
            out.append(_text_from_parts(*part))
        elif isinstance(part, dict):
            out.append(_stable_json(part))
        else:
            out.append(str(part))
    return "\n".join(p for p in out if p)


def _review_docs(path: Path, data: dict[str, Any]) -> Iterable[ProcessDocument]:
    source = str(path)
    mtime = path.stat().st_mtime
    book = data.get("book") or path.parent.name
    chapter = data.get("chapter")

    for idx, p in enumerate(data.get("passes", []) or [], start=1):
        if not isinstance(p, dict):
            continue
        pass_no = p.get("pass", "x")
        key = f"pass-{pass_no}#{idx:03d}"
        title = f"{book} {chapter} review pass {pass_no} {p.get('mode', '')}".strip()
        content = _text_from_parts(p)
        if content:
            yield ProcessDocument(
                source, "review-pass", book, chapter, None, key, title,
                content, mtime, _hash_text(content),
            )

    for idx, issue in enumerate(data.get("issues", []) or [], start=1):
        if not isinstance(issue, dict):
            continue
        issue_id = issue.get("id") or f"issue-{idx:03d}"
        key = f"{issue_id}#{idx:03d}"
        verse = issue.get("verse")
        title = f"{issue_id} {issue.get('category', '')} {issue.get('status', '')}".strip()
        content = _text_from_parts(
            issue.get("category"),
            issue.get("severity"),
            issue.get("quote_modernized"),
            issue.get("explanation"),
            issue.get("proposed_fix"),
            issue.get("rule_reference"),
            issue.get("rebuttal"),
            issue.get("status"),
            issue.get("location"),
            issue.get("verses_involved"),
        )
        if content:
            yield ProcessDocument(
                source, "review-issue", book, chapter, verse, key,
                title, content, mtime, _hash_text(content),
            )


def _output_note_docs(path: Path, data: dict[str, Any]) -> Iterable[ProcessDocument]:
    source = str(path)
    mtime = path.stat().st_mtime
    book = data.get("book") or path.parent.name
    chapter = data.get("chapter")
    for verse_obj in data.get("verses", []) or []:
        if not isinstance(verse_obj, dict):
            continue
        verse = verse_obj.get("verse_number")
        notes = verse_obj.get("notes") or []
        if isinstance(notes, str):
            notes = [notes]
        for idx, note in enumerate(notes, start=1):
            content = _text_from_parts(note)
            if not content:
                continue
            key = f"v{verse}-note-{idx}"
            title = f"{book} {chapter}:{verse} note {idx}"
            yield ProcessDocument(
                source, "output-note", book, chapter, verse, key, title,
                content, mtime, _hash_text(content),
            )


def collect_documents(root: Path) -> list[ProcessDocument]:
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"FOUT: --root bestaat niet of is geen directory: {root}")

    docs: list[ProcessDocument] = []
    for path in sorted(root.glob("*/*.json")):
        if path.parent.name == "META":
            continue
        data = _read_json(path)
        if not isinstance(data, dict):
            continue
        if path.name.startswith("review."):
            docs.extend(_review_docs(path, data))
        elif data.get("verses"):
            docs.extend(_output_note_docs(path, data))
    return docs


def _upsert_doc(conn: sqlite3.Connection, doc: ProcessDocument) -> bool:
    old = conn.execute(
        "SELECT id, sha256 FROM documents WHERE source=? AND doc_type=? AND key=?",
        (doc.source, doc.doc_type, doc.key),
    ).fetchone()
    if old and old[1] == doc.sha256:
        return False

    conn.execute(
        """
        INSERT INTO documents
            (source, doc_type, book, chapter, verse, key, title, mtime, sha256)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(source, doc_type, key) DO UPDATE SET
            book=excluded.book,
            chapter=excluded.chapter,
            verse=excluded.verse,
            title=excluded.title,
            mtime=excluded.mtime,
            sha256=excluded.sha256
        """,
        (
            doc.source, doc.doc_type, doc.book, doc.chapter, doc.verse,
            doc.key, doc.title, doc.mtime, doc.sha256,
        ),
    )
    doc_id = conn.execute(
        "SELECT id FROM documents WHERE source=? AND doc_type=? AND key=?",
        (doc.source, doc.doc_type, doc.key),
    ).fetchone()[0]
    conn.execute("DELETE FROM search WHERE doc_id=?", (doc_id,))
    conn.execute(
        """
        INSERT INTO search
            (doc_id, source, doc_type, book, chapter, verse, key, title, content)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            doc_id, doc.source, doc.doc_type, doc.book, doc.chapter,
            doc.verse, doc.key, doc.title, doc.content,
        ),
    )
    return True


def cmd_index(args: argparse.Namespace) -> None:
    conn = _connect(Path(args.db))
    if args.rebuild:
        conn.execute("DELETE FROM search")
        conn.execute("DELETE FROM documents")
        conn.commit()

    docs = collect_documents(Path(args.root))
    changed = 0
    for doc in docs:
        changed += int(_upsert_doc(conn, doc))
    conn.commit()

    total = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    print(json.dumps({
        "ok": True,
        "db": str(Path(args.db)),
        "documents_seen": len(docs),
        "documents_changed": changed,
        "documents_total": total,
        "rebuild": args.rebuild,
    }, ensure_ascii=False, indent=2))


def cmd_query(args: argparse.Namespace) -> None:
    db_path = Path(args.db)
    if not db_path.exists():
        raise SystemExit(f"FOUT: database bestaat niet: {db_path}. Draai eerst --rebuild.")
    conn = _connect(db_path)
    params: list[Any] = [args.query]
    filters = []
    if args.book:
        filters.append("book = ?")
        params.append(args.book)
    if args.type:
        filters.append("doc_type = ?")
        params.append(args.type)
    where = "search MATCH ?"
    if filters:
        where += " AND " + " AND ".join(filters)
    params.append(args.limit)
    rows = conn.execute(
        f"""
        SELECT source, doc_type, book, chapter, verse, key, title,
               snippet(search, 8, '[', ']', ' … ', 12) AS snippet,
               bm25(search) AS rank
        FROM search
        WHERE {where}
        ORDER BY rank
        LIMIT ?
        """,
        params,
    ).fetchall()
    print(json.dumps({
        "query": args.query,
        "results": [
            {
                "source": r[0],
                "type": r[1],
                "book": r[2],
                "chapter": r[3],
                "verse": r[4],
                "key": r[5],
                "title": r[6],
                "snippet": r[7],
                "rank": r[8],
            }
            for r in rows
        ],
    }, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default=str(DB_PATH), help="SQLite/FTS databasepad.")
    parser.add_argument("--root", default="output", help="Output-root met <BOEK>/*.json.")
    parser.add_argument("--rebuild", action="store_true", help="Verwijder bestaande index eerst.")
    parser.add_argument("--query", help="Zoekterm; als gezet wordt er niet geïndexeerd.")
    parser.add_argument("--limit", type=int, default=10, help="Maximaal aantal zoekresultaten.")
    parser.add_argument("--book", help="Filter query op boekcode.")
    parser.add_argument(
        "--type",
        choices=["review-pass", "review-issue", "output-note"],
        help="Filter query op documenttype.",
    )
    args = parser.parse_args()
    if args.query:
        cmd_query(args)
    else:
        cmd_index(args)


if __name__ == "__main__":
    main()
