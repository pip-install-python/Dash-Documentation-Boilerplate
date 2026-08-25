# SYNC 1.6.17 → 1.6.21 (template @ 1.6.21)

The fabric releases. Most of this range is template-only machinery
(the sync/ format itself, spec corrections, the sync-verbatim block)
or rides the block below as bytes — what needs a fork's judgment is
two items. Read `sync/README.md` for the format and `DIVERGENCES.md`
(yours) before anything else.

Floor statement, per the authoring rule: unchanged — `LLMS_PKG_FLOOR`
remains `(2, 7, 1)`. The rationale ladders retain every older rung by
design; do not read those as the floor.

```yaml sync-verbatim
# Whole-file byte-copy targets (sync/README.md). Same four as the
# previous spec — their bytes at 1.6.21 now carry the 1.6.17
# sync-template rewrite, the 1.6.18 fork-skip guard, and the
# 1.6.20/1.6.21 machine-fence pins.
- .claude/skills/wire-verify/SKILL.md
- .claude/skills/sync-template/SKILL.md
- .claude/skills/report/SKILL.md
- tests/test_claude_kit.py
```

### 1. DIVERGENCES.md gains its machine half: `byte-owned` (1.6.21)
class: contract
files: DIVERGENCES.md
detect: the kit test's `test_divergences_carry_the_byte_owned_block`
  passes — exactly one ```yaml byte-owned fence present
contract: append the "Byte-owned paths" section (the template's
  DIVERGENCES.md is the model — copy its section prose; the FENCE
  CONTENT is this fork's judgment and cannot fan out). The fan-out
  never overwrites a listed path; empty means "the template owns
  every sync-verbatim path here". Audit your own prose before
  filling it: a byte-level claim on a sync-verbatim path becomes an
  entry; an explanatory mention does not. The pilots were audited
  2026-08-24 — none of the three carries a byte-level claim on any
  sync-verbatim path (muicharts' host-pin nuance explains how the
  pin READS, and its own prose declares the skills byte-verbatim),
  so all three blocks start EMPTY.
acceptance: kit test green
notes: SEQUENCING — this spec's sync-verbatim block ships the kit
  test that enforces the fence, so a fan-out PR goes red on a fork
  until this item is ported. That red is the designed flag (this
  spec carries a contract item, so every fork needs a session touch
  this round regardless); port this item first and the PR greens.

### 2. CI asserts Docker's own health verdict (1.6.19 0f05540)
class: conditional
predicate: the fork's CI boots the Docker image
files: .github/workflows/ci.yml
detect: the CI body polls `docker inspect -f
  '{{.State.Health.Status}}'` to `healthy` and FAILS on `none`
acceptance: CI green with the verdict step present and the container
  reported healthy
notes: emojimart's template-class finding — the external curl proves
  the app answers, not the HEALTHCHECK instruction; a broken
  HEALTHCHECK shipped silently while everything stayed green. Fails
  on `none` because no HEALTHCHECK means the container is opaque to
  its orchestrator. Pairs with the previous spec's item 5 (the
  HEALTHCHECK itself); on failure dump `{{json .State.Health}}`.

## Reporting

Per-item disposition table (applied / ported-as-contract /
already-present / not-applicable-because, each with evidence), any
DIVERGENCES.md changes (the byte-owned fence content and why), full
suite + CD + `/wire-verify` output, and corrections to THIS SPEC
where it mismatched your tree.
