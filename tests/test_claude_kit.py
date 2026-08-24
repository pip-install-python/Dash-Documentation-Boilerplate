"""The shipped .claude/ development kit — the F1 fabric build (2026-08-24).

The kit is how every fork inherits the network's behavioral contract,
skills, and settings. These pins keep it shipped (the old blanket
`.claude/` ignore silently kept the project instructions local-only —
forks inherited NOTHING), keep it case-correct (macOS is
case-insensitive; the fleet's CI and Render are not), and keep each
fork's settings pointing at ITS OWN host rather than the template's.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parent.parent

KIT_FILES = (
    ".claude/CLAUDE.md",
    ".claude/settings.json",
    ".claude/skills/wire-verify/SKILL.md",
    ".claude/skills/sync-template/SKILL.md",
    ".claude/skills/report/SKILL.md",
    "DIVERGENCES.md",
)


def _ignored(path: str) -> bool:
    return (
        subprocess.run(
            ["git", "check-ignore", "-q", path], cwd=REPO
        ).returncode
        == 0
    )


def test_kit_files_exist_and_are_not_ignored():
    """The blanket `.claude/` ignore kept the contract local-only for the
    template's whole life — every fork inherited nothing. The allow-list
    must keep these shippable."""
    for rel in KIT_FILES:
        assert (REPO / rel).is_file(), f"kit file missing: {rel}"
        assert not _ignored(rel), (
            f"{rel} is gitignored — the kit cannot propagate to forks"
        )


def test_local_and_scratch_stay_local():
    """settings.local.json is the per-seat model override and must never
    ship; session working documents are local by convention network-wide
    (two public repos were caught tracking theirs)."""
    for rel in (
        ".claude/settings.local.json",
        ".claude/scratch-probe.png",
        "HANDOFF-probe.md",
        "KICKOFF-probe.md",
        "X402-SYNC-REPORT.md",
    ):
        assert _ignored(rel), f"{rel} would be committable — must stay local"


def test_claude_md_is_case_canonical_and_carries_the_contract():
    """macOS tolerates `claude.md`; the fleet's Linux CI does not. And the
    contract section is the point of shipping the file at all."""
    assert "CLAUDE.md" in os.listdir(REPO / ".claude"), (
        ".claude/CLAUDE.md must be exact-case for case-sensitive systems"
    )
    body = (REPO / ".claude" / "CLAUDE.md").read_text()
    for clause in (
        "behavioral contract",
        "Check the prompt against this tree",
        "Corrections are your job",
        "Verify your own deploy on the wire",
        "DIVERGENCES.md",
    ):
        assert clause in body, f"contract clause missing from CLAUDE.md: {clause!r}"


def test_skills_carry_frontmatter():
    for name in ("wire-verify", "sync-template", "report"):
        text = (REPO / ".claude" / "skills" / name / "SKILL.md").read_text()
        head = text.split("---", 2)
        assert len(head) >= 3, f"{name}: SKILL.md has no frontmatter block"
        front = head[1]
        assert re.search(r"^name:\s*\S", front, re.M), f"{name}: no name"
        assert re.search(r"^description:\s*\S", front, re.M), f"{name}: no description"


def test_settings_point_at_this_forks_own_host():
    """The anti-drift pin: settings ship with the TEMPLATE's host, and a
    fork that keeps them verbatim gets a sandbox that can wire-verify the
    template instead of itself. BASE_URL is the identity source — the
    settings must follow it."""
    from lib.constants import BASE_URL

    host = urlparse(BASE_URL).hostname
    settings = json.loads((REPO / ".claude" / "settings.json").read_text())

    domains = settings["sandbox"]["network"]["allowedDomains"]
    assert host in domains, (
        f"sandbox.network.allowedDomains lacks this repo's own host {host!r} "
        "— sessions here could not wire-verify their own production. "
        "Fork ritual: replace the template's host with yours."
    )
    assert "2plot.ai" in domains, "the hub must stay reachable (boards, presence)"

    allows = settings.get("permissions", {}).get("allow", [])
    assert f"WebFetch(domain:{host})" in allows, (
        f"permissions.allow lacks WebFetch(domain:{host})"
    )
