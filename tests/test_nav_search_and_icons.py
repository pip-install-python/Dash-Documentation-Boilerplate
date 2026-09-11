"""The page search lists nothing private, and every icon is a real icon.

1.6.45 rider (2026-09-09, note 140). CORRECTED the same hour it was sent:
this kit already has both behaviours, so these are REGRESSION TESTS, not
fixes — measured on this tree before writing them (`is_nav_page` already
excludes /admin/*, the hidden tier and /404; the icon fallback is already
the `or` form at components/navbar.py:134).

That is exactly why they are worth having. A behaviour nobody pinned is a
behaviour one refactor away from gone, and the failure is silent in the
direction that matters: an anonymous visitor enumerating admin paths from a
dropdown, or a blank square where an icon should be.

BOTH COPIES, because there are two. The header's `create_search` is
`visibleFrom="sm"` and the mobile drawer carries its own field — a test that
checked only `search_data()` would pass on a day when one copy stopped
calling it.
"""
from __future__ import annotations

import re

import pytest
from dash.development.base_component import Component

from components.header import create_search
from components.navbar import ADMIN_PREFIX, create_mobile_content, search_data


def _walk(node):
    """Every component in a rendered tree, depth first."""
    yield node
    children = getattr(node, "children", None)
    if isinstance(children, Component):
        yield from _walk(children)
    elif isinstance(children, (list, tuple)):
        for child in children:
            if isinstance(child, Component):
                yield from _walk(child)
    for attr in ("leftSection", "rightSection", "label", "icon"):
        value = getattr(node, attr, None)
        if isinstance(value, Component):
            yield from _walk(value)


def _select_options(tree):
    """Every `data` option value on a Select in the tree."""
    values = []
    for node in _walk(tree):
        data = getattr(node, "data", None)
        if isinstance(data, list):
            for option in data:
                if isinstance(option, dict) and "value" in option:
                    values.append(option["value"])
    return values


@pytest.fixture(scope="module")
def registry(app_module):
    import dash

    entries = list(dash.page_registry.values())
    assert entries, "the page registry is empty — nothing to sweep"
    return entries


# --------------------------------------------- (a) what the search lists --


def _copies(data):
    """The two search copies, by name, so a failure says WHICH one."""
    return {"header select": create_search(data),
            "mobile drawer": create_mobile_content(data)}


def test_both_search_copies_list_the_same_pages(registry):
    """If they drift, every assertion below covers one copy and not the
    other, and the one that drifted is the one nobody tested."""
    listed = {name: sorted(_select_options(tree))
              for name, tree in _copies(registry).items()}
    assert listed["header select"] == listed["mobile drawer"], listed
    assert listed["header select"], "neither copy lists any page at all"


def test_no_copy_lists_an_admin_path_a_hidden_page_or_the_404(registry):
    """Rider (a). An anonymous visitor must not be able to enumerate admin
    paths or hidden-tier pages from a dropdown."""
    from components.navbar import page_tier

    registered = len(registry)
    for name, tree in _copies(registry).items():
        listed = _select_options(tree)
        assert listed, f"{name} lists nothing — a sweep of nothing is green"
        offenders = [p for p in listed if p.startswith(ADMIN_PREFIX)]
        assert offenders == [], f"{name} lists admin paths: {offenders}"
        assert [p for p in listed if p in ("/404", "/")] == [], listed
        hidden = [p for p in listed if page_tier(p) == "hidden"]
        assert hidden == [], f"{name} lists hidden-tier pages: {hidden}"
    # (registered, listed) — the fork round asks each host for this pair.
    print(f"\n(registered, listed) = ({registered}, "
          f"{len(_select_options(_copies(registry)['header select']))})")


def test_a_synthetic_admin_entry_is_excluded_from_both_copies(registry):
    """Rider (a)'s positive control. Without it, the assertions above pass on
    a tree that happens to have no admin page registered — which is a green
    from an empty corpus, not from a working filter."""
    planted = dict(registry[0])
    planted.update({"path": f"{ADMIN_PREFIX}/planted-board",
                    "name": "Planted Board", "nav": "Planted Board",
                    "module": "pages.planted"})
    data = list(registry) + [planted]

    assert planted["path"] in {e["path"] for e in data}, "the plant is absent"
    for name, tree in _copies(data).items():
        listed = _select_options(tree)
        assert planted["path"] not in listed, (
            f"{name} lists the planted admin page — the filter is not the "
            "reason the real assertions pass"
        )


def test_the_control_would_catch_a_broken_filter(registry):
    """And the control's own control: a plant that is NOT admin-shaped DOES
    get listed, so the test above is not passing because the plant was
    malformed or the copies ignore extra entries."""
    planted = dict(registry[0])
    planted.update({"path": "/planted-public-page", "name": "Planted Public",
                    "nav": "Planted Public", "module": "pages.planted_public"})
    listed = _select_options(create_search(list(registry) + [planted]))
    assert "/planted-public-page" in listed, (
        "a plain planted page is not listed either — the plant never reaches "
        "the search, so the admin control proves nothing"
    )


