"""Every /admin page hides itself from everyone who is not an admin.

1.6.45 rider, born on the hub 2026-09-10: `/admin/bot-traffic` rendered its
whole board to anonymous and stranger browsers for a week, because its layout
never asked `is_admin_email` — and EVERY SUITE PASSED. The suites run with
Clerk OFF, where gates fall open by convention, so no test ever forced Clerk
ON and asked the question.

This file asks it GENERICALLY. It enumerates admin pages from
`dash.page_registry` rather than from a hand-written list, so a page added
next year is covered the day it is registered, without anyone remembering
this file exists. That is the whole point: the hub's defect was not a missing
gate anybody decided against, it was a gate nobody noticed was absent.
"""
from __future__ import annotations

import contextlib
import pathlib

import pytest
from dash.development.base_component import Component
from dash.exceptions import PreventUpdate

OWNER = "owner@example.test"
STRANGER = "stranger@example.test"


class _User:
    """The shape `lib.auth` reads off a Clerk user."""

    def __init__(self, email):
        self.email = email
        self.id = f"user_{email.split('@')[0]}"


# --------------------------------------------------------------- the pages --


@pytest.fixture(scope="module")
def admin_pages(app_module):
    import dash

    pages = [entry for entry in dash.page_registry.values()
             if (entry.get("path") or "") == "/admin"
             or (entry.get("path") or "").startswith("/admin/")]
    assert pages, (
        "no /admin pages in the registry — this file would pass by sweeping "
        "nothing, which is the defect it exists to prevent"
    )
    return pages


def test_the_admin_pages_are_enumerated_from_the_registry(admin_pages):
    """Detect: the file exists and enumerates from the registry."""
    paths = sorted(p["path"] for p in admin_pages)
    assert paths, paths
    assert all(p.startswith("/admin") for p in paths)


# ------------------------------------------------------- Clerk forced ON --


@pytest.fixture
def clerk_on(monkeypatch):
    """Force the gated regime, and force it EVERYWHERE the name was bound.

    `from lib.auth import clerk_enabled` copies the function object into each
    page module, so patching `lib.auth.clerk_enabled` alone leaves every page
    calling the original. The hub's defect hid behind exactly this kind of
    gap between what a test patches and what the code calls.
    """
    import lib.auth as auth

    state = {"user": None}

    def _clerk_enabled():
        return True

    def _current_user():
        return state["user"]

    def _is_admin_user(user=None):
        user = state["user"] if user is None else user
        return bool(user) and getattr(user, "email", "").lower() == OWNER

    monkeypatch.setattr(auth, "clerk_enabled", _clerk_enabled)
    monkeypatch.setattr(auth, "current_user", _current_user)
    monkeypatch.setattr(auth, "is_admin_user", _is_admin_user)
    monkeypatch.setattr(auth, "admin_access_open", lambda: False)

    import sys

    for name, module in list(sys.modules.items()):
        if not (name.startswith("pages.") or name.startswith("components.")
                or name in ("pages", "components")):
            continue
        for attr, replacement in (("clerk_enabled", _clerk_enabled),
                                  ("current_user", _current_user),
                                  ("is_admin_user", _is_admin_user),
                                  ("admin_access_open", lambda: False)):
            if hasattr(module, attr):
                monkeypatch.setattr(module, attr, replacement, raising=False)

    return state


def _ids(node, found=None):
    found = set() if found is None else found
    if isinstance(node, (list, tuple)):
        for child in node:
            _ids(child, found)
        return found
    if not isinstance(node, Component):
        return found
    identifier = getattr(node, "id", None)
    if isinstance(identifier, str):
        found.add(identifier)
    children = getattr(node, "children", None)
    if children is not None:
        _ids(children, found)
    return found


def _render(entry, clerk_on, email):
    clerk_on["user"] = _User(email) if email else None
    layout = entry["layout"]
    return _ids(layout() if callable(layout) else layout)


# ------------------------------------------------------------ the renders --


def test_no_admin_board_renders_for_anonymous_or_stranger(admin_pages, clerk_on):
    """(3) The owner's board and the other two must share NO component id."""
    for entry in admin_pages:
        owner_ids = _render(entry, clerk_on, OWNER)
        assert owner_ids, (
            f"{entry['path']}: the OWNER's render carries no component ids, so "
            "the comparison below is vacuous — a static layout would pass this "
            "file while exposing everything"
        )
        for label, email in (("anonymous", None), ("stranger", STRANGER)):
            other = _render(entry, clerk_on, email)
            leaked = owner_ids & other
            assert not leaked, (
                f"{entry['path']}: the {label} render shares {sorted(leaked)[:5]} "
                f"with the owner's board — the gate is not hiding it"
            )


