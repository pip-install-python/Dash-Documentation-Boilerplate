"""Heading ids that survive inline formatting — and match their TOC anchors.

Two defects in markdown2dash's heading handling, both hit as soon as a heading
contains anything other than plain text:

1. **`## The `peers` tier` raises `AttributeError`.**
   ``DashRenderer.heading`` does ``create_heading_id(text[0])``, where ``text``
   is the list of *rendered* inline tokens. When the first token is formatted,
   ``text[0]`` is a ``dmc.Code`` / ``dmc.Text`` component rather than a string,
   and ``create_heading_id`` calls ``.lower()`` on it. The whole page fails to
   import, so one backtick in one heading takes the site down at startup.

2. **Formatted headings get an id their own TOC doesn't link to.**
   Even when the first token *is* a string, only that first token becomes the
   id: ``## Wiring **it** up`` renders ``id="wiring"``. Meanwhile the `toc`
   directive slugs the raw markdown source — ``wiring-**it**-up`` — so the
   anchor in the sidebar points at a fragment that exists nowhere on the page.
   Clicking it does nothing, silently.

The fix is one slug function used by both sides: flatten the rendered heading
back to plain text for the id, strip the same inline markers out of the raw
source for the TOC, and the two agree again.

Plain-text headings — every heading in this repo before this module existed —
slug exactly as they did before, so no existing anchor or deep link moves.
"""

from __future__ import annotations

import re
from typing import Any

# Inline markdown markers to drop before slugging: code spans, emphasis,
# strong, strikethrough, and mark/spoiler. Deliberately NOT a general
# punctuation strip — "AI/LLM Integration" has always slugged to
# "ai/llm-integration", and rewriting that would break links that already
# point at it.
_INLINE_MARKERS = re.compile(r"[`*_~=]|\|\|")

# [label](target) -> label. A link in a heading otherwise drags its URL into
# the id.
_MD_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")


def slugify(text: str) -> str:
    """Slug a heading. Same output as markdown2dash for unformatted text."""
    text = _MD_LINK.sub(r"\1", text)
    text = _INLINE_MARKERS.sub("", text)
    return "-".join(text.lower().split())


_SIZE_CACHE: dict = {}


def _intrinsic_size(url: str):
    """(width, height) for an image this repo serves, else (None, None).

    Local only, and deliberately: a remote URL cannot be measured at render
    time without fetching it, and a render that reaches the network is a
    render that can hang. Pillow is a transitive dependency here rather than
    a declared one, so its absence is a silent no-op, not a crash.
    """
    if url in _SIZE_CACHE:
        return _SIZE_CACHE[url]
    size = (None, None)
    if not url.startswith(("http://", "https://", "//", "data:")):
        try:
            from pathlib import Path

            from PIL import Image

            rel = url.split("?", 1)[0].lstrip("/")
            path = Path(__file__).resolve().parents[2] / rel
            if path.is_file():
                with Image.open(path) as im:
                    size = im.size
        except Exception:
            size = (None, None)
    _SIZE_CACHE[url] = size
    return size


def plain_text(node: Any) -> str:
    """Flatten a rendered inline tree (strings + Dash components) to text."""
    if isinstance(node, str):
        return node
    if isinstance(node, (list, tuple)):
        return "".join(plain_text(child) for child in node)

    children = getattr(node, "children", None)
    if children is None:
        return ""
    return plain_text(children)


def patch_renderer() -> None:
    """Replace ``DashRenderer.heading`` with a version that reads all tokens.

    Monkeypatching rather than subclassing because ``create_parser`` hard-codes
    ``renderer=DashRenderer()``; subclassing would mean reimplementing its
    plugin list here and re-syncing that list on every markdown2dash upgrade.
    Idempotent — importing this module twice is harmless.
    """
    import dash_mantine_components as dmc
    from markdown2dash.src import renderer as m2d_renderer
    from markdown2dash.src.decorators import class_name

    if getattr(m2d_renderer.DashRenderer.heading, "_ddb_patched", False):
        return

    @class_name
    def heading(self, text, level: int, **attrs):
        return dmc.Title(text, order=level, id=slugify(plain_text(text)))

    heading._ddb_patched = True
    m2d_renderer.DashRenderer.heading = heading

    # Inline images (`![alt](src)`): markdown2dash defines no `image`, so
    # mistune's HTML fallback runs and raises on the DMC child list (found
    # when pages/home.py moved off dcc.Markdown, 1.6.38). Rendered as a
    # plain <img> with the alt text — a decorative shield or a hero image,
    # never a layout component.
    def image(self, text, url, title=None, **attrs):
        from dash import html

        # Explicit width/height where they can be KNOWN (1.6.44 item 6f).
        # Markdown carries no dimensions, so an image reserves no box and the
        # prose under it jumps when it loads. For an image served out of this
        # repo's own `assets/` the intrinsic size is readable off the file,
        # and the two attributes give the browser an aspect-ratio to reserve;
        # `maxWidth: 100%` + `height: auto` keep it responsive, which is the
        # combination that fixes layout shift instead of trading it for
        # overflow. A REMOTE image (a shields.io badge) has no readable size
        # at render time and gets none — recorded in DIVERGENCES rather than
        # guessed, because a wrong box is worse than no box.
        # `loading="lazy"` and `decoding="async"` are NOT available: neither
        # is a prop of dash 4.4.1's html.Img (measured — `_prop_names` has
        # width and height and neither of the other two), and Dash raises
        # rather than passing an unknown attribute through. So the box is
        # reserved and the load is not deferred; that is the whole of what
        # this renderer can do today.
        width, height = _intrinsic_size(url)
        extra = {"width": width, "height": height} if width else {}
        return html.Img(src=url, alt=plain_text(text), title=title,
                        style={"maxWidth": "100%", "height": "auto"}, **extra)

    m2d_renderer.DashRenderer.image = image
