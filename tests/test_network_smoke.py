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


# ------------------- the well-known battery rows (1.6.45 item 3) --


def _row(results, name):
    rows = [r for r in results if r[0] == name]
    assert rows, f"{name} did not run at all"
    return rows[0]


def _rewrite(wired, monkeypatch, path_suffix, transform):
    """Run the battery with one path's body or status rewritten."""
    real = wired.fetch

    def fetch(url, *args, **kwargs):
        status, headers, text = real(url, *args, **kwargs)
        if url.endswith(path_suffix):
            status, text = transform(status, text)
        return status, headers, text

    monkeypatch.setattr(wired, "fetch", fetch)
    monkeypatch.setattr(wired, "_RESULTS", [])
    wired.satellite_checks(BASE)
    return wired._RESULTS


def test_all_eight_well_known_rows_are_registered(battery):
    """Item 3's detect: the rows exist by name."""
    import inspect

    source = inspect.getsource(battery.satellite_checks)
    for name in ("wellknown_unknown_404", "api_catalog_links_resolve",
                 "mcp_card_matches_host", "skills_index_and_digest",
                 "page_markdown_negotiation", "edge_honours_vary",
                 "content_signal_matches_config"):
        assert f'("{name}", {name})' in source, f"{name} is not registered"
        assert f"def {name}()" in source


def test_the_rows_pass_against_this_app(wired):
    wired.satellite_checks(BASE)
    failed = [(n, d) for n, v, d in wired._RESULTS if v == wired.FAIL]
    assert failed == [], failed


def test_every_skip_names_what_it_did_not_cover(wired):
    """A skip that says nothing is indistinguishable from a pass that means
    nothing — item 3 requires each line to name its gap."""
    wired.satellite_checks(BASE)
    for name, verdict, detail in wired._RESULTS:
        if verdict == wired.SKIP:
            assert detail.strip(), f"{name} skipped with no reason"
            assert len(detail) > 30, (
                f"{name} skipped with {detail!r} — too terse to say what is "
                "uncovered"
            )


def test_an_html_404_body_is_caught(battery, wired, monkeypatch):
    """The failure is not a missing route — it is a catch-all answering 200
    (or 404) with the app shell."""
    results = _rewrite(wired, monkeypatch, "/.well-known/nope",
                       lambda s, t: (s, "<!doctype html><html>shell</html>"))
    name, verdict, detail = _row(results, "wellknown_unknown_404")
    assert verdict == battery.FAIL and "HTML" in detail


def test_a_200_on_an_unknown_well_known_path_is_caught(battery, wired, monkeypatch):
    results = _rewrite(wired, monkeypatch, "/.well-known/nope",
                       lambda s, t: (200, t))
    _n, verdict, detail = _row(results, "wellknown_unknown_404")
    assert verdict == battery.FAIL and "not 404" in detail


def test_a_404_body_that_does_not_name_llms_txt_is_caught(battery, wired,
                                                          monkeypatch):
    """piratesbargain.com serves its catch-all HTML at /llms.txt; a 404 body
    that does not point there is somebody else's error document."""
    results = _rewrite(wired, monkeypatch, "/.well-known/nope",
                       lambda s, t: (s, '{"error":"not found"}'))
    _n, verdict, detail = _row(results, "wellknown_unknown_404")
    assert verdict == battery.FAIL and "/llms.txt" in detail


def test_a_broken_catalog_link_is_caught(battery, wired, monkeypatch):
    """A catalog entry that 404s is the lie the guard removes."""
    import json as _json

    real = wired.fetch

    def fetch(url, *args, **kwargs):
        status, headers, text = real(url, *args, **kwargs)
        if url.endswith("/.well-known/api-catalog"):
            body = _json.loads(text)
            body["linkset"] = [{"anchor": BASE,
                                "service-desc": [{"href": "/nowhere-at-all"}]}]
            text = _json.dumps(body)
        return status, headers, text

    monkeypatch.setattr(wired, "fetch", fetch)
    monkeypatch.setattr(wired, "_RESULTS", [])
    wired.satellite_checks(BASE)
    _n, verdict, detail = _row(wired._RESULTS, "api_catalog_links_resolve")
    assert verdict == battery.FAIL and "do not resolve" in detail