# ---------------------------------------------------------- the callbacks --


@contextlib.contextmanager
def _callback_context():
    """A minimal Dash callback context, with a pattern-matching trigger.

    Needed because a callback that reads `ctx.triggered_id` raises a
    missing-context error OUTSIDE one — before it ever reaches its gate. The
    first version of this test invoked the callbacks bare, so the control
    board's write callback failed on the context and never exercised the
    admin check at all: the test would have passed a board with no gate for
    the same reason it failed a board that has one.

    The trigger is a pattern-matching id so `triggered_id` is a dict, which
    is what that callback requires before it reaches the gate.
    """
    from dash._callback_context import context_value
    from dash._utils import AttributeDict

    trigger = '{"path":"/backends","type":"cb-vis"}.value'
    token = context_value.set(AttributeDict({
        "triggered_inputs": [{"prop_id": trigger, "value": None}],
    }))
    try:
        yield
    finally:
        try:
            context_value.reset(token)
        except Exception:
            pass


# The names a refusal must be guarded by to count as a GATE. A refusal
# raised from any other line is the callback declining its own placeholder
# arguments, which is not a gate at all.
_GATE_NAMES = ("is_admin_user", "is_admin_email", "admin_access_open",
               "clerk_enabled", "is_owner", "_is_owner")


def _guard_line_for(traceback_obj):
    """(file, line number, guarding condition) for the frame that raised.

    Walks to the LAST frame — the one that actually raised — then back up the
    source to the nearest `if`/`elif` at a smaller indent, which is the
    condition the `raise` sits under.
    """
    frame = traceback_obj
    while frame.tb_next is not None:
        frame = frame.tb_next
    filename = frame.tb_frame.f_code.co_filename
    lineno = frame.tb_lineno

    try:
        lines = pathlib.Path(filename).read_text().splitlines()
    except OSError:
        return filename, lineno, ""

    raising = lines[lineno - 1]
    indent = len(raising) - len(raising.lstrip())
    for index in range(lineno - 2, -1, -1):
        candidate = lines[index]
        if not candidate.strip():
            continue
        candidate_indent = len(candidate) - len(candidate.lstrip())
        if candidate_indent < indent and candidate.lstrip().startswith(
                ("if ", "elif ")):
            return filename, lineno, candidate.strip()
        if candidate_indent < indent:
            indent = candidate_indent
    return filename, lineno, ""


def _refusal_verdict(function, arity, caller_is_owner=False):
    """How this callback refused: "gate", "own line", or "did not refuse".

    THE FOURTH SHAPE (ops, from the hub's build of this test): a callback
    whose first line declines placeholder arguments —
    `if not n: raise PreventUpdate` — satisfies "asserts PreventUpdate" while
    having NO owner gate at all. Asserting that something was raised is not
    the same as asserting the door is shut, so the raising LINE has to be
    identified and its guard read.
    """
    import sys

    try:
        function(*([None] * arity))
    except PreventUpdate:
        _f, lineno, condition = _guard_line_for(sys.exc_info()[2])
        if any(name in condition for name in _GATE_NAMES):
            return "gate", condition
        return "own line", f"line {lineno}: {condition or '<no guard>'}"
    except Exception as exc:
        return "did not refuse", f"{type(exc).__name__}: {exc}"
    return "did not refuse", "returned normally"


def _admin_callbacks(admin_pages):
    """Every callback DEFINED BY an admin page's module.

    Matched on the function's `__module__` against the registry entry's
    `module`, not on component ids appearing in a callback key. The first
    version matched ids loosely and collected unrelated callbacks —
    `url.href`, the navbar's — which then did not raise PreventUpdate
    because they were never gated in the first place, and the assertion
    failed for a reason that had nothing to do with admin gating.

    A gated layout only hides the UI: the callback endpoint stays reachable
    by anyone who can POST a reconstructed component id, so the gate has to
    run there too.
    """
    import dash

    modules = {entry.get("module") for entry in admin_pages}
    modules.discard(None)
    registry = getattr(dash._callback, "GLOBAL_CALLBACK_MAP", {})
    found = []
    for key, spec in registry.items():
        function = spec.get("callback") if isinstance(spec, dict) else None
        if function is None:
            continue
        if getattr(function, "__module__", None) in modules:
            # THE USER'S OWN FUNCTION, not Dash's wrapper. The registry holds
            # the wrapper, and invoking it needs a complete callback context
            # (`KeyError: 'outputs_list'`) which it raises BEFORE reaching any
            # gate — so a test that called it would report "did not refuse"
            # for every callback, gated or not. `__wrapped__` is where the
            # gate lives.
            found.append((key, getattr(function, "__wrapped__", function)))
    return found


