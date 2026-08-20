---
name: FastAPI Showcase
description: What the FastAPI backend unlocks in this boilerplate — OpenAPI docs, a native JSON API, ASGI middleware, and a path to MCP.
endpoint: /fastapi-showcase
package: fastapi-showcase
icon: simple-icons:fastapi
lastmod: 2026-08-16
---

.. llms_copy::FastAPI Showcase

.. toc::

### Why a dedicated showcase?

Most Dash docs assume Flask. With Dash 4.1+ you can swap in a real FastAPI app under the hood, and once you do, things you used to bolt on with extra packages — OpenAPI docs, native async, websocket callbacks, structured JSON APIs — become first-class.

This boilerplate ships both backends side by side. Switch with one env var:

```env
# .env
DASH_BACKEND=fastapi
```

When the badge in the header reads **FastAPI · async**, the surface described below is live.

---

### What lights up on FastAPI

| Surface | Path | Notes |
|--|--|--|
| Swagger UI | `/docs` | Interactive OpenAPI explorer (FastAPI built-in) |
| ReDoc | `/redoc` | Alternative OpenAPI viewer |
| OpenAPI schema | `/openapi.json` | Machine-readable spec |
| Liveness probe | `/healthz` | Returns active backend + Dash version |
| Active backend | `/api/backend` | Backend name, label, async flag |
| Page registry | `/api/pages` | All Dash pages, sortable list with metadata |
| LLM markdown | `/<page>/llms.txt` | Mounted by `dash-improve-my-llms` — backend-detected, identical body across Flask/FastAPI/Quart |
| Bot policy | `/robots.txt` | Same surface as the Flask build; same `RobotsConfig` |
| Sitemap | `/sitemap.xml` | Same priority inference; respects `mark_hidden()` |

Everything in the **Surface** column appears in `/docs` because the routes are declared with typed Pydantic models and `response_model=...` — Swagger UI picks them up automatically.

#### Try it live

This widget hits the JSON endpoints directly from your browser and pretty-prints the response. Useful for confirming the surface is up before you point a real client at it.

.. exec::docs.fastapi-showcase.endpoint_explorer
    :code: false

---

### The OpenAPI link in the header

The header surfaces a Swagger badge **only when the active backend is FastAPI**. The logic is small:

```python
# components/header.py
def _create_openapi_link():
    info = get_backend_info()
    if info.name != "fastapi":
        return None
    return dmc.Anchor(
        dmc.Badge("OpenAPI", leftSection=DashIconify(icon="logos:swagger"), ...),
        href="/docs",
        target="_blank",
    )
```

Open it in a new tab and you can `Try it out` against any of the routes without leaving the app.

---

### How the routes are mounted

`run.py` calls `add_llms_routes(app)` unconditionally — dash-improve-my-llms detects the FastAPI backend and mounts its own router. The boilerplate's `lib/asgi_routes.py` only carries the **showcase** surfaces (`/healthz`, `/api/backend`, `/api/pages`) — the things that demonstrate first-class OpenAPI integration:

.. source::lib/asgi_routes.py

Two things to notice:

1. **Pydantic models drive the schema.** `BackendInfoModel`, `PageSummary`, `PageListResponse`, `HealthResponse` — each one shows up in `/docs` with example values.
2. **Route ordering matters.** Mount your showcase routes *before* `add_llms_routes(app)`. The package's `/<page>/llms.txt` is greedy and would otherwise shadow `/api/*` matches.

`run.py` calls `register_asgi_routes(app, BACKEND_INFO)` in the `elif BACKEND == "fastapi":` branch and that's the whole wire-up.

---

### Analytics as ASGI middleware

The Flask build uses `@server.before_request` for the visitor tracker. Under FastAPI, that hook doesn't exist — instead we mount a Starlette middleware:

.. source::lib/asgi_middleware.py

This sits transparently in front of every request, including Dash's internal `_dash-update-component` calls, with no impact on callback latency (analytics writes go through the same backgroundable tracker).

---

### Async callbacks (you can write them now)

Once you're on FastAPI, callbacks can be `async def` and `await` directly. A typical pattern:

```python
import httpx
from dash import Input, Output, callback

@callback(Output("price", "children"), Input("ticker", "value"))
async def fetch_price(ticker):
    async with httpx.AsyncClient(timeout=5) as client:
        r = await client.get(f"https://api.example.com/{ticker}")
    return r.json()["price"]
```

