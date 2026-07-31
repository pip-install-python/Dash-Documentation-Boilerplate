#!/usr/bin/env bash
# Start the development server with THIS project's interpreter.
#
#   ./scripts/dev.sh              # backend from .env (or flask)
#   ./scripts/dev.sh fastapi      # override for one run
#
# The reason this exists: an IDE run configuration remembers an interpreter,
# and a configuration pointing at a different project's virtualenv starts the
# app against that project's dependency versions. Everything looks fine and
# the app serves older behaviour. Launching through this script removes the
# choice — the venv is resolved from the script's own location, not from
# whatever `python` happens to be on PATH or in an IDE setting.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python="$here/.venv/bin/python"

if [ ! -x "$python" ]; then
    echo "No virtualenv at $python" >&2
    echo "Create it with:" >&2
    echo "    python3 -m venv .venv && .venv/bin/pip install -r requirements.txt" >&2
    exit 1
fi

if [ $# -gt 0 ]; then
    export DASH_BACKEND="$1"
fi

cd "$here"
exec "$python" run.py
