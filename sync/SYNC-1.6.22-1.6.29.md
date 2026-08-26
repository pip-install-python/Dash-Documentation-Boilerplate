# SYNC 1.6.22 → 1.6.29 (template @ 1.6.29)

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
(1.6.28 is the batch-2/3 corrections release, spec and gate grammar
only, no runtime change: the block's gate moves from PATHS to the kit
CONTRACT — see the fence and sync/README.md's gate rule — item 5
gains its `runtime:` branch, the site-vs-package Python split and the
absence-is-not-adopted detect; items 6–7 are new; and
scripts/smoke_live.py rides the block. Three forks (flows,
muischeduler, clerkhook) filed item 5's runtime correction
INDEPENDENTLY in the batch-2/3 round — convergence adjudicated and
accepted by the ops seat, 2026-08-26.)
(1.6.29 pulls scripts/smoke_live.py back OUT of the block after
exactly one round: the LIVE fan-out — 2plot-network run 33000661276 —
landed the byte-identical file red on 7 of 12 forks, because every
fork's OWN tests/test_smoke_live.py monkeypatches `fetch` with the
pre-1.6.2x signature and wake()'s `fetch(url, retries=1, timeout=10)`
TypeErrors on the stub. Invariance of the file is not invariance of
its contract; item 6 is class contract for EVERY fork now, and the
authoring rule this bought — verbatim-safe only if no fork-owned test
exercises the interface; ask "who stubs this?" — is in
sync/README.md. The template's wake() is also stub-tolerant since
1.6.29, so a byte-copy port no longer detonates a not-yet-updated
legacy stub.)

Floor statement, per the authoring rule: unchanged — `LLMS_PKG_FLOOR`
remains `(2, 7, 1)`. The rationale ladders retain every older rung by
design; do not read those as the floor.

```yaml sync-verbatim
# requires-contract: .claude/CLAUDE.md :: Check the prompt against this tree
# The gate names the kit CONTRACT, never a kit path (1.6.28; the
# rule is in sync/README.md): flows carried a tracked
# .claude/CLAUDE.md since March 2026 — the component library's own
# guide, none of the kit — and a path gate read it as kit-adopted.
# The clause is one of the five the kit test greps; present means
# the contract section is really there. The old
# `# requires: .claude/settings.json` line is subsumed — settings
# ride the same adoption, and a pre-existing settings.json is
# exactly as possible as a pre-existing CLAUDE.md.
# SEQUENCING (ops seat): fanout.py must implement
# `# requires-contract:` and the per-file `# requires:` BEFORE the
# next round — an older parser reads the first as a plain comment
# (block UNGATED: kit cargo would ship to non-kit forks) and the
# second not at all (tests/test_auth_demos.py would land red on
# lockdown forks).
# The four standing kit files (their bytes at 1.6.25 carry the 1.6.22
# byte-owned skip and the 1.6.23 `# requires:` validation) plus the
# 1.6.24 dependabot.yml rewrite. dependabot.yml has said "satellites
# copy this verbatim" since 1.2.0 — the copy now REMOVES the pip
# ecosystem entry, which is the point, not an accident. (1.6.25
# removed dependabot-automerge.yml from this list — item 1 is
# RETIRED; a fork that already copied the workflow must delete it.)
# (1.6.26 adds tests/test_auth_demos.py — item 3's detect. EXPECT
# this test RED wherever DEMOS still holds the template's entry —
# that red IS item 3's detect firing; fix DEMOS in the same change,
# do not skip the test.) (1.6.28 moves its lib/auth_demos.py gate
# from the block level to the cargo line below: a lockdown fork has
# no demo gate and no such file LEGITIMATELY — clerkhook, forks=all
# dry run 32991971564 — and must still receive the rest of the
# block; the per-file gate skips just that one copy. 1.6.28 also
# added scripts/smoke_live.py — item 6: fork-invariant by
# construction, host from argv, knobs from env — while muischeduler
# certified CD with a 1.2.4-vintage copy: no wake loop, no retries.
# 1.6.29 REMOVES it after one live round: byte-invariant, but its
# INTERFACE is pinned by each fork's own tests/test_smoke_live.py —
# fetch stubs written for the pre-1.6.2x signature TypeErrored in
# wake() on 7 of 12 forks, run 33000661276. Item 6 is contract-class
# now; the rule is in sync/README.md: who stubs this?)
- .claude/skills/wire-verify/SKILL.md
- .claude/skills/sync-template/SKILL.md
- .claude/skills/report/SKILL.md
- tests/test_claude_kit.py
- .github/dependabot.yml
- tests/test_auth_demos.py  # requires: lib/auth_demos.py
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
  1.6.29 cargo audit (the who-stubs-this rule): nothing stubs this
  test, but it CALLS INTO two fork-owned seams — DEMOS's shape
  (mapping endpoint → {"module": ...}; `spec["module"]` assumes
  dict values) and conftest's `app_module` fixture. Both are
  fleet-uniform today (the 1.6.28 round landed it with zero
  interface reds); a fork that reshaped either reads a red here as
  interface drift, not the detect firing — port as contract there.

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

