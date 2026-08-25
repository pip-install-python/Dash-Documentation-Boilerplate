# SYNC 1.6.22 → 1.6.24 (template @ 1.6.24)

Machine-lane hardening (1.6.22 skip-on-absence, 1.6.23 `# requires:`)
rides the block below as bytes. What needs judgment is 1.6.24:
dependabot stops proposing pip floor-raises fleet-wide, and the
actions group auto-merges — one file removal-by-copy, one new
workflow, and two repo settings only an owner can flip. Read
`sync/README.md` for the format and `DIVERGENCES.md` (yours) first.
(1.6.25 amendment: the auto-merge half of that sentence is RETIRED —
see item 1's tail; the block no longer carries the workflow.)

Floor statement, per the authoring rule: unchanged — `LLMS_PKG_FLOOR`
remains `(2, 7, 1)`. The rationale ladders retain every older rung by
design; do not read those as the floor.

```yaml sync-verbatim
# requires: .claude/CLAUDE.md
# requires: .claude/settings.json
# The four standing kit files (their bytes at 1.6.25 carry the 1.6.22
# byte-owned skip and the 1.6.23 `# requires:` validation) plus the
# 1.6.24 dependabot.yml rewrite. dependabot.yml has said "satellites
# copy this verbatim" since 1.2.0 — the copy now REMOVES the pip
# ecosystem entry, which is the point, not an accident. (1.6.25
# removed dependabot-automerge.yml from this list — item 1 is
# RETIRED; a fork that already copied the workflow must delete it.)
- .claude/skills/wire-verify/SKILL.md
- .claude/skills/sync-template/SKILL.md
- .claude/skills/report/SKILL.md
- tests/test_claude_kit.py
- .github/dependabot.yml
```

### 1. Auto-merge is two repo settings away (1.6.24) — RETIRED (1.6.25)
class: contract
files: none — repository settings, owner-only
detect: `GET /repos/{owner}/{repo}` shows `"allow_auto_merge": true`,
  and a branch protection rule / ruleset on `main` requires the CI
  status checks
contract: the workflow the block ships is inert until the owner flips
  "Allow auto-merge" (Settings → General), and OVER-EAGER until `main`
  requires the CI checks — auto-merge waits for REQUIRED checks only;
  with none required the merge lands immediately, green or not
  (GitHub docs, automate-dependabot-with-actions). Flip both before
  or with the merge of the PR that carries the workflow.
acceptance: the next actions-group dependabot PR shows the
  `dependabot-automerge` run green and merges only after CI passes
notes: VERIFICATION TRAP, observed live on the template within
  minutes of shipping (merge `4a1d430`, 2026-08-25). The merge push
  creates ZERO workflow runs (GITHUB_TOKEN anti-recursion) and STILL
  reaches production — the deploy hook builds branch HEAD, so an
  in-flight CD run ships the merge while its own build-match wait
  holds out for the superseded release sha and goes red. After an
  auto-merge, expect: no CI/CD runs on the merge sha, the previous
  release's CD red on build-match, wire build == the merge sha. The
  remedy (as adjusted at retirement) is policy, not diagnosis —
  actions PRs: human merge when green; never a bot actor on main.
  SEQUENCING,
  observed the same way: copying dependabot.yml makes dependabot
  rebase your open actions PRs within seconds, and the workflow then
  merges them — on the template, 79 seconds BEFORE the PR's CI
  finished, because nothing was required. Flip both settings BEFORE
  merging the fan-out PR that carries this pair, or close your open
  actions PRs first.
retired: 2026-08-25, owner option A, one release after shipping.
  Why, in one line — the workflow could only ever fix the GATE
  (merge waits for CI), never the ACTOR: a GITHUB_TOKEN merge gets
  zero workflow runs on its sha, so no CD run certifies the deploy,
  and every repair is a quirk chain (a merge-capable secret per
  repo, or a workflow_run re-trigger that must also dispatch cd.yml
  through the anti-recursion exemption). ~11 human clicks a month
  fleet-wide is cheaper than three quirks holding up the fabric's
  one proof; the workflow_run shape is the recorded deferred option.
  Standing policy replacing this item: actions PRs are merged by a
  human click when the PR's CI is green — never a bot actor on
  main. Do NOT flip "Allow auto-merge" for this item (a
  checks-required ruleset on main remains optional hygiene). FOR
  CONSUMERS: if your fork copied `dependabot-automerge.yml` before
  this retirement, delete it in your next sync — as of retirement,
  no fork had (the pair never fanned out). Everything above this
  line is history, kept as written.

### 2. Close the lingering pip floor-raise PRs (1.6.24)
class: contract
files: none — open pull requests, owner-only
detect: zero open PRs on branches matching `dependabot/pip/*`
contract: removing the pip ecosystem entry stops NEW floor-raise PRs
  but closes nothing — proven on the template itself, where the five
  pip PRs opened 08-01/08-10 outlived the 08-23 allow-list that
  already excluded their packages. Close each with a one-line reason
  ("floors move through sync specs; see .github/dependabot.yml") so
  the dependabot timeline explains itself. Do not close docker PRs —
  base-image bumps remain merits decisions, handled on their merits.
acceptance: pip-branch PR count is zero and each close carries a
  reason
notes: fleet total at the 2026-08-25 reading was 18 pip floor-raises
  across the ten public forks; your count is in your own PR list.

## Reporting

Per-item disposition table (applied / ported-as-contract /
already-present / not-applicable-because, each with evidence), any
DIVERGENCES.md changes, full suite + CD + `/wire-verify` output, and
corrections to THIS SPEC where it mismatched your tree.
