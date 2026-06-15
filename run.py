import os
import dash
from dash import Dash, _dash_renderer
from components.appshell import create_appshell
import dash_mantine_components as dmc

# AI/LLM Integration & SEO — dash-improve-my-llms 2.0
# 2.0 supports Flask, FastAPI, and Quart via a single backend-detecting
# dispatcher. The custom Flask-only routes that used to live in this file
# (`/<page>/llms.txt`, `/<page>/page.json`, `/<page>/llms.toon`) are gone —
# the package owns `/llms.txt` and `/<page>/llms.txt`, and `/page.json` /
# `/llms.toon` were intentionally dropped in 2.0 (Dash 4.3 MCP covers the
# structured-introspection job they were doing).
from dash_improve_my_llms import (
    add_llms_routes,
    LLMSConfig,
    RobotsConfig,
    mark_hidden,
    register_page_metadata,
)

# Analytics tracking
from lib.analytics_tracker import tracker

# Backend selection (flask | fastapi | quart) — see lib/backend.py
from lib.backend import resolve_backend, get_backend_info

scripts = [
    "https://unpkg.com/hotkeys-js/dist/hotkeys.min.js",
]

# ----------------------------------------------------------------------------
# Pluggable backend (Dash 4.1+)
# ----------------------------------------------------------------------------
BACKEND = resolve_backend()
BACKEND_INFO = get_backend_info(BACKEND)
IS_FLASK = BACKEND == "flask"

print(f"[boilerplate] Starting Dash {dash.__version__} on backend='{BACKEND}'")

app = Dash(
    __name__,
    backend=BACKEND,
    suppress_callback_exceptions=True,
    use_pages=True,
    external_scripts=scripts,
    update_title=None,
    prevent_initial_callbacks=True,
    index_string=open('templates/index.html').read()
)

# Expose backend info so layout components can render a badge without
# re-reading the env var (which could drift between processes/workers).
app._backend_info = BACKEND_INFO

# ============================================================================
# AI/LLM & SEO Configuration
# ============================================================================

# Set base URL for SEO (change to your production URL)
app._base_url = "https://dash-documentation-boilerplate.onrender.com"

# Configure bot management policies. See dash-improve-my-llms 2.0 SKILLS for
# the full menu — balanced default = block training crawlers, allow AI search
# citations and traditional search.
app._robots_config = RobotsConfig(
    block_ai_training=False,      # Block GPTBot, CCBot, anthropic-ai, etc.
    allow_ai_search=True,         # Allow ChatGPT-User, ClaudeBot, PerplexityBot
    allow_traditional=True,       # Allow Googlebot, Bingbot, etc.
    crawl_delay=10,
    disallowed_paths=[],
)

# ============================================================================
# Register supplemental metadata for the home page.
# Markdown-driven pages register their own LLMS_DOC inside pages/markdown.py
# (the expanded markdown body becomes the literal /llms.txt response).
# ============================================================================

register_page_metadata(
    path="/",
    name="Dash Documentation Boilerplate",
    description=(
        "A modern, markdown-driven documentation system for Dash applications "
        "built on Dash Mantine Components, with first-class AI/LLM and SEO "
        "integration via dash-improve-my-llms 2.0."
    ),
)

# Internal pages — excluded from /sitemap.xml, blocked in /robots.txt,
# skipped by the MCP bridge, and return 404 to crawler requests on the
# page URL and on /<page>/llms.txt.
mark_hidden("/analytics/traffic")

# ============================================================================
# FastAPI showcase routes (only when running on FastAPI).
# These are NOT the AI/LLM endpoints — those are handled by add_llms_routes
# below. They are a small native API surface (`/healthz`, `/api/backend`,
# `/api/pages`) that demonstrates first-class OpenAPI/Swagger UI integration
# under Dash 4.1+'s FastAPI backend.
#
# Mounted BEFORE add_llms_routes so the package's catch-all
# `/<page>/llms.txt` matcher doesn't shadow these.
# ============================================================================

if BACKEND == "fastapi":
    from lib.asgi_routes import register_asgi_routes
    register_asgi_routes(app, BACKEND_INFO)
    print(
        "[boilerplate] FastAPI showcase routers mounted: /healthz, "
        "/api/backend, /api/pages. Swagger UI at /docs, ReDoc at /redoc."
    )

# Wire up the package: /llms.txt, /<page>/llms.txt, /robots.txt, /sitemap.xml,
# bot-detection middleware, and (on Dash 4.3+) MCP resource registration.
# Works under Flask, FastAPI, and Quart — no gating needed.
add_llms_routes(app, LLMSConfig(warn_missing_llms_doc=True))

# ============================================================================

app.layout = create_appshell(dash.page_registry.values())

server = app.server

# ============================================================================
# Analytics Tracking — backend-specific.
# Flask uses before_request; FastAPI uses ASGI middleware.
# ============================================================================

if IS_FLASK:
    from flask import request as _flask_request

    @server.before_request
    def track_visitor():
        """Track visitor analytics before each request."""
        try:
            tracker.track_visit(
                _flask_request.path,
                _flask_request.headers.get('User-Agent', ''),
                _flask_request.remote_addr,
            )
        except Exception:
            pass

elif BACKEND == "fastapi":
    from lib.asgi_middleware import register_asgi_middleware

    register_asgi_middleware(app)

# ============================================================================
# Optional: Dash 4.3+ MCP server.
# When available, this exposes the app's layout, components, pages and
# (whitelisted) callbacks to MCP-compatible LLM clients over Streamable HTTP.
# Best-effort: silently no-op on Dash <4.3 or on non-FastAPI backends.
#
# Note: dash-improve-my-llms 2.0 *also* registers each page's LLMS_DOC as a
# `dash.mcp` resource via its MCP bridge — that gives MCP clients access to
# the prose docs alongside whatever native introspection Dash provides.
# ============================================================================

try:
    from dash import mcp_enabled  # type: ignore[attr-defined]
    HAS_MCP = True
except ImportError:
    HAS_MCP = False

if HAS_MCP and BACKEND == "fastapi" and os.environ.get("DASH_MCP_ENABLED", "0") == "1":
    try:
        mcp_enabled(app)  # noqa
        print("[boilerplate] MCP server enabled at /mcp (Dash 4.3+ feature).")
    except Exception as e:  # pragma: no cover - best-effort
        print(f"[boilerplate] MCP wire-up failed: {e!r}")
elif not HAS_MCP and BACKEND == "fastapi":
    print(
        f"[boilerplate] MCP not available in dash {dash.__version__} "
        "(needs >=4.3). Set DASH_MCP_ENABLED=1 once upgraded."
    )

# ============================================================================


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port='8559')
