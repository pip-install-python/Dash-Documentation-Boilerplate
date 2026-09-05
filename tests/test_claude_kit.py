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


def _in_repo(rel: str) -> bool:
    return ".." not in rel and not rel.startswith("/")


def _machine_fence(kind: str, text: str, where: str) -> None:
    """The shared pin for machine fences (```yaml sync-verbatim in specs,
    ```yaml byte-owned in DIVERGENCES.md): exactly one block, `- path`
    lines with `#` comments, every path repo-relative and real at HEAD.
    Empty is valid — an empty block is a statement, a missing one is an
    omission. Gate lines (the fan-out's adoption gates) are validated
    like paths — a typo'd gate gates nothing:

      `# requires: <path>` (1.6.23) — the block applies only where
        <path> exists. For paths no pre-existing file can occupy;
        where one can, the gate must name a contract instead
        (sync/README.md — flows' pre-existing CLAUDE.md, 1.6.28).
      `# requires-contract: <path> :: <clause>` (1.6.28) — the block
        applies only where <path> exists AND contains <clause>. The
        clause must be real in THIS repo's copy at HEAD too.
      `- <path>  # requires: <other>` (1.6.28) — per-file gate: the
        fan-out skips this one copy where <other> is absent, instead
        of gating the whole block (clerkhook: a lockdown fork has no
        lib/auth_demos.py, legitimately, and must still receive the
        rest)."""
    fences = re.findall(
        r"^```yaml " + kind + r"[ \t]*\n(.*?)^```[ \t]*$", text, re.M | re.S
    )
    assert len(fences) == 1, (
        f"{where}: expected exactly one ```yaml {kind} fence, "
        f"found {len(fences)}"
    )
    for raw in fences[0].splitlines():
        stripped = raw.strip()
        if re.match(r"#\s*requires-contract:", stripped):
            gate = re.match(
                r"#\s*requires-contract:\s*(.+?)\s*::\s*(.+)$", stripped
            )
            assert gate, (
                f"{where} {kind}: {raw!r} — `# requires-contract:` takes "
                "`<path> :: <clause>`; a malformed gate gates nothing"
            )
            req, clause = gate.group(1).strip(), gate.group(2).strip()
            assert _in_repo(req), (
                f"{where} {kind}: `# requires-contract:` path {req!r} "
                "escapes the repo"
            )
            assert (REPO / req).is_file(), (
                f"{where} {kind}: `# requires-contract:` names {req!r} "
                "which does not exist at HEAD — a typo'd gate gates nothing"
            )
            assert clause in (REPO / req).read_text(), (
                f"{where} {kind}: `# requires-contract:` clause {clause!r} "
                f"is not in this repo's own {req} — a typo'd clause gates "
                "nothing"
            )
            continue
        required = re.match(r"#\s*requires:\s*(.+)$", stripped)
        if required:
            req = required.group(1).strip()
            assert _in_repo(req), (
                f"{where} {kind}: `# requires:` path {req!r} escapes the repo"
            )
            assert (REPO / req).is_file(), (
                f"{where} {kind}: `# requires:` names {req!r} which does "
                "not exist at HEAD — a typo'd gate gates nothing"
            )
            continue
        entry, _, comment = raw.partition("#")
        entry = entry.strip()
        if not entry:
            continue
        assert entry.startswith("- "), (
            f"{where} {kind}: {raw!r} is not a `- path` line"
        )
        path = entry[2:].strip()
        assert _in_repo(path), (
            f"{where} {kind}: {path!r} escapes the repo"
        )
        # `- <path>  # declined: <reason>` (1.6.36): the fork REFUSES this
        # cargo — it holds an equivalent elsewhere, or its posture inverts
        # the file. The path need not exist: it is the one entry that may
        # name something the fork never had (clerkhook's package suite at
        # tests/ root cannot take a site test dropped there). A reason is
        # mandatory; a bare `# declined` declines nothing.
        declined = re.match(r"\s*declined:\s*(\S.*)$", comment)
        if declined:
            assert kind == "byte-owned", (
                f"{where} {kind}: `# declined:` is a FORK fence entry "
                "(DIVERGENCES.md byte-owned); a spec cannot decline its own cargo"
            )
            continue
        assert not re.match(r"\s*declined\b", comment), (
            f"{where} {kind}: {raw!r} — `# declined:` needs a reason"
        )
        assert (REPO / path).is_file(), (
            f"{where} {kind}: {path!r} does not exist at HEAD "
            "— the machine would act on nothing or the wrong thing "
            "(a fork that never holds this cargo declines it: "
            "`# declined: <reason>`)"
        )
        # A per-file gate is the WHOLE trailing comment, `requires: <path>`
        # from its first character; prose comments that merely mention the
        # word stay prose.
        per_file = re.match(r"\s*requires:\s*(.+)$", comment)
        if per_file:
            gate_path = per_file.group(1).strip()
            assert _in_repo(gate_path), (
                f"{where} {kind}: per-file gate on {path!r} escapes the "
                f"repo: {gate_path!r}"
            )
            assert (REPO / gate_path).is_file(), (
                f"{where} {kind}: per-file gate on {path!r} names "
                f"{gate_path!r} which does not exist at HEAD — a typo'd "
                "gate gates nothing"
            )


