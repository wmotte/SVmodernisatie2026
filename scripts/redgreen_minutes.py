#!/usr/bin/env python3
"""Notulen- en state-manager voor de red-green debat-skill.

Houdt één debat-spoor bij voor het hele NT (boek-overstijgend, net als
`output/META/decisions.jsonl`):

  * `output/META/debate/state.json`   — cursor: rondes, gedebatteerde paren,
    debat-telling per boek, en `closed_keys` (beslechte punt-sleutels voor
    dedup zodat het red team niets herhaalt).
  * `output/META/debate/minutes.md`   — mens-leesbare notulen, één sectie
    per ronde.
  * `output/META/decisions.jsonl`      — geaccepteerde verdicts worden hier
    aangevuld (bestaand formaat, hergebruikt door query_decisions.py).

Subcommando's:
    init                         — lege state + minutes aanmaken (idempotent).
    summary                      — compacte status voor de orchestrator-context.
    closed-keys                  — beslechte punt-sleutels (één per regel) voor
                                   red-dedup.
    append --round <round.json>  — ronde verwerken: state bijwerken, notulen
                                   aanvullen, verdicts naar decisions.jsonl.

Round-bestand (geschreven door de subagents) heeft de vorm:
    {
      "round_no": 1,
      "books": ["MAT", "MRK"],
      "red":      [ {id, class, books, verse, quote, rule_reference,
                     explanation, proposed_fix, severity}, ... ],
      "green":    [ {point_id, stance, rebuttal, evidence}, ... ],
      "verdicts": [ {point_id, verdict, rationale, scope, applied}, ... ]
    }

Gebruik:
    uv run python scripts/redgreen_minutes.py init
    uv run python scripts/redgreen_minutes.py summary
    uv run python scripts/redgreen_minutes.py closed-keys
    uv run python scripts/redgreen_minutes.py append --round output/META/debate/round_1.json
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEBATE_DIR = REPO / "output" / "META" / "debate"
STATE_PATH = DEBATE_DIR / "state.json"
MINUTES_PATH = DEBATE_DIR / "minutes.md"
DECISIONS_PATH = REPO / "output" / "META" / "decisions.jsonl"

WORD_RE = re.compile(r"[0-9A-Za-zÀ-ÿ’']+")
SETTLED = {"red_wins", "green_wins", "rule_change"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _empty_state() -> dict:
    return {
        "rounds_done": 0,
        "pairs": [],
        "debate_count": {},
        "closed_keys": [],
        "open_keys": [],
        "updated_at": _now(),
    }


def _load_state() -> dict:
    return _read_json(STATE_PATH, _empty_state())


def _save_state(state: dict) -> None:
    state["updated_at"] = _now()
    DEBATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2),
                          encoding="utf-8")


def point_key(point: dict) -> str:
    """Stabiele dedup-sleutel voor een red-punt: class | sorted-books |
    eerste 8 inhoudswoorden van de quote | rule_reference."""
    cls = (point.get("class") or "?").strip().lower()
    books = ",".join(sorted(b.upper() for b in (point.get("books") or [])))
    quote = " ".join(WORD_RE.findall((point.get("quote") or "").lower())[:8])
    rule = (point.get("rule_reference") or "").strip().lower()
    return f"{cls}|{books}|{quote}|{rule}"


# --- subcommando's ----------------------------------------------------------

def cmd_init(_args: argparse.Namespace) -> None:
    DEBATE_DIR.mkdir(parents=True, exist_ok=True)
    if not STATE_PATH.exists():
        _save_state(_empty_state())
    if not MINUTES_PATH.exists():
        MINUTES_PATH.write_text(
            "# Red-green debat — notulen\n\n"
            "Boek-overstijgend debat-spoor voor het hele NT. Elke ronde = één\n"
            "debat over één boekenpaar. Lees dit (of `summary`) vóór een nieuwe\n"
            "sessie.\n",
            encoding="utf-8",
        )
    print(json.dumps({"init": True, "dir": str(DEBATE_DIR)}, ensure_ascii=False))


def cmd_summary(_args: argparse.Namespace) -> None:
    state = _load_state()
    pairs = state.get("pairs", [])
    print(json.dumps({
        "rounds_done": state.get("rounds_done", 0),
        "last_pairs": pairs[-3:],
        "closed_keys": len(state.get("closed_keys", [])),
        "open_keys": len(state.get("open_keys", [])),
        "debate_count": state.get("debate_count", {}),
        "updated_at": state.get("updated_at"),
    }, ensure_ascii=False))


def cmd_closed_keys(_args: argparse.Namespace) -> None:
    state = _load_state()
    for k in state.get("closed_keys", []):
        print(k)


def _append_minutes(round_data: dict) -> None:
    n = round_data.get("round_no", "?")
    books = " + ".join(round_data.get("books", []))
    red = round_data.get("red", [])
    verdicts = {v.get("point_id"): v for v in round_data.get("verdicts", [])}
    tally = {"red_wins": 0, "green_wins": 0, "rule_change": 0, "open": 0}
    for v in round_data.get("verdicts", []):
        tally[v.get("verdict", "open")] = tally.get(v.get("verdict", "open"), 0) + 1

    lines = [
        f"\n## Ronde {n} — {books}  ({_now()})\n",
        f"Red bracht {len(red)} punt(en). "
        f"Verdicts: red_wins={tally['red_wins']}, "
        f"green_wins={tally['green_wins']}, rule_change={tally['rule_change']}.\n",
    ]
    for p in red:
        pid = p.get("id")
        v = verdicts.get(pid, {})
        lines.append(
            f"- **[{pid}] ({p.get('class')})** {p.get('quote', '')[:120]}\n"
            f"  - regel: {p.get('rule_reference', '—')}; fix: {p.get('proposed_fix', '—')}\n"
            f"  - verdict: **{v.get('verdict', 'open')}** "
            f"(scope={v.get('scope', '—')}, applied={v.get('applied', False)}) — "
            f"{v.get('rationale', '')[:200]}\n"
        )
    DEBATE_DIR.mkdir(parents=True, exist_ok=True)
    with MINUTES_PATH.open("a", encoding="utf-8") as fh:
        fh.write("".join(lines))


def _append_decisions(round_data: dict) -> int:
    """Verdicts → decisions.jsonl (bestaand formaat). Retourneert aantal."""
    red_by_id = {p.get("id"): p for p in round_data.get("red", [])}
    books = round_data.get("books", [])
    src = f"output/META/debate/round_{round_data.get('round_no')}.json"
    written = 0
    DECISIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DECISIONS_PATH.open("a", encoding="utf-8") as fh:
        for v in round_data.get("verdicts", []):
            if v.get("verdict") not in SETTLED:
                continue
            p = red_by_id.get(v.get("point_id"), {})
            pbooks = p.get("books") or books
            rec = {
                "id": f"RG-{round_data.get('round_no')}-{v.get('point_id')}",
                "book": (pbooks[0] if pbooks else (books[0] if books else "")),
                "category": f"redgreen-{p.get('class', 'debat')}",
                "chapter": p.get("chapter") or p.get("verse"),
                "created_at": _now(),
                "decision": v.get("rationale", ""),
                "evidence": (round_data.get("green") and next(
                    (g.get("evidence", "") for g in round_data["green"]
                     if g.get("point_id") == v.get("point_id")), "")) or "",
                "id_point": v.get("point_id"),
                "rule_reference": p.get("rule_reference", ""),
                "scope": v.get("scope", "verse"),
                "source": src,
                "status": v.get("verdict"),
                "subject": p.get("quote", "")[:200],
                "verse": p.get("verse"),
            }
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            written += 1
    return written


def cmd_append(args: argparse.Namespace) -> None:
    round_data = _read_json(Path(args.round))
    if round_data is None:
        raise SystemExit(f"FOUT: kan round-bestand niet lezen: {args.round}")

    state = _load_state()
    n = int(round_data.get("round_no", state.get("rounds_done", 0) + 1))
    books = round_data.get("books", [])

    # State: cursor, paren, debat-telling.
    state["rounds_done"] = max(int(state.get("rounds_done", 0)), n)
    state.setdefault("pairs", []).append(books)
    dc = state.setdefault("debate_count", {})
    for b in books:
        dc[b] = int(dc.get(b, 0)) + 1

    # Dedup-sleutels: beslechte punten → closed_keys; rest → open_keys.
    red_by_id = {p.get("id"): p for p in round_data.get("red", [])}
    verdict_by_id = {v.get("point_id"): v.get("verdict")
                     for v in round_data.get("verdicts", [])}
    closed = set(state.get("closed_keys", []))
    open_keys = set(state.get("open_keys", []))
    new_closed = 0
    for pid, p in red_by_id.items():
        k = point_key(p)
        if verdict_by_id.get(pid) in SETTLED:
            closed.add(k)
            open_keys.discard(k)
            new_closed += 1
        else:
            open_keys.add(k)
    state["closed_keys"] = sorted(closed)
    state["open_keys"] = sorted(open_keys)
    _save_state(state)

    _append_minutes(round_data)
    decisions = _append_decisions(round_data)

    print(json.dumps({
        "round_no": n,
        "books": books,
        "red_points": len(red_by_id),
        "new_closed_keys": new_closed,
        "total_closed_keys": len(closed),
        "decisions_appended": decisions,
        "rounds_done": state["rounds_done"],
    }, ensure_ascii=False))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init", help="Lege state + minutes aanmaken.")
    sub.add_parser("summary", help="Compacte status (JSON) voor orchestrator.")
    sub.add_parser("closed-keys", help="Beslechte punt-sleutels (één per regel).")
    ap_app = sub.add_parser("append", help="Ronde verwerken naar state/minutes/decisions.")
    ap_app.add_argument("--round", required=True, help="Pad naar round_<N>.json.")

    args = ap.parse_args()
    {
        "init": cmd_init,
        "summary": cmd_summary,
        "closed-keys": cmd_closed_keys,
        "append": cmd_append,
    }[args.cmd](args)


if __name__ == "__main__":
    main()
