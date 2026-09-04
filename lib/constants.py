import os

# ---------------------------------------------------------------------------
# Site identity — one string, every surface
# ---------------------------------------------------------------------------
# The network standard (2plot.ai and 2plot.dev both ship it): a site states
# what it is, in the same words, on every surface an agent or a reader can
# reach. The surfaces this brand has to reach, and what serves each:
#
#   Dash(title=SITE_BRAND)              -> <title>, and the fallback identity
#   register_page_metadata(path="/",    -> the /llms.txt H1 and the llms
#       name=SITE_BRAND)                   viewer's brand chip, both via
#                                          dash-improve-my-llms 2.3.4's
#                                          `resolve_site_title`
#   pages/home.md's opening `# ` line   -> the home page's own prose
#
# tests/test_site_identity.py pins all four to this constant, because the
# failure is silent: `resolve_site_title` skips generic candidates ("Home",
# "Index", Dash's default "Dash"), so a site that never states its identity
# publishes a nav label or a framework default and nothing looks broken. That
# is exactly what this host did before — the viewer chip read a bare "Dash".
#
# Naming rules, from the network standard:
#   - the PACKAGE NAME belongs in the description, not in the brand;
#   - "Pip Install Python" is the byline (who made it), never the site name.
SITE_BRAND = "Dash Documentation Boilerplate — the 2plot network's template"

SITE_DESCRIPTION = (
    "dash-documentation-boilerplate — the markdown-driven documentation "
    "template every *.2plot.dev component site is forked from. Interactive "
    "examples, Dash Mantine Components theming, and first-class AI/LLM and "
    "SEO surfaces via dash-improve-my-llms. By Pip Install Python."
)

# Resolves {%title%} in templates/index.html, which is what the served HTML
# carries when dash-improve-my-llms is not rewriting the title per page
# (LLMSConfig(prerender=False), the documented rollback). Per-page titles still
# come from PAGE_TITLE_PREFIX below.
APP_TITLE = SITE_BRAND

# The brand without its tagline. SITE_BRAND is right for a page that has room
# for it; this is for the places that prefix something else and would otherwise
# run past every platform's truncation point.
SITE_SHORT_NAME = "Dash Documentation Boilerplate"

# The two-or-three-word mark in the header, next to the logo. Lives HERE and
# not as a string literal in components/header.py because a fork edits this
# file's identity block and reasonably assumes that's the whole job —
# llms-2plot-dev shipped serving the literal words "Dash Docs" beside its own
# logo because the wordmark was hardcoded in the header (found at its owner
# review, upstreamed in 1.6.8). The header's aria-label derives from this
# too, so the accessible name can never disagree with the visible one.
WORDMARK = "Dash Docs"
# The header's mark, lifted out of components/header.py (1.6.41) so that
# file holds no fork content: the asset under assets/, its box (an SVG
# needs no fixed width — set only what the asset needs), the wordmark
# colour, and the breakpoint the wordmark text appears from.
LOGO_ASSET = "ddb.png"
LOGO_STYLE = {"height": "36px", "width": "36px"}
WORDMARK_COLOR = "#03c7e5"
WORDMARK_VISIBLE_FROM = "xs"

# Prefixed to every per-page title (`pages/markdown.py`, `pages/home.py`), and
# therefore NOT only a browser-tab string: Dash passes the page title straight
# into `og:title` and `twitter:title` (dash/_pages.py `_page_meta_tags`), so
# this is the headline on every share card the site produces.
#
# It read "Dash Pip Components | " until 1.2.2 — the fork source's brand,
# inherited and never changed, so every unfurl of boilerplate.2plot.dev
# advertised a different site while `<title>`, `og:site_name` and the
# /llms.txt H1 all correctly said this one. That is exactly the drift the
# network's identity rule exists to stop, and it is invisible from inside the
# app because nobody sees their own share cards.
#
# Network convention, matching the other satellites (`dash-leaflet2 | `,
# `Dash Email | `): the SHORT site name, then a pipe. Derived rather than
# retyped so the two cannot drift apart; tests/test_site_identity.py pins the
# relationship.
PAGE_TITLE_PREFIX = f"{SITE_SHORT_NAME} | "

PRIMARY_COLOR = "teal"
APP_VERSION = "1.2.5"