_POSTURE_KEYS = {"ai_bots", "healthz", "runtime", "deploy", "unknown_ai"}
_POSTURE_ENUMS = {
    "healthz": {"minimal", "full"},
    "runtime": {"docker", "python"},
    "deploy": {"release-branch"},
    "unknown_ai": {"allow", "meter", "block"},
}


def _posture_fence(text: str, where: str) -> dict:
    """The ```yaml posture block in DIVERGENCES.md (1.6.30, F4).

    Declared postures used to live in the hub's own table — a copy of a
    measurement somebody took once, aging in a repo that cannot see the
    host. The fence homes each posture in the repo that serves it. SHAPE
    is all this validates: no test can tell a stale 200 from a fresh one,
    so the grammar is kept narrow enough that a wrong value is visibly
    wrong. Empty is valid and means "the template defaults".
    """
    fences = re.findall(
        r"^```yaml posture[ \t]*\n(.*?)^```[ \t]*$", text, re.M | re.S
    )
    assert len(fences) == 1, (
        f"{where}: expected exactly one ```yaml posture fence, "
        f"found {len(fences)}"
    )
    declared: dict = {}
    for raw in fences[0].splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        key, sep, value = stripped.partition(":")
        key, value = key.strip(), value.strip()
        assert sep, f"{where} posture: {raw!r} is not a `key: value` line"
        assert key in _POSTURE_KEYS, (
            f"{where} posture: unknown key {key!r} — the hub reads "
            f"{sorted(_POSTURE_KEYS)} and would ignore this one silently"
        )
        assert key not in declared, f"{where} posture: {key!r} declared twice"
        if key in _POSTURE_ENUMS:
            assert value in _POSTURE_ENUMS[key], (
                f"{where} posture: {key}: {value!r} — expected one of "
                f"{sorted(_POSTURE_ENUMS[key])}"
            )
            declared[key] = value
            continue
        try:
            statuses = json.loads(value)
        except ValueError as exc:
            raise AssertionError(
                f"{where} posture: ai_bots must be a JSON object like "
                f'{{"/": 403, "/llms.txt": 200}} — {exc}'
            ) from None
        assert isinstance(statuses, dict) and statuses, (
            f"{where} posture: ai_bots is {statuses!r} — a non-empty JSON "
            "object of path -> status, or omit the key entirely"
        )
        for path, status in statuses.items():
            assert path.startswith("/"), (
                f"{where} posture: ai_bots key {path!r} is not a path"
            )
            assert isinstance(status, int) and 100 <= status <= 599, (
                f"{where} posture: ai_bots[{path!r}] is {status!r} — an "
                "HTTP status, measured with a real vendor UA"
            )
        declared[key] = statuses
    return declared


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


