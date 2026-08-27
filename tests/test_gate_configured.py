"""The gate as PRODUCTION renders it — with Clerk configured (spec item 7).

Every battery in this fleet boots zero-secret (see tests/conftest.py, which
blanks every `CLERK_*` value before anything imports run.py). That is
deliberate and stays: the fail-closed assertions in test_access.py all
depend on it. The consequence is that until this file existed, the branch
this network actually SERVES was certified by nothing — with no Clerk keys
`lib.access.resolve_page_access` falls OPEN for `auth` pages, so every test
that has ever rendered a docs page rendered the ungated one, and the gate
card was only ever seen through a monkeypatched verdict
(tests/test_gate_layouts.py, which tests the card, not the decision).

Found by clerkhook, then reported `open` by leaflet, excalidraw,
modelviewer and muischeduler across three releases — each correctly
declining to invent a shape while the template owed one. This is that
shape. What it pins:

  * with a fake, non-empty Clerk config, an `auth` page renders the SIGN-IN
    card to an anonymous visitor — the configured branch, reached through
    the real `resolve_page_access`, not a stub;
  * the same page, same tier, zero-secret, renders its CONTENT — so the
    assertion above cannot pass by accident of the tier override;
  * `admin` stays closed in BOTH postures, which is the one direction that
    must not depend on a credential being present.

The keys are fakes and must stay fakes: `clerk_enabled()` asks only that
all three values are non-empty and that the package imports, so a dummy
`pk_test_...` exercises the whole branch and no real secret is ever needed
here. The markers are taken FROM `lib/gate_layouts.py` by rendering its own
card, never re-typed into this file — the rule item 7 states, so that a
fork renaming a button id sees this test move with it instead of rotting
into a vacuous pass.
"""

from __future__ import annotations

import pytest

from lib import access, auth, gate_layouts, page_visibility

# Non-empty and obviously not a credential. `clerk_keys()` reads these three
# names; `clerk_enabled()` additionally requires the vendored package.
FAKE_CLERK = {
    "CLERK_SECRET_KEY": "sk_test_not-a-real-key",
    "CLERK_PUBLISHABLE_KEY": "pk_test_not-a-real-key",
    "CLERK_SIGN_IN_URL": "https://example.test/sign-in",
}


def _ids(component, found=None):
    """Every component id in a Dash tree (same walk as test_gate_layouts)."""
    found = found if found is not None else set()
    comp_id = getattr(component, "id", None)
    if isinstance(comp_id, str):
        found.add(comp_id)
    children = getattr(component, "children", None)
    if isinstance(children, (list, tuple)):
        for child in children:
            _ids(child, found)
    elif children is not None:
        _ids(children, found)
    return found


@pytest.fixture(scope="module")
def gate_markers(app_module):
    """The ids only the sign-in card emits, read off the module that emits them."""
    markers = _ids(gate_layouts.sign_in_layout("Some Page"))
    assert markers, "the sign-in card declares no ids — nothing to assert on"
    return markers


@pytest.fixture
def gated_page(app_module, page_paths):
    """A real registered page, temporarily pinned to `auth` via the board's
    own writer — the same seam /admin/control-board uses in production."""
    import dash

    path = next(p for p in page_paths if p != "/")
    entry = dash.page_registry[
        next(k for k, v in dash.page_registry.items() if v["path"] == path)
    ]
    before = dict(page_visibility._overrides.get(path) or {})
    page_visibility.set_visibility(path, "auth")
    try:
        yield path, entry["layout"]
    finally:
        if before:
            page_visibility._overrides[path] = before
        else:
            page_visibility._overrides.pop(path, None)
        page_visibility._persist()


@pytest.fixture
def configured(monkeypatch):
    for key, value in FAKE_CLERK.items():
        monkeypatch.setenv(key, value)
    monkeypatch.delenv("DISABLE_CLERK", raising=False)
    if not auth.clerk_enabled():
        pytest.fail(
            "three non-empty CLERK_* values and dash_clerk_auth is in "
            "requirements.txt, yet clerk_enabled() is False — the configured "
            "branch cannot be reached, so nothing below would be testing it"
        )
    return True


def test_an_auth_page_renders_the_sign_in_card_when_clerk_is_configured(
    configured, gated_page, gate_markers
):
    """The branch production runs, reached through the real verdict."""
    path, layout = gated_page
    assert access.resolve_page_access(path) == "sign_in"
    rendered = layout()
    assert gate_markers <= _ids(rendered), (
        f"the configured branch did not render the gate card: "
        f"{sorted(gate_markers - _ids(rendered))} missing"
    )


def test_the_same_page_falls_open_with_no_clerk_config(gated_page, gate_markers):
    """Non-vacuity, and the fail-open posture itself.

    Zero-secret — the state every other test in this suite runs in — the same
    `auth` page serves its documentation. If this ever renders the card, the
    test above proves nothing about Clerk being configured.
    """
    path, layout = gated_page
    assert not auth.clerk_enabled(), "conftest's zero-secret boot has drifted"
    assert access.resolve_page_access(path) == "allow"
    assert not (gate_markers <= _ids(layout()))


def test_admin_stays_closed_in_both_postures(monkeypatch, gated_page):
    """The one direction that must not depend on a credential existing.

    `auth` falls open without Clerk because documentation must not brick on a
    missing key; `admin` does the opposite, and a test that only ever ran in
    one posture could not tell the two rules apart.
    """
    path, _layout = gated_page
    monkeypatch.delenv("ALLOW_UNGATED_ADMIN", raising=False)
    page_visibility.set_visibility(path, "admin")

    assert access.resolve_page_access(path) == "forbidden"

    for key, value in FAKE_CLERK.items():
        monkeypatch.setenv(key, value)
    # Configured, but nobody is signed in: the interactive verdict is the
    # sign-in funnel, never the page.
    assert access.resolve_page_access(path) == "sign_in"
