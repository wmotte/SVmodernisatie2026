"""Vector-DB voor SV-modernisatie.

Slaat per vers twee embeddings op (SV-origineel + modernisatie) zodat we op
beide assen kunnen zoeken. Gebruikt SQLite + Gemini embeddings (768 dim).

CLI:
    python scripts/memory.py count
    python scripts/memory.py query --text "..." [--k 5] [--axis sv|mod|both] \\
        [--exclude-book LUK --exclude-chapter 1 --exclude-verse 1]
    python scripts/memory.py add --book LUK --chapter 1 --verse 1 \\
        --sv "..." --modern "..." [--source-text "..."]
    python scripts/memory.py add --from-output output/LUK/LUK.1.json --verse 1
    python scripts/memory.py add --from-output output/LUK/LUK.1.json --all
    python scripts/memory.py sync [--root output/] [--check-only] [--quiet]

Bij her-modernisatie: gebruik --exclude-book/chapter/verse om te
voorkomen dat het te-her-moderniseren vers zichzelf als few-shot
terugziet (zelf-bevestigend).

Output: JSON op stdout. Logging op stderr.
"""

import argparse
import json
import os
import sqlite3
import struct
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from google import genai
from google.genai import types

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "memory" / "verses.db"
EMBED_MODEL = "gemini-embedding-001"
EMBED_DIM = 768


