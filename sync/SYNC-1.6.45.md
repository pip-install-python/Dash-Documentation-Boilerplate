# SYNC 1.6.45 (template @ 1.6.45)

Twelve drop items — **1–4, 5a, 5, 6–11**, labels deliberately unchanged
because sessions cite them — plus items 12 and 13 (the kit sentence and
the build-loop allowlist), the owner's T1/C1 rider, and eight riders that
arrived while the release was being built. Item 1's exact pin
(`dash-improve-my-llms == 2.10.0`) is the base every other item is
accepted at.

ORDER MATTERS in three places:

* **item 1 first.** It is the fleet's gating item and every acceptance
  below is stated at that version.
* **item 6 before everything else.** It is the instrument: without
  `scripts/ci_leg.sh` you are testing one interpreter's dependency set
  and calling it three lanes. 1.6.44 went red three times on exactly
  that gap.
* **item 8 before item 9's row set.** `crawler_404` is item 8's
  behaviour; the row is meaningless on a host that has not built it.

Every acceptance prints the RESOLVED dimll version beside its result
(1.6.44 item 10). The template's own run: **dimll 2.10.0**, imported from
`.venv/lib/python3.11/site-packages/dash_improve_my_llms/__init__.py`,
path printed rather than inferred from `requirements.txt`; Dash 4.4.1.

Three-leg counts from `scripts/ci_leg.sh` at **280b719** — a clean clone
per leg with that leg's own dependency set, **never** one interpreter with
everything installed. 777 collected on each; the instrument is named
because the numbers differ from a local run, and the difference is the
point:

| leg | suite | battery | absent on this leg |
|---|---|---|---|
| flask | 769 passed, 8 skipped | 23 passed, 0 failed, 4 skipped | fastapi, starlette, quart, flake8, pillow |
| fastapi | 772 passed, 5 skipped | 24 passed, 0 failed, 3 skipped | quart, flake8, pillow |
| quart | 766 passed, 11 skipped | 23 passed, 0 failed, 4 skipped | fastapi, starlette, flake8, pillow |

A LOCAL run of the same tree reports flask 773/4, fastapi 774/3, quart
770/7 — higher passes and fewer skips, because the dev interpreter has
every backend installed. Quoting those as the release's counts is the
mistake 1.6.44 went red three times on.

```yaml sync-verbatim
# EMPTY, again, and for the same reason as 1.6.44. Every item here is
# contract- or cargo-class with a fork-owned seam. `.claude/CLAUDE.md`
# ports its contract and traps sections and adapts everything above them;
# `.claude/session-name`'s CONTENT IS THE FORK'S OWN APP KEY.
```

---

### 1. Pin dimll == 2.10.0, every encoding moved
class: contract (the pin rule) + cargo (the line)
files: `requirements.txt`, `run.py`, tests, CI
detect: `grep -cE 'dash-improve-my-llms(\[[a-z,]+\])?==2\.10\.0'
  requirements.txt` = 1 and no `>=` on any dash-improve-my-llms line.
acceptance: `llms_version` on `/healthz` equals the pin, on the wire,
  twice, **on the lane you actually serve**.
notes: HISTORY, corrected — 1.6.44 shipped an exact `==2.9.4` on the
  template, so this is the second deliberate bump here. For every FORK
  it is the FIRST pin, replacing `>=2.8.0`. A `>=` floor can never pull a
  new release through a Docker cache hit; the requirements line changing
  IS the cache bust, and floors live in several encodings — grep the
  number, move every one.

### 2. SKILL.md, generated from the corpus, never hand-written
class: cargo (generator) + contract (the name rule)
files: `lib/skill_doc.py`, `run.py`
detect: `/.well-known/agent-skills/index.json` lists ≥ 1 skill.
acceptance: `sha256` of the FETCHED SKILL.md equals the index digest.
notes: frontmatter `name` is the host's package's PyPI name; a host with
  no package (this one) serves one skill for the network's use.

