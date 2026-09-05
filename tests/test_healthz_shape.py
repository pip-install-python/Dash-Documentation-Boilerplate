"""`/healthz` declares the FLEET's shape, not just this host's build.

Every machine that reads a satellite — the hub's hourly sweep, the F4
battery, cd.yml's build-match wait, `scripts/network_smoke.py` — reads this
payload BY KEY NAME. That makes the key set a fleet contract and not a local
convenience: a fork may ADD keys (flexlayout's `version`, the reporting
block) and nobody notices, but a fork that RENAMES one answers a different
document than the battery asks for, and every reader sees "absent".

Absent is the failure mode worth a test of its own, because 1.6.28's rule
says absence is NOT-ADOPTED, never not-applicable — so a renamed field does
not read as a bug, it reads as a fork that never adopted the item. Measured
across all thirteen hosts by the ops seat on 2026-08-27: one fork had
renamed `dash_version` to `dash` and dropped `backend`, reported item 5
green (correctly — `python` was there), and nothing in the round could see
it. This is the pin that would have.

The build key is the one exception and it is deliberate: `RENDER_GIT_COMMIT`
does not exist off-platform, so `health_payload` omits it locally. The test
below therefore checks it the only honest way — set the variable and assert
the key appears — rather than asserting its absence means nothing.
"""

from __future__ import annotations

import json
import os
import platform

import pytest

# The keys every fleet reader asks for by name. EXTRAS ARE FINE — this is a
# subset assertion on purpose; a fork's own diagnostics are its business.
FLEET_KEYS = frozenset(
    {"app", "backend", "build", "dash_version", "geo", "ok", "python"}
)

# Renames observed or plausible, mapped to the key they should have been.
# Not a lint of arbitrary extras: each entry is a name that reads as the
# fleet key to a human and as ABSENCE to every machine.
RENAMES = {
    "dash": "dash_version",
    "version": None,          # flexlayout's own field — an ADD, not a rename
    "py": "python",
    "commit": "build",
    "sha": "build",
    "server": "backend",
}


@pytest.fixture(scope="module")
def health(app_module):
    from lib import health

    return health


def test_the_payload_carries_every_fleet_key(health, monkeypatch):
    """With the platform variable present, all seven keys, spelled exactly."""
    monkeypatch.setenv("RENDER_GIT_COMMIT", "0" * 40)
    payload = health.health_payload("flask")
    missing = sorted(FLEET_KEYS - set(payload))
    assert not missing, (
        f"/healthz is missing fleet keys {missing} — every machine that reads "
        f"this host sees them as absent, and absence reads as NOT-ADOPTED. "
        f"Got: {sorted(payload)}"
    )


def test_no_fleet_key_is_present_under_a_renamed_spelling(health, monkeypatch):
    """The failure this item exists for, and the only one a value check misses.

    A renamed key is invisible to every check that reads the VALUE: nothing
    ever asks "is dash_version 4.4.1?", it asks "what is dash_version?" and
    gets None.
    """
    monkeypatch.setenv("RENDER_GIT_COMMIT", "0" * 40)
    payload = health.health_payload("flask")
    for alias, canonical in RENAMES.items():
        if canonical is None:
            continue
        assert not (alias in payload and canonical not in payload), (
            f"/healthz declares {alias!r} but not {canonical!r} — that is the "
            f"rename, not an addition. Extras beside the fleet key are fine; "
            f"a substitute for it is not."
        )


def test_the_values_are_this_process_not_a_constant(health):
    """Non-vacuity: a payload of seven correctly-named empty strings passes a
    key check and tells the fleet nothing."""
    payload = health.health_payload("quart")
    assert payload["ok"] is True
    assert payload["backend"] == "quart", "backend echoes its argument"
    assert payload["python"] == platform.python_version()
    assert payload["dash_version"].count(".") >= 1, payload["dash_version"]


def test_geo_is_declared_because_this_tree_is_above_the_package_floor(
    health, app_module
):
    """`geo` is omitted only on a pre-2.7 package, and the floor forbids one.

    A fork legitimately below the floor records that as a divergence — which
    is the point: recorded, not silently absent. The floor is read off the
    booted module rather than re-imported: `import run` here would execute
    run.py a SECOND time in the same process, re-registering every page.
    """
    assert getattr(app_module, "LLMS_PKG_FLOOR", (0,)) >= (2, 7), (
        "run.py's boot floor is below 2.7 — then an omitted geo block is "
        "correct here and this pin belongs in the fork's divergences"
    )
    payload = health.health_payload("flask")
    assert "geo" in payload, (
        "no geo block: the installed dash-improve-my-llms predates 2.7, which "
        "this repo's boot floor rejects — or the import in lib/health.py broke"
    )
    assert set(payload["geo"]) >= {"configured", "denied"}