def _eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS verses (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            book          TEXT NOT NULL,
            chapter       INTEGER NOT NULL,
            verse         INTEGER NOT NULL,
            sv_origineel  TEXT NOT NULL,
            modernisatie  TEXT NOT NULL,
            embedding_sv  BLOB NOT NULL,
            embedding_mod BLOB NOT NULL,
            metadata      TEXT,
            created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(book, chapter, verse)
        )
        """
    )
    conn.commit()
    return conn


def _client() -> genai.Client:
    # Laad .env in werkdirectory of project root.
    load_dotenv(PROJECT_ROOT / ".env")
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        _eprint("FOUT: GOOGLE_API_KEY niet gezet (zie .env.example).")
        sys.exit(2)
    return genai.Client(api_key=api_key)


def _embed(client: genai.Client, text: str, task_type: str) -> np.ndarray:
    # Gemini embed_content geeft een lijst embeddings; wij sturen één tekst,
    # dus we pakken het eerste resultaat. task_type onderscheidt query vs document.
    result = client.models.embed_content(
        model=EMBED_MODEL,
        contents=[text],
        config=types.EmbedContentConfig(
            output_dimensionality=EMBED_DIM,
            task_type=task_type,
        ),
    )
    vec = np.array(result.embeddings[0].values, dtype=np.float32)
    # L2-normaliseren zodat dot-product == cosine similarity.
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec


def _vec_to_blob(vec: np.ndarray) -> bytes:
    return struct.pack(f"{EMBED_DIM}f", *vec.tolist())


def _blob_to_vec(blob: bytes) -> np.ndarray:
    return np.array(struct.unpack(f"{EMBED_DIM}f", blob), dtype=np.float32)


def cmd_count(_args: argparse.Namespace) -> None:
    conn = _connect()
    n = conn.execute("SELECT COUNT(*) FROM verses").fetchone()[0]
    print(json.dumps({"count": n}))


def _add_one(client: genai.Client, conn: sqlite3.Connection,
             book: str, chapter: int, verse: int,
             sv: str, modern: str, source_text: str) -> None:
    emb_sv = _embed(client, sv, "RETRIEVAL_DOCUMENT")
    emb_mod = _embed(client, modern, "RETRIEVAL_DOCUMENT")
    metadata = {
        "source_text": source_text or "",
        "added_at": datetime.now(timezone.utc).isoformat(),
    }
    conn.execute(
        """
        INSERT INTO verses (book, chapter, verse, sv_origineel, modernisatie,
                            embedding_sv, embedding_mod, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(book, chapter, verse) DO UPDATE SET
            sv_origineel  = excluded.sv_origineel,
            modernisatie  = excluded.modernisatie,
            embedding_sv  = excluded.embedding_sv,
            embedding_mod = excluded.embedding_mod,
            metadata      = excluded.metadata
        """,
        (
            book, chapter, verse, sv, modern,
            _vec_to_blob(emb_sv), _vec_to_blob(emb_mod),
            json.dumps(metadata, ensure_ascii=False),
        ),
    )
    conn.commit()


def cmd_add(args: argparse.Namespace) -> None:
    """Voeg een vers toe via expliciete --sv/--modern, of vanuit een output-JSON.

    `--from-output` voorkomt shell-quoting voor lange teksten met kanttekeningen.
    Combineer met `--verse N` voor één vers, of `--all` voor alle verzen in
    het bestand. `--book` en `--chapter` worden uit de JSON gehaald.
    """
    client = _client()
    conn = _connect()

    if args.from_output:
        path = Path(args.from_output)
        if not path.exists():
            _eprint(f"FOUT: --from-output bestand niet gevonden: {path}")
            sys.exit(2)
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        book = data.get("book")
        chapter = data.get("chapter")
        verses = data.get("verses", [])
        if args.all:
            targets = verses
        elif args.verse is not None:
            targets = [v for v in verses if v.get("verse_number") == args.verse]
            if not targets:
                _eprint(f"FOUT: vers {args.verse} niet in {path}")
                sys.exit(2)
        else:
            _eprint("FOUT: gebruik --verse N of --all bij --from-output")
            sys.exit(2)

        added = []
        for v in targets:
            _add_one(
                client, conn, book, chapter, v["verse_number"],
                v["original"], v["modernized"], v.get("source_text", ""),
            )
            added.append(v["verse_number"])

        total = conn.execute("SELECT COUNT(*) FROM verses").fetchone()[0]
        if args.terse:
            vs = ",".join(str(n) for n in added)
            print(f"{book} {chapter}:{vs} -> {total}")
            return
        print(json.dumps({
            "ok": True,
            "book": book,
            "chapter": chapter,
            "verses_added": added,
            "total": total,
        }))
        return

    # Klassieke modus: expliciete --sv/--modern.
    if not args.sv or not args.modern or args.book is None or args.chapter is None or args.verse is None:
        _eprint("FOUT: zonder --from-output zijn --book, --chapter, --verse, --sv, --modern verplicht")
        sys.exit(2)
    _add_one(
        client, conn, args.book, args.chapter, args.verse,
        args.sv, args.modern, args.source_text,
    )
    total = conn.execute("SELECT COUNT(*) FROM verses").fetchone()[0]
    if args.terse:
        print(f"{args.book} {args.chapter}:{args.verse} -> {total}")
        return
    print(json.dumps({
        "ok": True,
        "book": args.book,
        "chapter": args.chapter,
        "verse": args.verse,
        "total": total,
    }))


def cmd_sync(args: argparse.Namespace) -> None:
    """Synchroniseer vector-DB met output-JSONs.

    Dirty-detectie via tekst-equality: per vers wordt (original, modernized,
    source_text) tussen JSON en DB vergeleken. Verschilt iets, of ontbreekt
    de DB-entry, dan opnieuw embedden + upserten. Orphan-entries (in DB maar
    niet meer in een output-JSON) worden gerapporteerd, nooit verwijderd.

    --check-only doet alleen detectie (geen Gemini-calls).
    """
    root = Path(args.root)
    if not root.exists() or not root.is_dir():
        _eprint(f"FOUT: --root {root} bestaat niet of is geen directory")
        sys.exit(2)

    # Pre-flight: --root verwacht een output-niveau directory met `<BOEK>/<H>.json`
    # subdirs. Wordt het script per ongeluk aangeroepen met een book-level pad
    # (bv. `output/LUK/`), dan levert glob('*/*.json') nul matches en lijken alle
    # DB-entries orphans. Detecteer dat: als root direct JSON-bestanden bevat én
    # geen subdir-JSON's, is dit waarschijnlijk een book-pad.
    direct_json = list(root.glob("*.json"))
    nested_json = list(root.glob("*/*.json"))
    if direct_json and not nested_json:
        _eprint(
            f"FOUT: --root {root} bevat {len(direct_json)} JSON-bestanden direct, "
            f"maar 0 op `<BOEK>/<H>.json`-pad. Bedoel je `--root {root.parent}`? "
            f"sync verwacht een output-niveau directory."
        )
        sys.exit(2)

    conn = _connect()

    db_rows = conn.execute(
        "SELECT book, chapter, verse, sv_origineel, modernisatie, metadata FROM verses"
    ).fetchall()
    db_index = {}
    for r in db_rows:
        meta = json.loads(r[5]) if r[5] else {}
        db_index[(r[0], r[1], r[2])] = {
            "sv": r[3],
            "modern": r[4],
            "source_text": meta.get("source_text", ""),
        }

    json_keys: set[tuple[str, int, int]] = set()
    dirty: list[dict] = []
    missing: list[dict] = []
    scanned_files = 0
    scanned_verses = 0

    for path in sorted(root.glob("*/*.json")):
        if path.parent.name == "META":
            continue
        try:
            with path.open(encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            _eprint(f"WAARSCHUWING: kan {path} niet lezen ({e}); skip")
            continue
        scanned_files += 1
        book = data.get("book")
        chapter = data.get("chapter")
        if book is None or chapter is None:
            _eprint(f"WAARSCHUWING: {path} mist book/chapter; skip")
            continue
        for v in data.get("verses", []):
            vn = v.get("verse_number")
            if vn is None:
                continue
            key = (book, chapter, vn)
            json_keys.add(key)
            scanned_verses += 1

            sv = v.get("original", "")
            modern = v.get("modernized", "")
            src = v.get("source_text", "")

            db_entry = db_index.get(key)
            if db_entry is None:
                missing.append({
                    "book": book, "chapter": chapter, "verse": vn,
                    "reason": "niet in DB",
                    "_payload": (sv, modern, src),
                })
            else:
                reasons = []
                if db_entry["sv"] != sv:
                    reasons.append("sv-origineel verschilt")
                if db_entry["modern"] != modern:
                    reasons.append("modernisatie verschilt")
                if db_entry["source_text"] != src:
                    reasons.append("source_text verschilt")
                if reasons:
                    dirty.append({
                        "book": book, "chapter": chapter, "verse": vn,
                        "reason": "; ".join(reasons),
                        "_payload": (sv, modern, src),
                    })

    orphan_list = [
        {"book": k[0], "chapter": k[1], "verse": k[2]}
        for k in db_index.keys()
        if k not in json_keys
    ]

    api_calls = 0
    if not args.check_only and (dirty or missing):
        client = _client()
        for entry in dirty + missing:
            sv, modern, src = entry["_payload"]
            _add_one(
                client, conn, entry["book"], entry["chapter"], entry["verse"],
                sv, modern, src,
            )
            api_calls += 2
            if not args.quiet:
                _eprint(
                    f"  re-embed {entry['book']} {entry['chapter']}:{entry['verse']} "
                    f"({entry['reason']})"
                )

    def _strip(lst):
        return [{k: v for k, v in e.items() if k != "_payload"} for e in lst]

    if args.terse:
        clean = scanned_verses - len(dirty) - len(missing)
        mode = "check" if args.check_only else "sync"
        print(
            f"{mode} {scanned_verses}v {clean}c {len(dirty)}d "
            f"{len(missing)}m {len(orphan_list)}o api={api_calls}"
        )
        return

    print(json.dumps({
        "scanned_files": scanned_files,
        "scanned_verses": scanned_verses,
        "clean": scanned_verses - len(dirty) - len(missing),
        "dirty": len(dirty),
        "missing": len(missing),
        "orphans": len(orphan_list),
        "api_calls": api_calls,
        "check_only": args.check_only,
        "details": {
            "dirty": _strip(dirty),
            "missing": _strip(missing),
            "orphans": orphan_list,
        },
    }, ensure_ascii=False, indent=2))


def cmd_query(args: argparse.Namespace) -> None:
    excl = (args.exclude_book, args.exclude_chapter, args.exclude_verse)
    excl_set = sum(x is not None for x in excl)
    if excl_set not in (0, 3):
        _eprint("FOUT: --exclude-book, --exclude-chapter en --exclude-verse moeten samen worden gezet (allen-of-niets)")
        sys.exit(2)
    excl_key = (args.exclude_book, args.exclude_chapter, args.exclude_verse) if excl_set == 3 else None

    # `--from-output --verse N` haalt de zoek-tekst (het SV-origineel) uit de
    # output-JSON, zodat de aanroeper geen lange tekst met kanttekeningen /
    # quotes / $refs$ door de shell hoeft te quoten of via inline python te
    # extraheren. Zonder expliciete --exclude-* sluit het ook het bevraagde
    # vers zelf uit.
    if args.from_output:
        if args.verse is None:
            _eprint("FOUT: --from-output vereist --verse N")
            sys.exit(2)
        path = Path(args.from_output)
        if not path.exists():
            _eprint(f"FOUT: --from-output bestand niet gevonden: {path}")
            sys.exit(2)
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        match = next((v for v in data.get("verses", []) if v.get("verse_number") == args.verse), None)
        if match is None:
            _eprint(f"FOUT: vers {args.verse} niet in {path}")
            sys.exit(2)
        args.text = match["original"]
        if excl_key is None:
            excl_key = (data.get("book"), data.get("chapter"), args.verse)
    elif args.text is None:
        _eprint("FOUT: gebruik --text of --from-output --verse N")
        sys.exit(2)

    conn = _connect()
    rows = conn.execute(
        "SELECT book, chapter, verse, sv_origineel, modernisatie, "
        "embedding_sv, embedding_mod, metadata FROM verses"
    ).fetchall()
    total_in_db = len(rows)

    if excl_key is not None:
        rows = [r for r in rows if (r[0], r[1], r[2]) != excl_key]

    if not rows:
        # Lege DB (of alles weggefilterd) is OK — agent moet hier met een lege lijst kunnen werken.
        if args.terse:
            print(f"query 0 results (total_in_db={total_in_db})")
        else:
            print(json.dumps({"results": [], "total_in_db": total_in_db}))
        return

    client = _client()
    q_vec = _embed(client, args.text, "RETRIEVAL_QUERY")

    # Stack alle embeddings als matrix; cosine sim = dot-product (al genormaliseerd).
    sv_mat = np.stack([_blob_to_vec(r[5]) for r in rows])
    mod_mat = np.stack([_blob_to_vec(r[6]) for r in rows])

    if args.axis == "sv":
        sims = sv_mat @ q_vec
    elif args.axis == "mod":
        sims = mod_mat @ q_vec
    else:  # both — neem max van beide assen per record
        sims = np.maximum(sv_mat @ q_vec, mod_mat @ q_vec)

    k = min(args.k, len(rows))
    top_idx = np.argsort(-sims)[:k]

    results = []
    for i in top_idx:
        r = rows[int(i)]
        meta = json.loads(r[7]) if r[7] else {}
        entry = {
            "book": r[0],
            "chapter": r[1],
            "verse": r[2],
            "sv": r[3],
            "modern": r[4],
            "similarity": float(sims[int(i)]),
        }
        if not args.terse:
            entry["source_text"] = meta.get("source_text", "")
        results.append(entry)

    print(
        json.dumps(
            {"results": results, "total_in_db": total_in_db, "axis": args.axis},
            ensure_ascii=False,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    sp_count = sub.add_parser("count", help="Toon aantal verzen in DB.")
    sp_count.set_defaults(func=cmd_count)

    sp_add = sub.add_parser("add", help="Voeg vers toe (of overschrijf bestaand).")
    sp_add.add_argument("--book", help="3-letterige boekcode, bv. LUK (genegeerd bij --from-output)")
    sp_add.add_argument("--chapter", type=int, help="Hoofdstuk (genegeerd bij --from-output)")
    sp_add.add_argument("--verse", type=int, help="Vers-nummer")
    sp_add.add_argument("--sv", help="SV-origineel met kanttekeningen (zonder --from-output)")
    sp_add.add_argument("--modern", help="Gemoderniseerde tekst (zonder --from-output)")
    sp_add.add_argument("--source-text", default="", help="Textus Receptus / brontekst")
    sp_add.add_argument(
        "--from-output",
        help="Pad naar output/<BOEK>/<BOEK>.<H>.json — leest book/chapter/verzen daaruit "
             "(voorkomt shell-quoting voor lange teksten).",
    )
    sp_add.add_argument(
        "--all",
        action="store_true",
        help="Bij --from-output: voeg alle verzen toe ipv. alleen --verse N.",
    )
    sp_add.add_argument(
        "--terse",
        action="store_true",
        help="Compacte tekstuele output ipv. JSON: '<BOOK> <chapter>:<verses> -> <total>'.",
    )
    sp_add.set_defaults(func=cmd_add)

    sp_sync = sub.add_parser(
        "sync",
        help="Synchroniseer DB met output-JSONs (re-embed stale entries, rapporteer orphans).",
    )
    sp_sync.add_argument(
        "--root",
        default="output",
        help="Root-directory met <BOEK>/<BOEK>.<H>.json bestanden (default: output).",
    )
    sp_sync.add_argument(
        "--check-only",
        action="store_true",
        help="Detecteer dirty/missing/orphan zonder re-embedden.",
    )
    sp_sync.add_argument(
        "--quiet",
        action="store_true",
        help="Onderdruk per-vers re-embed-log op stderr.",
    )
    sp_sync.add_argument(
        "--terse",
        action="store_true",
        help="Eén regel: '<mode> Nv Cc Dd Mm Oo api=N' ipv. JSON met details.",
    )
    sp_sync.set_defaults(func=cmd_sync)

    sp_q = sub.add_parser("query", help="Zoek top-k vergelijkbare verzen.")
    sp_q.add_argument("--text", help="Zoek-tekst (meestal SV-vers). Verplicht zonder --from-output.")
    sp_q.add_argument(
        "--from-output",
        help="Haal de zoek-tekst (SV-origineel) uit dit output-JSON-bestand i.c.m. --verse N; "
             "voorkomt shell-quoting van lange teksten. Sluit standaard het bevraagde vers zelf uit.",
    )
    sp_q.add_argument("--verse", type=int, help="Vers-nummer bij --from-output.")
    sp_q.add_argument("--k", type=int, default=5)
    sp_q.add_argument(
        "--axis",
        choices=["sv", "mod", "both"],
        default="sv",
        help="Op welke embedding zoeken: sv (default), mod, of beide (max).",
    )
    sp_q.add_argument("--exclude-book", help="Sluit dit (book, chapter, verse) tuple uit het resultaat (allen-of-niets).")
    sp_q.add_argument("--exclude-chapter", type=int, help="Zie --exclude-book.")
    sp_q.add_argument(
        "--terse",
        action="store_true",
        help="Drop source_text-veld uit elke hit (Griekse brontekst). Bespaart ~30% per call.",
    )
    sp_q.add_argument("--exclude-verse", type=int, help="Zie --exclude-book.")
    sp_q.set_defaults(func=cmd_query)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