### 3. Eight battery rows for the well-known surfaces
class: cargo + contract
files: `scripts/network_smoke.py`, `tests/test_network_smoke.py`
detect: `grep -c 'wellknown_unknown_404' scripts/network_smoke.py` = 0, or
  any of the eight row names absent from the registration list.
acceptance: green on the template; each row mutation-checked once, and
  each names what it did NOT cover when it skips.
notes: **A defect was RECORDED, not worked around.** `/healthz`,
  `/api/backend` and `/api/pages` emit the same `operationId` for GET and
  HEAD — 16 operations, 13 distinct — so the OpenAPI document is invalid
  fleet-wide. The cause is structural (dimll adds HEAD; FastAPI generates
  one id per route), so it is in `DIVERGENCES.md` as a dimll 2.11 item.
  Do not patch around it in a fork.

### 4. The agent-readiness scan as a recorded number
class: cargo
files: `scripts/agent_readiness.py`
detect: the file is absent, or it exits 0 on a scan that could not run.
acceptance: the release report quotes level + failing check names.
notes: three exit states, and the distinction is the point — 0 met the
  floor, 1 ran and failed, 2 COULD NOT RUN. A scan that could not run is
  not a scan that passed. The token is never written, echoed, printed or
  put in a URL.

### 5a. The licence agrees on every surface
class: contract
files: `lib/skill_doc.py`, tests
detect: a licence name written as a literal anywhere it is served,
  rather than read from `LICENSE`.
acceptance: the licence name checked through the MACHINE lane, not just
  the repo file.

### 5. The well-known namespace as a recorded convention
class: kit
files: `DIVERGENCES.md`, `tests/test_skill_doc.py`
detect: a host registering its own `/.well-known/*` route before
  `add_llms_routes()` and not recording it.