def test_search_data_is_what_both_copies_render(registry):
    """The helper and the rendered copies must agree; otherwise a future
    caller could filter correctly and render something else."""
    from_helper = sorted(option["value"] for option in search_data(registry))
    assert sorted(_select_options(create_search(registry))) == from_helper


# ------------------------------------------------- (b) every icon is real --


_ICON = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*:[a-z0-9]+(?:-[a-z0-9]+)*$")


def _icon_names(tree):
    names = []
    for node in _walk(tree):
        if type(node).__name__ == "DashIconify":
            names.append(getattr(node, "icon", None))
    return names


def test_every_icon_in_both_copies_is_prefix_colon_name(registry):
    """Rider (b). Iconify needs `prefix:name`; anything else renders as a
    blank square, and nothing errors."""
    for name, tree in _copies(registry).items():
        icons = _icon_names(tree)
        assert icons, f"{name} renders no DashIconify at all"
        bad = [i for i in icons if not (isinstance(i, str) and _ICON.match(i))]
        assert bad == [], f"{name} carries malformed icon names: {bad}"


def test_the_icon_regex_would_reject_the_shapes_that_break(registry):
    """Negative control for the pattern itself — a regex that matched
    everything would make the test above decorative."""
    for broken in ("mdi-code-tags", "", None, "Mdi:Code", ":name", "prefix:"):
        assert not (isinstance(broken, str) and _ICON.match(broken)), broken
    assert _ICON.match("mingcute:search-3-line")
    assert _ICON.match("fluent:lock-closed-16-regular")


def test_the_icon_fallback_is_the_or_form_not_a_two_argument_get():
    """Rider (b)'s second half, and it cannot be seen by rendering.

    `entry.get("icon", DEFAULT)` returns None when the key EXISTS and is
    None — which is what a page with `icon:` and no value in its frontmatter
    produces. The `or` form is the one that actually falls back.
    """
    import pathlib

    root = pathlib.Path(__file__).resolve().parent.parent
    for name in ("components/navbar.py", "components/header.py"):
        source = (root / name).read_text()
        offenders = re.findall(r'\.get\(\s*["\']icon["\']\s*,', source)
        assert offenders == [], (
            f"{name} uses the two-argument get for an icon fallback — it "
            "returns None when the key is present and empty"
        )


# ------- a control-board override must reach the listing (note 139) --


def test_a_board_hidden_page_leaves_both_search_copies(registry, monkeypatch):
    """Note 139's class, measured on this tree 2026-09-11 and fixed.

    `components.navbar.page_tier` read `page_tiers.local_tier` — the
    FRONTMATTER tier, which knows nothing about the control board. So after
    the owner hid a page from the board, `lib.access` answered "hidden" for
    every request while the sidebar and BOTH search dropdowns went on
    listing it: overrides that arrive from the store did not rebuild what
    the frontmatter built, and the page stayed advertised in the one place
    a hidden page is most visible.

    The override is injected at `page_visibility.tier_override` — the real
    seam `lib.access.local_tier` consults — rather than by writing the
    store, so the test neither touches disk nor depends on reload timing.
    """
    from lib import page_visibility

    target = next(p for p in
                  (option["value"] for option in search_data(registry))
                  if p not in ("/", "/404"))

    real = page_visibility.tier_override

    def hidden_for_target(path):
        return "hidden" if path == target else real(path)

    monkeypatch.setattr(page_visibility, "tier_override", hidden_for_target)

    for name, tree in _copies(registry).items():
        listed = _select_options(tree)
        assert listed, f"{name} lists nothing — nothing was judged"
        assert target not in listed, (
            f"{name} still lists {target} after the control board hid it — "
            "the listing reads the frontmatter tier, not the override"
        )


def test_the_override_seam_is_what_moved_it(registry, monkeypatch):
    """Control for the test above: without the override the same page IS
    listed, so its absence is the override's doing and not the target
    having been unlistable all along."""
    listed = _select_options(create_search(registry))
    target = next(p for p in listed if p not in ("/", "/404"))
    assert target in listed


def test_the_listing_and_the_gate_use_one_resolver():
    """They disagreed, and the fix was to stop having two. A future edit
    that reintroduces `page_tiers.local_tier` here would restore the
    defect silently, because both spellings read plausibly."""
    import inspect

    from components import navbar

    source = inspect.getsource(navbar.page_tier)
    assert "access.local_tier" in source, (
        "navbar.page_tier no longer resolves through lib.access — the "
        "sidebar and the gate can disagree about a hidden page again"
    )
