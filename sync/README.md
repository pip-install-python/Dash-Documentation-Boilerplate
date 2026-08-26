# Sync specs — propagation as artifact, not conversation

Every template release ships a spec here (`SYNC-<version>.md`, or
`SYNC-<from>-<to>.md` for a range). The spec IS the kickoff: a fork
session syncs by reading it with `/sync-template` — no hand-written
per-fork prompt. This is the F2 fabric build (2026-08-24); the format
below encodes what three rounds of hand-carried syncs and the F1
pilots proved necessary.

## How a fork consumes a spec

1. Read the fork's `DIVERGENCES.md` FIRST. Nothing in a spec
   overrides a recorded divergence — where they collide, port the
   item's CONTRACT into the fork's shape and say so.
2. For each item, run its **detect** check. Already-satisfied items
   are reported as such (`already-present`), not re-applied — forks
   at different levels consume the same spec.
3. Apply by class (below), run each item's **acceptance**, then the
   fork's full suite, push, CD green, `/wire-verify`, and report
   per-item dispositions: `applied` / `ported-as-contract` /
   `already-present` / `not-applicable-because` / `open`
   (+ evidence). `open` (1.6.28): the detect fires but the item is
   deliberately out of this session's scope — name it and who acts;
   do not invent a sixth word, the orchestrator reads these five.

Specs are NOT vendored into consumers (1.6.28, decided over scoping
the pins to the authoring repo). A fork copies the kit and the
block's cargo, never `sync/` itself: the kit test validates every
`sync/SYNC-*.md` at HEAD — each `- path` must exist — so a vendored
spec wakes those pins against a tree that legitimately lacks the
template's newest files and goes red on arrival (emojimart, whose
copy listed tests/test_auth_demos.py before receiving it).
Traceability lives in the fork's DIVERGENCES.md or changelog
("consumed SYNC-x at template <sha>"), not in a copy. Why not the
other option: an authoring-repo predicate inside the byte-verbatim
kit test would itself be a fork-divergent seam, and a silently
vacuous pin on vendored specs would hide exactly the staleness that
vendoring creates.

Batch-1 precedent (2026-08-25): a fork may already carry a
blanket-ignored `.claude/` with its OWN content (excalidraw: a
component-repo kit with agents/ and flat skills; email: a guide,
agents, and a `.pypirc` credential). A kit item is then a MERGE into
that content, never an install-over — and the ignore must take the
template's ALLOW-LIST form, because the allow-list is what keeps
credentials under `.claude/` structurally uncommittable. The adoption
gate reading such a fork as `not-adopted` is correct, not a bug: the
gate's markers absent means the kit CONTRACT is absent, whatever else
the directory holds.

## Item classes

- **verbatim** — byte-copy targets. If the fork's copy differs
  beyond a recorded divergence, the template wins.
- **contract** — the fork ports the BEHAVIOR, not the file. The item
  states the contract and its test pins; a fork satisfies it in its
  own shape, documented additions allowed (the F1 evidence standard:
  flexlayout's healthz differs from the template's by exactly one
  functional line — its `version` field — and that is a recorded
  divergence, not drift). Evidence for `already-present` on a
  contract item is a DIFF or the passing pins, not an assertion.
- **conditional** — applies only if the item's **predicate** matches
  the fork. `not-applicable` requires the predicate's evidence
  (flexlayout's Part B model: "does a FastAPI lane exist here?" was
  the first command, not an assumption).

## The `sync-verbatim` block

Every spec carries exactly ONE fenced machine block listing the
whole files the F3b fan-out workflow may byte-copy into a fork.
Prose stays the contract; the block is what the machine consumes:

    ```yaml sync-verbatim
    # requires-contract: .claude/CLAUDE.md :: Check the prompt against this tree
    - .claude/skills/wire-verify/SKILL.md
    - tests/test_claude_kit.py
    - tests/test_auth_demos.py  # requires: lib/auth_demos.py
    ```