acceptance: the detect reads PROVENANCE (the handler's `__module__`) and
  asserts the sweep was non-empty.
notes: **the first version of this detect was wrong on BOTH lanes, in
  opposite directions, and each error hid the other.** On flask it read
  the router AFTER `add_llms_routes()` and called the package's own four
  routes this host's — red on a clean tree. On fastapi it passed by
  sweeping ZERO paths: those routes register at lifespan, and once the
  lifespan runs they sit inside `_IncludedRouter` objects that expose no
  `.routes` (the real router is on `.original_router`). Fixed in
  `12c7bc0`. If your fork's copy greps the router, it has this.

### 6. `scripts/ci_leg.sh` — a CI leg's dependency SET, locally
class: cargo (the script) + contract (the acceptance shape)
files: `scripts/ci_leg.sh`, `scripts/smoke_inproc.py`
detect: the file exists and `ci_leg.sh flask` exits 0.
acceptance: **three legs green through the script, and the release note
  quotes the per-leg counts it printed.** Counts are taken AFTER the
  commit — the script clones, so it reports committed code.
notes: the instrument for everything else. Do not upgrade pip inside a
  proxied sandbox (pip ≥ 26 uses the system trust store and rejects the
  proxy cert). Mask absences with `sys.modules[name] = None`, never a
  raising stub — a stub still satisfies `find_spec`. RESOLVE what a leg
  installs; never assume. The in-process battery must run the ASGI
  LIFESPAN or it measures an app with no pages.

  **A FIX LANDED HERE AFTER THE SEAT MIRRORED THIS RELEASE, and it is a
  defect in the instrument's own test, not in the app.** `/healthz`
  embeds `ledger.path` as the checkout's ABSOLUTE path, so the body's
  LENGTH VARIES WITH WHERE THE REPO SITS. `test_smoke_inproc_dispatch`'s
  probe read exactly 400 bytes: a shallow clone gives 337 and parses;
  `ci_leg.sh` clones into a deeper work dir, the body crosses 400, and
  the probe returned JSON cut mid-token. It then failed as a
  `JSONDecodeError` — which reads like a broken app rather than a probe
  that stopped reading. Reproduced here at 427 bytes: "Unterminated
  string starting at char 398". CI's own checkout
  (`/home/runner/work/<repo>/<repo>`) sits under the old cap BY ACCIDENT
  OF PATH LENGTH, so this was invisible to every green CD run.

  The probe reads the whole body under a 64 KB cap and reports
  `truncated` as its own flag, so a cut can never again arrive disguised
  as a parse error. A control forces a long ledger path, asserts the
  path reached the served document AND that the body exceeds 400 bytes —
  a control that no longer crosses the old cap proves nothing. Forks
  taking this file take both.

  A fork with a SHORT checkout path will pass either way. That is the
  trap, not a reason to skip the fix.

### 7. `/healthz` counts the ledger without parsing it
class: contract
files: `lib/health.py`
detect: the counting path opens the file with a full `json.load`.
acceptance: a 200k-row fixture answers in < 50 ms and the counts equal
  the file's.
notes: measured 200k rows / 39.2 MB in **31.1 ms** (full parse 126 ms).
  An earlier attempt using one combined regex alternation was **436 ms**,
  17× worse than the naive read — the `"([a-z_]+)": \[` branch makes the
  engine try a match at every quote. Bounded `find`/`rfind` per table.

### 8. Unregistered paths answer 404 on the crawler lane
class: contract
files: `lib/soft404.py`, `run.py`, `lib/asgi_middleware.py`
detect: the crawler-lane 404 branch keys only on the hidden tier.
acceptance: an unregistered path → 404 to a crawler, 200 shell to a
  browser; a registered public page → 200 on both. Battery row
  `crawler_404` asks BOTH lanes plus a real page.
notes: measured before: `GET /definitely-not-a-page` with a Googlebot UA
  returned 200 and 46,160 bytes of app shell, byte-identical to the
  browser's. **Two lane defects while building it, both invisible on the
  lane checked first.** Dash's ASGI catch-all is spelled `{path:path}`
  with NO LEADING SLASH — skipping `/{path:path}` matched nothing, so
  both ASGI lanes concluded every path was served while flask passed
  15/15. And Quart got no hook at all: `run.py` guarded the middleware
  with `if BACKEND == "fastapi"`, and Quart is ASGI but not Starlette, so
  it takes no `add_middleware`. It has a `before_request` calling the
  same decision function.

### 9. Battery rows `assets_cached` and `healthz_keys_vs_template`
class: contract
files: `scripts/network_smoke.py`
detect: neither row exists.
acceptance: both pass on the template; each names what it did not cover.
notes: **CORRECTION TO THE DROP, accepted by ops.** "Compare against the
  TEMPLATE'S LIVE set" is a tautology *on the template* — the acceptance
  host — where the row can never fail however broken the host is. On the
  template the reference is the app's own `health_payload()` computed in
  process: wire keys vs code keys, which is exactly the ASGI
  response-model drop that hid `llms_version` for two days. On a FORK the
  drop's wording is unchanged. Mutation-checked by restoring the real
  1.6.44 defect (`HealthResponse` with `extra="ignore"`, no declared
  `llms_version`): the row goes red naming it. On a Flask origin the
  self-comparison is weak by construction — the route serialises the
  payload as-is — so its teeth are on the ASGI lanes, which is where the
  defect was.

### 10. The UA pin walks call sites
class: cargo
files: `tests/test_nav_contract.py`
detect: the pin passes when a file mentions a UA anywhere.
acceptance: a bare call beside a named one in ONE file reports the bare
  one, by line.
notes: `ast` over every Call whose func attr is `test_client`, then the
  keywords of the request made through it. Three shapes, each judged:
  bound (follow the name), chained (the call carries it), handed off (the
  ONE shape file-scoped analysis cannot follow — it keeps the old
  file-level rule, and only there). Reading the tree also retires
  `_code_only` for this pin: only keyword VALUES are read, so a UA in a
  comment cannot vouch for a call. Corpus asserted IN the test: 7 files,
  9 call sites today. Mutation on the real tree — removing the one
  `environ_base` line in `scripts/audit_links.py` reds it naming lines
  190, 218, 225.

### 11. A skip is a verdict, never a pass
class: contract
files: `scripts/network_smoke.py`, `.github/workflows/cd.yml`
detect: the summary prints skips but `--require` does not exist.
acceptance: a required row forced to skip turns verify red.
notes: `ai_bot_posture` skipped on every CD run for a whole release and
  the battery stayed green — the Fable audit found it, not the battery,
  because a skip is not a failure. cd.yml's verify requires
  **`ai_bot_posture,edge_honours_vary,healthz_keys_vs_template`** — each
  checked against production first so the flag was not arming a red. A
  name matching no row is itself an error: a typo makes the flag
  decorative, which is the same failure in a new place.

### 12. The kit sentence, amended
class: contract (CLAUDE.md ports the sentence verbatim)
detect: the 1.6.44 item 23(a) sentence present and the amended one
  absent from `.claude/CLAUDE.md`.
acceptance: the kit test that pins the sentence pins the NEW text.
notes: component forks push on the seat's word; **the template keeps the
  owner's push word** (a bad template push fans out on the next round),
  and the anchors carry no sentence at all. A peer's assurance that the
  owner agreed is not the owner's word — ask in your own terminal.

### 13. The satellite build-loop allowlist
class: cargo, byte-owned per fork for its WebFetch domains
detect: `permissions.allow` absent from `.claude/settings.json`.
acceptance: a full build on a fresh fork session raises zero permission
  dialogs.
notes: the template's own file keeps `git push` behind the owner's word.
  No unrecognised top-level keys — the settings validator rejects them.

---

## Riders and notes that landed in this release

### T1. The landing page opens with how you get the thing
class: cargo (the generator) + contract (nothing typed by hand)
files: `lib/versions.py` (`{{INSTALL}}`), `pages/home.md`
detect: the home page's first blocks contain no install/acquisition
  block, or contain a hand-typed version string.
acceptance: the block appears above the fold in BOTH lanes — inside the
  first 800 characters of `LLMS_DOC`, and in the rendered layout. On a
  fork the version equals `version_of(<its dist>)`.
notes: **CORRECTION, accepted by ops.** T1 says every landing page opens
  with `pip install <package>`. This host has no package —
  `pypi.org/pypi/dash-documentation-boilerplate/json` is 404 and the repo
  has no `pyproject.toml` or `setup.py` — so the line would publish an
  install instruction for a distribution that does not exist, in both
  lanes, on the most-copied page in the network. The rule underneath
  ships: the page opens by saying how to obtain the thing, nothing typed
  by hand. **A fork gets T1 verbatim** — `pip install <dist>` plus the
  resolved version. The block lives in the MARKDOWN, not the layout, so
  it reaches `LLMS_DOC` and every agent; a Dash component would have been
  invisible to the machine lane.

### C1. The private reporting contract loses its public link
class: contract (prose the network states identically)
files: `docs/network-standard/network-standard.md`,
  `docs/ai-integration/ai-integration.md`
detect: `grep -r '](https://2plot.ai/docs/satellite-analytics' docs/
  pages/` returns any line.
acceptance: no clickable link to the private document anywhere in
  `docs/` or `pages/`, AND the replacement sentence present — removing
  the link without it leaves the section stating no contract at all.
notes: measured before acting — the linked document answers 404 to
  Googlebot and gives a browser the hub's SPA shell, the same byte count
  a nonexistent path returns. One sentence, no link. The URL still
  appears once inside a fenced block quoting the shipped `INTERNAL_UA`
  constant; editing docs to disagree with code would be worse. MCP
  wording: no bespoke endpoint, Dash 4.x native MCP is the path.

### note 133. `{{VERSION}}` resolves a fork's OWN package from the tree
class: contract (the resolver) — **critical on every component fork**
files: `lib/versions.py`, `components/header.py`
detect: `{{VERSION:<your own package>}}` anywhere in your docs while
  `lib/versions.py` resolves only through `importlib.metadata`.
acceptance: the suite green in a venv WITHOUT the fork's own package
  installed, and the landing/migration pages rendering the tree's
  version in that venv.
notes: a component fork's package is imported from the TREE and never
  installed (CI installs requirements.txt; the image does `COPY . .`), so
  `{{VERSION:<own package>}}` raised LookupError during app construction
  and took the whole site down. Resolves from the module's `__version__`
  when the distribution is absent AND the name is one this host
  documents; **every other name keeps the LookupError**, or a typo
  becomes silent prose. One resolver — the header's badge delegates to it.

### note 139. A board-hidden page leaves the nav and both searches
class: **fix + regression test** — ops made this its own sync item
files: `components/navbar.py`, `tests/test_nav_search_and_icons.py`
detect: `page_tiers.local_tier` referenced from `components/navbar.py`
  (or any listing/search module).
acceptance: a board-hidden page (or a store override) absent from the
  sidebar and BOTH search dropdowns; present again when the override is
  removed.
notes: **FOUND ON THE TEMPLATE by measuring the class rather than
  concluding the rider did not apply.** Note 139 was reported against
  pipdocs' Postgres sync path, which this tree does not have. After the
  board set `/backends` to hidden: `lib.access.effective_tier` answered
  "hidden" while `components.navbar.page_tier` answered "public", because
  the latter read the FRONTMATTER tier. The page stayed listed in the
  sidebar and both searches — the one place a hidden page is most
  visible. Every fork carries this navbar; **measure your own board.**
  The crawler's 200 on the template is CONFIGURATION (this host boots
  with `access wiring off`), not a second defect — the listing layer is
  independent of the gate, which is why the defect was reachable on a
  host where the gate is off.

