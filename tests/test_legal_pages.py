"""The Legal section — 1.6.44 item 15.

The pages themselves are ordinary. What is not ordinary, and what these
tests exist for, is the relationship between the PRIVACY page's prose and
the code it describes: the page is generated from the mechanism, so a
tracker that starts storing something the page does not mention must turn a
test red rather than making the page quietly false.
"""
from __future__ import annotations

import pytest

from conftest import REPO_ROOT


@pytest.fixture(scope="module")
def registry(app_module):
    import dash

    return {e["path"]: e for e in dash.page_registry.values()}


# ----------------------------------------------------------- the section --


def test_legal_is_a_category_of_its_own():
    """Item 15's detect. Never inside Components — a fork's Components
    section is about the component it documents."""
    from lib.constants import CATEGORY_ORDER

    assert "Legal" in CATEGORY_ORDER
    assert CATEGORY_ORDER.index("Legal") == len(CATEGORY_ORDER) - 1, (
        "Legal must be the last of the app's own sections, so it renders "
        "directly above Admin (which the navbar builds separately)"
    )


def test_both_pages_are_registered(registry):
    for path in ("/terms", "/privacy"):
        assert path in registry, f"{path} is not registered"
        assert registry[path]["category"] == "Legal"


def test_the_section_renders_in_order(app_module):
    import dash

    from components.navbar import sections_for

    sections = dict((title, [e["name"] for e in entries])
                    for title, entries in sections_for(dash.page_registry.values()))
    assert sections.get("Legal") == ["Terms of Use", "Privacy"]
    assert list(sections)[-1] == "Legal"


# ------------------------------------------------- one string, two lanes --


@pytest.mark.parametrize("path,heading", [("/terms", "# Terms of Use"),
                                          ("/privacy", "# Privacy")])
def test_the_browser_and_the_machine_get_the_same_document(client, path, heading):
    """A site cannot have two versions of its own terms."""
    from pages.legal import PRIVACY_DOC, TERMS_DOC

    source = TERMS_DOC if path == "/terms" else PRIVACY_DOC
    assert source.startswith(heading)

    machine = client.get(f"{path}/llms.txt")
    assert str(machine.status).startswith("200") or machine.status == 200
    assert machine.text.splitlines()[0] == heading

    browser = client.get(path)
    assert str(browser.status).startswith("200") or browser.status == 200


def test_both_pages_are_in_the_root_index(client):
    """Acceptance: /terms/llms.txt and /privacy/llms.txt present in the
    root index, not merely reachable."""
    body = client.get("/llms.txt").text
    assert "/terms" in body and "/privacy" in body


# ------------------------------------ the privacy page describes the code --


def test_the_privacy_page_names_every_field_the_tracker_stores(client):
    """The load-bearing test of this item.

    A visit row's keys are read from the TRACKER, not from a list here, and
    each must be accounted for on the page. A new field that nobody
    describes fails this test — which is the only way a generated-from-the-
    mechanism page stays true after the mechanism moves.
    """
    from lib.analytics_tracker import AnalyticsTracker
    from pages.legal import PRIVACY_DOC

    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmp:
        tracker = AnalyticsTracker(data_file=Path(tmp) / "a.json")
        tracker.track_visit(
            "/backends",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "203.0.113.9",
            headers={"CF-IPCountry": "US"},
        )
        tracker.flush()
        import json

        # A CRAWLER row too — the first version of this test only built a
        # browser row, so the five keys a bot row carries were never checked
        # against the page at all (Fable audit, 1.6.44).
        tracker.track_visit(
            "/backends",
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "203.0.113.10",
            headers={"CF-IPCountry": "US"},
        )
        tracker.flush()
        visits = json.loads((Path(tmp) / "a.json").read_text())["visits"]
        row = {}
        for stored in visits:
            row.update(stored)          # union of the browser and bot shapes
        assert any(v.get("device_type") == "bot" for v in visits), (
            "no crawler row was produced — the bot-only keys are unchecked"
        )

    described = {
        "timestamp": "time",
        "path": "path",
        "device_type": "device type",
        "user_agent": "User-Agent",
        "visitor_key": "visitor key",
        "location": "location",
        # The crawler-row extras. The page describes them in one sentence
        # ("Crawler rows additionally carry the vendor identity the
        # classifier determined — which bot it was, and whether it
        # verified"), so they map to that phrase rather than to five.
        "bot_type": "vendor identity",
        "vendor_key": "vendor identity",
        "vendor_class": "vendor identity",
        "verified": "vendor identity",
        "lane": "vendor identity",
    }
    undescribed = sorted(set(row) - set(described))
    assert undescribed == [], (
        f"the tracker stores {undescribed} and the privacy page does not "
        "mention it"
    )
    for phrase in described.values():
        assert phrase in PRIVACY_DOC, f"the page never says {phrase!r}"


def test_the_privacy_page_claims_no_raw_address_and_the_code_agrees():
    from lib.analytics_tracker import KEEP_CLIENT_IP
    from pages.legal import PRIVACY_DOC

    assert "Your IP address" in PRIVACY_DOC
    assert "ANALYTICS_KEEP_CLIENT_IP" in PRIVACY_DOC, (
        "the page must name the switch, or it is describing a default as an "
        "absolute"
    )
    assert KEEP_CLIENT_IP is False, (
        "this host keeps client IPs while its privacy page says it does not"
    )


def test_the_privacy_page_claims_no_outbound_lookup_and_the_code_agrees():
    import ast

    from pages.legal import PRIVACY_DOC

    flat = " ".join(PRIVACY_DOC.split())
    assert "makes no outbound request about you" in flat

    tree = ast.parse((REPO_ROOT / "lib" / "analytics_tracker.py").read_text())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    # Every module that can open an outbound connection, not just the two the
    # first version named: http.client, socket, httpx and aiohttp would all
    # have sailed past it (Fable audit, 1.6.44).
    OUTBOUND = {"requests", "urllib", "urllib3", "http", "httpx", "aiohttp",
                "socket", "ftplib", "telnetlib", "smtplib"}
    reachable = OUTBOUND & imported
    assert not reachable, (
        f"the tracker can still make an outbound request via {sorted(reachable)}"
    )


def test_the_privacy_page_names_the_headers_the_tracker_reads():
    from lib.analytics_tracker import _GEO_HEADERS
    from pages.legal import PRIVACY_DOC

    for header in _GEO_HEADERS:
        pretty = header.replace("cf-ip", "CF-IP").replace("cf-", "CF-")
        assert pretty.lower() in PRIVACY_DOC.lower(), (
            f"the tracker reads {header} and the page does not say so"
        )


def test_the_privacy_page_points_at_a_surface_that_confirms_it(client):
    """The page tells a reader where to check the claim themselves; that
    surface has to exist."""
    from pages.legal import PRIVACY_DOC

    assert "geo.headers_seen" in PRIVACY_DOC
    assert "/healthz" in PRIVACY_DOC
    body = client.get("/healthz").text
    assert "headers_seen" in body