def test_the_live_route_serves_the_same_payload(client):
    """The route, not just the builder — a typed FastAPI response model that
    drops a field would leave the builder's test green."""
    response = client.get("/healthz")
    assert response.status == 200, response.status
    payload = json.loads(response.text)
    # `build` alone is environment-dependent; the other six are not.
    missing = sorted((FLEET_KEYS - {"build"}) - set(payload))
    assert not missing, f"the route dropped {missing}; served {sorted(payload)}"


def test_the_geo_block_lists_the_location_headers_this_host_has_seen():
    """1.6.44 item 16. The Cloudflare visitor-location transform is an owner
    click per zone, so the only honest answer to "is it on here?" is the set
    of headers that have actually turned up — and it must be readable from
    outside, or the answer lives in logs nobody reads."""
    from lib.analytics_tracker import header_geo
    from lib.health import health_payload

    header_geo({"CF-IPCountry": "US", "CF-IPCity": "Austin"})
    geo = health_payload("flask", headers={"CF-IPCountry": "US"}).get("geo", {})
    assert "headers_seen" in geo, "the geo block does not report the headers"
    assert isinstance(geo["headers_seen"], list)
    assert "cf-ipcountry" in geo["headers_seen"]


def test_the_geo_block_reports_headers_even_when_the_package_errors():
    """The error branch is the one a host actually hits on an old package —
    losing the field there would make it unreadable exactly when it matters.
    """
    src = (__import__("pathlib").Path(__file__).resolve().parent.parent
           / "lib" / "health.py").read_text()
    error_branch = src.split('"error": True', 1)[0][-400:]
    assert "headers_seen" in error_branch


# ------------------------------- the ledger block (1.6.44 item 20) --


def test_the_ledger_block_has_its_four_keys_and_their_types():
    from lib.health import health_payload

    ledger = health_payload("flask")["ledger"]
    assert set(ledger) == {"path", "persistent", "visits", "reads"}
    assert isinstance(ledger["persistent"], bool)
    assert isinstance(ledger["visits"], int)
    assert isinstance(ledger["reads"], int)
    assert ledger["path"] is None or isinstance(ledger["path"], str)


def test_persistent_is_measured_from_the_path_not_declared(monkeypatch, tmp_path):
    """BOTH directions, so the boolean cannot pass as a constant.

    leaflet ran for weeks with a declared disk and no disk. A blueprint's
    declaration is an intention; this reports the filesystem.
    """
    import lib.analytics_tracker as tracker_mod
    from conftest import REPO_ROOT
    from lib.health import health_payload

    outside = tmp_path / "ledger.json"
    monkeypatch.setattr(tracker_mod, "analytics_path", lambda: outside)
    assert health_payload("flask")["ledger"]["persistent"] is True

    inside = REPO_ROOT / "visitor_analytics.json"
    monkeypatch.setattr(tracker_mod, "analytics_path", lambda: inside)
    assert health_payload("flask")["ledger"]["persistent"] is False, (
        "a path under the app tree is the container filesystem, whatever "
        "the blueprint says"
    )


def test_a_missing_ledger_is_zeros_and_not_an_error(monkeypatch, tmp_path):
    """/healthz must stay 200. A diagnostic that can take the health probe
    down with it is a liability."""
    import lib.analytics_tracker as tracker_mod
    from lib.health import health_payload

    monkeypatch.setattr(tracker_mod, "analytics_path",
                        lambda: tmp_path / "nothing-here.json")
    payload = health_payload("flask")
    assert payload["ok"] is True
    assert payload["ledger"]["visits"] == 0 and payload["ledger"]["reads"] == 0
    assert payload["ledger"]["path"].endswith("nothing-here.json")


def test_a_corrupt_ledger_is_zeros_and_not_an_error(monkeypatch, tmp_path):
    import lib.analytics_tracker as tracker_mod
    from lib.health import health_payload

    broken = tmp_path / "half-written.json"
    broken.write_text('{"visits": [{"path": "/a"}')
    monkeypatch.setattr(tracker_mod, "analytics_path", lambda: broken)
    payload = health_payload("flask")
    assert payload["ok"] is True
    assert payload["ledger"]["visits"] == 0


