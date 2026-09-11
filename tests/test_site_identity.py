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

import re
from pathlib import Path

import pytest

from conftest import REPO_ROOT
from lib.constants import (
    PAGE_TITLE_PREFIX,
    SITE_BRAND,
    SITE_DESCRIPTION,
    SITE_SHORT_NAME,
)

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


# ---------------------------------------------------------------------------
# The per-page title — a share-card surface, not just a browser tab
#
# Dash passes each page's `title` straight into `og:title` and `twitter:title`
# (dash/_pages.py `_page_meta_tags`). PAGE_TITLE_PREFIX therefore sets the
# headline of every unfurl this site produces, and it read the FORK SOURCE's
# brand ("Dash Pip Components | ") in production until 1.2.2 — while every
# other surface correctly said this site's name. Nobody sees their own share
# cards, so only a test catches it.
# ---------------------------------------------------------------------------


def test_the_page_title_prefix_is_this_site():
    assert PAGE_TITLE_PREFIX == f"{SITE_SHORT_NAME} | "
    assert "Dash Pip Components" not in PAGE_TITLE_PREFIX, (
        "the fork source's brand is back in every share card"
    )


def test_the_short_name_cannot_drift_from_the_brand():
    """Two constants, one identity. Derived, so this should be automatic."""
    assert SITE_BRAND.startswith(SITE_SHORT_NAME)


def test_the_share_card_headline_names_this_site(client):
    """og:title and twitter:title, as a scraper reads them."""
    html = client.get("/").text
    for tag in ("og:title", "twitter:title"):
        found = re.findall(
            rf'<meta[^>]*property="{tag}"[^>]*content="([^"]*)"', html
        )
        assert found, f"no {tag} on the home page"
        for value in found:
            assert "Dash Pip Components" not in value, (
                f"{tag}={value!r} advertises the fork source"
            )
            assert SITE_SHORT_NAME in value, f"{tag}={value!r} does not name this site"


def test_no_surface_still_carries_the_fork_source_brand():
    """A sweep, because the prefix was not the only place it could hide."""
    offenders = []
    for path in ("lib/constants.py", "templates/index.html", "pages/home.md",
                 "assets/favicon/site.webmanifest"):
        text = (REPO_ROOT / path).read_text()
        # The constants file documents the old value in a comment explaining
        # the fix; that is the one legitimate mention.
        stripped = re.sub(r"#.*", "", text) if path.endswith(".py") else text
        stripped = re.sub(r"<!--.*?-->", "", stripped, flags=re.S)
        if "Dash Pip Components" in stripped:
            offenders.append(path)
    assert offenders == [], f"the fork source's brand survives in {offenders}"


def test_home_markdown_is_not_a_stale_copy_of_the_old_opening():
    """`# Welcome to:` was the old H1 — an identity that named nothing."""
    body = Path(REPO_ROOT / "pages" / "home.md").read_text()
    assert "# Welcome to:" not in body


# ---------------------------------------------------------------------------
# Version claims are DERIVED, never written. "Powered by dash-improve-my-llms
# 2.3.4" served on /llms.txt for months while a newer package was actually
# running the site — the most-read surface in the network publishing a false
# fact about itself. Prose writes {{VERSION:<distribution>}} (any installed
# package — satellites use it for the library they document); the loaders
# substitute the installed version via lib/versions.py; these tests close
# the loop.
# ---------------------------------------------------------------------------


def test_served_prose_reports_the_installed_package_version(client):
    from dash_improve_my_llms import __version__ as installed

    body = client.get("/llms.txt").text
    assert f"**{installed}**" in body, (
        "the 'Powered by' line no longer carries the installed version"
    )
    # And no OTHER version is claimed for the package anywhere in the index:
    # every "dash-improve-my-llms ... **X.Y.Z**" must be the installed one.
    for match in re.finditer(
        r"dash-improve-my-llms[^\n]*?\*\*(\d+\.\d+\.\d+)\*\*", body
    ):
        assert match.group(1) == installed, (
            f"/llms.txt claims version {match.group(1)}; installed is {installed}"
        )


