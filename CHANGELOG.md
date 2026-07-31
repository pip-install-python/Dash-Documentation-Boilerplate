# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Three threads of work, all still unreleased: the CI/CD system, network
analytics reporting, and the upgrade to `dash-improve-my-llms` 2.2.0.

2.1.0 was assigned during that package's development and never published, so
there is no 2.1.0 anywhere and 2.0.0 upgrades straight to 2.2.0. Work
described here as "2.1-era" in earlier drafts shipped as part of 2.2.0.

### Changed — dash-improve-my-llms from PyPI (2.3.3); vendored copy removed

The four-host verification gate passed, `dash-improve-my-llms` published, and
this repo switched from the vendored sdist to the PyPI pin
(`dash-improve-my-llms[flask]>=2.3.2`) — the Phase-5 step the vendor block
always anticipated. `vendor/dash_improve_my_llms-*.tar.gz` is gone; CI's ASGI
legs and the Dockerfile install from PyPI too. `vendor/` still carries
`dash_clerk_auth` (not on PyPI, deliberately outside requirements.txt).

The floor resolves to 2.3.3, which recategorises the Anthropic crawlers:
`ClaudeBot` — the actual *training* crawler — moves to `Disallow`, while the
user-triggered and search fetchers `Claude-User` / `Claude-SearchBot` are
allowed, matching the intent the OAI-SearchBot fix established for OpenAI.
It also strips unexpanded directive lines from resolved prose. The artifact
fingerprint in `tests/test_llms_routes.py` and `scripts/smoke_live.py` now
asserts the full crawler split, so a host running a stale build fails its
post-deploy battery by name.

Verifying that fingerprint exposed a real misconfiguration:
`run.py` set `block_ai_training=False`, so the training bucket was never
emitted and every training crawler was silently allowed — the opposite of the
"blocks AI training, allows AI search" policy this project documents, and it
would have made 2.3.3's ClaudeBot recategorisation invisible on this host.
Now `block_ai_training=True`, matching the documented policy and the rest of
the network.

### Changed — production rollout: re-vendor 2.3.2 / 0.9.1, live hub contract

Deployment prep for `boilerplate.2plot.dev` (rollout step 4; the hub's auth
endpoints are now live in production).

- **`dash-improve-my-llms` 2.3.0 → 2.3.2** (vendored). The vendored 2.3.0 was
  a pre-fix build whose robots.txt disallowed OAI-SearchBot — ChatGPT
  search's crawler, exactly the audience these surfaces exist for. 2.3.2
  allows it. `User-agent: OAI-SearchBot` → `Allow: /` in a live host's
  `/robots.txt` is the fingerprint that it runs the fixed artifact (pip
  metadata is invisible from outside); `test_robots_artifact_fingerprint`
  now asserts it locally so a vendored regression fails CI, not production.
  2.3.1 was assigned during development and never published.
- **`dash-clerk-auth` 0.9.0 → 0.9.1** (vendored, built from the
  Dash-Clerk-Auth-Hook working tree). 0.9.0 ships a bug hitting every Clerk
  satellite forked from this template: clerk-js v5 auto-instantiates from the
  script tag's `data-*` attributes and reads the *instance* domain, so on a
  satellite the user button never mounts (dead avatar) while server-side
  session verification keeps working. 0.9.1 emits
  `data-clerk-domain="<satellite_domain>"` on the tag when `is_satellite=True`.
  This app runs no Clerk by design — the bump is for the template's sake.
  `lib/auth.py`'s fixup #1 guards on the attribute's absence, so it degrades
  to a no-op under 0.9.1 and stays for forks still on 0.9.0.
- **`lib/hub_client.py` aligned with the hub's real contract.** Two functions
  predated the hub going live. `current_key()` now sends
  `{"token": <Clerk session token>, "app": ...}` — the hub 401s any
  caller-asserted identity (`user_id` in the payload is the forgery path) and
  verifies the token against Clerk's JWKS, minting at `scope=auth`, never
  admin. Call it on copy-button click, never on page render; `None` degrades
  to copying the plain URL. `hub_tiers()` is no longer a stub: signed POST
  `/api/page-tiers` `{"app": ...}` → `{"tiers": {path: tier}, "ttl": s}`,
  cached for the returned TTL with failures cached 60s — so a down hub costs
  one timeout per window, not one per request, and resolves to the local
  tier, which the ceiling rule guarantees can never loosen anything.
  `verify()` already matched the hub and is untouched.

### Added — AI/LLM surfaces (dash-improve-my-llms 2.2.0)

- **`lib/network_directory.py`** — the peer/affiliated/external directory,
  defined once here and copied verbatim into every satellite. Publishes
  `<link rel="related">` tags, a `## Network` section in `/llms.txt`, and
  followed links in the prerendered body, so an agent landing on one satellite
  can enumerate the rest. Filters the app's own URL out of `peers`.
- **Wordmark** — `"2"` + morse(`plot`) + `"ai"`, drawn as columns of dots and
  dashes in the header of the rendered `llms.txt` view. No period glyph: the
  morse block already separates the halves, and a literal `.` beside it reads
  as punctuation dropped into a graphic. The renderer turns a suffix ending in
  `i` into an upward flourish, so `"ai"` draws as `a` plus that mark, with the
  real domain in `label` for screen readers and the SVG `<title>`. It lives in
  the shared module rather than per-app, which is what keeps one mark across
  the network instead of twelve near-identical ones.
- **Page `llms.txt` documents are no longer dead ends.** Each now opens with
  the site index, the network index one level up the hub chain (`2plot.dev`,
  correct for a `*.2plot.dev` subdomain), and the sitemap. These documents are
  usually read in isolation — pasted into a chat, handed to an agent — and an
  agent fetches a URL rather than crawling from one, so previously its
  exploration simply stopped there.
- **The same URL content-negotiates.** Agents, crawlers and curl get the
  Markdown byte for byte; browsers get it rendered behind a header carrying
  the network identity. `?raw=1` and `?format=html` override, both variants
  send `Vary: Accept`, and the rendered view is `noindex` so it never competes
  with the page it documents. Verified identical on Flask, FastAPI and Quart.
- **`docs/networks/networks.md`** — the guide for satellite authors: the three
  tiers, why per-host SEO can't express any of this, the wordmark and bulletin
  conventions, the one-URL-two-audiences contract, and the verification
  commands.
- **Network bulletin left deliberately unwired.** `configure_bulletin()` sits
  commented next to `add_llms_routes` with a pointer to the contract.
  `2plot.dev` does not serve `/api/network/bulletin` yet, and pointing at a
  dead endpoint gains nothing: the client degrades silently and the header
  renders fine without it — the "Tips for getting started" and "What's new"
  panels use the package's built-in defaults, which a bulletin only overrides.

### Added — Clerk authentication and llms.txt access control

Opt-in, and off in a default clone. This is the template every `*.2plot.dev`
subdomain is forked from, so the goal was a pattern good enough to copy rather
than a one-off. Requires `dash-improve-my-llms` 2.3.0 (`configure_access`,
`configure_viewer_identity`) and the vendored `dash-clerk-auth` 0.9.0, which is
deliberately **not** on the active requirements line — a default install should
not pull in an auth stack the site does not use.

