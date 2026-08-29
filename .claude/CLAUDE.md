# Dash Documentation Boilerplate

## Project Overview

This project is a modern documentation boilerplate for Dash applications,
providing a markdown-driven documentation system with interactive examples,
comprehensive theming, and AI/LLM integration. It is the template that the
`*.2plot.dev` component documentation sites are forked from.

Versions, dependencies and history are deliberately not restated here — they go
stale. Read `requirements.txt` for the stack and `CHANGELOG.md` for what
changed and when.

---

## Custom Directives

| Directive | Syntax | Purpose |
|-----------|--------|---------|
| `toc` | `.. toc::` | Generate table of contents |
| `exec` | `.. exec::module.path` | Render Python component |
| `source` | `.. source::file/path.py` | Display source code |
| `kwargs` | `.. kwargs::ComponentName` | Show component props |

Options are documented in `docs/directives/directives.md`.

---

## Configuration

### Customization Points

| File | Purpose |
|------|---------|
| `lib/constants.py` | App-wide constants (colors, titles) |
| `assets/main.css` | Custom CSS styles |
| `templates/index.html` | HTML template (analytics, meta tags, SEO) |
| `components/appshell.py` | Theme configuration, MantineProvider settings |
| `components/navbar.py` | Navigation ordering and organization (incl. the full-height mobile drawer — the network-standard mobile nav) |
| `pages/control_board.py` | `/admin/control-board` — live per-page tier + llms.txt toggles (owner/admin-gated, fails closed) |
| `lib/page_visibility.py` | The board's override store (persists to `PAGE_VISIBILITY_FILE`; overrides beat frontmatter in `lib/access.py`) |
| `lib/auth_demos.py` | Live-demo teasers rendered inside the sign-in gate cards |

---

## Development Notes

### Adding New Documentation Pages
1. Create folder in `docs/` (e.g., `docs/my-component/`)
2. Create markdown file with frontmatter:
```markdown
---
name: My Component
description: Description of my component
endpoint: /components/my-component
icon: mdi:code-tags
---

.. toc::

## Overview
...
```
3. Add Python examples as needed
4. Reference with `.. exec::docs.my-component.example`
5. Page will auto-register and appear in navigation

### Creating Theme-Aware Charts
1. Import `dmc.add_figure_templates()`
2. Register templates at module level
3. Create callback with `Input("color-scheme-storage", "data")`
4. Use ternary to select template: `"mantine_dark" if theme == "dark" else "mantine_light"`
5. Recreate figure with template parameter

---

## Resources

