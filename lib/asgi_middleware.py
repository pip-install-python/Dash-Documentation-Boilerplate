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


# ``HeadAsGetMiddleware`` LIVED HERE FROM 1.6.32 TO 1.6.44, AND IS RETIRED.
#
# Why it existed: FastAPI's ``APIRoute`` takes ``methods`` literally, so a
# route declared ``@router.get(...)`` answered 405 to HEAD — and Dash's page
# catch-all is an ``APIRoute`` too, registered from the ASGI lifespan
# startup, which nothing in this repo could declare methods on. Every route
# of both FastAPI forks 405'd on HEAD (measured on pannellum and
# muischeduler, 2026-08-27), ``/healthz`` included, which is the default
# probe method of most uptime monitors.
#
# Why it is gone: at dash-improve-my-llms 2.9.4 the package walks the
# router itself and adds HEAD wherever GET is allowed, INCLUDING Dash's
# routes and its lifespan-registered catch-all — the one case this
# middleware was left in for. Its own docstring said "DO NOT REMOVE THIS
# WHEN THE PACKAGE FLOOR REACHES 2.7.2", and that was true AT 2.7.2, when
# the package fixed only its own doc routes. It stopped being true at
# 2.9.4, which is why the retirement is gated on the pin (item 1) and not
# on the calendar.
#
# The reason to remove rather than leave harmless: it converts HEAD to GET
# ABOVE the router, so every HEAD looked correct whatever the router did.
# It MASKED the package's fix instead of conflicting with it, and would
# have masked a regression in it just as well.
#
# MEASURED BEFORE REMOVING (1.6.44, dimll 2.9.4, FastAPI lane, in-process):
# 5 paths x 3 UAs — /healthz, /llms.txt, /robots.txt, /sitemap.xml, / with
# browser, crawler and internal-probe UAs — HEAD status == GET status in
# all 15 pairs WITHOUT this middleware, including ``/`` to a browser UA,
# the exact case the old docstring said would 405. The disable was proved
# non-vacuous first: the middleware stack was asserted to contain
# ``HeadAsGetMiddleware`` in the enabled run and not to contain it in the
# disabled one, because a parity result from a run that never removed
# anything would have been worthless. tests/test_head_method.py holds the
# parity so this cannot regress silently.


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


class StaticCacheMiddleware(BaseHTTPMiddleware):
    """Give ``/assets/`` a cache lifetime (1.6.44 item 6g).

    The ASGI half of the Flask ``after_request`` in ``run.py``; the policy
    itself lives in ``lib/static_cache`` so the two lanes cannot drift into
    serving different lifetimes for the same file.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        from lib.static_cache import cache_control_for

        value = cache_control_for(request.url.path)
        if value and response.status_code == 200:
            response.headers["Cache-Control"] = value
        return response


def register_asgi_middleware(app) -> None:
    """Attach all ASGI middleware to ``app.server`` (a FastAPI instance).

    ``HeadAsGetMiddleware`` was removed here at 1.6.44 (item 2) once the
    package answers HEAD at the route level — see the module docstring for
    what was measured before removing it.
    """
    app.server.add_middleware(AnalyticsMiddleware)
    app.server.add_middleware(StaticCacheMiddleware)
