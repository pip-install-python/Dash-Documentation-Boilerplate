#!/usr/bin/env python3
"""Post-deploy checks against a *live* satellite.

    python scripts/smoke_live.py https://boilerplate.2plot.dev

Everything here fails silently in production if it isn't checked. A wrong
canonical host doesn't error, it deindexes; a stub body doesn't error, it
serves crawlers nothing; a dead peer link doesn't error, it just teaches an
agent that this network's directory isn't worth following.

Run in CD after every deploy, and by hand against any satellite you're
upgrading. Exit code is the number of failed checks, capped at 125.

Only the standard library, so it runs anywhere without an install step.
"""

from __future__ import annotations

import os
import re
import sys
import ssl
import urllib.error
import urllib.request
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Every UA below carries the network's internal-traffic token (the analytics
# point of truth — https://2plot.ai/docs/satellite-analytics, "Internal
# traffic"). A post-deploy battery runs on every push and sweeps every peer in
# the directory; without the token it registers as a burst of visitors, and
# the crawler-shaped probes register as crawler interest. The Googlebot and
# Chrome tokens are still there, so the target exercises exactly the path
# being tested — it just knows the caller is machinery.
try:
    from lib.constants import INTERNAL_UA as _INTERNAL_UA
except Exception:  # pragma: no cover — running outside a repo checkout
    _INTERNAL_UA = "2plot-internal/1.0 (+https://2plot.ai/docs/satellite-analytics)"

CRAWLER_UA = (
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html) "
    + _INTERNAL_UA
)
BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 " + _INTERNAL_UA
)
# `/<page>/llms.txt` negotiates on Accept, not on the User-Agent.
BROWSER_ACCEPT = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
STUB_MARKER = "This page contains interactive content that requires JavaScript"
# Rendered chrome, not the bare class name — a Markdown page may legitimately
# discuss `dv-banner` (this network has one that does); it can never contain
# the element.
CHROME = re.compile(r'<[a-z]+ class="dv-banner')
TIMEOUT = 30


def _ssl_context() -> ssl.SSLContext:
    """Verify certificates via certifi when available.

    macOS Python ships without OS trust-store integration, so bare urllib
    fails every https fetch with CERTIFICATE_VERIFY_FAILED — which reads as
    "the whole site is down" (every check 0s). Same fix as audit_links.py.
    Verification stays ON either way; certifi only supplies the CA bundle.
    """
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


SSL_CONTEXT = _ssl_context()

failures: List[str] = []
checks_run = 0


def fetch(
    url: str, user_agent: str = BROWSER_UA, accept: Optional[str] = None
) -> Tuple[int, str, Dict[str, str]]:
    """Returns (status, body, headers).

    Headers are part of the contract from 2.2.0 on: `/<page>/llms.txt`
    content-negotiates, so which *type* came back is the thing being checked,
    and `Vary` is what stops a CDN handing cached HTML to the next agent.
    """
    headers = {"User-Agent": user_agent}
    if accept is not None:
        headers["Accept"] = accept
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(
            request, timeout=TIMEOUT, context=SSL_CONTEXT
        ) as response:
            body = response.read().decode("utf-8", "replace")
            return response.status, body, dict(response.headers)
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace"), dict(exc.headers or {})
    except Exception as exc:  # noqa: BLE001 - DNS, TLS, timeouts all land here
        return 0, f"{type(exc).__name__}: {exc}", {}


def header(headers: Dict[str, str], name: str) -> str:
    """Case-insensitive header lookup — proxies rewrite the casing."""
    for key, value in headers.items():
        if key.lower() == name.lower():
            return value
    return ""


def check(name: str, passed: bool, detail: str = "") -> None:
    global checks_run
    checks_run += 1
    if passed:
        print(f"  ok    {name}")
    else:
        print(f"  FAIL  {name}" + (f" — {detail}" if detail else ""))
        failures.append(name)


