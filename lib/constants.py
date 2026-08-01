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

PAGE_TITLE_PREFIX = "Dash Pip Components | "
PRIMARY_COLOR = "teal"
APP_VERSION = "1.2.0"

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
