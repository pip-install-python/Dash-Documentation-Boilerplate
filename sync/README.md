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
  item's byte-verbatim sub-targets qualify (the kit skills + kit
  test are the precedent) while its adapted halves stay out.
- **A whole file is verbatim-safe only if no fork-owned test
  exercises its interface** (1.6.29) — if `tests/` in a fork calls
  into it with a signature the fork wrote, the file is contract-class
  no matter how invariant its bytes are. Ask the question for every
  cargo candidate: who stubs this? **And its mirror: what does this
  call into?** (1.6.30) — cargo that CALLS a fork-owned seam is the
  same hazard from the other side. tests/test_auth_demos.py is the
  standing example: nothing stubs it, but it reads DEMOS's shape
  (`spec["module"]`, so dict values) and conftest's `app_module`
  fixture. Both are fleet-uniform today, which is why it stays in the
  block — uniform is a fact you check per round, not a property. The
  case: scripts/smoke_live.py
  rode the block for exactly one round (1.6.28) — byte-invariant by
  construction, host from argv, knobs from env — but every fork's own
  tests/test_smoke_live.py (BASE, canonical host, og:image are all
  per-fork, so the test can never be cargo) monkeypatches its
  `fetch`, and the live fan-out (run 33000661276) landed the file red
  on 7 of 12 forks: wake()'s new kwargs meeting stubs written for the
  pre-1.6.2x signature. Green on the other four proved
  stub-compatibility, not safety.
- **When a file LEAVES the block, the release notes name the forks it
  already landed on and what they must do** (1.6.30). Removal stops
  the NEXT fan-out and undoes nothing: every fork that took the copy
  still has it, in whatever state the round left it — green, red, or
  green-because-nothing-exercised-it. A removal that says only "no
  longer cargo" hands twelve sessions the job of working out whether
  they are one of the twelve. Name them, and name the remedy per
  state; where the round's own evidence cannot say (a fork with no
  test either way), say that too and make the detect the first step.
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
- **Dead cargo (1.6.36).** When a fork's DIVERGENCES records an
  INVERSION of a cargo file's posture — the fork's equivalent asserts
  the opposite of what the template's copy asserts — the fork
  declines the file (`# declined:` in its byte-owned fence, below)
  and the release notes name every fork already holding the dead
  copy, with the remedy (delete it + the declined entry). Instance:
  `scripts/smoke_live.py` on clerkhook — 611 lines, referenced by
  nothing, asserting content IS served on a host whose posture is
  that every surface denies (its DIVERGENCES §6 names
  `scripts/lockdown_smoke.py` as the inversion). A copy that
  contradicts the host it sits on is not "unused", it is a wrong
  statement waiting for a session to believe it.
- The block never carries `.claude/settings.json` unless the spec's
  prose says the release intends a fleet-wide settings change. It
  CAN fan out mechanically (a workflow commit is not bound by the
  session-side write guard — the F2 settings-write friction closes
  here), so it must be deliberate, never incidental.

## The fork's own fences (`DIVERGENCES.md`)

A spec's block says what the template SENDS. Two fences in the fork's
own `DIVERGENCES.md` say what the fork KEEPS and what it IS — both
validated for shape by `tests/test_claude_kit.py`, both SKIPPING on
absence so a fork that has not ported them keeps its CI green and
receives the contract item instead of a red. This section existed
nowhere until 1.6.31: every fork's fence was empty, so the format had
never been exercised, and flows — the first fork to put a real path in
one — had to derive the grammar from the test.

    ```yaml byte-owned
    # this fork's copy wins; the fan-out skips these paths
    - scripts/smoke_live.py
    ```

Grammar, identical to `sync-verbatim` plus ONE entry form of its
own: `- path` list items, one per line, repo-relative, no `..`, `#`
comments allowed, and (1.6.36) `- <path>  # declined: <reason>` —
the fork REFUSES this cargo: it holds an equivalent elsewhere, or its
posture inverts the file. A declined path is the only fence entry
that need not exist at HEAD (every other listed path must), because
it is the one way a fork can say no to cargo it never held —
clerkhook's PACKAGE suite lives at `tests/` root, so a site test
fanned out there would make its matrix ERROR, not skip; its site
tests live under `tests/site/`. The reason is mandatory. The
machine half already existed (`scripts/fanout.py` skips every path
DIVERGENCES names); only the kit test forbade the entry.

    ```yaml byte-owned
    - tests/test_analytics_classifier.py  # declined: package suite at tests/, site copy at tests/site/
    - scripts/smoke_live.py               # declined: lockdown inverts it (DIVERGENCES §6)
    ```

