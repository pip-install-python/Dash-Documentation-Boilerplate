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
# requires-contract: .claude/CLAUDE.md :: Check the prompt against this tree
# (Gate converted 1.6.28: a path gate read flows' pre-existing,
# non-kit .claude/CLAUDE.md as kit-adopted — a gate names a
# CONTRACT, never a path, wherever a pre-existing file can occupy
# the path; sync/README.md. The settings.json path gate is subsumed
# by the same adoption.)
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
detect: `pytest -v tests/test_claude_kit.py` shows
  `test_divergences_carry_the_byte_owned_block PASSED` — literally
  PASSED (1.6.28 wording): a SKIP is not-ported by 1.6.22's design,
  and an ABSENT test (a kit predating it) is not-ported too.
  `pytest -q`'s "6 passed, 1 skipped" reads identically for both
  unported states — emojimart sat in the absent one while its
  summary looked adopted. "Kit test green" was satisfiable by two
  states this item had not reached.
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
  so all three blocks start EMPTY. THE FENCE QUESTION (1.6.28,
  filed by flexlayout): an entry is a path whose difference the
  fork CHOSE — leaflet's npm ecosystem in dependabot.yml — never
  "does the file differ?". flexlayout's and muicharts' dependabot.yml
  differed from the template only by being BEHIND 1.6.24 (pip
  ecosystem still present): that is unsynced DRIFT, and fencing it
  freezes it in and routes a mechanical item to a session forever.
  Drift is never fenced — the fan-out is how it gets fixed.
acceptance: kit test green, with the detect's PASSED wording — a
  SKIP or an absent test is not this item landed
notes: SEQUENCING — this spec's sync-verbatim block ships the kit
  test that validates the fence, and on a fork that has not ported
  this item the pin SKIPS with a reason naming it ("port
  SYNC-1.6.17-1.6.21 item 1; until then the fan-out uses the
  mention heuristic" — 1.6.22, the ops seat's own correction of its
  red-until-ported first cut). The verbatim promise holds: fan-out
  PRs merge green regardless; CI guards what a fork HAS declared,
  and adoption is driven by this contract item's session round.
  EVIDENCE FOR THE FENCE, batch-2 (1.6.28): fan-out PR #6 on
  muicharts copied .claude/skills/sync-template/SKILL.md but
  WITHHELD tests/test_claude_kit.py — the mention heuristic read
  §8-style prose as a byte-claim on the very file carrying the
  fence's own pin. A present fence makes that misread impossible;
  that PR is the concrete case for porting this item.

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
already-present / not-applicable-because / open, each with
evidence), any DIVERGENCES.md changes (the byte-owned fence content
and why), full suite + CD + `/wire-verify` output, and corrections
to THIS SPEC where it mismatched your tree. `open` (1.6.28): the
detect fires but the item is deliberately out of this session's
scope — name it and who acts.
