#!/usr/bin/env bash
# Run one CI matrix leg's DEPENDENCY SET locally.  (1.6.45 item 6, note 107)
#
# WHY THIS EXISTS.  "Three lanes green" on one interpreter proves the lanes'
# CODE PATHS and says nothing about what each leg INSTALLS.  1.6.44 went red
# three times on that distinction: a test shelled out to flake8 (lint job
# only), a render path used Pillow (a build-script dependency), and a test
# imported lib.asgi_routes -> fastapi (installed on the fastapi leg alone).
# Every one was green on a developer machine that happened to have all three.
#
# The legs differ ONLY in what is installed:
#   flask    lacks fastapi, starlette, quart, Pillow, flake8
#   fastapi  lacks quart, Pillow, flake8
#   quart    lacks fastapi, starlette, Pillow, flake8
#
# SANDBOX NOTE, learned the hard way.  Do NOT `pip install --upgrade pip`
# inside a proxied sandbox: pip >= 26 validates against the system trust
# store and rejects the proxy's certificate, so every index fetch dies with
# SSLCertVerificationError.  The venv's stock pip works.  If the venv still
# cannot be built (the vendored sdist's PEP 517 build fetches its own build
# deps), this script FALLS BACK to resolved masks and says so — loudly,
# because a fallback that looked like the real thing would be the same
# species of lie the script exists to prevent.
#
#   scripts/ci_leg.sh flask
#   scripts/ci_leg.sh fastapi --masks     # skip the venv attempt
set -uo pipefail

BACKEND="${1:-}"
case "$BACKEND" in
  flask|fastapi|quart) ;;
  *) echo "usage: $0 <flask|fastapi|quart> [--masks]" >&2; exit 2 ;;
esac
FORCE_MASKS=0
[ "${2:-}" = "--masks" ] && FORCE_MASKS=1

REPO="$(cd "$(dirname "$0")/.." && pwd)"
WORK="${TMPDIR:-/tmp}/ci_leg_$BACKEND"
cd "$REPO" || exit 1

# The interpreter CI's main rows use; fall back to whatever python3 is here.
PY="$(command -v python3.14 || command -v python3)"
echo "== CI leg: $BACKEND =="
echo "interpreter: $PY ($("$PY" -V 2>&1))"

run_suite() {   # $1 = python to run pytest with, $2... = extra env assignments
  local py="$1"; shift
  # NO -q: pytest.ini already carries one and a second suppresses the summary
  # line entirely (note 99) — the run looks fine and reports no counts.
  env "$@" DASH_BACKEND="$BACKEND" "$py" -m pytest tests
}

# ---------------------------------------------------------------- venv path --
build_venv() {
  rm -rf "$WORK"
  "$PY" -m venv "$WORK" || return 1
  local pip="$WORK/bin/pip"
  # ci.yml's install block, in its order.  requirements.txt is installed from
  # the repo root because it references the vendored sdist by relative path.
  "$pip" install -q -r requirements.txt || return 1
  "$pip" install -q --no-deps markdown2dash==0.1.2 || return 1
  if [ "$BACKEND" != "flask" ]; then
    "$pip" install -q "dash[$BACKEND]" httpx || return 1
    "$pip" install -q "dash-improve-my-llms[$BACKEND]>=2.3.4" || return 1
  fi
  "$pip" install -q pytest pytest-cov || return 1
  return 0
}

if [ "$FORCE_MASKS" -eq 0 ] && build_venv 2>"$WORK.err"; then
  echo "-- dependency set (ABSENCES are the evidence) --"
  for pkg in fastapi starlette quart pillow flake8 dash dash-improve-my-llms; do
    line="$("$WORK/bin/pip" list 2>/dev/null | grep -iE "^$pkg " || true)"
    if [ -n "$line" ]; then echo "   present : $line"; else echo "   ABSENT  : $pkg"; fi
  done
  echo "-- suite --"
  run_suite "$WORK/bin/python"
  exit $?
fi

# --------------------------------------------------------------- mask path --
echo "!! venv could not be built here — FALLING BACK TO RESOLVED MASKS"
[ -s "$WORK.err" ] && echo "   reason: $(tail -1 "$WORK.err")"
echo "   (a mask run is weaker than a venv run: it proves this leg's absences,"
echo "    not this leg's versions.  Say so wherever you quote the counts.)"

MASKS="$WORK/masks"
rm -rf "$MASKS"; mkdir -p "$MASKS"

# Resolve what this leg actually installs, rather than assuming it.  Assuming
# is how the first attempt at this masked pydantic and httpx — both of which
# CI's flask leg HAS (dash requires pydantic; dash-clerk-auth requires httpx)
# — and manufactured a failure that did not exist.
REQ="$WORK/req.txt"
cp requirements.txt "$REQ"
if [ "$BACKEND" != "flask" ]; then
  printf '\ndash[%s]\nhttpx\ndash-improve-my-llms[%s]>=2.3.4\n' "$BACKEND" "$BACKEND" >> "$REQ"
fi
LOCAL_PY="$REPO/.venv/bin/python"
[ -x "$LOCAL_PY" ] || LOCAL_PY="$PY"
"$LOCAL_PY" -m pip install --dry-run --ignore-installed --quiet \
    --report "$WORK/report.json" -r "$REQ" >/dev/null 2>&1 || {
  echo "   cannot resolve the leg's package set either — no verification possible"
  exit 3
}

"$LOCAL_PY" - "$WORK" "$BACKEND" <<'PYGEN'
import json, pathlib, sys
work, backend = pathlib.Path(sys.argv[1]), sys.argv[2]
resolved = {i["metadata"]["name"].lower()
            for i in json.load(open(work / "report.json"))["install"]}
# Import names differ from distribution names for exactly one of these.
candidates = {"fastapi": "fastapi", "starlette": "starlette", "quart": "quart",
              "pillow": "PIL", "flake8": "flake8"}
absent = {dist: mod for dist, mod in candidates.items() if dist not in resolved}
(work / "absent.json").write_text(json.dumps(absent))
sitecustomize = work / "masks" / "sitecustomize.py"
sitecustomize.parent.mkdir(parents=True, exist_ok=True)
# sys.modules[name] = None makes `import X` raise ModuleNotFoundError AND
# importlib.util.find_spec(X) return None.  A raising stub package only does
# the first, so a find_spec guard would still think the package is present —
# which is how two guards were written wrong before this was understood.
sitecustomize.write_text(
    "import sys\n"
    f"for _m in {sorted(absent.values())!r}:\n"
    "    sys.modules[_m] = None\n"
)
print("-- resolved dependency set: "
      f"{len(resolved)} packages; absent here: {sorted(absent)} --")
PYGEN

echo "-- control: the masks bite --"
_CI_LEG_WORK="$WORK" PYTHONPATH="$MASKS" "$LOCAL_PY" - <<'PYCTL'
import json, os, pathlib
absent = json.load(open(pathlib.Path(os.environ["_CI_LEG_WORK"]) / "absent.json"))
for dist, mod in sorted(absent.items()):
    try:
        __import__(mod)
        print(f"   {mod}: STILL IMPORTABLE — the mask did not apply")
        raise SystemExit(4)
    except ModuleNotFoundError:
        print(f"   {mod}: masked")
PYCTL
CTL=$?
[ "$CTL" -ne 0 ] && { echo "   masks ineffective — refusing to report a green"; exit 4; }

echo "-- suite --"
run_suite "$LOCAL_PY" PYTHONPATH="$MASKS"
