"""Exercise scripts/smoke_live.py against the app itself.

The script only ever runs in CD, against a host that already exists, which is
exactly the kind of code that rots unnoticed — a typo in a regex turns every
check into a silent pass and CD keeps reporting green over a broken deploy.
So it gets run here too, with its `fetch` pointed at the in-process app
instead of the network.
"""

from __future__ import annotations

import importlib.util
import sys

import pytest

from conftest import REPO_ROOT, backend
from lib.constants import BASE_URL

# The app's real origin, because the script checks that canonical tags and
# sitemap URLs match the host being requested. Pointing it at a made-up
# hostname would fail those checks for the wrong reason.
BASE = BASE_URL


@pytest.fixture(scope="module")
def smoke():
    spec = importlib.util.spec_from_file_location(
        "smoke_live", REPO_ROOT / "scripts" / "smoke_live.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["smoke_live"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def wired(smoke, client, monkeypatch):
    """Point the script's fetch at the test client.

    Off-host URLs (the peers' llms.txt) resolve to a stub 200 — reaching over
    the network from a unit test would make the suite depend on eleven other
    deployments being up.
    """
    def fetch(url, user_agent=smoke.BROWSER_UA, accept=None):
        if url.startswith(BASE):
            path = url[len(BASE):] or "/"
            response = client.get(path, user_agent=user_agent, accept=accept)
            return response.status, response.text, response.headers
        return 200, "# peer\n", {"Content-Type": "text/markdown"}

    monkeypatch.setattr(smoke, "fetch", fetch)
    monkeypatch.setattr(smoke, "failures", [])
    monkeypatch.setattr(smoke, "checks_run", 0)
    return smoke


def test_smoke_script_passes_against_this_app(wired, capsys):
    exit_code = wired.main(BASE)
    output = capsys.readouterr().out
    assert exit_code == 0, f"smoke_live reported failures:\n{output}"
    assert "checks passed" in output


def test_smoke_script_detects_a_stub_body(wired, smoke, monkeypatch, capsys):
    """The check that matters most must actually fire when it should."""
    original = smoke.fetch

    def stubbed(url, user_agent=smoke.BROWSER_UA, accept=None):
        status, body, headers = original(url, user_agent, accept)
        if user_agent == smoke.CRAWLER_UA:
            body = f"<main><p>{smoke.STUB_MARKER}</p></main>"
        return status, body, headers

    monkeypatch.setattr(smoke, "fetch", stubbed)
    assert wired.main(BASE) > 0
    assert "served the JavaScript stub" in capsys.readouterr().out


def test_smoke_script_detects_a_foreign_canonical(wired, smoke, monkeypatch, capsys):
    original = smoke.fetch

    def rehosted(url, user_agent=smoke.BROWSER_UA, accept=None):
        status, body, headers = original(url, user_agent, accept)
        return status, body.replace(
            'rel="canonical" href="https://boilerplate.2plot.dev',
            'rel="canonical" href="https://someone-elses-host.example.com',
        ), headers

    monkeypatch.setattr(smoke, "fetch", rehosted)
    assert wired.main(BASE) > 0
    assert "canonical on" in capsys.readouterr().out


def test_smoke_script_detects_viewer_chrome_leaking_to_agents(
    wired, smoke, monkeypatch, capsys
):
    """The other check ROLLOUT.md calls out as silent and expensive.

    If the viewer's HTML ever reaches a plain fetch, every agent in the
    network pays tokens for decoration and nothing anywhere reports it.
    """
    original = smoke.fetch

    def leaky(url, user_agent=smoke.BROWSER_UA, accept=None):
        status, body, headers = original(url, user_agent, accept)
        if url.endswith("/llms.txt") and accept is None:
            body = '<!DOCTYPE html><div class="dv-banner">chrome</div>' + body
        return status, body, headers

    monkeypatch.setattr(smoke, "fetch", leaky)
    assert wired.main(BASE) > 0
    assert "viewer chrome" in capsys.readouterr().out


def test_peer_urls_survive_markdown_link_syntax(wired, smoke, capsys):
    """The 2.2.0 nav block writes `[https://host/llms.txt](https://host/llms.txt)`.

    A URL pattern that stops only at whitespace and `)` swallows the label and
    the opening paren into one malformed URL, which then 404s and fails a
    perfectly good deploy. Every extracted URL must be fetchable as-is.
    """
    assert wired.main(BASE) == 0
    # Either label: a peer that answers is reported as "serves a document",
    # one that doesn't as "reachable".
    reported = [
        line.split(": ", 1)[1].strip()
        for line in capsys.readouterr().out.splitlines()
        if "peer reachable: " in line or "peer serves a document: " in line
    ]
    assert reported, "no peer URLs were extracted at all"
    malformed = [u for u in reported if any(ch in u for ch in "()[]")]
    assert malformed == [], f"markdown syntax leaked into peer URLs: {malformed}"


def test_smoke_script_detects_a_missing_vary_header(wired, smoke, monkeypatch, capsys):
    """A CDN that never sees `Vary: Accept` will serve one cached variant to
    everyone — the one failure that only appears in front of a real cache."""
    original = smoke.fetch

    def unvaried(url, user_agent=smoke.BROWSER_UA, accept=None):
        status, body, headers = original(url, user_agent, accept)
        return status, body, {k: v for k, v in headers.items() if k.lower() != "vary"}

    monkeypatch.setattr(smoke, "fetch", unvaried)
    assert wired.main(BASE) > 0
    assert "Vary: Accept" in capsys.readouterr().out


def test_smoke_script_rejects_a_peer_serving_its_spa_shell(
    wired, smoke, monkeypatch, capsys
):
    """A 200 alone does not mean a host serves the document.

    A Dash app answers its catch-all with the SPA shell for any unmatched
    path, so a peer that publishes no llms.txt still returns 200 text/html.
    Verified against 2plot.dev, where `/api/this-endpoint-cannot-exist` also
    returns 200 text/html — a status-only check passes on every such host and
    the directory looks healthy while pointing at nothing.
    """
    original = smoke.fetch

    def spa_shell(url, user_agent=smoke.BROWSER_UA, accept=None):
        if not url.startswith(BASE):
            return 200, "<!DOCTYPE html><html><body>app</body></html>", {
                "Content-Type": "text/html; charset=utf-8"
            }
        return original(url, user_agent, accept)

    monkeypatch.setattr(smoke, "fetch", spa_shell)
    assert wired.main(BASE) > 0
    assert "that host's catch-all" in capsys.readouterr().out


@pytest.mark.skipif(backend() != "flask", reason="one backend is enough for this")
def test_smoke_script_reports_a_dead_peer(wired, smoke, monkeypatch, capsys):
    original = smoke.fetch

    def dead_peers(url, user_agent=smoke.BROWSER_UA, accept=None):
        if not url.startswith(BASE):
            return 404, "", {}
        return original(url, user_agent, accept)

    monkeypatch.setattr(smoke, "fetch", dead_peers)
    assert wired.main(BASE) > 0
    assert "peer reachable" in capsys.readouterr().out