def test_sync_specs_are_specifiable():
    """F2: every sync spec item must carry class/detect/acceptance — an
    item without detect and acceptance is not specifiable (write a
    kickoff instead and fix the item until it is; sync/README.md).

    Skips where no sync/ exists: forks CONSUME specs, only the template
    authors them — emojimart's F2 correction: this file is a byte-
    verbatim kit port, and without the guard it failed on arrival at
    every fork. The pin wakes up the day a fork starts authoring specs.

    F3b: every spec also carries exactly one ```yaml sync-verbatim
    fence — the machine block the fan-out workflow byte-copies from.
    Every listed path must exist at HEAD and stay inside the repo; a
    wrong entry becomes twelve wrong PRs.
    """
    import pytest

    sync_dir = REPO / "sync"
    if not sync_dir.is_dir():
        pytest.skip("no sync/ — this repo consumes specs, it does not author them")
    assert (sync_dir / "README.md").is_file(), "sync/README.md (the format) missing"
    specs = sorted(sync_dir.glob("SYNC-*.md"))
    assert specs, "no sync specs — releases ship one (F2)"
    for spec in specs:
        text = spec.read_text()
        blocks = re.split(r"^### ", text, flags=re.M)[1:]
        assert blocks, f"{spec.name}: no items"
        for block in blocks:
            title = block.splitlines()[0]
            for field in ("class:", "detect:", "acceptance:"):
                assert field in block, (
                    f"{spec.name} item {title!r} lacks {field}"
                )

        _machine_fence("sync-verbatim", text, spec.name)


def test_divergences_carry_the_byte_owned_block():
    """F3b A1's finding: the fan-out honours DIVERGENCES.md by never
    overwriting a byte-owned path, and a prose MENTION over-flags —
    muicharts' host-pin nuance names tests/test_claude_kit.py while its
    bytes are template-owned, a false positive recurring every release.
    The fence is the machine answer; when present it is authoritative,
    and empty means "the template owns every sync-verbatim path here".

    ABSENCE SKIPS, never fails (1.6.22, the ops seat's own correction):
    the machine tolerates a missing fence (the mention heuristic —
    over-flags, never restores), so the pin must too. Failing here
    would let one unported contract item keep every later mechanical
    PR red, revoking the fan-out's "verbatim class = green merge"
    promise indefinitely. CI guards what a fork HAS declared; the
    spec's contract item and its session round drive adoption.
    """
    import pytest

    div = REPO / "DIVERGENCES.md"
    if not div.is_file():
        pytest.skip("no DIVERGENCES.md — nothing for the fan-out to honour")
    text = div.read_text()
    if not re.search(r"^```yaml byte-owned[ \t]*$", text, re.M):
        pytest.skip(
            "DIVERGENCES.md has no byte-owned fence — port "
            "SYNC-1.6.17-1.6.21 item 1; until then the fan-out uses the "
            "mention heuristic"
        )
    _machine_fence("byte-owned", text, "DIVERGENCES.md")


def test_a_declined_entry_may_name_a_path_the_fork_never_had():
    """1.6.36: clerkhook's package suite lives at tests/ root, so a site
    test fanned out there would ERROR its matrix; the fork must be able to
    decline cargo it does not hold. Only a `# declined: <reason>` entry
    may be missing at HEAD; a plain missing path still fails, and a bare
    `# declined` with no reason is not a decline."""
    import pytest

    fence = "```yaml byte-owned\n- tests/no_such_cargo.py  # declined: package suite at tests/\n```\n"
    assert not (REPO / "tests/no_such_cargo.py").exists()
    _machine_fence("byte-owned", fence, "synthetic")           # validates

    with pytest.raises(AssertionError, match="does not exist at HEAD"):
        _machine_fence("byte-owned", "```yaml byte-owned\n- tests/no_such_cargo.py\n```\n", "synthetic")
    with pytest.raises(AssertionError, match="needs a reason"):
        _machine_fence("byte-owned", "```yaml byte-owned\n- tests/no_such_cargo.py  # declined\n```\n", "synthetic")
    with pytest.raises(AssertionError, match="cannot decline"):
        _machine_fence("sync-verbatim", "```yaml sync-verbatim\n- tests/no_such_cargo.py  # declined: x\n```\n", "synthetic")


