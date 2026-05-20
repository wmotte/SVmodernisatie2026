#!/usr/bin/env python3
"""Unified linter script that runs all SV modernization linters:
- lint_archaismen.py
- lint_carryovers.py
- lint_false_friends.py

Exits with non-zero if any underlying linter fails (returns non-zero exit code).
"""

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run all SV modernization linters.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--output", help="Path to a single output JSON file.")
    group.add_argument("--root", help="Directory path to scan recursively.")
    parser.add_argument("--terse", action="store_true", help="Compact textual output.")

    args = parser.parse_args()

    scripts_dir = Path(__file__).resolve().parent

    # Find the target files to lint
    if args.output:
        files = [Path(args.output)]
    else:
        files = sorted(Path(args.root).rglob("*.json"))

    if not files:
        print("No JSON files found to lint.", flush=True)
        sys.exit(0)

    any_failed = False

    # 1. Run lint_archaismen.py
    print("=== Running archaismen linter ===", flush=True)
    arch_cmd = [sys.executable, str(scripts_dir / "lint_archaismen.py"), "lint"]
    if args.output:
        arch_cmd.extend(["--output", args.output])
    else:
        arch_cmd.extend(["--root", args.root])
    if args.terse:
        arch_cmd.append("--terse")

    res = subprocess.run(arch_cmd)
    if res.returncode != 0:
        any_failed = True
    print(flush=True)

    # 2. Run lint_false_friends.py
    print("=== Running false friends linter ===", flush=True)
    ff_cmd = [sys.executable, str(scripts_dir / "lint_false_friends.py"), "lint"]
    if args.output:
        ff_cmd.extend(["--output", args.output])
    else:
        ff_cmd.extend(["--root", args.root])
    if args.terse:
        ff_cmd.append("--terse")

    res = subprocess.run(ff_cmd)
    if res.returncode != 0:
        any_failed = True
    print(flush=True)

    # 3. Run lint_carryovers.py
    # Note: lint_carryovers.py only supports single file (--output), so we run it per file.
    print("=== Running carryovers linter ===", flush=True)
    for fp in files:
        if len(files) > 1 and not args.terse:
            print(f"File: {fp}", flush=True)
        co_cmd = [
            sys.executable,
            str(scripts_dir / "lint_carryovers.py"),
            "lint",
            "--output",
            str(fp),
        ]
        if args.terse:
            co_cmd.append("--terse")
        res = subprocess.run(co_cmd)
        if res.returncode != 0:
            any_failed = True

    if any_failed:
        print("\n[FAIL] One or more linters detected issues.", flush=True)
        sys.exit(1)
    else:
        print("\n[OK] All linters passed.", flush=True)
        sys.exit(0)


if __name__ == "__main__":
    main()