def test_a_digest_that_does_not_match_the_bytes_is_caught(battery, wired,
                                                          monkeypatch):
    """The digest is the point of the spec: it must describe the bytes the
    host SERVES, not the ones it meant to."""
    real = wired.fetch

    def fetch(url, *args, **kwargs):
        status, headers, text = real(url, *args, **kwargs)
        if url.endswith("/assets/SKILL.md"):
            text = text + "\nedited after the index was built\n"
        return status, headers, text

    monkeypatch.setattr(wired, "fetch", fetch)
    monkeypatch.setattr(wired, "_RESULTS", [])
    wired.satellite_checks(BASE)
    _n, verdict, detail = _row(wired._RESULTS, "skills_index_and_digest")
    assert verdict == battery.FAIL and "hash to" in detail


def test_an_absent_skills_list_is_caught(battery, wired, monkeypatch):
    """Empty is an answer; absent is a mystery."""
    results = _rewrite(wired, monkeypatch, "/.well-known/agent-skills/index.json",
                       lambda s, t: (s, '{"$schema": "x"}'))
    _n, verdict, detail = _row(results, "skills_index_and_digest")
    assert verdict == battery.FAIL and "not a list" in detail


def _derived_page(wired) -> str:
    """The page the rows will probe, derived the way they derive it.

    These mutation tests used to key on the literal `/backends`. Once the
    rows stopped hardcoding it (pannellum's rider) the transforms stopped
    intercepting anything and the tests passed a mutation that never
    happened — a literal in a test guarding against literals.
    """
    import re
    import urllib.parse

    status, _, xml = wired.fetch(BASE + "/sitemap.xml", ua=wired.UA)
    assert status == 200, f"/sitemap.xml {status} — cannot derive a page"
    for loc in re.findall(r"<loc>\s*([^<]+?)\s*</loc>", xml):
        path = urllib.parse.urlsplit(loc).path.rstrip("/")
        if path and not path.startswith("/admin") and path != "/404":
            return path
    raise AssertionError("no public page in the sitemap")


def test_a_negotiated_page_that_is_a_different_page_is_caught(battery, wired,
                                                              monkeypatch):
    """The invariant is identity of the PAGE — the drop's byte-equality does
    not hold on dimll 2.10.0 (measured: a 7,481-char common suffix and a
    differing navigation line)."""
    page = _derived_page(wired)
    results = _rewrite(wired, monkeypatch, f"{page}/llms.txt",
                       lambda s, t: (s, "# Some Other Page\n\nbody\n"))
    _n, verdict, detail = _row(results, "page_markdown_negotiation")
    assert verdict == battery.FAIL and "different page" in detail


def test_a_content_signal_that_disagrees_with_the_config_is_caught(
        battery, wired, monkeypatch):
    results = _rewrite(
        wired, monkeypatch, "/robots.txt",
        lambda s, t: (s, t.replace("ai-train=yes", "ai-train=no")),
    )
    _n, verdict, detail = _row(results, "content_signal_matches_config")
    assert verdict == battery.FAIL and "RobotsConfig" in detail


def test_two_content_signal_lines_are_caught(battery, wired, monkeypatch):
    results = _rewrite(
        wired, monkeypatch, "/robots.txt",
        lambda s, t: (s, t + "\nContent-Signal: search=no\n"),
    )
    _n, verdict, detail = _row(results, "content_signal_matches_config")
    assert verdict == battery.FAIL and "allows one" in detail


# ------------- assets_cached / healthz_keys_vs_template (1.6.45 item 9) --
#           ------------- and crawler_404 (1.6.45 item 8) --


def _rewrite_full(wired, monkeypatch, transform):
    """Run the battery with (url, ua, status, headers, text) rewritable.

    `_rewrite` above reaches only the status and the body, keyed on the path.
    These three rows turn on the HEADERS (`cache-control`) and on the UA (the
    crawler lane and the browser lane must answer DIFFERENTLY for the same
    URL), so neither is reachable through it.
    """
    real = wired.fetch

    def fetch(url, *args, **kwargs):
        status, headers, text = real(url, *args, **kwargs)
        ua = kwargs.get("ua") or (args[0] if args else wired.UA)
        return transform(url, ua, status, headers, text)

    monkeypatch.setattr(wired, "fetch", fetch)
    monkeypatch.setattr(wired, "_RESULTS", [])
    wired.satellite_checks(BASE)
    return wired._RESULTS