# ---------------------------------------------------------------------------
# The network's internal-traffic contract
# ---------------------------------------------------------------------------
# The analytics point of truth is https://2plot.ai/docs/satellite-analytics
# ("Internal traffic"): any request whose User-Agent contains
# INTERNAL_UA_TOKEN is 2plot network machinery talking to itself — the hub's
# hourly health sweep, CI smoke batteries, the 4x-daily heartbeat, this app's
# own server-to-server calls to the hub. It is counted NOWHERE.
#
# Two halves, and both are required for the contract to hold:
#
#   inbound  — every tracker drops a token-carrying request at WRITE time,
#              before device detection and before bot classification, so it
#              never reaches the ledger the hourly rollup is built from;
#   outbound — every call this host makes to another network host sends
#              INTERNAL_UA, so the far side can apply the same rule.
#
# The outbound half is the one that was missing here. lib/ad_client.py fetched
# campaigns from 2plot.dev as bare `python-requests`, which the hub's own
# tracker classifies as a bot — every page view on this satellite was inflating
# 2plot.dev's bot_hits. lib/satellite_reporter.py and lib/hub_client.py had the
# same shape.
#
# The token string must stay byte-identical across the network; it mirrors
# 2plotai/lib/constants.py and pip-docs+/lib/constants.py.
INTERNAL_UA_TOKEN = "2plot-internal"
INTERNAL_UA = "2plot-internal/1.0 (+https://2plot.ai/docs/satellite-analytics)"


def internal_ua(caller: str = "") -> str:
    """``INTERNAL_UA`` with a caller suffix, e.g. ``"ad-client"``.

    The suffix is for reading logs on the far side; only the token matters to
    the contract, and it stays intact whatever the suffix says.
    """
    caller = (caller or "").strip()
    return f"{INTERNAL_UA} {caller}" if caller else INTERNAL_UA


# The fleet probe convention (1.6.44 item 4)
# ---------------------------------------------------------------------------
# A PROBE is machinery fetching a network host to check it: a workflow's
# `curl /healthz`, a smoke battery, a link audit, an anchor check. It is not
# the same shape as `internal_ua()`, which names this app calling a peer
# server-to-server, and the difference is worth a spelling of its own so a
# reader of the far side's logs can tell "a host checking itself" from "a host
# using another host".
#
# The rule, and both halves matter:
#
#   * the string LEADS with a real vendor-or-engine token — Chrome, Googlebot,
#     curl — because dash_improve_my_llms classifies on those tokens and the
#     probe must exercise the same lane the thing it is checking serves;
#   * it is GENERIC-WORD-FREE otherwise. `2plot-monitoring/1` is not a probe
#     UA: measured on dimll 2.9.4, that string classifies `bot_type='monitor'`
#     off the word "monitoring" alone, so a probe named that way changes the
#     document it was sent to measure.
#
# Suppression is the tracker's job, not the UA's: PROBE_UA_SUFFIX carries
# INTERNAL_UA_TOKEN, so `track_visit` and `record_read` drop the row at write
# time. Lane, vendor and class therefore hold BY CONSTRUCTION — measured on
# dimll 2.9.4, appending the suffix moves none of the three:
#
#   Chrome/126 …                     lane=browser bot_type=None        vendor=None
#   Chrome/126 … 2plot-internal/probe lane=browser bot_type=None        vendor=None
#   Googlebot/2.1 …                  lane=crawler bot_type=traditional vendor=googlebot
#   Googlebot/2.1 … 2plot-internal/probe lane=crawler bot_type=traditional vendor=googlebot
#
# `tests/test_internal_traffic.py` re-measures that table rather than trusting
# this comment, because a floor bump is exactly what would move it.
PROBE_UA_SUFFIX = f"{INTERNAL_UA_TOKEN}/probe"


def probe_ua(engine: str, caller: str = "") -> str:
    """A fleet probe UA: ``engine`` token, ``PROBE_UA_SUFFIX``, then ``caller``.

    ``engine`` is required and must be a real vendor-or-engine token; a probe
    with no engine token is classified crawler-lane at dimll >= 2.8 whatever
    it meant, which silently swaps the document under a browser-lane check.

    ``caller`` names which probe this is — ``"network-smoke"``,
    ``"link-audit"`` — for whoever reads the far side's log, exactly as
    ``internal_ua()``'s suffix does. It is not part of the contract: only the
    token is, and the caller tag must never be a generic word (see the
    ``2plot-monitoring`` measurement above). Measured on dimll 2.9.4, a caller
    tag moves neither lane nor vendor on any of the three engines.
    """
    engine = (engine or "").strip()
    if not engine:
        raise ValueError(
            "probe_ua() needs a vendor-or-engine token: a UA carrying only "
            "the internal suffix classifies crawler-lane and changes which "
            "document the probe is answered with"
        )
    caller = (caller or "").strip()
    ua = f"{engine} {PROBE_UA_SUFFIX}"
    return f"{ua} {caller}" if caller else ua


