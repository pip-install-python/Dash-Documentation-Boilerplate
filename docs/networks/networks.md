---
name: Multi-Site Networks
description: Wire a family of separately-hosted documentation sites together so search engines and AI agents can see them as one ecosystem
endpoint: /networks
package: networks
icon: mdi:lan-connect
lastmod: 2026-07-30
category: Network
order: 2
---

.. llms_copy::Multi-Site Networks

.. toc::

### Introduction

This page is for the case where you run **more than one** app: a hub, a set of
subdomains, some projects on unrelated domains, and dependencies on third-party
documentation. If you run one site on one host, you don't need any of it —
`add_llms_routes(app)` is the whole story, and the [AI/LLM Integration](/examples/ai-integration)
page covers that.

Everything below is already wired up in this boilerplate. Fork it and you
inherit the wiring; what you have to change is *one value*, and the last
section explains why getting it wrong is the most expensive mistake available
in this template.

---

### The problem: every SEO surface is scoped to one origin

Each thing the package serves stops at the host boundary, by design:

| Surface | Scope |
|---|---|
| `sitemap.xml` | Its own origin only — that's the sitemap spec, not a limitation to work around |
| Internal prose links | Within the app |
| `robots.txt` | One host |

So a network of a dozen hosts is a dozen disconnected islands. Nothing in any
of them says the other eleven exist.

The consequence differs by audience, and the second one is the expensive one:

- **Search engines** treat cross-host links as weak signals, but they do have
  crawlers that follow them. Given enough time and inbound links, Google finds
  your subdomains.
- **Agents don't crawl.** A model answering a question about your ecosystem
  fetches one or two URLs and reasons from what comes back. If it lands on
  `leaflet.2plot.dev`, it sees one library. There is no second request, no link
  traversal, no accumulation over time. Whatever that one response says *is*
  the ecosystem, for that answer.

Fixing it needs an explicit, machine-readable statement of the relationships,
served from **every** host.

---

### The three tiers

`register_network()` takes three lists, and keeping them distinct is the point
— collapsing them would either overclaim ownership of other people's sites or
bury your own network in an undifferentiated pile of links.

#### `peers` — same network, same operator

The hosts you own that are genuinely one product family. Peers get
`<link rel="related">` tags in `<head>`, a `## Network` section in `/llms.txt`,
and **followed** links in the prerendered body. This is the tier that builds
the cross-host graph you actually own, so put real relationships here and
nothing else.

#### `affiliated` — yours, on its own domain

Projects you built on domains that aren't part of the primary brand. Listed
under `## Related projects` with followed links. Separating these from `peers`
is what lets an agent answer *"what is the 2plot network?"* without sweeping in
every unrelated domain you happen to own — while still being able to answer
*"what else has this author built?"*.

#### `external` — third-party references

Documentation you depend on or point readers at. **Not yours.** Listed under
`## External references` and emitted with `rel="nofollow noopener"` — they are
references, not endorsements, and shouldn't pass ranking signal. Point at the
machine-readable URL when one exists:

```python
external=[
    {"name": "Dash Mantine Components",
     "url": "https://www.dash-mantine-components.com",
     "description": "The UI component layer these docs are built with.",
     "llms_txt": "https://www.dash-mantine-components.com/llms.txt"},
]
```

---

### One definition, imported everywhere

The peer list lives in `lib/network_directory.py` — **one file, copied verbatim
into every satellite**, not twelve hand-edited variants. A directory that
disagrees with itself across hosts is worse than no directory: an agent that
gets two different answers about the same network learns to trust neither.

.. source::lib/network_directory.py

Two details in there that are easy to get wrong:

1. **`peers_for()` filters the app's own URL out.** A site listing itself as
   its own peer reads as generated rather than curated, and burns a slot in a
   list a reader may only skim.
2. **`apply()` degrades instead of failing** when the installed
   `dash-improve-my-llms` predates 2.1. Losing the directory is a degradation;
   refusing to boot over it is not proportionate.

Only list hosts that are **actually live**. An entry pointing at a subdomain
with no site is a dead link an agent follows once, and then discounts the rest
of your list. Add a subdomain in the same change that ships it.

---

### The wordmark

The same module carries the network's mark, drawn in the header of the
rendered `llms.txt` view:

```python
WORDMARK = {
    "morse": "plot",
    "prefix": "2",
    "suffix": "ai",
    "label": "2plot.ai",
}
```

`"2"` + the morse encoding of `plot` drawn as columns of dots and dashes +
`"ai"`. There is deliberately **no period glyph**: the morse block already
separates the halves, and a literal `.` beside it reads as punctuation dropped
into a graphic. The renderer turns a suffix ending in `i` into an upward
flourish, so `"ai"` draws as `a` plus that mark, and `label` carries the real
domain for screen readers and the SVG `<title>` — which is the one place the
dot belongs.

It renders as self-contained inline SVG: no external fonts, no image requests,
no script, because it lands in a documentation page that has to work behind any
CSP. Like the peer list, it lives in this module rather than per-app, which is
what keeps one mark across the network instead of twelve near-identical ones.

### The bulletin

`configure_bulletin(url=...)` points an app at a hub-published JSON document of
tips and announcements, rendered in the same header — so a twenty-site network
says "here is what changed" once instead of in twenty repositories.