def main(base: str) -> int:
    base = base.rstrip("/")
    host = urlparse(base).netloc
    print(f"Smoke-testing {base}\n")

    # --- 1. The site is up, and llms.txt is the index it should be ---------
    print("Core surfaces")
    status, home, _ = fetch(f"{base}/")
    check("home page responds 200", status == 200, f"got {status}")

    status, llms, llms_headers = fetch(f"{base}/llms.txt")
    check("/llms.txt responds 200", status == 200, f"got {status}")
    check("/llms.txt lists pages", "## Pages" in llms or "# " in llms)
    check("/llms.txt publishes the network directory", "## Network" in llms)

    status, robots, _ = fetch(f"{base}/robots.txt")
    check("/robots.txt responds 200", status == 200, f"got {status}")
    check(
        "/robots.txt points at this host's sitemap",
        f"Sitemap: {base}/sitemap.xml" in robots,
        "sitemap line missing or pointing elsewhere",
    )
    # The artifact fingerprint. pip metadata is invisible from outside, so
    # these robots.txt pairs are how a live host is proven to run the intended
    # dash-improve-my-llms: 2.3.2 allowed OAI-SearchBot; 2.3.3 moved ClaudeBot
    # (the training crawler) to Disallow while allowing the user-triggered and
    # search fetchers Claude-User / Claude-SearchBot.
    robots_lines = robots.splitlines()

    def robots_rule(agent: str) -> str:
        marker = f"User-agent: {agent}"
        if marker not in robots_lines:
            return "(missing)"
        idx = robots_lines.index(marker)
        following = robots_lines[idx + 1: idx + 2]
        return following[0] if following else "(missing)"

    for agent, expected, since in (
        ("OAI-SearchBot", "Allow: /", "2.3.2"),
        ("ClaudeBot", "Disallow: /", "2.3.3"),
        ("Claude-User", "Allow: /", "2.3.3"),
        ("Claude-SearchBot", "Allow: /", "2.3.3"),
    ):
        got = robots_rule(agent)
        check(
            f"/robots.txt {agent} -> {expected.split(':')[0]} ({since} artifact fingerprint)",
            got == expected,
            f"got {got}: this host runs a pre-{since} artifact",
        )

    status, sitemap, _ = fetch(f"{base}/sitemap.xml")
    check("/sitemap.xml responds 200", status == 200, f"got {status}")
    page_urls = re.findall(r"<loc>([^<]+)</loc>", sitemap)
    check("/sitemap.xml lists pages", bool(page_urls), "no <loc> entries")
    foreign = [u for u in page_urls if urlparse(u).netloc != host]
    check("/sitemap.xml stays on this host", not foreign, f"foreign URLs: {foreign[:3]}")

    status, health, _ = fetch(f"{base}/healthz")
    check("/healthz responds 200", status == 200, f"got {status}")

    # --- 2. Canonical host — the failure that deindexes a satellite --------
    print("\nCanonical tags")
    for url in [f"{base}/"] + page_urls[:8]:
        _status, html, _ = fetch(url, CRAWLER_UA)
        found = re.findall(r'rel="canonical"\s+href="([^"]*)"', html)
        check(
            f"canonical on {urlparse(url).path or '/'}",
            len(found) == 1 and urlparse(found[0]).netloc == host,
            f"got {found}",
        )

    # --- 3. No page serves the JavaScript stub ----------------------------
    print("\nCrawler bodies")
    for url in [f"{base}/"] + page_urls[:8]:
        _status, html, _ = fetch(url, CRAWLER_UA)
        check(
            f"real content on {urlparse(url).path or '/'}",
            STUB_MARKER not in html,
            "served the JavaScript stub",
        )

    # --- 4. Content negotiation on llms.txt -------------------------------
    # Production is where this can break in ways development cannot show: a
    # CDN sitting in front of the app is free to ignore `Vary` and serve one
    # cached variant to everyone. Chrome leaking into the Markdown makes every
    # agent in the network pay tokens for decoration and appears in no
    # dashboard; the Markdown leaking into a browser just looks unfinished.
    print("\nContent negotiation")
    check(
        "/llms.txt serves Markdown to a plain request",
        not CHROME.search(llms) and "<!DOCTYPE html>" not in llms,
        "the viewer chrome reached an agent",
    )

    page_doc = next(
        (f"{u.rstrip('/')}/llms.txt" for u in page_urls if urlparse(u).path not in ("", "/")),
        f"{base}/llms.txt",
    )

    status, doc, doc_headers = fetch(page_doc)
    check(f"{urlparse(page_doc).path} responds 200", status == 200, f"got {status}")
    check(
        "agents get text/markdown",
        "text/markdown" in header(doc_headers, "Content-Type"),
        header(doc_headers, "Content-Type") or "no Content-Type",
    )
    check(
        "agents get no viewer chrome",
        not CHROME.search(doc) and "<!DOCTYPE html>" not in doc,
        "the viewer chrome reached an agent",
    )
    check(
        "page document is not a dead end",
        f"{base}/llms.txt" in doc,
        "no route back to the site index",
    )

    status, view, view_headers = fetch(page_doc, accept=BROWSER_ACCEPT)
    check(
        "browsers get text/html",
        "text/html" in header(view_headers, "Content-Type"),
        header(view_headers, "Content-Type") or "no Content-Type",
    )
    check("the viewer renders the network wordmark", "mk-wordmark" in view)
    check(
        "the viewer is noindex",
        bool(re.search(r'<meta[^>]+name="robots"[^>]+noindex', view)),
        "the rendered view would compete with the page it documents",
    )

    # Both variants, because a cache keys on the request that populated it.
    for label, headers in (("markdown", doc_headers), ("html", view_headers)):
        check(
            f"Vary: Accept on the {label} variant",
            "accept" in header(headers, "Vary").lower(),
            f"Vary: {header(headers, 'Vary') or '(absent)'} — a shared cache "
            "may serve this variant to everyone",
        )

    # --- 5. Every peer in the directory resolves --------------------------
    # A directory of dead links degrades quietly, and nothing else will tell
    # you. This is the check most worth having in CD.
    print("\nNetwork directory")
    # `[` `]` `(` are excluded, not just whitespace: the 2.2.0 nav block writes
    # links as `[https://host/llms.txt](https://host/llms.txt)`, and a class
    # that stops only at `)` swallows the label and the opening paren into one
    # malformed URL — which then 404s and fails a perfectly good deploy.
    peer_docs = sorted(set(re.findall(r"https://[^\s()\[\]\"'<>]+/llms\.txt", llms)))
    check("directory lists peer llms.txt URLs", bool(peer_docs), "none found")
    for url in peer_docs:
        if url.startswith(base):
            continue
        status, body, headers = fetch(url)
        # A 200 is not enough. A Dash app answers its catch-all with the SPA
        # shell for *any* unmatched path, so a host that does not serve
        # llms.txt at all still returns 200 text/html — and a status-only
        # check passes on every one of them. Verified on 2plot.dev, where
        # /api/this-endpoint-cannot-exist also returns 200 text/html.
        is_html = "text/html" in header(headers, "Content-Type").lower() or (
            body.lstrip()[:15].lower().startswith("<!doctype html")
        )
        if status != 200:
            check(f"peer reachable: {url}", False, f"got {status}")
        else:
            check(
                f"peer serves a document: {url}",
                not is_html,
                "200, but HTML — that host's catch-all, not an llms.txt",
            )

    print(f"\n{checks_run - len(failures)}/{checks_run} checks passed")
    if failures:
        print("\nFailed:")
        for name in failures:
            print(f"  - {name}")
        return min(len(failures), 125)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
