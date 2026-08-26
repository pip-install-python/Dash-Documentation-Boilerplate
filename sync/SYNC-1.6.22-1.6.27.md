# SYNC 1.6.22 → 1.6.27 (template @ 1.6.27)

Machine-lane hardening (1.6.22 skip-on-absence, 1.6.23 `# requires:`)
rides the block below as bytes. What needs judgment is 1.6.24:
dependabot stops proposing pip floor-raises fleet-wide, and the
actions group auto-merges — one file removal-by-copy, one new
workflow, and two repo settings only an owner can flip. Read
`sync/README.md` for the format and `DIVERGENCES.md` (yours) first.
(1.6.25 amendment: the auto-merge half of that sentence is RETIRED —
see item 1's tail; the block no longer carries the workflow.)
(1.6.26 extends the range with batch-1's two template-class findings
— items 3 and 4 — and the block gains item 3's test. This file was
`SYNC-1.6.22-1.6.24.md` until 1.6.26; one rolling document per
consumption round, renamed as its range grows. 1.6.27 adds item 5 —
one fleet Python — conditional on the fork having a Dockerfile, and
nothing new rides the block: every file the item touches is
fork-divergent or presumes files not every fork carries.)

Floor statement, per the authoring rule: unchanged — `LLMS_PKG_FLOOR`
remains `(2, 7, 1)`. The rationale ladders retain every older rung by
design; do not read those as the floor.

```yaml sync-verbatim
# requires: .claude/CLAUDE.md
# requires: .claude/settings.json
# requires: lib/auth_demos.py
# The four standing kit files (their bytes at 1.6.25 carry the 1.6.22
# byte-owned skip and the 1.6.23 `# requires:` validation) plus the
# 1.6.24 dependabot.yml rewrite. dependabot.yml has said "satellites
# copy this verbatim" since 1.2.0 — the copy now REMOVES the pip
# ecosystem entry, which is the point, not an accident. (1.6.25
# removed dependabot-automerge.yml from this list — item 1 is
# RETIRED; a fork that already copied the workflow must delete it.)
# (1.6.26 adds tests/test_auth_demos.py — item 3's detect — and the
# lib/auth_demos.py gate above: the test imports it, and every fork
# has carried the gate stack since the flip round. EXPECT this test
# RED wherever DEMOS still holds the template's entry — that red IS
# item 3's detect firing; fix DEMOS in the same change, do not skip
# the test.)
- .claude/skills/wire-verify/SKILL.md
- .claude/skills/sync-template/SKILL.md
- .claude/skills/report/SKILL.md
- tests/test_claude_kit.py
- .github/dependabot.yml
- tests/test_auth_demos.py
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

### 3. Every DEMOS entry resolves (1.6.26; found by excalidraw)
class: contract
files: lib/auth_demos.py (the entry — site judgment),
  tests/test_auth_demos.py (the detect — byte-verbatim, rides the
  block)
detect: tests/test_auth_demos.py present and green — every DEMOS
  endpoint is a registered page on THIS site AND its module imports
  and exposes a module-level `component`
contract: the sign-in card must never point at a demo the site
  cannot render. The template ships one working entry
  (/examples/visualization → docs.data-visualization.basic_chart);
  it resolves in the template and in NO fork — and `build_demo`
  swallows the import error BY DESIGN (a broken example must never
  take down the funnel) while its warning only fires when that
  endpoint's card renders, which never happens when the endpoint is
  not a page there. Every fork's gate cards have rendered demo-less
  since fork time, silently; this test is the only loud surface.
acceptance: the test green against the fork's own DEMOS + registry;
  if the table is non-empty, a browser look at that endpoint's
  sign-in card shows the live demo above the "Authentication
  required" copy
notes: the fork picks its OWN entry — excalidraw chose /ai-agent
  with the basic canvas; never a module that calls paid models from
  an unauthenticated card. An EMPTY table passes (deleting the dead
  template entry is the fastest green; choosing a real hero example
  is the funnel work, and it is judgment, not sync). The block
  fan-out will land this test red wherever the dead entry survives —
  that red is the detect firing, not breakage to route around.

### 4. home.py and markdown.py agree on the content pipeline (1.6.26)
class: contract
files: pages/home.py (upstream shape: substitute_versions on
  home.md's text at load). The pin lives in
  tests/test_site_identity.py upstream and is session-class, NOT
  block cargo: it presumes lib/versions.py, which forks predating
  the {{VERSION:...}} mechanism (template df2a8e0) do not have.
detect: the source pin — BOTH pages/home.py and pages/markdown.py
  call substitute_versions, checked by AST, not grep (the
  marker-in-comment trap cuts both ways: a comment naming the call
  satisfies a grep on a file that never runs it)
contract: whatever the docs lane substitutes, the home lane
  substitutes too. /llms.txt serves home.md's text, so a
  {{VERSION:...}} token there ships raw on the most-read machine
  surface when home.py skips the call. The wire check (no "{{" token
  on /llms.txt) is VACUOUS on the day home.md happens to carry no
  token — the source pin is not; run both. A fork without
  lib/versions.py at all first ports the mechanism or records in
  DIVERGENCES.md why it states versions some other way.
acceptance: the pin green; GET /llms.txt carries no {{VERSION: or
  {{DIMLL_VERSION}} token
notes: class ruling — contract, not verbatim: batch-1's own evidence
  (pannellum's hand-written home, item 8's correction in
  SYNC-1.6.10-1.6.16) proves home.py is not whole-file verbatim
  across the population; a byte-copy would clobber fork branding.

### 5. One fleet Python — image, matrix, render.yaml, healthz agree (1.6.27)
class: conditional (predicate: the fork has a Dockerfile) + contract
files: Dockerfile (FROM python:3.14-slim — MINOR tag, never a patch
  pin), render.yaml PYTHON_VERSION (full X.Y.Z, Render's encoding —
  minor must match), ci.yml matrix main + singleton jobs + cd.yml
  verify, lib/health.py + lib/asgi_routes.py (the `python` healthz
  field, one builder both backends), scripts/network_smoke.py (the
  `python_matches_declared` battery check), tests/
  test_python_version.py (the encodings-agreement pins — session-
  class, NOT block cargo: it presumes Dockerfile and render.yaml,
  which the predicate says not every fork carries)
detect: `grep ^FROM Dockerfile` — the tag must be the fleet minor
  and minor-only — AND healthz `python` on the wire reporting the
  same minor. Either alone can lie: the template itself carried a
  patch-pinned 3.11.8 image, a 3.12 matrix and a 3.12.0 render.yaml
  simultaneously, and no battery could see it (ops-seat finding,
  2026-08-25 — read in the tree, invisible on the wire by
  construction).
contract: ONE Python per fork, everywhere it is encoded. The fleet
  Python is 3.14, decided by evidence, not preference: the full
  suite and the docker boot/battery ran green on python:3.14-slim
  (template evidence run + CI matrix, 2026-08-25) with dash 4.4.1,
  dash-improve-my-llms ≥2.7.1, cryptography ≥50 all importing. The
  patch pin is the security bug — a `3.X.Y-slim` FROM never
  receives 3.X fix releases; the minor tag tracks them through the
  registry. render.yaml keeps a full X.Y.Z because Render's native
  runtime requires it — its minor is what must agree, its patch is
  a human bump. A fork whose platform runtime (dashboard
  PYTHON_VERSION) lags the repo declaration will fail the battery's
  python_matches_declared check — that red is the detect firing;
  the fix is the platform side, not the check.
acceptance: CI docker boot/battery green on the fork's own image;
  healthz on the wire carries `python` with the fleet minor;
  tests/test_python_version.py green where adopted
notes: the eight open dependabot docker PRs (python:3.12-slim →
  3.14-slim, 2026-08-25) are the ops seat's triage, not the fork
  session's: merged where byte-equivalent to this item's FROM line,
  closed with "template first, spec item 5" where not. A fork with
  no Dockerfile (predicate false) still benefits from the healthz
  field + battery check halves if it serves via a platform runtime
  — port them as contract; the agreement test then pins render.yaml
  against ci.yml with no image lane.

## Reporting

Per-item disposition table (applied / ported-as-contract /
already-present / not-applicable-because, each with evidence), any
DIVERGENCES.md changes, full suite + CD + `/wire-verify` output, and
corrections to THIS SPEC where it mismatched your tree.
