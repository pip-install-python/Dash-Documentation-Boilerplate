# SYNC 1.6.22 → 1.6.40 (template @ 1.6.40)

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
(1.6.31 is the round's own lesson, and three of its four changes
arrived as fork PUSHBACK the ops seat adjudicated. Item 6 stops
recommending a byte copy: flexlayout, leaflet and muischeduler each
showed the premise false — their smoke_live.py carries fork-owned
CHECKS, so a copy deletes measured guards silently (green, because a
deleted check does not fail) or asserts a posture the host does not
have (muischeduler's deliberate `block_ai_training=False` fails on
the byte-identical file). Diff and port; a copy is only safe when the
diff is empty both ways. Item 8 gains tests/test_social_card.py in
its `files:` — pannellum and modelviewer independently landed a red
there that the item's prose predicted and its scope line did not.
Item 10 is new: /healthz declares the fleet's SHAPE, after a
thirteen-host read found one fork answering `dash` where the battery
asks for `dash_version` while reporting item 5 green — correctly, the
round could not see it. Nothing new rides the block and no cargo
file's bytes change this round: both new template tests
(tests/test_healthz_shape.py, tests/test_gate_configured.py) CALL
INTO fork-owned modules — lib/health.py, lib/access.py,
lib/gate_layouts.py — so the mirror rule makes them contract, not
cargo. `.claude/CLAUDE.md`'s two trap rewrites port by the authoring
rule, as always: traps verbatim, everything above them adapted.)
(1.6.32 is a DEFECT release and item 11 is the only new item. HEAD
returns 405 on every route of both FastAPI forks — pannellum and
muischeduler, measured on the wire 2026-08-27, `/healthz` and
`/robots.txt` and `/sitemap.xml` included — because Werkzeug derives
a HEAD rule from every GET rule and FastAPI's `APIRoute` does not.
(That clause said "Starlette" until 1.6.33; Starlette's own `Route`
adds HEAD — see item 11's contract.) It is not a
fork's mistake: both hosts inherited it by choosing the backend the
template ships, and nothing in the contract could see it, because CI
never issued a HEAD and both live tools GET. The template's fix is
one ASGI middleware, its pin runs per backend, and both live tools
gain one request. Also here: 1.6.31's HEAD trap is CORRECTED in
`.claude/CLAUDE.md` — it said the ASGI hosts drop the `Link` headers
on HEAD, which was a true observation of a 405 and a wrong diagnosis
— and a new trap line makes the certifi/retry habit general, which
arrived as this seat's own pushback. Nothing new rides the block:
tests/test_head_method.py calls into the app run.py builds, and
`scripts/smoke_live.py` has been contract-class since 1.6.29 — this
round it grows a keyword, which is precisely why.)
(1.6.33 is a CORRECTION release — text only, no runtime change, no
change to the block — and it lands BEFORE the fan-out that carries
item 11, because that item currently teaches a mechanism that is
false. Three things. The LAYER: it is FastAPI's `APIRoute`, not
Starlette; `starlette.routing.Route` adds HEAD to every GET route the
way Werkzeug does, verified in the installed source of both packages
here. The POPULATION: seven ASGI hosts, not two — the two fleet forks,
the hub (which had the defect and has fixed it), and four second-ring
hosts this spec will never reach mechanically, named anyway. The
PERMANENCE: dash-improve-my-llms 2.7.2 fixes the package's own seven
doc routes, and the middleware STAYS regardless, because `/` is Dash's
page catch-all and every Dash route is an `APIRoute` — measured in
this tree, not assumed. Item 10 gains the hub as a fourth red and the
shape lesson behind it: a hand-declared healthz drifts silently, and a
package floor can make a key impossible rather than absent, which are
different states with different remedies.)

(1.6.34 is the LEDGER round — item 12, the first runtime item since
1.6.32. dash-improve-my-llms 2.8.0 produces the ledger's key
(`classify()`) and its row (`on_document_read`); the template's tracker
stops classifying and delegates, `run.py` keeps the row as a second
table in the analytics file, the rollup gains an additive `vendors[]`
block, and `/admin/traffic` shows the host its own ledger. The block
gains the two tests that import nothing fork-shaped and drops nothing.)
(1.6.35 is the RELEASE-BRANCH round — item 13, pipeline and docs only,
no runtime change: Render deploys `release`, and only CD writes it.
Nothing new rides the block: every cd.yml in the fleet differs from
the template's in host, timeouts and comments — 12 of 12 measured
2026-08-29 — so the item is contract-class by the README's rule.)
(1.6.36 is what the FIRST wire round taught the block — item 14, spec
+ kit test + README, no runtime code: the `# declined:` fence entry so
a fork can refuse cargo it never held (clerkhook's package suite at
tests/ root would ERROR on a site test dropped there); the v4 rollup
test made v3-agnostic and CHECKED against a pre-v3 fixture in the
template's own suite; the dead-cargo rule; the `unknown_ai` posture
key and the headless-browser trap from dimll 2.9.0 (floor stays
2.8.0); and the one-session-per-tree authoring rule.)
(1.6.37 is ROUND 3.4 — THE POSTURE FLIP, item 15, one flag and the
documents around it: training crawlers are ALLOWED by default because
the ledger now records and reconciles every read. Canary = boilerplate
+ llms; the fleet consumes it as item 15; clerkhook keeps its wall by
design. Two walls, one order: the app half is this item; the EDGE half
(the Cloudflare rule) is the owner's, after the seat verifies the app
half on the wire.)
(1.6.38 is the NAVIGATION round — item 16, an owner design round that
GATES the fleet's 12+13 pushes: every fork ports 16 alongside 12+13
before its push. One registry, two surfaces, the app's own docs in
between: sections from frontmatter against a fork-owned CATEGORY_ORDER;
the network as the top bar's Other Apps menu from lib/network_directory;
Resources from one constant; Admin owner-only; /changelog; a footer; a
generated /api page; a11y names; the no-`dcc` rule. Nothing rides the
block THIS round — navbar.py/header.py are divergent on every fork today
— and the item says which files become cargo next round.)
(1.6.40 is item 17 — two fleet-class findings from muischeduler's
item-12 port: the network battery's default UA is crawler-lane at
dimll ≥ 2.8 (fixed: browser engine token first, internal token after),
and a fork-local og:image augmentation the template does not carry.
Plus wording notes on items 9, 12, 13 and 15 from the first fork
reports — no runtime change beyond the one constant.)

Floor statement, per the authoring rule: **moved** — `LLMS_PKG_FLOOR`
is `(2, 8, 0)` from 1.6.34 (item 12). The rationale ladders retain
every older rung by design; do not read those as the floor.

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
# PARSER SUPPORT (was a SEQUENCING blocker until 1.6.31, and had
# been satisfied for two rounds while this note still said
# otherwise): the ops seat's scripts/fanout.py implements all three
# gate forms as of 2026-08-26 — `# requires-contract:`, the
# per-file `# requires:`, the `gated-skip` disposition and the
# `gated_skips` summary field, with five tests pinning the forms,
# the malformed-gate refusal, and per-file skip vs block gate. The
# forks=all dry run (32991971564) and both live rounds (33000661276,
# 33015477174) ran on that parser. A spec may use all three freely.
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
# (1.6.34 adds item 12's two cargo tests. Both were asked the README's
# questions — "who stubs this?" and "what does it import?" — before
# landing here: test_analytics_classifier.py imports AnalyticsTracker
# and lib.constants.INTERNAL_UA_TOKEN, two names every fork has had
# since the internal-traffic contract, and calls the tracker's public
# methods by the names forks already call them; test_traffic_rollup_v4.py
# imports daily_rollup / load_reads / vendor_rows from lib/traffic_rollup
# and the package's _ledger — nothing under lib/auth, no conftest
# fixture, no page. (1.6.41, note 61 — leaflet: `vendor_class` never
# reaches the ledger on 2.8.0 because EVENT_FIELDS lacks it and
# record_read stores EVENT_FIELDS only, so every host's rollup sends
# `class: null`; the v4 test now builds its rows THROUGH record_read and
# pins the seam — dimll 2.9.2 adds the field.) (1.6.41: the floor constant is spelled
# `LLMS_PKG_FLOOR` here and `_DIMLL_FLOOR` on emojimart — grep the
# ASSIGNMENT SHAPE `= (2, 8, 0)` / `>=2.8.0`, not one name.) CORRECTED
# 1.6.36: "imports nothing fork-shaped" was
# the wrong question — the real one is "does it pass against the
# OLDEST fork's rollup?", and at 1.6.34 it did not: the v4 test
# imported `load_agent_hits` and asserted `bot_visitors`, both v3 seams
# that clerkhook (v4 WITHOUT v3, its DIVERGENCES §9) lacks. Grep of the
# 12 local fork clones for `bot_visitors` in lib/traffic_rollup.py,
# 2026-08-29: clerkhook is the ONLY pre-v3 fork (its docstring says
# "THIS ROLLUP IS PRE-v3"); the other 11 carry v3. The test is now
# v3-agnostic (v4 keys only, `daily_rollup(app, day)` with the ledger
# path in the env) and the template's suite runs it against a
# clerkhook-shaped fixture (tests/fixtures/rollup_pre_v3.py, via
# tests/test_rollup_v4_is_v3_agnostic.py) so it cannot regress into
# v3 again. ALSO: a fork whose tests/ root is a PACKAGE suite
# (clerkhook) DECLINES both cargo tests with `# declined:` (item 14)
# and keeps its site copies under tests/site/. EXPECT BOTH RED on a
# fork that has not yet applied item 12 — that red IS the detect
# firing, exactly as item 3's test was
# — and apply the item in the same change; do not skip them. The other
# two 1.6.34 tests (test_read_ledger.py, test_traffic_page.py) drive the
# real app through conftest and compare against pages/control_board.py,
# which lockdown forks shape differently: contract, not cargo.)
- .claude/skills/wire-verify/SKILL.md
- .claude/skills/sync-template/SKILL.md
- .claude/skills/report/SKILL.md
- tests/test_claude_kit.py
- .github/dependabot.yml
- tests/test_auth_demos.py  # requires: lib/auth_demos.py
- tests/test_analytics_classifier.py  # requires: lib/analytics_tracker.py
- tests/test_traffic_rollup_v4.py  # requires: lib/traffic_rollup.py
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
  TOUCH.
  DIFF, DO NOT COPY (1.6.31 — this replaces "byte-copying the
  template's current file remains the recommended port", which three
  forks contradicted independently in one round, with two different
  failure modes). Diff your copy against the template's and port what
  is MISSING; your own blocks stay. A copy is safe in exactly one
  case: the diff is empty in both directions, where copy and port are
  the same act. The premise the old sentence rested on — "the bytes
  are fork-invariant, only the INTERFACE is fork-owned" — is false on
  at least three hosts: flexlayout's copy carries six check blocks the
  template's has never had (healthz build / app identity / geo
  diagnostic, the browser-lane prerender block, /api/agent-key closed
  to anonymous, machine surfaces stay open), each added for a defect
  measured on that host; leaflet's lines 192–230 assert its
  open-training posture (its divergence 4). A byte copy deletes those
  and CD STAYS GREEN — a deleted check does not fail, it stops being
  true and says nothing. muischeduler is the same class from the other
  side and louder: the template's copy asserts
  `ClaudeBot -> Disallow: /` while that host runs
  `block_ai_training=False` deliberately, so the byte-identical file
  FAILS on a correctly-configured site.
  The tolerant wake() (1.6.29; pinned by
  test_wake_survives_a_legacy_fetch_stub upstream) still earns its
  keep — state what it buys and no more: it degrades a stale-stub
  landing from a suite-wide TypeError into the fork's old red checks.
  It does not make a copy safe. The stub update is still the port's
  second half, not optional.
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
  THE FENCE IS THE DURABLE PROTECTION, AND IT IS NOT BEING WRITTEN
  (1.6.31). Class protects this file only while it stays
  contract-class; the byte-owned fence in your DIVERGENCES.md
  protects it across the next reclass, which is the one nobody will
  remember. Measured by the ops seat across eleven public forks'
  DIVERGENCES.md, 2026-08-27: flexlayout, flows and muischeduler
  fence scripts/smoke_live.py; LEAFLET DOES NOT, while reporting
  exactly the same fork-owned content. Nothing is at risk today —
  the item is contract-class and the fan-out no longer carries the
  path. The rule: if you ported rather than copied because your copy
  has fork-owned content, that path goes in the byte-owned fence in
  the SAME touch. The fence's grammar is documented in
  sync/README.md from 1.6.31 (it never was before; flows had to read
  it off the kit test).

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
notes: THE TEMPLATE'S OWN ADOPTION LANDED IN 1.6.31 —
  tests/test_gate_configured.py is the reference shape; adapt it,
  do not copy it (it imports lib.access, lib.auth, lib.gate_layouts
  and lib.page_visibility, all fork-owned). It was `open` here for
  three releases while four forks (leaflet, excalidraw, modelviewer,
  muischeduler) reported it `open` for the same reason and correctly
  declined to invent a shape — the template owed this one, and an
  item whose own author has not adopted it cannot close anywhere.
  What the reference does, in this tree's terms: conftest.py blanks
  every Clerk secret before any import and STAYS THAT WAY (every
  fail-closed assertion in test_access.py depends on it), so the
  test sets three FAKE non-empty `CLERK_*` values with monkeypatch
  at call time — `clerk_enabled()` reads the environment per call,
  so no second fixture and no change to conftest was needed. It then
  pins a real registered page to `auth` through the control board's
  own writer, renders the page's actual registered layout, and
  asserts the sign-in card's ids — READ OFF lib/gate_layouts by
  rendering its own card, never re-typed — are present. Its second
  test is the non-vacuity control: same page, same tier, zero-secret,
  renders the CONTENT (the documented fall-open), so the first test
  cannot pass by accident of the tier override. Its third pins the
  direction that must not depend on a credential existing: `admin`
  stays closed in both postures. A fork whose gate is a lockdown page
  rather than a card ports the three questions, not the ids.

### 8. The two heads declare the same identity (1.6.30; measured by emojimart)
class: contract
files: templates/index.html (the BROWSER head), run.py's
  `configure_seo(icons=..., ...)` (the CRAWLER head), the pin —
  tests/test_seo_icons.py — AND tests/test_social_card.py (1.6.31),
  where the fork's "no static duplicate of a Dash-emitted meta" sweep
  lives: adding the static `name="twitter:card"` this item requires
  trips that sweep, so the file is in this item's scope whether or not
  you touch it deliberately. Contract, not cargo, and by the mirror
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
  HEADLESS SCREENSHOTS (1.6.36): from dimll 2.9.0 a HeadlessChrome /
  Playwright / Puppeteer UA is crawler-lane, so a host that renders
  its OWN social card by screenshotting itself gets the crawler
  document unless the screenshot service sends a non-headless UA —
  the kit trap names it; check it before blaming the head parity.
  EXPECT ONE RED IN tests/test_social_card.py, AND THAT RED IS THIS
  ITEM WORKING (1.6.31; pannellum and modelviewer landed it
  independently, same as 1.6.26's DEMOS red). The static
  `name="twitter:card"` you add beside Dash's `property=` tag is a
  deliberate duplicate; your no-static-duplicate sweep will flag it.
  Fix it by writing the EXEMPTION into that test — `twitter:card`
  exempt, and both forms pinned at exactly one occurrence each — not
  by deleting the tag you just added. A session that reads `files:`
  as the scope statement and finds an unannounced red does the
  cheapest thing, which is revert; that is why the file is named in
  `files:` now. `files:` IS a scope statement, and one that omits a
  file the body requires teaches sessions to distrust it.

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
  branches on); since 1.6.35 `deploy` (`release-branch`, item 13) and
  since 1.6.36 `unknown_ai` (`allow` | `meter` | `block` — the host's
  `default_unknown_ai`; dimll 2.9.0 widened "block" to absent and
  unrecognised UAs, item 14). FROM MEASUREMENT, NOT FROM INTENT: nothing but a
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

### 10. /healthz declares the fleet's SHAPE, not just its build (1.6.31; seat-measured)
class: contract
files: the fork's healthz builder (lib/health.py, or wherever run.py
  assembles the payload) + a new tests/test_healthz_shape.py. The
  template's is the reference shape and is NOT cargo — it calls into
  lib/health.py, a fork-owned module, which is the mirror rule.