- [Dash Documentation](https://dash.plotly.com/)
- [Dash Mantine Components](https://www.dash-mantine-components.com/)
- [Mantine](https://mantine.dev/)
- [dash-improve-my-llms](https://pypi.org/project/dash-improve-my-llms/)
- [Project Repository](https://github.com/pip-install-python/Dash-Documentation-Boilerplate)
- [dmc-docs Inspiration](https://github.com/snehilvj/dmc-docs)
- [Plotly Community Forum](https://community.plotly.com/)

---

## Network role & the behavioral contract

This repo is a member of the 2plot network — either the template
itself (dash-documentation-boilerplate) or a fork of it serving one
component's documentation. **Identity derives from the repo, never
from this file**: the app key comes from `SATELLITE_APP_KEY` and
run.py's fork point, the host from `lib/constants.py`'s `BASE_URL`,
the deliberate differences from the template from `DIVERGENCES.md`
at the repo root. If those disagree with anything written here,
they win.

### The contract — every session, every prompt

1. **Check the prompt against this tree before executing.** Prompts
   are written from the template's perspective and your fork may
   legitimately differ — floors, backends, payload shapes, page
   sets. A prompt step that doesn't fit this repo is a finding to
   return, not an instruction to force.
2. **Corrections are your job, not scope creep.** If a prompt's
   reference list doesn't match its steps, if its assumed state is
   wrong, or if executing it as written would produce a
   green-but-vacuous result, say so and propose the corrected
   version before running it.
3. **Verify your own deploy on the wire before reporting.** A push
   is not a result. Run `/wire-verify` (or its manual equivalent)
   against production and paste what came back. If your sandbox
   cannot reach your own domain, say exactly that — an unverified
   claim marked as unverified is honest; the same claim unmarked is
   not.
4. **Report observed versus expected, with evidence.** Paste the
   JSON, the status code, the test count. "Should work" and summary
   claims without artifacts are not reports.
5. **Divergence is legitimate when written down.** Before syncing
   template changes, read `DIVERGENCES.md`; never let a sync
   "restore" a recorded deliberate difference. When you deliberately
   diverge, record it there in the same commit — an unrecorded
   divergence is indistinguishable from drift and will be treated
   as drift.
6. **Never touch**: environment variable VALUES, hosting dashboards,
   secrets, other repos' trees, or anything the prompt didn't put in
   scope. Enumerate what you cannot do (closing PRs, dashboard
   steps) for the owner instead of claiming it done.

### Verification traps (fleet-learned, keep them)

- A `>=` floor can never pull a new release through a Docker cache
  hit — the requirements line changing IS the cache bust, and floors
  live in several encodings (requirements, run.py's boot floor,
  tests, CI): grep the number, move every one.
- `/healthz` build == HEAD is the deploy proof; a missing geo block
  on dimll ≥2.7 means the cache trap fired (unless DIVERGENCES.md
  says this host's healthz is deliberately minimal).
- Always GET, never HEAD — and the mechanism, measured 2026-08-27
  after two rounds of wrong diagnoses: on the ASGI backends HEAD is
  answered by NOTHING AT ALL. Werkzeug derives a HEAD rule from
  every GET rule; FastAPI's `APIRoute` does not, so a route declared
  `@router.get(...)` returns 405, and every ASGI host in the network
  was 405ing HEAD on every route — `/healthz`, `/robots.txt`,
  `/sitemap.xml` included. Get the LAYER right (corrected 1.6.33,
  after this text and two seats' drops all said "Starlette", and
  three probes went looking in the wrong package):
  `starlette.routing.Route` DOES add HEAD wherever GET is present —
  `self.methods.add("HEAD")`, the same courtesy Werkzeug does — and
  FastAPI's `APIRoute` is the one that takes `methods` literally.
  A HEAD probe therefore tells you about
  the router's method table and never about the document. GET is
  never wrong, which is the whole reason to have one rule.
  Do NOT "verify" the trap on one host and conclude HEAD is fine:
  excalidraw measured twice and was right about its own Flask host
  and wrong about the fleet. Do not verify it on `HEAD /` either —
  a crawler-UA `HEAD /` is answered by the prerender middleware
  before routing, so it returns 200 on a host that 405s everything
  else, and that one case is how this repo's 1.6.31 in-process
  probe cleared the app code. Earlier text here said the ASGI hosts
  DROP the `Link` headers on HEAD: a 405 carries no `Link`, so the
  observation was true and the diagnosis was not. Fixed in the
  template at 1.6.32 (a HEAD→GET ASGI middleware, because the
  package's own adapter declares its routes GET-only); the fleet's
  two ASGI forks consume it as spec item 11, and the hub plus four
  second-ring hosts had the same defect — if you serve a non-Flask
  backend, assume you have it until you have probed a route that is
  NOT `/`. The middleware stays after dimll 2.7.2 fixes the
  package's own routes: `/` is Dash's page catch-all and every Dash
  route is an `APIRoute` too.
- Any throwaway Python probe a session writes against a production
  host needs the certifi SSL context AND a retry guard. Fixing the
  shipped tools does not cover the next ad-hoc script: the template
  seat hit `CERTIFICATE_VERIFY_FAILED` in a hand-written CD watcher
  one hour after shipping that exact fix inside both live tools,
  and the ops seat hit it plus an `IncompleteRead` on a chunked
  response in the same session. It is a seat habit, not a repo
  contract, which is what this file is for.
- Run-watchers keyed on a commit sha can match Dependabot's runs on
  the same sha — key on the workflow path (cd.yml) instead.
- The browser lane and the machine lane are different documents;
  a fix proven on one is unproven on the other.
- SUPERSESSION: cd.yml's build-match wait cannot tell "not deployed
  yet" from "already replaced" — both look like a live build that
  is not the sha it wants. A bot-merged PR (any GITHUB_TOKEN merge)
  is one road in: it lands with ZERO workflow runs on the merge sha
  (anti-recursion) yet still reaches production, because the deploy
  hook builds branch HEAD — so an in-flight CD run ships the merge
  while its own wait holds out for the superseded release sha
  (observed live on 4a1d430, 2026-08-25). It is NOT the only road,
  and taking the bot actor off main does not close the class: two
  human pushes inside one deploy window, or hook dispatch lag,
  produce exactly the same state. Since 1.6.25 the wait fails FAST
  when the live build is a DESCENDANT of the wanted sha (compare
  API) instead of going red at timeout — that is the diagnosis, and
  it works whoever merged. The policy — actions PRs: human merge
  when green, never a bot actor on main — removes the most common
  road, not the trap.
- Anonymous api.github.com is 60 requests/hour. With no `gh` and no
  token, read a run ONCE after CI's own jobs report complete — a
  blind 20 s poll loop spends the whole budget reading rate-limit
  bodies as "not done yet" (modelviewer, 2026-08-26).
- A GitHub API JSON body WITHOUT the field you asked for
  (`workflow_runs` absent, not empty) is a rate-limit error body,
  never an empty result — check the field exists before trusting
  the answer.
- `git fetch` before any audit: the fan-out pushes to these repos
  now, and a checkout current yesterday is 2–3 merges behind
  origin/main today (three pilot sessions, same day, 2026-08-26).
- A failed STEP is not a failed RUN. A job with
  `continue-on-error: true` (pip-audit here) reports its step red
  and the RUN still concludes `success`; the reverse also bites —
  a green-looking job list under a run whose conclusion is
  `failure`. Read the run's `conclusion`, then the annotations;
  never infer either one from the other.
- Never round-trip JSON through zsh `echo` — it interprets the
  `\n` inside a multi-line commit message and hands the parser
  real control characters (a broken API read on the template, then
  the same hour on the ops seat). Pipe curl straight into
  `python3`, or use `printf '%s'`.
- Repeated HTTP headers survive only if you keep them: both
  `dict(resp.headers)` and `{k: v for k, v in resp.headers.items()}`
  keep the LAST value per name, and dimll emits several `Link`
  headers (muicharts, 2026-08-26). Iterate the items, or ask for
  `resp.headers.get_all(name)`; in curl, `-D -` and read the raw
  block.
- Name the crawler UA when you probe the machine lane. Which
  document a host serves is decided by the package's UA
  classification, not by the absence of a UA: on the template
  today, curl's default `curl/8.x` receives the SAME crawler
  document as Googlebot (18,779 bytes, byte-identical) while a
  Chrome UA gets the 148 KB app shell. One host (muicharts) reported
  a UA-less probe classified the other way; treat that as
  UNCONFIRMED — muischeduler filed the same observation and then
  RETRACTED it (its report had the two documents swapped), leaving
  one unreproduced sighting, and a trap carrying an unreproducible
  fact spends somebody's afternoon. The advice does not depend on
  it: either lane can be the one you did not mean to test, so send
  `-A "<a real crawler UA>"` and confirm from the body which
  document came back.
- There is ONE classifier: `dash_improve_my_llms.classify()`. Never
  add a User-Agent list to this app — the tracker had one for a year
  (`lib/analytics_tracker.py`, until 1.6.34), it filed ClaudeBot as
  *search* (it is Anthropic's training crawler; the package's registry
  and this repo's own `run.py` comment both said so six lines from
  where the list ignored them), it still named the retired
  `anthropic-ai` / `claude-web` tokens, and it counted every UA-less or
  library client as a human. Every host in the fleet reported those
  numbers. A token the registry lacks is a pushback to the package
  seat, not a list here; `tests/test_analytics_classifier.py` greps the
  module for the old tokens and goes red if one comes back.
- `build == HEAD` on `/healthz` means HEAD of **`release`**, not main
  (1.6.35). Render deploys `release`; only cd.yml's `deploy` job writes
  it, fast-forward, after the CI matrix is green. `main` ahead of
  `release` is an uncertified push pending — its CD run is red or still
  running — never "drift" and never a reason to deploy by hand or to
  write `release` yourself (a non-fast-forward push fails the next run
  on purpose). Compare the wire against `git rev-parse origin/release`;
  the one measurement behind this: 2026-08-29 14:12Z, de0bcff pushed
  to main, built by Render inside the minute, red in CD at 14:13Z,
  served for ~6 minutes. A host whose DIVERGENCES.md posture fence has
  no `deploy:` key still watches main — there the trap is the old one.
