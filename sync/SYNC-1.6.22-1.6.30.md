# SYNC 1.6.22 → 1.6.30 (template @ 1.6.30)

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
(1.6.30 is the F4-battery round, closed by the two §A fork sessions
— emojimart f6da429, muicharts 9c4985e. Nothing new rides the block;
what changes is what the items ASK. Item 6 grows the QUIET half of
its failure mode — a fork with no tests/test_smoke_live.py at all,
where the byte copy landed green because nothing offline exercised
it and CD against production was the first thing to run the script —
and names BOTH live tools, network_smoke.py having shipped without
an SSL context until now. Item 5's window rule is corrected (the
fleet minor, one adjacent minor, and the site's declared floor where
it is lower) and its reference test is job-scoped, so a fork with a
package matrix stops failing on a lane the item disclaims. Items 8
and 9 are new: browser/crawler head parity, which measured wrong on
six of seven audited hosts, and the machine-readable POSTURE fence in
DIVERGENCES.md that moves the hub's seeded table into the repos that
can keep it true.)

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
  THE CLASS IS NOT RETIRED WITH THE ITEM (1.6.30): the trap is
  SUPERSESSION — the wait cannot distinguish "not deployed yet" from
  "already replaced" — and auto-merge was only its most reliable
  road. Two human pushes inside one deploy window, or deploy-hook
  dispatch lag, reach the same state with no bot anywhere. Read this
  item as "the bot actor is off main", never as "this host is
  immune"; the standing diagnosis is 1.6.25's fast-fail on a live
  build that is a DESCENDANT of the wanted sha, which does not care
  who merged.
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
files: lib/auth_demos.py — TWO things in it, not one (1.6.30, found
  by pannellum): the entry (site judgment) AND the module docstring's
  1.6.26 paragraph, the one beginning "The table ships with ONE
  working entry in the template". A fork whose copy still reads "The
  table ships EMPTY in the template" is describing a template that
  stopped existing at 1.6.26, and the next reader picks the wrong
  default. Port the paragraph with the entry —
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