# ---------------------------------------------------------------------------
# Public origin
# ---------------------------------------------------------------------------
# BASE_URL drives <link rel="canonical"> on every page, the absolute URLs in
# sitemap.xml, and the "this app" entry in /llms.txt. It is the single
# highest-consequence value in the template.
#
# THE FOOTGUN: this repo is the template the satellite documentation sites are
# forked from. A satellite that forks it and never changes this value emits
#     <link rel="canonical" href="https://boilerplate.2plot.dev/...">
# on every one of its pages — which tells Google that the entire satellite is
# a duplicate of the boilerplate and asks for it to be dropped from the index.
# Traffic disappears and nothing in the app looks broken.
#
# So: override APP_BASE_URL per deployment. `require_owned_base_url()` below
# refuses to boot in production if you didn't.
DEFAULT_BASE_URL = "https://boilerplate.2plot.dev"
BASE_URL = os.environ.get("APP_BASE_URL", DEFAULT_BASE_URL).rstrip("/")

# ---------------------------------------------------------------------------
# The social card
# ---------------------------------------------------------------------------
# TEMPLATE VALUE: a fork points this at its own image and changes nothing else.
#
# Dash builds `og:image` and `twitter:image` for every page (dash/_pages.py).
# When no `image_url=` is passed it INFERS one from the assets folder, looking
# for `<page>.<ext>`, then `app.<ext>`, then `logo.<ext>` — and this repo ships
# `assets/logo.svg`, so it inferred that. Two separate failures followed, both
# invisible from inside the app:
#
#   1. SVG is not a valid social image. Facebook, Twitter/X, LinkedIn and
#      Slack all reject it, so the card fell back to no image at all;
#   2. it DUPLICATED the og:image already declared in templates/index.html.
#      Two tags, and the scraper picks — usually the last, which was the SVG.
#
# Passing an explicit absolute `image_url` at register_page time resolves both:
# it overrides the inference, and it lets index.html stop declaring the URL
# itself and keep only the auxiliary width/height/alt tags Dash never emits.
#
# THE CARD LIVES ON THE CDN, NOT IN assets/. Network rule, and it is about
# cold starts rather than tidiness: a card served by the app is fetched by the
# scraper at unfurl time, and on a cold free-tier container that request lands
# mid-wake and times out. The preview renders blank ONCE and the platform
# caches the miss — so the first person to share the link poisons it for
# everyone. The CDN has no cold start.
#
# Rendered by `scripts/make_social_card.py` (1200x630 = 1.91:1, the Open Graph
# ideal, which also degrades cleanly into Twitter's 2:1 slot) and uploaded by
# hand to the Cloudflare bucket. There is no automated path to that bucket.
#
# Until 1.2.3 this was `{BASE_URL}/assets/ddb.png` — the app-served 784x741
# logo. Honest dimensions, but near-square: `summary_large_image` letterboxed
# it into a wide slot with bars either side.
#
# The width and height MUST match the file. A declared size that disagrees is
# worse than declaring none, because the platform reserves that box and crops
# into it. `tests/test_social_card.py` pins these against
# `templates/index.html`, and `scripts/smoke_live.py` fetches the real file
# after every deploy and checks its actual pixels against them — the only
# check that can catch the CDN object being replaced with something a
# different shape.
OG_IMAGE_URL = "https://cdn.2plot.ai/github_assets/boilerplate.2plot.dev.png"
OG_IMAGE_WIDTH = 1200
OG_IMAGE_HEIGHT = 630
OG_IMAGE_TYPE = "image/png"
OG_IMAGE_ALT = SITE_BRAND

# The package cross-link block — who publishes this site, and which other
# URLs are the same entity. `SAME_AS` becomes JSON-LD `sameAs` on every
# crawler page: for a docs satellite it should list the documented package's
# GitHub repo and PyPI project — three properties pointing at each other is
# the strongest statement of which URL is a package's canonical docs home.
# A fork sets these once; the other half of the loop (PyPI project_urls and
# the GitHub README pointing back at the docs subdomain) is a per-package
# checklist item, not code.
PUBLISHER = "Pip Install Python LLC"

# ONE constant for the repository. The header's GitHub icon, the footer,
# the Resources block and JSON-LD `sameAs` all read it (1.6.38): a fork
# sets it once. muischeduler's icon pointed at the profile while its
# sameAs named the repo — two truths, one of them wrong.
GITHUB_URL = "https://github.com/pip-install-python/dash-documentation-boilerplate"
SAME_AS = [GITHUB_URL]

# ---------------------------------------------------------------------------
# Navigation contract (1.6.38) — the parts of the sidebar/top bar that are
# IDENTICAL on every host come from template code and these constants; the
# app's own sections come from frontmatter. A fork edits THIS block and its
# docs' frontmatter, never components/navbar.py.
# ---------------------------------------------------------------------------