def test_admin_callbacks_refuse_anonymous_and_stranger(admin_pages, clerk_on):
    """(4) Invoke each admin callback as anonymous and as a stranger."""

    targeted = _admin_callbacks(admin_pages)
    assert targeted, (
        "no callback is defined by an admin page's module — either the boards "
        "are inert or this enumeration is looking in the wrong place; both "
        "make the assertion below meaningless"
    )

    import inspect

    verdicts = []
    for _key, function in targeted:
        try:
            arity = len(inspect.signature(function).parameters)
        except (TypeError, ValueError):
            arity = 0
        for label, email in (("anonymous", None), ("stranger", STRANGER)):
            clerk_on["user"] = _User(email) if email else None
            with _callback_context():
                verdict, detail = _refusal_verdict(function, arity)
            verdicts.append((function.__name__, label, verdict, detail))

    not_gated = [v for v in verdicts if v[2] != "gate"]
    assert not not_gated, (
        "these (callback, caller) pairs were not refused BY A GATE: "
        + "; ".join(f"{name} as {who}: {verdict} — {detail}"
                    for name, who, verdict, detail in not_gated)
    )
    refused = len(verdicts)

    assert refused == 2 * len(targeted), (
        f"{refused} of {2 * len(targeted)} (callback, caller) pairs refused — "
        "every admin callback must raise PreventUpdate for BOTH an anonymous "
        "and a stranger caller; a gated layout only hides the UI"
    )


# ------------------------------------------------------- the convention --


def test_gates_fall_open_without_clerk_by_decision_not_by_accident():
    """(5) State the convention, so it is a decision rather than a surprise.

    Everything else in this app degrades to public without Clerk, because
    documentation must never brick over a missing credential. Admin surfaces
    are the exception and fail CLOSED — `admin_access_open()` is False by
    default and `ALLOW_UNGATED_ADMIN=1` is the local escape hatch.

    This is also why the suite's ordinary runs cannot see an admin leak: they
    run with Clerk off, where a missing gate and a present one look the same.
    The hub lost a week to exactly that.
    """
    import lib.auth as auth

    assert auth.admin_access_open() is False, (
        "ALLOW_UNGATED_ADMIN is set in this environment — admin gates are "
        "open and the tests above are measuring the escape hatch"
    )
    doc = auth.admin_access_open.__doc__ or ""
    assert "fails open by design" in doc or "fail" in doc.lower()


# ---------------- the fourth shape: refused by its own line, not a gate --


def _ungated_callback(value):
    """A callback that declines placeholder arguments and has NO gate.

    This is the shape the addendum names: it raises PreventUpdate for every
    caller the test tries, so "asserts PreventUpdate" is satisfied while the
    door stands open for anyone who sends a real value.
    """
    if not value:
        raise PreventUpdate
    return {"the board": "everything"}


def _gated_callback(value):
    """The same callback with the gate the other one is missing."""
    import lib.auth as auth

    if not auth.is_admin_user():
        raise PreventUpdate
    if not value:
        raise PreventUpdate
    return {"the board": "everything"}


def test_an_own_line_refusal_is_not_a_gate(clerk_on):
    """The addendum's acceptance.

    Without this distinction the test asserts only that SOMETHING was raised,
    which a callback with no owner check satisfies trivially — it would pass
    on exactly the exposure it exists to catch.
    """
    clerk_on["user"] = None
    with _callback_context():
        verdict, detail = _refusal_verdict(_ungated_callback, 1)
    assert verdict == "own line", (verdict, detail)


def test_a_gated_refusal_is_recognised_as_one(clerk_on):
    """The other direction, so "own line" cannot become the answer for
    everything and quietly fail a correct board."""
    clerk_on["user"] = None
    with _callback_context():
        verdict, detail = _refusal_verdict(_gated_callback, 1)
    assert verdict == "gate", (verdict, detail)
    assert "is_admin_user" in detail


def test_the_real_admin_callbacks_refuse_at_their_gate(admin_pages, clerk_on):
    """And the measurement this tree actually produces, named rather than
    implied: both admin callbacks refuse at a line guarded by the gate."""
    import inspect

    seen = {}
    for _key, function in _admin_callbacks(admin_pages):
        arity = len(inspect.signature(function).parameters)
        clerk_on["user"] = None
        with _callback_context():
            verdict, detail = _refusal_verdict(function, arity)
        seen[function.__name__] = (verdict, detail)

    assert seen, "no admin callbacks found"
    for name, (verdict, detail) in seen.items():
        assert verdict == "gate", f"{name}: {verdict} — {detail}"
