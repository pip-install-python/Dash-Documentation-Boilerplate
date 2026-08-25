# SYNC 1.6.10 → 1.6.16 (retro-spec; template @ ceb0d50)

The floor round (waves 1–4) hand-carried most of 1.6.10–1.6.14 to the
twelve fleet forks; 1.6.15–1.6.16 reached only the three F1 pilots.
This spec covers the whole range with per-item **detect** so any fork
— rounded, pilot, second-ring, or brand new — consumes the same
document and applies only what it lacks. Read `sync/README.md` for
the format and `DIVERGENCES.md` (yours) before anything else.

Floor statement, per the authoring rule: after this spec,
`LLMS_PKG_FLOOR` is `(2, 7, 1)`. The rationale ladder in
requirements.txt and run.py retains every older rung by design —
do not read those as the floor.

### 1. Healthz identity + diagnostics (1.6.10 4523c69, 1.6.12 9462aff)
class: contract
files: lib/health.py, lib/asgi_routes.py (only if the fork has one)
detect: production /healthz shows app + build == HEAD + geo block
  (dimll ≥2.7), and tests pin a spoofed CF-IPCountry surfacing in
  geo.resolved on every backend the fork actually runs
contract: ONE payload builder, rendered per request (never a
  registration-time snapshot); `app` = SATELLITE_APP_KEY else
  "unknown"; `build` = RENDER_GIT_COMMIT, key omitted when unset;
  `geo` = {configured, denied, resolved} on dimll ≥2.7.0 — counts
  and flags only, key OMITTED on older packages; every route hands
  ITS OWN framework's headers to the resolver (the Flask-context
  fallback answers "no request context" on FastAPI/Quart forever —
  pannellum's production proved it). Documented additions are
  legitimate divergences (flexlayout's `version`, leaflet's
  base_url/reporting, clerkhook's minimal {ok, app, build}).
acceptance: the four 1.6.10 pins + the two CF-IPCountry pins + the
  context-free `_resolved_country({"CF-IPCountry": "DE"})` pin
  (1.6.13 — the only one that can fail from inside a Flask suite)
notes: leaflet still owes the headers-through half (its own filed
  finding); clerkhook satisfies this contract via its recorded
  minimal divergence — do not "fix" it.

### 2. dimll floor ≥2.7.1, every encoding (1.6.11 30075d0)
class: contract
files: requirements.txt, run.py (LLMS_PKG_FLOOR + message), tests, CI
detect: LLMS_PKG_FLOOR == (2, 7, 1) and the requirements install
  line says >=2.7.1
contract: the floor moves in EVERY encoding at once; the
  requirements line changing IS the Docker cache bust; the ladder
  EXTENDS (2.6.0 / 2.6.1 / 2.7.0 / 2.7.1 rungs), never rewrites;
  CHANGELOG history untouched. If the fork has NO boot floor, add
  one — then break it once deliberately, watch it refuse, restore.
acceptance: boot succeeds on ≥2.7.1 and refuses below; production
  healthz geo block present (the wire-side cache-trap tell)

### 3a. Fence-aware source expansion (1.6.11 30075d0)
class: verbatim
files: pages/markdown.py — `_expand_source_directives` (the line
  walker tracking ``` and ~~~ at depth zero)
detect: the fence unit test exists and passes ("a fenced example
  was expanded" pin)
acceptance: tests — a `.. source::` inside a fenced block stays
  documentation; a real one still expands

### 3b. Every-page structure pin (1.6.11 30075d0)
class: contract
files: tests/test_pages.py (or the fork's page-test home)
detect: a sweep test asserts exactly one <h1> per non-admin page to
  a generic client (HTML comments stripped) + no duplicate footer
  llms links (home exactly the root link once)
contract: sweep THIS fork's page registry (not the template's page
  list); exclude admin/locked surfaces for the reason the fork's own
  access model gives — never let the pin pass vacuously against 403
  bodies (clerkhook runs it through an authenticated client). Fix
  what the sweep finds; it catches real per-fork content drift
  beyond the fence class (leaflet's preamble, muicharts' M4
  headings, five forks' noscript h1).
acceptance: the sweep green against the fork's own registry

### 4. CD certifies the artifact, sized for the worst build
  (1.6.13 6a2901a + muicharts' skipped-guard, 1.6.16 ceb0d50)
class: conditional
predicate: the fork has a cd.yml that deploys
files: .github/workflows/cd.yml
detect: the wait loop compares `build == GITHUB_SHA` (check the
  BODY — step names lie in both directions), runs ≥100 × 15s with
  job timeout ≥30m, hookless deploys emit a ::warning, and the
  verify job's `if` excludes BOTH 'cancelled' AND 'skipped'
acceptance: next CD run green with the wait matching THIS sha
  before verify runs
notes: a floor bump busts the pip cache, so the round's most
  important deploy is Render's slowest — dash-email timed out on
  exactly that class.

### 5. Container honors $PORT (1.6.14 faafa8f)
class: conditional
predicate: the fork has a Dockerfile
files: Dockerfile
detect: CMD is shell-form on ${PORT:-8550} AND the HEALTHCHECK
  probes the same variable (exec-form CMD never expands env)
acceptance: CI's docker boot/battery green
notes: emojimart + muischeduler have no HEALTHCHECK at all — for
  them this item ADDS the template's block (curl in apt for the
  probe, or a python-urllib probe like clerkhook's; either way
  ${PORT:-8550}, never a hardcoded port).

### 6. The .claude development kit (1.6.15 1638528)
class: contract
files: .claude/CLAUDE.md, .claude/settings.json, .claude/skills/*,
  DIVERGENCES.md, tests/test_claude_kit.py, .gitignore
detect: test_claude_kit.py present and green
contract: skills + kit test byte-verbatim; CLAUDE.md's contract and
  traps sections VERBATIM, everything above them adapted wherever
  the fork's CLAUDE.md is its own guide (the F1 pilots' correction);
  settings.json host-swapped to THIS fork's domain (the pin derives
  it from lib/constants.BASE_URL), hub entries and "model": "opus"
  kept; .gitignore gains the .claude allow-list + session-document
  ignores (X402-SYNC-REPORT.md, HANDOFF-*.md, KICKOFF-*.md) — `git
  rm --cached` anything of that class currently tracked, and move
  any .git/info/exclude rules into .gitignore (per-clone excludes
  protect one checkout and no fork); DIVERGENCES.md written
  honestly — real divergences with reasons, retirements marked not
  deleted, no padding.
acceptance: kit test green; a probe HANDOFF-x.md is ignored;
  settings allowlist lets the session curl its own /healthz

### 7. smoke_live post() carries the SSL context (1.6.16 ceb0d50)
class: verbatim
files: scripts/smoke_live.py (post()'s urlopen gains
  context=SSL_CONTEXT), tests/test_auth_wiring.py (the source pin
  sweeping every urlopen)
detect: the source pin exists and passes
acceptance: source pin green; on macOS, the live auth probe returns
  401/200 instead of 0
notes: CI (Linux) is blind to the defect and wired tests monkeypatch
  post — only the source pin holds it.

### 8. The machine lane publishes the site brand at the root
  (1.6.16 ceb0d50)
class: contract
files: lib/page_visibility.py (published_name), pages/markdown.py
  (call site)
detect: the machine-lane home serves ONE h1 equal to the site
  brand, and the llms preamble matches the injected header
contract: whatever name dimll will inject is the name the llms doc
  preamble uses — SITE_BRAND at "/", the page name elsewhere. Forks
  with their own dedup mechanism (leaflet's published_name original,
  flexlayout's _build_llms_doc dedup) already satisfy this; record
  theirs in DIVERGENCES.md if the shape differs.
acceptance: item 3b's sweep green on "/"

### 9. The gate card promises only what ships (1.6.16 ceb0d50)
class: conditional
predicate: the fork carries lib/gate_layouts.py's preview-card copy
files: lib/gate_layouts.py
detect: the card copy does not mention "the AI assistant"
acceptance: grep clean; gate card renders

## Reporting

Per-item disposition table (applied / ported-as-contract /
already-present / not-applicable-because, each with evidence), any
DIVERGENCES.md changes, full suite + CD + `/wire-verify` output, and
corrections to THIS SPEC where it mismatched your tree — the spec is
subject to the same contract as any prompt.
