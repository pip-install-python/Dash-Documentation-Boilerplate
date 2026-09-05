"""Run the network battery against the in-process app.

`scripts/network_smoke.py` only ever executes in two places a developer never
watches: against the container CI just booted, and against production after a
deploy. That is exactly the code that rots — a typo in a check turns it into a
silent pass and the battery keeps reporting green over a broken host.

So it runs here too, with its `fetch` pointed at the test client. Three
distinct things get proven, and it is worth being explicit about which:

1. the battery's own logic still works (the checks fire, and they can fail);
2. this app satisfies every check the network standard makes of a satellite;
3. the per-site block at the top of the script — the expected H1, the hidden
   paths — still matches the app it describes.

What it cannot prove is the deployed artifact, which is the whole reason the
container run and the post-deploy run exist as well.
"""

from __future__ import annotations

import importlib.util
import sys

import pytest

from conftest import REPO_ROOT
from lib.constants import BASE_URL, INTERNAL_UA_TOKEN, SITE_BRAND

BASE = BASE_URL


@pytest.fixture(scope="module")
def battery():
    spec = importlib.util.spec_from_file_location(
        "network_smoke", REPO_ROOT / "scripts" / "network_smoke.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["network_smoke"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def wired(battery, client, monkeypatch):
    """Point the battery's `fetch` at the test client.

    The signature is `fetch(url, ua=..., method=..., body=..., headers=...)`
    and it returns `(status, lowercased_headers, text)`. The battery is a
    GET battery with two deliberate exceptions, both of which ASK whether
    HEAD works rather than using it to read a document: `HEAD /healthz`
    (1.6.32) and item 5's parity sweep, which probes the five infrastructure
    paths in three lanes precisely because `/` alone can answer for reasons
    the router knows nothing about. Anything else non-GET is still a bug in
    the script rather than something to emulate, so the allowance names its
    paths instead of dropping the guard.

    Headers come back as the battery's own `_Headers`, not a plain dict: the
    repeated-`Link` accessor is part of the interface under test, and a stub
    that flattened it would make item 5's lane check unable to fail.
    """
    seen_agents = []
    HEAD_OK = {"/healthz", "/llms.txt", "/robots.txt", "/sitemap.xml", "/"}

    def fetch(url, ua=battery.UA, method="GET", body=None, headers=None,
              timeout=None, retries=1):
        path = url[len(BASE):] if url.startswith(BASE) else url
        assert method == "GET" or (method == "HEAD" and (path or "/") in HEAD_OK), (
            f"the satellite battery issued a {method} to {path}"
        )
        seen_agents.append(ua)
        accept = (headers or {}).get("Accept")
        response = client.open(path or "/", method, user_agent=ua, accept=accept)
        return (response.status, battery._Headers(response.headers.items()),
                response.text)

    monkeypatch.setattr(battery, "fetch", fetch)
    monkeypatch.setattr(battery, "_RESULTS", [])
    # No declaration in the in-process seat: here the "host" serves from the
    # suite's own interpreter, which on the matrix's window legs (3.13/3.12)
    # is deliberately not the fleet Python. The python_matches_declared
    # check still proves the field EXISTS; holding the artifact to the
    # Dockerfile's minor is the container and production seats' job.
    monkeypatch.setattr(battery, "declared_python_minor", lambda: None)
    battery.seen_agents = seen_agents
    return battery


def test_the_battery_passes_against_this_app(wired, capsys):
    wired.satellite_checks(BASE)
    output = capsys.readouterr().out

    failed = [(name, detail) for name, verdict, detail in wired._RESULTS
              if verdict == wired.FAIL]
    assert failed == [], f"battery failures against the in-process app:\n{output}"
    assert len(wired._RESULTS) >= 9, "checks silently stopped running"


def test_every_request_the_battery_makes_is_internal(wired):
    """A battery that pollutes the ledger it is auditing is worse than none."""
    wired.satellite_checks(BASE)
    untokened = [ua for ua in wired.seen_agents if INTERNAL_UA_TOKEN not in ua]
    assert untokened == [], f"battery sent untokened User-Agents: {untokened}"


def test_the_expected_h1_tracks_the_brand_constant(battery):
    """The per-site block is a copy of `SITE_BRAND`; copies drift."""
    assert battery.SITE_H1 == f"# {SITE_BRAND}"


def test_the_battery_reports_a_failure_rather_than_swallowing_it(wired):
    """The check that keeps every other assertion here honest.

    If `check()` ever caught too broadly, the battery would print `pass` for a
    host that is on fire. Break one expectation on purpose and require it to
    be reported.
    """
    wired.SITE_H1 = "# not this site"
    try:
        wired.satellite_checks(BASE)
    finally:
        wired.SITE_H1 = f"# {SITE_BRAND}"

    verdicts = {name: verdict for name, verdict, _ in wired._RESULTS}
    assert verdicts.get("llms_txt_identity") == wired.FAIL


def test_the_default_base_url_matches_the_container_port(battery):
    """CI boots the image and runs the battery with no --base-url."""
    dockerfile = (REPO_ROOT / "Dockerfile").read_text()
    port = battery.DEFAULT_BASE_URL.rsplit(":", 1)[1]
    assert f"EXPOSE {port}" in dockerfile, (
        f"the battery defaults to port {port}; the image exposes something else"
    )
    assert f"0.0.0.0:{port}" in dockerfile, "the CMD binds a different port"


def test_the_batterys_default_ua_is_browser_lane_and_still_internal():
    """1.6.40 (muischeduler's finding): at dimll >= 2.8 a UA without a
    browser engine token is crawler-lane, so a default-UA check reads the
    crawler document. The default names the browser lane FIRST and keeps
    the internal token (a substring match) so the tracker still drops it;
    CRAWLER_UA stays the other lane."""
    from dash_improve_my_llms import classify

    from lib.constants import INTERNAL_UA_TOKEN
    from scripts import network_smoke as ns

    assert classify(ns.UA)["lane"] == "browser"
    assert ns.UA.startswith("Mozilla/5.0") and "AppleWebKit" in ns.UA
    assert INTERNAL_UA_TOKEN in ns.UA and ns.UA.endswith("network-smoke")
    assert classify(ns.CRAWLER_UA)["lane"] == "crawler"
    assert INTERNAL_UA_TOKEN in ns.CRAWLER_UA


# ------------------------------------------- the four fleet invariants (5) --


def test_the_four_fleet_invariants_are_registered_by_name(battery):
    """Item 5's detect: the four checks exist, by the names the fleet uses.

    A fork renaming one of these has not kept the invariant — the fan-out and
    every report read these names, and CD's log is where they are read.
    """
    import inspect

    source = inspect.getsource(battery.satellite_checks)
    for name in ("head_get_parity_three_uas", "api_llms_rows_present",
                 "discovery_link_headers_per_lane",
                 "directory_counts_are_derived"):
        assert f'("{name}", {name})' in source, (
            f"{name} is not registered in the battery's check list"
        )
        assert f"def {name}()" in source, f"{name} has no definition"


def test_repeated_link_headers_survive_the_header_mapping(battery):
    """The trap this mapping exists for: a dict keeps only the LAST value.

    Both shapes are legal and both must read the same — several `Link`
    headers (HTTP/1.1, the CI container) and one folded comma-joined value
    (HTTP/2, the wire read of this host on 2026-09-04).
    """
    repeated = battery._Headers([
        ("Link", '</llms.txt>; rel="alternate"; type="text/markdown"'),
        ("link", '</llms.txt>; rel="describedby"'),
        ("Content-Type", "text/html"),
    ])
    assert len(repeated.get_all("link")) == 2
    assert repeated["content-type"] == "text/html"
    assert dict(repeated)["link"].endswith('rel="describedby"'), (
        "the dict view should still be last-wins — existing callers rely on it"
    )

    folded = battery._Headers([
        ("link", '</llms.txt>; rel="alternate"; type="text/markdown", '
                 '</llms.txt>; rel="describedby"'),
    ])
    import re
    for headers in (repeated, folded):
        rels = set(re.findall(r'rel="?([a-zA-Z-]+)"?',
                              ", ".join(headers.get_all("link"))))
        assert rels == {"alternate", "describedby"}, rels


def test_a_check_that_cannot_apply_skips_and_never_passes(battery, monkeypatch):
    """`skip` is a verdict of its own — a pass here would be note 88's defect."""
    monkeypatch.setattr(battery, "_RESULTS", [])

    def cannot_apply():
        battery.skip("nothing to sweep")

    battery.check("a_check_with_no_corpus", cannot_apply)
    (name, verdict, detail), = battery._RESULTS
    assert (verdict, detail) == (battery.SKIP, "nothing to sweep")
    assert verdict != battery.PASS


def test_the_api_index_check_skips_only_while_the_host_declares_nothing(
        wired, monkeypatch):
    """Both directions, so the skip cannot pass as a constant.

    Empty API_PACKAGES (the template's own state) → skip. Non-empty → the
    check RUNS and reaches the wire; here that means a verdict other than
    skip, which is the whole point of the mutation.
    """
    import lib.constants as constants

    monkeypatch.setattr(constants, "API_PACKAGES", [])
    monkeypatch.setattr(wired, "_RESULTS", [])
    wired.satellite_checks(BASE)
    verdicts = {n: v for n, v, _ in wired._RESULTS}
    assert verdicts["api_llms_rows_present"] == wired.SKIP

    monkeypatch.setattr(constants, "API_PACKAGES", ["dash_mantine_components"])
    monkeypatch.setattr(wired, "_RESULTS", [])
    wired.satellite_checks(BASE)
    verdicts = {n: v for n, v, _ in wired._RESULTS}
    assert verdicts["api_llms_rows_present"] != wired.SKIP, (
        "the check still skipped with packages declared — it is a constant, "
        "not a check"
    )


# ------------------------ a proxied robots.txt is not yours (item 19) --


def test_the_ai_bot_posture_row_is_registered(battery):
    import inspect

    source = inspect.getsource(battery.satellite_checks)
    assert '("ai_bot_posture", ai_bot_posture)' in source
    assert "def ai_bot_posture()" in source


def test_the_row_compares_the_two_documents_and_passes_when_they_agree(wired):
    """The app's generated robots.txt against the one the world is served."""
    wired.satellite_checks(BASE)
    verdicts = {name: verdict for name, verdict, _ in wired._RESULTS}
    assert verdicts["ai_bot_posture"] == wired.PASS, [
        r for r in wired._RESULTS if r[0] == "ai_bot_posture"
    ]


def test_an_injected_disallow_reads_red(battery, wired, monkeypatch):
    """Item 19's acceptance. An edge can rewrite the file in valid syntax:
    the injected stanza below would sail past any `User-agent:` grep, and it
    turns off the entire crawl this network exists to serve."""
    real_fetch = wired.fetch

    def injected(url, *args, **kwargs):
        status, headers, text = real_fetch(url, *args, **kwargs)
        if url.endswith("/robots.txt"):
            text = ("# BEGIN Cloudflare Managed content\n"
                    "User-agent: GPTBot\nDisallow: /\n"
                    "# END Cloudflare Managed content\n") + text
        return status, headers, text

    monkeypatch.setattr(wired, "fetch", injected)
    monkeypatch.setattr(wired, "_RESULTS", [])
    wired.satellite_checks(BASE)

    row = [r for r in wired._RESULTS if r[0] == "ai_bot_posture"]
    assert row and row[0][1] == battery.FAIL, row
    detail = row[0][2]
    assert "not the one this app wrote" in detail
    assert "Cloudflare Managed" in detail or "disallow" in detail.lower()


def test_a_comment_only_edge_marker_still_reads_red(battery, wired, monkeypatch):
    """The marker IS the tell, and a marker with no directives under it is
    the shape a grep is least likely to notice."""
    real_fetch = wired.fetch

    def marked(url, *args, **kwargs):
        status, headers, text = real_fetch(url, *args, **kwargs)
        if url.endswith("/robots.txt"):
            text = "# BEGIN Cloudflare Managed content\n" + text
        return status, headers, text

    monkeypatch.setattr(wired, "fetch", marked)
    monkeypatch.setattr(wired, "_RESULTS", [])
    wired.satellite_checks(BASE)
    row = [r for r in wired._RESULTS if r[0] == "ai_bot_posture"]
    assert row and row[0][1] == battery.FAIL
    assert "edge marker" in row[0][2]


def test_the_row_skips_rather_than_inventing_one_side(battery, wired, monkeypatch):
    """A comparison with only one side is not a comparison. The battery runs
    against hosts whose checkout it does not have."""
    import lib.robots_expected as expected

    def unavailable():
        raise RuntimeError("no checkout here")

    monkeypatch.setattr(expected, "expected_directives", unavailable)
    monkeypatch.setattr(wired, "_RESULTS", [])
    wired.satellite_checks(BASE)
    row = [r for r in wired._RESULTS if r[0] == "ai_bot_posture"]
    assert row and row[0][1] == battery.SKIP, row
    assert row[0][1] != battery.PASS


def test_a_removed_directive_reads_red_too(battery, wired, monkeypatch):
    """The direction the first version was blind to (Fable audit, 1.6.44).

    An edge that REMOVES a directive is as much a rewrite as one that adds a
    stanza — and dropping this host's `Allow:` rules for the AI search agents
    is the change most likely to be made on your behalf by a "security"
    default. An added-only comparison calls that green.
    """
    real_fetch = wired.fetch

    def stripped(url, *args, **kwargs):
        status, headers, text = real_fetch(url, *args, **kwargs)
        if url.endswith("/robots.txt"):
            text = "\n".join(ln for ln in text.splitlines()
                             if not ln.strip().lower().startswith("allow:"))
        return status, headers, text

    monkeypatch.setattr(wired, "fetch", stripped)
    monkeypatch.setattr(wired, "_RESULTS", [])
    wired.satellite_checks(BASE)

    row = [r for r in wired._RESULTS if r[0] == "ai_bot_posture"]
    assert row and row[0][1] == battery.FAIL, row
    assert "NOT served" in row[0][2], row[0][2]


def test_the_cd_verify_job_can_generate_the_apps_side(battery):
    """Item 19's row is only meaningful where a real edge is in the path —
    the CD verify job — and generating the app's side needs the app.

    Without the install step the row takes its `skip` path and the battery
    is green having never made the comparison. That is what it did on every
    CD run between 1.6.44 landing and this fix, and a skip is not a failure,
    so nothing said so.
    """
    cd = (REPO_ROOT / ".github" / "workflows" / "cd.yml").read_text()
    verify = cd.split("Network smoke battery", 1)[0]
    assert "pip install -r requirements.txt" in verify, (
        "the verify job does not install the app — ai_bot_posture will skip "
        "and the battery will be green without comparing anything"
    )