### 5. One fleet Python — image, matrix, render.yaml, healthz agree (1.6.27; amended 1.6.28, 1.6.30)
class: conditional (predicate: the fork has a Dockerfile) + contract
files: Dockerfile (FROM python:3.14-slim — MINOR tag, never a patch
  pin), render.yaml PYTHON_VERSION (BRANCHES on `runtime:` — see
  contract), ci.yml matrix main + singleton jobs + cd.yml
  verify, lib/health.py + lib/asgi_routes.py (the `python` healthz
  field, one builder both backends), scripts/network_smoke.py (the
  `python_matches_declared` battery check), tests/
  test_python_version.py (the encodings-agreement pins — session-
  class, NOT block cargo: it presumes Dockerfile and render.yaml,
  which the predicate says not every fork carries; JOB-SCOPED since
  1.6.30, and a fork adapts exactly three things in it —
  `SITE_LANE_JOBS`, `PACKAGE_LANE_JOBS`, `SITE_PYTHON_FLOOR`)
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
  THREE 1.6.30 CORRECTIONS, all from §A sessions running the 1.6.28
  text against real forks:
  (a) THE SITE LANE IS DECLARED BY JOB NAME, not by file. Until
  1.6.30 the reference test's greps read the whole ci.yml while its
  docstring promised the site lane only — so the first fork with a
  package matrix failed on the lane this item explicitly disclaims.
  The shape to port (emojimart's): parse `jobs:`, classify every job
  into `SITE_LANE_JOBS` or `PACKAGE_LANE_JOBS`, read site-lane job
  bodies only, and carry the GUARD — a job that declares a Python
  literal and sits in neither set fails loudly. Scoping without the
  guard turns a red into a silence, which is the worse of the two.
  (b) THE WINDOW IS the fleet minor, ONE adjacent minor, and the
  SITE'S DECLARED FLOOR where it is lower — not a contiguous
  three-wide window. emojimart legitimately keeps a 3.10 leg
  (python-frontmatter needs typing.TypeGuard, so 3.10 is its real
  floor, four minors under the fleet Python); muicharts legitimately
  narrowed to 3.13/3.12. Breadth is a CEILING here, never a quota.
  The floor is a promise the README makes, so pin the two together —
  a floor declared only inside the test widens the window on nothing.
  (c) PINS COMPARE THE MINOR — say it in the item, because the patch
  is not yours to assert. Render RESOLVES the patch: muicharts asked
  for 3.14.7 and was served 3.14.3, which is the platform doing what
  it documents. A patch-level assertion against a native runtime is a
  test that fails on correct behaviour; the minor is the contract,
  and `python_matches_declared` on the wire holds the running
  interpreter to it.
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

### 6. The live tools: wake loop, retry ladder, SSL context (1.6.28; reclassed contract 1.6.29; both tools + the quiet failure mode 1.6.30)
class: contract
files: BOTH live tools (1.6.30) — scripts/smoke_live.py AND
  scripts/network_smoke.py, or the fork's recorded divergent
  equivalent of either. The contract sentence always said "whatever
  live tool a CD run certifies with"; the files: line named one, and
  the unnamed one shipped without an SSL context to the whole fleet.
  Plus tests/test_smoke_live.py — fork-OWNED, never cargo, but PORTABLE:
  the template's copy indirects every fork-specific value through
  lib.constants (BASE_URL, OG_IMAGE_*), so the body ships unchanged
  and only the fork's own stubs and divergences are local. It stays
  out of the block because tool and test move as ONE port, not
  because its bytes differ (1.6.30 correction — the 1.6.29 text said
  "BASE, the canonical host and the og:image URL inside it are
  per-fork", which describes the values, not the file).
detect: FOUR questions, and the fourth is the one 1.6.29 missed —
  (1) the cold-start wake loop present (`SMOKE_WAKE_ATTEMPTS`),
  (2) fetch retries present (`SMOKE_FETCH_RETRIES`),
  (3) an explicit SSL context on EVERY urlopen in EVERY live tool —
  the GET fetch and the auth POST both, in smoke_live.py and in
  network_smoke.py,
  (4) DOES tests/test_smoke_live.py EXIST AT ALL? Absence is
  NOT-ADOPTED, never not-applicable — the item-5 absent-field rule,
  arriving here for the same reason. This is THE detect for every
  fork, not just divergent-tool ones.
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
  THE QUIET HALF (1.6.30, emojimart and muicharts). 1.6.29 diagnosed
  the LOUD failure — a legacy stub TypeErrors and the fork's suite
  goes red, which at least tells somebody. The quiet one is a fork
  with NO tests/test_smoke_live.py: the byte copy lands, CI is green
  because nothing offline exercises the script, and the first thing
  ever to run it is CD against production. Both §A forks were in
  that state, and green told nobody. Where the test is absent the
  port CREATES it from the template's reference — the body ships
  unchanged (everything fork-specific is indirected through
  lib.constants) — and only then is the tool's behaviour ported.
  Test first, tool second, both in the same touch.
  network_smoke.py's own gap is the same shape (1.6.30, muicharts):
  no SSL context, invisible for the CI seat because CI runs it
  against http://localhost where TLS never comes up. Run from a Mac
  against a production https host it returned 0/12 —
  indistinguishable from the site being down, and the fleet standard
  in scripts/audit_links.py and smoke_live.py already had the fix.
  Both tools carry the certifi-backed context upstream from 1.6.30.
acceptance: the fork's own tests/test_smoke_live.py EXISTS and is
  green against its own copy; the fork's next CD log shows the wake
  ladder running; both live tools import and use an SSL context.
notes: a fork that replaced the tool records the divergence and
  ports the contract half; a template copy landing beside it is
  inert unless cd.yml invokes it. THE 1.6.28 ROUND'S GREENS WERE NOT
  ONE THING (corrected 1.6.30, and the correction matters because
  the file has since LEFT the block — removal stops the next
  fan-out and undoes nothing, so every fork that took the copy still
  has it): 7 of 12 went red on legacy stubs — port both halves and
  the red goes away. pipdocs matched signatures — currency still
  unproven, run the detect. emojimart and muicharts had NO
  tests/test_smoke_live.py at all, which is why they were green;
  1.6.29's note claiming they "matched signatures" was wrong, and
  their remedy is detect question 4, not a stub update. clerkhook
  has no such test either and runs a divergent tool — run the detect
  on lockdown_smoke.py. Where this round's evidence cannot say which
  state a fork is in, the detect is the first step, not the last.

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

### 8. The two heads declare the same identity (1.6.30; measured by emojimart)
class: contract
files: templates/index.html (the BROWSER head), run.py's
  `configure_seo(icons=..., ...)` (the CRAWLER head), and the pin —
  tests/test_seo_icons.py. Contract, not cargo, and by the mirror
  rule in sync/README.md: the pin CALLS INTO run.py, a fork-owned
  file, so it must land as behaviour a fork can satisfy in its own
  shape.
detect: two questions, offline, both cheap —
  (1) the browser head's `<link rel=icon|apple-touch-icon>` set,
  compared to `configure_seo(icons=)` as unordered (rel, href,
  sizes) triples with query strings stripped (Dash injects one
  cache-busting favicon link that is nobody's declaration), is EQUAL;
  (2) `twitter:card` appears exactly once as `name=` and exactly
  once as `property=`.
contract: content may differ between the crawler document and the
  browser document — that is what the prerender is for. IDENTITY MAY
  NOT, and the two heads are edited by hand in two different files,
  so nothing but a pin holds them together. Measured on the wire by
  emojimart and re-spot-checked by the ops seat, they had drifted on
  SIX OF SEVEN audited hosts: leaflet on the card; flows, email and
  muischeduler on icons; modelviewer and pannellum on both. The
  browser side was the poor one — usually missing 512x512, often
  192x192 too, the sizes Google prefers — and six of the seven share
  the boilerplate icon set, so this is one inherited edit reaching
  six hosts, not six mistakes. Two template-class facts underneath:
  (a) Dash emits the whole twitter:* set with `property=`, while the
  card spec wants `name=`; the static `name="twitter:card"` beside
  Dash's tag is therefore CORRECT and is the deliberate exception to
  "no static duplicate of a Dash-emitted meta" — the exemption must
  be written into that test explicitly and both forms pinned at one
  occurrence each, or the exception decays in either direction.
  (b) smoke_live.py's wire-side parity block was RIGHT on both hosts
  and is not a substitute: it compares the SET OF SIZES, so a bare
  .ico href pointing somewhere the other head never names is
  invisible to it. Offline triples see it; the template's own copy
  was wrong exactly there.
acceptance: tests/test_seo_icons.py green (both pins) in the fork's
  suite, and the fork's next live smoke run green on the
  crawler/browser identity parity block.
notes: CHECK THE TEMPLATE'S OWN index.html FIRST — the instruction
  earned itself. At 1.6.29 the boilerplate declared
  `/assets/favicon.ico` in the browser head and
  `/assets/favicon/favicon.ico` in the crawler head: byte-identical
  files, different paths, one extra browser-only declaration, and
  four passing icon tests. Fixed in 1.6.30 by moving the browser
  link onto the declared path. A fork whose two heads disagree fixes
  the BROWSER side by default — the declaration in run.py is what
  autodiscovery agrees with and what the crawler reads.

### 9. DIVERGENCES.md declares this host's POSTURE (1.6.30; F4)
class: contract
files: DIVERGENCES.md (the `yaml posture` fence),
  tests/test_claude_kit.py (the shape validator — byte-verbatim,
  rides the block)
detect: DIVERGENCES.md carries a second fenced block, ```yaml
  posture, alongside the byte-owned one; the kit test's
  posture pin is present and not skipping.
contract: the hub's F4 battery seeds each host's declared posture
  from its own table — which is a copy of a measurement somebody
  took once, aging in the one repo that cannot observe the host.
  Home the posture where it can be kept true. Three optional keys:
  `ai_bots` (a JSON object of path → status as measured with a REAL
  vendor UA — ClaudeBot, GPTBot; not a UA-less curl, which is
  classified separately and may land in either lane), `healthz`
  (`minimal` | `full` — the clerkhook divergence has a name here
  now), `runtime` (`docker` | `python`, the same value item 5
  branches on). FROM MEASUREMENT, NOT FROM INTENT: nothing but a
  probe can validate a status, so the test validates the SHAPE —
  one fence, known keys only, enum values, statuses that are
  integers — plus the one value the repo can contradict by itself,
  `runtime:` against render.yaml. An EMPTY fence means "the template
  defaults", present so the absence is a statement; absence of the
  fence SKIPS, like byte-owned, so a fork that has not ported this
  keeps its CI green and receives the item instead of a red.
acceptance: the kit test's posture pin green (not skipped) in the
  fork's suite, and every declared number reproduced by a probe
  pasted in the fork's report.
notes: re-measure when you change what the host serves — a stale 403
  in this fence is exactly the hub-table problem moved one repo
  closer. Template's measurement, 2026-08-27, build 5589318:
  `{"/": 403, "/llms.txt": 200, "/healthz": 403}` for ClaudeBot and
  GPTBot alike (a browser UA gets 200 on all three) — the agent
  surface stays open while the browser document is refused, which is
  the posture and is invisible from a browser.

## Reporting

Per-item disposition table (applied / ported-as-contract /
already-present / not-applicable-because / open, each with
evidence), any DIVERGENCES.md changes, full suite + CD +
`/wire-verify` output, and corrections to THIS SPEC where it
mismatched your tree. `open` (1.6.28): the detect fires but the
item is deliberately out of this session's scope — name it and who
acts; do not invent another word.
