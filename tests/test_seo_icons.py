"""dimll 2.6.0's SEO honesty features, pinned from the app's side.

Two contracts land with the 2.6.0 floor:

1. **Icon discovery agrees with the declaration.** This app still declares
   `configure_seo(icons=[...])` explicitly (declared wins), but the fleet's
   satellites will increasingly rely on discovery alone — so the reference
   host proves the two produce the SAME set. Set-equality, not order: the
   release notes are explicit that discovery orders differently
   (.ico first, biggest square descending, apple-touch last) and that
   order-inequality is not a failure.

2. **The sitemap tells the truth or says nothing.** `<lastmod>` is emitted
   verbatim from frontmatter `lastmod:` and omitted when unset. No date in
   the sitemap may exist that no page declared — the invented daily "today"
   is the exact lie 2.6.0 exists to end.

3. **HEAD PARITY (1.6.30).** The BROWSER head — templates/index.html's static
   links plus Dash's own — declares the same icons as `configure_seo(icons=)`,
   which is what the CRAWLER head carries. Measured across the fleet in
   2026-08 (emojimart, re-spot-checked by the ops seat): six of seven audited
   hosts disagreed on icons, and the browser side was the poor one — usually
   missing 512x512 and often 192x192, the sizes Google prefers. One inherited
   edit, six hosts. smoke_live.py compares the two heads ON THE WIRE, but by
   the SET OF SIZES, so an .ico href pointing at a different path than the
   declaration is invisible there (an .ico declares no size); this offline pin
   compares (rel, href, sizes) triples and is the half that can see it. It
   caught exactly that on the template itself.
"""

from __future__ import annotations

import re
from pathlib import Path


def _normalize(entries):
    """(rel, href, sizes) triples from the package's mixed icon shapes."""
    out = set()
    for e in entries:
        if isinstance(e, str):
            out.add(("icon", e, None))
        else:
            out.add((e.get("rel", "icon"), e["href"], e.get("sizes")))
    return out


def test_discovery_agrees_with_the_declared_icons(app):
    from dash_improve_my_llms.seo import _config, discover_icons

    declared = _normalize(_config.icons or [])
    discovered = _normalize(discover_icons(app))

    assert declared, "configure_seo(icons=) is no longer declared in run.py?"
    assert discovered, "discovery found nothing in assets/ — pattern drift?"
    assert declared == discovered, (
        "Declared and discovered icon sets diverged.\n"
        f"declared only:   {sorted(declared - discovered)}\n"
        f"discovered only: {sorted(discovered - declared)}\n"
        "If a favicon file was added/renamed, update run.py's icons list — "
        "or if discovery's patterns changed upstream, this is the canary."
    )


def _head_icons(html: str) -> set:
    """(rel, href, sizes) triples from a served <head>.

    Query strings are stripped: Dash injects its own favicon link with a
    cache-busting `?m=<mtime>` (the `{%favicon%}` placeholder), and that one
    link is not a declaration anybody authored — under this normalization it
    collapses onto whichever .ico the app already declares instead of
    reading as a phantom eighth icon.
    """
    out = set()
    for link in re.findall(r'<link[^>]+rel="(?:icon|apple-touch-icon)"[^>]*>', html):
        rel = re.search(r'rel="([^"]+)"', link).group(1)
        href = re.search(r'href="([^"]+)"', link).group(1).split("?")[0]
        sizes = re.search(r'sizes="([^"]+)"', link)
        out.add((rel, href, sizes.group(1) if sizes else None))
    return out