detect: `GET /healthz` and compare KEYS, not values, against the
  fleet set — {app, backend, build, dash_version, geo, ok, python}.
  Extra keys are a fork's business and always fine (flexlayout's
  `version`, the reporting block). A MISSING key is the item; a
  RENAMED key is the failure mode this item exists for, because it
  is invisible to every check that reads the value rather than the
  key. `build` is the one environment-dependent member: it comes
  from RENDER_GIT_COMMIT, so offline it is absent legitimately —
  test it by SETTING the variable and asserting the key appears.
contract: the hub's hourly sweep, the F4 battery, cd.yml's
  build-match wait and scripts/network_smoke.py all read this
  payload BY KEY NAME. A fork may ADD; it may not rename or omit. A
  genuinely absent capability is RECORDED, not silent — clerkhook
  has no geo layer and that is a divergence with a name (the
  `healthz: minimal` posture key, item 9), not a missing field.
  Measured across all thirteen hosts by the ops seat, 2026-08-27,
  against the template's own key set:
    flows      missing backend, dash_version — it renamed
               `dash_version` to `dash` (extras: dash, reporting,
               version)
    clerkhook  missing backend, dash_version, geo, python
    llms       missing python
    the other ten complete, extras only.
  flows reported item 5 GREEN and it IS green — `python` is there —
  so nothing in the round could see this: the battery reads
  `dash_version`, a renamed key reads as absent, and 1.6.28's rule
  says absence is NOT-ADOPTED, never not-applicable. One fork in
  twelve silently answers a different document than the battery asks
  for, and every reader of it was correct.
