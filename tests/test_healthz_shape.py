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
