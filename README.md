# Dash Documentation Boilerplate — the 2plot network's template

<p align="center">
  <img src="https://cdn.2plot.ai/github_assets/dark_mode_2plot.png" alt="2plot" width="640">
</p>

> `dash-documentation-boilerplate` — the markdown-driven documentation template every `*.2plot.dev` component site is forked from. By [Pip Install Python](https://2plot.dev).

<!-- One badge for both: cd.yml's first job `uses:` ci.yml, so this status IS
     the full CI matrix plus the deploy — the deploy cannot start unless CI
     passed. A standalone ci.yml badge would be frozen forever on the last
     pre-1.2.2 run: ci.yml deliberately has no push trigger on main (see the
     comment at the top of that file), and reusable-workflow calls count as
     runs of the CALLER, so ci.yml never gets a new run on main again. -->
[![CI/CD](https://github.com/pip-install-python/Dash-Documentation-Boilerplate/actions/workflows/cd.yml/badge.svg)](https://github.com/pip-install-python/Dash-Documentation-Boilerplate/actions/workflows/cd.yml)
[![Dash](https://img.shields.io/badge/Dash-4.4.1-blue.svg)](https://dash.plotly.com/)
[![DMC](https://img.shields.io/badge/DMC-2.7.0-teal.svg)](https://www.dash-mantine-components.com/)
[![Backends](https://img.shields.io/badge/Backends-Flask%20%7C%20FastAPI%20%7C%20Quart-orange.svg)](https://dash.plotly.com/)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Live:** [boilerplate.2plot.dev](https://boilerplate.2plot.dev) · the template every
[2plot.dev](https://2plot.dev) component documentation site is built from.


A comprehensive boilerplate for creating beautiful, interactive documentation for your Dash components, data science workflows, and applications. Features markdown-driven content, live code examples, and automatic theme persistence.

![Documentation Preview](assets/intro_img.jpg)

---

## ✨ Features

### 📝 Markdown-Driven Documentation
- Write documentation in Markdown with Python integration
- Custom directives for interactive examples, code highlighting, and component props
- Automatic page generation from markdown files with frontmatter metadata
- Table of contents generation for easy navigation

### 🎨 Modern UI/UX
- Built with [Dash Mantine Components](https://www.dash-mantine-components.com/)
- Responsive design for mobile, tablet, and desktop — the mobile burger
  opens a solid, full-height drawer docked under the header, with a
  sticky page-search on top (the network-standard mobile navigation;
  needs dash-mantine-components ≥ 2.8.0)
- Dark and light theme support with **automatic preference persistence**
- Icon-only controls carry `aria-label`s — screen readers and AI agents
  can name every button (Lighthouse Agentic-Browsing 3/3)
- Smooth transitions and professional styling
- Customizable color schemes and theming

### 🔐 Access Control & Live Page Management
- Four page tiers (`public` / `auth` / `admin` / `hidden`) declared in
  frontmatter, defaulted by `PAGE_DEFAULT_TIER`
- **`/admin/control-board`** — flip any page's tier or its llms.txt
  exposure live, no restart; overrides beat frontmatter and persist to
  `PAGE_VISIBILITY_FILE` on a mounted disk. Owner/admin-gated via
  `ADMIN_EMAILS` / `ADMIN_USER_IDS`; fails closed without Clerk
  (`ALLOW_UNGATED_ADMIN=1` for local work)
- Sign-in gate cards with an optional **live demo teaser**
  (`lib/auth_demos.py`) — anonymous visitors see a working example above
  the "create a free account" card
- Optional Clerk authentication (vendored `dash-clerk-auth`), fully
  inert until the `CLERK_*` env vars exist — a fork inherits the
  capability, never a login wall

### 🔍 Developer Experience
- Hot reload during development
- Searchable component navigation
- Syntax highlighting for multiple languages
- Interactive code examples with live callbacks
- Component props documentation auto-generation

### 🤖 AI/LLM & SEO Integration
- **`LLMS_DOC` pattern** — write a module-level prose string per page; served verbatim at `/<page>/llms.txt`
- **Multi-backend** — `add_llms_routes(app)` auto-detects Flask, FastAPI, or Quart and dispatches to the matching adapter
- **MCP bridge** — each page's prose registers as a `dash.mcp` resource on Dash 4.3+ (silent no-op otherwise)
- **SEO** — `sitemap.xml` with intelligent priority inference; respects `mark_hidden()`
- **Bot management** — training crawlers blocked (configurable), AI search citations allowed, browsers untouched
- **Privacy controls** — `mark_hidden()` to exclude pages from sitemap, robots, MCP, and crawler prerender
- **Share with AI** — paste the app URL into ChatGPT/Claude/etc.; they fetch the prose docs directly
- **Cross-host network directory** — `lib/network_directory.py` publishes the sibling sites so an agent landing on one satellite can find the rest ([docs](https://boilerplate.2plot.dev/networks))
- Powered by [dash-improve-my-llms](https://pypi.org/project/dash-improve-my-llms/) — the floor is pinned in `requirements.txt` (2.6.0, the 2plot network standard — truthful sitemap `<lastmod>`, icon autodiscovery, JSON-LD publisher logo); served pages read the version from the installed package rather than hardcoding it

### 🔌 Pluggable Backends (Dash 4.x)
- Run the **same app** on **Flask**, **FastAPI**, or **Quart** — switch with a single `DASH_BACKEND` environment variable
- Backend selection centralized in [`lib/backend.py`](lib/backend.py); a live badge shows which backend is serving the page
- FastAPI/Quart (ASGI) unlock async callbacks, websocket callbacks, OpenAPI docs, a native JSON API (`/api/backend`, `/api/pages`, `/healthz`), and ASGI middleware
- Dedicated docs: **Pluggable Backends**, **Backend Deep Dive**, and a **FastAPI Showcase**

### 🐋 Production Ready
- Docker and docker-compose support
- Gunicorn (WSGI) and Uvicorn (ASGI) production servers
- Optimized for deployment
- Environment-based configuration

### 🚀 Built With Latest Technologies
- **Dash 4.2.0** - Modern Plotly Dash framework with pluggable backends
- **DMC 2.7.0** - Dash Mantine Components
- **Mantine 8.3.6** - Beautiful React UI library
- **React 18** - Latest React features
- **Python 3.12+** - Modern Python

---

## 📋 Requirements

### System Requirements
- **Python**: 3.12 or higher (3.14 is the fleet Python — the Docker image, the CI matrix main and render.yaml all encode it, and `tests/test_python_version.py` holds them to one minor)
- **Node.js**: 14+ (for npm dependencies)
- **npm**: 6+

### Python Dependencies
- dash `~=4.4.1` — see the support matrix below; **not 4.3.0**
- dash-mantine-components >= 2.7.0
- dash-ag-grid
- dash-improve-my-llms >= 2.6.0 (the 2plot network standard — see below)
- flask >= 3.0.0 (default backend)
- plotly >= 5.0.0
- pandas >= 1.2.3
- pydantic >= 2.3.0
- python-frontmatter >= 1.0.0
- markdown2dash (installed `--no-deps` — see below)
- gunicorn >= 23.0.0 (WSGI production server; 21.x carried two request-smuggling CVEs)

**Optional backends** (install the matching extra to switch off Flask):
```bash
pip install "dash[fastapi]"   # FastAPI (ASGI) backend
pip install "dash[quart]"     # Quart (ASGI) backend
# then run with: DASH_BACKEND=fastapi python run.py  (needs uvicorn)
```

See [`requirements.txt`](requirements.txt) for the complete list.

#### Dash support matrix

Verified against real apps on each backend, with the failure reproduced on a
stock Dash app with `dash-improve-my-llms` uninstalled:

| Dash | Flask | FastAPI | Quart |
|---|---|---|---|
| 4.1.0 | ✅ | — no pluggable backends | — |
| 4.2.0 | ✅ | ✅ | ✅ |
| **4.3.0** | ✅ | ❌ **every non-root page 500s** | ✅ |
| 4.4.0 | ✅ | ✅ | ✅ |
| 4.4.1 | ✅ | ✅ | ✅ |

4.3.0 added an early-return path guard to the ASGI middleware that returns
*before* `set_current_request`, while the page catch-all still calls
`get_current_request()` — so it raises `RuntimeError: No active request in
context`. The catch-all is byte-identical between 4.2.0 and 4.3.0; only the
middleware changed. 4.4.0 fixed it by setting the context inside the catch-all
too.

That distinction matters for the pin: 4.2.0 works only because a single
upstream code path happens to cover it, whereas 4.4.x sets the context in both
places, so a future middleware guard can't reintroduce the bug. **4.4.x isn't
just currently-passing, it's structurally safer.**

`~=4.4.1` lets 4.4.2 patches flow without twenty pull requests but blocks
4.5.0, so a minor bump goes through the matrix deliberately. The pin is for the
most constrained backend **network-wide, including Flask-only apps** —
`DASH_BACKEND` is an environment variable and this repo is a shared template,
so a Flask deployment becomes a FastAPI deployment with one env change and no
code change.

> **Note on `dash-improve-my-llms`.** The floor is **2.6.0** — 2.5.1's Tier-B SEO standard plus the honesty layer: sitemap `<lastmod>` emitted verbatim from declarations and omitted when unset (older packages silently swallow the date and the sitemap goes back to lying), icon autodiscovery, JSON-LD publisher.logo. Below that, the Tier-B SEO
> standard: `configure_seo` (icons, social card, publisher/sameAs), the
> crawler `<title>` carrying the site name, per-page `title`/`image_url`/
> `schema_type` reaching the crawler document, `/favicon.ico` answered with a
> redirect instead of the app shell, and a prerender that never clobbers the
> app's own per-page `<title>`. Earlier floors still matter historically:
> 2.3.4 is what resolves this site's published identity (`resolve_site_title`
> skips generic candidates like `Home` and Dash's default `Dash` — before it,
> this host's viewer chip read a bare "Dash"). There is no vendored copy of
> the package any more; `vendor/` holds `dash_clerk_auth` alone. See
> [Network Standard](docs/network-standard/network-standard.md).

> **Note on `markdown2dash`.** Version 0.1.2 declares `gunicorn>=21.2.0,<22.0.0`
> — a markdown parser pinning a WSGI server, and directly against the
> CVE-driven `gunicorn>=23` floor. pip cannot resolve both, so it is installed
> without its dependency graph. Its real dependencies (`docutils`, `jsonpath`,
> `mistune`) are listed in `requirements.txt` instead. Every install path does
> the same two commands:
>
> ```bash
> pip install -r requirements.txt
> pip install --no-deps markdown2dash==0.1.2
> ```

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/pip-install-python/Dash-Documentation-Boilerplate.git
cd Dash-Documentation-Boilerplate
```

### 2. Install Dependencies

**Python packages:**
```bash
pip install -r requirements.txt
pip install --no-deps markdown2dash==0.1.2   # see the note above
```

**Node packages** (for DMC frontend components):
```bash
npm install
```

### 3. Run the Development Server

```bash
./scripts/dev.sh              # backend from .env (default flask)
./scripts/dev.sh fastapi      # override for one run
```

Visit **http://localhost:8559** in your browser.

`scripts/dev.sh` resolves the interpreter from its own location, so it always
uses this project's `.venv`. `python run.py` works too — but an IDE run
configuration pointing at *another project's* virtualenv starts the app
against that project's dependency versions, which is silent and expensive:
on `dash-improve-my-llms` 2.0.0 there is no viewer module at all, so
`/<page>/llms.txt` serves plain Markdown to everyone and nothing looks broken.
The app now refuses to boot below the pinned floors and prints
`sys.executable`, but the launcher avoids the question entirely.

### 4. Start Documenting!

Create your documentation in the `docs` folder:

```bash
docs/
├── your-component/
│   ├── your-component.md     # Markdown documentation
│   └── examples.py           # Python code examples (optional)
```

---

## 📁 Project Structure

```
dash-documentation-boilerplate/
├── assets/                      # Static assets and CSS
│   ├── m2d.css                 # Markdown-to-Dash styling (theme-aware)
│   ├── main.css                # Custom styles (theme-aware)
│   └── llms_copy.js            # "Copy for LLM" button handler
│
├── components/                  # Reusable UI components
│   ├── appshell.py             # Main app layout with MantineProvider
│   ├── header.py               # Header with search and theme toggle
│   ├── navbar.py               # Navigation sidebar and drawer
│   └── backend_badge.py        # Badge showing the active backend
│
├── docs/                        # Documentation content
│   ├── example/                # Getting Started guide
│   ├── directives/             # Custom Directives guide
│   ├── interactive-components/ # Callback patterns guide
│   ├── data-visualization/     # Theme-aware charts guide
│   ├── ai-integration/         # AI/LLM integration (dash-improve-my-llms 2.2)
│   ├── networks/               # Multi-site network wiring for satellites
│   ├── backends/               # Pluggable Backends guide
│   ├── backend-comparison/     # Flask vs FastAPI vs Quart deep dive
│   └── fastapi-showcase/       # What the FastAPI backend unlocks
│
├── lib/                         # Utility libraries
│   ├── constants.py            # BASE_URL + guard, APP_VERSION, colors
│   ├── network_directory.py    # Cross-host directory shared by every satellite
│   ├── backend.py              # Backend selection (DASH_BACKEND)
│   ├── asgi_middleware.py      # ASGI middleware (FastAPI/Quart)
│   ├── asgi_routes.py          # Showcase routes (/healthz, /api/*)
│   ├── analytics_tracker.py    # Lightweight visitor analytics
│   └── directives/             # Custom markdown directives
│       ├── kwargs.py           # Component props table generator
│       ├── source.py           # Source code display directive
│       ├── toc.py              # Table of contents directive
│       ├── headings.py         # Heading ids that survive inline formatting
│       └── llms_copy.py        # "Copy for LLM" button directive
│
├── pages/                       # Dash multi-page app pages
│   ├── home.md                 # Home page content
│   ├── home.py                 # Home page layout (exports LLMS_DOC)
│   └── markdown.py             # Dynamic markdown page loader
│
├── scripts/
│   └── smoke_live.py           # Post-deploy checks against a live site
│
├── tests/                       # pytest suite (runs on all three backends)
│   ├── conftest.py             # Boots run.py once; one client per backend
│   ├── test_pages.py           # Every page loads and serves real content
│   ├── test_llms_routes.py     # llms.txt, sitemap, robots, canonicals
│   ├── test_network_directory.py
│   ├── test_docs_content.py    # Frontmatter, directives, heading anchors
│   ├── test_config.py          # BASE_URL guard, index.html metadata
│   ├── test_internal_traffic.py # The analytics contract, both directions
│   ├── test_network_smoke.py   # The battery, run against this app
│   ├── test_site_identity.py   # One brand, every surface
│   └── test_smoke_live.py      # The CD script, run against this app
│
├── templates/
│   └── index.html              # SEO-optimized HTML template
│
├── vendor/                      # dash-clerk-auth sdist (not on PyPI)
│
├── .github/
│   ├── dependabot.yml          # dash-network update group
│   └── workflows/
│       ├── ci.yml              # Lint, matrix, image build + boot + battery
│       └── cd.yml              # Render deploy + live verification
│
├── .flake8
├── .gitignore
├── CHANGELOG.md                # Version history and changes
├── Dockerfile                  # Docker container definition
├── docker-compose.yml          # Docker compose configuration
├── package.json                # Node.js dependencies
├── package-lock.json           # Locked npm versions
├── pytest.ini
├── README.md                   # This file
├── render.yaml                 # Render Blueprint for boilerplate.2plot.dev
├── requirements.txt            # Python dependencies
└── run.py                      # Application entry point
```

---

## 📖 Usage Guide

### Creating Documentation Pages

1. **Create a new folder** in the `docs/` directory:
   ```bash
   mkdir -p docs/my-component
   ```

2. **Create a markdown file** with frontmatter:
   ```markdown
   ---
   name: My Component
   description: A description of my component
   endpoint: /components/my-component
   icon: mdi:code-tags
   ---

   ## My Component

   Your documentation content here...
   ```

3. **Add interactive examples** (optional):
   ```python
   # docs/my-component/example.py
   import dash_mantine_components as dmc

   component = dmc.Button("Click Me!", id="my-button")
   ```

4. **Use directives** in your markdown:
   ```markdown
   .. toc::

   .. exec::docs.my-component.example

   .. source::docs/my-component/example.py
   ```

### Custom Markdown Directives

#### `.. toc::`
Generates a table of contents from your markdown headings.

#### `.. exec::module.path.to.component`
Renders an executable Python component from a module.

#### `.. source::path/to/file.py`
Displays source code with syntax highlighting.

#### `.. kwargs::ComponentName`
Generates a props documentation table for a component.

#### `.. llms_copy::Page Title`
Adds a "Copy for LLM" button that copies the page's `/<page>/llms.txt` URL to the clipboard for sharing with ChatGPT, Claude, and other AI assistants.

### Customizing Themes

Modify `lib/constants.py` to change the primary color:

```python
PRIMARY_COLOR = "teal"  # Change to any Mantine color
```

Customize CSS in:
- `assets/main.css` - General styling
- `assets/m2d.css` - Markdown-specific styling

### Theme Persistence

The boilerplate automatically saves user theme preference (light/dark) in localStorage:
- First visit: Detects browser preference or defaults to light
- Theme toggle: Saves preference automatically
- Return visits: Restores saved theme preference

---

## ✅ Testing

The suite boots `run.py` itself rather than a test app assembled for the
occasion — almost everything worth catching here lives in the wiring
(registration order, which middleware runs first, whether a page's prose
survived to the response), and a test app that re-implements the wiring only
tests the re-implementation.

```bash
pip install pytest
pytest                       # whichever backend DASH_BACKEND / .env selects

DASH_BACKEND=flask pytest    # the three backends, one at a time
DASH_BACKEND=fastapi pytest
DASH_BACKEND=quart pytest

flake8 lib components pages tests run.py
```

What it covers, and why each one is there:

| Area | The failure it catches |
|---|---|
| Page registration & reachability | A markdown file that silently stops registering — invisible to any test that iterates whatever *did* register |
| Crawler bodies | A page serving the JavaScript stub. This is the regression that cost the network 12 of 14 crawlable URLs |
| Rendered prose | Links, tables, code fences and rules coming through as literal text instead of HTML |
| Canonical tags | Exactly one per page, on **this** host. A wrong one deindexes the site and looks like nothing is wrong |
| sitemap / robots / llms.txt | Missing pages, foreign hosts, a sitemap line pointing elsewhere |
| Network directory | Self-listed peers, duplicate or overlapping tiers, entries missing from the published output |
| Docs content | Broken `.. exec::` / `.. source::` targets, duplicate endpoints, incomplete frontmatter |
| Heading anchors | A TOC link whose target id doesn't exist — clicking it does nothing, silently |
| `BASE_URL` guard | A fork deploying with the boilerplate's own canonical host |
| `scripts/smoke_live.py` | The CD script itself, run against the in-process app, so a typo can't turn every live check into a silent pass |

### CI

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs on every push and
pull request:

- **lint** — flake8, blocking
- **test** — the full suite on Flask, FastAPI and Quart (Python 3.14), plus
  Python 3.12 and 3.13 on Flask. Asserts the installed Dash is ≥ 4.4 and
  `dash-improve-my-llms` is ≥ 2.1 before running anything
- **boot under gunicorn** — a page can render under a test client and still
  fail under a real WSGI worker
- **docker** — builds the image, boots it, and probes the live routes

---

## 🚀 Deployment

### Render (how boilerplate.2plot.dev is hosted)

[`render.yaml`](render.yaml) is the Blueprint for the live deployment:
gunicorn with two workers, `/healthz` as the health check, a persistent disk
for the analytics ledger, and the custom domain attached.

```bash
render blueprint launch        # or point a new Render service at this repo
```

**The one environment variable you must set** is `APP_BASE_URL`. It drives
`<link rel="canonical">`, `sitemap.xml`, and the absolute URLs in `llms.txt`.
A fork that leaves it unset inherits `https://boilerplate.2plot.dev` and tells
Google that every one of its pages is a duplicate of this one — traffic
disappears and nothing in the app looks broken. `lib/constants.py` refuses to
boot on Render without it, and rejects `*.onrender.com` values too, because
those keep resolving after a custom domain is attached and quietly split link
equity across two hosts.

```env
APP_BASE_URL=https://yoursite.2plot.dev   # required in production
DASH_BACKEND=flask                        # flask | fastapi | quart
CROSS_APP_WEBHOOK_SECRET=...              # optional: network analytics
TRAFFIC_ANALYTICS_FILE=/var/data/visitor_analytics.json
```

### CD

[`.github/workflows/cd.yml`](.github/workflows/cd.yml) runs CI, POSTs to the
Render deploy hook in the `RENDER_DEPLOY_HOOK_URL` secret, waits for the new
instance to be reliably healthy, and then verifies the **live** site with
[`scripts/smoke_live.py`](scripts/smoke_live.py).

Without that secret the deploy step skips itself and the workflow still
verifies whatever is currently live — so a fork doesn't fail CD on day one
over a secret it was never given.

You can run the same checks by hand against any satellite:

```bash
python scripts/smoke_live.py https://emojimart.2plot.dev
```

It checks the four things that are silent in production: a canonical on the
wrong host, a page serving the JavaScript stub, a missing network directory,
and dead peer `llms.txt` links.

### Docker

```bash
docker build -t dash-docs-boilerplate .
docker run -p 8550:8550 dash-docs-boilerplate     # http://localhost:8550
docker-compose up
```

The image serves with **gunicorn** and declares a `HEALTHCHECK` against
`/healthz`. Note that `vendor/` is copied in *before* the pip layer — while
`dash-improve-my-llms` installs from the sdist, the build fails without it.

---

## 🛰️ Forking this into a satellite site

This repo is the template the `*.2plot.dev` documentation sites are built
from, so changes here propagate. Four things to change when you fork it:

1. **`APP_BASE_URL`** in your host's environment, and `DEFAULT_BASE_URL` in
   [`lib/constants.py`](lib/constants.py). See above for why this one matters
   more than everything else combined.
2. **[`lib/network_directory.py`](lib/network_directory.py)** — keep it
   identical across every satellite. Twelve hand-maintained peer lists will
   drift, and a directory that disagrees with itself across hosts is worse
   than no directory. Only list hosts that are actually live.
3. **[`templates/index.html`](templates/index.html)** — title, description,
   Open Graph card, and the Schema.org blocks.
4. **`docs/`** — replace the example pages with your component's.

Leave `warn_missing_llms_doc=True` on. It names every page with no prose,
which is exactly the list of pages serving a stub to crawlers. Turning it off
hides the to-do list rather than shortening it. The full guide is at
[boilerplate.2plot.dev/networks](https://boilerplate.2plot.dev/networks).

---

## 🛠️ Development

### Setting Up Development Environment

1. **Create virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install --no-deps markdown2dash==0.1.2
   npm install
   ```

3. **Run in debug mode**:
   ```python
   # Modify run.py
   app.run(debug=True, host='0.0.0.0', port='8553')
   ```

### Adding New Components

1. Create your component in a separate module
2. Add documentation in `docs/your-component/`
3. The app automatically discovers and registers pages from markdown files
4. Restart the server to see your new documentation

### Modifying the Layout

Main layout components:
- **Header**: `components/header.py` - Logo, search, theme toggle
- **Navbar**: `components/navbar.py` - Sidebar navigation
- **AppShell**: `components/appshell.py` - Overall layout structure

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file (optional):

```env
DASH_DEBUG=False
DASH_HOST=0.0.0.0
DASH_PORT=8553
DASH_BACKEND=flask     # flask | fastapi | quart (requires the matching dash extra)

# Access control (all optional — see docs/authentication)
PAGE_DEFAULT_TIER=public          # the per-host gate switch
ADMIN_EMAILS=you@example.com      # control-board / admin-tier allowlist
ADMIN_USER_IDS=                   # Clerk user ids, same allowlist
ALLOW_UNGATED_ADMIN=0             # 1 ONLY on a local box: opens /admin/control-board without Clerk
PAGE_VISIBILITY_FILE=/var/data/page_visibility.json   # board overrides; must be a mounted disk in prod
```

### Network analytics (2plot.ai)

When deployed as a satellite of the 2plot network, this app reports its own
traffic to the hub so the owner-only `/traffic` dashboard can chart it. Two
signals, both hourly:

| Signal | How |
|--------|-----|
| **Health** | The hub probes `/healthz` (served on every backend) and records up/down + latency. |
| **Traffic** | `lib/satellite_reporter` POSTs a signed daily rollup to `https://2plot.ai/api/satellite/traffic`. |

```env
CROSS_APP_WEBHOOK_SECRET=...   # shared HMAC secret — without it, reporting is off
SATELLITE_APP_KEY=dev          # this app's key in the hub network directory
                               # (falls back to AD_APP_ID, then "dev")

# Optional
SATELLITE_TRAFFIC_URL=https://2plot.ai/api/satellite/traffic
SATELLITE_REPORT_INTERVAL_S=3600
ANALYTICS_GEO_LOOKUP=1         # 0 to skip ip-api.com (unnecessary behind Cloudflare)
ANALYTICS_RETENTION_DAYS=45    # local ledger retention; the hub keeps the history
```

Reporting is **off by default** — no secret, no POSTs, and the app logs that it
is disabled. Check what would be sent without sending it:

```bash
python -m lib.satellite_reporter --dry-run
```

The numbers (`visitors`, `sessions`, `median_session_s`, top pages, countries)
are computed in `lib/traffic_rollup.py` using the hub's own definitions — a
visitor is an `(IP, user-agent)` pair, a session breaks on a 30-minute gap, and
the median session length counts multi-page sessions only, so single pageviews
are never padded in. Behind a proxy or CDN, the tracker reads
`CF-Connecting-IP` / `X-Forwarded-For` for the client address and
`CF-IPCountry` for the country; without that, every visitor would look like the
proxy.

> **Deployment note — give the ledger a persistent disk.** The hub takes the
> *last* report for a given `(app, date)`. On an ephemeral filesystem (a plain
> Render/Heroku instance) a mid-day deploy wipes `visitor_analytics.json`, and
> the next hourly report overwrites today's correct total with the handful of
> hits collected since the restart. Mount a disk and point
> `TRAFFIC_ANALYTICS_FILE` at it (e.g. `/var/data/visitor_analytics.json`) so a
> deploy doesn't cost you a day of numbers.

### Customization Points

| File | Purpose |
|------|---------|
| `lib/constants.py` | App-wide constants (colors, titles) |
| `assets/main.css` | Custom CSS styles |
| `templates/index.html` | HTML template (for analytics, meta tags) |
| `components/appshell.py` | Theme configuration, MantineProvider settings |

---

## 📚 Documentation

### User Documentation
- **Getting Started**: This README
- **Changelog**: See [CHANGELOG.md](CHANGELOG.md)
- **Examples**: Check the `/docs/example/` folder

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Test thoroughly**: Ensure the app runs without errors
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guide for Python code
- Add docstrings to functions and classes
- Test your changes before submitting
- Update documentation if adding new features
- Keep commits atomic and well-described

---

## 🐛 Known Issues & Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'dash_html_components'`
- **Solution**: You're on an old version. Update to 1.0.0+ and import from the main package (`from dash import html, dcc`); 1.0.0 runs on Dash 4.x.

**Issue**: `DASH_BACKEND=fastapi` (or `quart`) fails to start
- **Solution**: Install the matching extra — `pip install "dash[fastapi]"` (or `[quart]`) — and serve with an ASGI server (`uvicorn`). The app falls back to Flask if the backend is unavailable.

**Issue**: Theme doesn't persist
- **Solution**: Check browser localStorage is enabled and not blocked

**Issue**: npm install fails
- **Solution**: Update Node.js to 14+ and npm to 6+

**Issue**: Port already in use
- **Solution**: Change port in `run.py` or stop the conflicting process

**Issue**: `RuntimeError: APP_BASE_URL is not set` on Render
- **Solution**: Working as intended. Set `APP_BASE_URL` to this deployment's real origin. Without it the app would serve the boilerplate's canonical host on every page.

**Issue**: `pip install -r requirements.txt` fails with a `gunicorn` resolution conflict
- **Solution**: `markdown2dash` 0.1.2 pins `gunicorn<22` against this project's `gunicorn>=23` floor. Install it separately: `pip install --no-deps markdown2dash==0.1.2`.

**Issue**: the llms.txt viewer's brand chip says "Dash", or `/llms.txt` opens with the wrong `# ` line
- **Solution**: You are on a pre-2.3.4 `dash-improve-my-llms`, or `SITE_BRAND` is unset. `pip install -U "dash-improve-my-llms[flask]>=2.6.0"` (the current network floor) and see [Network Standard](docs/network-standard/network-standard.md).

**Issue**: the Docker container exits at boot with `Could not import dash.backends._fastapi`
- **Solution**: A local `.env` was copied into the image. `.dockerignore` excludes it; make sure you have not removed that line.

**Issue**: Every non-root URL 500s with `No active request in context`
- **Solution**: You're on Dash 4.3.0 with the FastAPI backend. Upgrade to 4.4.0+; `requirements.txt` already floors it there.

For more issues, check [GitHub Issues](https://github.com/pip-install-python/Dash-Documentation-Boilerplate/issues)

---

## 📊 Version Information

**Current Version**: 1.2.4

| Component | Version |
|-----------|---------|
| Dash | 4.4.0+ (4.3.0 excluded — broken FastAPI backend) |
| Dash Mantine Components | 2.7.0+ |
| Mantine | 8.3.6 |
| Python | 3.12+ |
| React | 18.2.0 |
| Flask / FastAPI / Quart | pluggable backends |
| dash-improve-my-llms | 2.6.0+ |

See [CHANGELOG.md](CHANGELOG.md) for version history.

### What's New in 1.2.0

The 2plot network standard, landed on this template so every satellite can copy it. See [Network Standard](https://boilerplate.2plot.dev/network-standard).

- 🪪 **Explicit site identity** (`lib/constants.SITE_BRAND`) on `Dash(title=)`, `register_page_metadata(path="/")`, `pages/home.md` and `templates/index.html`. Before this, `/llms.txt`'s viewer chip published Dash's default title — a bare **"Dash"** — as the name of this site.
- 📈 **The internal-traffic contract**: network machinery is counted nowhere. Token-carrying requests are dropped at write time *before* bot classification, `/healthz` is no longer stored, and every outbound call to another network host now sends `INTERNAL_UA`. The ad client had been fetching a campaign from 2plot.dev on every page view as `python-requests` — this satellite's readers were being charted as bots on the hub.
- 🧪 **CI on the network baseline**: least-privilege `permissions`, per-job `timeout-minutes`, a buildx GHA cache, version fingerprints asserted *inside* the image, a secretless pytest suite, `scripts/network_smoke.py` run in three seats (container, production, in-process), Dependabot with a `dash-network` group, and an advisory `pip-audit`.
- 🔒 **gunicorn >= 23.0.0** (was 21.2.0, which carried CVE-2024-6827 and CVE-2024-1135). `markdown2dash`'s spurious `gunicorn<22` pin is dodged with a `--no-deps` install.
- 📦 **dash-improve-my-llms >= 2.3.4**.
- 🐋 **`.dockerignore`** — a local `.env` was being copied into the production image, which killed the container at boot on the first local run of the new battery. Secrets and dev config no longer reach an image layer.

### What's New in 1.1.0

- 🧪 **CI/CD**: a pytest suite that boots the real app on all three backends, flake8, a Docker build, and a CD workflow that deploys to Render and then verifies the live site.
- 🛰️ **Cross-host network directory** (`lib/network_directory.py`) plus a [Multi-Site Networks](https://boilerplate.2plot.dev/networks) guide for satellite authors.
- 🔒 **`APP_BASE_URL` guard**: production boots fail rather than silently serving another site's canonical host.
- 🎯 **dash-improve-my-llms 2.2**: merge semantics for page metadata, universal prerender, a Markdown renderer that emits real anchors, tables and code fences, a navigation block so a page's `llms.txt` is no longer a dead end, and content negotiation on that URL — Markdown for agents, a rendered view with the network wordmark for browsers.
- 🐛 **Fixes**: duplicate canonical tags on every page; a heading containing inline code crashing the renderer at startup; TOC anchors pointing at ids that didn't exist; MCP wiring that never ran because it imported a symbol that doesn't exist; dead `/page.json` and `/architecture.txt` links; a broken Open Graph image; `piratesbagain.com`.

### What's New in 1.0.0

First stable release — a major architectural milestone:

- 🚀 **Dash 4.x (4.2.0)** and **DMC 2.7.0** — modern framework with pluggable backends.
- 🔌 **Pluggable backends**: run the same app on **Flask**, **FastAPI**, or **Quart** by setting `DASH_BACKEND` — no code changes. ASGI backends add async/websocket callbacks, OpenAPI docs, a native JSON API, and ASGI middleware. New **Pluggable Backends**, **Backend Deep Dive**, and **FastAPI Showcase** docs.
- 🎯 **dash-improve-my-llms 2.0**: the `LLMS_DOC` pattern (per-page prose served at `/<page>/llms.txt`), multi-backend AI/LLM surfaces, and an MCP resource bridge on Dash 4.3+.
- 🧹 **Removed the TOON format** entirely — `lib/toon_generator.py`, the TOON docs/dashboard, and `/llms.toon` routes are gone (the package no longer exports `TOONConfig`, `toon_encode`, `generate_*_toon`).
- ⚠️ **Removed `mark_important()` / `mark_component_hidden()`** (now no-ops) and the `/page.json` / `/architecture.txt` routes — Dash 4.3 MCP covers structured introspection. Write emphasis directly into a page's `LLMS_DOC` markdown.

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

### Built With
- [Plotly Dash](https://dash.plotly.com/) - The web framework
- [Dash Mantine Components](https://www.dash-mantine-components.com/) - Beautiful UI components
- [Mantine](https://mantine.dev/) - React component library

### Inspired By
- [dmc-docs](https://github.com/snehilvj/dmc-docs) - Documentation framework inspiration

### Special Thanks
- [@AnnMarieW](https://github.com/AnnMarieW) for suggested improvements
- The Dash community for continuous support

---

## 📞 Support & Community

### Get Help
[![Discord Invite](https://img.shields.io/discord/396334922522165248?color=4A55CC&label=Discord&logo=discord&style=for-the-badge)](https://discord.gg/uwQ2f3KCad)

- **Documentation**: You're reading it!
- **Issues**: [GitHub Issues](https://github.com/pip-install-python/Dash-Documentation-Boilerplate/issues)
- **Discussions**: [GitHub Discussions](https://github.com/pip-install-python/Dash-Documentation-Boilerplate/discussions)
- **Dash Community**: [Plotly Community Forum](https://community.plotly.com/)

### Stay Connected

**GitHub**: [@pip-install-python](https://github.com/pip-install-python)
![GitHub Followers](https://img.shields.io/github/followers/pip-install-python?style=social)

**YouTube**: [@2plotai](https://www.youtube.com/@2plotai?sub_confirmation=1) — build-alongs and component walkthroughs

---

### Want to Contribute?
Check out open issues labeled [`good first issue`](https://github.com/pip-install-python/Dash-Documentation-Boilerplate/labels/good%20first%20issue)

---

<div align="center">

**[⬆ Back to Top](#dash-documentation-boilerplate)**

Made with ❤️ by the Dash community

Pip Install Python LLC @ [2plot.ai](https://2plot.ai)

**Star this repo** if you find it useful! ⭐

</div>
