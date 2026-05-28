#!/usr/bin/env python3
"""Detecteer het volgende blok nog-niet-gemoderniseerde verzen (default 3, zie --size).

Gebruikt door sv-batch-orchestrate Stap 1. Vervangt het inline-Python-blok
zodat de orchestrator-context niet vol loopt met herhaalde commandotekst.

Uitvoer (één regel):
  NEXT=<V_START>-<V_EIND>   of   CHAPTER_COMPLETE
"""
import argparse
import json
import sys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", required=True)
    ap.add_argument("--chapter", required=True, type=int)
    ap.add_argument("--ceil", type=int, default=None,
                    help="Plafond bij doorgegeven range; verzen > ceil worden genegeerd.")
    ap.add_argument("--size", type=int, default=3,
                    help="Aantal verzen per batch (default 3).")
    args = ap.parse_args()

    boek, h = args.book, args.chapter
    input_path = f"input.sv/{boek}/{boek}.{h}.json"
    output_path = f"output/{boek}/{boek}.{h}.json"
    try:
        with open(input_path) as f:
            inp = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: input niet gevonden: {input_path}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"ERROR: input is geen valide JSON ({input_path}): {exc}", file=sys.stderr)
        return 2
    try:
        with open(output_path) as f:
            out = json.load(f)
        done = {v["verse_number"] for v in out["verses"]}
    except FileNotFoundError:
        done = set()
    except json.JSONDecodeError as exc:
        print(f"ERROR: output is geen valide JSON ({output_path}): {exc}", file=sys.stderr)
        return 2

    todo = [v["verse_number"] for v in inp["verses"]
            if v["verse_number"] not in done
            and (args.ceil is None or v["verse_number"] <= args.ceil)]

    if not todo:
        print("CHAPTER_COMPLETE")
    else:
        size = args.size if args.size and args.size > 0 else 3
        nxt = todo[:size]
        print(f"NEXT={nxt[0]}-{nxt[-1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
