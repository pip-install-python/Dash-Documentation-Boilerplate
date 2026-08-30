---
name: Pluggable Backends
description: Run this documentation site on Flask, FastAPI or Quart with one environment variable, and learn what each backend unlocks.
endpoint: /backends
package: backends
icon: mdi:server-network
lastmod: 2026-08-16
category: Backends
order: 1
---

.. llms_copy::Pluggable Backends

.. toc::

### Overview

Dash **4.1+** introduces a pluggable server backend. Instead of being hard-wired to Flask, a Dash app can now be created on top of **FastAPI** or **Quart**, unlocking native async, websocket callbacks, and a transport surface that works well with the new MCP tooling shipping in Dash 4.3.

This boilerplate exposes the choice through a single environment variable so you can flip backends without editing code:

```bash
# Default — fully featured, all integrations on
DASH_BACKEND=flask python run.py

# Async backends (install the extra first)
pip install "dash[fastapi]"
DASH_BACKEND=fastapi python run.py

pip install "dash[quart]"
DASH_BACKEND=quart python run.py
```

The badge in the header and the navbar reflects whichever backend booted, so you always know what's running.

---

### How it's wired

The active backend is resolved once in `lib/backend.py` and threaded into both `run.py` and the UI components:

.. source::lib/backend.py

`run.py` then passes the resolved name straight to the `Dash()` constructor:

```python
from lib.backend import resolve_backend, get_backend_info

BACKEND = resolve_backend()
BACKEND_INFO = get_backend_info(BACKEND)
IS_FLASK = BACKEND == "flask"

app = Dash(
    __name__,
    backend=BACKEND,            # <-- new in Dash 4.1
    suppress_callback_exceptions=True,
    use_pages=True,
    ...
)
app._backend_info = BACKEND_INFO
```

The only remaining Flask-only integration is the `before_request` analytics hook, which the boilerplate transparently swaps for a Starlette `BaseHTTPMiddleware` when the backend is FastAPI. `add_llms_routes(app)` from `dash-improve-my-llms` auto-detects the backend and mounts its own router under all three — no `IS_FLASK` gate is needed for the AI/LLM surfaces anymore.

---

### What you get on each backend

| Feature | Flask | FastAPI | Quart |
|--|--|--|--|
| Synchronous callbacks | yes | yes | yes |
| `async def` callbacks | n/a | yes | yes |
| Websocket callbacks (`ctx.websocket`) | no | yes (Dash 4.2+) | yes (Dash 4.2+) |
| Persistent callbacks (Dash 4.2 rc) | no | yes | yes |
| MCP server / `mcp_enabled` decorator (Dash 4.3) | partial | yes | yes |
| `add_llms_routes` (dash-improve-my-llms) | yes | yes | yes |
| `/llms.txt`, `/robots.txt`, `/sitemap.xml` | yes | yes | yes |
| `gunicorn` deploy | yes | n/a | n/a |
| `uvicorn` deploy | n/a | yes | yes |

The AI/LLM surfaces (`/llms.txt`, `/robots.txt`, `/sitemap.xml`, bot middleware, MCP bridge) work identically under all three backends — pick the one that matches the rest of your stack.

---

### Choosing a backend

#### Flask (default)

The safe choice. Everything in this boilerplate works without changes, including the analytics tracker, the `dash-improve-my-llms` integration, and the SEO routes.

Deploy with `gunicorn run:server -b 0.0.0.0:8550` (already wired into the included `Dockerfile`).

#### FastAPI

Pick this when you want:

- Async callbacks (`async def update_table(...)`)
- Real-time websocket callbacks for streaming UI updates
- A first-class MCP server using Dash 4.3's framework utilities
- Easy interop with an existing FastAPI app — just pass it in:

```python
from fastapi import FastAPI
from dash import Dash

api = FastAPI()
api.add_api_route("/healthz", lambda: {"ok": True})

app = Dash(__name__, server=api)        # Dash detects FastAPI automatically
```

Deploy with `uvicorn run:server --host 0.0.0.0 --port 8550`.

#### Quart

A drop-in option for teams already on Quart, or who want async with Flask-style ergonomics (`@server.before_request` becomes `@server.before_request` returning a coroutine).

```python
from quart import Quart
from dash import Dash

server = Quart(__name__)
app = Dash(__name__, server=server)
```

Deploy with `uvicorn run:server --host 0.0.0.0 --port 8550`.

---

### Custom backends

`Dash(backend=...)` also accepts a subclass of `dash.backends.base_server.BaseDashServer` plus matching request/response adapters, so internal frameworks (a hardened ASGI server, an in-process test harness, etc.) can be plugged in without forking Dash. See the `dash.backends` module for the protocol.

---

### Migration checklist for your own apps

1. Bump `dash>=4.1.0` (and `dash-mantine-components>=2.7.0` if you use DMC).
2. Replace any `app.run_server(...)` calls with `app.run(...)`.
3. Audit every `@app.server.before_request` / `@app.server.route` — Flask-only. Wrap them in an `if backend == "flask":` guard or rewrite as FastAPI/Quart middleware.
4. Install the extra: `pip install "dash[fastapi]"` or `pip install "dash[quart]"`.
5. Pass `backend="fastapi"` (or `"quart"`) to `Dash(...)`, or set `DASH_BACKEND` if you're using this boilerplate's helper.
6. Swap your process manager: `gunicorn` → `uvicorn` (or `hypercorn`).

---

### What this site does today

This page is itself rendered by whichever backend `DASH_BACKEND` points at. The header badge tells you which one — change the env var, restart `run.py`, and the badge updates to match.
