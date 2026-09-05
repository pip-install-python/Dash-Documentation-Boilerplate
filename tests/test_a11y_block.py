"""The a11y / agentic block — 1.6.44 item 6, sub-items (a) to (g).

Each test names its sub-item. Two of the seven are RECORDED rather than
fixed, and say so here as well as in DIVERGENCES.md, because a sub-item that
quietly disappears from a checklist is indistinguishable from one that was
done:

(d) the mobile console error seen on leaflet/llms/pannellum — not reproduced
    on this host (the seat's phone-width pass, 1.6.44); recorded, not fixed;
(e) shipped CSS/JS minified — NOT minified, and deliberately: the wire
    serves them gzip-encoded, the whole of assets/ is 29 KB of text, and an
    unminified stylesheet is the one a fork reads when it forks. Recorded.

Everything else is asserted below.
"""
from __future__ import annotations

import re

import pytest

from conftest import REPO_ROOT

CSS = (REPO_ROOT / "assets" / "main.css").read_text()


def code(path) -> str:
    """A Python file with its comments removed.

    Item 13's rule, and this file needed it immediately: the first version of
    `test_the_other_apps_menu_target_is_a_real_button` searched the raw source
    for "aria-haspopup" and matched the COMMENT explaining why there isn't
    one. A detect that reads prose about a defect is a detect on prose.
    """
    return "\n".join(
        line for line in path.read_text().splitlines()
        if not line.lstrip().startswith("#")
    )


# ------------------------------------------------------------------- (a) --


def test_the_other_apps_menu_target_is_a_real_button():
    """A div with aria-haspopup is not a control; a Button is."""
    block = code(REPO_ROOT / "components" / "header.py").split(
        "def create_other_apps_menu", 1)[1]
    assert "dmc.MenuTarget(" in block and "dmc.Button(" in block, (
        "the menu target is not a real button element"
    )
    assert "aria-haspopup" not in block, (
        "a hand-written aria-haspopup means the target is standing in for a "
        "control rather than being one"
    )


def test_the_other_apps_menu_opens_without_a_pointer():
    """`trigger="hover"` makes the only listing of the network mouse-only."""
    block = code(REPO_ROOT / "components" / "header.py").split(
        "def create_other_apps_menu", 1)[1]
    assert 'trigger="click-hover"' in block, (
        "the menu opens on hover alone — focus it and press Enter and nothing "
        "happens"
    )


# ------------------------------------------------------------------- (b) --


def test_prose_links_do_not_rely_on_colour_alone():
    """WCAG 1.4.1. The global Anchor default is underline-on-hover, which is
    right for chrome and wrong inside running text."""
    block = re.search(r"#main-content p a[^{]*\{([^}]*)\}", CSS)
    assert block, "no prose-link rule scoped to #main-content"
    assert "text-decoration: underline" in block.group(1)


def test_the_chrome_keeps_its_hover_underline():
    """The fix must be scoped: underlining every anchor would put a rule
    under the nav rows and the footer icons."""
    appshell = (REPO_ROOT / "components" / "appshell.py").read_text()
    assert '"underline": "hover"' in appshell
    assert "\na {\n    text-decoration: underline" not in CSS, (
        "a global anchor underline would repaint the chrome too"
    )


# ------------------------------------------------------------------- (c) --


def test_touch_targets_reach_44px_at_phone_width():
    """iOS/Android minimum. The drawer rows already did; the icon buttons
    (ActionIcon size="lg" is 34px) did not."""
    phone = [b for b in re.findall(r"@media[^{]*\{(.*?)\n\}", CSS, re.S)
             if "max-width: 750px" in CSS[:CSS.index(b)][-120:]]
    assert phone, "no phone-width media block in main.css"
    icons = [b for b in phone if "ActionIcon" in b]
    assert icons, "no phone-width rule widens the icon controls"
    assert "min-width: 44px" in icons[0] and "min-height: 44px" in icons[0]


def test_the_mobile_drawer_rows_still_meet_the_minimum():
    """The rule this one was modelled on — a regression here is the same bug."""
    assert ".mobile-nav .navbar-link" in CSS
    row = CSS.split(".mobile-nav .navbar-link", 1)[1].split("}", 1)[0]
    assert "min-height: 44px" in row


# ------------------------------------------------------------------- (f) --


def test_a_local_content_image_carries_its_intrinsic_size():
    """Markdown supplies no dimensions, so an image reserves no box and the
    prose under it jumps. For an asset in this repo the size is readable."""
    from lib.directives.headings import _intrinsic_size

    width, height = _intrinsic_size("assets/intro_img.jpg")
    assert (width, height) == (673, 202), (width, height)


def test_a_remote_content_image_is_left_alone():
    """A render that reaches the network is a render that can hang, and a
    guessed box is worse than no box."""
    from lib.directives.headings import _intrinsic_size

    assert _intrinsic_size("https://img.shields.io/github/followers/x") == (None, None)
    assert _intrinsic_size("assets/does-not-exist.png") == (None, None)


def test_the_image_renderer_emits_the_box():
    block = code(REPO_ROOT / "lib" / "directives" / "headings.py").split(
        "def image(self", 1)[1].split("m2d_renderer", 1)[0]
    assert '_intrinsic_size(url)' in block
    assert '"maxWidth": "100%"' in block, (
        "width/height without maxWidth trades layout shift for overflow"
    )