acceptance: the shape test green in the fork's suite, AND the fork's
  live /healthz carrying all seven keys — pasted in the report. The
  offline test cannot see a typed response model or a proxy that
  strips a field, which is why the template's reference also fetches
  the route, not just the builder.
notes: remedies for the three reds — flows: rename `dash` back to
  `dash_version` and add `backend`; keep `dash` beside it if
  anything of yours reads it, an extra costs nothing and a substitute
  costs the fleet. clerkhook: item 5's `python` plus `backend` and
  `dash_version`; `geo` is its recorded lockdown divergence, so
  declare `healthz: minimal` in the posture fence and say so rather
  than leaving four keys missing. llms: the kit is not adopted there
  at all and its drop is open — this item arrives with that one.
  The template's reference test also pins the values shallowly (ok
  is True, backend echoes its argument, python is this interpreter)
  because seven correctly-named empty strings pass a key check and
  tell the fleet nothing.

  A HAND-DECLARED HEALTHZ IS ITS OWN FAILURE MODE (1.6.33). The reds
  are FOUR, not three: the hub (2plot.ai) carries six keys, missing
  `geo`, and it was never counted because the hub is not in the
  fan-out. Its cause is a shape any fork can be in: the hub declares
  `/healthz` by hand in `lib/asgi_routes.py` instead of building the
  payload with `lib/health.py`, so it drifts from the fleet shape
  silently — no test fails, no reader complains, the key is simply
  never added. AND its `geo` needs dash-improve-my-llms >= 2.7.0 while
  that host's floor is 2.6.1. Those are two different states and the
  distinction is the point: **a hand-declared healthz drifts, and a
  package floor can make a key IMPOSSIBLE rather than merely absent.**
  Establish which one you are in before recording either as a
  divergence — "we chose not to" and "our floor cannot" get different
  remedies, and only the first is a divergence at all.

  Red today per the ops seat, 2026-08-28: **flows** (`dash` for
  `dash_version`, no `backend`), **clerkhook** (three keys),
  **pipdocs** (`backend`), **hub** (`geo`, blocked on its own package
  floor). That list and the 2026-08-27 table above disagree on two
  rows — the table has `llms` missing `python` and no pipdocs row —
  and the drop that supplied it does not say whether llms was fixed or
  pipdocs newly measured. Trust the dated table for what it measured
  and re-measure both hosts before treating either as settled.

### 11. HEAD answers wherever GET answers (1.6.32; mechanism and population corrected 1.6.33)
class: conditional (predicate: the fork serves a non-Flask backend) +
  contract
files: wherever the fork registers ASGI middleware (template:
  lib/asgi_middleware.py + its one line in run.py) + a new
  tests/test_head_method.py + one check in EACH live tool
  (scripts/smoke_live.py, scripts/network_smoke.py). None of it is
  cargo: the test calls into the app run.py builds, and both tools
  have been contract-class since 1.6.29.
detect: `HEAD /healthz` and `HEAD /robots.txt` return the same status
  as their `GET`. On a Flask fork this passes for free and the item
  is `already-present` — run the detect anyway and PASTE it, because
  the answer is what records which lane this fork is on. Do not
  detect on `HEAD /` alone with a crawler UA: that one case succeeds
  on a fully broken host (see notes).
contract: HTTP requires HEAD wherever GET is served. Werkzeug derives
  a HEAD rule from every GET rule, so Flask and Quart get it for
  free. **It is FastAPI, not Starlette** (corrected at 1.6.33; 1.6.32
  said Starlette and was wrong, as did the drop that produced it, as
  did three separate probes): `starlette.routing.Route.__init__` ends
  with `if "GET" in self.methods: self.methods.add("HEAD")` — a plain
  Starlette route extends the same courtesy Werkzeug does.
  **`fastapi.routing.APIRoute` takes `methods` literally and adds
  nothing**, so `@router.get(...)`, `add_api_route(...)` and every
  other FastAPI declaration answers 405 to HEAD. Get the layer right
  before you look for the fix: a fork that reads "Starlette does not
  derive HEAD" will search the wrong package, and will conclude a
  bare-Starlette mount is affected when it is not. A fork that chose
  the ASGI lane inherited a 405 on
  every route and cannot see it from any surface the contract reads:
  CI never issues a HEAD, both live tools GET, and a browser never
  sends HEAD for a document. What must be true afterwards is the
  BEHAVIOUR — same status, same `Link` and `content-type`, empty
  body — not any particular mechanism.
acceptance: the per-backend pin green in the fork's suite, and
  `HEAD /healthz` == `GET /healthz` on the fork's live host, pasted.
  The pin must FAIL on the ASGI leg with the fix removed and PASS on
  the Flask leg — show both. A pin that is green on all backends
  before the fix is testing the test client, not the router, which is
  the exact trap that hid this defect for the whole life of the ASGI
  lane.