# The app's own sections, in sidebar order. Every docs page declares
# `category:` in its frontmatter; categories not listed here follow the
# listed ones, alphabetically. Keep names short — they are sidebar titles.
CATEGORY_ORDER = [
    "Getting started",
    "Backends",
    "Content",
    "Network",
    "Auth",
]

# Network-wide community links — identical on every host.
DISCORD_URL = "https://discord.gg/e5s5uHWUHH"
YOUTUBE_URL = "https://www.youtube.com/@2plotai"
YOUTUBE_SUBSCRIBE_URL = YOUTUBE_URL + "?sub_confirmation=1"
DMC_URL = "https://www.dash-mantine-components.com/"

# The upstream project a component wraps — `{"name": ..., "url": ...}` or
# None. Rendered as the last Resources link when declared (MUI X, Leaflet,
# React Flow, React Email, FlexLayout, emoji-mart, Excalidraw, model-viewer,
# Pannellum). The template wraps nothing.
UPSTREAM = None

# Dash component packages whose props the generated /api page documents
# (`["dash_mui_scheduler"]`). Empty → /api is not registered. The version
# badge in the header reads the first entry's __version__.
API_PACKAGES: list = []


# The owner's profile — the FOOTER's GitHub link (the repo is the top bar's).
GITHUB_PROFILE_URL = "https://github.com/pip-install-python"


def resources() -> list:
    """The sidebar's Resources section: THIRD-PARTY ONLY (owner, 2026-08-30).
    `dmc` and, when a fork declares it, the upstream project. The owner's
    own links (repo, Discord, YouTube) live in the top bar and the footer,
    never here; no community.plotly.com; no 2plot.dev (the network is the
    Other Apps menu)."""
    items = [
        {"label": "dmc", "url": DMC_URL, "icon": "ic:baseline-design-services"},
    ]
    if UPSTREAM:
        items.append({"label": UPSTREAM["name"], "url": UPSTREAM["url"],
                      "icon": UPSTREAM.get("icon", "mdi:open-in-new")})
    return items


def require_owned_base_url(base_url: str = BASE_URL) -> None:
    """Fail fast in production when BASE_URL isn't this app's real origin.

    Only enforced when a hosting platform is detected (Render sets ``RENDER``;
    ``APP_ENV=production`` works anywhere else), so local development and the
    test suite are unaffected.

    Two failures are caught:

    1. **APP_BASE_URL unset in production.** A fork inherits the boilerplate's
       default and quietly deindexes itself. There is no safe guess to make on
       its behalf, so this raises.
    2. **A platform-generated hostname.** ``*.onrender.com`` /
       ``*.herokuapp.com`` still resolve after a custom domain is attached, so
       canonicals pointing there split link equity across two hostnames for as
       long as nobody notices.
    """
    in_production = bool(os.environ.get("RENDER") or os.environ.get("APP_ENV") == "production")
    if not in_production:
        return

    if not os.environ.get("APP_BASE_URL"):
        raise RuntimeError(
            "APP_BASE_URL is not set. This app would serve "
            f"<link rel='canonical' href='{DEFAULT_BASE_URL}'> on every page, "
            "telling search engines it is a duplicate of the documentation "
            "boilerplate. Set APP_BASE_URL to this deployment's real origin "
            "(e.g. https://leaflet.2plot.dev)."
        )

    for platform_host in ("onrender.com", "herokuapp.com", "railway.app", "fly.dev"):
        if platform_host in base_url:
            raise RuntimeError(
                f"APP_BASE_URL={base_url!r} is a platform-generated hostname. "
                "Canonical tags, sitemap.xml and llms.txt would all point at it "
                "instead of the custom domain, splitting link equity across two "
                "hosts. Set APP_BASE_URL to the public domain."
            )


# Height of the fixed AppShell header, in px. Consumed by AppShell(header=...)
# and by the mobile drawer, which docks itself directly below the header.
# Change it here only — the two must never drift apart.
HEADER_HEIGHT = 70

# This will be populated by pages/markdown.py when loading documentation files
NAME_CONTENT_MAP = {}
PROPS_TO_EXCLUDE = [
    "unstyled",
    "m",
    "my",
    "mx",
    "mt",
    "mb",
    "ms",
    "me",
    "ml",
    "mr",
    "p",
    "py",
    "px",
    "pt",
    "pb",
    "ps",
    "pe",
    "pl",
    "pr",
    "bg",
    "c",
    "opacity",
    "ff",
    "fz",
    "fw",
    "lts",
    "ta",
    "lh",
    "fs",
    "tt",
    "td",
    "w",
    "miw",
    "maw",
    "h",
    "mih",
    "mah",
    "bgsz",
    "bgp",
    "bgr",
    "bga",
    "pos",
    "top",
    "left",
    "bottom",
    "right",
    "inset",
    "display",
    "flex",
]
