"""`scripts/agent_readiness.py` — 1.6.45 item 4.

The release report quotes a readiness number, so the number has to come from
somewhere a reader can re-run. These tests hold the SCORER, not the scanner:
the live call needs the network and is exercised by running the script, while
the parsing — which is where a wrong answer would come from — is pinned
against the payload shape measured on 2026-09-08.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys

import pytest

from conftest import REPO_ROOT

SCRIPT = REPO_ROOT / "scripts" / "agent_readiness.py"


@pytest.fixture(scope="module")
def scorer():
    spec = importlib.util.spec_from_file_location("agent_readiness", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# The real payload's shape, reduced. `checks` is a DICT of categories and
# each verdict is THREE-state — `neutral` is neither pass nor fail.
REPORT = {
    "level": 1,
    "levelName": "Basic Web Presence",
    "checks": {
        "discoverability": {
            "robotsTxt": {"status": "pass", "message": "robots.txt exists"},
            "dnsAid": {"status": "fail", "message": "DNS-AID records not found"},
        },
        "botAccessControl": {
            "contentSignals": {"status": "fail",
                               "message": "No Content Signals in robots.txt"},
            "webBotAuth": {"status": "neutral", "message": "not detected"},
        },
    },
    "nextLevel": {"target": 2, "name": "Bot-Aware",
                  "requirements": [{"check": "contentSignals"}]},
}


def test_it_reads_the_real_payload_shape(scorer):
    summary = scorer.summarise(REPORT)
    assert summary["level"] == 1
    assert summary["level_name"] == "Basic Web Presence"
    assert summary["passed"] == ["discoverability.robotsTxt"]
    assert [label for label, _ in summary["failing"]] == [
        "discoverability.dnsAid", "botAccessControl.contentSignals"]
    assert summary["next_level"] == 2
    assert summary["next_requirements"] == ["contentSignals"]


def test_neutral_is_neither_passed_nor_failed(scorer):
    """x402 on a non-commerce site is `neutral`; counting it either way
    misreports the host."""
    summary = scorer.summarise(REPORT)
    assert summary["neutral"] == ["botAccessControl.webBotAuth"]
    assert "botAccessControl.webBotAuth" not in summary["passed"]
    assert "botAccessControl.webBotAuth" not in [
        label for label, _ in summary["failing"]]


def test_an_unreadable_payload_raises_rather_than_scoring(scorer):
    """The defect this function was rewritten to remove.

    The first version was defensive: an unrecognised payload yielded empty
    levels and the script printed "failing: none" — which reads as a clean
    scan. It did that on a response it had NOT been able to read
    (IncompleteRead on a chunked body), turning "could not run" into "ran and
    found nothing wrong".
    """
    for payload in ({}, {"levels": []}, {"checks": None}, {"checks": {}}):
        with pytest.raises(ValueError):
            scorer.summarise(payload)


def test_the_floor_is_level_two(scorer):
    """CORRECTION to the drop, recorded rather than silently reinterpreted:
    it words the acceptance as "Level 1 5/5 and Level 2 >= 2/3", and the
    scanner reports no per-level tallies — one `level` integer plus
    per-category checks. Level >= 2 is the equivalent checkable statement."""
    assert scorer.meets_floor({"level": 2}) is True
    assert scorer.meets_floor({"level": 3}) is True
    assert scorer.meets_floor({"level": 1}) is False
    assert scorer.meets_floor({"level": None}) is False
    assert scorer.meets_floor({}) is False


def test_the_token_is_optional_and_never_printed():
    """MEASURED: the scan endpoint answers anonymously. The drop assumes a
    token is required; it is sent when present and the script runs without
    one. It must never reach stdout, a file, or a query string."""
    source = SCRIPT.read_text()
    assert "AGENT_READY_TOKEN" in source
    assert "Authorization" in source
    assert "?token=" not in source and "&token=" not in source
    # no print/format of the token itself
    assert "print(token" not in source and "{token}" not in source.replace(
        'f"Bearer {token}"', "")


def test_could_not_run_is_a_distinct_exit_state():
    """Three states, deliberately: 0 met the floor, 1 ran and did not, 2
    could not run. "Could not run" must never be reported as a score."""
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--url", "https://127.0.0.1:9/nope"],
        capture_output=True, text=True, cwd=REPO_ROOT, timeout=180,
    )
    assert result.returncode == 2, result.stdout + result.stderr
    assert "CANNOT RUN" in result.stderr
    assert "level" not in result.stdout.lower()


def test_the_probe_names_an_engine_and_carries_the_internal_token(scorer):
    from lib.constants import INTERNAL_UA_TOKEN

    assert INTERNAL_UA_TOKEN in scorer.UA
    assert scorer.UA.startswith("curl/")


def test_it_retries_a_truncated_read(scorer):
    """The first live call from this seat died with
    `IncompleteRead(6508 bytes read, 21923 more expected)` — a chunked
    response cut short. A partial read must never become a result."""
    assert scorer.ATTEMPTS >= 3
    source = SCRIPT.read_text()
    assert "certifi" in source, "an ad-hoc probe needs the certifi context"
