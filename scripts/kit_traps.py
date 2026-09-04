#!/usr/bin/env python3
"""Count the fleet-class traps in a `.claude/CLAUDE.md` traps section.

1.6.44 item 14 (emojimart 166e33a). A fork's traps section can sit fifteen
entries behind the template's — 7 against 22 on emojimart, whose HEAD trap
still carried the diagnosis 1.6.32 had corrected. The kit is contract-class,
so the sync never copied it, and nothing printed the gap.

This prints the PAIR. Run it with two paths and it reports
`fork N / template M` plus the titles the fork is missing, which is what the
fan-out needs per fork; run it with one and it reports that file's count.

Matching is by the first sentence of each entry, lower-cased and squeezed —
NOT by exact text, because a fork is expected to have merged a trap into its
own wording and adding a host-specific clause must not read as absence. That
is deliberately generous: the check exists to find a fork that never
received a trap, not to police prose.

    python3 scripts/kit_traps.py                       # this repo's count
    python3 scripts/kit_traps.py ../fork/.claude/CLAUDE.md
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HEADING = "### Verification traps"
REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_KIT = REPO_ROOT / ".claude" / "CLAUDE.md"


def traps_section(text: str) -> str:
    """The traps section, or "" when the file has none."""
    if HEADING not in text:
        return ""
    after = text.split(HEADING, 1)[1]
    # The section runs to the next `## ` heading, or to end of file.
    return re.split(r"^## ", after, maxsplit=1, flags=re.M)[0]


def trap_entries(text: str) -> list[str]:
    """One entry per top-level `- ` bullet, continuation lines folded in."""
    section = traps_section(text)
    entries, current = [], None
    for line in section.splitlines():
        if line.startswith("- "):
            if current is not None:
                entries.append(" ".join(current))
            current = [line[2:].strip()]
        elif current is not None and line.startswith("  "):
            current.append(line.strip())
        elif current is not None and not line.strip():
            continue
    if current is not None:
        entries.append(" ".join(current))
    return entries


def key(entry: str) -> str:
    """A readable identity for printing: the first sentence, normalised."""
    first = re.split(r"(?<=[.:])\s", entry, maxsplit=1)[0]
    first = re.sub(r"[`*_\"']", "", first)
    return re.sub(r"\s+", " ", first).strip().lower()[:60]


def _tokens(entry: str) -> set:
    """Content words of the first sentence, for overlap matching."""
    first = re.split(r"(?<=[.:])\s", entry, maxsplit=1)[0]
    words = re.findall(r"[a-z0-9_./>=-]+", first.lower())
    return {w for w in words if len(w) > 2}


# How much of a template trap's opening sentence a fork entry must share to
# count as the same trap. Deliberately loose: a fork is EXPECTED to merge a
# trap into its own wording and to add host-specific clauses, and a check
# that reported those as absence would train forks to paste over their own
# adaptations — the opposite of what item 14 asks for.
OVERLAP = 0.6


def _present(template_entry: str, fork_entries: list) -> bool:
    wanted = _tokens(template_entry)
    if not wanted:
        return True
    for candidate in fork_entries:
        shared = wanted & _tokens(candidate)
        if len(shared) / len(wanted) >= OVERLAP:
            return True
    return False


def compare(fork_text: str, template_text: str):
    """(fork count, template count, template entries the fork is missing)."""
    fork = trap_entries(fork_text)
    template = trap_entries(template_text)
    missing = [e for e in template if not _present(e, fork)]
    return len(fork), len(template), missing


def main(argv: list[str]) -> int:
    template_text = TEMPLATE_KIT.read_text()
    if len(argv) < 2:
        count = len(trap_entries(template_text))
        print(f"template {TEMPLATE_KIT}: {count} trap entries")
        return 0 if count else 1
    fork_path = Path(argv[1])
    fork_n, template_n, missing = compare(fork_path.read_text(), template_text)
    print(f"{fork_path}: fork {fork_n} / template {template_n}")
    for entry in missing:
        print(f"  MISSING: {key(entry)}…")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