def test_dash_still_rejects_the_lazy_loading_attributes():
    """Why the renderer does not defer the load, pinned to the reason.

    `loading` and `decoding` are not props of dash's html.Img — passing
    either RAISES at render, which is how this was found (196 collection
    errors, not a soft warning). If a future Dash adds them, this test goes
    red and the renderer can have them.
    """
    from dash import html

    props = html.Img()._prop_names
    assert "width" in props and "height" in props
    assert "loading" not in props and "decoding" not in props, (
        "Dash learned the lazy-loading attributes — the image renderer can "
        "now defer the load; add them back and delete this test"
    )


def test_the_corpus_of_content_images_is_not_empty():
    """Note 88 on this sub-item: if the docs shipped no images at all, every
    assertion above would be green and none of them would mean anything."""
    images = []
    for path in list(REPO_ROOT.glob("pages/*.md")) + list(REPO_ROOT.glob("docs/**/*.md")):
        images += re.findall(r"!\[[^\]]*\]\(([^)]+)\)", path.read_text())
    assert images, "no content images anywhere — sub-item (f) swept nothing"
    local = [u for u in images if not u.startswith(("http", "//", "data:"))]
    assert local, f"all {len(images)} content images are remote; (f) is vacuous"


# ------------------------------------------------------------------- (g) --


def test_assets_get_a_cache_lifetime_and_documents_do_not():
    from lib.static_cache import ASSET_CACHE_CONTROL, cache_control_for

    assert cache_control_for("/assets/main.css") == ASSET_CACHE_CONTROL
    assert "max-age=3600" in ASSET_CACHE_CONTROL
    for document in ("/", "/backends", "/llms.txt", "/healthz",
                     "/admin/traffic", "/api/pages",
                     "/_dash-component-suites/dash/x.js"):
        assert cache_control_for(document) is None, (
            f"{document} is an answer about right now — it must keep "
            "revalidating"
        )


@pytest.mark.parametrize("lane", ["flask", "asgi"])
def test_both_lanes_apply_the_same_policy_from_one_place(lane):
    """Two lanes serving different lifetimes for the same file is the drift
    this shares a module to prevent."""
    src = code(REPO_ROOT / ("run.py" if lane == "flask"
                            else "lib/asgi_middleware.py"))
    assert "from lib.static_cache import cache_control_for" in src
    assert "Cache-Control" in src


def test_the_preconnect_count_stays_small():
    """pannellum's other half: each preconnect costs a handshake the page may
    never use. Two live ones (the font host and its file host) is the budget;
    the commented CDN pair stays commented."""
    html = (REPO_ROOT / "templates" / "index.html").read_text()
    live = [ln for ln in html.splitlines()
            if 'rel="preconnect"' in ln and not ln.strip().startswith("<!--")]
    assert len(live) <= 4, f"{len(live)} live preconnects: {live}"
    assert any("fonts.gstatic.com" in ln for ln in live), (
        "preconnecting the CSS host without the FILE host is the half that "
        "does not help"
    )


def test_the_size_reader_needs_no_third_party_package():
    """Item 6(f) must work where the app actually runs.

    The first version used Pillow, which is installed by two BUILD-TIME
    scripts here and is deliberately not in requirements.txt. So the feature
    was inert in production and on every CI leg, and green only on the one
    machine that happened to have Pillow — which is exactly what CI said, on
    every matrix leg of runs 33941955814 and 33942828583.

    This test asserts the parser itself imports nothing outside the stdlib.
    """
    import ast

    src = (REPO_ROOT / "lib" / "directives" / "headings.py").read_text()
    tree = ast.parse(src)
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "_size_from_header")
    imports = [n for n in ast.walk(fn) if isinstance(n, (ast.Import, ast.ImportFrom))]
    assert imports == [], f"the header parser imports {imports}"
    assert "PIL" not in src, "Pillow is back in the render path"


def test_dimensions_are_read_from_the_file_header():
    """The formats this template ships, parsed from their own bytes."""
    from lib.directives.headings import _size_from_header

    png = (REPO_ROOT / "assets" / "intro_img.png").read_bytes()[:4096]
    jpg = (REPO_ROOT / "assets" / "intro_img.jpg").read_bytes()[:4096]
    assert _size_from_header(png) == (673, 202)
    assert _size_from_header(jpg) == (673, 202)


def test_an_unparseable_file_reserves_no_box_rather_than_guessing():
    from lib.directives.headings import _size_from_header

    assert _size_from_header(b"") == (None, None)
    assert _size_from_header(b"not an image at all") == (None, None)
    svg = (REPO_ROOT / "assets" / "logo.svg").read_bytes()[:4096]
    assert _size_from_header(svg) == (None, None), (
        "an SVG has no raster dimensions — a guessed box is worse than none"
    )


def test_the_reader_agrees_with_pillow_where_pillow_exists():
    """A cross-check against the reference implementation, SKIPPED where it
    is absent — which is most places, including CI, which is the whole
    reason the reader is hand-rolled."""
    # try/except rather than find_spec: a module can be importABLE and
    # unimportable (a broken install, or the stub used to reproduce CI's
    # environment locally). find_spec finds it and the import still raises,
    # which is the second time this release that a "is it installed?" guard
    # answered yes about something that could not run.
    try:
        from PIL import Image
    except Exception as exc:
        pytest.skip(f"Pillow unavailable here ({exc}) — it is a "
                    "build-script dependency, not a runtime one")

    from lib.directives.headings import _size_from_header

    for name in ("intro_img.png", "intro_img.jpg"):
        path = REPO_ROOT / "assets" / name
        with Image.open(path) as reference:
            assert _size_from_header(path.read_bytes()[:4096]) == reference.size
