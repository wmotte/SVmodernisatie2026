#!/usr/bin/env python3
"""Upsert vers / introductie / epiloog in output JSON.

Vervangt ad-hoc Python-heredocs in de modernize-subagent. Leest
input.sv/<BOEK>/<BOEK>.<H>.json voor `original` (text) en `source_text`
byte-exact uit; schrijft output/<BOEK>/<BOEK>.<H>.json met 2-space
indent, ensure_ascii=False en afsluitende newline.

CLI:
  upsert_verse.py verse    --book LUK --chapter 18 --verse 38 \\
                           --modernized "..." --examples 5 \\
                           [--notes-json '[{...}]'] [--model claude-opus-4-7[1m]]
  upsert_verse.py intro    --book LUK --chapter 18 --modernized "..." [--model ...]
  upsert_verse.py epilogue --book LUK --chapter 24 --modernized "..." [--model ...]

Uitvoer (stdout, één regel):
  UPSERT <BOEK> <H>:<V> ok
  UPSERT <BOEK> <H>:intro ok
  UPSERT <BOEK> <H>:epilogue ok

Exit non-zero bij fout (stderr-melding). Idempotent op herhaalde aanroep.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_MODEL = "claude-opus-4-7[1m]"

# Whitelist voor notes[*].type. Spiegelt _NOTES_ALLOWED_TYPES in validate.py.
# Pre-write enforcement voorkomt dat verse-objecten met type='retro-fix' of
# andere legacy/typo-waarden überhaupt naar disk gaan; validate.py vangt ze
# anders pas na de schrijfactie.
_NOTES_ALLOWED_TYPES = frozenset({"twijfel", "afwijking", "context"})


def _validate_notes(notes: list) -> str | None:
    """Return None bij OK, anders foutbericht-string."""
    for i, n in enumerate(notes):
        if not isinstance(n, dict):
            return f"notes[{i}]: moet object zijn, kreeg {type(n).__name__}"
        t = n.get("type")
        if t is None:
            return f"notes[{i}]: veld 'type' ontbreekt"
        if t not in _NOTES_ALLOWED_TYPES:
            allowed = ", ".join(sorted(_NOTES_ALLOWED_TYPES))
            return f"notes[{i}]: type={t!r} niet toegestaan (gebruik: {allowed})"
    return None


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _load_input(book: str, chapter: int) -> dict:
    p = Path(f"input.sv/{book}/{book}.{chapter}.json")
    if not p.exists():
        print(f"FOUT: input ontbreekt: {p}", file=sys.stderr)
        sys.exit(2)
    return json.loads(p.read_text(encoding="utf-8"))


def _load_output_or_skeleton(book: str, chapter: int, inp: dict) -> dict:
    p = Path(f"output/{book}/{book}.{chapter}.json")
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    skel = {
        "book": inp.get("book", book),
        "chapter": chapter,
        "introduction": {"original": inp.get("introduction", "")},
        "verses": [],
    }
    if "epilogue" in inp:
        skel["epilogue"] = {"original": inp["epilogue"]}
    return skel


def _write_output(book: str, chapter: int, out: dict) -> None:
    p = Path(f"output/{book}/{book}.{chapter}.json")
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")


def cmd_verse(args) -> int:
    inp = _load_input(args.book, args.chapter)
    src = {v["verse_number"]: v for v in inp["verses"]}
    if args.verse not in src:
        print(f"FOUT: vers {args.verse} niet in input.", file=sys.stderr)
        return 2
    sv = src[args.verse]
    entry = {
        "verse_number": args.verse,
        "original": sv["text"],
        "modernized": args.modernized,
        "source_text": sv["source_text"],
        "generated_at": _utc_now(),
        "model": args.model,
        "memory_examples_used": args.examples,
    }
    if args.notes_json:
        try:
            notes = json.loads(args.notes_json)
        except json.JSONDecodeError as e:
            print(f"FOUT: --notes-json niet parseerbaar: {e}", file=sys.stderr)
            return 2
        if not isinstance(notes, list):
            print("FOUT: --notes-json moet een JSON-array zijn.", file=sys.stderr)
            return 2
        err = _validate_notes(notes)
        if err is not None:
            print(f"FOUT: --notes-json {err}", file=sys.stderr)
            return 2
        entry["notes"] = notes
    out = _load_output_or_skeleton(args.book, args.chapter, inp)
    verses = out.setdefault("verses", [])
    idx = next(
        (i for i, v in enumerate(verses) if v["verse_number"] == args.verse),
        None,
    )
    if idx is None:
        verses.append(entry)
    else:
        verses[idx] = entry
    verses.sort(key=lambda v: v["verse_number"])
    _write_output(args.book, args.chapter, out)
    print(f"UPSERT {args.book} {args.chapter}:{args.verse} ok")
    return 0


def cmd_intro(args) -> int:
    inp = _load_input(args.book, args.chapter)
    out = _load_output_or_skeleton(args.book, args.chapter, inp)
    intro = out.setdefault("introduction", {"original": inp.get("introduction", "")})
    intro["original"] = inp.get("introduction", intro.get("original", ""))
    intro["modernized"] = args.modernized
    intro["generated_at"] = _utc_now()
    intro["model"] = args.model
    _write_output(args.book, args.chapter, out)
    print(f"UPSERT {args.book} {args.chapter}:intro ok")
    return 0


def cmd_epilogue(args) -> int:
    inp = _load_input(args.book, args.chapter)
    if "epilogue" not in inp:
        print("FOUT: input heeft geen epilogue.", file=sys.stderr)
        return 2
    out = _load_output_or_skeleton(args.book, args.chapter, inp)
    epi = out.setdefault("epilogue", {"original": inp["epilogue"]})
    epi["original"] = inp["epilogue"]
    epi["modernized"] = args.modernized
    epi["generated_at"] = _utc_now()
    epi["model"] = args.model
    _write_output(args.book, args.chapter, out)
    print(f"UPSERT {args.book} {args.chapter}:epilogue ok")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Upsert vers/intro/epilogue in output JSON.",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    pv = sub.add_parser("verse", help="upsert één vers.")
    pv.add_argument("--book", required=True)
    pv.add_argument("--chapter", required=True, type=int)
    pv.add_argument("--verse", required=True, type=int)
    pv.add_argument("--modernized", required=True)
    pv.add_argument("--examples", required=True, type=int)
    pv.add_argument("--notes-json", default=None,
                    help="JSON-array van note-objecten; optioneel.")
    pv.add_argument("--model", default=DEFAULT_MODEL)
    pv.set_defaults(func=cmd_verse)

    pi = sub.add_parser("intro", help="upsert introductie.")
    pi.add_argument("--book", required=True)
    pi.add_argument("--chapter", required=True, type=int)
    pi.add_argument("--modernized", required=True)
    pi.add_argument("--model", default=DEFAULT_MODEL)
    pi.set_defaults(func=cmd_intro)

    pe = sub.add_parser("epilogue", help="upsert epiloog.")
    pe.add_argument("--book", required=True)
    pe.add_argument("--chapter", required=True, type=int)
    pe.add_argument("--modernized", required=True)
    pe.add_argument("--model", default=DEFAULT_MODEL)
    pe.set_defaults(func=cmd_epilogue)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
