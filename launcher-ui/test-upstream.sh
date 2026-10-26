#!/usr/bin/env bash
# Runs CleanYourTV's test suite (tests/) the way it runs upstream, in a throwaway copy of this repository.
#
# Usage: launcher-ui/test-upstream.sh [unittest arguments]      e.g. -v, or -k gen_tables
#
# Many of those tests read README.md, and in this fork README.md is CleanYourTV UI's own page: upstream's is
# README.cleanyourtv.md, refreshed by every sync (.github/workflows/sync-upstream.yml). So the copy gets upstream's
# README back as README.md, without the line the sync puts on top, and loses the two READMEs only this fork has
# (README.cleanyourtv.md, README.pt-BR.md), which the translation tests would count as extra translations.
# Nothing in this checkout changes. Uncommitted changes to tracked files are tested too; untracked files are not.
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$(pwd)"
PY="$ROOT/tools/venv/bin/python"
[ -x "$PY" ] || PY="$ROOT/tools/venv/Scripts/python.exe"
[ -x "$PY" ] || { echo "run: python3 -m venv tools/venv && tools/venv/bin/pip install -r tools/requirements.txt" >&2; exit 1; }

# git stash create records the working tree as a commit without touching it or the stash list; empty when clean.
REV="$(git stash create)"
REV="${REV:-HEAD}"
COPY="$(mktemp -d "${TMPDIR:-/tmp}/cyt-ui-tests.XXXXXX")"
cleanup() { git -C "$ROOT" worktree remove --force "$COPY" 2>/dev/null || rm -rf "$COPY"; }
trap cleanup EXIT
git worktree add --quiet --detach "$COPY" "$REV"

cd "$COPY"
awk 'NR == 1 && /^> \*\*CleanYourTV UI:\*\*/ { skip = 1; next } skip && NR == 2 && $0 == "" { next } { print }' \
  README.cleanyourtv.md > README.md
rm -f README.cleanyourtv.md README.pt-BR.md
# The suite starts tools/*.sh, which look for tools/venv next to them.
ln -s "$ROOT/tools/venv" tools/venv
echo "Testing $(git -C "$ROOT" rev-parse --short HEAD)$([ "$REV" = HEAD ] || echo ' with uncommitted changes') with upstream's README.md"
"$PY" -m unittest discover -s tests "$@"