class _FakeHeaders:
    """Enough of the battery's header mapping to rewrite one name."""

    def __init__(self, real, overrides):
        self._real = real
        self._over = {k.lower(): v for k, v in overrides.items()}

    def get(self, name, default=None):
        key = name.lower()
        if key in self._over:
            return self._over[key]
        return self._real.get(name, default)

    def get_all(self, name):
        key = name.lower()
        if key in self._over:
            return [self._over[key]]
        return self._real.get_all(name)


def test_the_item_9_and_item_8_rows_are_registered(battery):
    """Detect for both items: the rows exist by name and are in the list."""
    import inspect

    source = inspect.getsource(battery.satellite_checks)
    for name in ("assets_cached", "healthz_keys_vs_template", "crawler_404"):
        assert f'("{name}", {name})' in source, f"{name} is not registered"
        assert f"def {name}()" in source


def test_a_no_cache_asset_is_caught(battery, wired, monkeypatch):
    """The pre-1.6.44 answer: every fork sent this, and the edge stored
    nothing. If this row cannot see it, the row is decoration."""
    def transform(url, ua, status, headers, text):
        if url.endswith("/assets/main.css"):
            headers = _FakeHeaders(headers, {"cache-control": "no-cache"})
        return status, headers, text

    results = _rewrite_full(wired, monkeypatch, transform)
    _n, verdict, detail = _row(results, "assets_cached")
    assert verdict == battery.FAIL and "max-age" in detail, detail


def test_a_zero_max_age_is_caught(battery, wired, monkeypatch):
    """`max-age=0` is stored and never used — a header that looks right."""
    def transform(url, ua, status, headers, text):
        if url.endswith("/assets/main.css"):
            headers = _FakeHeaders(headers, {"cache-control":
                                             "public, max-age=0"})
        return status, headers, text

    results = _rewrite_full(wired, monkeypatch, transform)
    _n, verdict, detail = _row(results, "assets_cached")
    assert verdict == battery.FAIL and "zero" in detail, detail


def test_a_healthz_key_dropped_between_code_and_wire_is_caught(
        battery, wired, monkeypatch):
    """The 1.6.44 defect itself: `llms_version` produced by health_payload()
    and absent from the response because a model did not declare it."""
    import json as _json

    def transform(url, ua, status, headers, text):
        if url.endswith("/healthz") and status == 200:
            body = _json.loads(text)
            body.pop("llms_version", None)
            text = _json.dumps(body)
        return status, headers, text

    results = _rewrite_full(wired, monkeypatch, transform)
    _n, verdict, detail = _row(results, "healthz_keys_vs_template")
    assert verdict == battery.FAIL and "llms_version" in detail, detail


def test_a_soft_404_is_caught(battery, wired, monkeypatch):
    """Item 8's row: the crawler gets 200 + the shell, which is what every
    host did before the fix."""
    def transform(url, ua, status, headers, text):
        if "definitely-not-a-page" in url and wired.CRAWLER_UA == ua:
            return 200, headers, "<!doctype html><html>shell</html>"
        return status, headers, text

    results = _rewrite_full(wired, monkeypatch, transform)
    _n, verdict, detail = _row(results, "crawler_404")
    assert verdict == battery.FAIL and "soft" in detail.lower(), detail


def test_a_404_to_the_BROWSER_is_caught_too(battery, wired, monkeypatch):
    """The over-correction. 404ing BOTH lanes would satisfy a row that only
    checked the crawler, and it would break the site for people."""
    def transform(url, ua, status, headers, text):
        if "definitely-not-a-page" in url and wired.BROWSER_UA == ua:
            return 404, headers, "not found"
        return status, headers, text

    results = _rewrite_full(wired, monkeypatch, transform)
    _n, verdict, detail = _row(results, "crawler_404")
    assert verdict == battery.FAIL and "BROWSER" in detail, detail


