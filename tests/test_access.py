"""Access control — the checks that justify this design over the simpler ones.

The package already covers the six-surface gate matrix in its own suite. What
is new *here* is the two-source resolution: a local Clerk session answering for
a person in a browser, and a hub call answering for an agent with a key. So
these tests concentrate on the seam between them, and specifically on what
happens when the hub is unavailable.

From AUTH-NETWORK.md, checks 1 and 3 are the point:

    1. Signed-in browser, hub UNREACHABLE  -> still allowed (local resolution)
    3. Agent with valid key, hub down      -> gated, not 500, not prose

If 1 fails, every satellite's availability is coupled to one host for no
benefit. If 3 fails, an outage either leaks prose or takes the site down.

`configure_access` is process-wide, so `access_on` saves and restores it —
otherwise a gate configured here would leak into every later test in the
session and the failures would look like anything but the cause.
"""

from __future__ import annotations

import re

import pytest

from conftest import CRAWLER_UA
from lib import access, auth, hub_client, page_tiers

GATED_PAGE = "/networks"
PUBLIC_PAGE = "/backends"
VALID_KEY = "k2p_testref_testsig"


@pytest.fixture
def restore_tiers():
    """Any test that registers a tier outside `access_on` must clean up, or the
    inertness assertion below sees a gate a later reader cannot explain."""
    saved = page_tiers.registered()
    yield
    page_tiers._LOCAL_TIERS.clear()
    page_tiers._LOCAL_TIERS.update(saved)


class FakeUser:
    """Stands in for ClerkUser. Only the attributes lib/auth reads."""

    def __init__(self, email="reader@example.com", user_id="user_1",
                 session_id="sess_1", plan=None):
        self.email = email
        self.user_id = user_id
        self.session_id = session_id
        self.plan = plan


@pytest.fixture
def access_on(app_module, monkeypatch):
    """Turn gating on for one test, then put the process back as it was."""
    import dash_improve_my_llms as pkg
    from dash_improve_my_llms import access as pkg_access

    saved_tiers = page_tiers.registered()
    page_tiers.register(GATED_PAGE, "auth")
    hub_client.clear_cache()
    access.configure(force=True)
    try:
        yield pkg
    finally:
        # The package ships reset() for exactly this; using it rather than
        # restoring _config by hand means the teardown cannot drift from
        # whatever configure_access sets next release.
        pkg_access.reset()
        page_tiers._LOCAL_TIERS.clear()
        page_tiers._LOCAL_TIERS.update(saved_tiers)
        hub_client.clear_cache()


@pytest.fixture
def hub_down(monkeypatch):
    """Every hub call fails, the way a real outage does: no exception escapes."""
    def unreachable(route, payload, timeout):
        return None

    monkeypatch.setattr(hub_client, "_post", unreachable)
    monkeypatch.setattr(hub_client, "enabled", lambda: True)
    hub_client.clear_cache()


@pytest.fixture
def hub_allows(monkeypatch):
    def allow(route, payload, timeout):
        return {"verdict": "allow", "ttl": 60}

    monkeypatch.setattr(hub_client, "_post", allow)
    monkeypatch.setattr(hub_client, "enabled", lambda: True)
    hub_client.clear_cache()


def signed_in(monkeypatch, user=None):
    monkeypatch.setattr(auth, "clerk_enabled", lambda: True)
    monkeypatch.setattr(auth, "current_user", lambda: user or FakeUser())


def anonymous(monkeypatch):
    monkeypatch.setattr(auth, "clerk_enabled", lambda: True)
    monkeypatch.setattr(auth, "current_user", lambda: None)


# ---------------------------------------------------------------------------
# The two checks that justify the design
# ---------------------------------------------------------------------------


def test_signed_in_browser_is_allowed_while_the_hub_is_unreachable(
    access_on, hub_down, monkeypatch
):
    """Check 1. The reason Clerk runs on satellites at all.

    Without local resolution every access decision needs the hub, so one host
    being down gates every restricted document on all twenty subdomains.
    """
    signed_in(monkeypatch)
    assert access.check(GATED_PAGE) == "allow"


def test_agent_with_a_key_is_gated_when_the_hub_is_down(
    access_on, hub_down, monkeypatch
):
    """Check 3. Not 500, not prose — gated."""
    anonymous(monkeypatch)
    monkeypatch.setattr(access, "_request_key", lambda: VALID_KEY)
    assert access.check(GATED_PAGE) == "gated"


def test_agent_with_a_valid_key_is_allowed_when_the_hub_answers(
    access_on, hub_allows, monkeypatch
):
    """Check 2."""
    anonymous(monkeypatch)
    monkeypatch.setattr(access, "_request_key", lambda: VALID_KEY)
    assert access.check(GATED_PAGE) == "allow"


