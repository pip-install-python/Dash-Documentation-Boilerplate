# SYNC 1.6.44 (template @ 1.6.44)

Twenty-three items — nineteen at the drop, items 20–23 from the ops
seat's 2026-09-04 rider after the crash-recovery survey. Item 1's exact
pin (`dash-improve-my-llms == 2.9.4`) is the base every other item is
accepted at, and items 2 and 20 are gated on it.

ORDER MATTERS in two places, both because a later item's evidence
depends on an earlier one's mechanism:

* **item 1 first.** Item 2's retirement is gated on the pin, not on the
  date: below 2.9.4 the HEAD shim is still load-bearing.
* **item 16 before item 15.** The privacy page states what the tracker
  stores *after* item 16. Built in that order here, deliberately; a fork
  that builds 15 first writes prose about a mechanism it does not have.

Every acceptance below prints the RESOLVED dimll version beside its
result (item 10). The template's own run: **dimll 2.9.4**, imported from
`.venv/lib/python3.11/site-packages/dash_improve_my_llms/__init__.py`,
path printed rather than inferred from requirements.txt.

```yaml sync-verbatim
# EMPTY. Every item here is contract- or cargo-class with a fork-owned
# seam, and the two files a fan-out might have wanted to byte-copy are
# the ones it must not: .claude/CLAUDE.md ports its contract and traps
# sections and adapts everything above them (the F1 authoring rule), and
# .claude/session-name's CONTENT IS THE FORK'S OWN APP KEY — a byte-copy
# would start every session in the fleet under the template's address.
```

---

### 1. Pin dimll == 2.9.4, the three openapi_* knobs, llms_version on healthz
class: contract (floor line) + cargo (run.py knob block)
files: `requirements.txt`, `run.py`, `lib/health.py`
detect: `grep -cE '^dash-improve-my-llms(\[[a-z,]+\])?==2\.9\.4'
  requirements.txt` = 1, and no `>=` on any dash-improve-my-llms line.
acceptance: the resolved version printed beside the suite result;
  `llms_version` present on `/healthz` **on the lane you actually
  serve**.