def test_divergences_posture_fence_is_wellformed():
    """The declared posture (1.6.30, F4): shape only, plus the one value
    the repo can contradict by itself.

    ABSENCE SKIPS, like the byte-owned fence and for the same reason — a
    fork that has not ported the item yet keeps its CI green and gets the
    contract item, not a red on arrival. What is declared is held: an
    unknown key would be read by nobody, and a `runtime:` disagreeing with
    render.yaml is the posture lying about something in its own tree.
    """
    import pytest

    div = REPO / "DIVERGENCES.md"
    if not div.is_file():
        pytest.skip("no DIVERGENCES.md — nothing to declare a posture in")
    text = div.read_text()
    if not re.search(r"^```yaml posture[ \t]*$", text, re.M):
        pytest.skip(
            "DIVERGENCES.md has no posture fence — port the 1.6.30 item; "
            "until then the hub reads its own seeded table"
        )
    declared = _posture_fence(text, "DIVERGENCES.md")

    render = REPO / "render.yaml"
    if "runtime" in declared and render.is_file():
        for line in render.read_text().splitlines():
            m = re.match(r"\s*runtime:\s*(\S+)", line)
            if m:
                assert declared["runtime"] == m.group(1), (
                    f"posture declares runtime {declared['runtime']!r}, "
                    f"render.yaml says {m.group(1)!r} — the posture is "
                    "wrong about this repo's own tree"
                )
                break


# ------------------------------- recorded conventions (1.6.44 item 9) --


def test_divergences_has_the_recorded_conventions_subsection():
    """Item 9's detect.

    A DIVERGENCE says "this repo differs, on purpose". A RECORDED CONVENTION
    says "this repo matches, and the match is a decision" — usually something
    deliberately removed. Nothing in a diff tells the second from an
    accident, so without the entry a sync restores it and nobody notices.
    """
    text = (REPO / "DIVERGENCES.md").read_text()
    assert "## Recorded conventions (not divergences)" in text


def test_the_header_explains_both_kinds_of_entry():
    """Contract-class: the FILE's own text is what sync authors and the
    fan-out read. A rule that lives only in a test docstring is invisible to
    both of them."""
    text = (REPO / "DIVERGENCES.md").read_text()
    intro = text.split("## This repo's divergences", 1)[0]
    assert "RECORDED CONVENTION" in intro
    assert "DIVERGENCE" in intro


def test_the_guard_entries_are_under_it_and_name_their_code():
    """Acceptance: the template's own guard entries moved under the heading,
    and each one names the thing a sync would restore."""
    text = (REPO / "DIVERGENCES.md").read_text()
    section = text.split("## Recorded conventions (not divergences)", 1)[1]
    section = section.split("\n## ", 1)[0]

    for needle in ("HeadAsGetMiddleware", "User-Agent list", "html.Img"):
        assert needle in section, f"guard entry for {needle} is not recorded"

    entries = [ln for ln in section.splitlines() if ln.startswith("- **")]
    assert len(entries) >= 4, f"only {len(entries)} guard entries"


