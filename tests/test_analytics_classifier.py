"""ONE classifier — the tracker delegates to dash_improve_my_llms.classify().

Until 1.6.34 lib/analytics_tracker.py carried its own User-Agent lists: it
filed ClaudeBot (Anthropic's TRAINING crawler) under "search", still named
the retired `anthropic-ai` / `claude-web` tokens, and counted every UA-less
or library client (httpx, Go-http-client, node-fetch) as a human. Every
host in the fleet reported those numbers to the hub. These pins hold the
delegation in place — each UA string is one taken from the wire on
2026-08-29 — and the last test greps the module so a list cannot come
back quietly.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from lib.analytics_tracker import AnalyticsTracker
from lib.constants import INTERNAL_UA_TOKEN

CLAUDEBOT = ("Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; "
             "ClaudeBot/1.0; +claudebot@anthropic.com)")
GPTBOT = "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)"
GOOGLEBOT = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
HTTPX = "python-httpx/0.27.0"
CHROME = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")


@pytest.fixture
def tracker(tmp_path, monkeypatch):
    monkeypatch.setenv("ANALYTICS_GEO_LOOKUP", "0")
    return AnalyticsTracker(tmp_path / "ledger.json")


def _rows(tracker):
    tracker.flush()
    path = Path(tracker.data_file)
    if not path.exists():        # nothing written → the file is never created
        return []
    return json.loads(path.read_text())["visits"]


def _one(tracker, ua):
    tracker.track_visit("/", ua, "203.0.113.9")
    rows = _rows(tracker)
    assert len(rows) == 1, rows
    return rows[0]


@pytest.mark.parametrize("ua, bot_type, vendor_key", [
    (CLAUDEBOT, "training", "claudebot"),
    (GPTBOT, "training", "gptbot"),
    (GOOGLEBOT, "traditional", "googlebot"),
    (HTTPX, "unknown", None),
    ("", "unknown", None),
    (None, "unknown", None),
])
def test_crawler_lane_rows(tracker, ua, bot_type, vendor_key):
    assert tracker.is_bot(ua) is True
    assert tracker.detect_bot_type(ua) == bot_type
    row = _one(tracker, ua)
    assert row["device_type"] == "bot"
    assert row["bot_type"] == bot_type
    assert row["vendor_key"] == vendor_key
    assert row["lane"] == "crawler"
    assert row["verified"] in ("verified", "unverified", "n/a")


def test_claudebot_is_training_and_unverifiable(tracker):
    """The finding that produced this file: ClaudeBot was 'search' for a
    year. And Anthropic publishes no IP ranges, so `verified` is n/a — a
    property of the vendor, never a defect on this host."""
    row = _one(tracker, CLAUDEBOT)
    assert row["bot_type"] == "training"
    assert row["vendor_class"] == "training"
    assert row["verified"] == "n/a"


def test_a_browser_row_carries_no_vendor_keys(tracker):
    """Human rows carry no vendor identity — the rollup's v3 tests must not
    move on adoption.

    THE KEY SET MOVED AT 1.6.44 (item 16), and this is the fork-owned seam
    the item warned about: `ip_address` is gone from a default-config row and
    `visitor_key` has taken its place. A fork porting item 16 will see this
    test fail, and that failure is the item landing, not a regression.
    """
    assert tracker.is_bot(CHROME) is False
    row = _one(tracker, CHROME)
    assert row["device_type"] == "desktop"
    assert set(row) <= {"timestamp", "path", "device_type", "user_agent",
                        "visitor_key", "ip_address", "location"}, row
    assert "ip_address" not in row, (
        "a raw address is in a default-config row — item 16 is not applied, "
        "or ANALYTICS_KEEP_CLIENT_IP leaked into the test environment"
    )
    assert row["visitor_key"], "no visitor_key: sessions collapse to the UA"


def test_internal_traffic_is_still_dropped_before_classification(tracker):
    tracker.track_visit("/", f"Mozilla/5.0 {INTERNAL_UA_TOKEN}-sweep", "203.0.113.9")
    assert _rows(tracker) == []


def test_the_module_carries_no_user_agent_list():
    """The grep. A token the registry lacks is a pushback to the package,
    never a list here (.claude/CLAUDE.md trap)."""
    src = (Path(__file__).resolve().parent.parent / "lib" / "analytics_tracker.py").read_text()
    code = "\n".join(
        line for line in src.splitlines()
        if not line.lstrip().startswith("#")
    )
    # Strip the module docstring — it names the old tokens to explain why
    # they are gone; the assertion is about CODE.
    code = re.sub(r'^"""[\s\S]*?"""', "", code, count=1)
    survivors = [t for t in ("'anthropic-ai'", "'claude-web'", "'perplexitybot'",
                             "'gptbot'", "'claudebot'", "'googlebot'", "'bingbot'",
                             "'headlesschrome'", "'phantomjs'", "'pingdom'")
                 if t in code]
    assert survivors == [], f"a hand-written UA list is back: {survivors}"
    assert "from dash_improve_my_llms import classify" in src


# ------------------------------------------- prefer, then derive (item 8) --


def test_a_package_provided_vendor_class_passes_through_untouched():
    """Item 8's acceptance. The package's answer wins, always.

    Deliberately conflicting fixture: the classification says `search` for a
    vendor whose registry entry says something else. A fork that derives
    unconditionally would return the registry's answer and silently disagree
    with the package that produced the row.
    """
    import lib.analytics_tracker as tracker_mod

    fixture = {
        "lane": "crawler",
        "bot_type": "search",
        "vendor_key": "googlebot",
        "vendor_class": "a-class-only-the-package-knows",
        "verified": "yes",
    }
    original = tracker_mod.classify
    tracker_mod.classify = lambda ua, ip=None: dict(fixture)
    try:
        result = tracker_mod._classify("anything")
    finally:
        tracker_mod.classify = original

    assert result["vendor_class"] == "a-class-only-the-package-knows"
    assert result["verified"] == "yes"


def test_the_class_is_derived_only_when_the_event_omits_it():
    """The other direction, so "prefer" cannot pass as "always derive".

    A floor below 2.9 (or a vendor matched without a class) leaves the field
    absent; the registry — the package's own, never a local table — fills it.
    """
    import lib.analytics_tracker as tracker_mod

    original = tracker_mod.classify
    tracker_mod.classify = lambda ua, ip=None: {
        "lane": "crawler", "bot_type": "traditional",
        "vendor_key": "googlebot", "verified": "n/a",
    }
    try:
        result = tracker_mod._classify("anything")
    finally:
        tracker_mod.classify = original

    from dash_improve_my_llms.vendors import get_vendor

    assert result["vendor_class"] == get_vendor("googlebot").cls
    assert result["vendor_class"] is not None, (
        "the registry no longer classes googlebot — the derive path is dead"
    )


def test_the_derivation_reads_the_packages_registry_and_not_a_local_table():
    """There is ONE classifier, and there is one registry with it."""
    from conftest import REPO_ROOT

    src = "\n".join(
        line for line in
        (REPO_ROOT / "lib" / "analytics_tracker.py").read_text().splitlines()
        if not line.lstrip().startswith("#")
    )
    assert "from dash_improve_my_llms.vendors import get_vendor" in src
    block = src.split("def _vendor_class_from_registry", 1)[1].split("\ndef ", 1)[0]
    assert "{" not in block.replace("{}", ""), (
        "a literal mapping in the derive path is a second registry"
    )


def test_an_unknown_vendor_derives_nothing_rather_than_guessing():
    from lib.analytics_tracker import _vendor_class_from_registry

    assert _vendor_class_from_registry("not-a-real-vendor") is None
    assert _vendor_class_from_registry(None) is None
    assert _vendor_class_from_registry("") is None


# ------------------------------- privacy by design (1.6.44 item 16) --


def test_no_raw_address_is_stored_by_default(tracker):
    """(a) The address is resolved, used, and dropped."""
    tracker.track_visit("/backends", CHROME, "203.0.113.42")
    row = _rows(tracker)[-1]
    assert "ip_address" not in row
    assert "203.0.113.42" not in json.dumps(row), (
        "the address survived somewhere in the row"
    )


def test_the_operator_can_still_opt_in(monkeypatch, tracker):
    """The switch record_read has always honoured, now honoured here too."""
    import lib.analytics_tracker as mod

    monkeypatch.setattr(mod, "KEEP_CLIENT_IP", True)
    tracker.track_visit("/backends", CHROME, "203.0.113.43")
    row = _rows(tracker)[-1]
    assert row["ip_address"] == "203.0.113.43"
    assert row["visitor_key"], "the hash is kept even when the address is"


def test_the_visitor_key_is_keyed_and_one_way():
    """An unsalted hash of an IPv4 address is a reversible encoding of it —
    the space is small enough to enumerate in seconds."""
    import hashlib

    from lib.analytics_tracker import visitor_key

    key = visitor_key("203.0.113.44", "Chrome")
    assert key != hashlib.sha256(b"203.0.113.44|Chrome").hexdigest()[:16], (
        "the digest is unkeyed — an attacker enumerates the address space"
    )
    assert visitor_key("203.0.113.44", "Chrome") == key          # stable
    assert visitor_key("203.0.113.45", "Chrome") != key          # separates
    assert visitor_key("203.0.113.44", "Firefox") != key
    assert len(key) == 16 and all(c in "0123456789abcdef" for c in key)


def test_the_lookup_is_gone_from_the_code_not_merely_disabled():
    """(b) Detect, done the way item 13 requires.

    The item words this as "no ip-api string in lib/", which CANNOT pass on a
    tree that documents the removal — this module explains it in two comments
    and would fail its own detect. So the detect is on the CODE: the module
    imports nothing that can make an outbound request, and none of the
    removed callables survive.
    """
    import ast

    from conftest import REPO_ROOT

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

    defined = {n.name for n in ast.walk(tree)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    assert defined, "parsed no functions — the AST read swept nothing"
    for gone in ("_geolocate", "geo_for", "get_geolocation", "_backfill_geo"):
        assert gone not in defined, f"{gone} is still defined"


def test_location_comes_from_whatever_the_edge_sent(tracker):
    """(c) Both directions, so the defensive read cannot pass as a constant."""
    tracker.track_visit("/backends", CHROME, "203.0.113.46", headers={
        "CF-IPCountry": "US", "CF-IPCity": "Austin", "CF-Region": "Texas",
        "CF-IPLatitude": "30.27", "CF-IPLongitude": "-97.74",
    })
    rich = _rows(tracker)[-1]["location"]
    assert rich["country"] == "US" and rich["city"] == "Austin"
    assert rich["region"] == "Texas" and rich["latitude"] == "30.27"

    tracker.track_visit("/backends", CHROME, "203.0.113.47",
                        headers={"CF-IPCountry": "GB"})
    bare = _rows(tracker)[-1]["location"]
    assert bare["country"] == "GB"
    assert "city" not in bare and "latitude" not in bare, (
        "a header that did not arrive produced a value anyway"
    )

    tracker.track_visit("/backends", CHROME, "203.0.113.48", headers={})
    assert "location" not in _rows(tracker)[-1]


def test_the_headers_this_host_has_seen_are_readable():
    """Listed additively on /healthz's geo block, so "is the transform on?"
    is answerable without reading logs."""
    from lib.analytics_tracker import geo_headers_seen, header_geo

    header_geo({"CF-IPCountry": "US", "CF-IPCity": "Austin"})
    seen = geo_headers_seen()
    assert "cf-ipcountry" in seen and "cf-ipcity" in seen
    assert seen == sorted(seen)


def test_this_tracker_synthesises_no_geo_for_local_addresses():
    """The conditional fleet check, run rather than assumed.

    pip-docs+ hands local/private addresses one of ten hard-coded sample
    cities keyed on the session id — rows indistinguishable from measurement
    once written. This tree has never had it; the check is cheap and the
    absence is worth pinning.
    """
    from conftest import REPO_ROOT

    src = (REPO_ROOT / "lib" / "analytics_tracker.py").read_text()
    for token in ("sample_locations", "Mumbai", "SAMPLE_CITIES"):
        assert token not in src, f"synthesised geo found: {token}"


def test_the_visitor_salt_is_never_committable():
    """It is key material.

    Caught the hard way while building item 16: the salt is generated beside
    the ledger, the ledger's default location is the repo root, and a
    `git add -A` swept it into the commit. A committed salt makes every
    `visitor_key` in every fork of this template computable by anyone with
    the repository — which is exactly the property the hash exists to
    provide.
    """
    from conftest import REPO_ROOT

    ignored = (REPO_ROOT / ".gitignore").read_text().splitlines()
    assert ".visitor_salt" in [ln.strip() for ln in ignored], (
        ".visitor_salt is not in .gitignore"
    )

    import subprocess

    tracked = subprocess.run(["git", "ls-files", ".visitor_salt"],
                             cwd=REPO_ROOT, capture_output=True, text=True)
    assert tracked.stdout.strip() == "", "the salt is tracked by git"
