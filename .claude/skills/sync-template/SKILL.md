---
name: sync-template
description: Apply a dash-documentation-boilerplate release to this fork — divergence-aware, spec-driven, acceptance-pinned. Use when a drop asks this repo to sync template changes or move a dependency floor.
---

The template is upstream; this fork is sovereign. A sync ports what
the template learned without erasing what this fork decided.

1. **Read `DIVERGENCES.md` FIRST.** Anything recorded there is
   design: a sync must not "restore" it. If a template change
   collides with a recorded divergence, port the change's CONTRACT
   (behavior + its test pins) into this fork's shape instead of
   copying the file — and say so in the report.

2. **Find the work list.** Preferred: the release's sync spec
   (`sync/SYNC-<version>.md` in the template repo), which classifies
   every change as `verbatim` (byte-copy target), `contract` (port
   the behavior, not the file), or `conditional` (applies only if a
   stated predicate matches this repo). If no spec exists, the
   drop's prompt supplies the list — check it against this tree
   before executing; a step that does not fit this repo is a finding
   to return, not an instruction to force.

3. **Floors**: a dependency floor lives in several encodings —
   requirements.txt, run.py's boot-floor tuple AND its message,
   tests, CI asserts. Grep the current number and move every one.
   The requirements line changing IS the Docker cache bust; extend
   rationale ladders, never rewrite them, and never touch CHANGELOG
   history. If this repo has no boot floor, add one — then break it
   deliberately once to watch it refuse, and restore it.

4. **Apply**: verbatim items byte-copied; contract items ported
   against this fork's shape with the template's test pins adapted;
   conditional items checked against their predicate and either
   applied or reported as not-applicable with the evidence. New
   deliberate differences created during the sync go into
   `DIVERGENCES.md` in the same commit.

5. **Acceptance**: full suite green locally; push; CI/CD green
   (this repo's CD must certify THE artifact — a wait that polls
   healthz until `build == GITHUB_SHA`); then `/wire-verify` against
   production. A sync is not done until the wire agrees.

6. **Report** via `/report`: include per-item disposition
   (applied / ported-as-contract / not-applicable-because), any
   DIVERGENCES.md updates, and anything the prompt got wrong about
   this repo.
