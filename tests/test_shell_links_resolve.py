"""Every internal link in the app shell resolves to a REGISTERED page.

1.6.44 item 11, from pipdocs f5ec42f: `/terms` and `/privacy` were linked
from every page in the fleet's footer and served nothing. They did not show
up as 404s because Dash answers 200 for ANY path — the server returns the
app shell and the client-side router decides what to render — so a status
sweep over the site cannot see a broken internal link. It reports 200 and
moves on.

The detect therefore has to be REGISTRATION, not a request: walk the shell's
internal hrefs and hold each one against `dash.page_registry`. That is a
question only the layout can answer, which is also why curl cannot ask it
(the shell is built by React from `app.layout`, so the served HTML does not
contain these links at all — the same reason a `curl | grep skip-link`
returns zero on a host whose skip link works).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
from dash.development.base_component import Component

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Paths served by something other than a registered page: the package's own
# routes and this app's native ones. Each is a real URL with a real handler,
# just not a Dash page.
NON_PAGE_ROUTES = {
    "/llms.txt", "/robots.txt", "/sitemap.xml", "/healthz",
    "/api/backend", "/api/pages", "/api/llms.txt",
}

# Swagger UI and ReDoc exist ONLY on the FastAPI backend, and the header's
# OpenAPI badge is gated on that (`_create_openapi_link` returns None
# otherwise). They are whitelisted per LANE rather than unconditionally: a
# blanket entry would let an un-gated badge ship a soft 404 on the Flask and
# Quart lanes and still pass this test, which is the exact defect the item
# exists to catch.
ASGI_DOC_ROUTES = {"/docs", "/redoc"}


def _served_non_page_routes() -> set:
    from lib.backend import get_backend_info

    routes = set(NON_PAGE_ROUTES)
    if get_backend_info().name == "fastapi":
        routes |= ASGI_DOC_ROUTES
    return routes


def _hrefs(node, out: list) -> None:
    """Every `href` in the tree, depth-first."""
    if isinstance(node, (list, tuple)):
        for child in node:
            _hrefs(child, out)
        return
    if not isinstance(node, Component):
        return
    href = getattr(node, "href", None)
    if isinstance(href, str):
        out.append(href)
    children = getattr(node, "children", None)
    if children is not None:
        _hrefs(children, out)


def _internal(href: str) -> bool:
    if not href.startswith("/"):
        return False          # external, a mailto:, or an in-page anchor
    return not href.startswith("//")


@pytest.fixture(scope="module")
def shell(app_module):
    """The app shell EXACTLY as run.py builds it.

    `create_appshell(dash.page_registry.values())` is the literal expression
    at run.py's `app.layout =`, so this walks header, navbar, mobile drawer
    and footer together rather than a hand-picked pair — the artifact the
    claim is about.
    """
    import dash

    from components.appshell import create_appshell

    return create_appshell(dash.page_registry.values())


@pytest.fixture(scope="module")
def registered(app_module):
    import dash

    return {entry["path"] for entry in dash.page_registry.values()}


def test_the_registry_is_populated(registered):
    """Note 88: an empty registry would make every assertion below green."""
    assert len(registered) >= 5, f"only {len(registered)} pages registered"


def test_the_walk_finds_links_at_all(shell):
    """And a shell with no links would do the same."""
    found = []
    _hrefs(shell, found)
    internal = [h for h in found if _internal(h)]
    assert found, "the walk found no hrefs anywhere in the shell"
    assert internal, (
        f"the shell has {len(found)} hrefs and none are internal — the walk "
        "is looking at the wrong tree"
    )


def test_every_internal_shell_link_is_a_registered_page(shell, registered):
    """Item 11. A soft 404 advertised from every page is still a soft 404."""
    found = []
    _hrefs(shell, found)
    internal = {h.split("#")[0].split("?")[0].rstrip("/") or "/"
                for h in found if _internal(h)}
    known = {p.rstrip("/") or "/" for p in registered} | {
        p.rstrip("/") or "/" for p in _served_non_page_routes()}
    unserved = sorted(internal - known)
    assert unserved == [], (
        f"the app shell links to {len(unserved)} path(s) nothing serves: "
        f"{unserved} — Dash answers 200 for these and renders nothing"
    )


def test_the_check_goes_red_when_a_link_points_at_nothing(registered):
    """The mutation, as a test rather than as a claim in a commit message.

    A guard that has never been shown to fail is a guard nobody has tested.
    """
    import dash_mantine_components as dmc

    broken = dmc.Anchor("Terms", href="/terms-that-nobody-registered")
    found = []
    _hrefs(broken, found)
    internal = {h.rstrip("/") for h in found if _internal(h)}
    known = {p.rstrip("/") for p in registered} | {
        p.rstrip("/") for p in _served_non_page_routes()}
    assert internal - known == {"/terms-that-nobody-registered"}, (
        "the walk cannot see a broken link, so its green means nothing"
    )


def test_the_openapi_badge_is_gated_on_the_lane_that_serves_it(app_module):
    """/docs and /redoc exist only on FastAPI, so the link must too.

    This is the whitelist's own guard: if the badge stopped being gated, the
    Flask and Quart lanes would advertise a path that answers with the app
    shell and renders nothing — and a lane-blind whitelist would have called
    that green.
    """
    from components.header import _create_openapi_link
    from lib.backend import get_backend_info

    rendered = _create_openapi_link() is not None
    assert rendered == (get_backend_info().name == "fastapi"), (
        "the OpenAPI badge no longer tracks the backend that serves it"
    )
