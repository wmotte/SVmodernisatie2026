#!/usr/bin/env python3
"""Python-based Git Worktree conflict check utility.
Replaces the external `clash` dependency to make parallel agent environments
fully self-contained.
"""

import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

# Match common bible book abbreviations and a chapter number in branch names.
BRANCH_PARSER = re.compile(
    r"\b(luk|mat|mrk|jhn|act|rom|heb|cor|gal|eph|php|col|the|tim|tit|phm|pet|jos|jud|rev|1co|2co|1tim|2tim|1pe|2pe|1jo|2jo|3jo)\D*(\d+)",
    re.IGNORECASE,
)


def get_worktrees() -> list[dict]:
    try:
        res = subprocess.run(
            ["git", "worktree", "list"], capture_output=True, text=True, check=True
        )
    except Exception as e:
        print(f"Error running git worktree list: {e}", file=sys.stderr)
        return []

    worktrees = []
    for line in res.stdout.strip().splitlines():
        if not line:
            continue
        # Format is: <path> <commit> [<branch>]
        parts = line.split()
        path = parts[0]
        branch = ""
        if len(parts) > 2 and parts[-1].startswith("[") and parts[-1].endswith("]"):
            branch = parts[-1][1:-1]

        target_book = None
        target_chapter = None
        if branch:
            match = BRANCH_PARSER.search(branch)
            if match:
                target_book = match.group(1).upper()
                target_chapter = int(match.group(2))

        worktrees.append(
            {
                "path": path,
                "branch": branch,
                "target": f"{target_book} {target_chapter}" if target_book else None,
                "book": target_book,
                "chapter": target_chapter,
            }
        )
    return worktrees


def main() -> None:
    worktrees = get_worktrees()
    if not worktrees:
        print("No worktrees found.")
        sys.exit(0)

    # Detect conflicts (same book and chapter)
    target_map = defaultdict(list)
    for wt in worktrees:
        if wt["target"]:
            target_map[wt["target"]].append(wt)

    conflicts = {target: wts for target, wts in target_map.items() if len(wts) > 1}

    print(f"{'Path':<60} {'Branch':<30} {'Target':<10} {'Status':<10}")
    print("-" * 115)
    for wt in worktrees:
        status = "OK"
        if wt["target"] in conflicts:
            status = "CONFLICT!"
        target_str = wt["target"] if wt["target"] else "-"
        path_str = wt["path"]
        if len(path_str) > 57:
            path_str = "..." + path_str[-54:]

        print(f"{path_str:<60} {wt['branch']:<30} {target_str:<10} {status:<10}")

    if conflicts:
        print(
            "\n[WARNING] Overlapping worktrees detected working on the same book/chapter:"
        )
        for target, wts in conflicts.items():
            print(f"  Target: {target}")
            for wt in wts:
                print(f"    - Branch: {wt['branch']} in {wt['path']}")
        print("\nRules for concurrency (WORKTREE_WORKFLOW.md):")
        print(
            "  - NO two worktrees should work on the same book and chapter simultaneously!"
        )
        sys.exit(1)
    else:
        print("\n[OK] No worktree chapter conflicts detected.")
        sys.exit(0)


if __name__ == "__main__":
    main()