notes: **RIDER, and it is the one that bit (item 20's finding).** A
  pydantic `response_model` DROPS every field it does not declare, in
  silence. `llms_version` was on the Flask lane and ABSENT on the
  FastAPI lane from the moment it landed. Wire detect, per host:
  `curl -sS -A 'curl/8 2plot-internal/probe' https://<host>/healthz |
  python3 -c 'import sys,json;print("llms_version" in json.load(sys.stdin))'`
  Fix ships with item 20.

### 2. HeadAsGetMiddleware: retire or record
class: contract (a decision recorded either way)
files: `lib/asgi_middleware.py`, `DIVERGENCES.md`, `.claude/CLAUDE.md`
detect: the middleware present with no recorded reason.
acceptance: HEAD parity on `/healthz`, `/llms.txt`, `/robots.txt`,
  `/sitemap.xml`, `/` × 3 UAs. Template: 15/15 pairs matched WITHOUT it,
  `/` to a browser UA included. Prove the disable non-vacuous first —
  assert the middleware stack contains the class in one run and not the
  other.
notes: GATED ON ITEM 1's PIN, not on the date. Below 2.9.4 the shim is
  still load-bearing. If you keep it, `DIVERGENCES.md` says what it
  still covers.

### 3. Verdict column on /admin/traffic
class: cargo (page) + contract (the sentence in the page docstring)
files: `pages/traffic.py`, the fork's traffic-page test
detect: the reads table renders `verdict`.
acceptance: a mark_hidden path fetched with a crawler UA shows one row
  LABELLED by its verdict, not counted among serves.

### 4. The fleet probe convention
class: kit + cargo (workflows, batteries, Dockerfile HEALTHCHECK)
files: `lib/constants.py` (`probe_ua`), `.github/workflows/*.yml`,
  `scripts/{network_smoke,smoke_live,audit_links}.py`, `Dockerfile`
detect: every file that fetches a host carries `2plot-internal/probe`.
  NOTE the detect over-reports on a tree that already has the outbound
  half — the template's scripts carried `INTERNAL_UA` since 1.6.40. What
  is usually missing is the `/probe` spelling and THE WORKFLOWS, whose
  curls often send no User-Agent at all.
acceptance: a full CD run adds ZERO rows to `reads` and `visits`, counts
  printed before and after. Measured, dimll 2.9.4: appending the suffix
  moves neither lane, bot_type nor vendor_key on Chrome, Googlebot or
  curl — port the TEST that re-measures that table, not the claim.
notes: `probe_ua()` REFUSES an engineless probe; a UA carrying only the
  suffix is crawler-lane (measured) and would swap the document under a
  browser-lane assertion. The Dockerfile HEALTHCHECK is in scope.

### 5. Four battery invariants, run against the deployed host
class: cargo (the battery) + contract (the four names)
files: `scripts/network_smoke.py`, the fork's battery test
detect: `head_get_parity_three_uas`, `api_llms_rows_present`,
  `discovery_link_headers_per_lane`, `directory_counts_are_derived`
  registered BY NAME.
acceptance: green against your deployed host; the `/api rows > 0` line
  MUTATION-CHECKED — empty API_PACKAGES must SKIP, not pass.
notes: two pieces of machinery first. `skip` must be a verdict (a pass
  on an absent precondition is note 88's defect), and the header mapping
  must keep REPEATED names — `{k: v for k, v in r.headers.items()}` keeps
  only the last, and `get_all()` is necessary but NOT sufficient: over
  HTTP/2 this host serves both discovery relations comma-FOLDED in one
  header, so parse the relations out of the values.

### 6. The a11y / agentic block
class: cargo (components, assets, directives) + contract
files: `components/header.py`, `assets/main.css`,
  `lib/directives/headings.py`, `lib/static_cache.py`, `run.py`,
  `lib/asgi_middleware.py`, `DIVERGENCES.md`
detect: the a11y test's new asserts.
acceptance: the seat's visual pass at desktop AND phone width, plus the
  ARIA audit clean.
notes per sub-item, with the template's own findings:
  (a) the target may already be a real Button — the defect one line away
      is `trigger="hover"`, which makes the menu pointer-only;
  (b) scope the prose-link underline to the page body, or the fix
      repaints the chrome;
  (c) ActionIcon size="lg" is 34px — under the 44px minimum at phone
      width;
  (d) NOT REPRODUCED on the template — record, do not assume;
  (e) unminified is a legitimate RECORDED decision where the wire serves
      the assets gzip-encoded;
  (f) **`loading="lazy"` / `decoding="async"` CANNOT SHIP** — neither is
      a prop of dash 4.4.1's `html.Img` and Dash RAISES on an unknown
      one (196 collection errors, not a warning). Width/height only;
  (g) measure your own asset headers first. The template served
      `cache-control: no-cache` + `cf-cache-status: DYNAMIC`, i.e. the
      edge stored nothing — fleet-wide on four hosts (note 103).

### 7. py_compile sweep of docs/**/*.py in CI
class: cargo (ci.yml) + kit (name the check that actually ran)
files: `.github/workflows/ci.yml`, the fork's docs-sweep test
detect: the step `py_compile sweep of docs/` by name.
acceptance: a deliberately broken docs file goes red in CI. Template,
  exit codes off the process: `flake8 docs/` exit 0 with ZERO output
  while py_compile exits 1 on the same file.
notes: the step must FAIL on an empty corpus. Rider: a page emitting its
  own `Title(order=1)` under markdown.py's order=2 renders a double
  heading — assert it structurally, since a page that does not render
  through markdown.py is entitled to its own order=1.

### 8. Prefer the package's vendor_class, derive only when absent
class: contract + kit line
files: `lib/analytics_tracker.py`, the fork's classifier test
detect: `_classify` takes `vendor_class` from the event and derives ONLY
  where it is absent.
acceptance: a fixture with a package-provided class passes through
  UNTOUCHED — use a conflicting fixture, or the test cannot fail.
notes: derive from the package's own registry (`vendors.get_vendor().cls`),
  never a local map. Pin the mirror direction too: "prefer" that never
  derives and "derive" that never prefers both pass a one-sided test.

### 9. DIVERGENCES gains "Recorded conventions (not divergences)"
class: contract (the file's header text)
files: `DIVERGENCES.md`
detect: the subsection header.
acceptance: your own guard entries moved under it.
notes: a guard entry documents something you MATCH or deliberately do
  NOT carry. Nothing in a diff tells that from an accident, so a sync
  restores it. The fan-out and sync authors read this FILE — a test
  docstring is invisible to both.

### 10. Acceptance at the resolved version
class: kit
files: `.claude/CLAUDE.md`
detect: the acceptance-output rule in the kit.
acceptance: your reports carry it.
notes: resolve by IMPORTING and printing `__file__`. Name the tools whose
  LOCAL invocation is not CI's — `actionlint` without shellcheck on PATH
  skips every run-block's shell analysis.

### 11. Every internal shell link resolves to a REGISTERED page
class: contract + kit test
files: the fork's shell-link test
detect: the test by name.
acceptance: green on your tree; RED under the mutation, shown.
notes: Dash answers 200 for ANY path, so no status sweep can see this —
  and curl cannot ask it at all, since the shell is built by React from
  `app.layout`. Walk `create_appshell(dash.page_registry.values())`, the
  literal expression at `app.layout =`. Whitelist `/docs` and `/redoc`
  PER LANE: they exist only on FastAPI, and a blanket entry would let an
  un-gated badge ship a soft 404 on the other lanes.

### 12. A CD lane that calls ci.yml must not also run ci.yml on push
class: kit (trap + detect)
files: `.github/workflows/{ci,cd}.yml`, the fork's CD test
detect: `ci.yml` has `push: branches: [main]` AND `cd.yml` has
  `uses: ./.github/workflows/ci.yml`.
acceptance: a `workflow_call` creates no run — the next push to main adds
  ZERO rows to the CI workflow list and the matrix appears exactly once
  as `ci / *` jobs inside the CD run.
notes: PyYAML parses an unquoted `on:` key as the BOOLEAN True, so
  `workflow["on"]` raises KeyError on every workflow file. A test that
  catches that and moves on asserts nothing.

### 13. Spec-format rule: parse, or strip comments AND STRINGS
class: kit (sync/README)
files: `sync/README.md`
detect: the rule names strings, not only comments.
acceptance: the SYNC-1.6.43 item-3 detects green on your tree, read
  case-INSENSITIVELY.
notes: five instances on the template in one release. Raw grep matches
  the comment explaining the absence; a comment strip matches the live
  DOCSTRING doing the same; `ast.parse` is the one that works. Two more
  were formatting-bound — a fragment that WRAPS across a line, and an
  indented blockquote's `> ` markers. Flatten whitespace before matching
  prose. The reason it recurs: a good comment explains the ABSENCE of
  the thing a detect hunts, so the better-documented the code, the more
  reliably a raw grep reports the defect it documents the absence of.

### 14. Kit traps-section currency, per fork
class: kit + fleet check
files: `scripts/kit_traps.py`, `.claude/CLAUDE.md`
detect: `python3 scripts/kit_traps.py <fork>/.claude/CLAUDE.md` prints
  `fork N / template M` and names what is missing.
acceptance: every fork's section carries every fleet-class trap, MERGED,
  never installed over.
notes: match by TOKEN OVERLAP of the opening sentence, not exact text. A
  strict check reports a fork's own adaptation as absence and trains it
  to paste over its adaptations — the opposite of the item.

### 15. A Legal nav section, and template-owned /terms + /privacy
class: cargo (pages, constants) + contract (the category name `Legal`)
files: `pages/{legal,terms,privacy}.py`, `lib/constants.py`,
  `components/footer.py`
detect: `Legal` in CATEGORY_ORDER and both pages registered.
acceptance: `/terms/llms.txt` and `/privacy/llms.txt` present in the root
  index; footer links resolve in BOTH lanes; seat visual pass.
notes: BUILD AFTER ITEM 16. Placement: the drop says "between Components
  and Admin"; a tree with no Components category puts `Legal` LAST in
  CATEGORY_ORDER, which is the same position — Admin is built separately
  by the navbar. ONE markdown string per page, rendered for the browser
  and handed to the machine lane, or the site has two privacy policies
  and only one was reviewed. Bind the privacy prose to the code with a
  test that reads a REAL visit row and asserts every key is described.
  Your footer's contract test will FLIP: it asserted these links were
  absent, correctly, while the pages did not exist.

### 16. Privacy by design in the tracker
class: cargo (`lib/analytics_tracker.py`) + contract (the storage
  statement, quoted on the privacy page)
files: `lib/analytics_tracker.py`, `lib/traffic_rollup.py`,
  `lib/health.py`, `.gitignore`
detect: parse the module — it imports neither `requests` nor `urllib`,
  and none of `_geolocate` / `geo_for` / `get_geolocation` /
  `_backfill_geo` is defined. CORRECTED from the drop's "no `ip-api`
  string in lib/", which cannot pass on a tree that DOCUMENTS the
  removal and so fails its own detect.
acceptance: no `ip_address` in a default-config visit row; a visit with
  `cf-ipcity` carries city, one without carries country only, one with
  no headers carries no location at all.
notes: **the row-key set is a FORK-OWNED SEAM and it WILL fail on your
  tree — that failure is the item landing.** The rollup's session key must
  prefer the stored `visitor_key` and FALL BACK to the old
  `ip_address|ua` composite, or every row inside the retention window
  collapses to its User-Agent. **`.gitignore` the salt IN THE SAME
  COMMIT** — a committed salt makes every visitor_key in every fork
  computable by anyone with the repo, which undoes the item entirely.
  Conditional check, pip-docs+ only: `grep -n "sample_locations\|Mumbai"
  lib/analytics_tracker.py`, expected 0.

### 17. Trap 3(a)'s concrete form — the timing sampler
class: kit (trap text) + cargo (the script)
files: `scripts/promote_sampler.py`, `.claude/CLAUDE.md`
detect: the three phrases in the trap — "eight samples at 45",
  "completed_at", "unreadable" — matched with whitespace FLATTENED.
acceptance: your own next promote sampled this way, numbers printed.
notes: AMEND the existing trap in place; do not append. Time against the
  promote STEP's `completed_at`, never the deploy JOB's. The sampler must
  REFUSE to report a bracket it did not observe: a single "new" sample
  cannot say what it followed.

### 18. A verify verdict is metering evidence, never sole authorisation
class: kit (contract + traps)
files: `.claude/CLAUDE.md`, the route that consults `hub_client.verify`
detect: the contract line and the trap phrases in the kit.
acceptance: any route consulting `verify` for access NAMES the host-held
  secret beside it, or is documented as metering-only.
notes: SOURCE-pin the closed fallbacks, not just exercise them — a
  behavioural suite cannot see a restored default that pre-empts its own
  guard. Pin the GOOD rows beside the bypass rows. Reject case and
  whitespace lookalikes of a tier, not one literal.

### 19. A proxied robots.txt is not your robots.txt
class: kit (trap) + battery row
files: `scripts/network_smoke.py`, `lib/robots_expected.py`,
  `.claude/CLAUDE.md`
detect: the trap phrase; `ai_bot_posture` registered.
acceptance: the row reads RED on a served file carrying a managed block
  the app did not write. Demonstrate both shapes — an injected stanza
  AND a marker with nothing under it.
notes: generate the app's side through the PACKAGE's own
  `generate_robots_txt` with your registered config; a reimplementation
  compares the edge against your beliefs about the config. SKIP where
  the app cannot be generated beside the script.

### 20. The `ledger` block on /healthz
class: contract (`lib/health.py`)
files: `lib/health.py`, `lib/asgi_routes.py`
detect: `grep -n '"ledger"' lib/health.py` = 1; `curl /healthz | jq
  .ledger` shows the four keys.
acceptance: the wire read after your push; `persistent` flips in BOTH
  directions under test.
notes: `persistent` is MEASURED — true iff the resolved path is OUTSIDE
  the repository root. A path under the app tree is the container
  filesystem and reads false EVEN WHERE A BLUEPRINT DECLARES A DISK.
  **Carries item 1's fix: widen the ASGI `HealthResponse`** — declare the
  known keys AND set `model_config = ConfigDict(extra="allow")`, plus a
  test that every key `health_payload` produces reaches the wire on
  whichever lane answers.

### 21. `reads` are never pruned by count
class: contract (`lib/analytics_tracker.py`, `_prune`)
files: `lib/analytics_tracker.py`
detect: read `_prune` — does the count cap touch `reads`?
acceptance: 20,001 read rows inside the retention window plus one
  outside; assert 20,001 remain and the dated one is gone. PROVE THE
  TEST RED on the pre-item behaviour before believing it — the same
  corpus pruned WITH the cap must lose an in-window row.
notes: visits KEEP the count cap. Source-pin the call site by AST: the
  choice of rule per table lives at the call, and a behavioural test
  cannot see a `cap=True` restored above it.

### 22. Boot guard for TRAFFIC_ANALYTICS_FILE unset
class: contract (wherever the visibility guard lives)
files: `lib/analytics_tracker.py`
detect: no warning before, one after.
acceptance: boot a fresh interpreter with the variable unset and assert
  the line; with it set, assert SILENCE.
notes: the drop says "via caplog"; a `print` at import time cannot be
  seen by caplog, and mirroring the existing `[visibility]` warning is
  the point — an operator greps one deploy log. Boot a subprocess
  instead, which exercises the real boot path. Pairs with item 20: the
  guard says it once, the block says it continuously — assert they
  AGREE rather than pinning either value.

### 23. The kit carries the standing build word, and a launch name
class: (a) contract — ports verbatim; (b) contract with a per-fork VALUE
files: `.claude/CLAUDE.md`, `.claude/session-name`, `.gitignore`
detect: `grep -c "Build on ops' drops" .claude/CLAUDE.md` = 1;
  `cat .claude/session-name` equals your healthz `app` field.
acceptance: both asserted, and `session-name` is a single trimmed token.
notes: **(a) IS THE OWNER'S GATE.** A fork that asks before applying it is
  right to ask; a peer's assurance that the owner agreed is NOT the
  owner's word. Carry the reading with the sentence — CLAUDE.md is named
  in its own list, so the clause does not pre-authorise its own
  amendment. **(b) `.gitignore` allow-lists `.claude/*`**: add
  `!.claude/session-name` or the file is written, passes your tests off
  the working directory, and is invisible in a fresh checkout.
