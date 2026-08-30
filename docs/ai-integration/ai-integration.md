---
name: AI/LLM Integration
description: Make your Dash app discoverable to MCP clients, web crawlers, and paste-into-chat users with the dash-improve-my-llms package this site runs.
endpoint: /examples/ai-integration
package: ai-integration
icon: mdi:robot-outline
lastmod: 2026-08-16
category: Network
order: 1
---

.. llms_copy::AI/LLM Integration

.. toc::

### Introduction

This boilerplate ships with [dash-improve-my-llms](https://pypi.org/project/dash-improve-my-llms/) **{{VERSION:dash-improve-my-llms}}** (this page reads the version from the installed package), a small companion package that fills the gaps Dash itself doesn't cover for AI-friendliness.

Since 2.0 the package narrows its scope to the three jobs that are genuinely not addressed by Dash 4.3's native MCP server:

| Audience              | Protocol                        | What it serves                                 |
|-----------------------|---------------------------------|------------------------------------------------|
| MCP clients           | JSON-RPC over Streamable HTTP   | Bridges `LLMS_DOC` → `dash.mcp` resources       |
| Web crawlers          | Plain HTTPS, often no JS        | `/robots.txt`, `/sitemap.xml`, prerender HTML  |
| Paste-into-chat users | One-shot HTTP fetch             | `/llms.txt`, `/<page>/llms.txt` as markdown    |

If you're on Dash 4.3+, MCP clients also get **live** component-tree introspection from Dash itself — `dash-improve-my-llms` no longer duplicates that.

---

### What you get

| Route | Purpose |
|---|---|
| `/llms.txt` | The site index: the home prose, every page, and the network directory |
| `/llms-small.txt` | Compact briefing of the whole site — fits a small context window (2.4.0+) |
| `/llms-full.txt` | The full corpus: every page's prose in one document (2.4.0+) |
| `/<page>/llms.txt` | Per-page narrative documentation (that page's `LLMS_DOC`) |
| `/robots.txt` | Bot policy — generated from your `RobotsConfig` |
| `/sitemap.xml` | SEO sitemap with priority inference, respects `mark_hidden()` |
| `/favicon.ico` + apple-touch paths | 302 to a `configure_seo()` icon, instead of Dash's app shell (2.5.0+) |
| Bot middleware | Training bots → 403, search bots → static HTML, browsers → React app |
| MCP bridge | Each non-hidden page's `LLMS_DOC` registers as a `dash.mcp` resource on Dash 4.3+ |

Every `llms` document content-negotiates: agents and crawlers get raw
Markdown byte-for-byte, a browser gets the same Markdown rendered behind the
network header (`?raw=1` forces the raw side).

**Removed in 2.0** (the package no longer serves these — Dash MCP or your own `LLMS_DOC` covers them):

- `/page.json`, `/<page>/page.json`
- `/architecture.txt`, `/architecture.toon`
- `/llms.toon`, `/<page>/llms.toon`

If your old code linked to any of those endpoints, the fix is to either delete the link or point it at the equivalent `/<page>/llms.txt`.

---

### Quick start — five lines

```python
from dash import Dash
from dash_improve_my_llms import add_llms_routes

app = Dash(__name__, use_pages=True)
add_llms_routes(app)
```

That's it. `add_llms_routes` detects the active backend (**Flask**, **FastAPI**, or **Quart**) and dispatches to the matching adapter — no `if backend == "flask"` gate, no environment variable, no code change.

On Dash 4.3+, it also registers each page's prose as an MCP resource.

---

### The LLMS_DOC pattern

This is the one new idea in 2.0. Each page module exports a module-level string named `LLMS_DOC`. That string is the literal body of `/<page>/llms.txt`. No layout walking, no extraction.

```python
# pages/equipment.py
from dash import html, register_page

register_page(__name__, path="/equipment", name="Equipment Catalog")

LLMS_DOC = """\
# Equipment Catalog

> Browse the equipment library with text search and a category dropdown.

## What this page does

The catalog renders a list of equipment items with name, category, and
status. Two controls filter the list in real time:

- A free-text search input that matches against the item name.
- A category dropdown: All, Tools, Machinery, Vehicles.

## What the user can do

- Type in the search box to narrow by name.
- Switch category to constrain by class.
- Combine both — filters AND together.

## What the page does NOT do

This is a demo. Item list is in-memory. No persistence, no edit/create,
no per-item detail view.
"""

def layout():
    return html.Div([...])
```

#### Where the prose lives

| Where | When to use it |
|---|---|
| Module-level `LLMS_DOC` | Default. Keeps prose next to the layout. |
| `register_page_metadata(path, llms_doc="...")` | When the prose is computed, imported from another file, or generated at runtime. |

The package looks up explicit registration first, then falls back to the module attribute.

#### Recommended structure for a good LLMS_DOC

1. `# Title` — matches the page name.
2. `> One-line tagline` — quoted blockquote at the top.
3. `## What this page does` — narrative description.
4. `## What the user can do` — interactions, in plain prose.
5. `## What the page does NOT do` — guard against the LLM hallucinating capabilities.

Length: 300–2000 words is typical. The package emits a warning naming pages without prose but never truncates.

#### How this boilerplate wires it up

Markdown-driven pages get their prose registered automatically. `pages/markdown.py` reads each `.md` file, expands `.. source::` directives by inlining the referenced file, then calls `register_page_metadata(path, llms_doc=expanded_markdown)`. That's why `/getting-started/llms.txt` returns the full page content with code samples already inlined — exactly what a paste-into-chat user wants.

The home page uses the simpler pattern: `pages/home.py` exports `LLMS_DOC = content` where `content` is the markdown body of `pages/home.md`.

---

### Multi-backend support

```bash
# 2.5.1 is the 2plot network floor — this repo's requirements.txt pins it.
# The package itself requires dash>=4.1 (there is no Dash 3.x support).
pip install "dash-improve-my-llms[flask]>=2.5.1"      # Dash's default backend
pip install "dash-improve-my-llms[fastapi]>=2.5.1"    # Dash 4.1+ FastAPI
pip install "dash-improve-my-llms[quart]>=2.5.1"      # Dash 4.1+ Quart
pip install "dash-improve-my-llms[all]>=2.5.1"        # all three
```

`add_llms_routes(app)` inspects `app.server` (via `dash.backends.get_server_type` on Dash 4.2+, falling back to `type(app.server).__name__`) and dispatches to the matching adapter. `GET /robots.txt` returns byte-identical content whether the app is Flask, FastAPI, or Quart.

The handlers live in `dash_improve_my_llms/handlers.py` as **pure functions**. Each adapter is a thin I/O wrapper, so behavior across backends is identical by construction.

---

### Bot management

```python
from dash_improve_my_llms import RobotsConfig

# Balanced (default-ish) — block training, allow citations
app._robots_config = RobotsConfig(
    block_ai_training=True,      # GPTBot, CCBot, anthropic-ai, Google-Extended
    allow_ai_search=True,        # ChatGPT-User, ClaudeBot, PerplexityBot
    allow_traditional=True,      # Googlebot, Bingbot, DuckDuckBot
    crawl_delay=10,
    disallowed_paths=["/admin", "/api/*"],
)
```

The bot middleware:

1. Training bot + `block_ai_training=True` → **403 Forbidden**.
2. Search or traditional bot → **prerendered static HTML** built from the page's `LLMS_DOC` (so they actually see content instead of an empty React shell).
3. Real browser → passes through to the Dash app.

Verify with `curl`:

```bash
# Training bot — expect 403 when block_ai_training=True
curl -A "Mozilla/5.0 (compatible; GPTBot/1.0)" http://localhost:8559/

# Search bot — expect static HTML with the LLMS_DOC content baked in
curl -A "Mozilla/5.0 (compatible; Googlebot/2.1)" http://localhost:8559/

# Real browser — passes through to Dash
curl -A "Mozilla/5.0 (Macintosh)" http://localhost:8559/ | head -20
```

---

### Hiding pages from crawlers and MCP

```python
from dash_improve_my_llms import mark_hidden

mark_hidden("/admin")
mark_hidden("/internal/metrics")
```

Effects: excluded from `/sitemap.xml`, added to `/robots.txt` Disallow list, returns 404 to crawler requests, returns 404 to `/admin/llms.txt`, and skipped when registering MCP resources.

There is **no component-level hiding** in 2.0. To hide content from extraction, simply don't write it into the page's `LLMS_DOC`.

---

### MCP integration

On Dash 4.3+, every non-hidden page's `LLMS_DOC` is registered as a `dash.mcp` resource:

- **URI**: `llms:///<page-path>` (e.g. `llms:///equipment`, `llms:///` for root)
- **mimeType**: `text/markdown`
- **content**: the `LLMS_DOC` string

This means an MCP-aware client can fetch the prose docs through its existing tool-call surface without an extra HTTP fetch. To opt out:

```python
from dash_improve_my_llms import LLMSConfig, add_llms_routes
add_llms_routes(app, LLMSConfig(register_mcp_resources=False))
```

On Dash 3.x or 4.1/4.2 the MCP bridge silently no-ops — the HTTP routes still work.

---

### Migration notes (1.x → 2.0)

If you upgraded an existing app:

1. **Install the right extra** — `pip install "dash-improve-my-llms[flask]>=2.5.1"` (or `[fastapi]`, `[quart]`).
2. **Add `LLMS_DOC` to each page module.** The startup `UserWarning` names every page that's missing prose.
3. **Remove `mark_important()` and `mark_component_hidden()` calls.** They're deprecation no-ops in 2.0 and will be deleted in 2.1.
4. **Remove links to dropped routes** — `/page.json`, `/architecture.txt`, `/architecture.toon`, `/llms.toon` (and per-page variants).
5. **Stop using `TOONConfig`, `PageType`, `generate_*_toon`, `toon_encode`, `extract_*`** — all removed from the public API.

The HTTP surfaces that survived (`/llms.txt`, `/robots.txt`, `/sitemap.xml`) and the APIs `RobotsConfig`, `mark_hidden`, `register_page_metadata` are byte-compatible with 1.x.

---

### Debugging

```bash
# Confirm routes are wired
curl -s http://localhost:8559/llms.txt | head -5
curl -s http://localhost:8559/robots.txt | head -10
curl -s http://localhost:8559/sitemap.xml | head -10

# See which pages are missing prose: just boot the app and read the UserWarning.
python run.py 2>&1 | grep -i "llms_doc"
```

```python
# Inspect backend detection
from dash_improve_my_llms import _detect_backend
print(_detect_backend(app))   # "flask" | "fastapi" | "quart"
```

```python
# Pure-function trace of a crawler request — no server needed
from dash_improve_my_llms.handlers import handle_bot_request

result = handle_bot_request(
    path="/",
    user_agent="Mozilla/5.0 (compatible; GPTBot/1.0)",
    app=app,
    page_metadata={},
    hidden_paths=set(),
)
```

---

### Why the surface shrank

Earlier releases generated `/page.json`, `/architecture.txt`, `/llms.toon`, and tried to extract prose from Dash component trees. Two things changed:

1. **Dash 4.3 shipped MCP.** A live, structurally-accurate description of the component tree is available natively through Streamable HTTP. Reading it from a boot-time snapshot is strictly worse.
2. **Layout extraction was never reliable.** Walking `dcc.Markdown` children and guessing what was important led to surprising outputs. The `LLMS_DOC` pattern moves the responsibility to you — write the prose, the package serves it.

The result is ~4,400 → ~1,900 lines of public surface, fewer endpoints to remember, and no quiet "the extraction missed my best paragraph" failures.

---

### Where to read more

- [`SKILLS.md`](https://github.com/pip-install-python/dash-improve-my-llms/blob/main/docs/SKILLS.md) — the practical guide bundled with the package.
- [`CHANGELOG.md`](https://github.com/pip-install-python/dash-improve-my-llms/blob/main/CHANGELOG.md) — full 2.0 breaking-changes list.
- [PyPI: dash-improve-my-llms](https://pypi.org/project/dash-improve-my-llms/) — install + latest version.
- [llms.txt spec](https://llmstxt.org/) — the convention the package implements.
