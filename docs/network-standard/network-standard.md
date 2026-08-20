---
name: Network Standard
description: The site-identity rules, the internal-traffic analytics contract and the CI baseline every 2plot satellite copies from this template
endpoint: /network-standard
package: network-standard
icon: mdi:file-certificate-outline
lastmod: 2026-08-19
---

.. llms_copy::Network Standard

.. toc::

### Introduction

The [Multi-Site Networks](/networks) page covers how a family of documentation
sites is wired together so agents can see it as one ecosystem. This page
covers what each site in that family has to *do* to hold up its end.

There are three obligations, and every one of them exists because the failure
it prevents is **silent** — nothing errors, nothing 500s, no dashboard turns
red, and the damage accumulates for months:

| Obligation | The silent failure it prevents |
|---|---|
| **Explicit site identity** | Your site publishes a framework default as its name |
| **The internal-traffic contract** | Your monitoring shows up in someone else's traffic charts |
| **The CI baseline** | A stale artifact serves happily and nobody can tell from outside |

Everything below is already wired up in this template. Fork it and you inherit
it. What you change is listed under each section.

---

### 1. Explicit site identity

A site states what it is, in the same words, on every surface a reader or an
agent can reach.

That sounds like a style rule. It is not — it is a defence against a specific
bug. `dash-improve-my-llms` resolves the `/llms.txt` H1 and the llms viewer's
brand chip through `resolve_site_title(home_page_name, app.title)`. Give it
nothing and it publishes whatever it finds, which on a stock Dash app is the
constructor's default title: the bare string **`Dash`**.

That is what this very host served in production until 2.3.4 landed. Every
agent that fetched `boilerplate.2plot.dev/llms.txt` cold was told the site was
called "Dash". The page rendered perfectly the whole time.

2.3.4 fixed half of it — `resolve_site_title` now *skips* generic candidates
(`Home`, `Homepage`, `Index`, `Main`, `Dash`) and falls through to the next
one — but a package cannot invent a name for you. The other half is stating it.

#### The four surfaces

One constant, `lib/constants.SITE_BRAND`, reaches all of them:

```python
# lib/constants.py
SITE_BRAND = "Dash Documentation Boilerplate — the 2plot network's template"
APP_TITLE = SITE_BRAND
```

```python
# run.py
app = Dash(__name__, title=APP_TITLE, ...)      # <title>, and the fallback

register_page_metadata(                          # the /llms.txt H1 and the
    path="/",                                    # llms viewer's brand chip
    name=SITE_BRAND,
    description=SITE_DESCRIPTION,
)
```

```markdown
<!-- pages/home.md, first line -->
# Dash Documentation Boilerplate — the 2plot network's template
```

...plus `templates/index.html`, where the same string fills `og:site_name`,
`og:title`, `twitter:title`, the schema.org `SoftwareApplication.name` and the
`<noscript>` heading.

#### The naming rules

- The **brand** says what the site *is*. `"dash-leaflet2 — Leaflet 2 maps for
  Dash"`, not `"Documentation"`.
- The **package name** goes in the description, never in the brand.
- **"Pip Install Python" is the byline** — who made it. It is never the site
  name; twenty satellites cannot all be called the same thing.

#### Version claims are derived, never written

The same principle covers the *numbers* a site publishes about itself. Prose
that states a package version writes a placeholder — the distribution name
exactly as it appears on PyPI — and the markdown loaders substitute the
version of whatever is actually installed:

```markdown
Powered by [dash-improve-my-llms](https://pypi.org/project/dash-improve-my-llms/) **{{VERSION:dash-improve-my-llms}}**
```

The placeholder works for **any installed distribution**, so a satellite makes
the same claim about the package it documents — `dash-mui-charts
**{{VERSION:dash-mui-charts}}**` — and a `pip install --upgrade` plus redeploy
updates the browser page, the copy button, `/llms.txt` and every
`/<page>/llms.txt` together. No prose edit, no drift between the docs and the
crawler surfaces. This host served "Powered by 2.3.4" on `/llms.txt` for
months while 2.5.1 ran the site; that class of lie is what the placeholder
retires.

A placeholder naming a distribution that is not installed fails the boot (and
therefore CI) rather than leaking into served prose. Version *floors* in
install instructions (`pip install "pkg>=2.5.1"`) stay literal — they are
requirements, not claims about what is running.

#### What a fork changes