The key discipline: **don't mix sync I/O into async callbacks**. Replace `requests` with `httpx.AsyncClient`, `psycopg2` with `asyncpg`, `time.sleep` with `asyncio.sleep`. A single blocking call inside an `async def` will stall every other request handled by that worker.

If you can't avoid a blocking call, wrap it:

```python
import asyncio

@callback(Output("data", "children"), Input("trigger", "n_clicks"))
async def slow_path(_):
    return await asyncio.to_thread(legacy_sync_fetch)
```

#### See the difference

This widget runs two callbacks side by side: a sync one that sleeps 3 × 500 ms sequentially (~1500 ms wall-clock) and an async one that fans out the same work with `asyncio.gather` (~500 ms). Both work on any backend, but the async path is what scales when concurrent users hit your app.

.. exec::docs.fastapi-showcase.async_demo
    :code: false

#### Stress test it

The button below fires N parallel `GET /healthz` requests from your browser and reports wall-clock + percentile latencies. On the FastAPI backend the wall-clock stays flat as N rises (the event loop services them concurrently). On Flask's default sync workers, wall-clock grows roughly linearly with N — that's the practical cost of WSGI's one-request-per-thread model.

.. exec::docs.fastapi-showcase.stress_test
    :code: false

---

### Websocket callbacks (Dash 4.2+)

ASGI gives Dash native websocket support. From a callback you can grab the websocket directly via `ctx.websocket` and push updates to the browser without polling.

```python
from dash import Input, Output, callback, ctx

@callback(Output("stream", "children"), Input("start", "n_clicks"))
async def stream(_):
    ws = ctx.websocket
    for i in range(10):
        await ws.send({"i": i})
    return "done"
```

This is gated behind the FastAPI backend — the Flask backend will simply not expose `ctx.websocket`.

---

### MCP server (Dash 4.3+)

When Dash 4.3 ships, the same FastAPI app can expose the dashboard's layout, components, pages, and (whitelisted) callbacks as MCP tools over Streamable HTTP. The wire-up in this boilerplate is best-effort:

```python
# run.py — runs only if the installed Dash supports it
try:
    from dash import mcp_enabled
    HAS_MCP = True
except ImportError:
    HAS_MCP = False

if HAS_MCP and BACKEND == "fastapi" and os.environ.get("DASH_MCP_ENABLED") == "1":
    mcp_enabled(app)
```

Set `DASH_MCP_ENABLED=1` in `.env` once you upgrade to a Dash version that includes MCP, and the server will be reachable at `/mcp` (subject to whatever path Dash settles on for the GA release).

---

### What's missing on FastAPI today

Honesty matters for a docs site:

- **`set_props`** works on FastAPI but if you scale to multiple workers you'll need Redis pub/sub for cross-worker fanout (same caveat as Flask).
- The `dash-improve-my-llms` MCP bridge silently no-ops on Dash 3.x and on Dash 4.1/4.2 — it requires Dash 4.3+ (where `dash.mcp` lands). The HTTP surfaces (`/llms.txt`, `/robots.txt`, `/sitemap.xml`) work on every version.

---

### Deployment

Swap the process manager:

```bash
# Flask (Dockerfile default today)
gunicorn run:server -b 0.0.0.0:8550

# FastAPI
pip install "dash[fastapi]" "uvicorn[standard]"
uvicorn run:server --host 0.0.0.0 --port 8550 \
    --workers 4 --proxy-headers --forwarded-allow-ips='*'
```

The `app.server` attribute returns either a `Flask` or `FastAPI` instance depending on `DASH_BACKEND`, so `run:server` works for both — only the runner changes.

---

### Recap

| Concern | Before | After |
|--|--|--|
| Backend selection | hardcoded Flask | `DASH_BACKEND` env var |
| OpenAPI surface | none | `/docs`, `/redoc`, `/openapi.json` |
| Health check | none | `/healthz` |
| JSON API for tooling | none | `/api/backend`, `/api/pages` |
| Async callbacks | thread-pooled | native `async def` |
| Websocket callbacks | not available | `ctx.websocket` |
| MCP integration | not available | best-effort, gated on `DASH_MCP_ENABLED` |
| LLM routes | `add_llms_routes()` | ported in `lib/asgi_routes.py` (subset) |
| Analytics | `before_request` | Starlette middleware |

Flip the env var, restart, watch the badge change. That's the whole user surface — everything else is a clean import switch under the hood.