### note 141. No page imports a component library inside its layout
class: cargo (regression test)
files: `tests/test_no_lazy_component_imports.py`
detect: an indented `import dash_*` / `dmc` / `dash_iconify` inside any
  layout function in `pages/` or `components/`.
acceptance: a FRESH interpreter imports run, renders every registered
  layout, and `ComponentRegistry` does not grow; a planted lazy import
  must fail it.
notes: inside pytest the libraries are already imported, so an in-process
  check passes on a tree that HAS the defect. The subprocess is the
  method. Where no plantable library is installed the control SKIPS
  naming the regression as UNVERIFIED on that leg.

### note 143. Every handler's annotations resolve
class: contract (ASGI hosts) + cargo (the sweep and the row)
files: `tests/test_openapi_document.py`, `scripts/network_smoke.py`
detect: `GET /openapi.json` answers 500 while `/docs` answers 200; or
  any FastAPI handler for which `typing.get_type_hints` raises.
acceptance: the sweep finds ≥ 10 handlers and 0 unresolvable; the
  document renders and describes ≥ 5 paths.
notes: ONE handler whose annotations cannot resolve poisons the WHOLE
  OpenAPI document, while `/docs` and `/redoc` keep answering 200 — they
  are shells that fetch it in the browser. **The check is
  `typing.get_type_hints` at runtime, not an AST scan**: an import inside
  a module-level `try:` IS module-level, and the AST form reported a
  clean host as exposed. Battery row `openapi_document_renders` takes its
  lane from the host's own `/healthz` and SKIPS on flask/quart.