def test_every_guard_entry_points_at_something_that_still_exists():
    """A guard entry naming code nobody has any more costs the reader's
    afternoon — the same rule the kit applies to traps."""
    middleware = REPO / "lib" / "asgi_middleware.py"
    assert middleware.exists(), (
        "the module the entry names is gone — the guard points at nothing"
    )
    # PARSED, not grepped, and not merely comment-stripped either: the
    # module names the retired class four times while explaining why it is
    # gone — three times in comments and once in a live DOCSTRING, which a
    # comment stripper keeps. Strings are the other half of item 13's rule,
    # and this is the case that proves it: a detect that reads the
    # documentation of an absence reports the absence as a presence.
    import ast

    tree = ast.parse(middleware.read_text())
    defined = {node.name for node in ast.walk(tree)
               if isinstance(node, (ast.ClassDef, ast.FunctionDef))}
    referenced = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    referenced |= {node.attr for node in ast.walk(tree)
                   if isinstance(node, ast.Attribute)}
    assert "HeadAsGetMiddleware" not in defined, "the shim came back"
    assert "HeadAsGetMiddleware" not in referenced, (
        "the shim is referenced in live code — retired means retired"
    )
    assert defined, "parsed no definitions at all — the AST read swept nothing"

    from dash import html

    assert "loading" not in html.Img()._prop_names


def test_the_acceptance_output_rule_is_in_the_kit():
    """Item 10's detect. An acceptance is a claim about a tree AT A VERSION,
    and the version has to be in the sentence carrying the number."""
    kit = (REPO / ".claude" / "CLAUDE.md").read_text()
    assert "PRINT THE RESOLVED VERSION BESIDE THE RESULT" in kit
    rule = kit.split("PRINT THE RESOLVED VERSION BESIDE THE RESULT", 1)[1]
    rule = rule.split("\n- ", 1)[0]
    assert "__file__" in rule, (
        "the rule must say HOW to resolve it — import and print the path, "
        "not read requirements.txt"
    )
    assert "actionlint" in rule and "shellcheck" in rule, (
        "the local-vs-CI half of the rule is missing"
    )


def test_the_kit_says_where_the_resolved_version_comes_from():
    """The three wrong ways are all in this file as traps; the rule has to
    point at the right one or it is a slogan."""
    kit = (REPO / ".claude" / "CLAUDE.md").read_text()
    assert "IMPORT THE THING" in kit, (
        "the cwd-shadowing trap is the mechanism this rule depends on"
    )


# ------------------------------- the spec-format rule (1.6.44 item 13) --


def test_the_spec_format_rule_names_strings_not_only_comments():
    """Item 13. Stripping comments is the half-measure that looks like the
    fix; a docstring is a string, and it is where the class actually bites.
    """
    readme = (REPO / "sync" / "README.md").read_text()
    rule = readme.split("## Authoring rules", 1)[1].split("\n- **Floors", 1)[0]
    assert "strip\n  comments and strings" in rule or "comments and strings" in rule
    assert "DOCSTRING" in rule.upper(), (
        "the rule must say that a docstring is a string — the comment-strip "
        "half-measure passes every test that does not"
    )
    assert "ast.parse" in rule, "the rule must name the technique that works"


def test_the_sync_1_6_43_item_3_detects_pass_on_this_tree():
    """Item 13's acceptance, run rather than asserted.

    These are the two detects that were casing-bound to the spec's own
    emphasis caps and returned 0 on the tree that authored them. Read
    case-insensitively, as the fix-forward specifies, they find the traps.
    """
    kit = (REPO / ".claude" / "CLAUDE.md").read_text().lower()
    for fragment in ("measured on a green push",
                     "corpus is non-empty",
                     "when a lane disagrees",
                     "verify the artifact the claim is about"):
        assert kit.count(fragment) >= 1, (
            f"detect fragment {fragment!r} is absent from the kit"
        )


