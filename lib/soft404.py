"""Unregistered paths answer 404 on the crawler lane (1.6.45 item 8, note 104).

Dash answers 200 for ANY path: the server returns the app shell and the
client-side router decides what to render. For a browser that is correct —
the router shows a 404 page. For a crawler it is a SOFT 404: every
mistyped link, every stale URL, every probe gets a 200 and a page of
JavaScript, and search engines and agents index it as real.

Measured on this tree before the fix: `GET /definitely-not-a-page` with a
Googlebot UA returned 200 and 46,160 bytes of app shell — byte-identical to
what a browser got. A registered-but-hidden page, by contrast, already
answered correctly, because the gate knows a page exists only when it is
REGISTERED.

THE BOUNDARY IS THE POINT. A rule that 404s "anything unregistered" would
break `/assets/…`, `/_dash-*`, `/.well-known/*`, `/llms.txt`, `/healthz` and
every other route this app serves without a page behind it. So the question
asked here is narrower and exact: WOULD THE CATCH-ALL SERVE THIS? Dash's
page route is a single rule (`/<path:path>` on Flask, `/{path:path}` on the
ASGI lanes) and every other route has its own. If the router would hand the
path to the catch-all, and no registered page claims it, then nothing exists
there — whatever the shell would have rendered.

The browser lane is untouched: it keeps Dash's own 404 page, which is a
better experience than a bare status code.
"""
from __future__ import annotations

# Dash's page catch-all, per lane. Matching on the ENDPOINT/route rather
# than on a path prefix is what keeps this from guessing.
_FLASK_CATCHALL = "/<path:path>"
# BOTH spellings. Dash's lifespan-registered page route arrives as
# `{path:path}` with NO LEADING SLASH — measured after running the lifespan,
# and the single missing character is why the first version skipped nothing,
# counted the catch-all as a real route, and concluded every path was served
# on both ASGI lanes while passing on Flask.
_ASGI_CATCHALL = {"{path:path}", "/{path:path}"}


def registered_paths() -> set:
    """Every path `dash.page_registry` claims, normalised without a trailing
    slash (`/` itself stays `/`)."""
    import dash

    paths = set()
    for entry in dash.page_registry.values():
        path = (entry.get("path") or "").strip()
        if path:
            paths.add(path.rstrip("/") or "/")
    return paths


def _flask_serves_from_catchall(server, path: str) -> bool:
    try:
        adapter = server.url_map.bind("localhost")
        endpoint, _args = adapter.match(path)
    except Exception:
        # Unroutable, or a method mismatch — Flask answers that itself and
        # this module has no business overriding it.
        return False
    return endpoint == _FLASK_CATCHALL


def _asgi_no_concrete_route(server, path: str) -> bool:
    """True when only Dash's page catch-all could serve `path`.

    Asked as "does any CONCRETE route match?" rather than "does the catch-all
    match?", because on the ASGI lanes the catch-all IS NOT IN `server.routes`
    at import time — Dash registers it from the lifespan startup (the same
    fact behind the kit's HEAD trap, and behind the in-process battery shim
    needing to run lifespan). A check that looked for it found nothing and
    concluded every path was served, so the crawler 404 never fired on two
    of this repo's three lanes while passing on the third.

    Phrased this way the answer is the same before and after lifespan, which
    is the property that matters: the test environment and production must
    not disagree about what exists.
    """
    from starlette.routing import Match

    scope = {"type": "http", "method": "GET", "path": path, "headers": [],
             "query_string": b"", "root_path": ""}
    for route in getattr(server, "routes", []):
        if str(getattr(route, "path", "")) in _ASGI_CATCHALL:
            continue
        try:
            match, _child = route.matches(scope)
        except Exception:
            continue
        if match is not Match.NONE:
            return False
    return True


def is_missing_page(app, path: str) -> bool:
    """True when nothing exists at `path` — the catch-all would serve it and
    no registered page claims it."""
    try:
        normalised = (path or "/").rstrip("/") or "/"
        if normalised in registered_paths():
            return False

        server = app.server
        if hasattr(getattr(server, "url_map", None), "bind"):
            return _flask_serves_from_catchall(server, path)
        return _asgi_no_concrete_route(server, path)
    except Exception:
        # Never turn a diagnostic into an outage: if the router cannot be
        # read, serve what the app would have served.
        return False


def is_crawler(user_agent: str) -> bool:
    """The one classifier, as always — never a User-Agent list here."""
    try:
        from dash_improve_my_llms import classify

        return (classify(user_agent or "") or {}).get("lane") == "crawler"
    except Exception:
        return False


def should_answer_404(app, path: str, user_agent: str) -> bool:
    """The whole decision, in one place so both lanes ask it identically."""
    return is_crawler(user_agent) and is_missing_page(app, path)


NOT_FOUND_BODY = (
    "# 404 — Not found\n\n"
    "No page exists at this path on this host. The site index is at "
    "/llms.txt.\n"
)
NOT_FOUND_TYPE = "text/markdown; charset=utf-8"
