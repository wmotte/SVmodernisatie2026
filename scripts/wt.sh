#!/usr/bin/env bash
# wt.sh — beheer git worktrees voor parallelle Claude Code sessies
# Zie WORKTREE_WORKFLOW.md voor het volledige protocol.
#
# Subcommando's:
#   wt new <suffix> [base]   Maak worktree feature/<suffix> vanaf base (default: main)
#   wt list                  Toon worktrees + branches + clash-status
#   wt rm <suffix>           Verwijder worktree (branch blijft staan, conform GIT_WORKFLOW)
#   wt clash                 Pass-through naar `clash status`
#   wt root                  Print de canonical main-repo root
#
# Layout:
#   Main repo: $HOME/Desktop/projects/SVmodernisatie2026
#   Worktrees: $HOME/Desktop/projects/SVmodernisatie2026.wt/<suffix>
#   memory/   in elke worktree is een symlink naar de main-repo memory/

set -euo pipefail

MAIN_REPO="$HOME/Desktop/projects/SVmodernisatie2026"
WT_ROOT="$HOME/Desktop/projects/SVmodernisatie2026.wt"

usage() {
    sed -n '2,16p' "$0"
    exit "${1:-0}"
}

cmd_new() {
    local suffix="${1:-}"
    local base="${2:-main}"
    [[ -z "$suffix" ]] && { echo "wt new: suffix vereist (bv. luk4-parallel)" >&2; exit 1; }

    local branch="feature/$suffix"
    local wt_path="$WT_ROOT/$suffix"

    [[ -e "$wt_path" ]] && { echo "wt new: $wt_path bestaat al" >&2; exit 1; }

    mkdir -p "$WT_ROOT"
    cd "$MAIN_REPO"

    # Up-to-date base voorkomt dat de nieuwe worktree achter loopt op main.
    git fetch origin "$base" --quiet
    if git show-ref --verify --quiet "refs/heads/$branch"; then
        echo "Branch $branch bestaat al; worktree gekoppeld aan bestaande branch."
        git worktree add "$wt_path" "$branch"
    else
        git worktree add -b "$branch" "$wt_path" "origin/$base"
    fi

    # memory/ shared via symlink — SQLite WAL handelt concurrent reads;
    # writes (memory.py add/sync) gaan onder flock in de skill.
    if [[ -e "$wt_path/memory" ]]; then
        rm -rf "$wt_path/memory"
    fi
    ln -s "$MAIN_REPO/memory" "$wt_path/memory"

    # .env meekopiëren (staat in .gitignore, dus niet in checkout).
    if [[ -f "$MAIN_REPO/.env" ]]; then
        cp "$MAIN_REPO/.env" "$wt_path/.env"
    fi

    # .agents/settings.local.json meekopiëren — bevat permission-allowlist
    # en hooks. Zonder dit hangen subagents in de worktree op routine-prompts
    # (bv. Edit op scripts/lint_carryovers.py) omdat de allowlist daar niet
    # gelezen wordt. Snapshot bij creatie: latere wijzigingen in main propageren
    # niet automatisch (bewust — geen drift tijdens lopende sessie).
    if [[ -f "$MAIN_REPO/.agents/settings.local.json" ]]; then
        mkdir -p "$wt_path/.agents"
        cp "$MAIN_REPO/.agents/settings.local.json" "$wt_path/.agents/settings.local.json"
    fi

    echo
    echo "Worktree klaar: $wt_path"
    echo "Branch:         $branch (vanaf origin/$base)"
    echo
    echo "Volgende stap:"
    echo "  cd $wt_path && claude"
}

cmd_list() {
    cd "$MAIN_REPO"
    git worktree list
    echo
    if command -v clash >/dev/null 2>&1; then
        echo "--- clash status ---"
        clash status || true
    else
        echo "(clash niet gevonden — installeer voor conflict-detectie)"
    fi
}

cmd_rm() {
    local suffix="${1:-}"
    [[ -z "$suffix" ]] && { echo "wt rm: suffix vereist" >&2; exit 1; }
    local wt_path="$WT_ROOT/$suffix"

    [[ ! -e "$wt_path" ]] && { echo "wt rm: $wt_path bestaat niet" >&2; exit 1; }

    cd "$MAIN_REPO"
    # symlink eerst losmaken zodat git worktree remove de memory-dir niet raakt
    if [[ -L "$wt_path/memory" ]]; then
        rm "$wt_path/memory"
    fi
    git worktree remove "$wt_path"
    # Branch wordt NIET verwijderd — conform GIT_WORKFLOW.md verboden patronen.
    echo "Worktree $wt_path verwijderd. Branch blijft staan."
}

cmd_clash() {
    cd "$MAIN_REPO"
    clash status "$@"
}

cmd_root() {
    echo "$MAIN_REPO"
}

case "${1:-}" in
    new)   shift; cmd_new "$@" ;;
    list)  shift; cmd_list "$@" ;;
    rm)    shift; cmd_rm "$@" ;;
    clash) shift; cmd_clash "$@" ;;
    root)  cmd_root ;;
    -h|--help|help|"") usage 0 ;;
    *)     echo "wt: onbekend commando '$1'" >&2; usage 1 ;;
esac