def test_the_browser_head_declares_the_configured_icons(client):
    """Head parity, offline (1.6.30).

    `configure_seo(icons=)` is the CRAWLER head's icon set — the static
    document dash-improve-my-llms serves a bot. templates/index.html is the
    BROWSER head's. Nothing but this pin holds them together, and across the
    fleet they had drifted on six of seven audited hosts: the browser head
    lacking 512x512, often 192x192 too, while the crawler head declared
    both. A browser that never sees the big square gets the small one
    upscaled on a home screen; a fork that trusted the wire-side parity
    check saw nothing, because it compares sizes and the difference here can
    be a bare href.
    """
    from dash_improve_my_llms.seo import _config

    declared = _normalize(_config.icons or [])
    served = _head_icons(client.get("/").text)

    assert declared, "configure_seo(icons=) is no longer declared in run.py?"
    assert served, "the browser head declares no icons at all"
    assert served == declared, (
        "The browser head and the crawler head declare different icons.\n"
        f"browser only: {sorted(served - declared)}\n"
        f"crawler only: {sorted(declared - served)}\n"
        "Both heads are edited by hand in different files — templates/"
        "index.html and run.py's configure_seo(icons=). Make the hrefs "
        "agree exactly; a byte-identical file at another path is still a "
        "different declaration."
    )


def _declared_lastmods() -> set[str]:
    dates = set()
    for md in Path("docs").glob("**/*.md"):
        head = md.read_text().split("---")[1] if md.read_text().startswith("---") else ""
        m = re.search(r"^lastmod:\s*(\d{4}-\d{2}-\d{2})\s*$", head, re.MULTILINE)
        if m:
            dates.add(m.group(1))
    # Generated pages declare theirs from their SOURCE (1.6.41): /changelog's
    # is the newest dated release heading in CHANGELOG.md, /api's the
    # committed extract's `generated` stamp — both move exactly when the
    # content moves, which is what "declared" means here.
    try:
        from pages.changelog import newest_date

        if newest_date():
            dates.add(newest_date())
    except Exception:  # noqa: BLE001 — no changelog page on this fork
        pass
    try:
        from lib import api_reference
        from lib.constants import API_PACKAGES

        for pkg in API_PACKAGES:
            stamp = api_reference.slim_generated_on(pkg)
            if stamp:
                dates.add(stamp)
    except Exception:  # noqa: BLE001
        pass
    return dates


def test_sitemap_lastmod_is_verbatim_or_absent(client):
    sitemap = client.get("/sitemap.xml").text
    emitted = re.findall(r"<lastmod>([^<]+)</lastmod>", sitemap)
    declared = _declared_lastmods()

    assert emitted, (
        "No <lastmod> anywhere — the frontmatter stamps were removed? "
        "Truth-or-silence allows silence per page, but the docs set "
        "deliberately declares real dates."
    )
    undeclared = [d for d in emitted if d not in declared]
    assert not undeclared, (
        f"Sitemap emits dates nobody declared: {undeclared} — an invented "
        "date is the lie that gets the whole sitemap discarded."
    )

    # The home page declares no lastmod; its <url> entry must carry none.
    home_block = re.search(
        r"<url>\s*<loc>[^<]*?://[^/<]+/</loc>.*?</url>", sitemap, re.DOTALL
    )
    assert home_block and "<lastmod>" not in home_block.group(0), (
        "The home page's sitemap entry carries a lastmod it never declared."
    )


def test_apple_touch_icon_is_opaque():
    """iOS composites the icon's alpha onto ITS OWN background — black on
    some surfaces, white on others — so a transparent apple-touch icon
    renders differently everywhere it appears. scripts/make_favicons.py
    flattens exactly this one file onto opaque white (every other size
    keeps its alpha; browsers and Android handle it correctly).

    Read the colour type straight out of the PNG header — stdlib only, no
    Pillow in the test environment. IHDR is always the first chunk: colour
    type is the byte at offset 25. 2 = RGB (opaque), 6 = RGBA. A palette
    PNG (3) can smuggle transparency back in through a tRNS chunk, so pin
    that absent too.
    """
    icon = (
        Path(__file__).resolve().parent.parent
        / "assets"
        / "favicon"
        / "apple-touch-icon.png"
    )
    data = icon.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG?"
    colour_type = data[25]
    assert colour_type in (0, 2, 3), (
        f"apple-touch-icon.png has colour type {colour_type} (an alpha "
        "channel) — regenerate it with scripts/make_favicons.py, which "
        "flattens this one icon onto opaque white."
    )
    assert b"tRNS" not in data, (
        "apple-touch-icon.png carries a tRNS transparency chunk — iOS will "
        "composite it onto an unpredictable background."
    )