- **`lib/auth.py`** — adapted from `2plot_leaflet/lib/auth.py`, the
  implementation already sharing authenticated state across `2plot.ai` →
  `2plot.dev` → `leaflet.2plot.dev` in production. Keeps both satellite fixups
  for `dash-clerk-auth` 0.9.0 (clerk-js reads `domain` as a *constructor*
  option from `data-clerk-domain`, and a satellite must `redirectToSignIn()`
  rather than open a modal that 403s), the `pk_live` auto-enable so production
  cannot silently boot in primary mode, `DISABLE_CLERK=1`, and call-time env
  reads. Changed for the template: the satellite domain derives from
  `APP_BASE_URL`, which every deployment must set anyway — one variable rather
  than two, and one fewer way to announce another site's domain to Clerk.
- **`lib/page_tiers.py`** — `public < auth < admin < hidden`, declared in
  markdown frontmatter (`tier: admin`) because this template is already
  frontmatter-driven and marking one page should not require a control board.
  Two rules: everything except `hidden` falls open when Clerk is unavailable
  (documentation must not brick over a missing credential), and
  `effective_tier = more_restrictive(local, hub)` so a satellite may restrict
  further but never loosen.
- **`lib/hub_client.py`** — the client for the hub's `/api/agent-key/current`
  and `/api/agent-key/verify`. Authenticates the caller with the network's
  existing `CROSS_APP_WEBHOOK_SECRET` HMAC scheme, the one
  `lib/satellite_reporter` already uses: it authenticates *who is asking* and
  derives nothing, which is what keeps "satellites hold no key material" true
  while still keeping the verify endpoint from being an open key-guessing
  oracle. Verdicts cached on a SHA-256 fingerprint of the key rather than the
  key, because that cache is process memory a debugger or error reporter can
  dump. `allow` cached 900s, `deny` 60s — a brief hub outage must not gate
  readers who were fine a minute ago, while a revoked key should stop working
  promptly.
- **`lib/access.py`** — the policy, and its ordering is the design:
  tier → **local Clerk session** → hub, only for `?key=`. A signed-in visitor
  resolves entirely on this host, so the hub being down gates nothing for them;
  only the agent path, which arrives with no cookie, needs the hub at all.
  Reversing it would couple every satellite's availability to one host for no
  benefit. Kept out of `run.py` so satellites inherit one file.
- **`docs/authentication/`** — three layers, so a reader stops at the one they
  need: the default (nothing to do), a standalone site with its own Clerk, and
  joining or running a network. Names the two traps: the Clerk token's `iat` is
  the token's age, not the sign-in's, so wiring it renders a clock that resets
  every minute; and identity must never travel in the bulletin, which is
  TTL-cached and shared across every satellite.
- **`handoff/`** — kickoff prompts for the two repos this unblocks: an addendum
  pairing with the `pip-docs+` hub brief, carrying the request shapes and cache
  TTLs the client already sends, and a per-subdomain port guide.
- **`tests/test_access.py`** — 17 tests against a fake hub. The two that
  justify the design: signed-in browser with the hub unreachable still resolves
  to `allow`, and a valid key with the hub down degrades to `gated` rather than
  500 or prose. One asserts the *ordering* rather than the outcome — a
  signed-in reader must trigger zero hub calls, since "allowed" could otherwise
  come from a hub that happened to agree.

**Inert until a tier says otherwise.** With the wiring in place, no Clerk keys,
and every page public, all 43 surfaces are byte-identical to the build before
any of it existed — measured, with a control run to strip out the per-request
ids Dash puts in page HTML.

### Changed — dash-improve-my-llms 2.2.0 → 2.3.0

Vendored, as before; 2.3.0 is additive and opt-in. Verified as a no-op on the
surfaces that matter: every Markdown document, the root index, `sitemap.xml`,
`robots.txt` and the crawler HTML are byte-identical. The HTML viewer variants
grow by 192 bytes each — three CSS rules for the identity block that ship
whether or not identity is configured. Behaviourally a no-op; not literally
byte-identical everywhere, which is worth stating precisely since this baseline
is what a later regression gets attributed to.

### Added — CI/CD and tests

- **`.github/workflows/ci.yml`** — flake8 (blocking), then the full test suite
  across a matrix of Python version × backend × Dash version: Flask, FastAPI
  and Quart on Python 3.12, Python 3.11 and 3.13 on Flask, and the bottom of
  the `~=4.4.1` range pinned explicitly on Flask and FastAPI so a 4.4.0-only
  regression cannot hide behind pip resolving to 4.4.1. Asserts the resolved
  Dash and `dash-improve-my-llms` versions before running anything, boots the
  app under gunicorn (a page can render under a test client and still fail
  under a real WSGI worker), and builds and probes the Docker image.
- **`.github/workflows/cd.yml`** — runs CI, POSTs the `RENDER_DEPLOY_HOOK_URL`
  secret, waits for the new instance to be *sustainably* healthy (Render swaps
  instances rather than restarting in place, so a single 200 from `/healthz`
  proves nothing), then verifies the live site. Skips the deploy step when the
  secret is absent instead of failing, so a fork isn't red on day one.
- **`tests/`** — a pytest suite that boots `run.py` itself rather than a test
  app. `conftest.py` normalises the three backends' test clients behind one
  synchronous `.get()`, including driving Quart's async client from a
  fixture-owned event loop. Covers page registration and reachability, stub
  bodies, rendered prose, canonical tags, sitemap/robots/llms.txt, content
  negotiation in both directions, the navigation block, the banner and its
  panels, the network directory and wordmark, docs frontmatter and directive
  targets, heading anchors, and the `BASE_URL` guard.
- **`scripts/smoke_live.py`** — post-deploy checks against a live satellite,
  standard library only. Covers the failures that are silent in production: a
  canonical on the wrong host, a page serving the JavaScript stub, viewer
  chrome leaking into an agent's Markdown, a missing `Vary: Accept`, a missing
  network directory, and dead peer `llms.txt` links. Run in CD and by hand
  (`python scripts/smoke_live.py https://emojimart.2plot.dev`), and itself
  tested against the in-process app so a typo can't turn every live check into
  a silent pass.
- **`scripts/dev.sh`** — starts the development server with *this* project's
  interpreter, resolved from the script's own location rather than from an IDE
  setting or `PATH`.
- **`scripts/audit_links.py`** — walks every page's `llms.txt`, extracts every
  link, resolves internal paths in-process and checks the rest over the
  network. A dead link in an `llms.txt` is worse than one on a page: the agent
  holding that document has no navigation to fall back on and no way to tell a
  typo from a host that is down.

  Classified rather than lumped together, because the classes want different
  responses: `internal` is a real defect, `self-host` is correct once deployed,
  `network` is a peer awaiting the rollout, `unpushed` is a file that exists
  locally and 404s only until the branch is pushed, and `external` is someone
  else's problem to route around. Code spans and fenced blocks are skipped —
  a URL inside backticks renders as `<code>`, not `<a>` — and a transport
  failure is retried once, because an audit that cries wolf gets ignored.
