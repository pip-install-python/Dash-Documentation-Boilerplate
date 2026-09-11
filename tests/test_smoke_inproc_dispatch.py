"""The in-process shim serves THIS app's host and nothing else.

1.6.45 rider (b) addendum, measured by muischeduler: a shim that answered
every URL in-process let the local catch-all answer a row's absolute fetch of
a CDN-hosted og:image, returning the app shell as text/html — a false red on
a row that was correct. A shim that lies about somebody else's host is worse
than no shim, because its answers look like measurements.

Run in a SUBPROCESS on purpose: importing the shim boots the app and
replaces `urllib.request.urlopen` process-wide, which must not happen inside
the suite.
"""
from __future__ import annotations

import json
import subprocess
import sys

import pytest

from conftest import REPO_ROOT

SHIM = REPO_ROOT / "scripts" / "smoke_inproc.py"

PROBE = r'''
import json, os, sys, urllib.request
_CAP = 1 << 16
sys.argv = ["x"]
src = open("scripts/smoke_inproc.py").read()
# Stop before the shim runs the battery; we only want the patched urlopen.
src = src.split('sys.argv = ["network_smoke.py"')[0]
exec(compile(src, "smoke_inproc", "exec"), {"__name__": "shim"})
out = {}
try:
    with urllib.request.urlopen(
            urllib.request.Request(
                "%(url)s",
                headers={"User-Agent": "curl/8 2plot-internal/probe"}),
            timeout=45) as r:
        out["status"] = r.status
        # READ THE WHOLE BODY, with a cap far above any healthz document and
        # a flag that says whether the cap was reached. The first version
        # read exactly 400 bytes, and `/healthz` embeds `ledger.path` — the
        # checkout's ABSOLUTE path — so the body's length depends on WHERE
        # THE REPO SITS. In a shallow clone it is 337 bytes and parses; from
        # a deeper work dir it crosses 400 and arrives cut mid-token, and
        # the test failed as a JSONDecodeError that pointed at the app
        # rather than at the probe. Measured here: a 427-byte body cut at
        # 400 gives "Unterminated string starting at char 398".
        raw = r.read(_CAP + 1)
        out["truncated"] = len(raw) > _CAP
        out["body"] = raw[:_CAP].decode("utf-8", "replace")
except Exception as exc:
    out["error"] = f"{type(exc).__name__}: {exc}"
print("RESULT " + json.dumps(out))
'''


def _run(url: str, backend: str = "flask", extra_env: dict | None = None) -> dict:
    env = {"PATH": "/usr/bin:/bin", "HOME": "/tmp",
           "DASH_BACKEND": backend, "APP_ENV": "ci"}
    import os

    for name in ("HTTPS_PROXY", "HTTP_PROXY", "NO_PROXY", "SSL_CERT_FILE",
                 "REQUESTS_CA_BUNDLE", "TMPDIR"):
        if os.environ.get(name):
            env[name] = os.environ[name]
    env.update(extra_env or {})
    result = subprocess.run([sys.executable, "-c", PROBE % {"url": url}],
                            cwd=REPO_ROOT, env=env, capture_output=True,
                            text=True, timeout=300)
    for line in result.stdout.splitlines():
        if line.startswith("RESULT "):
            return json.loads(line[len("RESULT "):])
    raise AssertionError(f"probe produced no result:\n{result.stdout[-2000:]}\n"
                         f"{result.stderr[-2000:]}")


def test_the_apps_own_host_is_served_in_process():
    """127.0.0.1:8550 is this app, answered with no socket."""
    out = _run("http://127.0.0.1:8550/healthz")
    assert "error" not in out, out
    assert out["status"] == 200
    assert not out.get("truncated"), "the probe capped the body"
    body = json.loads(out["body"])
    assert body["ok"] is True
    assert body["backend"] == "flask"


def test_a_long_ledger_path_does_not_truncate_the_probe(tmp_path):
    """The control for the cap, and for a failure the seat hit on the
    template's own instrument (2026-09-11).

    `/healthz` embeds `ledger.path` as an ABSOLUTE path, so the body's
    length varies with where the repo is checked out. `scripts/ci_leg.sh`
    clones into a deeper work dir than a hand-made clone, so the SAME
    commit that passed everywhere failed there — and it failed as a
    JSONDecodeError, which reads like a broken app rather than a probe that
    stopped reading. CI's own checkout sits under the old 400-byte cap by
    accident of path length.

    A path long enough to have broken it is forced here, so the cap cannot
    quietly come back.
    """
    deep = tmp_path
    for part in ("ci_leg_work", "clone_of_the_repository_under_test",
                 "deeper", "and", "deeper", "still", "nested", "further"):
        deep = deep / part
    deep.mkdir(parents=True, exist_ok=True)
    ledger = deep / "visitor_analytics.json"

    out = _run("http://127.0.0.1:8550/healthz",
               extra_env={"TRAFFIC_ANALYTICS_FILE": str(ledger)})
    assert "error" not in out, out
    assert not out.get("truncated"), "the probe capped a healthz body"
    body = json.loads(out["body"])
    assert body["ok"] is True
    assert body.get("ledger", {}).get("path") == str(ledger), (
        "the long path did not reach the served document, so this control "
        "did not exercise the length that broke the probe"
    )
    assert len(out["body"]) > 400, (
        f"the body is {len(out['body'])} bytes — shorter than the cap that "
        "used to truncate it, so this control proves nothing; make the "
        "forced ledger path longer"
    )


def test_an_off_host_url_reaches_the_real_network():
    """The property the addendum asks for, with a positive control that can
    tell the two apart: production serves a `build` field naming a real
    commit, and the in-process app does not. If the shim answered this
    itself, the two would be indistinguishable — which is exactly how the
    false red happened."""
    out = _run("https://boilerplate.2plot.dev/healthz")
    if "error" in out:
        pytest.skip(f"the real network is unreachable from here ({out['error']}) "
                    "— the ROUTING is untested, not proven wrong")
    assert out["status"] == 200
    body = json.loads(out["body"])
    assert body.get("app") == "boilerplate"
    build = body.get("build") or ""
    assert len(build) == 40, (
        f"answered by something without a real build sha ({build!r}) — this "
        "looks like the in-process app, not production"
    )


def test_the_shim_names_the_split_in_its_output():
    """An off-host fetch prints that it went out, so a reader of a battery
    log can see which answers came from where."""
    source = SHIM.read_text()
    assert "off-host -> real network" in source
    assert "_real_urlopen" in source
    assert "BASE_NETLOC" in source