def test_no_source_markdown_hardcodes_a_package_version():
    """The placeholder is the only way prose may state the package version.

    Sweeps the SOURCE files, so a hardcoded number is caught even on pages
    these tests never fetch. CHANGELOGs and history-narrating docs may name
    versions in context ("until 2.3.4 landed"), and install floors
    (`pkg>=2.5.1`) are requirements, not claims; what prose may not do is
    claim a version as current — which always takes the bold form the
    'Powered by' lines use, next to the package's name or PyPI link.
    """
    claim = re.compile(
        r"(dash-improve-my-llms|pypi\.org/project/)[^\n]*?\*\*\d+\.\d+(\.\d+)?\*\*"
    )
    offenders = []
    for md in [REPO_ROOT / "pages" / "home.md", *(REPO_ROOT / "docs").rglob("*.md")]:
        for line in md.read_text().splitlines():
            if claim.search(line):
                offenders.append(f"{md.relative_to(REPO_ROOT)}: {line.strip()[:80]}")
    assert offenders == [], f"hardcoded package versions in prose: {offenders}"


def test_version_placeholder_never_leaks_unsubstituted(client):
    from lib.constants import BASE_URL  # noqa: F401 — client is same-host

    for path in ("/llms.txt", "/", "/examples/ai-integration/llms.txt"):
        body = client.get(path).text
        assert "{{DIMLL_VERSION}}" not in body, f"unsubstituted placeholder on {path}"
        assert "{{VERSION:" not in body, f"unsubstituted placeholder on {path}"


def test_substitution_works_for_any_installed_distribution():
    """The generic form is what lets every satellite state ITS package's
    version — the mechanism must not be special-cased to one package."""
    from importlib.metadata import version

    from lib.versions import substitute_versions

    assert substitute_versions("dash **{{VERSION:dash}}**") == (
        f"dash **{version('dash')}**"
    )


def test_legacy_placeholder_still_resolves():
    """{{DIMLL_VERSION}} predates the generic form; forks may still write it."""
    import dash_improve_my_llms as pkg

    from lib.versions import substitute_versions

    assert substitute_versions("{{DIMLL_VERSION}}") == pkg.__version__


def test_a_version_claim_for_an_absent_package_fails_the_boot():
    """A claim that cannot be true must fail loudly at load time, not leak."""
    import pytest

    from lib.versions import substitute_versions

    with pytest.raises(LookupError, match="not-a-real-distribution"):
        substitute_versions(
            "{{VERSION:not-a-real-distribution}}", source="docs/x.md"
        )


def test_code_examples_keep_the_placeholder_syntax_verbatim():
    """docs/network-standard SHOWS the syntax in a fence; substituting there
    would render the example as a number and undocument the mechanism."""
    from lib.versions import substitute_versions

    fenced = "```markdown\n**{{VERSION:dash}}**\n```\n"
    assert substitute_versions(fenced) == fenced
    inline = "write `{{VERSION:dash}}` in prose"
    assert substitute_versions(inline) == inline


def test_both_content_lanes_run_the_versions_pipeline():
    """home.py and markdown.py agree on the content pipeline.

    /llms.txt serves home.md's text, so a {{VERSION:...}} token there ships
    raw on the most-read machine surface unless home.py runs the same
    substitute_versions the docs pages get (batch-1 finding, 2026-08-25:
    older forks skipped home). The wire check two tests up is vacuous the
    day home.md happens to carry no token; this source pin is not.

    AST, not grep — the marker-in-comment trap cuts both ways: a comment
    naming the call would satisfy a grep on a file that never runs it.
    """
    import ast

    for rel in ("pages/home.py", "pages/markdown.py"):
        tree = ast.parse((REPO_ROOT / rel).read_text(encoding="utf-8"))
        called = any(
            isinstance(node, ast.Call)
            and "substitute_versions"
            in (getattr(node.func, "id", ""), getattr(node.func, "attr", ""))
            for node in ast.walk(tree)
        )
        assert called, (
            f"{rel} never calls substitute_versions — its lane serves "
            "version tokens raw"
        )


# --------- the own-package {{VERSION}} fallback (note 133, excalidraw) --


@pytest.fixture
def fake_own_package(monkeypatch):
    """A fork's shape: a component module importable from the TREE whose
    DISTRIBUTION is not installed — which is every component fork on CI and
    in the image, because neither runs `pip install .`."""
    import sys
    import types

    module = types.ModuleType("dash_fakecomponent")
    module.__version__ = "9.9.9"
    monkeypatch.setitem(sys.modules, "dash_fakecomponent", module)
    monkeypatch.setattr("lib.constants.API_PACKAGES", ["dash_fakecomponent"])
    return module