This boilerplate ships it **commented out** in `run.py`, and a satellite should
too until the hub actually serves the endpoint. It is opt-in by design: with no
call, the package makes no outbound requests at all. When it is enabled, the
fetch happens on a daemon thread behind a TTL cache, so a request never blocks
on it and a dead endpoint degrades to "no bulletin" rather than a 500.

---

### Wiring it into a satellite

In `run.py`, before `add_llms_routes(app)`:

```python
from lib.constants import BASE_URL, require_owned_base_url
from lib import network_directory

require_owned_base_url()
app._base_url = BASE_URL
network_directory.apply(BASE_URL)

add_llms_routes(app, LLMSConfig(warn_missing_llms_doc=True))
```

Order matters: the package reads the registered directory when it builds
`/llms.txt` and the prerendered HTML, so registration has to happen first.

Leave `warn_missing_llms_doc=True` on. It names every page with no prose, which
is exactly the list of pages that serve a stub body to crawlers. Turning it off
doesn't fix anything — it hides the to-do list. If a page genuinely shouldn't be
indexed, `mark_hidden()` it; hidden pages are excluded from the warning by
design.

---

### The one value you must change

`BASE_URL` drives `<link rel="canonical">` on every page, the absolute URLs in
`sitemap.xml`, and the "this app" entry in `/llms.txt`.

A satellite forked from this template that never changes it emits:

```html
<link rel="canonical" href="https://boilerplate.2plot.dev/some-page">
```

…on every one of its own pages. That tells Google the entire satellite is a
duplicate of the boilerplate and asks for it to be dropped from the index.
Traffic disappears, and **nothing in the app looks broken** — which is why this
is the highest-consequence footgun in the template and why it gets a guard
rather than a comment.

So `lib/constants.py` reads the origin from the environment, and
`require_owned_base_url()` refuses to boot in production if you left it at the
default:

```python
DEFAULT_BASE_URL = "https://boilerplate.2plot.dev"
BASE_URL = os.environ.get("APP_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
```

Set `APP_BASE_URL` in your host's environment (Render → Environment →
`APP_BASE_URL=https://yoursite.2plot.dev`) and change `DEFAULT_BASE_URL` to
your own domain while you're forking.

The guard also rejects platform-generated hostnames — `*.onrender.com`,
`*.herokuapp.com`, `*.fly.dev`. Those keep resolving after you attach a custom
domain, so canonicals pointing at them split link equity across two hosts for
as long as nobody notices. This is not hypothetical: one satellite in this
network shipped with `dash-pannellum.onrender.com` as its canonical host and
spent months telling search engines its `2plot.dev` URLs were the duplicates.

---

### One URL, two audiences

From 2.2.0 on, `/<page>/llms.txt` content-negotiates. Agents, crawlers, curl
and link unfurlers get the Markdown byte for byte; a browser gets it rendered
behind the header described above. `?raw=1` forces Markdown, `?format=html`
forces the view, and both variants send `Vary: Accept` so a CDN cannot hand
cached HTML to the next agent.

The document also opens with a navigation block — the site index, the network
index one level up the hub chain, and the sitemap. Before that, a page's
`llms.txt` was a dead end: it described one page and gave an agent nothing to
follow, which matters because an agent fetches a URL rather than crawling from
one.

Nothing to configure. But two things are worth checking on a satellite, because
both fail silently:

- **The viewer's chrome must never reach a plain fetch.** If it does, every
  agent in the network pays tokens for decoration and it appears in no
  dashboard.
- **Any route you add must not shadow `/<page>/llms.txt`.** Mount custom routes
  *before* `add_llms_routes`, as `lib/asgi_routes.py` does. A custom handler on
  that path swallows both surfaces at once.

### Verifying a deployment

Six checks worth running after every deploy — all of these failures are silent
and expensive:

```bash
APP=https://yoursite.2plot.dev

# 1. Canonical must point at THIS host.
curl -s $APP/ | grep -o 'rel="canonical" href="[^"]*"'

# 2. No page may serve the JavaScript stub.
curl -s -A "Googlebot/2.1" $APP/ | grep -c "requires JavaScript"   # expect 0

# 3. The directory is published.
curl -s $APP/llms.txt | grep -A3 "## Network"

# 4. Every peer llms.txt in the directory resolves.
curl -s $APP/llms.txt | grep -oE 'https://[^ ]+/llms\.txt' | sort -u \
  | while read -r u; do printf "%s %s\n" "$(curl -s -o /dev/null -w '%{http_code}' "$u")" "$u"; done

# 5. Agents get Markdown; the viewer's chrome must not leak into it.
curl -sI $APP/networks/llms.txt | grep -i 'content-type\|vary'   # text/markdown, Vary: Accept
curl -s $APP/networks/llms.txt | grep -c 'dv-banner'             # expect 0

# 6. Browsers get the rendered view.
curl -s -H 'Accept: text/html' $APP/networks/llms.txt | grep -c 'mk-wordmark'   # expect 1
```

Checks 4 and 5 are the ones worth automating: a directory of dead links and
chrome leaking to agents both degrade quietly, and nothing else will tell you.
This repo runs all six against the live deployment via
[`scripts/smoke_live.py`](https://github.com/pip-install-python/Dash-Documentation-Boilerplate/blob/main/scripts/smoke_live.py)
in `.github/workflows/cd.yml` after every release.
