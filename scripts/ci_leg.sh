#!/usr/bin/env bash
# Run one CI matrix leg — its CODE, its DEPENDENCY SET, and its BATTERY.
# (1.6.45 item 6, rewritten by rider (b); notes 107 and 124.)
#
# WHY THIS EXISTS.  1.6.44 went red three times on one distinction: "three
# lanes green" on one interpreter proves the lanes' CODE PATHS and says
# nothing about what each leg INSTALLS.  A test shelled out to flake8 (lint
# job only); a render path used Pillow (a build-script dependency); a test
# imported lib.asgi_routes -> fastapi (fastapi leg only).  All three were
# green on a machine that happened to have all of them.
#
# THE CLONE AND THE VENV TEST DIFFERENT THINGS, and the rewrite exists
# because the first version conflated them: the CLONE tests the CODE (an
# untracked file that only exists on this machine cannot help it pass), and
# only a FRESH VENV tests the RESOLUTION (leaflet's reused .venv hid a red).
# You need both, so this does both.
#
# AND THE BATTERY, which no seat could run until now: CI's "boot under a
# production server + battery" step needs a listening socket, which every
# sandbox in this fleet refuses.  That step hid two of three wave-1 reds.
# `scripts/smoke_inproc.py` runs the battery's own main() against the app
# in-process — Flask's test client on the flask leg, httpx ASGITransport on
# the two ASGI legs.
#
# SANDBOX NOTES, each learned the hard way and none of them obvious:
#   * do NOT `pip install --upgrade pip` behind a proxy: pip >= 26 validates
#     against the system trust store, rejects the proxy's certificate, and
#     every index fetch dies with SSLCertVerificationError.  PIP_CERT does
#     not override it.  The venv's stock pip works.  Never follow pip's own
#     upgrade notice here.
#   * `--python` goes BEFORE the subcommand (`pip --python X install ...`),
#     which is how a 3.12-made venv's pip builds for the 3.14 leg.
#   * `env -i` with the venv's bin FIRST on PATH: a bare `python3` under a
#     cleared environment is macOS's 3.9, not the leg's interpreter.
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
# A PER-UID TEMP DIR IS SHARED STATE. $TMPDIR here is /tmp/claude-<uid>,
# shared by every seat running as this user, so `ci_leg_$BACKEND` put two
# repos' clones in ONE directory: pannellum measured its own flask clone
# sitting at another fork's commit while its other two legs were its own,
# and the contaminated run reported EXACTLY its clean numbers — a wrong
# green that announces nothing. Every work path under a shared temp dir
# carries the repo's identity.
#
# basename alone is not enough: a fork and the template it came from, or
# two checkouts of one fork, still collide. The cksum of the full path
# separates them; the basename stays so the directory is still readable.
REPO_KEY="$(basename "$REPO")-$(printf '%s' "$REPO" | cksum | cut -d' ' -f1)"
WORK="${TMPDIR:-/tmp}/ci_leg_${REPO_KEY}_$BACKEND"
CLONE="$WORK/clone"
VENV="$WORK/venv"

echo "== CI leg: $BACKEND =="

# ------------------------------------------------------------------- lock --
# REPO_KEY separates FORKS; it does not separate two runs of the SAME fork,
# and `rm -rf "$CLONE"` is the operation that eats a concurrent run
# mid-suite. leaflet's rider, 2026-09-12. Exit 5, because 3 and 4 are taken
# ("no verification possible" and "masks ineffective") and a reader of the
# exit code should not have to guess which refusal happened.
mkdir -p "$WORK"
LOCK="$WORK/.lock"
if [ -f "$LOCK" ]; then
  holder="$(cat "$LOCK" 2>/dev/null || true)"
  if [ -n "$holder" ] && kill -0 "$holder" 2>/dev/null; then
    echo "!! another run (pid $holder) holds $WORK — refusing rather than"
    echo "   deleting its clone from under it. Wait, or use a different repo"
    echo "   checkout; two runs of ONE checkout cannot share a work dir."
    exit 5
  fi
  echo "-- clearing a stale lock (pid ${holder:-unknown} is gone) --"
  rm -f "$LOCK"
fi
printf '%s' "$$" > "$LOCK"
trap 'rm -f "$LOCK"' EXIT INT TERM

# ---------------------------------------------------------- the clean clone --
# Shallow, from the working tree's HEAD.  An untracked file cannot help this
# pass — which is how 1.6.44 caught `.claude/session-name` being gitignored
# after its tests had been passing off the working directory for an hour.
rm -rf "$CLONE"
git -C "$REPO" clone --quiet --depth 1 --no-local "file://$REPO" "$CLONE" 2>/dev/null \
  || git -C "$REPO" clone --quiet --depth 1 "file://$REPO" "$CLONE" \
  || { echo "clone FAILED"; exit 1; }