def test_a_forks_own_package_resolves_from_the_tree(fake_own_package):
    """Note 133: this raised LookupError during app construction and took
    the whole site down — every test red, the boot step red."""
    from lib.versions import substitute_versions

    out = substitute_versions("dash-fakecomponent {{VERSION:dash-fakecomponent}}",
                              source="<t>")
    assert out == "dash-fakecomponent 9.9.9", out


def test_the_module_spelling_resolves_too(fake_own_package):
    """`API_PACKAGES` holds module names; prose writes the PyPI name. Both
    spellings name the same package and both must resolve."""
    from lib.versions import version_of

    assert version_of("dash-fakecomponent") == "9.9.9"
    assert version_of("dash_fakecomponent") == "9.9.9"


def test_any_other_absent_distribution_still_raises(fake_own_package):
    """The fallback must not turn a TYPO into a silent pass — that is the
    whole reason the substituter fails loudly at import."""
    from lib.versions import substitute_versions

    with pytest.raises(LookupError) as excinfo:
        substitute_versions("{{VERSION:dash-notinstalled-xyz}}", source="<t>")
    assert "dash-notinstalled-xyz" in str(excinfo.value)


def test_the_template_itself_keeps_the_loud_failure():
    """Positive control on the SHIPPED tree: API_PACKAGES is empty here, so
    the fallback is inert and an absent name raises exactly as before. A
    fallback that silently covered every name would pass the test above and
    still be wrong."""
    from lib.constants import API_PACKAGES
    from lib.versions import substitute_versions

    assert API_PACKAGES == [], (
        "this host documents a package — the control below no longer tests "
        "the template's shape"
    )
    with pytest.raises(LookupError):
        substitute_versions("{{VERSION:dash-fakecomponent}}", source="<t>")


def test_an_own_package_with_no_dunder_version_says_so(monkeypatch):
    """A component package missing `__version__` is a real fork defect, and
    the error must name it rather than reporting 'not installed'."""
    import sys
    import types

    module = types.ModuleType("dash_noversion")
    monkeypatch.setitem(sys.modules, "dash_noversion", module)
    monkeypatch.setattr("lib.constants.API_PACKAGES", ["dash_noversion"])
    from lib.versions import substitute_versions

    with pytest.raises(LookupError) as excinfo:
        substitute_versions("{{VERSION:dash-noversion}}", source="<t>")
    assert "__version__" in str(excinfo.value)


def test_the_header_badge_reads_the_same_resolver(
        fake_own_package, monkeypatch):
    """The badge and the prose must not disagree about what this host runs
    — they resolved independently before note 133.

    `components/header.py` does `from lib.constants import API_PACKAGES`, so
    the name is bound in ITS namespace at import and patching lib.constants
    alone does not reach it. Patch where the name was bound, or this test
    reads the template's empty list and passes on a None it never meant to
    assert.
    """
    import components.header as header

    monkeypatch.setattr(header, "API_PACKAGES", ["dash_fakecomponent"])
    assert header._package_version() == "9.9.9"


# ------------------ the landing page's install block (item T1) --


def _home_markdown() -> str:
    return (REPO_ROOT / "pages" / "home.md").read_text()


def test_the_landing_page_opens_with_the_acquisition_block():
    """T1's detect, on the SOURCE: the placeholder is there and it is one of
    the first blocks under the title — not buried below the fold."""
    source = _home_markdown()
    assert "{{INSTALL}}" in source, (
        "the landing page does not carry the install block at all"
    )
    above = source.split("{{INSTALL}}", 1)[0]
    assert above.count("\n\n") <= 4, (
        f"the install block sits under {above.count(chr(10) + chr(10))} "
        "blocks — T1 wants it among the first, above the fold"
    )


def test_the_version_is_never_typed_into_the_landing_page():
    """The whole point: a number in prose is a lie waiting for the next
    release. Nothing version-shaped may be hand-written in the block."""
    source = _home_markdown()
    assert "pip install dash-documentation-boilerplate" not in source
    assert not re.search(r"Current version: \*\*\d", source), (
        "a literal version is typed into home.md — it must come from the "
        "installed package or the tree"
    )


def test_the_template_does_not_advertise_a_package_that_does_not_exist():
    """CORRECTION TO T1, pinned so a later sync cannot quietly undo it.

    T1 says every satellite landing page opens with `pip install <package>`.
    This host has no package: `dash-documentation-boilerplate` is not on
    PyPI and the repo carries no pyproject.toml or setup.py. Rendering the
    line here would publish an install instruction for a distribution that
    does not exist, in both lanes, on the network's most-copied page.
    """
    from lib.constants import API_PACKAGES
    from lib.versions import install_markdown

    assert API_PACKAGES == [], "this host now documents a package"
    assert not (REPO_ROOT / "pyproject.toml").exists()
    assert not (REPO_ROOT / "setup.py").exists()

    block = install_markdown()
    assert "pip install" not in block, block
    assert "git clone" in block and "github.com" in block, block