- **`LICENSE`** — the MIT text the README badge, `pages/home.md` and the
  Schema.org block have all claimed since 0.1.0 without the file ever existing.
- **`render.yaml`** — Render Blueprint for `boilerplate.2plot.dev`: gunicorn,
  `/healthz` health check, custom domain, and a persistent disk for the
  analytics ledger (on an ephemeral filesystem a mid-day deploy wipes it and
  the next hourly report overwrites the day's real total).
- **`.flake8`**, **`pytest.ini`**.

### Added — Network analytics reporting to 2plot.ai

- **`lib/satellite_reporter.py`** — hourly signed rollup POSTed to
  `https://2plot.ai/api/satellite/traffic`, so a deployed docs site shows up on
  the hub's owner-only `/traffic` dashboard. HMAC-SHA256 over
  `"{timestamp}." + body` with `CROSS_APP_WEBHOOK_SECRET`, matching the
  network's existing webhook scheme. Off by default: no secret, no reporting.
  Re-posts yesterday during the first hours of a new day so the final hits of a
  day aren't left out, and uses a lease file so only one web worker reports per
  interval instead of every worker racing. `python -m lib.satellite_reporter
  --dry-run` prints the payload without sending it.
- **`lib/traffic_rollup.py`** — derives the reported numbers (`human_hits`,
  `bot_hits`, `visitors`, `sessions`, `median_session_s`, top pages, countries)
  using the hub's own definitions, so this app's figures are comparable with
  every other app on the chart. Infrastructure paths (`/healthz`, `/llms.txt`,
  `/robots.txt`, `/sitemap.xml`, assets, Dash internals) are excluded from the
  report but stay in the local ledger.
- **`lib/health.py`** — `/healthz` on Flask and Quart, matching the endpoint
  the FastAPI build already declared. The hub's hourly sweep probes it for
  up/down + latency, which previously only worked on one of the three backends.
- Quart now tracks visitors too; previously only Flask and FastAPI did.

### Changed — dependencies

- **`dash-improve-my-llms` 2.0.0 → 2.2.0**, installed from `vendor/` until it
  is published to PyPI. App 1 of 4 in a staged rollout, first because every
  satellite documentation site is forked from this repo — a convention set here
  propagates, and so does a mistake.

  Page metadata now *merges* instead of assigning, so no later bookkeeping call
  can erase a page's prose; the prerender reaches every visitor rather than
  only recognised crawlers; and the Markdown renderer emits real anchors,
  tables, code fences and rules. Measured on this app: link counts in crawler
  bodies went from 3 per page to 3–11, code fences from 0 to 5–29 per page, and
  horizontal rules stopped rendering as literal `---` text. No page serves the
  crawler stub, before or after — this repo was never affected by the
  prose-erasure bug, having no bridge loop over `dash.page_registry`.

- **Dash pinned to `~=4.4.1`** (was `>=4.4.0`). Verified matrix, from real apps
  on each backend with the failure reproduced on stock Dash:

  | Dash | Flask | FastAPI | Quart |
  |---|---|---|---|
  | 4.1.0 | ok | n/a — no pluggable backends | n/a |
  | 4.2.0 | ok | ok | ok |
  | 4.3.0 | ok | **broken — every non-root page 500s** | ok |
  | 4.4.0 | ok | ok | ok |
  | 4.4.1 | ok | ok | ok |

  4.3.0 added an early-return path guard to the ASGI middleware that returns
  before `set_current_request`, while the page catch-all still calls
  `get_current_request()` — so it raises `RuntimeError: No active request in
  context`. The catch-all is byte-identical between 4.2.0 and 4.3.0; only the
  middleware changed. 4.4.0 set the context inside the catch-all as well, so a
  future middleware guard cannot reintroduce it: 4.4.x is structurally safer,
  not merely currently-passing.

  `~=4.4.1` lets patch releases flow without twenty pull requests while
  blocking 4.5.0, so a minor bump goes through the matrix deliberately. Pinned
  for the most constrained backend network-wide, **including Flask-only apps** —
  `DASH_BACKEND` is an env var and this is a shared template, so a Flask
  deployment becomes a FastAPI deployment with one env change and no code
  change.

- **Dependency floors are enforced at startup, not advised.** A version below
  the floor stops the boot, names what would degrade, and prints
  `sys.executable` alongside the expected interpreter. `ALLOW_STALE_DEPS=1`
  opts out for anyone deliberately testing an older release. The Dash floor is
  fatal only on FastAPI, where 4.3.0 is an outage rather than a degradation.
  See *Fixed — environment and tooling* for why this is a hard failure.

- **`network_directory.apply()` gates the `wordmark` argument** on the
  installed signature. During a staged rollout this module reaches satellites
  before the new package does, and Python raises `TypeError` on an unknown
  keyword — so passing it unconditionally would turn an older satellite's boot
  into a crash rather than a missing graphic. Same technique `run.py` uses for
  Dash's `enable_mcp`.

### Changed — hosts, branding and repo hygiene

- **`BASE_URL` moved to `lib/constants.py`** and reads `APP_BASE_URL` from the
  environment, defaulting to `https://boilerplate.2plot.dev`.
  `require_owned_base_url()` refuses to boot in production when `APP_BASE_URL`
  is unset or points at a platform hostname (`*.onrender.com` and friends).
  This is the template's highest-consequence footgun: a fork that leaves the
  default in place emits the boilerplate's canonical URL on every one of its
  pages, which asks Google to deindex it, and nothing about the app looks
  broken while it happens.
- **YouTube links now point at [@2plotai](https://www.youtube.com/@2plotai)**;
  `plotly.pro` is replaced by `2plot.ai` throughout, and the deployment host by
  `boilerplate.2plot.dev`. A test fails the build if a live link to
  `plotly.pro` reappears.
- **`.claude/` is untracked and gitignored.** Local session workspace; noise in
  a template other people fork.
- **Dockerfile** copies `vendor/` before the pip layer (the build fails
  otherwise while the package installs from an sdist), declares a `HEALTHCHECK`
  against `/healthz`, and no longer leaves apt lists in the image.

### Fixed — SEO and template

- **Every page shipped two `<link rel="canonical">` tags.** `templates/index.html`
  hard-coded one pointing at the site root while the package injected the
  correct per-page one. A conflicting pair is treated as no signal at all, so
  the per-page canonicals were doing nothing. The template no longer sets one.
- **Two advertised LLM endpoints were 404s.** `<meta name="llms-page-json">`
  and `llms-architecture` pointed at `/page.json` and `/architecture.txt`,
  both removed in dash-improve-my-llms 2.0. The `<noscript>` block linked to
  them too.
- **The Open Graph image never existed.** Every share rendered a blank card
  against `assets/og-image.png`, a file not in the repo. Now points at a real
  asset with its actual declared dimensions.
- **`apple-touch-icon.png` and `site.webmanifest` 404'd on every page load** —
  both `<link>`ed but neither shipped. Commented out with instructions.
- **`piratesbagain.com`** in the navbar (missing `r`) — a dead outbound link
  on every page.
- Placeholder metadata left in the template: `"Your Organization Name"`,
  `"Your Name or Organization"`, `yourdomain.com`, and a `price` of
  `"29_000_000"` in the SoftwareApplication schema (not a valid number, and
  the project is MIT-licensed).

### Fixed — every page shipped the same hard-coded title

`templates/index.html` hard-coded a `<title>` and contained no `{%title%}`
placeholder anywhere, so the per-page titles `pages/markdown.py` registers were
discarded and every page's title depended entirely on `dash-improve-my-llms`
rewriting that one element. `LLMSConfig(prerender=False)` — the documented
one-argument rollback — silently reverted every page on every satellite to one
identical string.

Now `<title>{%title%}</title>`, with `app.title` set from a new
`constants.APP_TITLE`. Without that second half the placeholder resolves to
Dash's default, the bare string `"Dash"`, which is worse than what it replaced.

**The trap, for anyone editing that block.** The package finds the element with
`re.compile(r"<title>.*?</title>", DOTALL | IGNORECASE)` and rewrites the first
match:

- Delete the element and no closing tag remains to anchor on — nothing is
  rewritten and no page has a title at all.
- Spell the tag name in angle brackets inside a nearby *comment* and the match
  starts there instead, running to the next closing tag and replacing every
  line in between. The comment, and any markup after it, vanishes from the
  served page. With rewriting on it still looks correct, so the damage is only
  visible in the served bytes.

The comment above the element used to contain a literal `<title>` for exactly
this reason, and the first attempt at this fix reintroduced it *while
explaining it*. The block now describes the tags in words, and three tests pin
it: the placeholder is present, the title regex matches nothing but the element
itself, and no comment spells the tag in angle brackets. A fourth asserts every
page serves a distinct title.

### Fixed — dead links in the llms.txt documents

Found by `scripts/audit_links.py` across all 10 documents and 102 links.

- **The MIT `LICENSE` file did not exist.** `pages/home.md` and the README
  both linked to it, and the Schema.org block declared the licence — so the
  one link a reader follows to check the terms was the one that 404'd. Added.
- **The development-server port was wrong.** `pages/home.md` said
  `http://localhost:8553`; `run.py` binds **8559**. The Docker instruction
  (8550) was right for the container but rendered as a live link that 404s for
  anyone not running the image — both are now code spans, so they read as
  instructions rather than as something to click.
- **The `SKILLS.md` link pointed at the wrong path** —
  `dash-improve-my-llms/blob/main/SKILLS.md`, but the file lives under
  `docs/`. Fixed to `blob/main/docs/SKILLS.md`.

### Fixed — Markdown rendering

- **A heading containing inline code crashed the site at startup.**
  markdown2dash's renderer does `create_heading_id(text[0])`, and when the
  first inline token is formatted, `text[0]` is a component rather than a
  string — `AttributeError` at import, taking every page down. Fixed in
  `lib/directives/headings.py`.
- **TOC anchors pointed at ids that didn't exist.** Even when it didn't crash,
  the renderer slugged only the *first* inline token (`## Wiring **it** up` →
  `id="wiring"`) while the `toc` directive slugged the raw markdown
  (`wiring-**it**-up`). Both now use one `slugify`, so the link and its target
  agree. Plain headings slug exactly as before, so no existing anchor moved.

### Fixed — MCP wiring

- **The MCP server was never enabled.** `run.py` did
  `from dash import mcp_enabled`, but the symbol lives in `dash.mcp` — the
  import always raised, and the app printed "MCP not available in dash 4.4.1
  (needs >=4.3)" while running 4.4.1. `mcp_enabled` is also the decorator for
  marking a *function* as an MCP tool, not a server switch. The server is
  started from Dash's constructor, so `enable_mcp=` / `mcp_path=` is now passed
  there, and it works on all three backends rather than only FastAPI. Passed as
  `**kwargs` so naming a 4.3+ keyword can't break the boot on an older Dash.

### Fixed — environment and tooling

- **The app booted silently against another project's virtualenv.** An IDE run
  configuration pointing elsewhere started this app against whatever versions
  that environment held — on `dash-improve-my-llms` 2.0.0 there is no
  `llms_viewer.py` at all, so `/<page>/llms.txt` served plain Markdown to every
  visitor and nothing in the log said why. It cost a debugging session across
  two repositories, chasing a stale process and a browser cache that were both
  innocent, and survived a server restart and an incognito window because
  neither was the variable.

  Made worse by this repo's own `enable_mcp` fix, which removed the
  `TypeError` that had been failing loudly on the wrong interpreter — trading a
  crash for a plausible wrong answer.

  Warnings were tried first and were not enough: they scroll past above a wall
  of page-loading output while the app keeps serving. The floors are now fatal
  (see *Changed — dependencies*), and `scripts/dev.sh` removes the choice of
  interpreter entirely. A test asserts the same floor, so `pytest` in the wrong
  environment reports the cause instead of thirty downstream symptoms.
- **CI installed a tarball path that no longer existed.** `ci.yml` hardcoded
  the vendored filename for the FastAPI and Quart legs, so a version bump broke
  exactly two of the matrix entries. It now globs `vendor/`.
- **Header lookups in the test client were case-sensitive.** Werkzeug returns
  `Content-Type`, httpx returns `content-type`, so the content-negotiation
  assertions passed on Flask and failed on FastAPI and Quart — reading like a
  backend bug when the served headers were identical and correct.
- **A peer serving its SPA shell counted as a live document.** The peer check
  asserted only `status == 200`, but a Dash app answers its catch-all with the
  app shell for *any* unmatched path — `2plot.dev/api/this-endpoint-cannot-exist`
  returns `200 text/html`, as does `/api/network/bulletin`, which does not
  exist. A status-only check therefore passes against every host in the
  network whether or not it publishes anything. `smoke_live.py` now rejects an
  HTML body for a document URL, and the same reasoning applies to the
  network-wide check in `ROLLOUT.md`.
- **`smoke_live.py` extracted malformed peer URLs.** Its pattern stopped only
  at whitespace and `)`, and the 2.2.0 navigation block writes links as
  `[https://host/llms.txt](https://host/llms.txt)` — so it produced
  `https://2plot.dev](https://2plot.dev/llms.txt`, which would 404 in CD and
  fail a perfectly good deploy. Invisible locally, because the test shim
  answers 200 for off-host URLs.
- **Viewer-chrome detection keyed on a bare class name.** `docs/networks`
  legitimately *documents* `dv-banner`, so a substring check failed on the
  page's own prose. Both the suite and `smoke_live.py` now match rendered
  markup (`<div class="dv-banner"`), which a Markdown document can never
  contain — otherwise the check quietly teaches people to stop documenting the
  viewer.

### Fixed — Analytics accuracy

- **AI-search crawlers were not being counted.** The visitor hook was
  registered after `add_llms_routes`, and the package's bot middleware
  short-circuits ClaudeBot / ChatGPT-User / PerplexityBot with its own
  response — so those requests never reached the tracker. The hook is now
  registered first on Flask/Quart (and last on FastAPI, where Starlette runs
  the most recently added middleware outermost).
- **Every visitor looked like one visitor behind a proxy.** The tracker used
  `remote_addr`, which on Render/Cloudflare is the proxy. It now reads
  `CF-Connecting-IP`, `True-Client-IP`, `X-Real-IP` and `X-Forwarded-For`
  first, and takes the country from Cloudflare's `CF-IPCountry` header when
  present — free, instant and accurate.
- **Concurrent workers overwrote each other's hits.** The ledger was read,
  modified and rewritten with no lock; under four workers most hits were lost.
  Writes now take an `flock` and land via an atomic replace.
- **Geolocation no longer blocks page views.** The ip-api.com lookup ran inline
  with a 2s timeout on the first hit from each new IP. It now runs in a bounded
  background thread and is backfilled into the buffered hit before it is
  written, so the country is still recorded. Disable with
  `ANALYTICS_GEO_LOOKUP=0`.
- **The ledger is bounded and no longer rewritten on every request.** Hits are
  buffered (10 hits / 30s) and pruned to `ANALYTICS_RETENTION_DAYS` (45) and
  `ANALYTICS_MAX_VISITS` (20000); the hub holds the durable history.
- The ledger path is now absolute (`TRAFFIC_ANALYTICS_FILE`, else repo root) —
  a relative default wrote a different file depending on the working directory.
- Tablets are no longer counted as mobile (iPads and most Android tablets send
  a mobile token too, and the mobile test ran first).

## [1.0.0] - 2026-06-14

First stable release. The boilerplate moves to **Dash 4.x** with pluggable
backends and **dash-improve-my-llms 2.0**, and retires the experimental TOON
format entirely. This is a significant architectural release — see the
migration notes at the end of this section.

> **Versioning note:** the `0.5.0`–`0.8.0` entries below were the December 2025
> TOON line. That work has been removed (see "Removed" below) and the project
> resumes a single, monotonic version line at `1.0.0`. A short-lived second
> `0.5.0` (the May 2026 dash-improve-my-llms 2.0 preview) has been folded into
> this entry.

### Added — Pluggable backends (Flask / FastAPI / Quart)

- **`lib/backend.py`** — single source of truth for backend selection. Reads
  the `DASH_BACKEND` environment variable (`flask` | `fastapi` | `quart`),
  falls back to `flask`, and exposes `BackendInfo` (label, color, icon,
  async flag) so UI components stay in sync with the running backend.
- **`run.py`** constructs `Dash(backend=resolve_backend(), ...)` and attaches
  `app._backend_info` for layout components.
- **`components/backend_badge.py`** — a navbar/header badge that shows which
  backend the site is currently running on.
- **`lib/asgi_middleware.py`** and **`lib/asgi_routes.py`** — ASGI middleware
  and showcase routes (`/healthz`, `/api/backend`, `/api/pages`) that light up
  on the FastAPI/Quart backends.
- New documentation sections:
  - **Pluggable Backends** (`docs/backends/`) — run the site on any of the
    three backends with one env var.
  - **Backend Deep Dive** (`docs/backend-comparison/`) — architecture,
    strengths/weaknesses, deployment, and best practices for each backend.
  - **FastAPI Showcase** (`docs/fastapi-showcase/`) — OpenAPI docs, a native
    JSON API, ASGI middleware, async demo, endpoint explorer, and a stress
    test, showing what the ASGI backends unlock.

### Added — AI/LLM integration via dash-improve-my-llms 2.0

- **`LLMS_DOC` pattern.** Pages expose a module-level prose string (or call
  `register_page_metadata(path, llms_doc=...)`); the package serves it verbatim
  at `/<page>/llms.txt` under whichever backend is active.
  - `pages/markdown.py` registers the expanded markdown body (with
    `.. source::` directives inlined) for every markdown-driven page.
  - `pages/home.py` exports `LLMS_DOC = content` for the root prose.
- **Multi-backend AI/LLM surfaces.** `add_llms_routes(app)` auto-detects the
  backend and serves `/llms.txt`, `/<page>/llms.txt`, `/sitemap.xml`, and
  `/robots.txt` under Flask, FastAPI, and Quart alike — no `if IS_FLASK:` gate.
- **MCP resource bridge.** Each page's prose registers as a `dash.mcp` resource
  on Dash 4.3+ (a silent no-op on older Dash).

### Changed

- **Upgraded Dash 3.2.0 → 4.2.0** and **Dash Mantine Components 2.4.0 → 2.7.0**
  (Mantine 8.3.6). React 18.2.0.
- **`docs/ai-integration/ai-integration.md`** fully rewritten for the 2.0
  surface (LLMS_DOC, multi-backend, MCP bridge).
- **`requirements.txt`** now pins `dash>=4.1.0`, `dash-mantine-components>=2.7.0`,
  and `dash-improve-my-llms[flask]>=2.0.0`, with commented `[fastapi]`,
  `[quart]`, and `[all]` extras plus `uvicorn` for ASGI deployment.
- **`docs/example/example.md`** "Highlighting Important Elements" section
  rewritten around the `LLMS_DOC` pattern.
- **`components/header.py`**, **`components/appshell.py`**, and
  **`components/navbar.py`** updated for the new backend badge and navigation
  (TOON Format and Handoff entries removed).
- **`lib/directives/llms_copy.py`** / **`assets/llms_copy.js`** updated for the
  2.0 `/<page>/llms.txt` routing.
- `APP_VERSION` and `package.json` bumped to `1.0.0`.

### Removed

- **The entire TOON format system** — `lib/toon_generator.py` (~1100 lines),
  the `docs/toon-format/` page, the TOON Analytics Dashboard
  (`docs/data-visualization/toon_dashboard.py`), and all `/llms.toon`
  routes. `dash-improve-my-llms` 2.0 removed TOON from its public API
  (`TOONConfig`, `toon_encode`, `generate_*_toon` no longer exist).
- **`/page.json` and `/<page>/page.json`** routes — dropped in
  dash-improve-my-llms 2.0; Dash 4.3 MCP exposes layouts as resources natively.
- **`/architecture.txt`** — likewise superseded by MCP.
- **`mark_important()`** and **`mark_component_hidden()`** — now deprecated
  no-ops in 2.0. Write the emphasis directly into a page's `LLMS_DOC` markdown.
- **`LLMS_INTEGRATION.md`** and the `docs/handoff/` doc (the FastAPI port plan
  that became 2.0) — superseded by the in-app AI Integration page.

### Migration notes (from any 0.x)

1. **Backend:** the site defaults to Flask, so no change is required. To run on
   FastAPI or Quart, install the matching extra (`pip install "dash[fastapi]"`)
   and set `DASH_BACKEND=fastapi`.
2. **AI/LLM prose:** give each page module an `LLMS_DOC = """..."""` string at
   module scope (or `register_page_metadata(path, llms_doc=...)` when the prose
   is computed). The startup `UserWarning` from 2.0 names every page still
   missing prose.
3. **dash-improve-my-llms extra:** pick `[flask]`, `[fastapi]`, `[quart]`, or
   `[all]` in `requirements.txt`.
4. **Removed APIs:** replace any `mark_important()` / `mark_component_hidden()`
   calls (now no-ops) with `LLMS_DOC` content, and remove references to TOON,
   `/page.json`, and `/architecture.txt`.

---

## [0.8.0] - 2025-12-14

### Added
- **TOON v3.3 Format Enhancements** - Major comprehension improvements from ~75-80% to ~95%+
  - **New Dataclasses**:
    - `CodeTip` - Short instructional code snippets with context
    - `BestPractice` - Numbered best practices with multi-line code examples
    - `Pattern` - Architectural patterns with implementation code
    - `Resource` - External resource links with full URLs
  - **New Extraction Functions**:
    - `extract_code_tips()` - Finds short code snippets (2-15 lines) with headings
    - `extract_best_practices()` - Extracts numbered practices from "Best Practices" sections
    - `extract_patterns()` - Captures pattern implementations from "Common Patterns" sections
    - `extract_resources()` - Extracts markdown links with full URLs preserved
  - **New TOON Sections**:
    - `tips[N]{context,lang,code}:` - Compact code tips with one-line previews
    - `bestPractices[N]:` - Full multi-line code snippets for each practice
    - `patterns[N]:` - Pattern descriptions with implementation code blocks
    - `resources[N]{name,url}:` - External links without URL truncation

### Changed
- **Updated TOON format version from toon/3.2 to toon/3.3**
- **Enhanced summary line** to include tips, best practices, patterns, and resources counts
- **Improved content deduplication** - Tips exclude Best Practices and Patterns sections to avoid duplicate code

### Fixed
- **Code block detection in section boundaries** - Headings inside code blocks (like `## My Visualization` in markdown examples) were incorrectly detected as section boundaries
  - Added code block range detection using `code_block_ranges` list
  - Added `is_in_code_block()` helper to filter out false headings
  - Applied fix to `extract_code_tips()`, `extract_best_practices()`, and `extract_patterns()`
- **`re.escape()` issue** - `re.escape("Best Practices")` was escaping spaces incorrectly
  - Changed to custom escaping that only escapes regex special chars but preserves spaces

### Technical Details
- Updated `lib/toon_generator.py` (~1100 lines after updates)
- Test results for Data Visualization page:
  - 6 tips (properly deduplicated)
  - 5 best practices (all with full multi-line code)
  - 3 patterns (all with implementation code)
  - 4 resources (with full URLs)
  - TOON size: 11,444 chars

---

## [0.7.0] - 2025-12-13

### Added
- **Custom Documentation-Aware TOON Generator** (`lib/toon_generator.py`)
  - Custom TOON route that processes raw markdown from `NAME_CONTENT_MAP`
  - Achieves **54.7% token reduction** vs llms.txt while preserving all content
  - Full directive awareness (exec, source, kwargs, toc, llms_copy)
  - Features:
    - Section extraction with hierarchical structure (h2-h6)
    - Directive parsing with option extraction
    - Source file embedding with smart code compression
    - Table and list preservation in compact format
    - Exec component detection with callback markers
    - Deduplication of code examples and directives
  - Smart code compression (`compress_code()`) that:
    - Preserves imports, function/class definitions
    - Keeps callback decorators and Input/Output patterns
    - Truncates long files with line count indicator
  - TOON v3.2 format with optimized output:
    - Compact section format: `[level] title`
    - Grouped directives by type
    - Inline table format with pipe separators
    - Key lists extraction for substantial bullet points

### Changed
- **Custom `/<page>/llms.toon` route** in `run.py`
  - Overrides default dash-improve-my-llms TOON for markdown pages
  - Uses raw markdown from NAME_CONTENT_MAP instead of rendered components
  - Processes source directives to embed actual file content

### Fixed
- **TOON content gap issue** - Previous TOON was only capturing 15-20% of documentation content
  - Root cause: dash-improve-my-llms extracts from rendered Dash components, losing directive context
  - Solution: Custom route processes raw markdown with full directive awareness
  - Previous TOON was 185% the size of llms.txt (27,669 chars vs 14,943 chars)
  - New TOON is 45.3% the size of llms.txt (6,965 chars vs 15,369 chars)

### Technical Details
- New module: `lib/toon_generator.py` (698 lines)
  - `generate_documentation_toon()` - Main entry point
  - `build_documentation_toon()` - TOON string builder
  - `extract_sections()` - Hierarchical section parser
  - `extract_directives()` - Directive extractor with options
  - `process_source_directive()` - File content reader
  - `process_exec_directive()` - Component metadata extractor
  - `compress_code()` - Smart code compression
  - `compress_section_content()` - Content summarization
  - `extract_tables()` / `extract_lists()` - Structure extractors

---

## [0.6.0] - 2025-12-13

### Added
- **Enhanced TOON Format v3.1** - Lossless semantic compression with 40-50% token reduction
  - Application context with related pages and multi-page awareness
  - Page purpose explanations with human-readable descriptions
  - Component breakdown with type distribution
  - Human-readable callback descriptions
  - Synthesized page summaries
  - Link categorization (internal vs external)

### Changed
- **Upgraded dash-improve-my-llms from v1.0.0 to v1.1.0**
  - Lossless semantic compression preserves all meaningful content
  - New content extraction: `extract_markdown_content()`, `parse_markdown_content()`
  - Smart compression: `compress_code_example()`, `compress_section_content()`
  - New helper functions: `_generate_page_summary()`, `_format_callback_description()`

### New TOONConfig Options
- `preserve_code_examples=True` - Include code snippets from markdown
- `preserve_headings=True` - Keep section structure
- `preserve_markdown=True` - Extract dcc.Markdown content
- `max_code_lines=30` - Max lines per code example
- `max_sections=20` - Max sections to include
- `max_content_items=100` - Increased from 20

### Documentation
- **Updated AI/LLM Integration Guide** with v1.1.0 TOON enhancements
  - Added design principle: lossless semantic compression
  - Updated token efficiency comparison table
  - Added 6 content gap examples (context, purpose, components, callbacks, summary, navigation)
  - Updated TOONConfig with new v1.1.0 options

### Improved
- Better content preservation in TOON format
- Optimal information density vs token reduction balance
- Enhanced developer experience with richer TOON output

---

## [0.5.0] - 2025-12-13

### Added
- **TOON Format Support** - Token-Oriented Object Notation for 50-60% fewer tokens
  - New `/llms.toon` endpoint for token-optimized LLM documentation
  - New `/architecture.toon` endpoint for token-optimized architecture
  - New `/<page>/llms.toon` per-page TOON format endpoints
  - TOON provides tabular arrays and explicit length markers for LLM validation
  - Ideal for API calls, large apps, and cost-conscious deployments

### Changed
- **Upgraded dash-improve-my-llms from v0.3.0 to v1.0.0**
  - Production-ready release with comprehensive test coverage (88 tests, 98% coverage)
  - New API exports: `TOONConfig`, `toon_encode`, `generate_llms_toon`, `generate_architecture_toon`
  - Zero-change migration: existing code works without modifications

### Documentation
- **Updated AI/LLM Integration Guide** with comprehensive TOON format documentation
  - Added TOON format section with benefits comparison table
  - Added example comparison (markdown vs TOON token usage)
  - Added TOONConfig configuration examples
  - Added programmatic TOON generation examples
  - Updated available routes table with new TOON endpoints
  - Updated key functions reference with new TOON imports

### Improved
- Better AI/LLM documentation organization
- Enhanced developer experience with new format options
- Cost optimization through token-efficient TOON format

---

## [0.4.0] - 2025-11-10

### Added
- **LLM Copy Button Directive** (`.. llms_copy::`)
  - New custom directive that adds a "Copy for llm 📋" button to documentation pages
  - Copies the page's `/llms.txt` URL to clipboard for easy AI assistant sharing
  - Users can paste the URL into ChatGPT, Claude, or other AI assistants for context-aware help
  - Features:
    - Automatic URL construction based on current page path
    - Visual feedback with "✓ Copied! ✓" confirmation
    - Fallback clipboard method for non-HTTPS contexts (HTTP development servers)
    - Works across all modern browsers
    - Tooltip: "Copy llms.txt URL for AI assistants"
  - Implementation:
    - Python directive: `lib/directives/llms_copy.py`
    - JavaScript handler: `assets/llms_copy.js`
    - Uses both modern Clipboard API and legacy `execCommand` fallback
    - Mutation observer for Dash-rendered content detection
  - Documentation updated in Custom Directives guide
  - Added to all 5 example documentation pages

## [0.3.0] - 2025-11-09

### Added - Documentation System
- **Comprehensive Getting Started Guide** (385+ lines)
  - Detailed directive options documentation (`:code: false`, `:defaultExpanded`, `:withExpandedButton`)
  - Interactive examples with best practices
  - File structure examples and patterns
- **Custom Directives Guide** (476 lines)
  - Complete documentation for all 4 directives (toc, exec, source, kwargs)
  - 3 live Python examples (button, counter, form validation)
- **Data Visualization Guide** (465+ lines)
  - 5 chart type examples with full implementations
  - Plotly template integration guide
  - Real-time updates and dashboard patterns
- **Interactive Components Guide** (569 lines)
  - 6 callback pattern examples
  - State management, pattern matching, chained callbacks
  - Loading states demonstration
- **AI/LLM Integration Guide** (577 lines)
  - Complete dash-improve-my-llms documentation
  - SEO optimization strategies
  - Bot management and privacy controls

### Added - Theme System
- **DMC Figure Templates Integration**
  - All Plotly charts now use `dmc.add_figure_templates()`
  - Theme-aware callbacks for 6 chart examples
  - Charts dynamically update with light/dark theme toggle
  - Proper background rendering in both themes
- **Code Block Theming**
  - Theme-aware CSS for markdown code blocks
  - Proper syntax highlighting in light and dark modes
  - Inline code and code block styling
- **Comprehensive Theme Configuration**
  - Professional typography hierarchy (h1-h6)
  - Systematic 4px-based spacing scale
  - 5-level shadow system
  - Consistent border radius system
  - Global component defaults via theme.components
  - Softer black (#1a1b1e) for better contrast

### Added - UI/UX Enhancements
- **Navigation Improvements**
  - Custom page ordering (Getting Started → Custom Directives → AI/LLM → Interactive → Visualization)
  - Better visual hierarchy
  - Organized documentation sections
- **Typography System**
  - Inter font family across application
  - Optimized line heights (md: 1.55 for body text)
  - Proper font sizes (16px base)
  - Font smoothing and text rendering optimization
- **Layout Refinements**
  - Better responsive breakpoints (md for navbar)
  - Improved spacing consistency
  - Enhanced mobile experience
  - Better heading spacing (1.5em top, 0.5em bottom)

### Added - Production Features
- **SEO-Ready HTML Template**
  - Comprehensive meta tags with developer guidance
  - Open Graph and Twitter Card configuration
  - Structured data (Schema.org) for Organization and SoftwareApplication
  - Analytics integration (Google Analytics ready to enable)
  - Favicon configuration with multiple formats
  - Performance optimization (preconnect hints)
  - Search engine verification placeholders
  - Enhanced noscript fallback with styled content
  - 297 lines of documentation and configuration

### Improved
- **15 Working Python Examples**
  - Button interactions, counters, form validation
  - 5 chart types (bar, line, scatter, realtime, dashboard)
  - Callback patterns and state management
  - All examples theme-aware and fully functional
- **Directive System**
  - Fixed kwargs directive to parse component specifications (e.g., `dmc.Button`)
  - Better error handling and fallbacks
  - Support for directive options
- **Code Quality**
  - Fixed JSON serialization error (removed lambda from theme styles)
  - Better import statements
  - Comprehensive inline comments
  - Fixed DMC 2.4.0 compatibility issues

### Changed
- **Better Performance**
  - Optimized theme switching
  - Smooth transitions
  - Better font loading
- **Documentation Organization**
  - Clear learning path
  - Progressive complexity
  - Better code examples

### Fixed
- Import errors in example files (missing dmc, State imports)
- DMC 2.4.0 compatibility (removed unsupported `type` prop from TextInput)
- JSON serialization error in theme configuration
- Heading ID generation with code blocks in markdown
- Theme persistence and switching
- Code block rendering in dark mode

## [0.2.0] - 2025-11-09

### Changed
- **BREAKING**: Migrated from Dash 2.5.0+ to Dash 3.2.0
- **BREAKING**: Migrated from dash-mantine-components 0.14.7 to 2.4.0
- **BREAKING**: Updated all Mantine packages from 7.14.1 to 8.3.6
- Updated Flask from 1.0.4+ to 3.1.2
- Updated Plotly from 5.0.0+ to 6.4.0
- Updated `app.run_server()` to `app.run()` (Dash 3.x standard)

### Removed
- **BREAKING**: Removed deprecated package imports:
  - `dash-html-components` (now part of main `dash` package)
  - `dash-core-components` (now part of main `dash` package)
  - `dash_table` (now part of main `dash` package)

### Fixed
- Replaced deprecated `NotificationProvider` with `NotificationContainer`
- Fixed Mantine version mismatch between package.json and DMC version
- Added node_modules to .gitignore

### Added
- Added package-lock.json for reproducible npm builds
- Comprehensive migration documentation (8 detailed guides)
- Project analysis and assessment documentation
- Persistent theme preference storage using localStorage
- Browser color scheme preference detection on first visit
- Smooth theme transitions without page flash
- AI/LLM & SEO Integration (dash-improve-my-llms v0.3.0)
  - Automatic llms.txt, page.json, architecture.txt generation
  - SEO-optimized sitemap.xml with intelligent priority
  - Bot management (blocks AI training, allows AI search)
  - Structured data for better search indexing
  - Privacy controls for sensitive pages

### Improved
- Better dependency management with cleaner requirements.txt
- Improved code organization with inline comments
- Enhanced theme management system
- Better performance with latest Dash and DMC versions

## [0.1.0] - 2024-11-30

### Added
- Initial release of Dash Documentation Boilerplate
- Markdown-driven documentation system
- Support for light and dark themes
- Responsive design for mobile and desktop
- Docker deployment support
- Interactive code examples with syntax highlighting
- Custom markdown directives:
  - `toc` - Table of contents generation
  - `exec` - Executable Python code blocks
  - `source` - Source code display with syntax highlighting
  - `kwargs` - Component props documentation
- AppShell layout with header, navbar, and responsive drawer
- Search functionality for navigation
- Theme toggle with icon indicators
- Integration with dash-mantine-components (DMC)
- Integration with python-frontmatter for metadata
- Custom CSS styling system
- Docker and docker-compose configuration

### Documentation
- README with getting started guide
- Project structure documentation
- Example documentation pages

---

## Version History Summary

| Version | Date | Dash | DMC | Mantine | Python | Features |
|---------|------|------|-----|---------|--------|----------|
| 1.0.0 | 2026-06-14 | 4.2.0 | 2.7.0 | 8.3.6 | 3.11+ | Pluggable backends (Flask/FastAPI/Quart), dash-improve-my-llms 2.0, TOON removed |
| 0.8.0 | 2025-12-14 | 3.2.0 | 2.4.0 | 8.3.6 | 3.11+ | TOON v3.3, tips/best practices/patterns/resources extraction |
| 0.7.0 | 2025-12-13 | 3.2.0 | 2.4.0 | 8.3.6 | 3.11+ | Custom TOON generator, documentation-aware TOON v3.2 |
| 0.6.0 | 2025-12-13 | 3.2.0 | 2.4.0 | 8.3.6 | 3.11+ | Enhanced TOON v3.1, dash-improve-my-llms v1.1.0 |
| 0.5.0 | 2025-12-13 | 3.2.0 | 2.4.0 | 8.3.6 | 3.11+ | TOON format, dash-improve-my-llms v1.0.0 |
| 0.4.0 | 2025-11-10 | 3.2.0 | 2.4.0 | 8.3.6 | 3.11+ | LLM Copy Button directive |
| 0.3.0 | 2025-11-09 | 3.2.0 | 2.4.0 | 8.3.6 | 3.11+ | Comprehensive docs, theme system, SEO |
| 0.2.0 | 2025-11-09 | 3.2.0 | 2.4.0 | 8.3.6 | 3.11+ | Migration to Dash 3.x, DMC 2.4.0, AI/LLM |
| 0.1.0 | 2024-11-30 | 2.5.0+ | 0.14.7 | 7.14.1 | 3.11+ | Initial release |

---

## Migration Guides

### Migrating to 1.0.0 from any 0.x

This is the major release that moves the boilerplate to Dash 4.x. See the
**Migration notes** under [1.0.0](#100---2026-06-14) for the full checklist.
In short:

1. **Backend:** defaults to Flask — no change required. For FastAPI/Quart,
   `pip install "dash[fastapi]"` (or `[quart]`) and set `DASH_BACKEND=fastapi`.
2. **AI/LLM prose:** add an `LLMS_DOC` string to each page module (or call
   `register_page_metadata(path, llms_doc=...)`); the 2.0 startup warning lists
   pages still missing prose.
3. **dash-improve-my-llms extra:** pick `[flask]` / `[fastapi]` / `[quart]` /
   `[all]` in `requirements.txt`.
4. **Removed APIs:** drop any TOON usage (`TOONConfig`, `toon_encode`,
   `generate_*_toon`), `/page.json`, `/architecture.txt`, and the now-no-op
   `mark_important()` / `mark_component_hidden()` calls — move emphasis into
   `LLMS_DOC` instead.

### Migrating to 0.6.0 from 0.5.0

**Zero changes required!** The upgrade is fully backwards compatible.

Key changes:
1. Update `dash-improve-my-llms` in requirements.txt to `>=1.1.0`
2. TOON output now includes richer, lossless semantic content automatically

Optional new TOONConfig options:
```python
from dash_improve_my_llms import TOONConfig

app._toon_config = TOONConfig(
    # New in v1.1.0:
    preserve_code_examples=True,   # Include code snippets
    preserve_headings=True,        # Keep section structure
    preserve_markdown=True,        # Extract dcc.Markdown content
    max_code_lines=30,             # Max lines per code example
    max_sections=20,               # Max sections to include
    max_content_items=100,         # Increased from 20
)
```

### Migrating to 0.5.0 from 0.4.0

**Zero changes required!** The upgrade is fully backwards compatible.

Key changes:
1. Update `dash-improve-my-llms` in requirements.txt to `>=1.0.0`
2. New TOON endpoints are automatically available:
   - `/llms.toon` - Token-optimized LLM docs
   - `/architecture.toon` - Token-optimized architecture
   - `/<page>/llms.toon` - Per-page TOON format

Optional new features:
```python
# Configure TOON output (optional)
from dash_improve_my_llms import TOONConfig

app._toon_config = TOONConfig(
    indent=2,
    delimiter=",",
    include_metadata=True
)

# Programmatic TOON encoding (optional)
from dash_improve_my_llms import toon_encode
toon_string = toon_encode({"key": "value"})
```

### Migrating to 0.3.0 from 0.2.0

Minor updates, mostly additive. Key changes:
1. Documentation content significantly expanded
2. Chart examples now use DMC figure templates
3. Enhanced SEO features in index.html
4. Better theme integration across all components

### Migrating to 0.2.0 from 0.1.0

Major breaking changes. See migration documentation:

- **Quick Start**: `MIGRATION_README.md`
- **Detailed Guide**: `claude.md`
- **Step-by-Step**: `MIGRATION_CHECKLIST.md`
- **Code Changes**: `CODE_CHANGES_SUMMARY.md`

Key changes to be aware of:
1. Update all imports from `dash_html_components` to `from dash import html`
2. Update all imports from `dash_core_components` to `from dash import dcc`
3. Replace `dmc.NotificationProvider()` with `dmc.NotificationContainer()`
4. Update custom components to use DMC 2.4.0 API
5. Check CSS for any Mantine 8 specific changes

---

## Support

- **Issues**: [GitHub Issues](https://github.com/pip-install-python/Dash-Documentation-Boilerplate/issues)
- **Discussions**: [GitHub Discussions](https://github.com/pip-install-python/Dash-Documentation-Boilerplate/discussions)
- **Dash Community**: [Plotly Community Forum](https://community.plotly.com/)

---

[unreleased]: https://github.com/pip-install-python/Dash-Documentation-Boilerplate/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/pip-install-python/Dash-Documentation-Boilerplate/compare/v0.8.0...v1.0.0
[0.8.0]: https://github.com/pip-install-python/Dash-Documentation-Boilerplate/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/pip-install-python/Dash-Documentation-Boilerplate/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/pip-install-python/Dash-Documentation-Boilerplate/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/pip-install-python/Dash-Documentation-Boilerplate/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/pip-install-python/Dash-Documentation-Boilerplate/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/pip-install-python/Dash-Documentation-Boilerplate/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/pip-install-python/Dash-Documentation-Boilerplate/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/pip-install-python/Dash-Documentation-Boilerplate/releases/tag/v0.1.0
