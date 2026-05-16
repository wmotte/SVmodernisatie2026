#!/usr/bin/env python3
"""Detecteer het volgende blok van 3 nog-niet-gemoderniseerde verzen.

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
    args = ap.parse_args()

    boek, h = args.book, args.chapter
    with open(f"input.sv/{boek}/{boek}.{h}.json") as f:
        inp = json.load(f)
    try:
        with open(f"output/{boek}/{boek}.{h}.json") as f:
            out = json.load(f)
        done = {v["verse_number"] for v in out["verses"]}
    except FileNotFoundError:
        done = set()

    todo = [v["verse_number"] for v in inp["verses"]
            if v["verse_number"] not in done
            and (args.ceil is None or v["verse_number"] <= args.ceil)]

    if not todo:
        print("CHAPTER_COMPLETE")
    else:
        nxt = todo[:3]
        print(f"NEXT={nxt[0]}-{nxt[-1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