def test_a_fork_gets_T1s_line_with_a_resolved_version(fake_own_package):
    """And on a host that DOES document a package — every component fork —
    the block is T1 verbatim, with the version read, never typed."""
    from lib.versions import install_markdown, version_of

    block = install_markdown()
    assert "pip install dash-fakecomponent" in block, block
    assert version_of("dash-fakecomponent") == "9.9.9"
    assert "**9.9.9**" in block, block


def test_a_fork_whose_package_has_no_version_fails_loudly(monkeypatch):
    """A satellite cannot state its own install line without a version, and
    a silent empty one is worse than a boot failure."""
    import sys
    import types

    module = types.ModuleType("dash_noversion2")
    monkeypatch.setitem(sys.modules, "dash_noversion2", module)
    monkeypatch.setattr("lib.constants.API_PACKAGES", ["dash_noversion2"])
    from lib.versions import install_markdown

    with pytest.raises(LookupError) as excinfo:
        install_markdown()
    assert "install line" in str(excinfo.value)


def test_the_crawler_document_carries_the_block(app_module):
    """The MACHINE lane, on its own artifact. `LLMS_DOC` is the prose
    dash-improve-my-llms serves as the opening of /llms.txt, and it is built
    from the substituted markdown — so the block reaches an agent, which is
    the half a Dash component would never have reached (note 132)."""
    import pages.home as home

    doc = home.LLMS_DOC
    assert "{{INSTALL}}" not in doc, "the placeholder was served unsubstituted"
    assert "git clone" in doc, doc[:400]
    above = doc.split("git clone", 1)[0]
    assert len(above) < 800, (
        f"the block is {len(above)} characters down the crawler document — "
        "T1 wants it above the fold in BOTH lanes"
    )


def test_the_browser_page_carries_the_block_too(app_module):
    """The BROWSER lane, on ITS artifact — the rendered layout, not the
    served HTML. The page is a Dash component tree, so `curl | grep` finds
    nothing here even when the block is present and correct (the kit's
    skip-link finding, the same trap in the other direction)."""
    import json

    import pages.home as home

    rendered = json.dumps(home.layout.to_plotly_json(), default=str)
    assert "git clone" in rendered, (
        "the landing page's layout does not contain the acquisition block"
    )


# ------- the private reporting contract is not linked publicly (C1) --


def test_no_public_link_to_the_hubs_private_analytics_document():
    """C1. The hub's satellite-analytics document is not public, and this
    site linked to it from the Network Standard page.

    Measured on the wire 2026-09-11 before removing it: the path answers 404
    to a crawler (Googlebot), and a browser gets the hub's SPA shell — the
    same 124,698 bytes a nonexistent path returns — so nothing a reader
    follows the link with reaches the document.

    A CLICKABLE link is what C1 removes. The URL still appears once inside a
    fenced code block on that page, quoting the shipped `INTERNAL_UA`
    constant verbatim; that is the value this host really sends, and making
    the documentation disagree with the code would be the worse error.
    """
    offenders = []
    for folder in ("docs", "pages"):
        for path in sorted((REPO_ROOT / folder).rglob("*.md")):
            text = path.read_text()
            if "](https://2plot.ai/docs/satellite-analytics" in text:
                offenders.append(str(path.relative_to(REPO_ROOT)))
    assert offenders == [], (
        f"{offenders} link publicly to the hub's private document — C1 says "
        "one sentence and no link"
    )


def test_the_network_standard_states_the_contract_without_linking_it():
    """And the sentence is actually there — removing the link without
    replacing it would leave the section stating no contract at all."""
    page = (REPO_ROOT / "docs" / "network-standard"
            / "network-standard.md").read_text()
    assert "The reporting contract is private; every kit carries its half." \
        in page


def test_the_mcp_wording_names_dashs_native_support_and_no_bespoke_endpoint():
    """C1's second half, two sentences: no bespoke endpoint, Dash 4.x native
    MCP is the path, dimll's resources ride it."""
    page = (REPO_ROOT / "docs" / "ai-integration"
            / "ai-integration.md").read_text()
    assert "no bespoke MCP endpoint" in page
    assert "native MCP support is the path" in page