def test_the_hub_is_not_consulted_for_a_signed_in_reader(
    access_on, monkeypatch
):
    """Local-first is an ordering claim; this asserts the ordering itself.

    A passing check-1 could also be produced by a hub that happened to allow.

    "Zero hub calls" means the per-reader agent-key endpoints. The page-tiers
    feed is different in kind: one cached per-app fetch per TTL, consulted for
    every path (a hub ceiling must bind even on locally-public pages), and its
    failure resolves to the local tier — so it never couples a signed-in
    reader's access to hub availability, which is what this test protects.
    """
    calls = []
    monkeypatch.setattr(hub_client, "_post", lambda *a, **k: calls.append(a) or None)
    monkeypatch.setattr(hub_client, "enabled", lambda: True)
    signed_in(monkeypatch)
    assert access.check(GATED_PAGE) == "allow"
    agent_key_calls = [c for c in calls if "/api/agent-key/" in c[0]]
    assert agent_key_calls == [], "a signed-in reader triggered a per-reader hub call"


# ---------------------------------------------------------------------------
# Tiers, degradation and the hub ceiling
# ---------------------------------------------------------------------------


def test_public_pages_never_reach_the_session_or_the_hub(access_on, monkeypatch):
    monkeypatch.setattr(auth, "current_user", lambda: pytest.fail("session consulted"))
    monkeypatch.setattr(hub_client, "_post", lambda *a, **k: pytest.fail("hub consulted"))
    assert access.check(PUBLIC_PAGE) == "allow"


def test_admin_tier_gates_a_signed_in_non_admin(access_on, monkeypatch):
    page_tiers.register(GATED_PAGE, "admin")
    signed_in(monkeypatch)
    monkeypatch.setattr(auth, "is_admin_user", lambda user=None: False)
    assert access.check(GATED_PAGE) == "gated"
    monkeypatch.setattr(auth, "is_admin_user", lambda user=None: True)
    assert access.check(GATED_PAGE) == "allow"


def test_hidden_is_deny_even_with_a_session(access_on, monkeypatch):
    page_tiers.register(GATED_PAGE, "hidden")
    signed_in(monkeypatch)
    assert access.check(GATED_PAGE) == "deny"


def test_everything_but_hidden_falls_open_without_clerk(access_on, monkeypatch):
    """Documentation must not brick over a missing credential.

    `hidden` still holds, because it means "there is nothing here" rather than
    "not yet" — and admin surfaces gate on `admin_access_open()`, not on this.
    """
    monkeypatch.setattr(auth, "clerk_enabled", lambda: False)
    for tier, expected in (("auth", "allow"), ("admin", "allow"), ("hidden", "deny")):
        page_tiers.register(GATED_PAGE, tier)
        assert access.check(GATED_PAGE) == expected, tier


def test_the_hub_sets_the_ceiling(restore_tiers):
    """A satellite may restrict further; it may never loosen."""
    page_tiers.register("/x", "public")
    assert page_tiers.effective_tier("/x", "auth") == "auth", "hub ceiling did not hold"
    page_tiers.register("/x", "admin")
    assert page_tiers.effective_tier("/x", "auth") == "admin", "local restriction lost"
    assert page_tiers.effective_tier("/x", None) == "admin", "hub outage changed the tier"


def test_a_hub_published_tier_gates_a_locally_public_page(access_on, monkeypatch):
    """The ceiling, end to end through the real feed: this site says public,
    the hub's /api/page-tiers says auth, an anonymous reader is gated."""
    anonymous(monkeypatch)

    def hub(route, payload, timeout):
        assert route == "/api/page-tiers"
        assert payload == {"app": hub_client.app_id()}
        return {"tiers": {PUBLIC_PAGE: "auth"}, "ttl": 300}

    monkeypatch.setattr(hub_client, "_post", hub)
    monkeypatch.setattr(hub_client, "enabled", lambda: True)
    hub_client.clear_cache()
    assert access.check(PUBLIC_PAGE) == "gated", "hub ceiling not applied"


def test_the_tier_feed_is_fetched_once_per_ttl_not_per_request(monkeypatch):
    calls = []

    def hub(route, payload, timeout):
        calls.append(route)
        return {"tiers": {"/x": "auth"}, "ttl": 300}

    monkeypatch.setattr(hub_client, "_post", hub)
    monkeypatch.setattr(hub_client, "enabled", lambda: True)
    hub_client.clear_cache()
    for _ in range(5):
        assert hub_client.hub_tiers() == {"/x": "auth"}
    assert len(calls) == 1, "every request paid a hub round trip"


def test_a_failed_tier_fetch_is_cached_and_loosens_nothing(
    restore_tiers, monkeypatch
):
    """An outage answers {} (hub unknown -> local tier holds) and is cached,
    so a down hub costs one timeout per window, not one per request."""
    calls = []
    monkeypatch.setattr(hub_client, "_post", lambda *a, **k: calls.append(a) or None)
    monkeypatch.setattr(hub_client, "enabled", lambda: True)
    hub_client.clear_cache()
    for _ in range(5):
        assert hub_client.hub_tiers() == {}
    assert len(calls) == 1, "a down hub was hammered per-request"
    page_tiers.register("/x", "admin")
    assert page_tiers.effective_tier("/x", hub_client.hub_tiers().get("/x")) == "admin"