A missing fence
means "no fence" and drops the fan-out back to the mention heuristic,
which over-flags and never restores; an EMPTY fence means "the
template owns every sync-verbatim path here" — a statement, not an
omission. A prose mention is NOT a fence: muicharts' host-pin nuance
names `tests/test_claude_kit.py` in prose while its bytes are
template-owned, and that false positive recurred every release until
the fence answered the question mechanically.

**What belongs in it (1.6.31, and this is the durable half of item 6's
lesson):** if you PORTED a file rather than copying it — because your
copy carries checks the template's does not, or asserts a posture the
template's copy contradicts — that path belongs in the byte-owned
fence in the SAME touch. Three forks reported exactly that content in
the F4 round and only two had fenced it. Class protects a file for as
long as it stays contract-class; the fence protects it across the next
reclass, which is the one nobody will remember.

    ```yaml posture
    ai_bots: {"/": 403, "/llms.txt": 200, "/healthz": 403}
    healthz: full
    runtime: python
    ```

The second fence (1.6.30) declares what this host SERVES, measured
with a real vendor UA: `key: value` lines, known keys only (`ai_bots`,
`healthz` ∈ {minimal, full}, `runtime` ∈ {docker, python}, `deploy` ∈
{release-branch} (1.6.35), `unknown_ai` ∈ {allow, meter, block}
(1.6.36 — the host's `default_unknown_ai`; dimll 2.9.0 widened
"block" to absent and unrecognised UAs, so the value is now a posture
a probe can see)), statuses as integers. The test validates shape plus the one value the repo can
contradict by itself — `runtime:` against render.yaml. Nothing but a
probe can validate a status, so re-measure when you change what the
host serves and paste the probe in your report.

## Authoring rules (earned, not invented)

- **A detect or a pin that reads a source file must PARSE it — or strip
  comments and strings first — AND assert non-vacuity** (it matched
  something; it swept at least N files). Five instances in the 1.6.43
  round read PROSE and called it code: item 15's detect, item 17's
  og:image detect, the file-scoped `.test_client()` pin (red on a
  comment ABOUT greps, then green by sweeping zero files after a
  tokenize rewrite), excalidraw's `record_read` ordering pin matching
  docstring order, and SYNC-1.6.43 item 3's two detects, which were
  casing-bound to this format's own emphasis caps and returned 0 on the
  tree that authored them. Case-insensitivity fixes those two; the rule
  stops the class. Corollary, measured the hard way: parsing is not
  automatically the safe alternative — a regex over a package constant
  truncated on a `)` inside a comment (twice, two seats), and an AST
  rewrite agreed with the wrong answer because both were reading a file
  while the import read a different one. Where a value can be IMPORTED,
  import it and print `__file__`.
  STRIPPING COMMENTS IS NOT THE FIX — it is the half-measure that looks
  like the fix, and 1.6.44 produced three instances in one afternoon on
  the template alone. A menu pin searched raw source for `aria-haspopup`
  and matched the COMMENT explaining why there isn't one; a docs-page
  pin searched for `markdown.py` and matched two comments describing how
  those pages differ from it; and a guard on the retired
  `HeadAsGetMiddleware` passed a comment strip and then matched the live
  DOCSTRING recording the retirement. Strings are the other half of the
  rule, and a docstring is a string. The progression to copy — it is
  written out in the item-9 commit — is: raw grep, comment strip,
  `ast.parse`. Only the third one is right, and it costs four lines:
  walk the tree for `ClassDef`/`FunctionDef` names and `Name`/
  `Attribute` ids, then assert the parse found definitions at all so an
  unreadable file cannot pass as a clean one.
  The reason this class keeps recurring is worth naming: a good comment
  explains the absence of the thing the detect hunts, so the better the
  code is documented, the more reliably a raw grep reports the defect it
  is documenting the absence of. The detects most likely to be wrong are
  the ones on the best-explained code.
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
- **One session per tree (1.6.36).** A sub-agent must not edit files
  its parent also edits — email's child could not see its parent's
  item-13 diff and asked the ops seat whether it was foreign — and a
  drop's completion signal is the REPORT, never an idle notice:
  flexlayout's idle notice fired the moment it delegated, with the
  work still running.
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