### note 149. Two consecutive bad reads, and the gap verdict
class: cargo (the sampler) + contract (what counts as a verdict)
files: `scripts/promote_sampler.py`
detect: a watcher that calls anything wrong on ONE unreadable read, or a
  sampler that reports a gap verdict without printing the gap.
acceptance: one unreadable sample is an ordinary bracket member; two
  consecutive are reported; a gap under 180 s reports "no verdict
  possible".
notes: one unreadable `/healthz` mid-swap is a container restarting —
  this host put exactly one inside the bracket on both measured pairs, so
  a rule firing on one would cry wolf on every promote. The push →
  promote gap is printed beside the bracket; under 180 s the two
  hypotheses predict the same wire and the output is "NO VERDICT
  POSSIBLE". **Applying that to this host's own pairs puts BOTH under the
  floor** (112 s and 135 s against a 99–113 s build+swap). The floor was
  not tuned to make our numbers pass: the bracket-position inference
  still holds, with ~17 s of margin, and that is all it holds by.

### Admin gates (rider + two addenda)
class: cargo (the tests) + contract (the conftest snapshot)
files: `tests/test_admin_gates.py`, `tests/conftest.py`
detect: the gate tests read `dash._callback.GLOBAL_CALLBACK_MAP` live
  rather than a conftest snapshot; or they are run as a FILE rather than
  inside the full suite per leg. **Both are the defect** — a fork that
  takes the snapshot and keeps running the file alone still cannot see
  the failure.