def test_a_guard_that_eats_registered_pages_is_caught(battery, wired,
                                                      monkeypatch):
    """A 404-everything guard passes any row that only checks the 404."""
    page = _derived_page(wired)

    def transform(url, ua, status, headers, text):
        if url.endswith(page):
            return 404, headers, "not found"
        return status, headers, text

    results = _rewrite_full(wired, monkeypatch, transform)
    _n, verdict, detail = _row(results, "crawler_404")
    assert verdict == battery.FAIL and "eating registered pages" in detail


# ------------------------- --require: a skip is a verdict (1.6.45 item 11) --


def _main_with(battery, monkeypatch, results, require):
    """Run main() over a fabricated result set and return its exit code."""
    monkeypatch.setattr(battery, "_RESULTS", list(results))
    monkeypatch.setattr(battery, "satellite_checks", lambda base: None)
    monkeypatch.setattr(
        battery.sys, "argv",
        ["network_smoke.py", "--base-url", BASE, "--require", require])
    return battery.main()


def test_the_require_flag_exists(battery):
    """Item 11's detect: the summary line counted skips already, but nothing
    could make one fail."""
    import inspect

    source = inspect.getsource(battery.main)
    assert '"--require"' in source


def test_a_required_row_that_skipped_exits_non_zero(battery, monkeypatch):
    results = [("ai_bot_posture", battery.SKIP, "the app was not importable"),
               ("healthz_ok", battery.PASS, "")]
    assert _main_with(battery, monkeypatch, results, "ai_bot_posture") == 1


def test_a_required_row_that_passed_exits_zero(battery, monkeypatch):
    """Negative control: --require must not fail a run on its own."""
    results = [("ai_bot_posture", battery.PASS, ""),
               ("healthz_ok", battery.PASS, "")]
    assert _main_with(battery, monkeypatch, results, "ai_bot_posture") == 0


def test_a_required_row_that_does_not_exist_exits_non_zero(battery, monkeypatch):
    """A typo in the flag requires NOTHING, and the run would go green having
    proved nothing — the same failure the flag exists to remove."""
    results = [("ai_bot_posture", battery.PASS, "")]
    assert _main_with(battery, monkeypatch, results, "ai_bot_postrue") == 1


def test_an_unrequired_skip_still_does_not_fail_the_run(battery, monkeypatch):
    """Rows that legitimately do not apply to a host must keep skipping."""
    results = [("mcp_card_matches_host", battery.SKIP, "no MCP bridge here"),
               ("healthz_ok", battery.PASS, "")]
    assert _main_with(battery, monkeypatch, results, "healthz_ok") == 0


def test_the_cd_verify_job_requires_the_rows_that_only_mean_something_there(
        battery):
    """The flag is useless unless the verify job passes it, and every name it
    passes must be a REAL row — a typo would be silently decorative, which is
    exactly what `ai_bot_posture` skipping for a release already looked like.
    """
    import inspect

    cd = (REPO_ROOT / ".github" / "workflows" / "cd.yml").read_text()
    verify = cd.split("Network smoke battery", 1)[1]
    assert "--require" in verify, (
        "the verify job does not pass --require, so a row that skips there "
        "is still a pass and the item bought nothing"
    )
    required = verify.split("--require", 1)[1].split()[0]
    names = [n for n in required.split(",") if n]
    assert len(names) >= 3, names
    source = inspect.getsource(battery.satellite_checks)
    for name in names:
        assert f'("{name}", {name})' in source, (
            f"cd.yml requires {name!r}, which is not a row in the battery"
        )


# ------------------ openapi_document_renders (note 143, 1.6.45 rider) --


def test_the_openapi_row_is_registered(battery):
    import inspect

    source = inspect.getsource(battery.satellite_checks)
    assert '("openapi_document_renders", openapi_document_renders)' in source
    assert "def openapi_document_renders()" in source


