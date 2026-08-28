"""HEAD answers wherever GET answers — on every backend (1.6.32).

The defect this pins was live on the wire for the whole life of the ASGI
lane and invisible to everything the contract reads. Werkzeug derives a
HEAD rule from every GET rule; **FastAPI's ``APIRoute`` does not**, so a
route declared ``@router.get(...)`` answers **405** to HEAD. The layer
matters and cost three probes to locate (corrected 1.6.33):
``starlette.routing.Route`` adds HEAD wherever GET is present, exactly as
Werkzeug does — it is FastAPI that takes ``methods`` literally. Seven ASGI
hosts across the network were measured 405ing HEAD on every route on
2026-08-27/28 — both FastAPI forks, the hub, four second-ring sites —
``/healthz`` included: the default probe method of most uptime monitors,
against hosts whose deploy proof IS ``/healthz``.

Why it hid so well, and what that demands of this file:

* CI never issued a HEAD, both live tools GET (correctly — "probe with
  GET, never HEAD" is the standing rule precisely BECAUSE of this), and
  a browser never sends HEAD for a document.
* The one probe that did run HEAD in-process ran it against ``/`` with a
  crawler UA — the single case that succeeds, because the package's
  prerender middleware answers before the request reaches the router at
  all — and concluded the app code was fine. So this file exercises the
  router (a browser UA on ``/``) and the routes the template does NOT
  declare, not just the two it does.
* **The pin must therefore run per backend.** A test that passes on all
  three before the fix is testing the test client, not the router.
"""
from __future__ import annotations

import pytest

from conftest import BROWSER_UA, CRAWLER_UA, backend

# The four crawler-facing surfaces plus the probe. Only two of them
# (`/healthz`, `/api/*`) are declared by this tree: `/llms.txt`,
# `/robots.txt` and `/sitemap.xml` come from dash-improve-my-llms'
# per-backend adapter and `/` from Dash's page catch-all, which is why
# the fix cannot live in route declarations here.
CORE_PATHS = ["/", "/healthz", "/llms.txt", "/robots.txt", "/sitemap.xml"]


def assert_head_matches_get(client, path: str, user_agent: str) -> None:
    get = client.get(path, user_agent=user_agent)
    head = client.head(path, user_agent=user_agent)

    # Non-vacuity: a 405/405 pair is "parity" too. The GET has to work
    # first, or this file passes on a site that serves nothing.
    assert get.status == 200, (
        f"GET {path} answered {get.status} as {user_agent.split('/')[0]} — "
        "the parity assertions below would be vacuous"
    )
    assert head.status == get.status, (
        f"HEAD {path} answered {head.status} where GET answered "
        f"{get.status}. On the ASGI lane a 405 here means the router has "
        "no HEAD rule for a GET route."
    )
    assert head.content_type == get.content_type, (
        f"HEAD {path} content-type {head.content_type!r} != GET "
        f"{get.content_type!r}"
    )
    # `Response.headers` keeps the LAST value per name, so a multi-Link
    # response compares its last Link on both sides — the same collapse
    # applied to both, which is all this assertion needs.
    assert head.header("link") == get.header("link"), (
        f"HEAD {path} Link {head.header('link')!r} != GET "
        f"{get.header('link')!r} — a HEAD that loses the discovery "
        "headers is the shape this defect wore before it was measured"
    )

    # The body, where the layer under test is the one that empties it.
    # Werkzeug's client and Starlette's both strip it; Quart's does not,
    # and no part of the Quart app does either — h11, under uvicorn and
    # hypercorn both, frames a HEAD response as content-length 0 and
    # never writes those bytes (h11/_connection.py::_body_framing). So on
    # Quart the emptiness is the SERVER's and asserting it here would be
    # asserting something nothing under test performs. Said plainly
    # rather than asserted loosely: comparing the two bodies instead
    # fails on Dash's per-render ids, which is a fact about Dash.
    if backend() != "quart":
        assert head.text == "", (
            f"HEAD {path} returned {len(head.text)} bytes of body"
        )


@pytest.mark.parametrize("path", CORE_PATHS)
def test_head_matches_get_for_a_crawler(client, path):
    assert_head_matches_get(client, path, CRAWLER_UA)


@pytest.mark.parametrize("path", CORE_PATHS)
def test_head_matches_get_for_a_browser(client, path):
    """The browser lane, and on ``/`` it is the one that means something.

    A crawler's ``HEAD /`` is answered by the prerender middleware before
    routing; a browser's is not. This leg is what actually asks the
    router whether it has a HEAD rule for the page catch-all.
    """
    assert_head_matches_get(client, path, BROWSER_UA)


def test_healthz_answers_head(client):
    """Stated once on its own because it is the operational half.

    HEAD is the default probe method of a large share of uptime
    monitoring. A 405 here reads as "the site is down" while the site is
    perfectly healthy — and this is the route cd.yml's build-match wait
    and the hub's hourly sweep both depend on.
    """
    get = client.get("/healthz")
    head = client.head("/healthz")
    assert (get.status, head.status) == (200, 200)
    assert head.content_type.startswith("application/json")