acceptance: every `/admin` page enumerated from the registry; each
  callback invoked as anonymous and as a stranger and required to refuse
  AT ITS GATE; addendum 2 enumerates with `ast.walk` for `@callback` at
  ANY nesting and judges from the SOURCE, so a callback CI cannot invoke
  is still judged. A synthetic callback nested under `if FLAG:` with no
  gate must red.
notes: **`Dash()` CLEARS `dash._callback.GLOBAL_CALLBACK_MAP`.** Any test
  that builds its own app empties the real app's callbacks, and because
  the page modules stay in `sys.modules` nothing re-registers. After
  `tests/test_access.py` the map held 0 entries, down from 35 — and
  `test_access` sorts BEFORE `test_admin_gates`, so these tests were
  green run alone and red in the full suite, which is how they shipped.
  conftest snapshots the map at import. **Both halves matter to a fork:
  take the snapshot AND run the file inside the full suite per leg** — a
  fork that takes the snapshot and keeps running the file alone still
  cannot see the failure. The source-level verdict allows ONE hop to a
  module helper that gates; it runs BESIDE the invocation tests, never
  instead, because "names a gate" is strictly weaker than "refuses".

### Nav riders (a) and (b)
class: cargo (regression tests)
files: `tests/test_nav_search_and_icons.py`
detect: no test renders BOTH search copies; or the icon fallback uses
  the two-argument `.get("icon", DEFAULT)` form.
acceptance: neither search copy lists an admin path, a hidden-tier page
  or /404, with a synthetic admin plant excluded; every `DashIconify` in
  both copies carries `prefix:name`; the icon fallback is the `or` form.
notes: regression tests — the kit already had both behaviours. **BOTH
  copies**: the header's `create_search` is `visibleFrom="sm"` and the
  mobile drawer carries its own field, so a test of `search_data()` alone
  passes on the day one copy stops calling it. The fallback half cannot
  be seen by rendering: `entry.get("icon", DEFAULT)` returns None when
  the key EXISTS and is empty. Report `(registered, listed)` — the
  template's is **(17, 13)**.

---

## Traps this release paid for

* **A green from a file run alone is not a green from the suite.** Two
  detects shipped green because nobody ran the whole suite per leg.
* **Verify the artifact the claim is about** — and when a lane disagrees,
  THAT is the finding; never relocate the assertion to the lane that
  passes.
* **Parse, do not grep.** The PEP 563 source pin went red on a CORRECT
  file: `"from __future__ import annotations" not in source` matched the
  module's DOCSTRING, which says it deliberately omits that line. Second
  recorded instance of a grep matching the prose ABOUT the defect it
  hunts — this time inside the test written to guard that family.
* **In zsh, `"$sha:path"` applies the `:l` modifier** and swallows the
  path's first letter. Measured here: `"$sha:lib/health.py"` expands to
  `…80fib/health.py`; git exits 128, but through a pipe the pipeline
  reports exit **0** with `pipestatus=(128 0)`. Always `"${sha}:path"`,
  and read `pipestatus` when a parser sits downstream.
