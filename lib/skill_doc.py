"""Generate this host's ``SKILL.md`` from its own corpus (1.6.45 item 2).

The package looks for `SKILL.md` in the app's assets folder, digests the
BYTES ON DISK, and lists it at `/.well-known/agent-skills/index.json`. It
does not generate the file — the content is the host's, and on this network
the host generates it from the corpus rather than a human writing it, for
the reason every generated surface here exists: a hand-written skill goes
stale silently, and the first reader to notice is an agent acting on it.

Frontmatter is two scalar fields by the agent-skills spec, and the package
parses them with a deliberately small reader (no YAML dependency), so this
writes exactly what that reader can read: `name:` and `description:` on
their own lines, no block scalars, no nesting.

The NAME rule (the item's contract half): the host's package's PyPI name,
lower-case with hyphens. A host that documents a component names that
component, because that is the string an agent would `pip install`. A host
with no package — this template, pipdocs — names its own distribution
instead and serves one skill for the network's use, which is why the index
is empty on neither.
"""
from __future__ import annotations

import re
from pathlib import Path

from lib.constants import (
    API_PACKAGES,
    BASE_URL,
    GITHUB_URL,
    SITE_DESCRIPTION,
    SITE_SHORT_NAME,
)

SKILL_FILENAME = "SKILL.md"

# The spec's ceiling. Truncated rather than dropped: a description that is
# too long is still the best answer available, and an absent one makes the
# index entry less useful than a shortened one.
MAX_DESCRIPTION = 1024

_REPO_ROOT = Path(__file__).resolve().parent.parent


def skill_name() -> str:
    """The PyPI-style name an agent would install, lower-case and hyphenated."""
    if API_PACKAGES:
        return str(API_PACKAGES[0]).strip().lower().replace("_", "-")
    # No package: this host IS the artifact. The repository name is the
    # distribution name for a template that is forked rather than installed.
    tail = GITHUB_URL.rstrip("/").rsplit("/", 1)[-1]
    return tail.strip().lower().replace("_", "-")


def skill_description() -> str:
    """The site's own description, flattened to one line and capped."""
    text = " ".join(SITE_DESCRIPTION.split())
    if len(text) > MAX_DESCRIPTION:
        text = text[: MAX_DESCRIPTION - 1].rstrip() + "…"
    return text


def _quickstart() -> str:
    """The `## Quick Start` section of the home page, verbatim.

    From the corpus, not a copy: home.md is what a human reader is shown, so
    an agent and a reader get the same instructions or the generator is
    pointless. Absent section -> empty string, and the body still carries the
    pointers, because a skill with no quickstart is thinner but not wrong.
    """
    home = _REPO_ROOT / "pages" / "home.md"
    try:
        text = home.read_text()
    except OSError:
        return ""
    match = re.search(r"^## Quick Start\s*$(.*?)(?=^## |\Z)", text,
                      re.M | re.S)
    return match.group(1).strip() if match else ""


def build_skill_md() -> str:
    """The whole document, frontmatter included."""
    lines = [
        "---",
        f"name: {skill_name()}",
        f"description: {skill_description()}",
        "---",
        "",
        f"# {SITE_SHORT_NAME}",
        "",
        "This file is GENERATED from this site's own corpus at boot "
        "(`lib/skill_doc.py`). Edit the corpus, not this file.",
        "",
    ]

    quickstart = _quickstart()
    if quickstart:
        lines += ["## Quick Start", "", quickstart, ""]

    lines += [
        "## Where to read more",
        "",
        f"- Full documentation for agents: {BASE_URL}/llms.txt",
        f"- Human-readable site: {BASE_URL}/",
        f"- Source: {GITHUB_URL}",
    ]
    if API_PACKAGES:
        # The component's generated props reference — only where a package
        # is declared, since the page does not exist otherwise (and item
        # 11's link check would call a pointer to it a soft 404).
        lines.append(f"- Component API reference: {BASE_URL}/api")
    lines.append("")
    return "\n".join(lines)


def write_skill_md(assets_folder) -> Path:
    """Write `SKILL.md` where the package looks for it; return the path.

    Rewritten on every boot rather than written once: the digest the index
    serves is computed from these bytes, so a stale file would advertise a
    digest for content the corpus no longer contains.
    """
    path = Path(assets_folder) / SKILL_FILENAME
    path.write_text(build_skill_md(), encoding="utf-8")
    return path
