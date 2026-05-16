#!/usr/bin/env bash
# Maak de batch-branch klaar vanaf origin/main.
# Gebruikt door sv-batch-orchestrate Stap 2 (pre-flight) en Stap 6.5 stap 3.
# Vervangt het inline multi-regel-bashblok zodat de orchestrator-context
# niet vol loopt met herhaalde commandotekst.
#
# Gebruik:  scripts/mkbatch.sh <boek-lowercase> <H> <V_START> <V_EIND>
#       of: scripts/mkbatch.sh <boek-lowercase> <H> adversarial-fix
# Uitvoer:  BRANCH=<branch-naam>
set -euo pipefail

BOEK=$1
H=$2

if [ "${3:-}" = "adversarial-fix" ]; then
    BRANCH="feature/${BOEK}-${H}-adversarial-fix"
else
    V_START=$3
    V_EIND=$4
    BRANCH="feature/${BOEK}${H}-batch-${V_START}-${V_EIND}"
fi

if git ls-remote --heads origin "$BRANCH" | grep -q "$BRANCH"; then
    BRANCH="${BRANCH}-modernize"
fi

git fetch origin main --quiet
git checkout -B "$BRANCH" origin/main >/dev/null 2>&1
echo "BRANCH=$BRANCH"