### 5. One fleet Python — image, matrix, render.yaml, healthz agree (1.6.27; amended 1.6.28)
class: conditional (predicate: the fork has a Dockerfile) + contract
files: Dockerfile (FROM python:3.14-slim — MINOR tag, never a patch
  pin), render.yaml PYTHON_VERSION (BRANCHES on `runtime:` — see
  contract), ci.yml matrix main + singleton jobs + cd.yml
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
  construction). A MISSING `python` field on healthz is NOT-ADOPTED,
  never not-applicable (1.6.28): emojimart's image moved to 3.14 via
  dependabot alone, so the cheap half of this detect passed while
  the expensive half failed invisibly — absence counts as a fail.
contract: ONE Python per fork, everywhere it is encoded — and the
  Python in scope is the SITE's, not any package's (1.6.28, filed
  independently by flows and clerkhook): a fork's ci.yml may carry
  PACKAGE matrices testing a wheel's `requires-python` claim
  (3.9–3.13 is normal) beside the SITE lane. Those are the package's
  business and outside this item. The pins hold the SITE lane — the
  jobs that install the site's requirements file (requirements.txt
  here, requirements-docs.txt on component forks) and boot/serve the
  docs app — to the image's minor; name the lane in the test so a
  session can tell which of the two Pythons any pin is reading. The
  fleet Python is 3.14, decided by evidence, not preference: the
  full suite and the docker boot/battery ran green on
  python:3.14-slim (template evidence run + CI matrix, 2026-08-25)
  with dash 4.4.1, dash-improve-my-llms ≥2.7.1, cryptography ≥50
  all importing. The patch pin is the security bug — a `3.X.Y-slim`
  FROM never receives 3.X fix releases; the minor tag tracks them
  through the registry. render.yaml BRANCHES ON THE SERVICE RUNTIME
  (1.6.28, filed independently by flows, muischeduler and clerkhook
  — adopted): `runtime: python` → PYTHON_VERSION is REQUIRED, full
  X.Y.Z because Render's native runtime demands that encoding,
  minor pinned to the fleet Python, patch a human bump.
  `runtime: docker` → PYTHON_VERSION must be ABSENT: nothing reads
  it there, and a string that reads like the platform's setting and
  can never be true is this item's own defect class arriving
  through the fix. Any other runtime fails the test loudly — extend
  the branch deliberately. tests/test_python_version.py upstream
  carries BOTH branches as the reference implementation, not just
  the template's own service type. A fork whose platform runtime
  (dashboard PYTHON_VERSION) lags the repo declaration will fail
  the battery's python_matches_declared check — that red is the
  detect firing; the fix is the platform side, not the check. On a
  host whose DIVERGENCES.md declares a MINIMAL healthz payload
  (clerkhook's recorded divergence), python_matches_declared must
  SKIP-WITH-NOTICE, never fail (1.6.28): the fork proves its
  interpreter in-image in CI instead, and F4 reads the skip as
  declared divergence rather than drift.
acceptance: CI docker boot/battery green on the fork's own image;
  healthz on the wire carries `python` with the fleet minor (or the
  recorded minimal-payload divergence plus the in-image CI proof);
  tests/test_python_version.py green where adopted
notes: the eight open dependabot docker PRs (python:3.12-slim →
  3.14-slim, 2026-08-25) are the ops seat's triage, not the fork
  session's: merged where byte-equivalent to this item's FROM line,
  closed with "template first, spec item 5" where not. A fork with
  no Dockerfile (predicate false) still benefits from the healthz
  field + battery check halves if it serves via a platform runtime
  — port them as contract; the agreement test then pins render.yaml
  against ci.yml with no image lane.

### 6. smoke_live.py: wake loop, retry ladder, SSL context (1.6.28; reclassed contract 1.6.29)
class: contract
files: scripts/smoke_live.py (or the fork's recorded divergent tool),
  tests/test_smoke_live.py (fork-OWNED and never cargo: BASE, the
  canonical host and the og:image URL inside it are per-fork)
detect: the cold-start wake loop present (`SMOKE_WAKE_ATTEMPTS`),
  fetch retries present (`SMOKE_FETCH_RETRIES`), and an explicit SSL
  context on EVERY urlopen — the GET fetch and the auth POST both.
  This is now THE detect for every fork, not just divergent-tool
  ones.
contract: whatever live tool a CD run certifies with must carry the
  wake loop, the retry ladder and the certifi-backed SSL context.
  The file had no spec item, so it drifted exactly as unversioned
  copies do: muischeduler ran a 1.2.4-vintage copy — no wake loop,
  no env knobs — against a free-tier host in CD; clerkhook's
  lockdown_smoke.py had no SSL context while being that host's ONLY
  deploy proof (flexlayout filed the same class earlier — the POST
  half, pinned upstream in tests/test_auth_wiring.py).
  RECLASSED 1.6.29, after exactly one round as block cargo: the live
  fan-out (run 33000661276) landed the byte-identical file red on 7
  of 12 forks — every fork's OWN tests/test_smoke_live.py
  monkeypatches `fetch` with the pre-1.6.2x signature
  `(url, user_agent, accept)`, and wake()'s
  `fetch(url, retries=1, timeout=10)` TypeErrors on the stub. The
  file's bytes are fork-invariant; its INTERFACE is pinned by a
  fork-owned, fork-specific test that can never be cargo — so the
  class is contract, per sync/README.md's who-stubs-this rule. A
  session ports the behaviour and updates its stubs IN THE SAME
  TOUCH. Byte-copying the template's current file remains the
  recommended port — since 1.6.29 its wake() probes tolerantly
  (falls back to `fetch(url)` when a legacy stub rejects the
  kwargs; pinned by test_wake_survives_a_legacy_fetch_stub
  upstream), so a copy landing ahead of the stub update degrades to
  the fork's old red checks instead of a suite-wide TypeError. The
  stub update is still the port's second half, not optional.
acceptance: the fork's own tests/test_smoke_live.py green against
  its own copy; the fork's next CD log shows the wake ladder
  running.
notes: a fork that replaced the tool records the divergence and
  ports the contract half; a template copy landing beside it is
  inert unless cd.yml invokes it. Green in the 1.6.28 round proved
  only stub-compatibility, not currency: emojimart, muicharts and
  pipdocs matched signatures, clerkhook has no such test — run the
  detect there anyway.

### 7. The battery must see the CONFIGURED gate page (1.6.28; found by clerkhook)
class: conditional + contract
predicate: the fork serves a sign-in gate or lockdown page — any
  page whose rendering changes when auth/lockdown secrets are
  present
files: the fork's gate/lock page module + its test suite (shapes
  differ per fork; no byte target)
detect: a test renders the gate/lock page with a FAKE, non-empty
  config (a dummy publishable key is enough — never a real secret)
  and asserts the CONFIGURED branch actually rendered — a marker
  only that branch emits, so the assertion is non-vacuous — with
  the marker/stripping rules IMPORTED from the live tool's own
  module by path, never duplicated into the test.
contract: every fleet battery boots zero-secret, so any page that
  renders differently once secrets are present has its configured
  branch certified by NOTHING — the battery tests the wrong page.
  Observed end-to-end on clerkhook: no test had ever rendered the
  lock page's ClerkJS bootstrap branch, and the first live run of
  lockdown_smoke.py produced 220 false "leaks" (the package's own
  RECONCILE_MARK string), a traceback on a chunked short read, and
  a verdict on a partial body — fork-local fixes in clerkhook
  5c5e9ea; the CLASS is fleet-wide. Importing the tool's rules is
  what keeps test and tool from drifting apart again.
acceptance: the test green in the fork's suite; the fork's live
  gate tool runs against production without false leaks.
notes: THE TEMPLATE'S OWN ADOPTION IS OPEN — conftest.py blanks
  every Clerk secret before any import, so this suite renders the
  sign-in gate cards zero-secret only; the detect fires here too.
  Recorded as `open` in the 1.6.28 report, queued for the next
  template runtime pass (this release is spec-only by design).

## Reporting

Per-item disposition table (applied / ported-as-contract /
already-present / not-applicable-because / open, each with
evidence), any DIVERGENCES.md changes, full suite + CD +
`/wire-verify` output, and corrections to THIS SPEC where it
mismatched your tree. `open` (1.6.28): the detect fires but the
item is deliberately out of this session's scope — name it and who
acts; do not invent another word.