def test_a_junk_tier_from_the_hub_cannot_loosen_a_local_tier(restore_tiers):
    page_tiers.register("/x", "admin")
    assert page_tiers.effective_tier("/x", "not-a-tier") == "admin"
    assert page_tiers.effective_tier("/x", "public") == "admin"


# ---------------------------------------------------------------------------
# The mint path (nothing calls it on this deployment; forks will)
# ---------------------------------------------------------------------------


def test_current_key_sends_the_token_never_an_asserted_identity(monkeypatch):
    """The hub 401s caller-asserted identity by design — a satellite POSTing
    {"user_id": ...} could claim to be anyone. Only the Clerk session token
    travels, because only Clerk's signature says who the reader is."""
    captured = {}

    def hub(route, payload, timeout):
        captured.update({"route": route, "payload": payload})
        return {"key": "k2p_minted"}

    monkeypatch.setattr(hub_client, "_post", hub)
    monkeypatch.setattr(hub_client, "enabled", lambda: True)
    assert hub_client.current_key("clerk-session-token") == "k2p_minted"
    assert captured["route"] == "/api/agent-key/current"
    assert captured["payload"] == {
        "token": "clerk-session-token", "app": hub_client.app_id()
    }
    assert "user_id" not in captured["payload"]


def test_current_key_degrades_to_none_when_the_hub_is_down(hub_down):
    """None -> the copy button falls back to the plain URL."""
    assert hub_client.current_key("clerk-session-token") is None
    assert hub_client.current_key("") is None


# ---------------------------------------------------------------------------
# What must never leak
# ---------------------------------------------------------------------------


def test_a_key_never_reaches_the_sitemap_or_canonical_tags(access_on, client):
    """Authority is scoped to the response it arrived in.

    A key in a canonical tag or a sitemap entry would be published to every
    crawler that reads them.
    """
    sitemap = client.get(f"/sitemap.xml?key={VALID_KEY}").text
    assert VALID_KEY not in sitemap

    html = client.get(f"{PUBLIC_PAGE}?key={VALID_KEY}", user_agent=CRAWLER_UA).text
    canonicals = re.findall(r'rel="canonical"\s+href="([^"]*)"', html)
    assert canonicals and all(VALID_KEY not in c for c in canonicals)


def test_a_key_never_reaches_a_peer_host(access_on, client):
    """The directory points at other origins; a capability must not travel."""
    body = client.get(f"/llms.txt?key={VALID_KEY}").text
    for line in body.splitlines():
        if "2plot.ai" in line or "leaflet.2plot.dev" in line:
            assert VALID_KEY not in line, f"key leaked to a peer link: {line}"


def test_the_cache_never_stores_the_key_itself():
    hub_client.clear_cache()
    hub_client._cache_put(hub_client._fingerprint(VALID_KEY), "/x", "allow", 60)
    assert all(VALID_KEY not in str(k) for k in hub_client._VERDICT_CACHE)


# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------


def test_markdown_is_byte_identical_with_and_without_a_signed_in_reader(
    access_on, client, monkeypatch
):
    """Check 5. Identity is chrome for people; it must cost an agent nothing."""
    anonymous(monkeypatch)
    anonymous_body = client.get(f"{PUBLIC_PAGE}/llms.txt").text
    signed_in(monkeypatch)
    signed_in_body = client.get(f"{PUBLIC_PAGE}/llms.txt").text
    assert anonymous_body == signed_in_body


def test_viewer_identity_uses_session_first_seen_not_the_token_iat(monkeypatch):
    """A Clerk session token refreshes about every 60 seconds, so its `iat`
    renders a "signed in since" clock that resets. This must be stable."""
    monkeypatch.setattr(auth, "clerk_enabled", lambda: True)
    monkeypatch.setattr(auth, "current_user", lambda: FakeUser(session_id="sess_stable"))
    auth._SESSION_FIRST_SEEN.clear()
    first = auth.viewer_identity()
    second = auth.viewer_identity()
    assert first["since"] == second["since"]
    assert first["name"] == "reader@example.com"


def test_viewer_identity_is_none_when_nobody_is_signed_in(monkeypatch):
    monkeypatch.setattr(auth, "clerk_enabled", lambda: True)
    monkeypatch.setattr(auth, "current_user", lambda: None)
    assert auth.viewer_identity() is None


# ---------------------------------------------------------------------------
# Inertness
# ---------------------------------------------------------------------------


def test_access_control_is_off_when_every_page_is_public():
    """A fork inherits the machinery without inheriting a gate.

    It also keeps the per-request check off the hot path for the sites — most
    of them — that have nothing to gate.
    """
    assert not access.gating_configured()
    assert access.configure() is False


def test_a_check_that_raises_degrades_to_gated(access_on, monkeypatch):
    """The package's fail-safe, asserted from this side of the contract.

    Not `allow` — a bug in this repo's policy must not publish gated prose.
    Not `deny` — a bug must not black-hole every document on the site.
    """
    from dash_improve_my_llms import access as pkg_access

    def boom(path):
        raise RuntimeError("policy bug")

    monkeypatch.setattr(pkg_access._config, "check", boom)
    assert pkg_access.resolve(GATED_PAGE) == "gated"