CLONED_SHA="$(git -C "$CLONE" rev-parse HEAD)"

# THE INTERPRETER IS CHOSEN BY WHETHER ITS VENV CAN INSTALL, not by
# preference (leaflet's rider, 2026-09-12). 3.14.4's ensurepip ships pip
# 26.1, which validates TLS through the macOS truststore and ignores
# --cert/PIP_CERT, so behind a proxy the sdist's isolated build env cannot
# reach the index (OSStatus -26276) and the vendored dash-clerk-auth sdist
# fails to build. Measured by leaflet: python3.14 -> pip 26.1 -> SSL
# verification error; python3.12 -> pip 24.0 -> installs fine. A box where
# 3.14's pip works still gets 3.14; a box where it does not gets a REAL
# VENV on the next candidate rather than the weaker mask path.
PY_CANDIDATES="python3.14 python3.13 python3.12 python3.11 python3"

# certifi's bundle, for the scrubbed environment below. Empty if certifi is
# not importable, in which case the variables are simply not set.
CERT_FILE="$("$REPO/.venv/bin/python" -c 'import certifi;print(certifi.where())' 2>/dev/null || true)"

report_env() {   # $1 = the python that will run the suite
  echo "-- environment --"
  echo "   pwd          $(pwd)"
  echo "   cloned sha   $CLONED_SHA"
  echo "   interpreter  $1 ($("$1" -V 2>&1))"
  echo "   pip          $("$1" -m pip --version 2>&1 | cut -d" " -f1-2)"
  echo "   pytest       $("$1" -m pytest --version 2>&1 | /usr/bin/head -1)"
}

report_collected() {  # $1 = python, $2... = env assignments
  local py="$1"; shift
  local n
  # No extra -q here either: pytest.ini already carries one, and a second
  # turns --collect-only's per-test listing into a per-FILE summary, so the
  # count comes out as 0.  Read the "N tests collected" line pytest prints.
  n="$(env "$@" DASH_BACKEND="$BACKEND" "$py" -m pytest tests --collect-only 2>/dev/null \
        | grep -oE '[0-9]+ tests? collected' | /usr/bin/head -1)"
  echo "   collected    ${n:-UNKNOWN — the collect step printed no count}"
}

# --------------------------------------------------------------- venv path --
build_venv() {   # $1 = the interpreter to build with
  local interp="$1"
  rm -rf "$VENV"
  "$interp" -m venv "$VENV" || return 1
  local pip="$VENV/bin/pip"
  # ci.yml's install block, in its order.  Run from the CLONE so the vendored
  # sdist's relative path resolves against the tree under test.
  ( cd "$CLONE" && "$pip" install -q -r requirements.txt ) || return 1
  ( cd "$CLONE" && "$pip" install -q --no-deps markdown2dash==0.1.2 ) || return 1
  if [ "$BACKEND" != "flask" ]; then
    ( cd "$CLONE" && "$pip" install -q "dash[$BACKEND]" httpx ) || return 1
    ( cd "$CLONE" && "$pip" install -q "dash-improve-my-llms[$BACKEND]>=2.3.4" ) || return 1
  fi
  ( cd "$CLONE" && "$pip" install -q pytest pytest-cov ) || return 1
  return 0
}

run_leg() {   # $1 = python, $2... = extra env assignments
  local py="$1"; shift
  cd "$CLONE" || return 1
  report_env "$py"
  report_collected "$py" "$@"
  echo "-- suite --"
  # NO -q: pytest.ini carries one and a second suppresses the summary line
  # entirely (note 99) — the run looks fine and reports no counts at all.
  env "$@" DASH_BACKEND="$BACKEND" "$py" -m pytest tests
  local suite=$?
  echo "-- battery (in-process; CI's boot-and-battery step, without a socket) --"
  # SMOKE_PYTHON_DECLARED=ignore for the same reason ci.yml's matrix boot step
  # sets it: this interpreter is not the Dockerfile's fleet Python, so the
  # python_matches_declared row is off-contract HERE and armed in the docker
  # job and CD's verify, where the interpreter IS the artifact.
  env "$@" DASH_BACKEND="$BACKEND" SMOKE_PYTHON_DECLARED=ignore \
      "$py" scripts/smoke_inproc.py
  local battery=$?
  echo "-- verdict: suite exit $suite, battery exit $battery --"
  [ "$suite" -eq 0 ] && [ "$battery" -eq 0 ]
}

CHOSEN_PY=""
if [ "$FORCE_MASKS" -eq 0 ]; then
  for cand in $PY_CANDIDATES; do
    cand_path="$(command -v "$cand" 2>/dev/null || true)"
    [ -n "$cand_path" ] || continue
    if build_venv "$cand_path" 2>>"$WORK.err"; then
      CHOSEN_PY="$cand_path"
      echo "-- venv built with $cand ($("$cand_path" -V 2>&1)) --"
      break
    fi
    echo "-- $cand: its venv could not install the leg — trying the next --"
  done