def test_the_counts_are_the_rows_of_the_file_the_tracker_writes(monkeypatch,
                                                                tmp_path):
    import json as _json

    import lib.analytics_tracker as tracker_mod
    from lib.health import health_payload

    ledger = tmp_path / "a.json"
    ledger.write_text(_json.dumps({
        "visits": [{"path": "/a"}, {"path": "/b"}, {"path": "/c"}],
        "reads": [{"path": "/llms.txt"}],
    }))
    monkeypatch.setattr(tracker_mod, "analytics_path", lambda: ledger)
    block = health_payload("flask")["ledger"]
    assert (block["visits"], block["reads"]) == (3, 1)


def test_the_block_never_carries_row_contents(monkeypatch, tmp_path):
    """Counts, a boolean and a path. Nothing about a visitor."""
    import json as _json

    import lib.analytics_tracker as tracker_mod
    from lib.health import health_payload

    ledger = tmp_path / "a.json"
    ledger.write_text(_json.dumps({
        "visits": [{"path": "/secret", "user_agent": "SECRET-UA",
                    "visitor_key": "deadbeefdeadbeef"}],
        "reads": [],
    }))
    monkeypatch.setattr(tracker_mod, "analytics_path", lambda: ledger)
    serialised = _json.dumps(health_payload("flask")["ledger"])
    for leaked in ("SECRET-UA", "deadbeefdeadbeef", "/secret"):
        assert leaked not in serialised


def test_item_10s_keys_are_still_there(client):
    """A RENAME is still the failure; this block is additive."""
    import json as _json

    body = _json.loads(client.get("/healthz").text)
    for key in ("ok", "backend", "dash_version", "python", "ledger"):
        assert key in body, f"/healthz lost {key}"


def test_the_two_lanes_serve_the_same_keys(client):
    """The ASGI lane's response_model must not narrow the payload.

    Found while building item 20 and it was already live: a pydantic
    response_model drops undeclared fields SILENTLY, so `llms_version` —
    item 1's rider, added two days earlier precisely so the CI-vs-production
    gap would stop being self-reported — was on the Flask lane and absent
    from this one. The template's production is Flask, so nothing said so;
    the fleet's two ASGI forks would have shipped a healthz without it.

    This test is the guard for the CLASS, not for those two keys: every key
    `health_payload` produces must reach the wire, whichever lane answers.
    """
    import json as _json

    from lib.backend import get_backend_info
    from lib.health import health_payload

    served = _json.loads(client.get("/healthz").text)
    expected = health_payload(get_backend_info().name)

    missing = sorted(set(expected) - set(served))
    assert missing == [], (
        f"the {get_backend_info().name} lane's /healthz drops {missing} — a "
        "response_model that narrows the payload is the two-lanes trap with "
        "a type annotation on it"
    )


def test_the_asgi_model_keeps_keys_it_does_not_know_about():
    """Belt to the test above: the next additive key must survive without
    anyone remembering to declare it.

    `lib.asgi_routes` imports fastapi at module level, and CI's matrix
    installs each leg's backend ONLY — so this import is a hard dependency
    that the flask and quart legs do not have. It went red on both
    (ModuleNotFoundError at lib/asgi_routes.py:22) after passing locally,
    because this machine has all three backends installed: running
    `DASH_BACKEND=flask` here proves the flask CODE PATH, never the flask
    leg's DEPENDENCY SET. `importorskip` is the tree's existing precedent
    (test_llms_routes.py:216) and it performs the import rather than asking
    find_spec, which answers yes for an importable-but-broken module.

    THE POSITIVE CONTROL below is the point. A bare skip would make this the
    fourth check-that-cannot-fail in a release about checks that cannot
    fail: on the leg that DOES have fastapi, the import must SUCCEED, and
    skipping there would be a silent loss of the only coverage this test
    provides.
    """
    if os.environ.get("DASH_BACKEND") == "fastapi":
        from lib.asgi_routes import HealthResponse   # must import, never skip
    else:
        pytest.importorskip("fastapi")
        from lib.asgi_routes import HealthResponse

    widened = HealthResponse(backend="fastapi", dash_version="4.4.1",
                             python="3.14.7", a_future_key="kept")
    assert widened.model_dump().get("a_future_key") == "kept", (
        "an undeclared key is dropped — declare extra='allow'"
    )