Rules:

- **Only whole-file byte-copy targets go in.** A verbatim item whose
  target is a fragment (a function, a pin inside a shared test file)
  stays session-class: listed in prose with `class: verbatim` as
  always, never in the block — "the template wins on these bytes" is
  something a session can apply to a fragment and a workflow cannot.
  The criterion is the target, not the item's class: a contract
  item's byte-verbatim sub-targets qualify (item 6's skills + kit
  test are the precedent) while its adapted halves stay out.
- Paths are repo-relative, no `..`, one per line, `#` comments
  allowed.
- **Adoption gates** — zero or more gate lines inside the fence.
  A fork failing a block-level gate receives NOTHING from the block
  and is flagged for a session — its next step is the contract item
  the cargo assumes, not the cargo (the machine must not do a
  session's job badly: six fleet forks predate the kit, and ungated
  cargo would have dropped a failing kit test into each). Three
  forms, all validated against template HEAD by the kit test — a
  typo'd gate gates nothing:
  - `# requires: <repo-relative path>` (1.6.23) — the file must
    already exist in the consuming fork. ONLY for paths no
    pre-existing file can occupy.
  - `# requires-contract: <path> :: <clause>` (1.6.28) — the file
    must exist AND contain the clause. **A gate names a contract,
    never a path, whenever a pre-existing file can occupy the
    path**: flows carried a tracked `.claude/CLAUDE.md` since March
    2026 — the component library's own guide, none of the kit — and
    a path gate read it as kit-adopted (the third fork where "no
    .claude/" was wrong). Any block carrying kit files or the kit
    test gates on the kit CONTRACT — one of the five clauses the
    kit test greps in `.claude/CLAUDE.md` — never on kit paths.
  - `- <path>  # requires: <other-path>` (1.6.28) — per-file gate:
    the fan-out skips this ONE copy where the named file is absent
    in the fork, instead of gating the whole block (clerkhook: a
    lockdown fork legitimately has no lib/auth_demos.py and must
    still receive the rest). The gate is the whole trailing
    comment, `requires:` from its first character; prose comments
    stay prose.
- A spec with no whole-file verbatims ships an EMPTY block —
  present, so the absence is a statement, not an omission.
- A fork's recorded divergence on a listed path wins: the workflow
  skips it and flags the fork for a session. The author does not
  need to know the fleet's divergences.
- The block never carries `.claude/settings.json` unless the spec's
  prose says the release intends a fleet-wide settings change. It
  CAN fan out mechanically (a workflow commit is not bound by the
  session-side write guard — the F2 settings-write friction closes
  here), so it must be deliberate, never incidental.

## Authoring rules (earned, not invented)

- **Floors are stated by `LLMS_PKG_FLOOR` semantics, never by
  grepping the number.** The rationale ladder retains old rungs BY
  DESIGN — a spec (or a session) that greps finds history and calls
  it the present. When a floor moves, every encoding moves
  (requirements, the boot tuple + message, tests, CI) and the ladder
  EXTENDS.
- **`.claude/CLAUDE.md`: the contract and traps sections port
  verbatim; everything above them adapts** wherever a fork's
  CLAUDE.md is its own guide (all three F1 pilots corrected the
  original "port verbatim" instruction — adopted).
- **DIVERGENCES retirements are marked, not deleted**, when older
  reports still describe the divergence as live. A record that
  overclaims teaches the next sync to defend a line nobody is
  attacking.
- Every item carries **detect** (how to tell it's already there) and
  **acceptance** (the pin or wire check that proves it landed). An
  item without both is not specifiable — write a kickoff instead and
  fix the item until it is.

## Item template

    ### <n>. <title> (template <version> <sha>)
    class: verbatim | contract | conditional
    files: <paths>
    detect: <command or check>
    predicate: <conditional only>
    contract: <contract only — the behavior + its pins>
    acceptance: <test / wire check>
    notes: <traps, fork precedents>