def test_a_case_bound_detect_would_still_fail_here():
    """The mechanism behind the fix-forward, kept as evidence.

    The traps ship in sentence case; the spec styles its fragments in caps.
    A case-SENSITIVE grep for the capitalised form finds nothing — which is
    exactly what happened, in the item about checks that cannot fail.
    """
    kit = (REPO / ".claude" / "CLAUDE.md").read_text()
    assert "ASSERT THE CORPUS IS NON-EMPTY" not in kit
    assert "assert the corpus is non-empty" in kit.lower()


# --------------------------- traps-section currency (1.6.44 item 14) --


def test_the_traps_counter_reads_this_repos_section():
    """Item 14's detect needs a counter that works before it can print a
    pair. Non-vacuity first: it must find this repo's own traps."""
    import sys

    sys.path.insert(0, str(REPO / "scripts"))
    from kit_traps import trap_entries

    entries = trap_entries((REPO / ".claude" / "CLAUDE.md").read_text())
    assert len(entries) >= 20, (
        f"the template's traps section reads as {len(entries)} entries — the "
        "counter is looking at the wrong thing, or traps were lost"
    )
    assert all(e.strip() for e in entries)


def test_the_counter_reports_a_fork_that_is_behind():
    """The pair the fan-out prints. A counter that cannot report a gap is
    the check-that-cannot-fail again — so the gap is constructed here.
    """
    import sys

    sys.path.insert(0, str(REPO / "scripts"))
    from kit_traps import compare

    template_text = (REPO / ".claude" / "CLAUDE.md").read_text()
    head, tail = template_text.split("### Verification traps", 1)
    truncated = head + "### Verification traps" + "\n".join(
        tail.splitlines()[:80])

    fork_n, template_n, missing = compare(truncated, template_text)
    assert template_n >= 20
    assert fork_n < template_n, "the truncated fork did not read as behind"
    assert missing, "no missing entries reported for a fork that is behind"


def test_a_fork_that_reworded_a_trap_is_not_reported_as_missing_it():
    """Merged, never installed over. A fork adapting a trap to its own host
    must not read as absence, or the check trains people to paste."""
    import sys

    sys.path.insert(0, str(REPO / "scripts"))
    from kit_traps import compare

    template_text = (REPO / ".claude" / "CLAUDE.md").read_text()
    reworded = template_text.replace(
        "- Always GET, never HEAD — and the mechanism",
        "- Always GET, never HEAD — and the mechanism (on this host too)",
        1,
    )
    _fork_n, _template_n, missing = compare(reworded, template_text)
    assert not any("always get, never head" in m.lower() for m in missing), (
        "a trap with an added clause read as missing — the check would push "
        "forks to overwrite their own adaptations"
    )


def test_a_fork_with_no_traps_section_reads_as_zero_not_as_equal():
    import sys

    sys.path.insert(0, str(REPO / "scripts"))
    from kit_traps import compare

    template_text = (REPO / ".claude" / "CLAUDE.md").read_text()
    fork_n, template_n, missing = compare("# a kit with no traps\n", template_text)
    assert fork_n == 0 and template_n >= 20
    assert len(missing) == template_n


# ------------------------------- the timing sampler (1.6.44 item 17) --


def test_the_sampler_trap_carries_its_three_phrases():
    """Item 17's detect. Each phrase is a correction some host paid for.

    Whitespace is normalised before matching, and that is not tidiness: the
    first version of this test failed because "eight samples at 45 s" wraps
    across a line break in the kit. A detect keyed on where a line happens
    to break is a detect on formatting — item 13's rule, one more time, in
    the same file that records it.
    """
    kit = " ".join((REPO / ".claude" / "CLAUDE.md").read_text().lower().split())
    for phrase in ("eight samples at 45", "completed_at", "unreadable"):
        assert phrase in kit, f"the trap does not carry {phrase!r}"
    assert "promote step" in kit


def test_the_trap_points_at_the_script_rather_than_describing_it():
    kit = (REPO / ".claude" / "CLAUDE.md").read_text()
    assert "scripts/promote_sampler.py" in kit
    assert (REPO / "scripts" / "promote_sampler.py").exists()