def test_a_500_on_the_document_is_caught(battery, wired, monkeypatch):
    """muischeduler's actual failure: the document 500s while /docs stays
    200, because /docs is a shell that fetches this in the browser."""
    def transform(url, ua, status, headers, text):
        if url.endswith("/healthz"):
            import json as _json
            body = _json.loads(text)
            body["backend"] = "fastapi"          # force the lane on
            return status, headers, _json.dumps(body)
        if url.endswith("/openapi.json"):
            return 500, headers, "Internal Server Error"
        return status, headers, text

    results = _rewrite_full(wired, monkeypatch, transform)
    _n, verdict, detail = _row(results, "openapi_document_renders")
    assert verdict == battery.FAIL and "500" in detail, detail


def test_a_document_that_describes_nothing_is_caught(battery, wired,
                                                     monkeypatch):
    """A 200 that renders an empty document is the same silence."""
    def transform(url, ua, status, headers, text):
        if url.endswith("/healthz"):
            import json as _json
            body = _json.loads(text)
            body["backend"] = "fastapi"
            return status, headers, _json.dumps(body)
        if url.endswith("/openapi.json"):
            return 200, headers, '{"openapi": "3.1.0", "paths": {}}'
        return status, headers, text

    results = _rewrite_full(wired, monkeypatch, transform)
    _n, verdict, detail = _row(results, "openapi_document_renders")
    assert verdict == battery.FAIL and "describes 0 path" in detail, detail


def test_a_non_fastapi_host_skips_and_names_what_is_uncovered(battery, wired,
                                                              monkeypatch):
    """A copy of this battery aimed at a Flask peer must SKIP, and the skip
    must say what it did not cover — never a quiet pass."""
    def transform(url, ua, status, headers, text):
        if url.endswith("/healthz"):
            import json as _json
            body = _json.loads(text)
            body["backend"] = "flask"
            return status, headers, _json.dumps(body)
        return status, headers, text

    results = _rewrite_full(wired, monkeypatch, transform)
    _n, verdict, detail = _row(results, "openapi_document_renders")
    assert verdict == battery.SKIP, (verdict, detail)
    assert "NOT covered" in detail, detail


# ---- "cannot run here" must RAISE, never return (muicharts, 2026-09-12) --


def test_no_row_expresses_cannot_run_here_as_a_bare_return(battery):
    """The generalised form of the `python_matches_declared` false pass.

    The bug was not the env knob. It was that "this row cannot run here" was
    expressed as a RETURN, and a bare return is indistinguishable from a
    pass at EVERY layer above it — the counts, the summary line, the exit
    code, the annotation. A row whose precondition is absent must RAISE the
    skip.

    So this sweeps every row, not just the one that was found. The predicate
    is not a name whitelist: a bare return is allowed only where the same
    block has already called `expect`, i.e. the row reached a verdict and is
    returning early rather than bailing out silently.
    """
    import ast
    import inspect
    import textwrap

    source = textwrap.dedent(inspect.getsource(battery.satellite_checks))
    outer = next(n for n in ast.walk(ast.parse(source))
                 if isinstance(n, ast.FunctionDef)
                 and n.name == "satellite_checks")
    rows = [n for n in outer.body if isinstance(n, ast.FunctionDef)]
    assert len(rows) >= 20, (
        f"only {len(rows)} rows found — the walk is not reaching them and a "
        "clean sweep of almost nothing is not a result"
    )

    def blocks(node):
        for field in ("body", "orelse", "finalbody"):
            value = getattr(node, field, None)
            if isinstance(value, list):
                yield value
            if isinstance(value, list):
                for child in value:
                    yield from blocks(child)

    offenders = []
    for row in rows:
        for block in blocks(row):
            for index, statement in enumerate(block):
                if not (isinstance(statement, ast.Return)
                        and statement.value is None):
                    continue
                before = block[:index]
                reached_a_verdict = any(
                    isinstance(call.func, ast.Name)
                    and call.func.id in ("expect", "skip")
                    for earlier in before
                    for call in ast.walk(earlier)
                    if isinstance(call, ast.Call)
                )
                if not reached_a_verdict:
                    offenders.append(f"{row.name}:{statement.lineno}")

    assert offenders == [], (
        f"{offenders} bail out with a bare return before reaching any "
        "verdict — that is counted as a PASS. Raise the skip instead: "
        "`skip(...)` names what was not covered, a return names nothing."
    )
