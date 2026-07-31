import os

# The site's own title. Resolves {%title%} in templates/index.html, which is
# what the served HTML carries when dash-improve-my-llms is not rewriting the
# title per page (LLMSConfig(prerender=False), the documented rollback).
# Without it Dash's default — the bare string "Dash" — would ship on every
# page. Per-page titles still come from PAGE_TITLE_PREFIX below.
APP_TITLE = "Dash Documentation Boilerplate"

PAGE_TITLE_PREFIX = "Dash Pip Components | "
PRIMARY_COLOR = "teal"
APP_VERSION = "1.1.0"

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