fi

if [ -n "$CHOSEN_PY" ]; then
  echo "-- dependency set (ABSENCES are the evidence) --"
  for pkg in fastapi starlette quart pillow flake8 dash dash-improve-my-llms; do
    line="$("$VENV/bin/pip" list 2>/dev/null | grep -iE "^$pkg " || true)"
    if [ -n "$line" ]; then echo "   present : $line"; else echo "   ABSENT  : $pkg"; fi
  done
  # env -i, with the venv's bin FIRST: a bare `python3` under a cleared
  # environment is macOS's 3.9.
  # The proxy and CA variables SURVIVE the scrub. `env -i` strips them, and
  # a battery row that fetches off-host (a CDN og:image, a peer, the hub)
  # then dies on DNS inside a sandbox — muischeduler measured exactly that
  # after fixing the in-process shim to route off-host URLs outward.
  run_leg "$VENV/bin/python" \
      -i HOME="$HOME" PATH="$VENV/bin:/usr/bin:/bin" TMPDIR="${TMPDIR:-/tmp}" \
      CI=true GITHUB_ACTIONS=true APP_ENV=ci \
      HTTPS_PROXY="${HTTPS_PROXY:-}" HTTP_PROXY="${HTTP_PROXY:-}" \
      NO_PROXY="${NO_PROXY:-}" SSL_CERT_FILE="${SSL_CERT_FILE:-$CERT_FILE}" \
      REQUESTS_CA_BUNDLE="${REQUESTS_CA_BUNDLE:-$CERT_FILE}"
  exit $?
fi

# --------------------------------------------------------------- mask path --
echo "!! venv could not be built here — FALLING BACK TO RESOLVED MASKS"
[ -s "$WORK.err" ] && echo "   reason: $(/usr/bin/tail -1 "$WORK.err")"
echo "   (weaker than a venv run: it proves this leg's ABSENCES, not its"
echo "    VERSIONS, and it runs the clone's code with this machine's"
echo "    site-packages.  Say so wherever you quote the counts.)"

MASKS="$WORK/masks"
rm -rf "$MASKS"; mkdir -p "$MASKS"
REQ="$WORK/req.txt"
cp "$CLONE/requirements.txt" "$REQ"
if [ "$BACKEND" != "flask" ]; then
  printf '\ndash[%s]\nhttpx\ndash-improve-my-llms[%s]>=2.3.4\n' "$BACKEND" "$BACKEND" >> "$REQ"
fi
LOCAL_PY="$REPO/.venv/bin/python"
[ -x "$LOCAL_PY" ] || LOCAL_PY="$PY_LOCAL"

# Resolve what this leg actually installs rather than assuming it.  Assuming
# is how the first attempt masked pydantic and httpx — both of which the
# flask leg HAS (dash requires pydantic, dash-clerk-auth requires httpx) —
# and manufactured a failure that did not exist.
( cd "$CLONE" && "$LOCAL_PY" -m pip install --dry-run --ignore-installed --quiet \
    --report "$WORK/report.json" -r "$REQ" ) >/dev/null 2>&1 || {
  echo "   cannot resolve the leg's package set either — no verification possible"
  exit 3
}

"$LOCAL_PY" - "$WORK" <<'PYGEN'
import json, pathlib, sys
work = pathlib.Path(sys.argv[1])
resolved = {i["metadata"]["name"].lower()
            for i in json.load(open(work / "report.json"))["install"]}
candidates = {"fastapi": "fastapi", "starlette": "starlette", "quart": "quart",
              "pillow": "PIL", "flake8": "flake8"}
absent = {d: m for d, m in candidates.items() if d not in resolved}
(work / "absent.json").write_text(json.dumps(absent))
sc = work / "masks" / "sitecustomize.py"
sc.parent.mkdir(parents=True, exist_ok=True)
# sys.modules[name] = None makes `import X` raise ModuleNotFoundError AND
# importlib.util.find_spec(X) return None.  A raising stub only does the
# first, so a find_spec guard still thinks the package is present — which is
# how two guards were written wrong before this was understood.
sc.write_text("import sys\n"
              f"for _m in {sorted(absent.values())!r}:\n"
              "    sys.modules[_m] = None\n")
print(f"-- resolved dependency set: {len(resolved)} packages; "
      f"absent here: {sorted(absent)} --")
PYGEN

echo "-- control: the masks bite --"
if ! _CI_LEG_WORK="$WORK" PYTHONPATH="$MASKS" "$LOCAL_PY" - <<'PYCTL'
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
then
  echo "   masks ineffective — refusing to report a green"
  exit 4
fi

run_leg "$LOCAL_PY" PYTHONPATH="$MASKS" APP_ENV=ci
