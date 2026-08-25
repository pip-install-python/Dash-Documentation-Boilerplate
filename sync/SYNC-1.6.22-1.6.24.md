# SYNC 1.6.22 → 1.6.24 (template @ 1.6.24)

Machine-lane hardening (1.6.22 skip-on-absence, 1.6.23 `# requires:`)
rides the block below as bytes. What needs judgment is 1.6.24:
dependabot stops proposing pip floor-raises fleet-wide, and the
actions group auto-merges — one file removal-by-copy, one new
workflow, and two repo settings only an owner can flip. Read
`sync/README.md` for the format and `DIVERGENCES.md` (yours) first.

Floor statement, per the authoring rule: unchanged — `LLMS_PKG_FLOOR`
remains `(2, 7, 1)`. The rationale ladders retain every older rung by
design; do not read those as the floor.

```yaml sync-verbatim
# requires: .claude/CLAUDE.md
# requires: .claude/settings.json
# The four standing kit files (their bytes at 1.6.24 carry the 1.6.22
# byte-owned skip and the 1.6.23 `# requires:` validation) plus the
# 1.6.24 dependabot pair. dependabot.yml has said "satellites copy
# this verbatim" since 1.2.0 — the copy now REMOVES the pip ecosystem
# entry, which is the point, not an accident.
- .claude/skills/wire-verify/SKILL.md
- .claude/skills/sync-template/SKILL.md
- .claude/skills/report/SKILL.md
- tests/test_claude_kit.py
- .github/dependabot.yml
- .github/workflows/dependabot-automerge.yml
```

### 1. Auto-merge is two repo settings away (1.6.24)
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
notes: VERIFICATION TRAP, fleet-wide — auto-merge here is enabled by
  `GITHUB_TOKEN`, and GITHUB_TOKEN-triggered events do not create
  workflow runs (the Actions anti-recursion rule). If the eventual
  merge push does not trigger cd.yml, healthz `build` will lag HEAD
  after every auto-merged actions bump. That is NOT the cache trap:
  before diagnosing a build/HEAD mismatch, check whether HEAD is a
  dependabot actions merge. First live auto-merge on each repo is the
  experiment; if CD is confirmed suppressed, report it — the fix
  (ops-seat PAT vs. accepting the lag for workflow-only commits) is
  an ops-seat decision, not a fork-side one.

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
