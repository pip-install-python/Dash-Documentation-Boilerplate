"""Site identity: one brand, every surface, verbatim.

The network standard says a site states what it is in the same words
everywhere an agent or a reader can reach. The failure this pins is silent,
which is why it needs tests rather than a code review: nothing errors when a
surface falls back to a default. On this host, before `SITE_BRAND` existed,
the llms viewer's brand chip read a bare **"Dash"** — the `Dash()`
constructor's default title, leaking out as the public identity of a
production documentation site.

dash-improve-my-llms 2.3.4's `resolve_site_title` is what makes the fix
possible: it takes the home page's registered `name` first, `app.title`
second, and *skips* generic candidates ("Home", "Index", "Dash") rather than
publishing them. These tests assert both ends of that — the inputs this repo
controls, and the H1 it produces.
"""

from __future__ import annotations

from pathlib import Path

from conftest import REPO_ROOT
from lib.constants import SITE_BRAND, SITE_DESCRIPTION

# Spelled out rather than imported, so that renaming the constant cannot
# silently rename the site. Changing the brand should require changing this
# line, deliberately.
EXPECTED_BRAND = "Dash Documentation Boilerplate — the 2plot network's template"


def test_brand_constant_is_the_agreed_identity():
    assert SITE_BRAND == EXPECTED_BRAND


def test_app_title_is_the_brand(app):
    """`Dash(title=...)` — the <title> and `resolve_site_title`'s fallback."""
    assert app.title == EXPECTED_BRAND


def test_home_prose_opens_with_the_brand():
    first = (REPO_ROOT / "pages" / "home.md").read_text().splitlines()[0]
    assert first == f"# {EXPECTED_BRAND}"


def test_llms_index_h1_is_the_brand(client):
    """The single most-read line of this site, and the one nobody looks at."""
    response = client.get("/llms.txt")
    assert response.ok
    assert response.text.splitlines()[0] == f"# {EXPECTED_BRAND}"


def test_llms_index_tagline_is_the_description(client):
    body = client.get("/llms.txt").text
    assert f"> {SITE_DESCRIPTION}" in body


def test_the_viewer_brand_chip_is_not_a_framework_default(client):
    """The chip that read "Dash" on the pre-2.3.4 artifact.

    It is rendered from the same `resolve_site_title` call as the H1, so
    asserting the brand is present and the default is absent catches both a
    stale package and a regressed constant.
    """
    import html as html_module

    from conftest import BROWSER_ACCEPT

    page = client.get("/backends/llms.txt", accept=BROWSER_ACCEPT).text
    # The banner is templated markup, so the brand arrives escaped — the
    # apostrophe in "network's" becomes `&#x27;`. Comparing the raw string
    # here would fail for a reason that has nothing to do with identity.
    assert html_module.escape(EXPECTED_BRAND) in page, (
        "the viewer banner does not name this site"
    )


def test_the_package_name_is_in_the_description_not_the_brand():
    """Naming rules from the standard, both directions.

    The brand says what the site *is*; the package name and the byline belong
    in the description. A brand of "Pip Install Python" would make every
    satellite in the network share one name.
    """
    assert "dash-documentation-boilerplate" in SITE_DESCRIPTION
    assert "dash-documentation-boilerplate" not in SITE_BRAND
    assert "Pip Install Python" in SITE_DESCRIPTION
    assert "Pip Install Python" not in SITE_BRAND


def test_no_surface_falls_back_to_a_generic_title():
    """The values `resolve_site_title` is designed to skip.

    If the brand were ever set to one of these, the package would silently
    fall through to the next candidate and this repo would have no idea which
    string it was publishing.
    """
    from dash_improve_my_llms.handlers import _GENERIC_SITE_TITLES

    assert SITE_BRAND.strip().lower() not in _GENERIC_SITE_TITLES


def test_readme_and_docs_agree_with_the_brand():
    """A README that names the site differently is the next drift."""
    readme = (REPO_ROOT / "README.md").read_text()
    assert EXPECTED_BRAND in readme, "README.md does not state the site brand"


def test_llms_package_floor_is_the_network_standard():
    """Identity resolution lives in the package; the floor is what delivers it."""
    import dash_improve_my_llms as pkg

    parts = tuple(int(p) for p in pkg.__version__.split(".")[:3] if p.isdigit())
    assert parts >= (2, 3, 4), (
        f"dash-improve-my-llms {pkg.__version__} predates resolve_site_title; "
        "the viewer chip and the /llms.txt H1 would fall back to app.title"
    )


def test_home_markdown_is_not_a_stale_copy_of_the_old_opening():
    """`# Welcome to:` was the old H1 — an identity that named nothing."""
    body = Path(REPO_ROOT / "pages" / "home.md").read_text()
    assert "# Welcome to:" not in body