notes: THE POPULATION IS EVERY ASGI HOST IN THE NETWORK, and it is
  seven, not the two this item named at 1.6.32. Measured on the wire
  by the ops seat, 2026-08-27/28, across every host that seat can
  reach:

    fleet, reached by this fan-out       pannellum, muischeduler
    hub, reached by its own drop         2plot.ai — HAD the defect,
                                         already fixed
    second ring, reached by NEITHER      piratesbargain.com,
                                         ai-agent.buzz, 2plot.xyz,
                                         cast.2plot.net
    Flask hosts (ten) + 2plot.media      200 already, no action

  Two of those rows correct the drop's own earlier text: the hub was
  never in this item's population and had the defect anyway, and
  `cast` is a fourth second-ring host that the hub seat had no reason
  to check. The second ring is NOT in the fan-out and this item will
  never reach it mechanically — it is named here as **known-affected,
  reached by a drop rather than by the spec**, because notes that stop
  at the fan-out's edge read as "these two hosts" when the truth is
  "every ASGI host, and we know which."

  The single exception, `HEAD /` with a crawler UA answering 200, is the
  package's prerender middleware replying before the request reaches
  the router at all — a session that probes only that case will
  conclude the host is fine. (It is also how the template's own
  1.6.31 in-process probe cleared the app code: it ran HEAD against
  `/`, the one route that worked.)

  MIDDLEWARE, NOT THE DECLARATIONS, and the reason is measurable in
  your own tree: `methods=["GET", "HEAD"]` on the routes you declare
  fixes `/healthz` and `/api/*` and nothing else. `/llms.txt`,
  `/<page>/llms.txt`, `/robots.txt`, `/sitemap.xml` and the policy
  panel are registered GET-only by dash-improve-my-llms' own FastAPI
  adapter (`_fastapi_adapter.py`, 2.7.1 — only the root icon paths
  declare HEAD), and `/` by Dash's page catch-all. A declarations-only
  fix leaves three of the four crawler-facing surfaces 405ing. The
  template's shape: a pure-ASGI middleware, added LAST so Starlette
  runs it outermost, that re-dispatches the scope as GET and sends
  one empty final body message. Pure ASGI rather than
  `BaseHTTPMiddleware` so it neither buffers nor breaks streaming.

  QUART NEEDS NOTHING, and this was measured, not assumed: all five
  core routes answer HEAD 200 in-process on Quart, whose routing is
  Werkzeug-descended. Its test client hands back the full body where
  Werkzeug's and Starlette's strip it — that is the client, not the
  app: h11, under uvicorn and hypercorn both, frames a HEAD response
  as content-length 0 and never writes those bytes
  (`h11/_connection.py::_body_framing`). So the template's pin
  asserts the empty body on the two backends where a layer under test
  performs the strip, and says why on the third rather than asserting
  loosely. Read this item's "empty body" as **the wire is empty**,
  never as "your adapter empties it": Werkzeug's response object,
  httpx's ASGI transport and h11 under both servers each drop it, and
  h11 raises if a server forwards one. The package seat declined to
  assert emptiness in its own adapters for exactly that reason and was
  right; status + content-type parity, never-405, and
  empty-or-identical is the assertable shape when you are not the
  layer doing the stripping.

  THE LIVE-TOOL CHECK COSTS A KEYWORD (1.6.29's hazard, again). Both
  tools now need `HEAD`, and `scripts/smoke_live.py`'s `fetch` had no
  `method` parameter. Adding one is the wake() failure verbatim: the
  template's own tests/test_smoke_live.py stubs `fetch` with a fixed
  signature in TWELVE places and every one of them had to grow
  `method` in the same commit. Yours will too — and
  tests/test_network_smoke.py's stub asserted `method == "GET"`
  outright, which now names the one path allowed to differ instead of
  dropping the guard. Port the check and the stubs together or the
  suite goes red on a keyword rather than on a defect.

  This does NOT weaken "probe with GET, never HEAD" (kit trap, and it
  stands). That rule is about how a session READS a site: HEAD tells
  you about the router's method table and never about the document —
  which is exactly what this item measures. The rule exists because
  of this defect; the check is the defect's own detector.

  THE MIDDLEWARE IS THE FLOOR AND STAYS AFTER THE PACKAGE FIX. The
  package's FastAPI adapter declared its routes GET-only; that is
  fixed in dash-improve-my-llms 2.7.2 (`DOC_ROUTE_METHODS =
  ["GET", "HEAD"]` across all three adapters), so when the fleet floor
  reaches 2.7.2 the package's seven doc routes stop needing help. **Do
  not remove the middleware when that lands.** It covers routes
  neither the fork nor the package declares, and this tree measured
  which, rather than assuming (1.6.33, in-process on fastapi, the
  middleware removed):

    HEAD /            browser UA   405   ← Dash's page catch-all
    HEAD /            crawler UA   200   ← the prerender, not the router
    HEAD /healthz, /llms.txt, /robots.txt, /sitemap.xml    405
    → 10 of the 11 pins red; the 1 green is the crawler `/` shadow

  `/` is served by Dash itself, and every Dash route is an `APIRoute`:
  `dash/backends/_fastapi.py::add_url_rule` calls
  `server.add_api_route(..., methods=methods or ["GET"])`, and the
  page catch-all is registered `methods=["GET"]` at line 345. That
  covers `/`, `/_dash-layout`, `/_dash-dependencies`, `/_reload-hash`
  and the asset routes — nothing in the fork or in
  dash-improve-my-llms can declare methods on any of them, and a fork
  that later declares its own route GET-only is covered too. The
  package fix removes one reason for the middleware; it does not
  replace it.

  UPSTREAM, not in scope for a fork: Dash's FastAPI backend should add
  HEAD alongside GET the way its Flask and Quart backends get it from
  Werkzeug — a one-line change in `add_url_rule`. Owner / upstream
  item; until then the middleware is the only thing standing in front
  of Dash's own routes.

### 12. The ledger row — one classifier, the read table, rollup v4, /admin/traffic (1.6.34)
class: contract (floor + four seams ported into the fork's shape) +
  two cargo tests in the block (see the fence note). Contract rather
  than verbatim because every file the item touches answers the
  README's questions the wrong way for a byte-copy:
  `lib/analytics_tracker.py` — forks' own tests call `is_bot` /
  `detect_bot_type` (the names and signatures are KEPT for exactly
  that reason; the bodies delegate); `lib/traffic_rollup.py` — several
  forks' tests/test_satellite_reporter.py stub `daily_rollup` and a
  byte-copy would change what the stub is stubbing; `pages/traffic.py`
  calls into `lib.auth` (`is_admin_user`, `admin_access_open`) and
  `lib.gate_layouts`, which the lockdown forks (clerkhook) shape
  differently; `run.py` is fork-divergent by definition.
files: requirements.txt (the dimll line, all four encodings) ·
  run.py (`LLMS_PKG_FLOOR`, the `on_document_read` registration next
  to `add_llms_routes`) · lib/analytics_tracker.py · lib/traffic_rollup.py
  · pages/traffic.py (new) · .claude/CLAUDE.md (the ONE-classifier
  trap, rides the kit) · tests: test_analytics_classifier.py and
  test_traffic_rollup_v4.py (block), test_read_ledger.py and
  test_traffic_page.py (port into the fork's fixtures).
detect: `grep -c "'claudebot'" lib/analytics_tracker.py` ≠ 0 ⇒ not
  adopted (the old search list named it). Also:
  `grep -c on_document_read run.py` = 0 ⇒ the row is not kept;
  `python -c "import lib.traffic_rollup as t; t.load_reads"` fails ⇒
  no v4; `LLMS_PKG_FLOOR < (2, 8, 0)` ⇒ the floor did not move. Run all
  four and PASTE them: a fork can be at any subset.
contract:
  (a) FLOOR ≥ 2.8.0 in every encoding (requirements, run.py's boot
      floor, any test that names it, CI if it pins — and CI may pin
      the floor MORE THAN ONCE: grep for the number, not for one
      line; 1.6.40 note from the first fork ports). The requirements
      line changing is the cache bust — grep the number, move every
      one (kit trap). Do NOT wait for 2.8.1: `policy` is None on every
      event until it ships and the rollup groups None as "default".
  (b) ONE CLASSIFIER. `is_bot(ua)` ⇔ `classify(ua)["lane"] == "crawler"`;
      `detect_bot_type(ua)` ⇔ `classify(ua)["bot_type"] or "unknown"`.
      `track_visit` classifies ONCE, after the real client IP is
      resolved (so `verified` is against the client, not the proxy),
      and crawler rows gain `vendor_key`, `vendor_class`, `verified`,
      `lane`; human rows are byte-identical to before (the fork's
      existing v3 rollup tests must pass unmodified). The
      `INTERNAL_UA_TOKEN` drop stays FIRST, before classification.
      The module ends with ZERO User-Agent strings. A token the old
      list carried that the registry lacks and that matters for the
      fork's accounting (`headlesschrome`, `phantomjs`, uptime
      monitors) is a PUSHBACK to the package seat named in the report,
      never a list kept in the fork. An absent UA is a bot now (the
      package puts the empty UA on the crawler lane); it used to be a
      desktop human.
  (c) THE ROW. `on_document_read(tracker.record_read)` registered
      once, idempotently (the suite imports run.py more than once and
      the hook appends), next to `add_llms_routes`. `record_read`
      keeps every `_ledger.EVENT_FIELDS` key verbatim plus
      `"kind": "read"` in a `reads` list in the SAME analytics file —
      same buffer, lock, flush cadence and retention as `visits` —
      dropping `client_ip` unless `ANALYTICS_KEEP_CLIENT_IP=1`. A
      ledger without a `reads` key reads as empty. NO double count:
      `reads` is a second table joined by the rollup, never summed
      into `human_hits` / `bot_hits` / `pages`.
  (d) ROLLUP v4, additive, present ONLY on a day with reads:
      `vendors: [{key, class, verified, policy, hits, bytes,
      tiers:{small,index,full,page,html,policy,sitemap}}]` — one row
      per `(key, verified, policy)`, null key KEPT (the unverifiable
      bulk), sorted by hits desc, capped at 40, `tiers` from the
      package's `TIERS` tuple with all seven keys always; and
      `reads: int` = `sum(vendors[].hits)`. Every v3 key byte-identical.
      A reads-only day is reported (the machine-only-day rule). The
      reporter changes nothing: it POSTs what `daily_rollup` returns,
      and the hub ignores keys it does not know (seat-read at 54bfa5a).
      THESE KEYS ARE THE HUB CONTRACT (round 3.3) — do not rename them
      in a port without saying why in the report.
  (e) `/admin/traffic`: the control board's exact gate (same
      redirect/deny branches, `mark_hidden` at import), reads the
      analytics file directly, last 14 days: vendor × day (hits, with
      a bytes column), vendor → tier for the picked day, top paths per
      vendor (10 per vendor, top 8), the v3 headline numbers for the
      same day, and one line saying what `verified` means per vendor
      (`n/a` = the operator publishes no ranges — Anthropic does not,
      so ClaudeBot is ALWAYS n/a; say it on the page or the owner reads
      it as a defect). Plain tables, NO charts, no interval callback,
      the day dropdown is the only control (fleet fact 18: a 14 × 40
      table of strings is ~1 ms; five charts were ten seconds).
acceptance: the fork's suite green on ≥2.8.0 including the two cargo
  tests and the fork's ports of test_read_ledger.py / test_traffic_page.py
  (assert the NUMBERS in the fixture ledger, not "renders"); the four
  detects pasted at zero / present; and on the wire after deploy, a
  `GET /llms.txt` with a real vendor UA followed by the fork's own
  `/admin/traffic` showing that row (`ALLOW_UNGATED_ADMIN` is for local
  work only — never set it on a host).
notes: REPORTING CONSEQUENCE, say it in your CHANGELOG under Changed:
  `human_hits` DROPS and `bot_hits` RISES on adoption day, because
  UA-less and library clients (`httpx`, `Go-http-client`, `node-fetch`,
  an empty UA) move from human to crawler. That is the number becoming
  true, not a regression; the hub's day-over-day view will show the
  step. The FINDING behind (b), dated 2026-08-29: the tracker's search
  list named `claudebot` — Anthropic's TRAINING crawler, which the
  package's registry has said since 2.3.3 and the fork's own run.py
  comment says six lines from where the list ignored it — and still
  carried the retired `anthropic-ai` / `claude-web` tokens. Every host
  reported it. Two measured facts a port needs: in-process (test
  client, no client address) the package cannot verify GPTBot and says
  `n/a`; on the wire the same request is verified/unverified — pin the
  triple in the in-process test, not the pair. And the package emits
  for the crawler document only: a Chrome `GET /` writes no read row
  (measured on the 2.8.0 wheel). THE FLOOR BUMP BREAKS ONE VERBATIM
  TEST ON EVERY FLASK FORK: `tests/test_proxy_scheme.py::
  test_the_tag_dash_emits_follows_the_forwarded_scheme` (a "satellites
  copy this verbatim" file) sends NO User-Agent, and at ≥2.8.0 an
  absent UA is the crawler lane — it receives the crawler document,
  which has no `twitter:url`, and fails on "no tag" without saying
  anything about the scheme. The template's release commit went red
  in CD on all four Flask legs for exactly this (run 33256965081,
  2026-08-29; FastAPI/Quart skip the test). Port the fix WITH the
  floor: the request sends `BROWSER_UA` from conftest (template
  acc3651). Either lane can be the one you did not mean to test. Round 3.3 (the hub fold) and 3.4 (the
  posture flip) are NOT this item; the template's posture fence in
  DIVERGENCES.md is unchanged (`/` still 403 to training UAs).

### 13. Render deploys `release`; only CD writes `release` (1.6.35)
class: contract. cd.yml is fork-UNIFORM on the hook step (11 of 12
  local fork checkouts carry it verbatim; dash-hook-my-ai has its own
  pipeline with no hook step) but NOT byte-uniform: every copy differs
  from the template's in the host string, the wait's timeout sizing and
  comments (41–258 differing lines per fork, measured 2026-08-29), so a
  byte-copy would overwrite a fork's own tuning. Port the CONTRACT.
files: .github/workflows/cd.yml (job `deploy`: hook step → "Promote to
  release", job-level `permissions: contents: write`, header comment) ·
  render.yaml (`branch: release` + two-line comment) · DIVERGENCES.md
  posture fence (`deploy: release-branch`) · .claude/CLAUDE.md (the
  build==HEAD-of-release trap; rides the kit) · tests/test_claude_kit.py
  (`_POSTURE_KEYS` gains `deploy`) · a port of
  tests/test_cd_promotes_release.py (parses cd.yml + render.yaml with
  PyYAML, which python-frontmatter already pulls in).
detect: `grep -c RENDER_DEPLOY_HOOK_URL .github/workflows/cd.yml` ≠ 0
  ⇒ not adopted. Also `grep -c "branch: release" render.yaml` = 0 ⇒
  Render still watches main. Paste both.
contract:
  (1.6.40 note: forks on the 1.6.33 block hit a one-hunk conflict in
  tests/test_claude_kit.py when porting this item — take the NEWER
  bytes, the template's; the hunk is the posture-key allowlist.)
  OWNER STEP BEFORE THE FIRST PUSH (1.6.41; muischeduler's first
  promote, run 33318542986, FAILED at `git push origin
  HEAD:refs/heads/release` with the whole matrix green): the repo's
  Actions default workflow permission is READ-ONLY (GitHub's default
  since Feb 2023) and it CAPS the job-level `contents: write` — the
  template's repo already allowed write, which a template cannot see
  in itself. Settings → Actions → General → Workflow permissions →
  "Read and write permissions". DETECT, where a token exists:
  `gh api repos/<owner>/<repo>/actions/permissions/workflow` →
  `default_workflow_permissions == "write"`; without a token the first
  promote IS the detect, and its failure is SAFE — nothing deploys by
  CD and `verify` correctly SKIPS (that skip is contract (a2) working,
  measured on the same run). REMEDY after a failure: the setting, then
  "Re-run failed jobs" — never a PAT, never a force push, never writing
  `release` by hand.
  (a) cd.yml `deploy` keeps `needs: [test]` — that IS the gate — and
      replaces the hook step with `git push origin HEAD:refs/heads/release`
      after an `actions/checkout` **with `fetch-depth: 0`** — MEASURED on
      the template's second promote (run 33262495272, 747d8b3,
      2026-08-29): a depth-1 clone pushing HEAD onto an EXISTING
      `release` is rejected as non-fast-forward ("fetch first"), because
      a shallow history cannot show the remote that release's tip is an
      ancestor; the FIRST promote passes regardless because it creates
      the branch, so a fork will not see this until its second push.
      Reproduced locally: depth-1 rejected, `--unshallow` lands. The
      push is the run's own sha, fast-forward, NOT
      forced (a non-fast-forward means someone wrote `release` by hand
      and the job must FAIL and say so). Job-level
      `permissions: contents: write` on `deploy` only; the workflow
      stays `contents: read`. Guard the step with
      `if: github.event_name == 'push' || inputs.target_url == ''` so a
      verify-only dispatch against another host never moves the ref
      (the hook step never had this guard — the drop assumed one; the
      tree had none). GITHUB_TOKEN pushes trigger no workflows, which
      is correct: `on:` is main-only and Render, not Actions, reacts
      to `release`. On the first run `release` does not exist and the
      push creates it. The build-match wait is unchanged. Delete every
      trace of the hook secret's NAME from the file (the detect greps
      for it — say "the deploy-hook secret", not its name, in prose).
  (b) render.yaml `branch: release`; autoDeploy stays unset/on — it is
      the mechanism.
  (a2) `verify` runs ONLY on `needs.deploy.result == 'success'` — the
      template's old `always() && != 'cancelled' && != 'skipped'`
      admitted `failure`, so on that same failed promote `verify` ran
      and reported GREEN against the PREVIOUS build (ops finding). And
      verify's first step asserts `/healthz build == github.sha` itself
      (exit 1 otherwise; skipped only on a dispatch against another
      host) — the stronger form catches a promote that succeeded while
      the platform build did not, or a later run promoting past this
      one. A verify that passes when nothing deployed must not exist.
  (c) DIVERGENCES.md posture fence gains `deploy: release-branch`
      (absent reads as main); the kit trap says `build == HEAD` means
      HEAD of `release` and `main` ahead of `release` is an uncertified
      push pending, never drift, never a hand deploy.
acceptance: one green run on main whose `deploy` job ends with
  `origin/release` == the run's sha, `/healthz build` == that sha (the
  existing wait proves it), `verify` green; the structural pins green
  (needs contains test; promote step present and unforced; checkout
  fetch-depth == 0; hook name absent; deploy.permissions.contents ==
  write; workflow-level read; verify `if` == deploy success and carries
  the sha step; render branch == release; posture fence declares it).
  Then a SECOND push — the first only creates the branch. Paste
  `git rev-parse origin/release` next to the healthz build.
notes: OWNER STEP PER FORK, listed, not done by the session: if the
  Render service is NOT Blueprint-managed, render.yaml's `branch:` is
  documentation and the dashboard's Branch field is the switch. The
  first promoted run cannot tell the two apart from the wire — main
  and release hold the same sha, so autoDeploy-from-main and
  autoDeploy-from-release produce the same /healthz. The discriminating
  observation is the NEXT push that goes red on main: `release` must
  not move and the wire must not change. Report which the host was.
  (A `branch` field on /healthz from RENDER_GIT_BRANCH would make it
  one read; that is a runtime change and not this item — proposed to
  the ops seat as a follow-up.) For the hub seat: the F4 battery's
  "HEAD has a green CD run" row compares to `release` after adoption.

### 14. What the first wire round taught the block — `# declined:`, `unknown_ai`, dead cargo (1.6.36)
class: contract (spec grammar + the byte-verbatim kit test, which
  rides the block already; DIVERGENCES.md is fork-owned; no runtime
  code).
files: tests/test_claude_kit.py (block — `_machine_fence` accepts
  `# declined: <reason>`; `_POSTURE_KEYS`/`_POSTURE_ENUMS` gain
  `unknown_ai`) · DIVERGENCES.md (yours: the byte-owned fence's
  declined entries where they apply; the posture fence's
  `unknown_ai:`) · .claude/CLAUDE.md (the headless-browser trap, rides
  the kit) · sync/README.md is template-only.
detect: `grep -c "declined:" tests/test_claude_kit.py` = 0 ⇒ the kit
  test predates the grammar (the block delivers it). For the fork's
  OWN state: any cargo test at a path the fork's suite cannot host,
  or any cargo file whose posture the fork's DIVERGENCES inverts,
  present without a `# declined:` entry ⇒ dead cargo.
contract:
  (a) THE DECLINED ENTRY. `- <path>  # declined: <reason>` in the
      byte-owned fence means the fork refuses this cargo (holds an
      equivalent elsewhere, or its posture inverts it). It is the only
      fence entry that may name a path absent at HEAD; the reason is
      mandatory; a spec's sync-verbatim block cannot carry one. The
      fan-out already skips every path DIVERGENCES names
      (scripts/fanout.py `divergence_names`) — the ops seat adds the
      declined-entry test THERE; this item only frees the kit test to
      allow it.
  (b) DEAD CARGO. When your DIVERGENCES records an inversion of a
      cargo file's posture, decline the file AND delete the dead copy
      in the same touch. Instance, clerkhook (session action, NOT done
      here): `scripts/smoke_live.py` — 611 lines, referenced by
      nothing but its own DIVERGENCES §6 and tests/site/
      test_smoke_source.py's contrast, asserting content IS served on
      a host that denies every surface — delete it, decline it. And
      its site tests live under tests/site/ (already true for
      test_analytics_classifier.py, test_read_ledger.py,
      test_traffic_page.py at 2026-08-29): decline the two item-12
      cargo tests at tests/ root with the reason "package suite at
      tests/, site copy at tests/site/".
  (c) `unknown_ai: allow | meter | block` in the posture fence — your
      `default_unknown_ai`, what an unrecognised or absent UA gets on
      the corpus. Absent reads as `allow`. dimll 2.9.0 is NOT required
      for the key (the floor stays 2.8.0); it is what made the value
      observable, since 2.9.0 widened "block" to those UAs.
  (d) Headless browsers are crawler-lane at 2.9.0 (kit trap): a host
      that screenshots itself for cards needs its screenshot service
      to send a non-headless UA, or it cards the crawler document.
acceptance: the kit test at this release green (declined grammar
  cases pass; `unknown_ai` validates); every declined entry's reason
  names a DIVERGENCES section or an equivalent path; no cargo test at
  a path the fork's suite cannot host; the dead-cargo instance closed
  on clerkhook with a diff. Nothing on the wire changes.
notes: THE FIXTURE IS THE PROOF for item 12's cargo: the template's
  suite now runs tests/test_traffic_rollup_v4.py against
  tests/fixtures/rollup_pre_v3.py (clerkhook's shape — no
  `load_agent_hits`, no `bot_visitors`, `daily_rollup(app, day,
  visits=None, reads=None)`) via a subprocess pytest with
  `ROLLUP_V4_MODULE` set, and it is green; a future edit that reaches
  for a v3 seam goes red HERE, not on the oldest fork. ONE SESSION PER
  TREE (README authoring rule): a sub-agent must not edit files its
  parent also edits, and the completion signal is the report, never
  an idle notice — two forks lost time to each in the 1.6.35 round.

### 15. The posture flip — training crawlers allowed by default (1.6.37; Round 3.4)
class: contract (one flag in run.py + the tests and tools that
  fingerprinted the old posture + the fence). NOT verbatim: run.py is
  fork-divergent, and the two live tools are contract-class since
  1.6.29.
files: run.py (`RobotsConfig(block_ai_training=False, …)` and the
  comment block that says why) · tests/test_llms_routes.py (the
  robots fingerprint: ClaudeBot → `Allow: /`) · scripts/smoke_live.py
  and scripts/network_smoke.py (same tuple) · DIVERGENCES.md (the
  posture fence's `ai_bots`, re-measured and re-dated) · CHANGELOG.
detect: `grep -cE '^\s*block_ai_training=True' run.py` ≠ 0 ⇒ not
  flipped (1.6.41: anchored to the line start so a COMMENT documenting
  the flag a host did not take — muischeduler:381 — no longer fires).
  (1.6.40 note: item 9 — the posture fence — is UNADOPTED on several
  forks; it is a MEASUREMENT pass, never a copy of the template's
  numbers: probe your own host with both UAs and write what it answered.)
  Then the WIRE: ClaudeBot and GPTBot UAs × `/`, `/llms.txt`,
  `/healthz` — paste all six with the date.
contract: DEFAULT ALLOW. The owner's decision (2026-08-29): the wall
  decided by vendor CLASS what nobody could account for; since item 12
  every corpus read is a ledger row and the hub reconciles it against
  the wire (boilerplate 534 == 534), so a read is recorded and
  priceable and the tool is now per-vendor policy —
  `vendor_policy={"<key>": "block" | "meter"}` for ONE vendor whose
  rows justify it, never the class. `block_ai_training=False`;
  `allow_ai_search` / `allow_traditional` unchanged. robots.txt then
  carries `Allow: /` for GPTBot, ClaudeBot, CCBot, …, and the package
  middleware stops 403ing the browser document and /healthz for them.
  A FORK WHOSE POSTURE FENCE DECLARES `ai_bots` 403 BY DESIGN (clerkhook:
  a locked host) keeps `block_ai_training=True`, keeps its fingerprint
  lines on `Disallow`, and says so in DIVERGENCES.md — that is a
  recorded divergence, not drift, and this item is `not-applicable-
  because` there with the fence as evidence. Forks that ALREADY allow
  at the app level (leaflet, muischeduler — the ops seat's reading,
  2026-08-29) report `already-present` with their fence and the six
  wire lines.
  THE EDGE WALL IS UNOBSERVED (corrected the night of 2026-08-29, on
  the canary): the drop framed the template's 403 as two walls — the
  app's and a Cloudflare rule on `/` — and the flip alone produced
  200/200/200 on the wire with no Cloudflare edit; every 403 on
  boilerplate was the app's. The owner is checking whether any zone
  rule exists at all. So: ship the app half; measure BEFORE and AFTER;
  the app-level wire measurement is the acceptance. If YOUR host still
  403s `/` on the wire while in-process answers 200, THAT is an edge
  wall — name it, paste both, and hand it to the owner; do not "fix"
  the app again.
acceptance: in-process ClaudeBot + GPTBot on `/`, `/llms.txt`,
  `/healthz` → 200 (the crawler document on `/`); robots.txt carries
  no Disallow for them; the fork's suite green (the fingerprint line
  flipped, not deleted); on the wire, the six lines pasted and dated
  in the posture fence (200/200/200 for both UAs) — the app-level
  wire measurement alone, unless the host measures otherwise.
notes: in-process is the app's own answer; the wire minus in-process
  is whatever sits in front of it. (1.6.40 wording note: fingerprint
  tests that bypass conftest's `get()` wrapper via
  `app.server.test_client()` send NO User-Agent and land on the crawler
  lane at ≥2.8 — item 12's proxy-scheme hazard applies to every such
  test, not only test_proxy_scheme.py — and to ANY in-process probe that
  sends no UA: muicharts' scripts/route_parity.py probed every route
  UA-less and its CI gate reported `/admin/control-board: 404` at 2.8;
  grep test_client()/probe calls without headers.) On the canary the difference was
  ZERO: `/` and `/healthz` both 403ed from the APP (in-process at
  ecc66f8: 403 with the 318-byte denial body) and both opened with
  the flag. The robots.txt shape after the flip is NO training stanza
  at all (GPTBot/ClaudeBot fall under `User-agent: *` / Allow), so a
  fingerprint that looks the stanza up raises — assert "no Disallow",
  not "Allow: /" (the template's three sites do).

### 16. Navigation from one registry; the app's identity from frontmatter (1.6.38; owner design round — GATES the 12+13 pushes)
class: contract THIS round. Every fork's navbar.py/header.py is
  hand-edited today (the survey of 2026-08-30: twelve different copies
  of the template's page_order/excluded_links/section literals), so a
  byte-copy would overwrite each fork's identity. After a fork carries
  the constants block, these files hold NO fork content and become
  cargo-eligible NEXT round: components/navbar.py, components/header.py,
  components/footer.py, pages/changelog.py, pages/api.py,
  lib/api_reference.py, tests/test_nav_contract.py, and
  tests/test_excluded_links_hidden.py (rewritten). Say in your report
  whether your copies are byte-identical to the template's at 1.6.38
  once ported — that is the evidence the reclass needs.
files: lib/constants.py (GITHUB_URL + SAME_AS=[GITHUB_URL], CATEGORY_ORDER,
  DISCORD_URL/YOUTUBE_URL/YOUTUBE_SUBSCRIBE_URL/DMC_URL, UPSTREAM,
  API_PACKAGES, resources()) · lib/network_directory.py (ICONS table +
  other_apps_for()) · components/navbar.py (sections_for, admin
  callback, search_data; page_order and excluded_links DELETED) ·
  components/header.py (Other Apps menu, GitHub → GITHUB_URL, Burger
  aria-label, version badge, search from navbar.search_data) ·
  components/footer.py + appshell (AppShellFooter) · pages/changelog.py ·
  pages/api.py + lib/api_reference.py · pages/home.py (markdown2dash,
  not dcc.Markdown) · lib/directives/headings.py (inline-image renderer)
  · lib/directives/source.py (copyLabel/copiedLabel) · pages/markdown.py
  (Meta.order) · pages/traffic.py (DatePickerInput + People) · every
  docs page's frontmatter (`category:`, `order:`) · tests.
detect: `grep -cE "page_order|excluded_links|EXCLUDED_LINKS" components/navbar.py`
  ≠ 0 ⇒ not adopted (forks spell the list both ways — 1.6.41). Also
  `grep -c "dcc.Dropdown" pages/traffic.py` ≠ 0.
contract (the design's numbered list, DESIGN-navigation-uniformity §The
  contract; each is a pin in tests/test_nav_contract.py):
  (1) Sidebar: Home · Changelog → the app's sections from frontmatter
      `category:` + `order:` in CATEGORY_ORDER (unknown categories after,
      alphabetically; uncategorised pages in one trailing "Documentation"
      section — give every page a category instead) → API (only when
      API_PACKAGES is set) → Resources → Admin (owner-only). /admin/*
      never enters a section or search; neither does a hidden-tier page.
  (2) Top bar: Burger (aria-label) · wordmark · backend badge · OpenAPI
      badge (FastAPI) · version badge (API_PACKAGES[0]'s version, when
      declared) · search (sidebar pages only) · Other Apps hover menu =
      the PRIMARY applications only (owner's review, 2026-08-30:
      2plot.ai, 2plot.dev, 2plot.media, piratesbargain.com,
      ai-agent.buzz — never the docs subdomains, which 2plot.dev's
      catalogue lists), from `network_directory.PRIMARY` (a URL set
      inside the registry, not a hand-typed menu) minus this host,
      labelled by DOMAIN, icons from
      network_directory.ICONS (keyed by URL — NOT a field on the entries:
      the package's register_network forwards every entry key and an
      unknown one is a TypeError at boot; measured on the template) ·
      GitHub icon → GITHUB_URL · theme toggle · avatar. The sidebar's
      network / "Pip Components" / "Other Apps I've built" sections are
      DELETED — the network is listed once, in the menu.
  (3) Footer: © {computed year} Pip Install Python LLC · GitHub PROFILE
      (GITHUB_PROFILE_URL — the repo link is the top bar's icon) ·
      Discord · YouTube (subscribe); NO Changelog link (the sidebar's is
      the single one); every icon labelled; no Terms/Privacy.
  (4) /changelog: pages/changelog.py — CHANGELOG.md as a Timeline, the
      file (minus its H1) as LLMS_DOC. Sidebar link under Home; footer.
  (5) Resources = lib.constants.resources(): THIRD-PARTY ONLY — `dmc`
      (labelled exactly that; it fits the sidebar) + UPSTREAM when
      declared. No GitHub, Discord or YouTube here (top bar + footer
      carry the owner's links), no community.plotly.com, no 2plot.dev.
      The kit test asserts the absence.
  (6) Admin: the pip-docs+ callback — `navbar-admin-{desktop,mobile}`
      filled only for is_admin_user() (or admin_access_open() locally);
      the startup tree carries no /admin/ href at all.
  (7) /api from API_PACKAGES via lib/api_reference (the package's
      metadata.json — Dash 4 generated classes carry no `_prop_names`;
      the docstring and metadata.json are what exist): one dmc.Table per
      exported component, prop · type · default · description; LLMS_DOC
      is the same tables as Markdown. Not registered when the list is
      empty.
  (8) a11y: every dmc.Burger/ActionIcon in components/ has aria-label;
      CodeHighlightTabs sets copyLabel/copiedLabel.
  (9) No `dcc.` in pages/ or components/ except Location, Store,
      Interval, Upload, Graph. Home renders through markdown2dash with
      patch_renderer() — which now also renders inline `![alt](src)`
      images (markdown2dash has no image renderer and mistune's fallback
      raises on DMC children; found converting home.py).
  (10) /admin/traffic: dmc.DatePickerInput (id `traffic-day`; min/max =
      the ledger's first/last day, presets Today / Yesterday / Last 7
      days (start), valueFormat YYYY-MM-DD) and a People section above
      the crawler ledger with the day's human_hits / visitors / sessions
      / median_session_s and the line "humans never enter the read
      ledger — the tables below are crawlers only".
  PER-FORK IDENTITY (the freedom): muischeduler keeps "Scheduler" and
  "Radial Charts" as categories, drops its "2plot network" section (the
  menu has it) and its "name — role" titles; email keeps "App";
  muicharts keeps its families as categories and its raw-markdown
  changelog becomes the Timeline; leaflet and emojimart already have
  categories — map them onto CATEGORY_ORDER; llms loses the two
  duplicate listings and GAINS the Admin section (today hidden from the
  owner too); pannellum retires pip-install-python.com and its
  pre-network Other Apps; clerkhook: the public nav is n/a (lockdown) —
  a11y labels only. Every component fork sets UPSTREAM (MUI X, Leaflet,
  React Flow, React Email, FlexLayout, emoji-mart, Excalidraw,
  model-viewer, Pannellum) and API_PACKAGES = [its package].
acceptance: tests/test_nav_contract.py green (a11y, no-dcc, menu ==
  registry, anonymous tree has no /admin/ href and the admin tree lists
  every admin page, sections follow CATEGORY_ORDER, footer, changelog,
  api fixture) + tests/test_excluded_links_hidden.py (rewritten) green;
  the rendered section list pasted in the report; and the ops seat's
  visual pass in the owner's browser — the owner asked for polish, which
  no test measures.
notes: detect fires on every fork today. THREE places the design did
  not fit the template's tree, each now in the contract text so no fork
  rediscovers it: (a) the registry `icon` field — the package forwards
  every entry key to register_network_site and TypeErrors at boot; icons
  live in ICONS keyed by URL (contract 2); (b) `_prop_names` — absent on
  Dash 4 generated classes; read metadata.json (contract 7); (c) inline
  images — markdown2dash has no `image` renderer and mistune's fallback
  raises on DMC children; patch_renderer() adds one (contract 9). A
  fourth, smaller: DMC's Burger accepts `aria-label` as a wildcard prop
  though its docstring does not list it — pinned by construction in the
  a11y grep, not by the docstring.
  KIT TRAP FOR THIS ITEM (1.6.41): DMC 2.8's Anchor / ActionIcon accept
  `aria-*` wildcards but REJECT `title=` with a TypeError raised at app
  CONSTRUCTION — the whole site fails to boot. Use dmc.Tooltip for any
  hover text. SECOND-ROUND FITS (leaflet, excalidraw, modelviewer, all
  measured on real packages, all now in the template): (a) the
  changelog heading regex accepts `-`, `–` and `—` between version and
  date — an em-dash repo rendered every version DATELESS; (b) Resources
  bans the OWNER's links only (GITHUB_URL, GITHUB_PROFILE_URL,
  pip-install-python, discord.gg, youtube.com) — five of nine upstream
  projects live on GitHub and contract 5 REQUIRES the upstream link;
  (c) `tier: auth` / `admin` docs pages show a lock + Tooltip ("Sign in
  required" / "Admin access required") — signage, the gate is unchanged;
  (d) /changelog and /api register the FULL machine record
  (page_visibility.register_default + page_tiers.register +
  register_page_metadata with lastmod: the changelog's newest dated
  heading; /api's committed-extract `generated` stamp) — a module-level
  LLMS_DOC alone enters the sitemap undated and escapes the control
  board's llms.txt toggle; (e) /api reads three sources in order —
  metadata.json, the committed `api_metadata.json` extract
  (scripts/build_api_metadata.py; a component REPO's metadata.json can
  be a 27 MB gitignored artifact absent on the host, so /api renders
  EMPTY in production while every local check passes), then the class
  docstrings (hook-based packages ship no metadata) — and escapes pipes
  in EVERY Markdown cell; forks with a no-regeneration guard exempt
  tests/fixtures/.
  CARGO CANDIDATES (1.6.41, measured by muischeduler against 519d496):
  nine files came out BYTE-IDENTICAL after its port — components/
  navbar.py, footer.py, pages/changelog.py, pages/api.py,
  lib/api_reference.py, lib/aside.py, lib/network_directory.py,
  pages/traffic.py, lib/directives/source.py — the next round's block
  candidates. header.py joins them at 1.6.41: its last fork content
  (logo asset, wordmark colour and breakpoint) moved to lib/constants
  (LOGO_ASSET, LOGO_STYLE, WORDMARK_COLOR, WORDMARK_VISIBLE_FROM), and
  create_link() takes visible_from so the GitHub icon drops at phone
  widths (the footer carries it there). Also 1.6.41: the skip link
  ("Skip to content" → #main-content, first tab stop, visible on
  focus) adopted from muischeduler into appshell + main.css — ahead of
  the template on requirement 9; and the two per-fork pins generalised:
  the API test branches on API_PACKAGES (declared → /api registered, in
  the sidebar, components from metadata.json; none → no /api), and the
  aside pin + the hidden-links positive control derive their pages from
  the registry instead of naming template paths.
  THE VISUAL PASS (1.6.39, same item): four things no test had
  measured, all now contract + pinned — (i) the AppShell reserves the
  aside column on every page; collapse it where no `.. toc::` fills it
  (lib/aside.py + a callback on url.pathname) or /changelog renders
  with an empty right gutter; (ii) the mobile Drawer is keepMounted
  (the hamburger's callback fires but a mount-on-open transition can
  leave it empty; and #navbar-admin-mobile must exist on every load);
  (iii) code blocks inside a List item / Blockquote widen the whole
  document at phone width — `min-width: 0; max-width: 100%` on the
  public Mantine wrappers + `overflow-x: auto` on pre, in main.css,
  never per page; (iv) Menu.Dropdown gets a solid themed background
  (near-transparent in dark mode by default) and every PRIMARY entry
  an icon.

### 17. The battery's default UA names the browser lane; no fork-local og:image augmentation (1.6.40; found by muischeduler)
class: contract (both live tools have been contract-class since
  1.6.29 — every fork's copy carries its own stubs; port the constant,
  not the file).
files: scripts/network_smoke.py (`BROWSER_UA` = Chrome/AppleWebKit token
  + INTERNAL_UA + " network-smoke"; `UA = BROWSER_UA`; CRAWLER_UA
  untouched) · tests/test_network_smoke.py (the lane pin) · your run.py
  IF it augments the crawler HTML with og:image / twitter:* tags.
detect: `python -c "from dash_improve_my_llms import classify; from
  scripts import network_smoke as n; print(classify(n.UA)['lane'])"`
  prints `crawler` ⇒ not adopted. And `grep -c "og:image" run.py` ≠ 0
  ⇒ you carry an augmentation the template does not.
contract:
  (a) At dimll ≥ 2.8 a User-Agent with no browser engine token is
      crawler-lane, so the battery's default UA — the bare internal
      token plus " network-smoke" — made every default-UA check read
      the prerendered crawler document. On muischeduler its own
      `installable_as_an_app` ("no manifest link") and
      `social_card_real_pixels` ("2 og:image tags") went red in CD's
      VERIFY job the moment the floor moved. The template never went
      red only because its battery has no browser-document check with
      the default UA (its default-UA checks read healthz, llms.txt,
      robots, sitemap — crawler-lane surfaces regardless) — the default
      was still the wrong lane. Fix: a real Chrome/AppleWebKit token
      FIRST, the internal token AFTER it (INTERNAL_UA_TOKEN is a
      substring match — measured at 2.8.0: the new UA is `browser`
      lane and the tracker still drops it); CRAWLER_UA is the other
      lane, untouched. scripts/smoke_live.py already had this shape
      (BROWSER_UA + internal token) — audit yours.
  (b) The template's run.py injects NO og:image / twitter:card /
      twitter:image; Dash emits those per page and templates/index.html
      declares only the auxiliaries (og:image:width/height/type/alt,
      secure_url) plus the one exempted static twitter:card (item 8).
      A fork that augmented the crawler HTML with those tags on top of
      the package's has a DUPLICATE the moment its battery reads the
      browser document — remove the augmentation, or guard every
      injected tag the way `canonical` is guarded (emit only when the
      package did not). muischeduler's is fork-local (recorded there as
      divergence 8 pending this item); if yours came from an older
      template era, say so in the report — it is not in 1.6.40's tree.
acceptance: the lane pin green; `grep -c og:image run.py` = 0 or
  every injected tag guarded; your live battery green on the browser
  document with the default UA.
notes: THE LESSON IS THE LANE, again: name the lane in every UA you
  send, and check the body says which document answered. It is the
  fourth time this round (kit trap, item 12's proxy test, item 15's
  in-process/wire split, and now the battery's own default).

## Reporting

Per-item disposition table (applied / ported-as-contract /
already-present / not-applicable-because / open, each with
evidence), any DIVERGENCES.md changes, full suite + CD +
`/wire-verify` output, and corrections to THIS SPEC where it
mismatched your tree. `open` (1.6.28): the detect fires but the
item is deliberately out of this session's scope — name it and who
acts; do not invent another word.
