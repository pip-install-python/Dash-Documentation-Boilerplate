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
   `already-present` / `not-applicable-because` (+ evidence).

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
