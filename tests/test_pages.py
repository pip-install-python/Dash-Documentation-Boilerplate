"""Every page loads, and every page serves real content to a crawler."""

from __future__ import annotations

import re

import pytest

from conftest import CRAWLER_UA, STUB_MARKER, main_body

# Pages that must exist. A markdown file silently failing to register is
# invisible in a smoke test that only iterates whatever did register — the
# suite would pass with half the site missing.
REQUIRED_PATHS = {
    "/",
    "/getting-started",
    "/backends",
    "/backend-comparison",
    "/fastapi-showcase",
    "/networks",
    "/examples/ai-integration",
    "/examples/directives",
    "/examples/interactive",
    "/examples/visualization",
}


def test_every_required_page_registered(page_paths):
    missing = REQUIRED_PATHS - set(page_paths)
    assert not missing, f"pages missing from dash.page_registry: {sorted(missing)}"


def test_no_duplicate_page_paths(page_paths):
    duplicates = {p for p in page_paths if page_paths.count(p) > 1}
    assert not duplicates, f"two pages registered on the same path: {sorted(duplicates)}"


def test_pages_are_reachable(client, page_paths):
    failures = [(p, client.get(p).status) for p in page_paths]
    assert [f for f in failures if f[1] != 200] == []


def test_no_page_serves_the_javascript_stub(client, page_paths):
    """The regression that cost this network twelve of fourteen crawlable URLs.

    A stub here means the page has no prose registered, or something erased
    it after registration. Either way crawlers and agents see nothing.
    """
    stubbed = [p for p in page_paths if STUB_MARKER in client.get(p, user_agent=CRAWLER_UA).text]
    assert stubbed == [], f"pages serving the stub body to crawlers: {stubbed}"


def test_crawler_bodies_are_substantial(client, page_paths):
    """A page can avoid the stub and still serve almost nothing."""
    thin = []
    for path in page_paths:
        body = main_body(client.get(path, user_agent=CRAWLER_UA).text)
        if len(body) < 2000:
            thin.append((path, len(body)))
    assert thin == [], f"suspiciously small crawler bodies: {thin}"


def test_prose_renders_as_html_not_literal_markdown(client):
    """2.1's renderer: links, code fences, rules and tables, not raw text.

    Before 2.1 these came through as `<p>---</p>`, literal `[text](url)` and
    pipe characters. Checked on the directives page because it is the most
    heavily formatted one in the repo.
    """
    body = main_body(client.get("/examples/directives", user_agent=CRAWLER_UA).text)

    assert body.count("<pre") >= 10, "expected code fences to render as <pre> blocks"
    assert "<hr" in body, "expected horizontal rules to render as <hr>"
    assert not re.search(r"<p>\s*-{3,}\s*</p>", body), "horizontal rule leaked as literal text"
    assert not re.search(r"\[[^\]]+\]\(https?://", body), "markdown link leaked as literal text"


def test_pages_have_distinct_titles(client, page_paths):
    """Dash serves one static index template for every route, so without a
    per-page title every URL ships identical head metadata — which is most of
    what makes a site look like a set of near-duplicates."""
    titles = {}
    for path in page_paths:
        html = client.get(path).text
        match = re.search(r"<title>(.*?)</title>", html, re.S)
        assert match, f"{path} served no title element"
        titles[path] = match.group(1).strip()

    duplicates = {t for t in titles.values() if list(titles.values()).count(t) > 1}
    assert not duplicates, f"pages sharing a title: {duplicates}"


def test_home_page_links_out_to_other_pages(client):
    body = main_body(client.get("/", user_agent=CRAWLER_UA).text)
    assert body.count("<a href=") >= 5, "home page prose has almost no outbound links"


@pytest.mark.parametrize("path", ["/nope", "/examples/does-not-exist"])
def test_unknown_paths_do_not_500(client, path):
    assert client.get(path).status in (200, 404), "unknown path should 404 or render the app's 404"


def test_prerender_rides_the_generic_lane_not_a_ua_gate(client):
    """The universal prerender must be in the initial HTML for a PLAIN
    client — no crawler user-agent. An outside SEO audit (2026-08-22) read
    five hosts as serving "Loading... and nothing else" to browsers; the
    prose was there all along, but every test in this file fetched with
    CRAWLER_UA (which exercises the separate bot-document path), so a
    regression that UA-gated the universal lane would have been invisible
    to the suite. This test is the generic-lane pin.

    KNOWN LIMITATION, deliberately not asserted yet: dimll <= 2.6.0 ships
    the injected div with the `hidden` attribute, so visibility-respecting
    text extractors (and arguably crawler content weighting) still see
    nothing — the visibility fix is package-side (the prerender div must
    be visible by default and hidden by a synchronous inline script that
    only JS browsers execute; React's mount already wipes the div, so
    `hidden` only ever covered the pre-mount flash). When the floor moves
    past the fixing release, extend this test to assert the div is NOT
    `hidden`.
    """
    for path in ("/", "/getting-started"):
        html = client.get(path).text  # default UA — the point of the test
        assert 'id="dimll-prerender"' in html, (
            f"{path}: no prerender block for a generic client — the "
            "universal lane is gated or off"
        )
        assert "<main>" in html, f"{path}: prerender block carries no <main> prose"