`SITE_BRAND` and `SITE_DESCRIPTION` in `lib/constants.py`, the first line of
`pages/home.md`, the meta tags in `templates/index.html`, and
`EXPECTED_BRAND` in `tests/test_site_identity.py`. That last one is
deliberate: renaming a site should require editing the test that says what it
is called. Anywhere the fork's docs state the documented package's current
version, write `{{VERSION:<its-pypi-name>}}` instead of a number.

---

### 2. The internal-traffic contract

The point of truth is [2plot.ai's satellite-analytics
document](https://2plot.ai/docs/satellite-analytics), section "Internal
traffic". The rule is one sentence:

> Any request whose `User-Agent` contains `2plot-internal` is network
> machinery talking to itself, and is counted **nowhere**.

Health sweeps, CI smoke batteries, the four-times-daily heartbeat, and every
server-to-server call one host makes to another. None of it is a visitor.
None of it is a bot. It simply does not appear.

The contract has two halves and both are required. A host that honours only
the inbound half keeps its own numbers clean while polluting everyone else's.

#### Inbound: drop at write time, before classification

```python
# lib/analytics_tracker.py — the first thing track_visit does
from lib.constants import INTERNAL_UA_TOKEN

if INTERNAL_UA_TOKEN in (user_agent or "").lower():
    return
```

Two details are load-bearing:

- **Before `detect_device_type`, not after.** A health sweep and a CI battery
  both look like bots. Classified first, they land in `bot_hits` and get
  reported to the hub as crawler interest in your documentation.
- **At write time, not read time.** Filtering on the way out leaves rows in the
  ledger that a human reading a local analytics view has to know to discount.

`/healthz` is dropped in the same place, for the same reason: the hub sweeps
it hourly and the hosting platform's own probe hits it far more often.

#### Outbound: every call carries the token

```python
# lib/constants.py
INTERNAL_UA_TOKEN = "2plot-internal"
INTERNAL_UA = "2plot-internal/1.0 (+https://2plot.ai/docs/satellite-analytics)"

def internal_ua(caller: str = "") -> str:
    return f"{INTERNAL_UA} {caller}" if caller.strip() else INTERNAL_UA
```

Everything this app sends to another network host now uses it:

| Caller | Was arriving as | Volume |
|---|---|---|
| `lib/ad_client.py` → 2plot.dev | `python-requests/2.x` | **one per docs page view** |
| `lib/satellite_reporter.py` → 2plot.ai (rollup) | `python-requests/2.x` | one per report interval (default hourly; the fleet runs 15 min) |
| `lib/satellite_reporter.py` → 2plot.ai (presence beacon) | `python-requests/2.x` | one per minute |
| `lib/hub_client.py` → 2plot.dev | `python-requests/2.x` | per agent-key verify |
| `scripts/network_smoke.py`, `smoke_live.py`, `audit_links.py` | crawler / browser UAs | every deploy |

The ad client is the one that mattered. It fetches a campaign server-to-server
on **every single page view**, and `python-requests` matches 2plot.dev's bot
patterns — so this satellite's readers were being charted as bots on the hub.

The battery scripts keep their Googlebot and Chrome tokens *and* append the
internal one: the target still exercises exactly the code path under test, it
just knows the caller is machinery.

The click beacon is the deliberate exception. It is fired by the reader's own
browser, which cannot set a `User-Agent` — and a click is a real person.

#### What a fork changes

Nothing. The token string must stay byte-identical across the network, and
`lib/constants.py`, `lib/analytics_tracker.py`, `lib/ad_client.py`,
`lib/hub_client.py` and `lib/satellite_reporter.py` are copied verbatim.

---

### 3. The CI baseline

pip metadata is invisible from outside a running host. A satellite serving a
two-year-old artifact looks exactly like one serving today's. So the baseline
is built around proving, from the inside and then from the outside, what is
actually deployed.

#### The workflow

`.github/workflows/ci.yml` is a template file. Its shape is the standard:

- `permissions: contents: read` — nothing here publishes, comments or tags.
- `concurrency` with `cancel-in-progress` — a rapid second push does not race
  the first.
- `timeout-minutes` on **every** job. The GitHub default is six hours, which
  is how one hung `curl` burns a day of runner minutes with nobody watching.
- `docker/setup-buildx-action` with `cache-from/to: type=gha` — the real image,
  built the way the platform builds it, without paying full price every run.
- **Version fingerprints asserted inside the image**, not in the runner:

```python
assert parts(version('dash-improve-my-llms')) >= (2, 3, 4)   # resolve_site_title
assert parts(version('gunicorn'))[:2] >= (23, 0)             # CVE-2024-6827, -1135
```

- **A secretless pytest suite.** No `CLERK_*`, no `CROSS_APP_WEBHOOK_SECRET`,
  no `SESSION_SECRET`. The zero-secret boot is itself the first invariant:
  fail-closed behaviour is only provable when nothing is configured.
  `tests/conftest.py` pins each secret to `""` *before* importing `run.py`,
  because `load_dotenv()` runs during that import and a developer's local
  `.env` would otherwise flip the app into a configured posture.
- `.github/dependabot.yml` with a **`dash-network` group**, so a package
  release lands as one reviewable pull request per repo instead of five.
- An **advisory** `pip-audit`. Worth knowing the day a CVE lands; not worth
  anybody's broken build at 2am.

#### The battery

`scripts/network_smoke.py` runs in three seats with the same check names, so a
failure reads identically wherever it happens:

```bash
python scripts/network_smoke.py --base-url http://localhost:8550    # CI container
python scripts/network_smoke.py --base-url https://your.2plot.dev   # after deploy
pytest tests/test_network_smoke.py                                  # in-process
```

It proves identity (`llms_txt_identity` — the H1 is the brand, verbatim), the
artifact (`robots_artifact_fingerprint` — the crawler split that only a
current build emits), that no owner-only surface leaks, that a crawler gets
prose rather than the JavaScript stub, and that agents and browsers get
different content types with a `Vary: Accept` that keeps a CDN from mixing
them.

The in-process seat is not redundant. A script that only ever runs in CI and
after a deploy is exactly the code that rots: a typo turns a check into a
silent pass and the battery keeps reporting green over a broken host.
`tests/test_network_smoke.py` therefore also breaks a check on purpose and
requires it to be reported as a failure.

#### What a fork changes

The block marked `per-site` at the top of `scripts/network_smoke.py` — the
expected H1, the container port, the paths that must 404 — and the matrix and
image name in `ci.yml`. Everything else is the standard; if a check there is
wrong, it is wrong on twenty hosts.

---

### The files a satellite copies verbatim

Each of these is copied as-is; the only edits are the per-site values called
out above.

> `scripts/network_smoke.py` is deliberately **not** inlined on this page. It
> carries the literal stub marker it searches for, and inlining it would put
> that string into this page's prose — where `tests/test_pages.py` reads it as
> this page serving the stub. Read it in the repository instead. That is not a
> footnote: "the document about the check contains the string the check looks
> for" is the same class of bug as the viewer-chrome detection on the
> [Multi-Site Networks](/networks) page, and it is why both checks are worth
> writing narrowly.

| File | Role |
|---|---|
| `.github/workflows/ci.yml` | the CI baseline |
| `.github/workflows/cd.yml` | deploy, then run both batteries against the live host |
| `.github/dependabot.yml` | the `dash-network` update group |
| `lib/constants.py` | `SITE_BRAND`, `INTERNAL_UA`, `internal_ua()` (brand values are per-site) |
| `lib/analytics_tracker.py` | the write-time internal-traffic drop |
| `lib/network_directory.py` | the cross-host peer list |
| `tests/conftest.py` | the secretless boot |
| `tests/test_internal_traffic.py` | proves the exclusion reaches `human_hits` / `bot_hits` |
| `tests/test_site_identity.py` | pins every identity surface (change `EXPECTED_BRAND`) |
| `tests/test_network_smoke.py` | runs the battery in-process |

---

### Checklist for a new satellite

1. Set `SITE_BRAND` and `SITE_DESCRIPTION` in `lib/constants.py`. Brand says
   what the site is; package name in the description; byline is not the name.
2. Set `EXPECTED_BRAND` in `tests/test_site_identity.py` to match.
3. Make the first line of `pages/home.md` `# <brand>`.
4. Update the meta tags and JSON-LD in `templates/index.html`.
5. Set `SITE_H1` and `HIDDEN_DOC_PATHS` in `scripts/network_smoke.py`.
6. Set `APP_BASE_URL` in the deployment environment — see
   [Multi-Site Networks](/networks) for why leaving it at the template's
   default deindexes your site.
7. Set `SATELLITE_APP_KEY` to your own directory key, or your traffic rollups
   overwrite another app's rows at the hub.
8. Add your site to `PEERS` in `lib/network_directory.py`, in the same change
   that ships it — never before, because a dead directory entry teaches an
   agent to distrust the whole list.
9. Run `pytest tests -q` with no secrets set. Green means the posture is right.