def test_the_sampler_records_unreadable_as_its_own_state():
    import sys

    sys.path.insert(0, str(REPO / "scripts"))
    from promote_sampler import NEW, OLD, UNREADABLE, classify

    assert classify(None, "abc123") == UNREADABLE
    assert UNREADABLE != OLD, (
        "collapsing unreadable into old invents a bracket nobody observed"
    )
    assert classify("abc123def456", "abc123def456") == NEW
    assert classify("999999999999", "abc123def456") == OLD


def test_the_sampler_refuses_a_bracket_it_did_not_observe(capsys):
    """A single NEW sample proves nothing: it cannot say what it followed.

    This is the difference between evidence and a number, and it is the one
    thing a sampler must not get wrong.
    """
    import sys

    sys.path.insert(0, str(REPO / "scripts"))
    import promote_sampler

    original = promote_sampler.read_build
    try:
        promote_sampler.read_build = lambda url: "abc123def456"   # NEW always
        code = promote_sampler.main(
            ["prog", "--sha", "abc123def456", "--samples", "2", "--interval", "0"]
        )
    finally:
        promote_sampler.read_build = original

    assert code == 1, "a run with no OLD sample reported a bracket"
    assert "cannot say what the swap followed" in capsys.readouterr().out


def test_the_sampler_reports_a_real_bracket(capsys):
    import sys

    sys.path.insert(0, str(REPO / "scripts"))
    import promote_sampler

    sequence = iter(["oldbuild0000", None, "abc123def456"])
    original = promote_sampler.read_build
    try:
        promote_sampler.read_build = lambda url: next(sequence)
        code = promote_sampler.main(
            ["prog", "--sha", "abc123def456", "--samples", "3", "--interval", "0"]
        )
    finally:
        promote_sampler.read_build = original

    out = capsys.readouterr().out
    assert code == 0
    assert "last OLD" in out and "first NEW" in out
    assert "inside the bracket" in out, (
        "the unreadable sample between old and new was not surfaced — that "
        "sample is the restart, and it landed inside the bracket twice out "
        "of two on this host"
    )


def test_the_sampler_probe_carries_the_internal_token():
    import sys

    sys.path.insert(0, str(REPO / "scripts"))
    from promote_sampler import PROBE_UA

    from lib.constants import INTERNAL_UA_TOKEN

    assert INTERNAL_UA_TOKEN in PROBE_UA
    assert PROBE_UA.startswith("curl/"), "an engineless probe is crawler-lane"


def test_the_sampler_verifies_certificates():
    """Every ad-hoc probe against production needs this, and shipping the
    fix inside the live tools did not stop the next hand-written script
    from hitting CERTIFICATE_VERIFY_FAILED an hour later."""
    src = (REPO / "scripts" / "promote_sampler.py").read_text()
    assert "certifi" in src and "create_default_context" in src
    assert "ATTEMPTS = 3" in src


def test_the_verify_contract_line_and_its_traps_are_in_the_kit():
    """Item 18's detect: the contract line and the trap phrases."""
    kit = " ".join((REPO / ".claude" / "CLAUDE.md").read_text().lower().split())
    assert "metering evidence, never sole authorisation" in kit
    assert "gated by a secret that host holds" in kit
    for phrase in (
        "a test that exercises a dependency's absence is not a test of that "
        "dependency's policy",
        "a fixture cannot falsify the assumption it was built from",
        "a defaulted argument hides its own default",
        "a test at the wrong level",
    ):
        assert phrase in kit, f"the kit does not carry: {phrase!r}"


def test_the_proxied_robots_trap_is_in_the_kit():
    """Item 19's detect."""
    kit = " ".join((REPO / ".claude" / "CLAUDE.md").read_text().lower().split())
    assert "a proxied robots.txt is not your robots.txt" in kit
    assert "when they differ, the difference is the finding" in kit
    assert "ai_bot_posture" in kit
