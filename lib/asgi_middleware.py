"""
ASGI/Starlette middleware ports of Flask-only hooks used in this boilerplate.

When the Dash backend is FastAPI, these slot in where the Flask
``before_request`` decorator was used.
"""
from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from lib.analytics_tracker import tracker


class HeadAsGetMiddleware:
    """Answer ``HEAD`` wherever ``GET`` is served (1.6.32).

    HTTP requires it, Werkzeug derives it from every ``GET`` rule for free,
    and Starlette does not: a FastAPI route declared ``@router.get(...)``
    answers ``405 Method Not Allowed`` to ``HEAD``. On the wire that meant
    **every route of both FastAPI forks 405'd on HEAD** — measured on
    pannellum and muischeduler, 2026-08-27 — including ``/healthz``, which
    is the default probe method of most uptime monitors, and ``/robots.txt``
    and ``/sitemap.xml``, whose entire job is to be fetched by crawlers that
    may preflight with HEAD.

    Why middleware and not ``methods=["GET", "HEAD"]`` on the declarations:
    this tree only declares two of the affected surfaces. ``/llms.txt``,
    ``/<page>/llms.txt``, ``/robots.txt``, ``/sitemap.xml`` and the policy
    panel are registered GET-only by dash-improve-my-llms' own FastAPI
    adapter, and ``/`` by Dash's page catch-all. Fixing the declarations we
    own would leave three of the four crawler-facing surfaces 405ing, so the
    fix has to sit above the router. Pure ASGI rather than
    ``BaseHTTPMiddleware`` so it neither buffers the response nor breaks
    streaming.

    The re-dispatch is a full ``GET``: same status, same headers, same work.
    The body is dropped here so the response is empty at every layer under
    test — on the wire h11 (under both uvicorn and hypercorn) already frames
    a HEAD response as content-length 0 and never writes those bytes, which
    is why Quart needs nothing and gets nothing.
    """

    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope, receive, send) -> None:
        if scope.get("type") != "http" or scope.get("method") != "HEAD":
            await self.app(scope, receive, send)
            return

        sent_body = False

        async def send_without_body(message) -> None:
            nonlocal sent_body
            if message["type"] != "http.response.body":
                await send(message)
                return
            # A streaming handler emits many body messages; exactly one
            # empty, final message goes out or the server raises on the
            # message after the response completed.
            if sent_body:
                return
            sent_body = True
            await send({"type": "http.response.body", "body": b"",
                        "more_body": False})

        await self.app({**scope, "method": "GET"}, receive, send_without_body)


class AnalyticsMiddleware(BaseHTTPMiddleware):
    """Track every request through the analytics tracker.

    Mirrors the Flask ``before_request`` shim in ``run.py``. Failures are
    silently swallowed — analytics should never block a real response.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            client = request.client
            ip = client.host if client else None
            # Headers carry the real client IP/country behind a proxy or CDN;
            # request.client is the last hop (the proxy) in production.
            tracker.track_visit(
                request.url.path,
                request.headers.get("user-agent", ""),
                ip,
                headers=dict(request.headers),
            )
        except Exception:
            pass
        return await call_next(request)


def register_asgi_middleware(app) -> None:
    """Attach all ASGI middleware to ``app.server`` (a FastAPI instance).

    Order matters twice over: Starlette runs the LAST-added middleware
    outermost, so ``HeadAsGetMiddleware`` goes on after the tracker and the
    HEAD becomes a GET before anything else — the package's bot middleware
    and the prerender included — sees the request.
    """
    app.server.add_middleware(AnalyticsMiddleware)
    app.server.add_middleware(HeadAsGetMiddleware)
