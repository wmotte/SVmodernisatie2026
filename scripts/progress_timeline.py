#!/usr/bin/env python3
"""Temporeel voortgangspatroon van de SV-modernisatie.

Loopt door de git-historie en telt per commit hoeveel verzen er op dat
moment in output/<BOEK>/<BOEK>.<H>.json staan (review.*.json telt niet mee).
Aggregeert naar kalenderdag: cumulatief aantal gemoderniseerde verzen,
dagdelta, commits per dag en cumulatief gemergede PR's.

Output:
  - docs/progress_timeline.csv   (datum, commits, merged_prs_cum, verzen_delta, verzen_cum, pct)
  - docs/progress_timeline.png   (matplotlib-lijngrafiek; overslaan als matplotlib ontbreekt)
  - ASCII-grafiek naar stdout

Verzen tellen alleen mee als ze in output/ aanwezig zijn op dat commit;
de curve is dus de feitelijke staat van de repo per dag tot het heden.

Gebruik:  python3 scripts/progress_timeline.py
Reproduceerbaar; geen argumenten nodig.
"""
from __future__ import annotations

import csv
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOCS = REPO / "docs"
CSV_OUT = DOCS / "progress_timeline.csv"
PNG_OUT = DOCS / "progress_timeline.png"

# output/<BOEK>/<BOEK>.<H>.json  -> verstekst; review.*.json uitsluiten.
VERSE_PATH = re.compile(r"^output/([A-Z0-9]+)/\1\.\d+\.json$")


def git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(REPO), *args],
        check=True, capture_output=True, text=True,
    ).stdout


def total_nt_verses() -> int:
    """Totaal NT-verzen uit het bronkorpus input.sv/."""
    total = 0
    src = REPO / "input.sv"
    for book in sorted(src.iterdir()):
        if not book.is_dir():
            continue
        for f in book.glob(f"{book.name}.*.json"):
            try:
                total += len(json.loads(f.read_text()).get("verses", []))
            except (json.JSONDecodeError, OSError):
                pass
    return total


def commits_touching_output() -> list[tuple[str, str]]:
    """(hash, YYYY-MM-DD) chronologisch voor commits die output/ wijzigen."""
    out = git("log", "--reverse", "--date=format:%Y-%m-%d",
              "--format=%H|%cd", "--", "output")
    rows = []
    for line in out.splitlines():
        if "|" in line:
            h, d = line.split("|", 1)
            rows.append((h, d))
    return rows


def blob_verse_counts(commit: str, cache: dict[str, int]) -> int:
    """Som van versaantallen over alle verstekst-blobs in output/ op `commit`."""
    tree = git("ls-tree", "-r", commit, "--", "output")
    total = 0
    pending: list[str] = []  # blob-hashes nog niet in cache
    paths: list[str] = []
    for line in tree.splitlines():
        # "<mode> blob <hash>\t<path>"
        meta, _, path = line.partition("\t")
        if not VERSE_PATH.match(path):
            continue
        parts = meta.split()
        if len(parts) < 3 or parts[1] != "blob":
            continue
        h = parts[2]
        if h in cache:
            total += cache[h]
        else:
            pending.append(h)
            paths.append(h)
    # lees onbekende blobs in batch
    for h in pending:
        content = git("cat-file", "-p", h)
        try:
            n = len(json.loads(content).get("verses", []))
        except json.JSONDecodeError:
            n = 0
        cache[h] = n
        total += n
    return total


def merged_prs_by_day() -> dict[str, int]:
    """Aantal gemergede PR's per dag (commit-subject 'Merge pull request')."""
    out = git("log", "--date=format:%Y-%m-%d", "--format=%cd|%s")
    per_day: dict[str, int] = defaultdict(int)
    for line in out.splitlines():
        d, _, subj = line.partition("|")
        if subj.startswith("Merge pull request"):
            per_day[d] += 1
    return per_day


def ascii_chart(rows: list[dict], width: int = 48) -> str:
    if not rows:
        return "(geen data)"
    peak = max(r["verzen_cum"] for r in rows) or 1
    lines = ["", "Cumulatief gemoderniseerde verzen per dag", ""]
    for r in rows:
        filled = round(r["verzen_cum"] / peak * width)
        bar = "█" * filled + "░" * (width - filled)
        lines.append(
            f"{r['datum']}  {bar} {r['verzen_cum']:>5}  "
            f"(+{r['verzen_delta']:>4}, {r['commits']:>3} commits, {r['pct']:>4.1f}%)"
        )
    return "\n".join(lines)


def main() -> int:
    nt_total = total_nt_verses()
    commits = commits_touching_output()
    if not commits:
        print("Geen commits raken output/.", file=sys.stderr)
        return 1

    # cumulatief versaantal = staat van output/ bij het laatste commit van elke dag.
    cache: dict[str, int] = {}
    last_commit_per_day: dict[str, str] = {}
    commits_per_day: dict[str, int] = defaultdict(int)
    for h, d in commits:
        last_commit_per_day[d] = h  # chrono volgorde -> overschrijft tot laatste
        commits_per_day[d] += 1

    prs_per_day = merged_prs_by_day()

    rows: list[dict] = []
    prev_cum = 0
    pr_cum = 0
    for day in sorted(last_commit_per_day):
        cum = blob_verse_counts(last_commit_per_day[day], cache)
        pr_cum += prs_per_day.get(day, 0)
        rows.append({
            "datum": day,
            "commits": commits_per_day[day],
            "merged_prs_cum": pr_cum,
            "verzen_delta": cum - prev_cum,
            "verzen_cum": cum,
            "pct": round(cum / nt_total * 100, 2),
        })
        prev_cum = cum

    DOCS.mkdir(exist_ok=True)
    with CSV_OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(ascii_chart(rows))
    print(f"\nNT-totaal: {nt_total} verzen.  "
          f"Heden: {rows[-1]['verzen_cum']} ({rows[-1]['pct']}%).")
    print(f"CSV  -> {CSV_OUT.relative_to(REPO)}")

    try:
        write_png(rows, nt_total)
        print(f"PNG  -> {PNG_OUT.relative_to(REPO)}")
    except ImportError:
        print("PNG  -> overgeslagen (matplotlib niet geïnstalleerd; "
              "`pip install matplotlib`).")
    return 0


def write_png(rows: list[dict], nt_total: int) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from datetime import date

    xs = [date.fromisoformat(r["datum"]) for r in rows]
    ys = [r["verzen_cum"] for r in rows]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.fill_between(xs, ys, step="post", alpha=0.18, color="#2b6cb0")
    ax.step(xs, ys, where="post", color="#2b6cb0", linewidth=2.2,
            marker="o", markersize=4)
    ax.axhline(nt_total, color="#c53030", linestyle="--", linewidth=1,
               label=f"NT-totaal ({nt_total})")

    for r, x, y in zip(rows, xs, ys):
        ax.annotate(f"{y}\n{r['pct']:.0f}%", (x, y),
                    textcoords="offset points", xytext=(0, 8),
                    ha="center", fontsize=8, color="#1a365d")

    ax.set_title("SV-modernisatie — cumulatief gemoderniseerde verzen tot heden")
    ax.set_ylabel("Verzen (cumulatief)")
    ax.set_xlabel("Datum")
    ax.set_ylim(0, nt_total * 1.05)
    ax.legend(loc="upper left")
    ax.grid(True, axis="y", alpha=0.25)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(PNG_OUT, dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    raise SystemExit(main())
