"""Unregistered paths answer 404 on the crawler lane — 1.6.45 item 8, note 104.

Dash answers 200 for ANY path: the server returns the app shell and the
client-side router decides. For a browser that is right — the router shows a
404 page. For a crawler it is a SOFT 404, and every mistyped link, stale URL
and probe gets indexed as a real page.

Measured on this tree BEFORE the fix: `GET /definitely-not-a-page` with a
Googlebot UA returned 200 and 46,160 bytes of app shell, byte-identical to
the browser's.
"""
from __future__ import annotations

import pytest

CRAWLER = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
BROWSER = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
           "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")


def test_an_unregistered_path_is_404_to_a_crawler(client):
    response = client.get("/definitely-not-a-page", user_agent=CRAWLER)
    assert str(response.status).startswith("404"), response.status


def test_the_same_path_is_still_the_shell_to_a_browser(client):
    """The browser lane keeps Dash's own 404 page, which is a better
    experience than a bare status code. This is the positive control: without
    it, 404ing everything would pass the test above."""
    response = client.get("/definitely-not-a-page", user_agent=BROWSER)
    assert str(response.status).startswith("200"), response.status
    assert response.text.lstrip().lower().startswith("<!doctype")


def test_a_registered_page_is_200_on_both_lanes(client):
    for label, ua in (("crawler", CRAWLER), ("browser", BROWSER)):
        response = client.get("/backends", user_agent=ua)
        assert str(response.status).startswith("200"), f"{label}: {response.status}"


@pytest.mark.parametrize("path", [
    "/llms.txt", "/backends/llms.txt", "/robots.txt", "/sitemap.xml",
    "/healthz", "/assets/main.css", "/.well-known/api-catalog",
    "/.well-known/agent-skills/index.json",
])
def test_the_routes_with_no_page_behind_them_are_untouched(client, path):
    """THE BOUNDARY IS THE POINT. A rule that 404'd "anything unregistered"
    would break every route this app serves without a page — which is most of
    the machine lane, i.e. exactly the readers this item is for."""
    response = client.get(path, user_agent=CRAWLER)
    assert str(response.status).startswith("200"), f"{path}: {response.status}"


def test_the_decision_keys_on_the_catch_all_not_on_a_prefix_list(app_module):
    """Detect: the branch asks whether Dash's catch-all would serve the path,
    not whether the path looks like a page. A prefix allowlist would drift
    the day someone adds a route."""
    from lib.soft404 import is_missing_page

    assert is_missing_page(app_module.app, "/definitely-not-a-page") is True
    assert is_missing_page(app_module.app, "/backends") is False
    assert is_missing_page(app_module.app, "/llms.txt") is False
    assert is_missing_page(app_module.app, "/healthz") is False
    assert is_missing_page(app_module.app, "/assets/main.css") is False


def test_a_registered_but_hidden_page_is_not_this_branchs_business(app_module):
    """/admin/* already answers 404 to a crawler through the TIER gate, and
    this branch must not claim that behaviour as its own — the two answer the
    same status for different reasons, and conflating them would hide a
    regression in either."""
    from lib.soft404 import is_missing_page

    assert is_missing_page(app_module.app, "/admin/traffic") is False


def test_the_lane_comes_from_the_one_classifier(app_module):
    """Never a User-Agent list here — this repo deleted its last one at
    1.6.34 and the reason has not changed."""
    from lib.soft404 import is_crawler

    assert is_crawler(CRAWLER) is True
    assert is_crawler(BROWSER) is False

    import ast

    from conftest import REPO_ROOT

    # PARSED, not grepped, and docstrings excluded BY NODE rather than by
    # comparing text. The first version searched raw source and matched the
    # module's own docstring, which describes the measurement that motivated
    # the fix; the second compared against `ast.get_docstring`, which returns
    # CLEANED text that never equals the raw constant. A detect reading prose
    # about the thing it hunts, twice in one test.
    tree = ast.parse((REPO_ROOT / "lib" / "soft404.py").read_text())
    docstring_nodes = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef)):
            body = getattr(node, "body", None) or []
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                docstring_nodes.add(id(body[0].value))

    ua_tokens = [
        node.value for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
        and id(node) not in docstring_nodes
        and any(token in node.value.lower() for token in
                ("googlebot", "bingbot", "gptbot", "claudebot"))
    ]
    assert ua_tokens == [], (
        f"a User-Agent list has appeared in lib/soft404.py: {ua_tokens} — "
        "there is ONE classifier, and this repo deleted its last local list "
        "at 1.6.34"
    )


def test_a_router_that_cannot_be_read_serves_what_it_would_have(app_module,
                                                                monkeypatch):
    """Never turn a diagnostic into an outage."""
    from lib import soft404

    monkeypatch.setattr(soft404, "registered_paths",
                        lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    assert soft404.is_missing_page(app_module.app, "/whatever") is False
