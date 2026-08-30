# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.6.41] - 2026-08-30

muischeduler's item-16 port measured nine files byte-identical to the
template and six not; the six were template asks. No runtime behaviour
changes beyond a skip link and a header breakpoint.

### Added
- Skip link ("Skip to content" → `#main-content`), the first tab stop,
  visible only on keyboard focus — adopted from muischeduler
  (`components/appshell.py`, `assets/main.css`); pinned.
- `lib/constants.py`: `LOGO_ASSET`, `LOGO_STYLE`, `WORDMARK_COLOR`,
  `WORDMARK_VISIBLE_FROM` beside `WORDMARK` — `components/header.py`'s
  last fork content, so it can become cargo. `create_link()` takes
  `visible_from`; the GitHub icon drops below `xs` (the footer carries
  it on phones).

- `/changelog` and `/api` register the full machine record —
  `page_visibility.register_default`, `page_tiers.register`,
  `register_page_metadata(... lastmod=)` (the changelog's newest dated
  heading; `/api`'s committed-extract `generated` stamp) — so both carry
  a sitemap `lastmod` and sit under the control board's llms.txt toggle
  (leaflet's finding: a module-level `LLMS_DOC` alone entered the sitemap
  undated).
- `lib/api_reference.py` reads three sources in order: `metadata.json`,
  the committed `api_metadata.json` extract written by the new
  `scripts/build_api_metadata.py` (a component repo's `metadata.json`
  can be a 27 MB gitignored artifact absent on the host — leaflet's
  `/api` was empty in production while every local check passed), then
  the classes' docstrings (hook-based packages ship no metadata —
  modelviewer). Pipes are escaped in every Markdown cell. Two fixture
  packages pin the fallbacks.
- Sidebar links to `tier: auth` / `admin` docs pages carry a lock icon
  and a `dmc.Tooltip` ("Sign in required" / "Admin access required") —
  adopted from excalidraw. `title=` is never used: DMC 2.8 rejects it
  at app construction (recorded in item 16).

- Frontmatter `nav:` — a short sidebar/search label, default = `name`
  (emojimart, muicharts: long names where they had short labels;
  shortening `name:` would churn `<title>`, og:title and the llms.txt
  heading). `Meta.nav` → `register_page(nav=)`; the sidebar and both
  search boxes read it.
- `scripts/smoke_live.py` fetches `GITHUB_URL` (its own request, never
  the stubbable `fetch`; unreachable is a notice, a reachable 404 is
  red) — pannellum: four spellings of `dash-pannellum` for the repo
  `dash_pannellum`, a live 404 the profile-vs-repo framing never caught.
- `pages/api.py` yields when a docs page owns `/api` (pannellum,
  muicharts serve it as a `.. kwargs::` page with curated prose) —
  read from the docs' frontmatter, since page modules load before
  `pages/markdown.py`.
- `assets/main.css`: `.m2d-block-props table` joins the scrolling-table
  rule (a fork's `.. props::` directive stamps the wrapper; the rule
  must match the table).

### Changed
- `pages/changelog.py` accepts `-`, `–` and `—` between version and
  date (leaflet's em-dash headings rendered every version dateless),
  bare or bracketed versions, and prose-first releases — paragraphs
  under a version heading become a `Notes` section of `para` items
  (pannellum's `## 2.0.0 — 2026-08-02` releases rendered eight empty
  headings, silently).
- `tests/test_traffic_rollup_v4.py` builds its read rows THROUGH
  `AnalyticsTracker.record_read` from a classify()-shaped event
  (leaflet, note 61): the stored row carries only the package's
  `EVENT_FIELDS`, which on 2.8.0 lacks `vendor_class`, so every host's
  rollup has been sending `class: null` while the hand-built fixture
  asserted "training". The pin follows the seam (`CLASS_ON_THIS_PACKAGE`)
  and a new test asserts the row shape; dimll 2.9.2 adds the field and
  the pin flips with it. `vendor_rows` keeps its fallback-free semantics.
- `components/header.py` reads `HEADER_HEIGHT` instead of a literal 70.
- The aside pin names only template-owned TOC-less pages (`/changelog`,
  the admin pages); a fork may serve `/` or `/api` as a docs page with
  its own toc (muicharts). `tests/test_seo_icons.py` counts the
  changelog's newest dated heading and `/api`'s `generated` stamp as
  declared dates.
- Item 13 gains the owner step a template cannot see in itself: the
  repo's Actions default workflow permission must be "Read and write"
  or it caps the promote job's `contents: write` — muischeduler's first
  promote failed there with a green matrix and `verify` correctly
  skipped; detect via `gh api …/actions/permissions/workflow`, remedy =
  the setting + re-run, never a PAT or a force push. The promote step's
  comment in cd.yml says the same.
- Item 12/15/16 detects and wording: `EXCLUDED_LINKS` / `_DIMLL_FLOOR`
  spellings, "any in-process probe that sends no UA", "every tool that
  asserts a ClaudeBot stanza", and `components/header.py` is never
  cargo. Item 16 notes: count canonical/meta ELEMENTS, never
  substrings (the template's browser document: one element, three
  substring hits — a comment and a script selector; note 63).
- `test_resources_are_third_party_only` bans the owner's links only;
  an upstream project on GitHub is allowed (contract 5 requires it).
- `tests/test_nav_contract.py`: the API pin branches on `API_PACKAGES`
  (declared → `/api` registered, in the sidebar, components from
  `metadata.json`; none → no `/api`); the aside pin and
  `tests/test_excluded_links_hidden.py`'s positive control derive their
  pages from the registry instead of naming `/backend-comparison` and
  `/getting-started` — both files are fork-invariant now.
- Item 15's detect anchors to the line start (`^\s*block_ai_training=True`)
  so a comment documenting the flag no longer fires it; item 16 notes
  name muischeduler's nine byte-identical files as next round's cargo
  candidates. Tests 438 → 450.

## [1.6.40] - 2026-08-30

Two fleet-class findings from muischeduler's item-12 port, both checked
against this tree.

### Fixed
- `scripts/network_smoke.py`: the battery's default `UA` names the
  browser lane first — a Chrome/AppleWebKit token, then the internal
  token, then " network-smoke". At dash-improve-my-llms ≥ 2.8 the old
  bare-internal-token UA classified as a crawler, so every default-UA
  check read the prerendered crawler document; muischeduler's own
  manifest and og:image checks went red in CD's verify job when its
  floor moved. This template never went red only because its battery
  has no browser-document check on the default UA (its default-UA
  checks read healthz, llms.txt, robots and sitemap, crawler-lane
  surfaces regardless) — the lane was still wrong. Measured at 2.8.0:
  the new UA is `browser`, `INTERNAL_UA_TOKEN` is still a substring so
  the tracker drops it, `CRAWLER_UA` untouched. `scripts/smoke_live.py`
  already had this shape. Pinned in `tests/test_network_smoke.py`.

### Recorded, no change
- No og:image / twitter:card / twitter:image augmentation exists in
  this `run.py` (Dash emits them per page; `templates/index.html`
  declares only the auxiliaries and the one exempted static
  `twitter:card`). muischeduler's duplicate is fork-local (its
  divergence 8); sync item 17 tells forks how to check theirs.
- Wording notes folded into items 9, 12, 13 and 15 from the first fork
  reports: CI may pin the floor more than once (grep the number); tests
  that bypass conftest's `get()` via `app.server.test_client()` send no
  UA and land on the crawler lane; 1.6.33-block forks take the newer
  kit-test bytes on the one-hunk item-13 conflict; item 9 is a
  measurement pass, never a copy.
- `sync/SYNC-1.6.22-1.6.38.md` → `…-1.6.40.md`, item 17. Tests 437 → 438.

## [1.6.39] - 2026-08-30

The visual pass on 1.6.38 (ops seat in the owner's Chrome; contract
met, four notes). Fix-forward, same round.

### Fixed
- `/changelog` (and every page that renders no `.. toc::` — home, `/api`,
  the admin pages) is full width: `lib/aside.py` records which endpoints
  fill the aside and a callback on `url.pathname` collapses the
  AppShell's aside column elsewhere. Before, the shell reserved the
  column on every page.
- The mobile drawer is `keepMounted=True`. Measured on the wire at phone
  width: the hamburger's callback fired (`opened` → true, `n_clicks`
  incrementing, the dependency registered) while the drawer content
  never mounted in an unfocused window — a mount-on-open transition the
  nav must not depend on. It also guarantees `#navbar-admin-mobile`
  exists on every load. The owner's "burger does not open the
  navigation" report is taken as the fact; this removes the mechanism
  that can produce it.
- Code blocks no longer widen the page (`assets/main.css`): a flex parent
  with the default `min-width:auto` — Mantine's List item wrapper, a
  Blockquote — refused to shrink below the code's intrinsic width
  (measured: a 959 px document in a 200 px viewport; widest element the
  List itemWrapper around "Replace @server.before_request…" on
  /backend-comparison). Re-measured on the owner's local build at 391
  px after the first rule: the wrapper was constrained but its
  `.mantine-List-itemLabel` child still grew to 887 px — the label is
  constrained too; the `.. kwargs::` prop table carries
  `m2d-block-kwargs`, not `m2d-table`, and joins the scrolling-table
  rule (a 457 px table on /examples/directives); and `/changelog`'s
  bullet rows get `min-width: 0; overflow-wrap: anywhere` so a
  60-character test name in a `code` span breaks instead of pushing the
  row out of its card (a 549 px document); and inline code in prose
  (`code.m2d-codespan`) wraps with `overflow-wrap: anywhere` — the last
  353 px token on /backend-comparison. Verified on the owner's local
  build at 391 px: every page's document width equals the viewport,
  zero overflowing flow elements (13 pages swept in same-origin
  iframes). Public Mantine class names only.
- The Other Apps dropdown has a solid themed background and border in
  both schemes; every PRIMARY app has an icon (piratesbargain.com
  `mdi:pirate`, 2plot.media `mdi:movie-open-play-outline`), and the
  fleet's docs hosts lose their `mdi:web` placeholders.
- Four pins in `tests/test_nav_contract.py`. Tests 432 → 437.

## [1.6.38] - 2026-08-30

Navigation — **uniform where it should be identical, free where identity
matters** (owner design round, 2026-08-30; gates the fleet's 12+13
pushes as sync item 16). The survey found one root cause: the sidebar
was hand-written in `components/navbar.py` — a `page_order` of display
names, an `excluded_links` list inherited from the DMC docs that matched
nothing here, literal sections, the network typed by hand twice — and
every fork edited that file differently or not at all. `navbar.py` is no
longer a file forks edit.

### Added
- `lib/constants.py` navigation block: `GITHUB_URL` (one constant;
  `SAME_AS` reads it), `CATEGORY_ORDER`, `DISCORD_URL`, `YOUTUBE_URL`,
  `YOUTUBE_SUBSCRIBE_URL`, `DMC_URL`, `UPSTREAM`, `API_PACKAGES`,
  `resources()`.
- Other Apps as a top-bar hover menu (`components/header.py`) from
  `lib/network_directory.other_apps_for()` — the registry's `PRIMARY`
  set (2plot.ai, 2plot.dev, 2plot.media, piratesbargain.com,
  ai-agent.buzz; the owner's review of 2026-08-30 — never the docs
  subdomains, which 2plot.dev's catalogue lists) minus this host,
  labelled by domain, icons from a new `ICONS` table keyed by URL.
  2plot.media joins AFFILIATED so the registry stays the source. The
  sidebar's "Pip Components" and "Other Apps I've built" sections are
  gone.
- Admin section, owner-only: `navbar-admin-{desktop,mobile}` filled by a
  callback that returns nothing unless `is_admin_user()` (pip-docs+'s
  pattern); the startup tree carries no `/admin/` href; search lists
  sidebar pages only (never `/admin/*`, never hidden-tier).
- `/changelog` (`pages/changelog.py`): `CHANGELOG.md` as a DMC Timeline;
  the file, minus its H1, is the page's LLMS_DOC. Linked under Home and
  in the footer.
- `components/footer.py` — `AppShellFooter`: © {computed year} Pip
  Install Python LLC · GitHub profile (`GITHUB_PROFILE_URL`; the repo is
  the top bar's icon) · Discord · YouTube, every icon labelled; no
  Changelog link (the sidebar's is the single one), no Terms/Privacy.
- `/api` (`pages/api.py`, `lib/api_reference.py`): one `dmc.Table` per
  exported component from each `API_PACKAGES` entry's `metadata.json`
  (prop · type · default · description); the same tables as Markdown for
  `/api/llms.txt`. Not registered when the list is empty (the template's
  case); tested with `tests/fixtures/fake_dash_pkg`.
- `pages/markdown.py` `Meta.order` (default 1000) → `register_page(order=)`;
  every docs page declares `category:` and `order:`.
- `/admin/traffic`: `dmc.DatePickerInput` day picker (ledger-bounded,
  presets Today / Yesterday / Last 7 days) and a **People** section — the
  day's human hits, visitors, sessions and median session — above the
  crawler ledger, with the line "humans never enter the read ledger —
  the tables below are crawlers only".
- Inline `![alt](src)` images render through markdown2dash
  (`lib/directives/headings.py` `patch_renderer`): the library has no
  image renderer and mistune's fallback raised on DMC children.
- `tests/test_nav_contract.py` (19 pins) and the rewritten
  `tests/test_excluded_links_hidden.py` (admin pages hidden from both
  audiences and the sidebar tree). Tests 413 → 432.

### Changed
- `components/navbar.py`: sections from frontmatter against
  `CATEGORY_ORDER`; `page_order` and `excluded_links` deleted; Resources
  rendered from `resources()` — third-party only: `dmc` and the
  fork's `UPSTREAM` (owner's review, 2026-08-30).
- `components/header.py`: GitHub icon → `GITHUB_URL`; `dmc.Burger`
  `aria-label`; version badge from `API_PACKAGES[0]` when declared;
  search data from `navbar.search_data`.
- `pages/home.py` renders through markdown2dash, not `dcc.Markdown`
  (the fleet's no-`dcc` rule); `lib/directives/source.py` sets
  `copyLabel`/`copiedLabel`.
- The template's docs are five short sections: Getting started ·
  Backends · Content · Network · Auth.
- `sync/SYNC-1.6.22-1.6.37.md` → `…-1.6.38.md`, item 16 (contract now;
  names the files that become cargo next round).

### Recorded, no change
- Two places the design did not fit the tree: an `icon` field on the
  registry entries breaks `register_network` at boot (the package
  forwards every key) — icons live in `ICONS` keyed by URL; and Dash 4
  generated component classes carry no `_prop_names` — `metadata.json`
  and the docstring are the sources. Both are in item 16's contract.
- No `dcc.` remains in `pages/` or `components/` except `Location` and
  `Store`.

## [1.6.37] - 2026-08-29

Round 3.4 — **the posture flip.** Owner decision, 2026-08-29: AI-training
crawlers are allowed by default, because the ledger now records and
reconciles every read (boilerplate 534 == 534 against the wire). The
wall decided by vendor class what nobody could account for; a read
that is a row is priceable, and the tool from here on is per-vendor
policy, not the class. Canary: boilerplate + llms; the fleet via sync
item 15; clerkhook keeps its wall by design.

### Changed
- `run.py`: `RobotsConfig(block_ai_training=False, …)`; the comment
  block says why, and shows the per-vendor line
  (`vendor_policy={"bytespider": "block", "gptbot": "meter"}`) that
  replaces the class wall.
- The robots.txt fingerprint of ClaudeBot flips to `Allow: /` in
  `tests/test_llms_routes.py`, `scripts/smoke_live.py` and
  `scripts/network_smoke.py` — that line now fingerprints the POSTURE;
  OAI-SearchBot / Claude-User / Claude-SearchBot still fingerprint the
  artifact.
- `DIVERGENCES.md` posture fence: the interim measurement, dated with
  both UAs (2026-08-29T23:49Z, build ecc66f8: `/` 403, `/llms.txt`
  200, `/healthz` 403 — identical for ClaudeBot and GPTBot, in-process
  and on the wire). Two walls produced it: the app's (retired here) and
  the edge's (a Cloudflare rule on `/`, the owner's, narrowed after
  this release is verified on the wire). Expected after both:
  200/200/200; the block is re-measured and re-dated then.
- `sync/SYNC-1.6.22-1.6.36.md` → `…-1.6.37.md`, item 15.

### Recorded, no change
- Landed and measured on the wire (2026-08-30T00:09Z, build 700a170): ClaudeBot and
  GPTBot both 200/200/200 on `/`, `/llms.txt`, `/healthz`, robots.txt
  with no Disallow for either, and NO Cloudflare edit — the "edge wall"
  the drop framed was never observed on this host; every 403 was the
  app's. The fence, item 15 and this entry are corrected to say so;
  the owner is checking whether any zone rule exists at all.
- The robots.txt shape after the flip is no training stanza at all
  (GPTBot/ClaudeBot under `User-agent: *`), so the three fingerprint
  sites assert "no Disallow", not "Allow: /".

## [1.6.36] - 2026-08-29

What the first wire round taught the block. Spec, kit test and README;
the only test code that moves is the v4 rollup cargo test, made
v3-agnostic — no runtime code. Two findings, both clerkhook's
(2026-08-29, seat-verified): a live fan-out would have dropped
`tests/test_traffic_rollup_v4.py` and `tests/test_analytics_classifier.py`
at `tests/` root, where that fork's PACKAGE suite lives (its matrix
would ERROR, not skip), and the v4 test asserted v3 seams
(`load_agent_hits`, `bot_visitors`) that the fork — v4 without v3 —
does not have. The fence grammar could not express "I decline this
cargo", because the kit test required every fenced path to exist.

### Added
- `- <path>  # declined: <reason>` in the byte-owned fence
  (`sync/README.md` fork-fences section): the fork refuses this cargo.
  The only fence entry that may name a path absent at HEAD; the reason
  is mandatory; a spec's own block cannot carry one. `_machine_fence`
  in `tests/test_claude_kit.py` accepts it, and three new cases pin it
  (declined-missing validates; plain-missing still fails; bare
  `# declined` fails; a spec block cannot decline). The machine half
  already existed — `scripts/fanout.py` skips every path DIVERGENCES
  names; the ops seat adds the declined-entry test there.
- Posture key `unknown_ai: allow | meter | block` — the host's
  `default_unknown_ai`; dimll 2.9.0 widened "block" to absent and
  unrecognised UAs, which makes the value a posture a probe can see.
  `_POSTURE_KEYS`/`_POSTURE_ENUMS` extended; the template's own fence
  declares `unknown_ai: allow`.
- Kit trap: headless browsers are crawler-lane from dimll 2.9.0 —
  measured on the 2.9.0 wheel: `HeadlessChrome/…` and a Playwright UA
  classify `lane: crawler, bot_type: monitor, vendor_key: headless`
  (2.8.0 says browser). A host that screenshots itself for social
  cards gets the crawler document unless its screenshot service sends
  a non-headless UA. Item 8's notes point at it.
- `tests/fixtures/rollup_pre_v3.py` (clerkhook's rollup shape: no
  `load_agent_hits`, no `agent_visits`, no `bot_visitors`) and
  `tests/test_rollup_v4_is_v3_agnostic.py`, which runs the cargo test
  against it in a subprocess (`ROLLUP_V4_MODULE`). Green in this suite
  means the cargo is safe on every rollup shape the fleet has.
- `sync/README.md`: the dead-cargo rule (block rules) and the
  one-session-per-tree authoring rule (a sub-agent must not edit
  files its parent also edits; the completion signal is the report,
  never an idle notice).
- `sync/SYNC-1.6.22-1.6.35.md` → `…-1.6.36.md`, item 14.

### Changed
- `tests/test_traffic_rollup_v4.py` asserts only v4: `vendors[]`,
  `reads`, their shapes, and that every non-v4 key is identical with
  and without reads. `daily_rollup(app, day)` with the ledger in the
  env is the one call shape every version accepts; the
  `load_agent_hits` import and the `bot_visitors` assertion are gone.
- Item 12's fence note corrected: the question was never "does it
  import anything fork-shaped" but "does it pass against the OLDEST
  fork's rollup". Grep of the 12 local fork clones: clerkhook is the
  only pre-v3 fork; the other 11 carry v3.
- Item 9's key list names `deploy` and `unknown_ai`.

### Recorded, no change
- Dead cargo, first instance: `scripts/smoke_live.py` on clerkhook —
  611 lines, referenced by nothing, asserting content IS served on a
  host whose posture denies every surface (its DIVERGENCES §6 names
  `scripts/lockdown_smoke.py` as the inversion). Remedy = delete it +
  a `# declined:` entry; a clerkhook session action (item 14), not
  done here. Same fork: its site tests already live under
  `tests/site/`; the two item-12 cargo tests at `tests/` root are to
  be declined there.
- The floor stays ≥2.8.0. 2.9.0 is not required this round: nothing
  here depends on its behaviour — the `unknown_ai` key is a posture
  declaration and the headless trap is a warning; a host on 2.8.0
  simply has no headless lane yet. The floor moves when a release
  needs 2.9.0's routes, not its registry.

## [1.6.35] - 2026-08-29

Pipeline and docs only — no runtime code moves. **Render deploys
`release`, and only CD writes `release`** (owner decision A of
2026-08-29, chosen over hook-only and branch protection). The
measurement: 14:12Z that day, de0bcff was pushed to main; Render,
watching main, built it within the minute; cd.yml run 33256965081 went
red at 14:13Z with the deploy job skipped; `/healthz` served the red
build for ~6 minutes until acc3651. CI could not stop a deploy because
the platform watched the same branch CI was still judging. Auto-deploy
stays exactly as it is — it now watches a branch that only ever holds
certified commits.

### Changed
- `.github/workflows/cd.yml`: the `deploy` job (still `needs: [test]`
  — that is the gate) checks out and runs "Promote to release":
  `git push origin HEAD:refs/heads/release`, the run's own sha,
  fast-forward, never forced — a non-fast-forward means somebody wrote
  `release` by hand and the job fails and says so. Job-level
  `permissions: contents: write` on `deploy` only; the workflow stays
  `contents: read`. Guarded with `if: github.event_name == 'push' ||
  inputs.target_url == ''` so a verify-only dispatch against another
  host never moves the ref (the hook step had no such guard). The
  build-match wait is unchanged. First run creates the branch.
- `render.yaml`: `branch: release`, autoDeploy left unset (on).
- `DIVERGENCES.md` posture fence gains `deploy: release-branch`
  (absent reads as main); `tests/test_claude_kit.py` `_POSTURE_KEYS`
  admits it.
- `.claude/CLAUDE.md`: the trap — `build == HEAD` on `/healthz` means
  HEAD of `release`; `main` ahead of `release` is an uncertified push
  pending, never drift, never a hand deploy.
- `sync/SYNC-1.6.22-1.6.34.md` → `…-1.6.35.md`, item 13 (contract:
  every fork's cd.yml differs in host, timeouts and comments — 12 of 12
  measured — so nothing rides the block).
- Tests: +7, `tests/test_cd_promotes_release.py` — parses cd.yml and
  render.yaml and pins the structure (needs, the unforced push, the
  dispatch guard, the job-only write grant, the hook's absence, the
  branch, the fence).

### Removed
- The Render deploy-hook step and its secret from cd.yml. A
  `RENDER_DEPLOY_HOOK_URL` repository secret is now inert and safe to
  delete (owner; dashboards are out of a session's reach).

### Recorded, no change
- Fix-forward, same version (ops finding on run 33262495272): `verify
  the live site` ran and reported GREEN on a run whose promote step had
  FAILED — its `if: always() && != 'cancelled' && != 'skipped'` admitted
  `failure`, so it smoke-tested the previous build. Now
  `if: needs.deploy.result == 'success'`, and verify's first step asserts
  `/healthz build == github.sha` itself (also catches a promote that
  succeeded while Render's build did not). Pinned.
- Fix-forward, same version: the promote checkout is `fetch-depth: 0`.
  Run 33262495272 (747d8b3) failed "Promote to release" in one second —
  a depth-1 clone pushing onto an EXISTING `release` is rejected as
  non-fast-forward ("fetch first"), because a shallow history cannot
  show the remote that release's tip is an ancestor. ea4e104's promote
  passed only because it CREATED the branch. Reproduced locally
  (depth-1 rejected, `--unshallow` lands); pinned in
  `tests/test_cd_promotes_release.py`. That failed run is also the
  dashboard proof: with Branch = release, main moved and neither
  `release` nor the wire did (36 samples over 7 min, ops seat).
- Dashboard Branch set to `release` for boilerplate-2plot-dev by the
  owner, 2026-08-29 (after the first promoted run showed Render had
  built ea4e104 from main). This entry's own push is the road's proof
  — see the ops report for its three timestamps.
- Owner step, named not assumed: if the Render service is not
  Blueprint-managed, the dashboard's Branch field is the switch, not
  render.yaml. The first promoted run cannot distinguish the two from
  the wire (main and release hold the same sha); the next red push on
  main can. A `branch` field on `/healthz` from `RENDER_GIT_BRANCH`
  would make it one read — a runtime change, proposed, not done.

## [1.6.34] - 2026-08-29

The ledger round — the template half of the network's ledger plan
(`PLAN-ledger-and-corpus-2026-08-29`: *the ledger is the asset, not the
wall*). dash-improve-my-llms 2.8.0 now produces the ledger's key
(`classify()`) and its row (`on_document_read`); this release makes the
app the first thing that KEEPS the row, and the first place a host's
bot accounting can be checked against its own wire. Nothing new leaves
the host: the reporter POSTs the same endpoint with two more keys the
hub ignores until round 3.3. No hub change, no posture change.

**The finding, dated 2026-08-29.** `lib/analytics_tracker.py` was the
fleet's fourth classifier, and it was wrong about the vendor the whole
plan is written around: its search list named `claudebot` — Anthropic's
*training* crawler, which the package's registry has said since 2.3.3
and this repo's own `run.py` comment said six lines from where the list
ignored it — and still carried the retired `anthropic-ai` /
`claude-web` tokens. `device_type == "bot"` decided `human_hits`, and
it was set from that list, so an `httpx`, `Go-http-client` or UA-less
request was a *human* in every rollup the hub has ever received. Every
host in the fleet reported those numbers.

### Added
- `AnalyticsTracker.record_read` and the ledger's second table:
  `run.py` registers it with `on_document_read` (once; guarded against
  the suite's repeat imports) and every corpus document the package
  serves lands as a row in `reads` in the same `visitor_analytics.json`
  — every `_ledger.EVENT_FIELDS` key verbatim plus `kind: read`, same
  buffer, lock, flush cadence and retention as `visits`; `client_ip`
  dropped unless `ANALYTICS_KEEP_CLIENT_IP=1`. A pre-1.6.34 ledger has
  no `reads` key and reads as empty. `reads` is a second table joined
  by the rollup, never summed into `human_hits` / `bot_hits` / `pages`.
- Rollup v4 in `lib/traffic_rollup.py`, additive and present only on a
  day with reads: `vendors[]` — one row per `(key, verified, policy)`
  with `class`, `hits`, `bytes` and a seven-key `tiers` map from the
  package's `TIERS` tuple; the null-key row (the unidentified crawler
  lane) is kept on purpose; sorted by hits, capped at 40 — and
  `reads: int`, the reconciliation total. `load_reads()` and
  `vendor_rows()` are the new seams; `daily_rollup(..., reads=)` loads
  them itself when not handed them, so `lib/satellite_reporter.py`
  changes nothing. Every v3 key byte-identical; `tests/test_traffic_rollup.py`
  passes unmodified.
- `pages/traffic.py` — `/admin/traffic`, the host's own ledger behind
  the control board's exact gate (fails closed without Clerk;
  `ALLOW_UNGATED_ADMIN=1` locally; `mark_hidden` at import): vendor ×
  day with a bytes column, vendor → tier and top paths per vendor for a
  picked day, the v3 headline numbers for the same day, and the line
  that says `n/a` means the operator publishes no ranges (Anthropic
  does not; ClaudeBot is always `n/a`). Plain tables, no charts, one
  dropdown — fleet fact 18.
- `.claude/CLAUDE.md`: the ONE-classifier trap.
- `sync/SYNC-1.6.22-1.6.33.md` → `…-1.6.34.md`, item 12 (class
  contract, with `tests/test_analytics_classifier.py` and
  `tests/test_traffic_rollup_v4.py` as the block's cargo — the two that
  import nothing fork-shaped).
- Tests: 372 → 401. `test_analytics_classifier.py` (each pin a UA from
  the wire, plus the grep that fails if a hand-written list comes
  back), `test_read_ledger.py` (the real app: one `GET /llms.txt` from
  GPTBot → exactly one row with tier/lane/vendor/verdict/status/bytes
  and no `client_ip`; a Chrome `GET /` → none; the hook registered
  once; a raising writer warns and the response is unchanged),
  `test_traffic_rollup_v4.py`, `test_traffic_page.py` (hidden from the
  sitemap and llms.txt, denied identically to the board, and a 3-vendor
  × 2-day fixture whose cells are asserted as numbers).

### Changed
- dash-improve-my-llms floor **2.7.1 → 2.8.0** in every encoding
  (`requirements.txt` × 4, `run.py`'s `LLMS_PKG_FLOOR` and its
  diagnostic; `tests/test_config.py` reads the boot floor). Why 2.8:
  one classifier, the read event, `Vary: User-Agent`, verified vendor
  identity. 2.8.1 (the resolved `policy` on every event) is NOT waited
  on — `policy` is `None` until then and the rollup groups it as
  `"default"`.
- `lib/analytics_tracker.py` delegates: `is_bot` and `detect_bot_type`
  keep their names and signatures and their bodies are `classify()`;
  `track_visit` classifies once, after the real client IP is resolved,
  and crawler rows gain `vendor_key`, `vendor_class`, `verified`,
  `lane`. Human rows are unchanged byte-for-byte. The module carries
  zero User-Agent strings. Tokens the old list had that the registry
  lacks — `headlesschrome`, `phantomjs`, `monitoring`, `uptime`,
  `pingdom`, `better-uptime` — are a pushback to the package seat,
  named in the 1.6.34 report, not a list kept here.
- **Reporting consequence:** `human_hits` drops and `bot_hits` rises
  on every host that adopts this, because UA-less and library clients
  move from human to crawler (and an empty UA is a bot now, where it
  used to be a desktop human). That is the number becoming true, not a
  regression; the hub's day-over-day view will show a step on adoption
  day.

### Fixed
- (follow-up commit, same version — `de0bcff` went red in CD and Render's
  autoDeploy shipped it anyway, uncertified.) `tests/test_proxy_scheme.py`'s
  end-to-end tag test sent NO User-Agent; under 2.8.0 an absent UA is the
  crawler lane, so it received the crawler document — which has no
  `twitter:url` at all — and failed on "no tag" on every Flask leg
  (green on 2.7.1; it passed the template's local 3.11 run only by test
  ordering). It now names the browser lane. The mirror of the kit's
  machine-lane trap: either lane can be the one you did not mean to
  test. Also three flake8 F401s in the new files.
- Nothing else — the classifier finding was never a bug by its own
  lights; it is a Changed.

### Recorded, no change
- In-process (test client, no client address) the package cannot check
  GPTBot's published ranges and says `verified: n/a`; on the wire the
  same request is `verified` / `unverified`. The drop's acceptance
  named the pair; the tree pins the triple and says why.
- `DIVERGENCES.md`'s posture fence is unchanged: `/` still answers 403
  to training UAs. The flip is round 3.4, the owner's.

## [1.6.33] - 2026-08-27

A correction release: no behaviour changes, no test changes, no
change to what the sync block carries. What changes is what the
documents TEACH, and it lands ahead of the fan-out that carries item
11, because that item was about to teach two forks a mechanism that is
false. **Scope note, per the drop that requested this one:** its §4
asked whether the middleware should survive the package fix, and said
a code change would be a legitimate expansion. It did not become one —
the answer is "keep it", so the change is the docstring that says why.
Comments and docstrings naming the wrong layer were corrected in five
files; not one line of executable code moved.

**It is FastAPI, not Starlette.** Every document here said Starlette
registers only the methods a route declares. It does not:
`starlette.routing.Route.__init__` ends with
`if "GET" in self.methods: self.methods.add("HEAD")` — the same
courtesy Werkzeug extends. `fastapi.routing.APIRoute` is the class
that takes `methods` literally and adds nothing. Both statements
verified in the installed source (starlette 1.1.0, fastapi 0.141.1).
Two seats and three probes reached for the wrong layer on this, which
is reason enough to state the true one precisely once: a fork that
reads "Starlette does not derive HEAD" searches the wrong package, and
may conclude a bare-Starlette mount is affected when it is not.

**The population was seven hosts, not two.** Item 11 named pannellum
and muischeduler. The ops seat's wire sweep of 2026-08-27/28 found the
hub (2plot.ai) had the defect too — it was never in the item's
population — plus four second-ring sites the fan-out does not reach:
piratesbargain.com, ai-agent.buzz, 2plot.xyz and cast.2plot.net. They
are named in the notes as known-affected-reached-by-a-drop, because
notes that stop at the fan-out's edge read as "these two hosts" when
the truth is "every ASGI host in the network, and we know which."

**The middleware stays after the package fix, and this tree measured
why.** dash-improve-my-llms 2.7.2 declares `["GET", "HEAD"]` on its
own doc routes, which removes one reason for `HeadAsGetMiddleware` and
not the others. `/` is served by Dash's page catch-all, and *every*
Dash route is a FastAPI `APIRoute`:
`dash/backends/_fastapi.py::add_url_rule` calls
`add_api_route(..., methods=methods or ["GET"])`, with the catch-all
registered `methods=["GET"]`. Re-measured in-process with the
middleware removed: 10 of the 11 pins red, the single green being
`HEAD /` with a *crawler* UA — the prerender answering before the
router. The same path with a *browser* UA is 405. Nothing in this repo
or in the package can declare methods on Dash's routes.

### Changed
- `sync/SYNC-1.6.22-1.6.32.md` → `sync/SYNC-1.6.22-1.6.33.md`. Item
  11's `contract:` carries the corrected layer and the reason to get
  it right; its `notes:` carry the seven-host population, the
  middleware's permanence with the Dash measurement behind it, and an
  upstream item that is now Dash's rather than the package's.
- Item 10's `notes:` gain the hub as a **fourth** red and the shape
  lesson under it: a hand-declared `/healthz` drifts from the fleet
  shape silently, and a package floor can make a key *impossible*
  rather than merely absent. Different states, different remedies,
  and only one of them is a divergence.
- `.claude/CLAUDE.md`'s HEAD trap: the layer corrected, the population
  widened to every ASGI host, and the "keep the middleware" note so
  the next floor bump does not delete it.
- Comment/docstring corrections in `lib/asgi_middleware.py`,
  `tests/conftest.py`, `tests/test_head_method.py`,
  `scripts/network_smoke.py`, `scripts/smoke_live.py` — the same false
  sentence, five times, in the files a fork reads while porting.

### Recorded, no change
- Item 10's red list disagrees with its own dated table on two rows
  (`llms` missing `python` on 08-27; `pipdocs` missing `backend` on
  08-28, with no llms row). Both are written down, neither is
  reconciled here — the spec says to re-measure rather than pick.
- 1.6.32's "empty body" is read as **the wire is empty**, never as
  "your adapter empties it": Werkzeug's response, httpx's ASGI
  transport and h11 under both servers each drop it, and h11 raises if
  a server forwards one. The package seat declined to assert emptiness
  in its adapters for that reason and was right.

## [1.6.32] - 2026-08-27

A defect release, and one this template shipped to two forks itself.
**`HEAD` returned 405 on every route of both FastAPI hosts** —
pannellum and muischeduler, measured on the wire — `/healthz`,
`/robots.txt` and `/sitemap.xml` included. Werkzeug derives a HEAD
rule from every GET rule; Starlette does not, so every route declared
`@router.get(...)` answered "method not allowed" to the method most
uptime monitoring probes with, against the two hosts whose deploy
proof IS `/healthz`. Neither fork did anything wrong: they inherited
it by choosing the backend this template ships.

It hid perfectly. CI never issued a HEAD, both live tools GET (which
is the standing rule, and this defect is why the rule exists), and a
browser never sends HEAD for a document. The one in-process probe that
did run HEAD — 1.6.31's, checking whether the ASGI lane lost the
`Link` headers — ran it against `/`, which is the single route that
answers, because the package's prerender middleware replies before the
request reaches the router at all. True observation, wrong conclusion,
twice over: a 405 carries no `Link` header either.

### Added
- `lib/asgi_middleware.py` — `HeadAsGetMiddleware`, pure ASGI, added
  last so Starlette runs it outermost: a HEAD request is re-dispatched
  as GET and answered with the same status and headers and an empty
  body. Middleware rather than `methods=["GET", "HEAD"]` on the
  declarations because this tree declares only two of the affected
  routes — `/llms.txt`, `/<page>/llms.txt`, `/robots.txt`,
  `/sitemap.xml` and the policy panel come from
  dash-improve-my-llms' own FastAPI adapter (GET-only; only the root
  icon paths declare HEAD) and `/` from Dash's page catch-all. Fixing
  what we declare would have left three of the four crawler-facing
  surfaces 405ing.
- `tests/test_head_method.py` — status, `content-type` and `Link`
  parity between HEAD and GET on all five core routes, both UAs, per
  backend. Proven the only way it can be: with the middleware removed
  the FastAPI leg fails 9 of 11 and the Flask and Quart legs pass. A
  pin that is green on all three before the fix is testing the test
  client, not the router.
- One check in each live tool — `HEAD /healthz` answers what `GET
  /healthz` answers. One request, and the check that would have caught
  this on the first CD run after either fork switched backends.
- `Client.head()` / `Client.open()` in `tests/conftest.py`, so the
  method is a first-class question across all three test clients.

### Changed
- `scripts/smoke_live.py`'s `fetch` grows a `method` keyword — used by
  exactly one call site, and every other one still GETs. This is
  1.6.29's wake() hazard verbatim: twelve fixed-signature `fetch`
  stubs in `tests/test_smoke_live.py` had to grow `method` in the same
  commit, and `tests/test_network_smoke.py`'s stub asserted
  `method == "GET"` outright — it now names the one path allowed to
  differ rather than dropping the guard. Forks port the check and the
  stubs together.
- `.claude/CLAUDE.md`: the HEAD trap now carries the measured
  mechanism (nothing answers HEAD on the ASGI lane) in place of the
  1.6.31 text (the ASGI hosts drop the `Link` headers, cause open),
  and warns off both false verifications — one Flask host, and
  `HEAD /` with a crawler UA. A second trap generalises the certifi
  habit: any throwaway probe a session writes against production needs
  the SSL context and a retry guard, because fixing the shipped tools
  does not cover the next ad-hoc script.
- `sync/SYNC-1.6.22-1.6.31.md` → `sync/SYNC-1.6.22-1.6.32.md`, gaining
  item 11 (HEAD answers wherever GET answers; conditional on a
  non-Flask backend, `already-present` on a Flask fork — run the
  detect anyway, the answer records which lane the fork is on).

### Fixed
- Quart was measured, not assumed, and needs nothing: all five core
  routes answer HEAD 200 there. Its test client returns the body where
  Werkzeug's and Starlette's strip it, which is the client — h11,
  under uvicorn and hypercorn both, frames a HEAD response as
  content-length 0 and never writes those bytes.

## [1.6.31] - 2026-08-27

What the F4 round taught, most of it arriving as fork pushback the ops
seat adjudicated and accepted. The headline is a retirement: "byte-copy
the template's current file" stops being the recommended port for
`scripts/smoke_live.py`, because three forks contradicted its premise
independently — the file's CONTENT is fork-owned on at least three
hosts, not just its interface. A copy deletes measured checks silently
(green: a deleted check does not fail, it stops being true) or asserts
a posture the host deliberately does not have. Diff and port; copying
is safe only when the diff is empty in both directions.

Two more things this release stops being able to hide. `/healthz` is
read by four different machines BY KEY NAME, and a thirteen-host read
found one fork answering `dash` where the battery asks for
`dash_version` — reporting the Python item green, correctly, while
being invisible to every reader. And spec item 7, the configured gate
page, has been `open` here for three releases while four forks
reported it `open` for the same reason and rightly declined to invent
a shape; the template owed the reference and now has one.

### Added
- `tests/test_healthz_shape.py` — the payload's KEY SET is a fleet
  contract (`app backend build dash_version geo ok python`). Extras
  are always fine; a rename is the failure this pins, because it is
  invisible to every check that reads a value rather than a key.
  Checks the builder AND the live route (a typed response model that
  drops a field leaves the builder green), and `build` the only
  honest way: set `RENDER_GIT_COMMIT`, assert the key appears.
- `tests/test_gate_configured.py` — spec item 7 adopted here at last.
  Renders a real registered page, pinned to `auth` through the control
  board's own writer, with three FAKE non-empty `CLERK_*` values, and
  asserts the sign-in card rendered — the branch production serves and
  no test had ever reached, since every battery in this fleet boots
  zero-secret. The card's markers are read off `lib/gate_layouts.py`
  by rendering its own card, never re-typed. Its second test is the
  non-vacuity control (same page, zero-secret, serves the CONTENT —
  the documented fall-open); its third pins `admin` closed in both
  postures. `conftest.py` is unchanged: `clerk_enabled()` reads the
  environment per call, so `monkeypatch.setenv` was enough.
- Spec item 10 — `/healthz` declares the fleet's shape, with the
  three current reds and each one's remedy.
- `sync/README.md` gains a section on the fork's OWN fences
  (`byte-owned`, `posture`): grammar, absence-vs-empty, and the rule
  that content you ported rather than copied goes in the byte-owned
  fence in the same touch. The fence had been validated by the kit
  test since 1.6.22 and documented nowhere — every fork's was empty,
  so nothing had ever exercised the format until flows put a path in
  one (flows).

### Changed
- Sync spec renamed `SYNC-1.6.22-1.6.30.md` → `SYNC-1.6.22-1.6.31.md`.
  Nothing new rides the block and no cargo file's bytes change: both
  new tests call into fork-owned modules, which the mirror rule makes
  contract, not cargo.
- Spec item 6's contract: **diff, do not copy**, with the three
  contradicting hosts named — flexlayout (six fork-added check blocks
  a copy would delete), leaflet (its open-training posture, same
  shape, unfenced), muischeduler (the template's `ClaudeBot ->
  Disallow: /` assertion FAILS on its deliberate
  `block_ai_training=False`). The tolerant `wake()` stays and its
  claim is narrowed to what it buys: a stale-stub landing degrades to
  the fork's old red checks instead of a suite-wide TypeError. Its
  notes gain the fence rule and the measurement behind it — three of
  the four forks with fork-owned content fence the path; leaflet does
  not (ops seat, eleven public forks, 2026-08-27).
- Spec item 8's `files:` names `tests/test_social_card.py`, and its
  notes name the expected red the way 1.6.26 named the DEMOS red:
  the static `name="twitter:card"` trips the fork's own
  no-static-duplicate sweep, and the fix is writing the exemption
  into that test, never deleting the tag you just added (pannellum
  and modelviewer, independently). `files:` is a scope statement; one
  that omits a file the body requires teaches sessions to distrust it.
- The block's SEQUENCING note is struck. `scripts/fanout.py`
  implemented all three gate forms on 2026-08-26 — before the last
  round ran — while the note kept telling every fork session the
  fan-out was unsafe.
- `.claude/CLAUDE.md`, two traps. "GET, not HEAD" is now stated as
  what it is: a BACKEND-level divergence (ten Flask hosts serve the
  `Link` headers on HEAD, both FastAPI hosts drop them), so verifying
  it false on one host proves nothing — excalidraw was right about
  its own host and wrong about the rule. Where the loss happens is
  recorded as still open: this repo's in-process probe gets both
  `Link` headers on HEAD on both backends, so the app code is not it.
  And the UA-less-curl counter-observation is marked unconfirmed —
  muischeduler filed the same note and retracted it.

### Fixed
- `scripts/smoke_live.py` fetched the home page twice in sections 2,
  3 and 3c: every loop prepends `/` and this fleet's sitemap lists
  `/` first. Filtered once at the sitemap parse rather than at three
  call sites. The waste was minor; the reason it is pinned is that
  two checks emitted the SAME label, so one failing home page printed
  two identical FAIL lines and read as two broken pages (flexlayout
  reported 3c; it was all three).

## [1.6.30] - 2026-08-27

The F4 battery's first round, closed by two §A fork sessions
(emojimart f6da429, muicharts 9c4985e) that corrected the ops seat's
diagnosis the same way and found fleet-class gaps on the way. Two
lessons carry: a green suite proves nothing about a file NOTHING
exercises — where 1.6.29 diagnosed the loud failure (a legacy stub
TypeErrors), the quiet one is a fork with no `tests/test_smoke_live.py`
at all, where the byte copy landed green and CD against production
was the first thing ever to run the script — and identity that is
authored twice drifts, which is why the browser head and the crawler
head disagreed on six of seven audited hosts.

### Changed
- Sync spec renamed `SYNC-1.6.22-1.6.29.md` → `SYNC-1.6.22-1.6.30.md`.
  Nothing new rides the block; what changes is what the items ask.
- Spec item 6 now names **both** live tools (`scripts/smoke_live.py`
  and `scripts/network_smoke.py`) and grows a fourth detect question:
  does `tests/test_smoke_live.py` exist at all? Absence is
  NOT-ADOPTED, never not-applicable. Its 1.6.29 note claiming
  emojimart and muicharts "matched signatures" was wrong — neither had
  the test — and the item now names, per state, what each fork that
  already took the copy must do.
- Spec item 5 corrected three ways: the site lane is declared by JOB
  NAME (not by file), the compat window is *the fleet minor, one
  adjacent minor, and the site's declared floor where it is lower*
  (emojimart's 3.10 leg and muicharts' narrowing are both right), and
  the render.yaml pin compares the MINOR because Render resolves the
  patch itself (muicharts asked 3.14.7, was served 3.14.3).
- Spec item 3's `files:` line now names the 1.6.26 docstring paragraph
  in `lib/auth_demos.py` alongside the entry (pannellum): a fork whose
  copy still says the table "ships EMPTY" describes a template that
  stopped existing at 1.6.26.
- Spec item 1's retirement note: the SUPERSESSION class is not retired
  with the item — dispatch lag and two pushes in one window reach the
  same state with no bot anywhere. Same correction in the kit
  CLAUDE.md trap.
- `sync/README.md`: the who-stubs-this rule gains its mirror — **what
  does this call into?** — and a new rule, that a file LEAVING the
  block must be accompanied by the forks it already landed on and what
  each must do (removal stops the next fan-out and undoes nothing).
- `.claude/skills/wire-verify/SKILL.md` step 3 names a crawler UA
  instead of relying on curl's default. Which lane answers is the
  package's UA classification, not the absence of a UA.
- Kit CLAUDE.md gains four traps: a failed STEP in a
  `continue-on-error` job is not a failed RUN; never round-trip JSON
  through zsh `echo`; repeated HTTP headers survive only if you keep
  them (`dict(resp.headers)` and a dict comprehension over `.items()`
  both drop all but the last); name the crawler UA when probing the
  machine lane.

### Added
- Spec item 8 — **the two heads declare the same identity.** New pin
  `test_the_browser_head_declares_the_configured_icons`: the browser
  head's icon links equal `configure_seo(icons=)` as unordered
  (rel, href, sizes) triples, query strings stripped so Dash's
  cache-busting favicon link is not read as a phantom declaration. It
  caught the template itself — `templates/index.html` declared
  `/assets/favicon.ico` while run.py declared
  `/assets/favicon/favicon.ico`, byte-identical files at different
  paths, invisible to the wire-side parity check because that one
  compares the set of SIZES and an .ico declares none. The browser
  link now points at the declared path.
- `test_the_twitter_card_is_a_large_image` tightened to pin both forms
  at exactly one occurrence each. Dash emits `property=`, which
  Twitter's parser does not read; the static `name=` tag is the only
  declaration a scraper sees, which is why it is the standing
  exception to the no-static-duplicate rule — an exception that decays
  in both directions unless pinned on both sides.
- Spec item 9 — **DIVERGENCES.md declares this host's POSTURE.** A
  second machine fence (```yaml posture) with `ai_bots` (path →
  status, measured with a real vendor UA), `healthz`
  (`minimal`|`full`) and `runtime` (`docker`|`python`). The kit test
  validates shape (one fence, known keys, enum values, integer
  statuses) and holds `runtime:` against render.yaml; absence skips,
  empty means template defaults. The hub reads this instead of its own
  seeded table. Measured here 2026-08-27:
  `{"/": 403, "/llms.txt": 200, "/healthz": 403}` for ClaudeBot and
  GPTBot, 200 on all three for a browser.

### Fixed
- `scripts/network_smoke.py` had no SSL context — CI runs it against
  `http://localhost`, so TLS never came up and the omission was
  invisible for six months of releases. From a Mac against a
  production https host it returned 0/12,
  indistinguishable from the site being down (muicharts). Same
  certifi-backed `_ssl_context()` as smoke_live.py and audit_links.py;
  verification stays on either way.
- `tests/test_python_version.py` is job-scoped: `SITE_LANE_JOBS` /
  `PACKAGE_LANE_JOBS` classify every job, the pins read site-lane job
  bodies only, and a new guard fails loudly on any job that declares a
  Python literal and sits in neither set. Until now the greps read the
  whole file while the docstring promised the site lane only — the
  first fork with a package matrix failed on the lane the item
  disclaims. The window rule follows item 5's correction, and
  `SITE_PYTHON_FLOOR` (3.12 here) is pinned against the README's own
  promise so a floor cannot be invented inside the test.

## [1.6.29] - 2026-08-26

The 1.6.28 corrections' own correction, one round later. The LIVE
fan-out of SYNC-1.6.22-1.6.28 (2plot-network run 33000661276) went
red on 7 of 12 forks with one signature: the block's new cargo
`scripts/smoke_live.py` calls `fetch(url, retries=1, timeout=10)` in
wake(), and every fork's OWN `tests/test_smoke_live.py` monkeypatches
`fetch` with the pre-1.6.2x signature `(url, user_agent, accept)` —
TypeError before a single check ran. The file is byte-invariant; its
INTERFACE is pinned by a fork-owned, fork-specific test that can
never be cargo. Invariance of a file is not invariance of its
contract.

### Changed
- Sync spec renamed `SYNC-1.6.22-1.6.28.md` → `SYNC-1.6.22-1.6.29.md`.
  `scripts/smoke_live.py` removed from the sync-verbatim block; item 6
  reclassed **contract** for every fork — detect: wake loop
  (`SMOKE_WAKE_ATTEMPTS`) + fetch retries (`SMOKE_FETCH_RETRIES`) +
  explicit SSL context on EVERY urlopen; acceptance: the fork's own
  `tests/test_smoke_live.py` green against its own copy, stubs updated
  in the same touch. The divergent-tool branch (clerkhook's
  lockdown_smoke.py) kept as written.
- `sync/README.md` gains the authoring rule the round bought: **a
  whole file is verbatim-safe only if no fork-owned test exercises
  its interface** — ask "who stubs this?" for every cargo candidate.
- `scripts/smoke_live.py` wake() is stub-tolerant: when a legacy
  fetch stub rejects the retries/timeout kwargs (TypeError at
  signature binding — the real fetch cannot raise it), the probe
  falls back to a bare `fetch(url)`. A template copy landing ahead of
  a fork's stub update now degrades to that fork's honest check
  results instead of a suite-wide crash. Pinned by
  `test_wake_survives_a_legacy_fetch_stub`. This makes the release
  spec + one CD-tool robustness change, not spec-only as dropped.
- Spec item 3 notes gain the 1.6.29 cargo audit of
  `tests/test_auth_demos.py`: nothing stubs it, but it calls INTO two
  fork-owned seams (DEMOS's dict shape, conftest's `app_module`
  fixture) — fleet-uniform today; a reshaped fork reads a red there
  as interface drift, not the detect firing.

## [1.6.28] - 2026-08-26

Batch-2/3 corrections release — spec text, gate grammar and reference
pins only; no runtime change. Five forks consumed the 1.6.27 spec at
`055363e`; three (flows, muischeduler, clerkhook) filed the SAME
correction to item 5 independently, two filed the same `# requires:`
gap — independent convergence, adjudicated by the ops seat.

### Changed
- Sync spec renamed `SYNC-1.6.22-1.6.27.md` → `SYNC-1.6.22-1.6.28.md`.
  Item 5 amended: render.yaml BRANCHES on `runtime:` (`python` →
  PYTHON_VERSION required, minor-pinned; `docker` → must be ABSENT —
  nothing reads it there, and a string that reads like the platform's
  setting but can never be true is the item's own defect class); the
  SITE lane's Python split from PACKAGE matrices and both named; a
  MISSING healthz `python` field is not-adopted, never n/a
  (emojimart); minimal-payload hosts (clerkhook's recorded
  divergence) get skip-with-notice from `python_matches_declared`.
- The sync-verbatim blocks in ALL THREE specs gate on the kit
  CONTRACT (`# requires-contract: .claude/CLAUDE.md :: Check the
  prompt against this tree`), never on kit paths — flows' pre-existing
  non-kit CLAUDE.md read as adopted was the third "no .claude/"
  misread. `tests/test_auth_demos.py` carries a per-file gate
  (`# requires: lib/auth_demos.py`) so lockdown forks receive the
  rest of the block (clerkhook, dry run 32991971564). SEQUENCING:
  fanout.py must learn both forms before the next round.
- `tests/test_claude_kit.py` `_machine_fence` validates the two new
  gate forms — path + clause real at template HEAD, per-file gate
  path real — the release's one kit-test change.
- `tests/test_python_version.py`: the render.yaml pin branches on the
  service runtime (both branches upstream as the fleet reference);
  SITE-lane naming in the module and test docstrings.
- `SYNC-1.6.17-1.6.21.md` item 1 amended: detect wording (`pytest -v`
  shows PASSED — a SKIP or an absent test is not-ported; emojimart's
  "6 passed, 1 skipped" read identically for both unported states);
  the fence question ("is the difference a fork DECISION?" — drift is
  never fenced; flexlayout/muicharts' behind-1.6.24 dependabot.yml);
  muicharts fan-out PR #6 cited as the fence's concrete case.
- `.claude/CLAUDE.md` traps: anonymous api.github.com is 60 req/h —
  read a run once after CI completes, never poll blind; a JSON body
  without the asked-for field is a rate-limit error, not an empty
  list; `git fetch` before any audit.
- `/report` skill + `sync/README.md` + all three specs' Reporting
  sections: `open` added to the disposition vocabulary (detect fires,
  deliberately out of this session's scope).

### Added
- Spec item 6: `scripts/smoke_live.py` is versioned cargo — verbatim,
  rides the block (fork-invariant by construction; muischeduler's CD
  certified with a 1.2.4-vintage copy); contract half for forks whose
  CD uses a different live tool (wake loop + retries + SSL context).
- Spec item 7: the battery must see the CONFIGURED gate/lock page —
  fake config in a test, non-vacuous configured-branch assertion,
  marker/stripping rules imported from the live tool by path
  (clerkhook 5c5e9ea; class fleet-wide). The template's own adoption
  is recorded `open` — this suite blanks every Clerk secret before
  import.
- `sync/README.md`: the gate rule (a gate names a contract, never a
  path, wherever a pre-existing file can occupy the path; three gate
  forms documented) and the vendoring rule (specs are NOT vendored
  into consumers — decided over scoping the pins to the authoring
  repo).

## [1.6.27] - 2026-08-25

One Python for the fleet. The repo declared three (Dockerfile
`3.11.8-slim` — a patch pin that never received a 3.11.x security
release; CI matrix `3.12`; render.yaml `3.12.0`), the docker
boot/battery tested an interpreter the matrix never ran, and healthz
could not contradict any of it — the drift was invisible to the
battery by construction (ops-seat finding, read in the tree,
2026-08-25). The fleet Python is now **3.14**, decided by evidence:
the full suite and the real image's boot/battery ran green on
`python:3.14-slim` before anything shipped.

### Changed

- **`Dockerfile`**: `FROM python:3.11.8-slim` → `python:3.14-slim`.
  MINOR tag, never a patch pin — the minor tag tracks 3.14.x fix
  releases through the registry; the patch pin was the security bug.
- **CI matrix**: main `3.12` → `3.14` (all three backends); window
  legs `3.11`/`3.13` → `3.13`/`3.12` (three wide around the main —
  3.15 is at rc1 and does not exist as a release). The two dash-4.4.0
  bottom-range rows stay on 3.12 deliberately: each include row
  varies one axis. lint, pip-audit and cd.yml's verify job align to
  3.14.
- **`render.yaml`**: `PYTHON_VERSION` `3.12.0` → `3.14.7` (Render's
  native runtime requires full X.Y.Z; the minor is what the test
  pins). Blueprint env applies on a sync, not a push — a lagging
  dashboard value is exactly what the new battery check catches.
- **README / home.md**: supported floor 3.11+ → 3.12+ (the window).

### Added

- **`/healthz` reports `python`** (`platform.python_version()`) —
  one field, both backends: set in `lib/health.py`'s shared builder,
  typed as a required field on `HealthResponse` in
  `lib/asgi_routes.py`, pinned per backend in
  `tests/test_llms_routes.py`. The serving interpreter is now
  observable, so this drift class cannot re-hide.
- **`python_matches_declared`** in `scripts/network_smoke.py`: the
  served minor must equal the Dockerfile's FROM minor (declaration
  read from the checkout; field presence alone where there is none).
  Runs in CI against the booted container and in CD against
  production, like every battery check.
- **`tests/test_python_version.py`** — the encodings-agreement pins:
  FROM tag is minor-only, render.yaml/matrix main/singleton jobs all
  carry the same minor, matrix legs stay inside the three-wide
  window. Session-class for forks (presumes Dockerfile+render.yaml).
- **Spec item 5** in the rolling spec, renamed
  `SYNC-1.6.22-1.6.26.md` → `SYNC-1.6.22-1.6.27.md`: conditional
  (predicate: the fork has a Dockerfile) + contract. Nothing new
  rides the sync-verbatim block — every file the item touches is
  fork-divergent or presumes files not every fork carries. The eight
  open dependabot docker PRs are the ops seat's triage: merge where
  byte-equivalent, close with "template first, spec item 5".

## [1.6.26] - 2026-08-25

Batch-1 adoption feedback folds back into the specs: four corrections
where the retro-spec described the template's shape as a requirement,
one consumer precedent, and two new template-class items the round
surfaced — a gate-card demo table whose one entry resolved on no fork
(silently, by design), and a home lane that skipped the versions
pipeline the docs lane ran. Sources: excalidraw 76a9112, pannellum
97d1cba, email 9bcd32a, all wire-verified by the ops seat.

### Added

- **`tests/test_auth_demos.py`** — every DEMOS endpoint must be a
  registered page on THIS site and its module must import and expose
  `component`. `build_demo` degrades silently BY DESIGN (a broken
  example must never take down the sign-in funnel) and its warning
  only fires when the endpoint's card renders — which never happens
  when the endpoint is not a page there, so every fork's gate cards
  have rendered demo-less since fork time without a line of log.
  This test is the one loud surface. Byte-verbatim: it rides the
  sync-verbatim block, gated on `lib/auth_demos.py`, and is EXPECTED
  red on a fork until that fork picks its own entry (or empties the
  table) — the red is the detect firing.
- **A source pin in `tests/test_site_identity.py`**: both
  `pages/home.py` and `pages/markdown.py` call
  `substitute_versions` — /llms.txt serves home.md's text, so a
  `{{VERSION:…}}` token there ships raw on the most-read machine
  surface when home skips the call. AST, not grep (the
  marker-in-comment trap cuts both ways). Session-class, not block
  cargo: it presumes `lib/versions.py`, which pre-`{{VERSION}}`
  forks don't have.
- **Spec items 3–4** in the rolling spec, which extends its range
  and is renamed `SYNC-1.6.22-1.6.24.md` → `SYNC-1.6.22-1.6.26.md`.
  Item 3 (DEMOS resolution) is contract-class with the block-carried
  test as detect; item 4 (the content-pipeline agreement) is ruled
  contract, not verbatim — batch-1's own evidence (pannellum's
  hand-written home) proves home.py is not whole-file verbatim in
  the population.

### Fixed

- **Four SYNC-1.6.10-1.6.16 corrections** (each marked "batch-1
  correction, 2026-08-25" in place, emojimart's precedent): item 7's
  `files:` no longer claims `tests/test_auth_wiring.py` "ports
  everywhere" — the pin's home is fork-shaped and the pin is not
  auth-specific; item 8's `files:` is labeled the template's shape,
  not a requirement (the detect is shape-independent); item 6's
  .gitignore list omitted `kickoff/` while reading as complete — the
  template's block is now named the source of truth — and its notes
  gain the write-guard-scope (probe, don't assume) and
  one-terminal-line copy-command lessons; item 5's no-HEALTHCHECK
  note generalizes from a fork list to "any fork predating 1.6.14 —
  the detect decides".
- **`sync/README.md` consumer precedent**: a fork may carry a
  blanket-ignored `.claude/` with its own content — a kit item is
  then a MERGE, not an install-over; the allow-list ignore form is
  what keeps credentials under `.claude/` structurally
  uncommittable; and the adoption gate reading that fork
  `not-adopted` is correct, not a bug.
- **`lib/auth_demos.py` docstring** no longer claims the table
  "ships EMPTY in the template" — it has carried one working entry
  since the pattern shipped; the docstring now says so and points at
  the new test.

## [1.6.25] - 2026-08-25

The bot actor comes off main; the build-match wait learns to say
"superseded" in one poll instead of red-at-timeout. Owner option A on
the 1.6.24 report: the auto-merge workflow could only ever fix the
GATE (merge waits for CI), never the ACTOR — a GITHUB_TOKEN merge
gets zero workflow runs on its sha, so no CD run certifies the
deploy, and every repair (a merge-capable secret in every repo, or a
workflow_run re-trigger that must ALSO dispatch cd.yml through the
anti-recursion exemption) is a quirk chain propping up the fabric's
one proof. ~11 human clicks a month fleet-wide is cheaper; the
workflow_run shape is recorded as the deferred option if clicks ever
become the burden.

### Removed

- **`.github/workflows/dependabot-automerge.yml`** (added 1.6.24,
  retired one release later) and its line in SYNC-1.6.22-1.6.24's
  sync-verbatim block; spec item 1 is marked RETIRED with its
  history appended, not rewritten. Standing policy in its place:
  actions-group PRs are merged by a human click when the PR's CI is
  green — the human actor's push triggers CD, which certifies the
  merge. No fork ever received the workflow (the pair never fanned
  out), so the deletion has no fleet tail beyond the spec's
  consumer note. The dependabot.yml actions-group comment now
  states the policy instead of pointing at the deleted file.

### Changed

- **`cd.yml`'s build-match wait fails FAST on supersession.** When
  a different build serves, one compare-API call per distinct sha
  classifies it: "ahead" (the live build is a DESCENDANT of this
  run's sha) means branch HEAD moved past this run and the hook
  shipped it — this run's build can never serve again, so the wait
  errors "superseded" immediately instead of red after 25 minutes.
  "behind" (the previous release still serving mid-build, or a
  deliberate ROLLBACK — an older build is not a descendant),
  "diverged", and unknown/404 shas all keep waiting. Everything
  else — 100×15s, matched≥3, the pre-build-field fallback — is
  unchanged.
- The trap texts (CLAUDE.md, spec item 1 notes, the 1.6.24 entry
  below) keep the observed narrative; the remedy line becomes
  "actions PRs: human merge when green; never a bot actor on main".

## [1.6.24] - 2026-08-25

Dependabot stops proposing pip floor-raises; the actions group
auto-merges. Owner decision on the ops seat's fleet-wide reading of
all 38 open dependabot PRs: 18 were pip floor-raises — the
`dash-network` allow-list group, built to make a package release ONE
reviewable PR, could only ever propose floor raises on range
requirements, structurally producing the class the allow-list exists
to suppress. Drift detection, the group's stated purpose, is already
answered on the wire by the contract battery (healthz `dash_version`
against the floor).

### Removed

- **The `pip` ecosystem entry in `.github/dependabot.yml`** —
  allow-list, `dash-network` group and all. Floors move deliberately
  through sync specs, every encoding at once. SECURITY updates are
  unaffected, verified against GitHub's docs before shipping: they
  ride the alerts channel (dependency graph + Dependabot alerts, a
  repo setting), and "there is no interaction between the settings
  specified in the dependabot.yml file and Dependabot security
  alerts" (code-security/concepts/supply-chain-security/
  dependabot-security-updates). Removing the entry closes NOTHING:
  the template's own five pip floor-raise PRs (#6–#10) outlived the
  08-23 allow-list that already excluded their packages — closing
  them is SYNC-1.6.22-1.6.24 item 2, an owner action.

### Added

- **`.github/workflows/dependabot-automerge.yml`**: on dependabot
  PRs whose branch is `dependabot/github_actions/*` (the branch
  prefix IS the ecosystem — no third-party metadata action to pin),
  `gh pr merge --auto --squash` with `GITHUB_TOKEN`, permissions
  contents+pull-requests write on this workflow only. Docker
  base-image PRs are NOT auto-merged — a Python major is a merits
  decision. Inert until the owner flips "Allow auto-merge", and
  over-eager until `main` requires the CI checks (auto-merge waits
  for REQUIRED checks only) — both enumerated as the new spec's
  item 1.
- **SYNC-1.6.22-1.6.24.md** — "the next spec" did not exist (1.6.22
  and 1.6.23 shipped as amendments), so this release authors it.
  Both dependabot files join the sync-verbatim block under the
  existing kit gate: inert on a non-adopted fork anyway, and one
  gate keeps one rule.
- A CLAUDE.md verification trap, amended same-day to the OBSERVED
  shape: the workflow fired live within minutes (dependabot rebased
  PR #4 on the config change; merged as `4a1d430`, 79s before its
  own CI finished — no required checks on main). The merge sha got
  ZERO workflow runs (GITHUB_TOKEN anti-recursion) yet reached
  production anyway: the deploy hook builds branch HEAD, so the
  in-flight 1.6.24 CD shipped the merge while its build-match wait
  held out for `f25cb4f` and went red. Not a lag, a race; the fix
  was a re-verify commit. (Remedy line adjusted in 1.6.25 — actions
  PRs: human merge when green; never a bot actor on main.)

## [1.6.23] - 2026-08-25

The sync-verbatim block gains its adoption gate. Found by the ops
seat's first `forks=all` fan-out dry run (32812831785): six of the
ten public fleet forks predate the .claude kit, and the ungated
block would have dropped three skills and a FAILING kit test into
each — the machine doing a session's job badly.

### Added

- **`# requires: <repo-relative path>`** (sync/README.md): zero or
  more lines inside the fence naming files that must already exist
  in the consuming fork for the block to apply AT ALL. A fork
  missing any receives nothing and is flagged `not-adopted` — its
  next step is the contract item the cargo assumes, not the cargo.
  Any block carrying kit files or the kit test requires the kit's
  own markers (`.claude/CLAUDE.md`, `.claude/settings.json`); both
  specs' blocks gained the two lines — the 1.6.10–16 spec is what a
  fresh fork consumes first, so it gates too.
- **`_machine_fence` validates the directive**: a required path must
  exist at template HEAD and stay inside the repo — a typo'd gate
  gates nothing, so the pin fails it.
- Gate is per-BLOCK, not per-path, per the ops seat's position
  (adopted here): skills without the kit's CLAUDE.md contract are
  inert files, and a partial kit is worse than none — the next
  adopter session has to detect which half landed. If a future
  block ever carries mixed-prerequisite cargo, the fix is that
  spec's requires set, not per-path gating; today's cargo is all
  item-6 halves.

## [1.6.22] - 2026-08-24

The ops seat's correction of its own 1.6.21 drop, after proving the
sequencing note on a fresh fence-less clone (1 failed, 5 passed,
1 skipped): the byte-owned pin failing on absence let one unported
contract item keep EVERY later mechanical PR red — revoking the
fan-out's "verbatim class = green merge" promise indefinitely, and
contradicting the same release's own rule that the machine tolerates
absence via the mention heuristic.

### Fixed

- **The byte-owned pin SKIPS when the fence is absent**, with the
  reason naming the adoption path ("port SYNC-1.6.17-1.6.21 item 1;
  until then the fan-out uses the mention heuristic"). One or more
  fences still validate exactly as before (exactly one, paths real
  at HEAD, no escapes). Template-side behaviour unchanged — the
  template's fence exists. CI guards what a fork HAS declared; the
  contract item's session round drives adoption. A fork that once
  had the fence and lost it degrades safely: the mention heuristic
  over-flags and never restores, and deleting the fence is a
  session-class DIVERGENCES.md edit the report contract covers.
- The spec's sequencing note now describes the skip, not the red.

## [1.6.21] - 2026-08-24

DIVERGENCES.md gets its machine half. Found by the ops seat's A1
rehearsal of the fan-out against 1.6.20: honouring divergences by
prose MENTION over-flags — muicharts' host-pin nuance names the kit
test while its bytes are template-owned, a false positive recurring
every release on a file the template intends to own.

### Added

- **The `byte-owned` block** (DIVERGENCES.md, final section): the
  fence is the machine answer to "may the fan-out overwrite this
  path?" — listed paths are the fork's byte-for-byte; empty means
  the template owns every sync-verbatim path here; a fork without
  the block gets the conservative mention heuristic (over-flags,
  never restores). The template's own block ships empty.
- **The pin** (`tests/test_claude_kit.py`): exactly one byte-owned
  fence wherever DIVERGENCES.md exists, paths real at HEAD, none
  escaping the repo — validation shared with the sync-verbatim
  fence via one helper. Byte-portable.
- **`sync/SYNC-1.6.17-1.6.21.md`**: the range's first spec (1.6.17–
  1.6.20 shipped without one — the drop said "the next spec" and
  none existed; corrected by authoring it). Item 1 (contract): the
  byte-owned retro-add — fence content is per-fork judgment and
  cannot fan out; the pilots were audited first and none of the
  three carries a byte-level claim on a sync-verbatim path, so all
  three blocks start empty. Item 2 (conditional): the 1.6.19 docker
  health-verdict step. Sequencing note recorded in the spec: this
  spec's own sync-verbatim block ships the enforcing test, so
  fan-out PRs run red until item 1 is ported — the designed flag,
  not an accident.

## [1.6.20] - 2026-08-24

The F3b prerequisite, authored by the ops seat (2plot-network) and
executed here: the sync spec grows a machine-readable half. Prose
stays the contract; the fenced block is what the fan-out workflow
byte-copies into a fork.

### Added

- **The `sync-verbatim` block** (`sync/README.md`): every spec
  carries exactly one fenced list of whole-file byte-copy targets.
  The class boundary becomes explicit — whole-file = machine,
  fragment = session. "The template wins on these bytes" is
  something a session can apply to a function; a workflow cannot,
  and without the block the fan-out had nothing safe to carry.
  Recorded divergences on a listed path win (the workflow skips and
  flags); `.claude/settings.json` never rides along unless the
  spec's prose declares a fleet-wide settings change — it CAN fan
  out mechanically, so it must be deliberate.
- **The pin extends** (`tests/test_claude_kit.py`): every
  `SYNC-*.md` has exactly one block, every listed path exists at
  HEAD, none escapes the repo. An empty block is a statement; a
  missing one is an omission. Fork-side the whole test still skips
  (no `sync/`).
- **The retro-spec gains its block**: item 6's four byte-verbatim
  halves (the three skills + the kit test). Verified against the
  actual pilot population before listing — leaflet2 (pushed HEAD via
  API; its local checkout is months stale), muicharts, flexlayout:
  wire-verify and report SKILL.md byte-identical to the template on
  all three; sync-template SKILL.md and the kit test lag identically
  on all three (pre-1.6.17/1.6.18 copies — no localisation anywhere,
  and exactly the cargo the fan-out's first run should carry).
  Rejected from the block: nothing beyond the drop's own fragment
  exclusions (3a, 7).

## [1.6.19] - 2026-08-24

F2 closes: emojimart synced from the spec alone (078e514,
wire-verified — the conditional predicate delivered its missing
HEALTHCHECK unprompted). Its remaining corrections and its
template-class finding, adopted:

### Fixed

- **Spec item 2's detect can't catch item 2's own failure mode**
  (the sharp one): sampling two of four floor encodings reports
  already-present on exactly the forks that drifted — emojimart's
  ci.yml asserts still gated (2,6,0) while both sampled encodings
  were correct, a guard that silently stopped guarding. The detect
  now also requires that no GATING encoding names a lower version —
  a negative grep that doesn't collide with the never-grep rule,
  because it greps for what must NOT appear in gates.
- **Spec item 5's detect is port-agnostic** (defaulted at the point
  of use is the contract; 8550 is the template's number) and **item
  7's files** acknowledge forks without post() — the source pin is
  the half that ports everywhere.

### Added

- **CI asserts Docker's own health verdict** (emojimart's
  template-class finding — the guard on the guard): the boot step
  curls /healthz from outside, proving the app answers, but a broken
  HEALTHCHECK instruction shipped silently while everything stayed
  green. The docker job now polls
  `docker inspect '{{.State.Health.Status}}'` to `healthy`, fails on
  `none` (no HEALTHCHECK = opaque to the orchestrator), and dumps
  the probe's own log on failure.

## [1.6.18] - 2026-08-24

The retro-spec's first real consumer (emojimart, the F2 acceptance
run) returned two spec corrections and one permission lesson — all
adopted.

### Fixed

- **Spec item 9's detect was unsatisfiable by grep** — the fix's own
  explanatory comment necessarily names the phrase it retired, so
  the template failed its own detect. Now "the intro STRING,
  comments stripped" — the marker-in-comment trap, in its third
  costume.
- **The kit's sync-spec pin skips where no `sync/` exists**: forks
  consume specs, only the template authors them — the byte-verbatim
  kit port failed on arrival at every fork without the guard. The
  pin wakes if a fork ever authors specs.

### Added

- **The settings-write precedent** (spec item 6 notes):
  `.claude/settings.json` is permission-classed and a session may be
  unable to write it — that guard is CORRECT, and the procedure is:
  stage the exact content in the scratchpad, hand the owner a
  one-line `!` copy, orchestrator verifies the staged content before
  the copy.

## [1.6.17] - 2026-08-24

The F2 fabric build: propagation as artifact, not conversation.

### Added

- **`sync/` — release sync specs** (`sync/README.md` defines the
  format; `sync/SYNC-1.6.10-1.6.16.md` is the retro-spec pilot).
  Each item carries a class (`verbatim` / `contract` /
  `conditional`), a **detect** check so forks at different levels
  consume the same document and apply only what they lack, and an
  **acceptance** pin. The authoring rules are the F1 pilots'
  earned corrections: floors stated by `LLMS_PKG_FLOOR` semantics
  (the ladder retains old rungs by design — grep finds history and
  calls it the present), CLAUDE.md's contract/traps sections
  verbatim with the rest adapted, DIVERGENCES retirements marked
  not deleted, and the contract-class evidence standard (a diff or
  passing pins, never an assertion). A format pin in
  tests/test_claude_kit.py rejects any spec item lacking
  detect + acceptance: an item without both is not specifiable.
- **`/sync-template` aligned**: the current floor is what
  `LLMS_PKG_FLOOR` says, never what grepping finds; detect-first
  dispositions (`already-present` with evidence); the spec is
  subject to the same correction contract as any prompt.

## [1.6.16] - 2026-08-24

The first harvest of the F1 pilots: three template-class defects found
by fork sessions exercising the new behavioral contract, all verified
against this tree before adoption, plus one honesty fix.

### Fixed

- **`scripts/smoke_live.py` `post()` passes `context=SSL_CONTEXT`**
  (flexlayout's finding): `fetch()` carried it; `post()` didn't, so on
  any Python without OS trust-store integration (macOS — the fleet's
  whole local-dev half) every auth POST died in the TLS handshake,
  returned 0, and the check accused the app of the exact
  `configure_app` regression it exists to detect. CI never saw it
  (Linux verifies fine); no wired test could (they monkeypatch
  `post`) — a SOURCE pin in tests/test_auth_wiring.py now sweeps every
  `urlopen` in the file.
- **cd.yml's verify job also skips on a SKIPPED deploy** (muicharts'
  fix, adopted): with only `!= 'cancelled'`, a skipped deploy still
  ran verification against whatever build happened to be serving —
  one cause, two red jobs.
- **The machine lane publishes the site brand at the root**
  (leaflet's finding): `_build_llms_doc` took `metadata.name`, so a
  home page named "Home" put `# Home` in the preamble while the
  package injects the site brand — mismatched H1s the 2.7.0 dedup
  cannot fold (leaflet's home served three). `published_name(path,
  name)` (ported from leaflet's fork-side fix into
  lib/page_visibility.py) returns `SITE_BRAND` at "/" and the page
  name elsewhere; the markdown pipeline now publishes through it, so
  fresh forks stop re-living the defect.
- **The gate card stops promising "the AI assistant"** (leaflet's
  catch): no fork wires one, and a sign-in card selling a feature
  that doesn't exist spends credibility at the highest-intent moment.
  The card now promises exactly what ships.

## [1.6.15] - 2026-08-24

The F1 fabric build: the `.claude/` development kit ships with the
template, so every fork inherits the network's behavioral contract
instead of a blank slate. Until now the blanket `.claude/` gitignore
kept the project instructions local-only — forks inherited NOTHING.

### Added

- **`.claude/CLAUDE.md` gains the network role & behavioral
  contract**: identity derives from the repo, never the file; check
  every prompt against this tree; corrections are the session's job;
  wire-verify your own deploy before reporting; divergence is
  legitimate when recorded; never touch env values/dashboards/other
  repos — plus the fleet's verification traps (cache bust, GET not
  HEAD, dependabot-run watchers, two-lane rule). File case
  canonicalized (`claude.md` → `CLAUDE.md` — macOS forgave it,
  Linux would not).
- **`DIVERGENCES.md`** at the repo root: the boundary between design
  and drift. Syncs read it first and must not restore what it
  records; an unrecorded difference is treated as drift. Fleet
  precedents named (flexlayout, flows, clerkhook, muischeduler).
- **Three skills**: `/wire-verify` (the acceptance ritual as one
  command — healthz identity/build/geo, both lanes, the traps),
  `/sync-template` (divergence-aware, spec-driven, acceptance-
  pinned), `/report` (evidence-first structure with the observed
  anti-patterns named and rejected).
- **`.claude/settings.json`** (checked in): fleet model default
  (opus — seats override locally via settings.local.json, which
  stays ignored), sandbox network allowlist naming THIS host +
  the hub so sessions can wire-verify their own production
  (clerkhook and pannellum both couldn't reach theirs), WebFetch
  domain allows. `tests/test_claude_kit.py` pins the kit shipped,
  case-correct, and — the anti-drift pin — that allowedDomains
  follows `lib/constants.BASE_URL`, so a fork keeping the
  template's host verbatim goes red until it points at itself.

### Changed

- **`.gitignore`**: `.claude/` blanket ignore becomes an allow-list
  (`CLAUDE.md`, `settings.json`, `skills/` ship; scratch and
  settings.local.json stay local), and the session-document
  convention is now enforced network-wide: `X402-SYNC-REPORT.md`,
  `HANDOFF-*.md`, `KICKOFF-*.md` ignored — two public fleet repos
  were caught tracking theirs, and clerkhook's staged handoff was
  one push from public.

## [1.6.14] - 2026-08-23

### Fixed

- **The container honors `$PORT`** (Dockerfile): exec-form CMD never
  expands env, so the old
  `["gunicorn", "run:server", "-b", "0.0.0.0:8550"]` hardcoded the
  port regardless of what the platform asked for — it only worked on
  Render because Render port-detects. Now shell form with
  `${PORT:-8550}`, and the HEALTHCHECK probes the same variable.
  run.py has honored `$PORT` since 1.6.8; the container lane finally
  agrees. Credit: excalidraw fixed this fork-side in its gate-wave
  pass and, on floor-round sync, rightly refused to adopt the
  template's regression — this release makes the template agree with
  the fork instead.

## [1.6.13] - 2026-08-23

Two wave-2 findings folded back, both from hosts that hit what the
template hadn't: dash-email's CD timeout class and dash-flows' proof
that the Flask-lane healthz pin couldn't fail.

### Changed

- **CD's build-match wait is sized for the worst build, not the
  median** (cd.yml): the loop grows to 100 × 15s and the job timeout
  to 30 minutes. A floor bump busts the Docker dependency cache by
  design, so the pipeline's most important deploy is also Render's
  slowest build — dash-email's wait timed out on exactly that class.
- **Hookless deploys warn instead of whispering**: with
  RENDER_DEPLOY_HOOK_URL unset the step now emits a `::warning` with
  accurate wording (the push deploys only if autoDeploy fires; the
  build-match wait still holds for THIS commit). dash-email hit the
  case where autoDeploy also skipped — nothing deployed, the wait
  honestly timed out, and the quiet `::notice` was why the cause took
  a full run to see.

### Added

- **Context-free `_resolved_country` pin** (dash-flows' finding): the
  in-request pins pass even if a Flask route drops `headers=` — the
  context fallback reads the same headers, and the lanes that truly
  break are unreachable from a Flask-pinned suite. The new test calls
  `_resolved_country({"CF-IPCountry": "DE"})` outside any request
  context, where there is no fallback to hide behind.

## [1.6.12] - 2026-08-23

### Fixed

- **healthz `geo.resolved` works on every backend**: each route now
  hands its own request headers to `health_payload`, which passes them
  to `geo.explain_resolution` explicitly. The 1.6.10 version read
  Flask's request context, so the FastAPI and Quart lanes answered
  "no request context" forever — pannellum's production healthz
  (FastAPI) was the host that showed it, caught by the round-3 wave-1
  wire check within hours of shipping. `normalize_headers` accepts
  Flask/Starlette/Quart headers and never raises; the Flask-context
  fallback stays for callers that pass nothing. Both backend tests now
  pin that a spoofed `CF-IPCountry` header surfaces in `resolved`.
  Waves 2–4 of the floor round port this version automatically;
  pannellum takes it as a one-line follow-up.

## [1.6.11] - 2026-08-23

The fleet floor-round opener: the dimll floor moves to ≥2.7.1, and the
pin written for what that floor buys immediately caught a template bug
of its own.

### Changed

- **dimll floor ≥2.7.1** in every encoding (requirements.txt, run.py's
  `LLMS_PKG_FLOOR` + boot message, the tests). What it buys: 2.7.0
  dedups the prerender H1 (every page served two h1s to crawlers) and
  the home footer's doubled /llms.txt link, hardens the idempotency
  probe (the marker-in-comment trap), and ships the geo guardrail +
  operator panel seams; 2.7.1 adds the llms.txt v2 discovery relations
  on both lanes + Link headers, the text/plain Accept ramp, and the
  representation digest. The requirements line changing IS each fork's
  Docker cache bust — the round-2 lesson, now restated beside the
  floor. The boot floor turns a stale image into a loud refusal.

### Fixed

- **`_expand_source_directives` is fence-aware** (pages/markdown.py):
  it expanded `.. source::` examples sitting INSIDE fenced code blocks
  — docs/example and docs/directives teach the directive inside
  ```markdown fences — injecting a fence into the open fence, closing
  it early, and rendering the inlined Python file as markdown on the
  machine lane: every `# comment` line became an `<h1>` (five h1s on
  the directives tutorial, on every fork, browser lane unaffected).
  Found minutes after writing the single-h1 pin below.

### Added

- **Every-page generic-lane structure pin** (tests/test_pages.py):
  exactly one `<h1>` per document (comments stripped), no duplicate
  llms.txt links in the prerender footer, home carries exactly the
  root link — plus a unit pin that fenced directive examples stay
  documentation.

## [1.6.10] - 2026-08-23

Two `/healthz` defects found (and first fixed) on llms-2plot-dev during
its production verification, ported back as the reference
implementation — plus the identity and geo diagnostics that exposed
them. The probe is how CD, the hub sweep, and any outside verification
know WHAT is serving; both defects made it lie by omission.

### Fixed

- **The Flask/Quart payload was a snapshot**: `register_health_route`
  computed the dict once at registration and the route closed over it.
  Harmless while every field was static, silently wrong the moment one
  is not — on the fork, the route is mounted before `configure_geo`
  runs, so the new geo diagnostic reported the guardrail unconfigured
  on a host where it is configured. Built per request now.
- **FastAPI built its own payload and never called `health_payload`**,
  so a FastAPI deployment silently lacked `build` — the exact field
  cd.yml's build-match wait polls for. It would have fallen into the
  "predates the build field" warning path forever, verifying whichever
  release happened to be serving: the muicharts defect the wait was
  written to prevent, reintroduced per-backend. All backends now render
  from the one `health_payload`; `HealthResponse` only types it for
  Swagger.

### Added

- **`app` in the healthz payload** (`SATELLITE_APP_KEY`, else
  `"unknown"`): `build` says which commit answered, `app` says which
  satellite — different questions on a fleet where every host shares
  one template and a hostname can be repointed between services
  (llms.2plot.dev was, 2026-08-23).
- **`geo` in the healthz payload** on dash-improve-my-llms ≥ 2.7.0:
  `{configured, denied, resolved}` — counts and flags only, never the
  denylist's country codes; `resolved` reveals only the caller's own
  country, and is the per-host check GEO.md calls mandatory before
  trusting a denylist. On older packages the key is OMITTED, not
  error-flagged — the fleet's ≥2.7.1 floor round lights it up with no
  further change. Four tests pin the contract (per-request liveness,
  identity fields, FastAPI parity, counts-not-codes).

## [1.6.9] - 2026-08-23

### Removed

- **The vestigial Node layer left the production image** (issue #12,
  CVE-2026-1615): `package.json`/`package-lock.json` were
  dash-mantine-components' component-build toolchain, inherited
  through the fork lineage and used by NOTHING here — no webpack
  config, no `src/ts`, no CI job, no served asset — yet the
  Dockerfile apt-installed nodejs+npm and `npm install`ed the tree
  into every production image, fleet-wide, including a
  known-vulnerable `jsonpath@1.1.1` (static-eval expression
  evaluation; fixed upstream in 1.3.0, March 2026). Exploitability
  here was effectively nil — no Node process serves traffic, nothing
  evaluates user-supplied JSONPath, and the code isn't bundled into
  any served asset — but dead weight that trips scanners and bloats
  images is still dead weight. Both files deleted, the Dockerfile
  keeps only curl (the HEALTHCHECK's), with the rationale in place so
  no future fork re-adds Node by inheritance. Forks that genuinely
  build JS components add their own toolchain knowingly. Docs-fleet
  forks pick this up with the next Dockerfile sync (the ≥2.7.1 floor
  round carries it).

## [1.6.8] - 2026-08-22

Five fork footguns upstreamed from the llms-2plot-dev phase-1 fork
audit — each fires on every fork, not just that one, and each carries
that repo's fix as its reference implementation.

### Fixed

- **`excluded_links` now hides from BOTH audiences**: the navbar wires
  every excluded path through dimll's `mark_hidden`, so a page removed
  from the sidebar is also removed from sitemap.xml, /llms.txt, the
  tier corpora, MCP, the prerender and the crawler document. Before
  this, llms-2plot-dev "hid" the template's tutorial pages and kept
  publishing them to every crawler as its own documentation — duplicate
  content invisible from a browser. `tests/test_excluded_links_hidden.py`
  pins the parity from both ends, with a positive control so an empty
  sitemap can't pass it vacuously.
- **The header wordmark moved to `lib/constants.WORDMARK`**: it was a
  hardcoded "Dash Docs" string in components/header.py, so a fork that
  edited the constants identity block — reasonably assuming that was
  the whole job — still served the template's wordmark beside its own
  logo. The aria-label derives from the same constant, so the
  accessible name can never disagree with the visible one.
- **The foreign-canonical smoke test derives its host from BASE_URL**:
  it spelled the template's hostname literally, so on any renamed fork
  its rewrite matched nothing and the test passed as a no-op — a guard
  that silently stopped guarding exactly where it was needed. An
  in-stub assertion now errors if the rewrite ever fails to change a
  canonical-bearing page.
- **`page_visibility.json` (+ lock/tmp) joined .gitignore**: with
  PAGE_VISIBILITY_FILE unset the control-board store falls back to the
  app directory, so running the board locally wrote a real policy file
  into the checkout — same class as the analytics ledger, which was
  already ignored for exactly this reason.
- **run.py's dev server honours $PORT and HOST**: the port was a string
  literal and the host hardcoded, so a platform injecting $PORT needed
  a code change. Production never reaches this block (gunicorn).

## [1.6.7] - 2026-08-22

### Added

- **Auth-wiring guards, both halves** (the flexlayout finding):
  dash-clerk-auth wires either side of `Dash(...)` — `register()` is
  the UI half, `configure_app(app)` the server half (`/api/auth/*`
  routes + per-request identity). Flexlayout's batch-2 pass shipped
  the first call without the second: components rendered and ClerkJS
  reported signed-in while every server render read signed-out — the
  control board served the owner the sign-in card forever,
  `POST /api/auth/session` answered 405 through Dash's GET-only page
  catch-all, and sign-out never revoked. Invisible to every suite,
  because Clerk is off in test environments and `configure_app`
  no-ops without keys. Two guards now, one per environment:
  `tests/test_auth_wiring.py` pins structurally (AST) that run.py
  calls BOTH halves; `scripts/smoke_live.py` gains an "Auth wiring"
  block that POSTs both endpoints on the live host (registered =
  2xx/4xx; unregistered = 404/405), gated on the package's inline
  bootstrap being present in the served shell so clerk-off hosts skip
  rather than fail. Measured baselines: boilerplate answers 401/200,
  flexlayout answered 405/405. Note: the battery's POST probes need
  real egress — sandboxed environments that allow only GET report
  transport-0.

## [1.6.6] - 2026-08-22

### Changed

- **dimll floor 2.6.0 → 2.6.1** (requirements incl. the commented
  backend extras, run.py's boot floor + its message, and the test —
  the floor lives in more than one place; all moved together). 2.6.1
  makes the universal prerender VISIBLE to non-JS consumers: below it
  the injected block carries a literal `hidden` attribute, so every
  visibility-respecting reader (html-to-text extractors, arguably
  crawler content-weighting) saw only "Loading..." — the outside-audit
  finding of 2026-08-22, diagnosed live across six hosts and fixed at
  the package. The generic-UA prerender test now asserts the fixed
  shape: div without `hidden`, plus the marked synchronous hide script
  that keeps JS browsers flash-free (React's mount wipes the pair, so
  nothing changes for humans). The fleet inherits 2.6.1 on each host's
  next deploy with no requirements edit; this release is the reference
  host's own pickup plus the floor that makes the guarantee permanent.

## [1.6.5] - 2026-08-22

Batch-1 closeout: the wave's other three hosts (emojimart, modelviewer,
excalidraw) shipped dark, and four of their findings trace to this
template. All four are fixed at the source so batch 2 and every future
fork inherit the fix instead of rediscovering it.

### Added

- **Runtime-imports guard** (`tests/test_runtime_imports.py`, the
  modelviewer finding): a fork died in production on a
  function-local `import PIL` that every dev machine happened to
  satisfy — suite green, boots locally, dies in a clean image, and one
  docs example took all ten pages down because Dash imports every page
  at construction. The test AST-walks every runtime module and asserts
  each absolute import resolves in the environment CI installs
  (requirements.txt and nothing else); nesting is deliberately ignored
  because it does not predict boot-fatality. The optional-backend
  exemption (fastapi/quart select by env) is earned by two companion
  tests: the extras must stay documented as commented requirements
  lines, and the carrier modules must never be hoisted to run.py's
  unconditional top level. A third companion pins that runtime code
  never imports build-time `scripts/`.
- **CSS hygiene guard** (`tests/test_css_hygiene.py`, the excalidraw
  finding, landed at the source): fails on any hashed `.m_*` Mantine
  selector in `assets/*.css`. Three forks have paid for this class —
  leaflet's floating drawer, emojimart's 63vh drawer, and excalidraw
  inheriting two dead-or-harmful hashed rules **from this template**.
- **modelviewer + excalidraw joined the canonical network directory**
  (`lib/network_directory.py`): both were deliberately absent until
  they deployed; both are live and build-identity-verified as of
  2026-08-21/22. The fleet re-copy carries the entries everywhere.
- **Markdown tables scroll in their own box** (`table.m2d-table`,
  GitHub's recipe: content-width, capped at the container, scrollable
  past it — the excalidraw finding): a `<table>` is min-content sized,
  so one wide prop table dragged an entire page 105px sideways at
  414px. A no-op for tables that already fit; covers kwargs prop
  tables too, since markdown2dash stamps the class on every table.

### Fixed

- **The three hashed-selector fossils removed from `assets/main.css`**
  (dmc-docs fork era, present since the initial commit):
  `.m_46b77525` put an `!important` margin on every Input wrapper in
  every docs example; `.m_5caae85b` was dead in DMC 2.7 **and** 2.8;
  `.m_9cdde9a` restated Mantine's own aside declarations around one
  intentful pixel — the TOC's 15px breathing gap, which moved to the
  static `aside.mantine-AppShell-aside` rule.
- **`scripts/make_favicons.py` now flattens the apple-touch icon onto
  opaque white** (the emojimart finding): iOS composites the icon's
  alpha onto its own background — black on some surfaces, white on
  others — so every fork that ran this script shipped an icon that
  renders differently everywhere it appears. Every other size keeps
  its transparency. The template's own `apple-touch-icon.png` is
  regenerated (the other seven files regenerated byte-identical,
  confirming provenance), and a header-level PNG colour-type test
  pins opacity without needing Pillow in CI.
- **The header wordmark now hides below `xs` with the accessible name
  preserved** — the pattern both modelviewer and excalidraw needed and
  implemented divergently. `visibleFrom` keeps the node in the DOM
  (the typing animation still finds it) but `display:none` DOES remove
  it from the accessibility tree, so the home link now carries a
  permanent `aria-label` and the logo img is explicitly decorative
  (`alt=""`). Without the label, phones would get a home link with no
  name at all — the modelviewer defect, which excalidraw's pass
  reasoned incorrectly about and likely still ships.

## [1.6.4] - 2026-08-21

Two fleet-class fixes surfaced by the wave's first pair, landed at the
source so the other eighteen forks inherit them.

### Fixed

- **CD now verifies the artifact it shipped, not "whatever is live"**
  (the muicharts finding): with `RENDER_DEPLOY_HOOK_URL` unset, the old
  workflow skipped the wait and ran the live battery seconds after the
  push — against the previous release, every run, invisibly.
  `/healthz` now reports the running instance's commit
  (`RENDER_GIT_COMMIT`, optional field — the fleet probe contract is
  unchanged), and the CD wait holds until it matches the run's SHA,
  falling back once (with a warning) on builds predating the field.
- **The byte-copy identity trap** (the pannellum finding): the
  reporter must stay byte-identical across forks, so its fallback
  app key says "boilerplate" everywhere — while a fork's other modules
  default to the fork's own key. `run.py` now claims the identity via
  `os.environ.setdefault("SATELLITE_APP_KEY", ...)` before any
  hub-facing import — the marked FORK POINT; forks change that one
  string and keep the reporter byte-identical. A real env value always
  wins.

## [1.6.3] - 2026-08-21

### Changed

- **Vendored dash-clerk-auth 1.0.4 → 1.0.5** (sha256 `a2f9062e…b74f3`,
  full provenance in requirements.txt). Fixes the return-trip stale
  gate the owner observed live: landing back on an auth-gated page
  after signing in on the primary showed the gate card until a manual
  refresh, because the first server render precedes `__dca_identity`
  minting. 1.0.5 syncs the session and reloads once, with a
  sessionStorage no-loop marker shared by both reconciliation paths.
  The provenance rule is now general: only the recorded sha admits a
  tarball — stale early builds have bitten on both of the last two
  releases and are indistinguishable by name, size, or date.

## [1.6.2] - 2026-08-21

The pre-wave hygiene pass, from the four-repo review.

### Fixed

- **Date-skew corrections (leaflet handoff §8):** seven committed
  provenance stamps read `2026-08-22` for events whose verified date is
  `2026-08-21` (git author dates corroborate) — CHANGELOG headers
  1.5.3–1.6.1, `components/header.py`, `lib/ad_client.py`,
  `requirements.txt`. All corrected; the three release commit SUBJECTS
  carrying the wrong date are immutable and stand corrected by this
  entry. A date nobody can trace is worse than no date.
- `docs/authentication/authentication.md` now documents the
  control-board override layer (override → frontmatter →
  `PAGE_DEFAULT_TIER`, hub ceiling on top) instead of contradicting
  shipped behavior; `lastmod` bumped accordingly.
- `run.py`'s floor failure message now names what a 2.5.x actually
  loses first — silently swallowed `lastmod`, the lying sitemap —
  matching the comment that raised the floor.
- `lib/auth.py`'s signout-shim docstring caught up with reality
  (upstream fix shipped in 1.0.3/1.0.4; the shim is a deliberate
  duplicate until the fleet-wide retirement pass).

### Changed

- README caught up three releases: dimll floor 2.5.1 → 2.6.0 in five
  places, a new Access Control & Live Page Management section
  (control board, admin allowlist, gate teasers), the mobile-drawer
  standard under UI/UX, and the admin env vars in Configuration.
- `.env.example` gains the admin surface (`ADMIN_EMAILS`,
  `ADMIN_USER_IDS`, `ALLOW_UNGATED_ADMIN`) — the gate for the 1.6.0
  headline feature was previously undiscoverable from the env template.
- `.claude/CLAUDE.md` Customization Points now lists the control board,
  the override store, and the auth-demo teasers.

## [1.6.1] - 2026-08-21

### Fixed

- Accessibility + agentic-browsing names on the header's icon controls
  (hamburger, theme toggle, GitHub link — `create_link` now requires a
  label), and the network-ad image reserves a square box via
  `aspect-ratio` so the aside no longer layout-shifts when the creative
  loads. All three were Lighthouse findings on the pilot host measured
  against template code — every fork inherits the fix.

## [1.6.0] - 2026-08-21

Every fork gets its own live control board — the leaflet pilot's proven
UX, ported with its scar tissue included.

### Added

- **`/admin/control-board`** (`pages/control_board.py`): flip any docs
  page between public / auth / admin / hidden and toggle its llms.txt
  exposure, live — changes apply on the next render, no restart. Gated
  by the ADMIN_EMAILS/ADMIN_USER_IDS allowlist + owner; **fails CLOSED**
  without Clerk (`ALLOW_UNGATED_ADMIN=1` for local work), and the write
  callback re-checks the gate server-side (pattern-matching callbacks
  stay callable by anyone who can POST). The board stays OUT of both
  tier ledgers — its machine surfaces are silenced package-side via
  `mark_hidden()` (sitemap, llms.txt, MCP, prerender, crawler HTML all
  treat it as absent) so `access.gating_configured()` stays False on
  all-public forks and the hot path stays check-free.
- **`lib/page_visibility.py`** — the override store, with both fleet
  lessons built in: mtime-throttled cross-worker reload (a toggle lands
  on every gunicorn worker within ~1s — the pilot's coin-flip defect)
  and loud persistence guards (boot warns when `PAGE_VISIBILITY_FILE`
  is unset OR points under /var/ without a real mount — the
  twice-observed silent-reset-per-deploy class).
- Override-first resolution in `lib/access.py`: board override →
  frontmatter → env default, with the hub ceiling still applied on top
  (an override can loosen a local declaration, never a network
  restriction). `pages/markdown.py` registers every docs page on both
  ledgers from the one declared value.
- The sign-in card's live-demo teaser now ships ARMED: DEMOS carries a
  working entry (`/examples/visualization` → the theme-aware chart), so
  gating that page shows "Live demo — try it" above "Authentication
  required — You're looking at a live preview of {page}. Create a free
  account to unlock the full documentation — every interactive example,
  the complete API reference, and the AI assistant."
- `render.yaml` + `.env.example`: `PAGE_VISIBILITY_FILE` on the
  /var/data disk, with the blueprint-vs-dashboard drift warning
  inline. 14 new tests (`tests/test_control_board.py`).

## [1.5.4] - 2026-08-21

### Changed

- Navigation order: "Other Apps I've built" now sits above "Resources",
  and "Resources" is the LAST section — own-work ranks above third-party
  links, and the only section that navigates away from the network
  closes the list.

## [1.5.3] - 2026-08-21

### Changed

- **Vendored dash-clerk-auth 1.0.3 → 1.0.4** (sha256 `7a7c333a…cf701a`,
  recorded in full in requirements.txt with the stale-first-build
  warning). What 1.0.4 fixes, from the live network certification: the
  FastAPI auth endpoints were never callable (un-annotated request
  param → required query field → 422 on every POST — inert on this
  Flask host, fatal on fastapi ones), and the ghost-cookie fresh-load
  case — a page loading with ClerkJS signed-out while the server still
  held the identity now reconciles with a signout POST + single reload,
  which is the cross-host sign-out path no click shim can cover.
  `revokeServerSession` also verifies its response now. The 1.5.1 shim
  remains an idempotent duplicate; retirement is one clean release
  cycle after the fleet is on >=1.0.4.

## [1.5.2] - 2026-08-21

### Changed

- **Vendored dash-clerk-auth 1.0.2 → 1.0.3** (sha256 `2c6b40f4…da1944`,
  recorded in full in requirements.txt — the tarball IS the release;
  there is no PyPI for this package). 1.0.3 fixes sign-out revocation
  package-side (both entry points + the signed-in→signed-out listener
  transition, so sign-outs propagate across tabs and hosts), replaces
  the DiceBear default avatar with an inline SVG data URI (no third
  party in the UI path), and discards non-absolute
  `satellite_sign_in_redirect` values loudly. 1.5.1's app-side signout
  shim is idempotent alongside it and retires next release.
- Provenance caveat recorded in requirements.txt: vendor from the hook
  repo's `dist/` artifact ONLY — its `main` currently holds a broken
  build (boot-time collection error on Python 3.10/3.11) until the
  import-fix PR lands; verify the sha before re-vendoring.

## [1.5.1] - 2026-08-21

Pilot-week hotfix: Sign Out that actually signs out, and an honest
floor comment.

### Fixed

- **Sign Out now revokes the server session.** dash-clerk-auth 1.0.2's
  logout runs `window.Clerk.signOut()` client-side and reloads — but the
  server keeps trusting the signed `__dca_identity` cookie (max-age
  `session_lifetime_days`, default **7 days**) and the Flask session it
  minted at sign-in, so a signed-out browser kept rendering every
  auth-gated page; on a shared computer the next person inherited the
  previous user's access. The package ships the endpoint that fixes this
  (`POST /api/auth/signout`) but nothing ever called it. New
  `lib/auth.py:_install_signout_delegation()` — a capture-phase delegate
  on the logout menu item (the sign-in delegation's proven pattern) —
  owns the click and sequences `Clerk.signOut()` FIRST (so the slow path
  can't re-verify `__session` and re-mint), then the server signout,
  then the reload, awaited so the reload never races the cookie clears.
  The package-side fix ships in dash-clerk-auth 1.0.3; this delegate is
  idempotent alongside it and retires a release after the fleet vendors
  `>=1.0.3`.

### Changed

- **Floor-comment honesty** (`run.py`, `pages/markdown.py`): 1.5.0's
  claim that passing `lastmod=` "TypeErrors on anything older" was
  false — measured on 2.5.1 by the pip-docs+ stage-4 session, the
  signature is `(path, name=None, description=None, llms_doc=None,
  **kwargs)`, so older packages accept the date and silently ignore it.
  The 2.6.0 floor stays load-bearing, but for honesty (below it, every
  stamped date is swallowed and the sitemap goes back to swearing
  everything changed at build time), not crash avoidance.

## [1.5.0] - 2026-08-20

The reference host proves dimll 2.6.0 (stage 2 of the network rollout
order). The floor is load-bearing: pages/markdown.py passes `lastmod=`
unconditionally, which TypeErrors on anything older.

### Changed

- `dash-improve-my-llms[flask]>=2.6.0` (was 2.5.1), and
  `LLMS_PKG_FLOOR = (2, 6, 0)`. What arrives: icon autodiscovery, truthful
  sitemap `<lastmod>`, JSON-LD `publisher.logo`, and the llms.txt viewer
  banner de-dup (package-side, free).
- Every docs page's frontmatter now declares `lastmod:` with its REAL git
  last-commit date (2025-11-09 through 2026-08-19 — eleven pages, zero
  invented dates). The `Meta` model gains the field with a
  YAML-date-to-ISO validator; `register_page_metadata` passes it through;
  unset pages omit the tag — truth or silence. Deliberately not scripted
  from file mtimes, which reset on every Docker build and would re-invent
  the daily-lie sitemap 2.6.0 exists to end.
- `configure_seo(icons=)`'s `.ico` entry moved to the
  `assets/favicon/favicon.ico` copy (byte-identical to the root one
  index.html links) so the declared list is SET-equal to what 2.6.0's
  discovery finds.

### Added

- `tests/test_seo_icons.py`: discovery-vs-declaration set-agreement (the
  proof the fleet can rely on discovery alone once its pixels are right —
  order-inequality is not a failure, per the release notes) and
  sitemap-honesty pins (every emitted `<lastmod>` traceable to a
  frontmatter declaration; the undeclared home page carries none).

## [1.4.1] - 2026-08-19

### Changed

- `dash-clerk-auth` is now installed by requirements.txt (from the vendored
  tarball) rather than riding the image uninstalled. 1.4.0 shipped the whole
  sign-in surface — avatar, gate cards, delegation — but the deployed
  reference site could not render any of it because the package it wires was
  never on `sys.path`. Runtime posture is unchanged: with no `CLERK_*` keys
  the site is exactly as public as before, so forks inherit the capability,
  never a login wall. Alongside it, the fleet security floors are now
  asserted rather than merely permitted: `clerk-backend-api>=7.0.0,<8` and
  `cryptography>=50.0.0` (the four-advisory baseline dash-clerk-auth 1.0.1
  widened its cap for).

## [1.4.0] - 2026-08-19

The interactive gate and the real-time half of the fleet's analytics land on
the template. Humans meet a sign-in card on gated pages while agents keep
reading the machine surfaces through the data window — the two lanes split
onto separate axes, each flipped per host by one env var. The satellite
reporter grows a presence beacon so the hub board can show "active right
now" without waiting for a rollup. On THIS host the gate ships dark twice
over: every tier is public, and dash-clerk-auth is deliberately not in
requirements.txt (the vendored tarball exists for the docs' optional-auth
install command) — the presence beacon is what this deploy turns on.

### Added
- **The interactive gate** (`lib/gate_layouts.py`): every markdown docs page
  renders through a per-request verdict — sign-in card at HTTP 200 (with an
  optional live teaser demo via `lib/auth_demos.py`, table empty in the
  template), forbidden and 404 cards, the content on allow. The verdict is
  the new `access.resolve_page_access()`: docs fall open without Clerk,
  admin fails closed, and `?key=` never unlocks a browser layout. The gate
  switch is `PAGE_DEFAULT_TIER=auth` per deployment; `/`,
  `/getting-started` and the corpus pseudo-paths are pinned public so no
  env flip can gate the funnel. Card buttons ride
  `assets/auth_gate.js`/`.css` (satellite mode navigates to the primary
  with `?returnTo=`; local dev opens the Clerk modal).
- **The second tier axis, `llms_public`** (frontmatter, or
  `LLMS_PUBLIC_DEFAULT`, default open): a gated page's machine twin —
  `/<page>/llms.txt`, crawler HTML, the prerender — stays public while the
  interactive page is gated. That split is the data-window posture, and the
  later agent flip is `LLMS_PUBLIC_DEFAULT=0`, env only. The exemption
  never applies to a hub-imposed tier: a satellite's env default cannot
  loosen what the network restricted.
- **`GET /api/agent-key`** (`lib/agent_key.py`, all three backends): turns
  the browser's Clerk session into the hub-minted `?key=` that the "Copy
  for LLM" button (`assets/llms_copy.js`) now appends, so a copied URL
  keeps working inside an assistant that has no cookie. 204 for
  anonymous / Clerk-off / hub-down; `Cache-Control: private, no-store`
  always; the token is read from the `__session` cookie, never the query.
- **The presence beacon** (`lib/satellite_reporter.py`): a second,
  fail-silent daemon thread POSTs `{app, active}` to the hub's
  `/api/satellite/active` every 60s (`SATELLITE_PRESENCE_INTERVAL_S`,
  floor 30, `0` disables) — distinct human visitors inside the session
  window, the same derivation as the hub's own count. Display-only and
  ephemeral hub-side; the daily rollup stays the sole source of the daily
  numbers. A hub that predates the endpoint 404s harmlessly.
- Clerk avatar in the header (`components/header.py::create_clerk_avatar`),
  rendered only when Clerk is configured.

### Changed
- `render.yaml`: rollup cadence `SATELLITE_REPORT_INTERVAL_S=900` (the
  fleet is on paid instances and the hub board now reads near-real-time),
  the full Clerk satellite env block, and the two gate knobs — remembering
  that env/plan changes apply on Blueprint sync, not git push.
- `lib/auth.py`: the hand-rolled 0.9.0/0.9.1 satellite fixups are retired —
  both are upstream in the vendored dash-clerk-auth 1.0.2. What remains is
  capture-phase *delegation* (`_install_satellite_signin_delegation`,
  back-ported from the leaflet pilot 2026-08-19): late-rendered
  `#clerk-login-button`s get exactly one handler, preferring
  `buildSatelliteRedirect()` with `?returnTo=`, falling back to
  `redirectToSignIn` on origin+pathname so stale `__clerk_*` params never
  ride into the next sign-in.
- The corpus pseudo-paths (`/llms-small.txt`, `/llms-full.txt`) register
  `public` explicitly instead of falling through the tier default, so
  `PAGE_DEFAULT_TIER` can never gate them; `/` likewise (it registers via
  pages/home.py, which no frontmatter ever tiers).
- Vendored `dash_clerk_auth` 0.9.1 → 1.0.2 (the clerk-backend-api `<8`
  cap for the `cryptography>=50` floor, plus the avatar session fix).

### Fixed
- The peer-host key-leak test judges parsed origins, not substrings —
  bare-host matching flags a site's own links whenever a peer host is a
  substring of its own (`2plot.dev` ⊂ `leaflet.2plot.dev`; found by the
  leaflet pilot, this repo was saved only by its hostname). The invariant
  stated properly: any URL carrying a key must be same-origin.
- `lib/agent_key.py` records why it must not use
  `from __future__ import annotations`: PEP 563 turns the FastAPI
  `Request` annotation into a string resolved against module globals,
  where the locally imported class does not exist — the parameter silently
  becomes a required query field and the route 422s.

## [1.3.0] - 2026-08-15

Instrument first: the 402 groundwork lands on the template. The network's
metered lane is gated on ~30 days of crawl data (owner decision 2026-08-10);
this release is what makes that data exist and stay true on every satellite
forked from here — machine-surface demand reported per document, counted
once, tested, and tierable per deployment. No payment code ships here.
Rollout plan: `kickoff/KICKOFF-x402-instrumentation-rollout.md` (local).

### Added
- **The daily rollup now reports the machine surfaces** (the network's
  v3 analytics fields): unique bot visitors per day (`bot_visitors`, a
  daily distinct count), and llms.txt / robots / sitemap / page.json rows
  in `pages` with a per-row bot split — mirroring the hub's own
  self-report semantics exactly. These fetches were always recorded; they
  were only hidden from the report. A day with only machine-surface
  fetches is now reported instead of skipped — crawlers hammering
  llms.txt with zero human visits is exactly the signal the hub's
  day-pass board exists to see.
- **The machine-surface rollup is tested** (`tests/test_traffic_rollup.py`)
  — 15 hand-checkable cases pinning the partition (every path is a page
  visit or a machine-surface hit, never both), the machine-only-day
  report, the per-row bot split, and the distinct `bot_visitors` count.
  This data is the evidence base for the network's 402 pricing decision;
  untested measurement code deciding a revenue model was the wrong risk
  to carry.
- **Tier registrations for the corpus documents.** Every satellite built
  from this template now declares access tiers for `/llms-small.txt` and
  `/llms-full.txt` (served by dash-improve-my-llms ≥ 2.4.0; inert on older
  versions): `LLMS_SMALL_TIER` / `LLMS_FULL_TIER` env vars set them
  locally (unset = public; documented in `.env.example` and visible in
  `render.yaml` so every fork sees the knob), and the hub's page-tier
  ceilings can tighten either network-wide with no redeploy here. The
  dependency-floor message notes the 2.4.0 requirement for the tier
  documents.
- **Generic version placeholder `{{VERSION:<distribution>}}`** (new
  `lib/versions.py`, used by both markdown loaders). Prose may now state
  the installed version of *any* package — not just dash-improve-my-llms —
  so every satellite can write `{{VERSION:<its-pypi-name>}}` for the
  library it documents and a package upgrade propagates to the browser
  page, the copy button, `/llms.txt` and every `/<page>/llms.txt` on the
  next deploy, with no prose edit. `{{DIMLL_VERSION}}` remains as a legacy
  alias. Fenced code blocks and inline code spans are left verbatim (the
  network-standard page shows the syntax in a fence), and a placeholder
  naming an uninstalled distribution fails the boot instead of leaking.
  The identity tests now also sweep for bold version claims next to any
  PyPI link, not only dash-improve-my-llms's.

### Fixed
- **Machine-surface fetches were double-counted.** `_SKIP` excluded
  `/llms.txt`, `/robots` and `/sitemap` from page visits by substring —
  but `/llms.txt` does not substring-match `/llms-small.txt`, so the tier
  documents and `page.json` twins landed in BOTH `load_visits` and
  `load_agent_hits`, inflating `human_hits`/`bot_hits`/`pages` for
  exactly the surfaces the 402 board prices. `_SKIP` now names all three.
  The hub's `traffic_insights._SKIP` has the same gap (its comment claims
  the exclusion; its tuple doesn't deliver it) — port this fix there
  before the data window opens.
- **Dash-built components rendered empty props tables.** The
  numpy-docstring branch in `lib/directives/kwargs.py` (for
  dash-mantine-components' hand-written docs) shadowed the base
  markdown2dash parser for the `Keyword arguments:` format that
  dash-generate-components emits — the format of every component a
  library satellite documents — so their `.. kwargs::` tables rendered
  silently empty. Found on muicharts' `/api`; pannellum's likely affected
  too. The directive now falls back to the base parser for that shape.

## [1.2.5] - 2026-08-01

### Fixed — `scripts/smoke_live.py` failed CD on healthy sites

The post-deploy battery is the fleet's deploy gate: `cd.yml` runs it against
the live host after every merge and its exit code decides whether the run
goes green. Its `fetch` was a single `urlopen` — no retry, no wake-up — while
most of the fleet sits on Render tiers where a cold start or a dropped
connection is routine. Measured on dash-flows-upgraded: two runs minutes
apart against the same host, `FAIL canonical on /interactions` then
`ok canonical on /interactions`. A misdiagnosed failure is worse than a slow
one; it sends you to look at canonical tags that were correct all along.

Both fixes already existed in-fleet and never met (blueprint LESSONS §21
states the rule outright):

- **A wake-up loop before the first check.** `/healthz` is polled up to 24
  times, 10s apart — deliberately wider than §21's "12×5s is plenty",
  because a free-tier cold start routinely takes 60–90s and the window only
  costs time when the host is actually down. Awake means `ok: true`, not any
  200: Render's loading page and a CDN error page can both be 200s. A host
  that never wakes is ONE failure ("nothing else was tested"), not a cascade
  of forty per-check failures that all mean the same thing.
- **A retry ladder inside `fetch`** — the shape `scripts/network_smoke.py`
  already had, and that leaflet's copy of this very script grew without the
  fix ever flowing back to the canonical here. Transport errors and 5xx
  retry with backoff; 2xx/3xx/4xx return immediately, because a 404 is a
  verdict and retrying it only slows the battery. Retries print to the CD
  log — a green run that shows retries is a host worth watching.

Proven live before shipping, twice over: on the first run after the change,
flows' llms.txt dropped the connection mid-body (`IncompleteRead`) and passed
on retry — the exact flake that triggered this fix — and a run against
email.2plot.dev saw its OWN pages do the same on two *fatal* checks that
would have turned that deploy red.

Tunables (env, so satellites stretch them without editing the file):
`SMOKE_WAKE_ATTEMPTS`, `SMOKE_WAKE_INTERVAL_S`, `SMOKE_FETCH_RETRIES`. Exit
semantics unchanged; no check weakened, removed, or reordered. The file
remains the canonical copy — satellites take it verbatim on their next touch.

## [1.2.4] - 2026-08-01

### Fixed — the network bulletin was never wired up

`NETWORK_BULLETIN_URL` has been set in production, pointing at a hub endpoint
that works, against code that never read it. The wiring sat **commented out**
in `run.py` under a note saying "2plot.dev does not serve
/api/network/bulletin yet". The hub started serving it; the comment did not
change.

Nothing failed. `configure_bulletin` is opt-in, so an unwired app makes no
request at all and the viewer header renders perfectly well on the package's
built-in tips and an "No announcements." empty state. The only symptom was an
announcement that never appeared — which nobody goes looking for.

Now `lib/bulletin.py`, shaped like `lib/proxy.py` and `lib/access.py`: a
`configure()` that returns whether it wired, and a boot line that says which
of the two states the process is in. No commented-out code to go stale, and
`tests/test_bulletin.py::test_run_py_wires_it_rather_than_leaving_it_commented_out`
fails the moment someone comments it out again — commented wiring cannot
define the name it asserts on.

Two details worth keeping:

- **`app_id` comes from `SATELLITE_APP_KEY`**, reused from
  `lib.satellite_reporter.app_key()` rather than hard-coded. The hub scopes
  announcements by `?app=` and uses it to see which satellites actually render
  the bulletin, so a fork left announcing itself as `boilerplate` would
  receive this template's news *and* be miscounted. One notion of "which
  satellite am I", not two that can disagree.
- **The TTL is floored at 60s.** It is configurable via
  `NETWORK_BULLETIN_TTL_S`, and a small value would refetch on nearly every
  llms.txt view; junk falls back to the default rather than raising at boot.

Verified end to end against the live hub: the rendered header carries the
hub's own tip wording ("Append /llms.txt to any URL") rather than the
package's default ("Append /llms.txt to any page URL"), and the current
announcement.

One thing that cost time and is worth recording: on macOS the package's
bulletin client fails with `CERTIFICATE_VERIFY_FAILED`, because it uses a bare
`urlopen` with no CA bundle and the system Python has no OS trust-store
integration. That is a local-development artifact only — Linux containers have
a working store — but locally it looks exactly like a broken fetch. Run with
`SSL_CERT_FILE=$(python -c "import certifi;print(certifi.where())")` to tell
the two apart. `scripts/smoke_live.py` and `scripts/audit_links.py` already
carry their own certifi context for the same reason.

### Changed — one identifier for this app on every hub surface

`AD_APP_ID` now defaults to **`boilerplate`**, not
`dash-documentation-boilerplate`. Four modules present an identity to the hub
— `lib/ad_client.py`, `lib/satellite_reporter.py`, `lib/hub_client.py` and
`lib/bulletin.py` — each with its own fallback, and the ad client was the odd
one out. The visible cost was a column on `/admin/ad-board` that did not line
up with `/traffic`; the invisible one is that `hub_client.app_id()` falls back
to `AD_APP_ID` when `SATELLITE_APP_KEY` is unset, so a deployment that set the
long name for ads alone was silently presenting it as its hub identity too.

`lib/satellite_reporter.app_key()` still refuses to chain to `AD_APP_ID`. The
two agreeing here is a convenience, not a contract — leaflet.2plot.dev runs
`AD_APP_ID=dash-leaflet2` against directory key `leaflet`, and setting one for
ads must never re-key a satellite's analytics series.

`render.yaml` now sets `AD_APP_ID` explicitly rather than leaning on the code
default, so the deployed value is visible in the blueprint.

**This splits ad history.** The ad server keys impressions and clicks by
`app`, so anything already logged under `dash-documentation-boilerplate` stays
there — worth a look at `/admin/ad-board` on 2plot.dev before assuming the
numbers reset.

### Added — `.env.example`

The repo had none, so every configurable was discoverable only by reading
`lib/`. Each block states what turns ON when set and what the app does when
it is not — because almost every one of these fails silently rather than
loudly: no `APP_BASE_URL` deindexes a fork, no `CROSS_APP_WEBHOOK_SECRET`
means the hub simply never charts this app, no `NETWORK_BULLETIN_URL` renders
a header that looks complete.

Not gitignored (the pattern is `.env`, exactly), and `.dockerignore` already
whitelists it against the `.env*` exclusion added in 1.2.2.

`render.yaml` gains `NETWORK_BULLETIN_URL` so the deployment documents itself
rather than depending on someone remembering to set it in the dashboard.

## [1.2.3] - 2026-08-01

**The social card, finished.** 1.2.2 closed three of four defects and left
this one open because the artwork did not exist. It does now.

### Added — `scripts/make_social_card.py`

Renders the 1200×630 card: the artwork composited onto a frame carrying the
brand, tagline and domain, using the manifest's own `background_color` and
`theme_color` so the card, the browser chrome and the install splash cannot
disagree. Output lands in `build/social-cards/<domain>.png`, which is
gitignored.

A TEMPLATE FILE, and that is the point — pass `--brand/--tagline/--domain`
and every satellite is framed identically, instead of each card being made by
hand once and drifting. Three details that are not incidental: the artwork's
alpha bounding box is cropped before fitting (`assets/ddb.png` carries ~66px
of transparent margin that would otherwise be centred as if it were image); a
brand too long for two lines shrinks once rather than colliding with the
domain strip; and fonts resolve from a candidate list (macOS, then
Debian/Ubuntu) rather than being bundled, because shipping a licensed TTF in
a template every satellite forks is a question best not answered.

Pillow stays out of `requirements.txt`. Nothing at runtime renders images,
and a docs site should not carry an image library into production for a
script run by hand every few months.

**1200×630 = 1.91:1**, the Open Graph documented ideal, which also degrades
cleanly into Twitter's 2:1 `summary_large_image` slot. Deliberately not
leaflet's 1280×515 (2.49:1), which is wider than both and gets cropped on
each — and what sits at that URL today is the 2plot wordmark rather than a
per-site card at all. This is the shape for the network to converge on.

### Changed — `og:image` moved to the CDN

```
was:  https://boilerplate.2plot.dev/assets/ddb.png   784×741  (1.06:1)
now:  https://cdn.2plot.ai/github_assets/boilerplate.2plot.dev.png  1200×630
```

The old image's declared dimensions were honest, so nothing was broken — it
was simply near-square, and `summary_large_image` letterboxed it into a wide
slot with bars either side.

Moving it off the app is the network rule and it is about cold starts, not
tidiness: a card the app serves is fetched by the scraper at unfurl time, and
on a cold free-tier container that request lands mid-wake and times out. The
preview renders blank **once**, and the platform caches the miss — so the
first person to share the link poisons it for everyone. The CDN has no cold
start.

`og:image:secure_url` and `og:image:type` join the auxiliaries in
`templates/index.html`, matching what leaflet carries. Both are tags Dash does
not emit, which is the only reason they belong in the template.

### Added — the live card check that no offline test can make

The card's dimensions are now declared in **three** places: `lib/constants.py`,
`templates/index.html`, and the CDN object itself. `test_social_card.py` pins
the first two against each other, but nothing offline can look at the third —
so replacing the uploaded file with a differently-shaped one would leave every
test green while the platform reserves the wrong box and crops into it.

`scripts/smoke_live.py` now fetches the real file after every deploy and reads
its actual pixel dimensions out of the PNG's IHDR chunk, checking them against
the declared tags, plus the ratio, plus that `og:image` is neither empty nor
app-served. Two tests prove the check fires rather than merely existing:
`test_a_reshaped_card_on_the_cdn_fails_the_deploy` and
`test_an_empty_og_image_fails_the_deploy`.

That second case is not hypothetical — it is 2plot.dev's live state today, and
the reason `kickoff/` now holds a handoff for it.

`fetch()` in that script changed from `errors="replace"` to
`errors="surrogateescape"` to make this possible. `"replace"` substitutes
U+FFFD for every invalid byte and is one-way, so the PNG header was gone
before it could be read; surrogateescape round-trips exactly and behaves
identically for text.

### Changed — the two peer tests narrowed to peers

`test_smoke_script_rejects_a_peer_serving_its_spa_shell` and
`test_a_dead_peer_is_reported_but_does_not_fail_the_deploy` stubbed *every*
off-host URL, which now included the CDN-hosted card and failed the
(correctly fatal) card checks. The card is off-host but it is this
deployment's own responsibility, not a peer's — the distinction 1.2.2 drew
between "this host is fatal, somebody else's host is a warning" holds, the
stubs just needed to respect it.

### Changed — `build/` and `kickoff/` are gitignored

`build/` because the card is published to the CDN and never committed or
served. `kickoff/` because handoff notes start a session in *another* repo: a
task list for 2plot.dev has no business in the template's checkout, and every
satellite forking this repo would inherit a to-do that was never theirs.

## [1.2.2] - 2026-08-01

**Finishing 1.2.1, and the three things it exposed.** 1.2.1 shipped the right
template and half the change. Everything below was measured against the live
site rather than a local boot, because the local/deployed gap is precisely
what hid the first defect for a day.

### Fixed — the 1.2.1 files were never committed

`assets/favicon/` (the whole icon set plus `site.webmanifest`) and
`tests/test_social_card.py` were sitting UNTRACKED. The committed template
pointed at `/assets/favicon/…`, the deploy builds from git, so production
404'd the manifest, the apple-touch-icon and every PNG icon link — the entire
installable-app surface — while every local boot looked perfect because the
files were on disk. Nothing in the app reported it; `git status` was the only
place it appeared. Measured on the live site:

```
/assets/favicon/site.webmanifest      404
/assets/favicon/apple-touch-icon.png  404
/assets/favicon/favicon-32x32.png     404
```

The guard test was untracked too, so the one thing that would have caught this
had never run in CI either. Both are now tracked, and
`test_every_asset_the_template_references_resolves` widens the check from
"the manifest icons resolve" to "**every** `/assets/…` the template
references resolves" — because the failure was never about icons, it was
about a template referencing a file the repository does not have. A checkout
is what CI tests, so it fails there the moment something is not committed.

The manifest's contents needed no change; they were already correct.

### Fixed — the fork source's brand on every share card

`PAGE_TITLE_PREFIX` still read `"Dash Pip Components | "`, inherited from the
upstream this template was forked from and never changed. That is not only a
browser-tab string: Dash passes each page's title straight into `og:title` and
`twitter:title` (`dash/_pages.py:_page_meta_tags`), so every unfurl of
`boilerplate.2plot.dev` advertised **a different site**, while `<title>`,
`og:site_name` and the `/llms.txt` H1 all correctly said this one.

Now `f"{SITE_SHORT_NAME} | "`, matching the network convention the other
satellites already use (`dash-leaflet2 | `, `Dash Email | `) and derived from
the brand rather than retyped, so the two cannot drift.
`tests/test_site_identity.py` pins the prefix, the derivation, the rendered
`og:title`/`twitter:title`, and sweeps the identity surfaces for any surviving
mention of the old brand.

Nobody sees their own share cards, which is the whole reason this needed a
test rather than a look at the page.

### Fixed — `twitter:url` advertised `http://` (`lib/proxy.py`)

Dash builds that tag from `request.url`, and on Flask `request.url` comes from
`wsgi.url_scheme`. Requests arrive over Cloudflare → Render → gunicorn and the
last hop is plaintext, so production told every social scraper
`http://boilerplate.2plot.dev/`. `og:url` looked fine throughout because the
template hard-codes it.

gunicorn does try to fix this — it rewrites the scheme from
`X-Forwarded-Proto`, but only when the immediate peer is in
`forwarded_allow_ips`, which defaults to `127.0.0.1`. Reading the header
ourselves one layer above gunicorn sidesteps the question entirely:
`HTTP_X_FORWARDED_PROTO` is in the environ either way.

Notes on the implementation, all of them load-bearing:

- **Only the scheme is taken.** Host is not rewritten from
  `X-Forwarded-Host`; `BASE_URL` is already this project's single source of
  truth for the public origin, and a second header-derived notion of "what
  host am I" is how a fork ends up serving two.
- **The FIRST entry of the header wins.** Proxies append, as with
  `X-Forwarded-For`, so the last entry is the hop nearest the app — the
  plaintext one being seen past. Reading from the wrong end reinstates the
  bug and still passes a single-proxy test, so there is a test for it.
- **`TRUST_PROXY_HEADERS=0`** turns it off. This trusts a header from whoever
  connected, which is correct behind Render (it overwrites the header on every
  inbound request) and wrong for an app exposed directly, where a client could
  forge it.
- **The server object is wrapped, never rebound** — `app.server` stays the
  Flask/FastAPI/Quart instance that gunicorn imports as `run:server` and that
  `run.py` hangs `before_request` off. All three backends are handled.

The sibling `leaflet.2plot.dev` already serves `https` in the same tag from an
identical Cloudflare/Render/gunicorn stack with no proxy configuration of its
own; the difference we could observe is that it deploys as a Docker service
rather than a native one, which would plausibly put the proxy on loopback and
satisfy gunicorn's default. That is inference — Render's internal topology is
not visible to us — and the fix deliberately does not depend on which
explanation is true.

### Added — client-side URL sync on SPA navigation

Ported from `leaflet.2plot.dev` and adapted: that site hard-codes a static
canonical and this one does not (dash-improve-my-llms injects a per-page one),
so this version only ever *corrects* tags that exist and never creates one.

Three tags go stale after the first client-side route change, each for a
different reason: `og:url` is static in the template, `twitter:url` is
server-rendered from the entry request, and the injected canonical is right on
arrival and wrong thereafter. Dash routes through `history.pushState`, which
fires no event, so the tags advertise the landing URL for the rest of the
session. The origin is read from the existing `og:url` tag rather than
hard-coded a second time.

This helps Google, which runs JS. It cannot help social scrapers, which do
not — which is why the scheme half had to be fixed server-side.

### Changed — `test_exactly_one_canonical_tag_for_browsers` counts elements

It counted the substring `rel="canonical"`, and the new sync script's selector
(`link[rel="canonical"]`) is not a canonical tag. Same lesson as the
`dv-banner` chrome check it sits beside: match the markup, not the words, so a
file may legitimately discuss what it is being checked for.

### Still open — the card image is not on the CDN

`og:image` remains `/assets/ddb.png`, 784×741, served by the app. The declared
dimensions match the file honestly, so nothing is broken, but it misses two
network rules: cards belong on `cdn.2plot.ai` so a cold free-tier container
cannot blank a preview, and `summary_large_image` wants roughly 1.91:1
(leaflet's is 1280×515). `https://cdn.2plot.ai/github_assets/boilerplate.2plot.dev.png`
does not exist yet, and pointing `og:image` at a 404 is strictly worse than
the present state, so this waits on the asset. When it lands, the change is
`OG_IMAGE_URL` plus the width/height constants, plus the `og:image:secure_url`
and `og:image:type` tags leaflet carries.

## [1.2.1] - 2026-07-31

**The social card and the installable app** — the two surfaces that live
entirely outside the app, and so fail where nobody is looking. Found while
rolling the standard onto `leaflet.2plot.dev`, which inherited the same shapes
from this template. Satellites copy `tests/test_social_card.py` verbatim.

### Fixed

- **Two `og:image` tags per page, and the wrong one won.** `templates/index.html`
  declared `og:image` / `twitter:image` statically while Dash also emits both
  per page. With no `image_url=` passed, Dash *inferred* an image from the
  assets folder, found `assets/logo.svg`, and emitted it alongside the static
  tag. Every major scraper rejects SVG, and the inferred tag came last — so the
  card described so carefully in the template lost to an image nothing can
  render. `lib/constants.OG_IMAGE_URL` is now passed to `register_page`, and
  the template keeps only the auxiliaries Dash omits.
- **The same duplication across nine other tags** — `description`, `og:type`,
  `og:title`, `og:description`, `twitter:card`, `twitter:url`, `twitter:title`,
  `twitter:description`, `twitter:image` were all declared statically *and*
  emitted by Dash. The static copies described the site where Dash's describe
  the page, so the duplicate was both redundant and the less accurate of the
  two. `test_no_meta_tag_dash_emits_is_also_declared_statically` pins the rule.
- **The home page published an empty `description`.** `pages/home.py` never
  passed one, so Dash emitted `description`, `og:description` and
  `twitter:description` as `content=""` on the most-linked page on the site.
- **The web app manifest was inert, and named the wrong product.** Its link and
  the `apple-touch-icon` were commented out behind a note saying the files were
  missing — a note that outlived their arrival in `assets/favicon/` — and the
  commented hrefs pointed at `/assets/`, one level above where they live. The
  manifest itself still read *"Dash Email — Email components for Plotly Dash"*,
  copied in from another repo; that string is what an installed app would have
  shown on the home screen. Fixed, linked, and its `theme_color` reconciled
  with the `theme-color` meta tag.

### Added

- `tests/test_social_card.py` — a template file. Asserts the image is declared
  exactly once, is absolute, is not an SVG and resolves; that the manifest is
  linked, served, correctly named and has resolving icons; and that
  `templates/index.html` is still wired in, since it looks removable (
  dash-improve-my-llms appears to cover OpenGraph) and is not — its injection
  runs only on the prerender path, which social scrapers do not take.
- `lib/constants.OG_IMAGE_URL` / `_WIDTH` / `_HEIGHT` / `_ALT` — the per-site
  values a fork changes.

## [1.2.0] - 2026-07-31

**The 2plot network standard, landed on the template.**

`2plot.ai` (the network root) and `2plot.dev` (the section hub) shipped this
first; satellites are next, and this repo is the one they fork. So the point
of this release is not that `boilerplate.2plot.dev` complies — it is that the
files a satellite copies verbatim now carry the standard with them. The new
[Network Standard](https://boilerplate.2plot.dev/network-standard) page is the
per-site checklist.

The three obligations below share a shape, and it is worth naming: **every
failure they prevent is silent.** Nothing errors, no dashboard turns red, and
the damage accumulates for months. That is why each one is now pinned by a
test rather than by a convention.

### Added — explicit site identity (`lib/constants.SITE_BRAND`)

One constant, `"Dash Documentation Boilerplate — the 2plot network's
template"`, now reaches every surface that states what this site is:
`Dash(title=)`, `register_page_metadata(path="/", name=…)`, the first line of
`pages/home.md`, and `templates/index.html` (`og:site_name`, `og:title`,
`twitter:title`, the schema.org `SoftwareApplication.name`, the `<noscript>`
heading).

What this fixes is not cosmetic. `dash-improve-my-llms` resolves the
`/llms.txt` H1 and the llms viewer's brand chip through
`resolve_site_title(home_page_name, app.title)`, and given nothing useful it
publishes what it finds. On this host that was the `Dash()` constructor's
default title: every agent that fetched `boilerplate.2plot.dev/llms.txt` cold
was told the site is called **"Dash"**. The page rendered perfectly the whole
time. 2.3.4 fixed half of it — generic candidates (`Home`, `Index`, `Dash`)
are now skipped rather than served — but a package cannot invent a name; the
other half is stating one.

Naming rules, from the standard: the brand says what the site *is*; the
package name (`dash-documentation-boilerplate`) belongs in the description;
"Pip Install Python" is the byline and never the site name.

`tests/test_site_identity.py` pins all of it, including the direction that is
easy to lose — that `SITE_BRAND` is not itself one of the generic values the
package skips.

### Added — the internal-traffic contract, both halves

The point of truth is [2plot.ai's satellite-analytics
document](https://2plot.ai/docs/satellite-analytics), "Internal traffic": any
request whose User-Agent contains `2plot-internal` is network machinery
talking to itself and is counted **nowhere**.

*Inbound.* `lib/analytics_tracker.track_visit` drops token-carrying requests
at write time, **before** `detect_device_type`. The ordering is the whole
point: a health sweep and a CI battery both look like bots, so classified
first they land in `bot_hits` and get reported to the hub as crawler interest
in these docs. `/healthz` and `/health` stopped being stored at all —
`lib/traffic_rollup` already filtered them on the way out, but a row that
exists and must be discounted is still a row somebody has to know about.

*Outbound — the half that was missing here.* Every call this host makes to
another network host now sends `INTERNAL_UA`:

- `lib/ad_client.py` → `2plot.dev`, **once per docs page view**;
- `lib/satellite_reporter.py` → `2plot.ai`, hourly;
- `lib/hub_client.py` → `2plot.dev`, per agent-key verify and tier fetch;
- `scripts/network_smoke.py`, `scripts/smoke_live.py`, `scripts/audit_links.py`.

The ad client is the one that mattered. All of these were arriving as
`python-requests/2.x`, which matches the hub's own bot patterns — so this
satellite's readers were inflating 2plot.dev's `bot_hits`, once per page view,
and had been for as long as the ad slot has existed. The battery scripts keep
their Googlebot and Chrome tokens *and* append the internal one: the target
still exercises exactly the path under test, it just knows the caller is
machinery. The click beacon is the deliberate exception — a browser cannot set
a User-Agent, and a click is a real person.

`tests/test_internal_traffic.py` proves the exclusion reaches the numbers the
hub actually charts (`human_hits` / `bot_hits` in `daily_rollup`), proves the
positive case still counts (a rule that drops everything would satisfy the
negative assertions), and asserts the outbound header on all three clients and
all three scripts.

### Added — `scripts/network_smoke.py`, run in three seats

The same named checks against the CI container, against production after a
deploy, and in-process from `tests/test_network_smoke.py`, so a failure reads
identically wherever it happens. It proves identity (the `/llms.txt` H1 is the
brand, verbatim), the deployed artifact (the robots.txt crawler split, which
is the only fingerprint visible from outside — pip metadata is not), that no
owner-only surface leaks, that a crawler gets prose and not the JavaScript
stub, and that agents and browsers get different content types under a
`Vary: Accept`.

The in-process seat is not redundant: a script that only ever runs in CI and
after a deploy is exactly the code that rots, where a typo turns a check into
a silent pass. That test also breaks a check on purpose and requires the
battery to report it.

### Changed — CI on the network baseline

`.github/workflows/ci.yml` is now a template file in its own right:
least-privilege `permissions: contents: read`, `timeout-minutes` on every job
(the default is six hours, which is how one hung `curl` burns a day of runner
minutes), `docker/setup-buildx-action` with a `type=gha` cache, and version
fingerprints asserted **inside the built image** rather than in the runner.
The container is booted and probed by the battery before anything is allowed
to merge. `cd.yml` runs the battery against the live host before
`smoke_live.py`.

`tests/conftest.py` now boots the app secretless, the way CI's container does:
every `CLERK_*`, `CROSS_APP_WEBHOOK_SECRET` and `SESSION_SECRET` is pinned to
`""` **before** `run.py` is imported, because `load_dotenv()` runs during that
import and a developer's local `.env` would otherwise flip the app into a
configured posture and quietly invalidate every fail-closed assertion in
`tests/test_access.py`. The analytics ledger moves to a temp dir in the same
block — the suite had been appending its own hits to the repo's checked-out
`visitor_analytics.json`.

Added `.github/dependabot.yml` with a `dash-network` group (a package release
lands as one reviewable PR per repo, not five) and an advisory `pip-audit`
job.

### Changed — dependency floors

- **`dash-improve-my-llms` >= 2.3.4** (from 2.3.2). The network standard;
  `run.py`'s startup floor and CI's in-image fingerprint both assert it.
  There is no vendored copy of this package anywhere in the repo — the stale
  comments in `Dockerfile`, `render.yaml` and `README.md` that still described
  one are gone. `vendor/` holds `dash_clerk_auth` alone.
- **`gunicorn` >= 23.0.0** (from 21.2.0). 21.x carried two HTTP
  request-smuggling CVEs (CVE-2024-6827, CVE-2024-1135), both fixed in 23.0.
  `markdown2dash` 0.1.2 declares `gunicorn>=21.2.0,<22.0.0` — a markdown
  parser pinning a WSGI server — which pip cannot reconcile with that floor,
  so markdown2dash is installed with `--no-deps` and its real dependencies
  (`docutils`, `jsonpath`, `mistune`) are listed in `requirements.txt`
  instead. Every install path does the same two commands: `requirements.txt`,
  `scripts/dev.sh`, the `Dockerfile`, `render.yaml`'s `buildCommand`, CI, and
  the README. CI's in-image assert is what keeps the dodge honest.

### Added — `.dockerignore`

Found by booting the image locally as part of verifying this release: the
Dockerfile ends in `COPY . .`, so a developer's `.env` was being baked into
the production image. The container died at boot with `Could not import
dash.backends._fastapi` — the local file said `DASH_BACKEND=fastapi` and the
image has no FastAPI extra. It never appeared in CI, where the checkout has no
`.env`, which is precisely what made it worth a file rather than a lesson: the
same `COPY` would carry real Clerk keys and the webhook secret into an image
layer on any machine that has them. The ledger, session store, virtualenv and
`node_modules` are excluded too. `docs/**/*.md` deliberately is **not** —
those files *are* the app.

### Note on versioning

1.1.0 was declared in `README.md` and `lib/constants.APP_VERSION` but never
cut here; everything previously sitting under `[Unreleased]` ships as part of
1.2.0. `templates/index.html`'s `softwareVersion` and `APP_VERSION` now agree,
which `tests/test_config.py` asserts.

---

Previously unreleased, now shipping as part of 1.2.0 — three threads of work:
the CI/CD system, network analytics reporting, and the upgrade to
`dash-improve-my-llms` 2.2.0.

2.1.0 was assigned during that package's development and never published, so
there is no 2.1.0 anywhere and 2.0.0 upgrades straight to 2.2.0. Work
described here as "2.1-era" in earlier drafts shipped as part of 2.2.0.

### Changed — dash-improve-my-llms from PyPI (2.3.3); vendored copy removed

The four-host verification gate passed, `dash-improve-my-llms` published, and
this repo switched from the vendored sdist to the PyPI pin
(`dash-improve-my-llms[flask]>=2.3.2`) — the Phase-5 step the vendor block
always anticipated. `vendor/dash_improve_my_llms-*.tar.gz` is gone; CI's ASGI
legs and the Dockerfile install from PyPI too. `vendor/` still carries
`dash_clerk_auth` (not on PyPI, deliberately outside requirements.txt).

The floor resolves to 2.3.3, which recategorises the Anthropic crawlers:
`ClaudeBot` — the actual *training* crawler — moves to `Disallow`, while the
user-triggered and search fetchers `Claude-User` / `Claude-SearchBot` are
allowed, matching the intent the OAI-SearchBot fix established for OpenAI.
It also strips unexpanded directive lines from resolved prose. The artifact
fingerprint in `tests/test_llms_routes.py` and `scripts/smoke_live.py` now
asserts the full crawler split, so a host running a stale build fails its
post-deploy battery by name.

Verifying that fingerprint exposed a real misconfiguration:
`run.py` set `block_ai_training=False`, so the training bucket was never
emitted and every training crawler was silently allowed — the opposite of the
"blocks AI training, allows AI search" policy this project documents, and it
would have made 2.3.3's ClaudeBot recategorisation invisible on this host.
Now `block_ai_training=True`, matching the documented policy and the rest of
the network.

### Changed — production rollout: re-vendor 2.3.2 / 0.9.1, live hub contract

Deployment prep for `boilerplate.2plot.dev` (rollout step 4; the hub's auth
endpoints are now live in production).

- **`dash-improve-my-llms` 2.3.0 → 2.3.2** (vendored). The vendored 2.3.0 was
  a pre-fix build whose robots.txt disallowed OAI-SearchBot — ChatGPT
  search's crawler, exactly the audience these surfaces exist for. 2.3.2
  allows it. `User-agent: OAI-SearchBot` → `Allow: /` in a live host's
  `/robots.txt` is the fingerprint that it runs the fixed artifact (pip
  metadata is invisible from outside); `test_robots_artifact_fingerprint`
  now asserts it locally so a vendored regression fails CI, not production.
  2.3.1 was assigned during development and never published.
- **`dash-clerk-auth` 0.9.0 → 0.9.1** (vendored, built from the
  Dash-Clerk-Auth-Hook working tree). 0.9.0 ships a bug hitting every Clerk
  satellite forked from this template: clerk-js v5 auto-instantiates from the
  script tag's `data-*` attributes and reads the *instance* domain, so on a
  satellite the user button never mounts (dead avatar) while server-side
  session verification keeps working. 0.9.1 emits
  `data-clerk-domain="<satellite_domain>"` on the tag when `is_satellite=True`.
  This app runs no Clerk by design — the bump is for the template's sake.
  `lib/auth.py`'s fixup #1 guards on the attribute's absence, so it degrades
  to a no-op under 0.9.1 and stays for forks still on 0.9.0.
- **`lib/hub_client.py` aligned with the hub's real contract.** Two functions
  predated the hub going live. `current_key()` now sends
  `{"token": <Clerk session token>, "app": ...}` — the hub 401s any
  caller-asserted identity (`user_id` in the payload is the forgery path) and
  verifies the token against Clerk's JWKS, minting at `scope=auth`, never
  admin. Call it on copy-button click, never on page render; `None` degrades
  to copying the plain URL. `hub_tiers()` is no longer a stub: signed POST
  `/api/page-tiers` `{"app": ...}` → `{"tiers": {path: tier}, "ttl": s}`,
  cached for the returned TTL with failures cached 60s — so a down hub costs
  one timeout per window, not one per request, and resolves to the local
  tier, which the ceiling rule guarantees can never loosen anything.
  `verify()` already matched the hub and is untouched.

### Added — AI/LLM surfaces (dash-improve-my-llms 2.2.0)

- **`lib/network_directory.py`** — the peer/affiliated/external directory,
  defined once here and copied verbatim into every satellite. Publishes
  `<link rel="related">` tags, a `## Network` section in `/llms.txt`, and
  followed links in the prerendered body, so an agent landing on one satellite
  can enumerate the rest. Filters the app's own URL out of `peers`.
- **Wordmark** — `"2"` + morse(`plot`) + `"ai"`, drawn as columns of dots and
  dashes in the header of the rendered `llms.txt` view. No period glyph: the
  morse block already separates the halves, and a literal `.` beside it reads
  as punctuation dropped into a graphic. The renderer turns a suffix ending in
  `i` into an upward flourish, so `"ai"` draws as `a` plus that mark, with the
  real domain in `label` for screen readers and the SVG `<title>`. It lives in
  the shared module rather than per-app, which is what keeps one mark across
  the network instead of twelve near-identical ones.
- **Page `llms.txt` documents are no longer dead ends.** Each now opens with
  the site index, the network index one level up the hub chain (`2plot.dev`,
  correct for a `*.2plot.dev` subdomain), and the sitemap. These documents are
  usually read in isolation — pasted into a chat, handed to an agent — and an
  agent fetches a URL rather than crawling from one, so previously its
  exploration simply stopped there.
- **The same URL content-negotiates.** Agents, crawlers and curl get the
  Markdown byte for byte; browsers get it rendered behind a header carrying
  the network identity. `?raw=1` and `?format=html` override, both variants
  send `Vary: Accept`, and the rendered view is `noindex` so it never competes
  with the page it documents. Verified identical on Flask, FastAPI and Quart.
- **`docs/networks/networks.md`** — the guide for satellite authors: the three
  tiers, why per-host SEO can't express any of this, the wordmark and bulletin
  conventions, the one-URL-two-audiences contract, and the verification
  commands.
- **Network bulletin left deliberately unwired.** `configure_bulletin()` sits
  commented next to `add_llms_routes` with a pointer to the contract.
  `2plot.dev` does not serve `/api/network/bulletin` yet, and pointing at a
  dead endpoint gains nothing: the client degrades silently and the header
  renders fine without it — the "Tips for getting started" and "What's new"
  panels use the package's built-in defaults, which a bulletin only overrides.

### Added — Clerk authentication and llms.txt access control

Opt-in, and off in a default clone. This is the template every `*.2plot.dev`
subdomain is forked from, so the goal was a pattern good enough to copy rather
than a one-off. Requires `dash-improve-my-llms` 2.3.0 (`configure_access`,
`configure_viewer_identity`) and the vendored `dash-clerk-auth` 0.9.0, which is
deliberately **not** on the active requirements line — a default install should
not pull in an auth stack the site does not use.

- **`lib/auth.py`** — adapted from `2plot_leaflet/lib/auth.py`, the
  implementation already sharing authenticated state across `2plot.ai` →
  `2plot.dev` → `leaflet.2plot.dev` in production. Keeps both satellite fixups
  for `dash-clerk-auth` 0.9.0 (clerk-js reads `domain` as a *constructor*
  option from `data-clerk-domain`, and a satellite must `redirectToSignIn()`
  rather than open a modal that 403s), the `pk_live` auto-enable so production
  cannot silently boot in primary mode, `DISABLE_CLERK=1`, and call-time env
  reads. Changed for the template: the satellite domain derives from
  `APP_BASE_URL`, which every deployment must set anyway — one variable rather
  than two, and one fewer way to announce another site's domain to Clerk.
- **`lib/page_tiers.py`** — `public < auth < admin < hidden`, declared in
  markdown frontmatter (`tier: admin`) because this template is already
  frontmatter-driven and marking one page should not require a control board.
  Two rules: everything except `hidden` falls open when Clerk is unavailable
  (documentation must not brick over a missing credential), and
  `effective_tier = more_restrictive(local, hub)` so a satellite may restrict
  further but never loosen.
- **`lib/hub_client.py`** — the client for the hub's `/api/agent-key/current`
  and `/api/agent-key/verify`. Authenticates the caller with the network's
  existing `CROSS_APP_WEBHOOK_SECRET` HMAC scheme, the one
  `lib/satellite_reporter` already uses: it authenticates *who is asking* and
  derives nothing, which is what keeps "satellites hold no key material" true
  while still keeping the verify endpoint from being an open key-guessing
  oracle. Verdicts cached on a SHA-256 fingerprint of the key rather than the
  key, because that cache is process memory a debugger or error reporter can
  dump. `allow` cached 900s, `deny` 60s — a brief hub outage must not gate
  readers who were fine a minute ago, while a revoked key should stop working
  promptly.
- **`lib/access.py`** — the policy, and its ordering is the design:
  tier → **local Clerk session** → hub, only for `?key=`. A signed-in visitor
  resolves entirely on this host, so the hub being down gates nothing for them;
  only the agent path, which arrives with no cookie, needs the hub at all.
  Reversing it would couple every satellite's availability to one host for no
  benefit. Kept out of `run.py` so satellites inherit one file.
- **`docs/authentication/`** — three layers, so a reader stops at the one they
  need: the default (nothing to do), a standalone site with its own Clerk, and
  joining or running a network. Names the two traps: the Clerk token's `iat` is
  the token's age, not the sign-in's, so wiring it renders a clock that resets
  every minute; and identity must never travel in the bulletin, which is
  TTL-cached and shared across every satellite.
- **`handoff/`** — kickoff prompts for the two repos this unblocks: an addendum
  pairing with the `pip-docs+` hub brief, carrying the request shapes and cache
  TTLs the client already sends, and a per-subdomain port guide.
- **`tests/test_access.py`** — 17 tests against a fake hub. The two that
  justify the design: signed-in browser with the hub unreachable still resolves
  to `allow`, and a valid key with the hub down degrades to `gated` rather than
  500 or prose. One asserts the *ordering* rather than the outcome — a
  signed-in reader must trigger zero hub calls, since "allowed" could otherwise
  come from a hub that happened to agree.

**Inert until a tier says otherwise.** With the wiring in place, no Clerk keys,
and every page public, all 43 surfaces are byte-identical to the build before
any of it existed — measured, with a control run to strip out the per-request
ids Dash puts in page HTML.

### Changed — dash-improve-my-llms 2.2.0 → 2.3.0

Vendored, as before; 2.3.0 is additive and opt-in. Verified as a no-op on the
surfaces that matter: every Markdown document, the root index, `sitemap.xml`,
`robots.txt` and the crawler HTML are byte-identical. The HTML viewer variants
grow by 192 bytes each — three CSS rules for the identity block that ship
whether or not identity is configured. Behaviourally a no-op; not literally
byte-identical everywhere, which is worth stating precisely since this baseline
is what a later regression gets attributed to.

### Added — CI/CD and tests

- **`.github/workflows/ci.yml`** — flake8 (blocking), then the full test suite
  across a matrix of Python version × backend × Dash version: Flask, FastAPI
  and Quart on Python 3.12, Python 3.11 and 3.13 on Flask, and the bottom of
  the `~=4.4.1` range pinned explicitly on Flask and FastAPI so a 4.4.0-only
  regression cannot hide behind pip resolving to 4.4.1. Asserts the resolved
  Dash and `dash-improve-my-llms` versions before running anything, boots the
  app under gunicorn (a page can render under a test client and still fail
  under a real WSGI worker), and builds and probes the Docker image.
- **`.github/workflows/cd.yml`** — runs CI, POSTs the `RENDER_DEPLOY_HOOK_URL`
  secret, waits for the new instance to be *sustainably* healthy (Render swaps
  instances rather than restarting in place, so a single 200 from `/healthz`
  proves nothing), then verifies the live site. Skips the deploy step when the
  secret is absent instead of failing, so a fork isn't red on day one.
- **`tests/`** — a pytest suite that boots `run.py` itself rather than a test
  app. `conftest.py` normalises the three backends' test clients behind one
  synchronous `.get()`, including driving Quart's async client from a
  fixture-owned event loop. Covers page registration and reachability, stub
  bodies, rendered prose, canonical tags, sitemap/robots/llms.txt, content
  negotiation in both directions, the navigation block, the banner and its
  panels, the network directory and wordmark, docs frontmatter and directive
  targets, heading anchors, and the `BASE_URL` guard.
- **`scripts/smoke_live.py`** — post-deploy checks against a live satellite,
  standard library only. Covers the failures that are silent in production: a
  canonical on the wrong host, a page serving the JavaScript stub, viewer
  chrome leaking into an agent's Markdown, a missing `Vary: Accept`, a missing
  network directory, and dead peer `llms.txt` links. Run in CD and by hand
  (`python scripts/smoke_live.py https://emojimart.2plot.dev`), and itself
  tested against the in-process app so a typo can't turn every live check into
  a silent pass.
- **`scripts/dev.sh`** — starts the development server with *this* project's
  interpreter, resolved from the script's own location rather than from an IDE
  setting or `PATH`.
- **`scripts/audit_links.py`** — walks every page's `llms.txt`, extracts every
  link, resolves internal paths in-process and checks the rest over the
  network. A dead link in an `llms.txt` is worse than one on a page: the agent
  holding that document has no navigation to fall back on and no way to tell a
  typo from a host that is down.

  Classified rather than lumped together, because the classes want different
  responses: `internal` is a real defect, `self-host` is correct once deployed,
  `network` is a peer awaiting the rollout, `unpushed` is a file that exists
  locally and 404s only until the branch is pushed, and `external` is someone
  else's problem to route around. Code spans and fenced blocks are skipped —
  a URL inside backticks renders as `<code>`, not `<a>` — and a transport
  failure is retried once, because an audit that cries wolf gets ignored.
- **`LICENSE`** — the MIT text the README badge, `pages/home.md` and the
  Schema.org block have all claimed since 0.1.0 without the file ever existing.
- **`render.yaml`** — Render Blueprint for `boilerplate.2plot.dev`: gunicorn,
  `/healthz` health check, custom domain, and a persistent disk for the
  analytics ledger (on an ephemeral filesystem a mid-day deploy wipes it and
  the next hourly report overwrites the day's real total).
- **`.flake8`**, **`pytest.ini`**.

### Added — Network analytics reporting to 2plot.ai

- **`lib/satellite_reporter.py`** — hourly signed rollup POSTed to
  `https://2plot.ai/api/satellite/traffic`, so a deployed docs site shows up on
  the hub's owner-only `/traffic` dashboard. HMAC-SHA256 over
  `"{timestamp}." + body` with `CROSS_APP_WEBHOOK_SECRET`, matching the
  network's existing webhook scheme. Off by default: no secret, no reporting.
  Re-posts yesterday during the first hours of a new day so the final hits of a
  day aren't left out, and uses a lease file so only one web worker reports per
  interval instead of every worker racing. `python -m lib.satellite_reporter
  --dry-run` prints the payload without sending it.
- **`lib/traffic_rollup.py`** — derives the reported numbers (`human_hits`,
  `bot_hits`, `visitors`, `sessions`, `median_session_s`, top pages, countries)
  using the hub's own definitions, so this app's figures are comparable with
  every other app on the chart. Infrastructure paths (`/healthz`, `/llms.txt`,
  `/robots.txt`, `/sitemap.xml`, assets, Dash internals) are excluded from the
  report but stay in the local ledger.
- **`lib/health.py`** — `/healthz` on Flask and Quart, matching the endpoint
  the FastAPI build already declared. The hub's hourly sweep probes it for
  up/down + latency, which previously only worked on one of the three backends.
- Quart now tracks visitors too; previously only Flask and FastAPI did.

### Changed — dependencies

- **`dash-improve-my-llms` 2.0.0 → 2.2.0**, installed from `vendor/` until it
  is published to PyPI. App 1 of 4 in a staged rollout, first because every
  satellite documentation site is forked from this repo — a convention set here
  propagates, and so does a mistake.

  Page metadata now *merges* instead of assigning, so no later bookkeeping call
  can erase a page's prose; the prerender reaches every visitor rather than
  only recognised crawlers; and the Markdown renderer emits real anchors,
  tables, code fences and rules. Measured on this app: link counts in crawler
  bodies went from 3 per page to 3–11, code fences from 0 to 5–29 per page, and
  horizontal rules stopped rendering as literal `---` text. No page serves the
  crawler stub, before or after — this repo was never affected by the
  prose-erasure bug, having no bridge loop over `dash.page_registry`.

- **Dash pinned to `~=4.4.1`** (was `>=4.4.0`). Verified matrix, from real apps
  on each backend with the failure reproduced on stock Dash:

  | Dash | Flask | FastAPI | Quart |
  |---|---|---|---|
  | 4.1.0 | ok | n/a — no pluggable backends | n/a |
  | 4.2.0 | ok | ok | ok |
  | 4.3.0 | ok | **broken — every non-root page 500s** | ok |
  | 4.4.0 | ok | ok | ok |
  | 4.4.1 | ok | ok | ok |

  4.3.0 added an early-return path guard to the ASGI middleware that returns
  before `set_current_request`, while the page catch-all still calls
  `get_current_request()` — so it raises `RuntimeError: No active request in
  context`. The catch-all is byte-identical between 4.2.0 and 4.3.0; only the
  middleware changed. 4.4.0 set the context inside the catch-all as well, so a
  future middleware guard cannot reintroduce it: 4.4.x is structurally safer,
  not merely currently-passing.

  `~=4.4.1` lets patch releases flow without twenty pull requests while
  blocking 4.5.0, so a minor bump goes through the matrix deliberately. Pinned
  for the most constrained backend network-wide, **including Flask-only apps** —
  `DASH_BACKEND` is an env var and this is a shared template, so a Flask
  deployment becomes a FastAPI deployment with one env change and no code
  change.

- **Dependency floors are enforced at startup, not advised.** A version below
  the floor stops the boot, names what would degrade, and prints
  `sys.executable` alongside the expected interpreter. `ALLOW_STALE_DEPS=1`
  opts out for anyone deliberately testing an older release. The Dash floor is
  fatal only on FastAPI, where 4.3.0 is an outage rather than a degradation.
  See *Fixed — environment and tooling* for why this is a hard failure.

- **`network_directory.apply()` gates the `wordmark` argument** on the
  installed signature. During a staged rollout this module reaches satellites
  before the new package does, and Python raises `TypeError` on an unknown
  keyword — so passing it unconditionally would turn an older satellite's boot
  into a crash rather than a missing graphic. Same technique `run.py` uses for
  Dash's `enable_mcp`.

### Changed — hosts, branding and repo hygiene

- **`BASE_URL` moved to `lib/constants.py`** and reads `APP_BASE_URL` from the
  environment, defaulting to `https://boilerplate.2plot.dev`.
  `require_owned_base_url()` refuses to boot in production when `APP_BASE_URL`
  is unset or points at a platform hostname (`*.onrender.com` and friends).
  This is the template's highest-consequence footgun: a fork that leaves the
  default in place emits the boilerplate's canonical URL on every one of its
  pages, which asks Google to deindex it, and nothing about the app looks
  broken while it happens.
- **YouTube links now point at [@2plotai](https://www.youtube.com/@2plotai)**;
  `plotly.pro` is replaced by `2plot.ai` throughout, and the deployment host by
  `boilerplate.2plot.dev`. A test fails the build if a live link to
  `plotly.pro` reappears.
- **`.claude/` is untracked and gitignored.** Local session workspace; noise in
  a template other people fork.
- **Dockerfile** copies `vendor/` before the pip layer (the build fails
  otherwise while the package installs from an sdist), declares a `HEALTHCHECK`
  against `/healthz`, and no longer leaves apt lists in the image.

### Fixed — SEO and template

- **Every page shipped two `<link rel="canonical">` tags.** `templates/index.html`
  hard-coded one pointing at the site root while the package injected the
  correct per-page one. A conflicting pair is treated as no signal at all, so
  the per-page canonicals were doing nothing. The template no longer sets one.
- **Two advertised LLM endpoints were 404s.** `<meta name="llms-page-json">`
  and `llms-architecture` pointed at `/page.json` and `/architecture.txt`,
  both removed in dash-improve-my-llms 2.0. The `<noscript>` block linked to
  them too.
- **The Open Graph image never existed.** Every share rendered a blank card
  against `assets/og-image.png`, a file not in the repo. Now points at a real
  asset with its actual declared dimensions.
- **`apple-touch-icon.png` and `site.webmanifest` 404'd on every page load** —
  both `<link>`ed but neither shipped. Commented out with instructions.
- **`piratesbagain.com`** in the navbar (missing `r`) — a dead outbound link
  on every page.
- Placeholder metadata left in the template: `"Your Organization Name"`,
  `"Your Name or Organization"`, `yourdomain.com`, and a `price` of
  `"29_000_000"` in the SoftwareApplication schema (not a valid number, and
  the project is MIT-licensed).

### Fixed — every page shipped the same hard-coded title

`templates/index.html` hard-coded a `<title>` and contained no `{%title%}`
placeholder anywhere, so the per-page titles `pages/markdown.py` registers were
discarded and every page's title depended entirely on `dash-improve-my-llms`
rewriting that one element. `LLMSConfig(prerender=False)` — the documented
one-argument rollback — silently reverted every page on every satellite to one
identical string.

Now `<title>{%title%}</title>`, with `app.title` set from a new
`constants.APP_TITLE`. Without that second half the placeholder resolves to
Dash's default, the bare string `"Dash"`, which is worse than what it replaced.

**The trap, for anyone editing that block.** The package finds the element with
`re.compile(r"<title>.*?</title>", DOTALL | IGNORECASE)` and rewrites the first
match:

- Delete the element and no closing tag remains to anchor on — nothing is
  rewritten and no page has a title at all.
- Spell the tag name in angle brackets inside a nearby *comment* and the match
  starts there instead, running to the next closing tag and replacing every
  line in between. The comment, and any markup after it, vanishes from the
  served page. With rewriting on it still looks correct, so the damage is only
  visible in the served bytes.

The comment above the element used to contain a literal `<title>` for exactly
this reason, and the first attempt at this fix reintroduced it *while
explaining it*. The block now describes the tags in words, and three tests pin
it: the placeholder is present, the title regex matches nothing but the element
itself, and no comment spells the tag in angle brackets. A fourth asserts every
page serves a distinct title.

### Fixed — dead links in the llms.txt documents

Found by `scripts/audit_links.py` across all 10 documents and 102 links.

- **The MIT `LICENSE` file did not exist.** `pages/home.md` and the README
  both linked to it, and the Schema.org block declared the licence — so the
  one link a reader follows to check the terms was the one that 404'd. Added.
- **The development-server port was wrong.** `pages/home.md` said
  `http://localhost:8553`; `run.py` binds **8559**. The Docker instruction
  (8550) was right for the container but rendered as a live link that 404s for
  anyone not running the image — both are now code spans, so they read as
  instructions rather than as something to click.
- **The `SKILLS.md` link pointed at the wrong path** —
  `dash-improve-my-llms/blob/main/SKILLS.md`, but the file lives under
  `docs/`. Fixed to `blob/main/docs/SKILLS.md`.

### Fixed — Markdown rendering

- **A heading containing inline code crashed the site at startup.**
  markdown2dash's renderer does `create_heading_id(text[0])`, and when the
  first inline token is formatted, `text[0]` is a component rather than a
  string — `AttributeError` at import, taking every page down. Fixed in
  `lib/directives/headings.py`.
- **TOC anchors pointed at ids that didn't exist.** Even when it didn't crash,
  the renderer slugged only the *first* inline token (`## Wiring **it** up` →
  `id="wiring"`) while the `toc` directive slugged the raw markdown
  (`wiring-**it**-up`). Both now use one `slugify`, so the link and its target
  agree. Plain headings slug exactly as before, so no existing anchor moved.

### Fixed — MCP wiring

- **The MCP server was never enabled.** `run.py` did
  `from dash import mcp_enabled`, but the symbol lives in `dash.mcp` — the
  import always raised, and the app printed "MCP not available in dash 4.4.1
  (needs >=4.3)" while running 4.4.1. `mcp_enabled` is also the decorator for
  marking a *function* as an MCP tool, not a server switch. The server is
  started from Dash's constructor, so `enable_mcp=` / `mcp_path=` is now passed
  there, and it works on all three backends rather than only FastAPI. Passed as
  `**kwargs` so naming a 4.3+ keyword can't break the boot on an older Dash.

### Fixed — environment and tooling

- **The app booted silently against another project's virtualenv.** An IDE run
  configuration pointing elsewhere started this app against whatever versions
  that environment held — on `dash-improve-my-llms` 2.0.0 there is no
  `llms_viewer.py` at all, so `/<page>/llms.txt` served plain Markdown to every
  visitor and nothing in the log said why. It cost a debugging session across
  two repositories, chasing a stale process and a browser cache that were both
  innocent, and survived a server restart and an incognito window because
  neither was the variable.

  Made worse by this repo's own `enable_mcp` fix, which removed the
  `TypeError` that had been failing loudly on the wrong interpreter — trading a
  crash for a plausible wrong answer.

  Warnings were tried first and were not enough: they scroll past above a wall
  of page-loading output while the app keeps serving. The floors are now fatal
  (see *Changed — dependencies*), and `scripts/dev.sh` removes the choice of
  interpreter entirely. A test asserts the same floor, so `pytest` in the wrong
  environment reports the cause instead of thirty downstream symptoms.
- **CI installed a tarball path that no longer existed.** `ci.yml` hardcoded
  the vendored filename for the FastAPI and Quart legs, so a version bump broke
  exactly two of the matrix entries. It now globs `vendor/`.
- **Header lookups in the test client were case-sensitive.** Werkzeug returns
  `Content-Type`, httpx returns `content-type`, so the content-negotiation
  assertions passed on Flask and failed on FastAPI and Quart — reading like a
  backend bug when the served headers were identical and correct.
- **A peer serving its SPA shell counted as a live document.** The peer check
  asserted only `status == 200`, but a Dash app answers its catch-all with the
  app shell for *any* unmatched path — `2plot.dev/api/this-endpoint-cannot-exist`
  returns `200 text/html`, as does `/api/network/bulletin`, which does not
  exist. A status-only check therefore passes against every host in the
  network whether or not it publishes anything. `smoke_live.py` now rejects an
  HTML body for a document URL, and the same reasoning applies to the
  network-wide check in `ROLLOUT.md`.
- **`smoke_live.py` extracted malformed peer URLs.** Its pattern stopped only
  at whitespace and `)`, and the 2.2.0 navigation block writes links as
  `[https://host/llms.txt](https://host/llms.txt)` — so it produced
  `https://2plot.dev](https://2plot.dev/llms.txt`, which would 404 in CD and
  fail a perfectly good deploy. Invisible locally, because the test shim
  answers 200 for off-host URLs.
- **Viewer-chrome detection keyed on a bare class name.** `docs/networks`
  legitimately *documents* `dv-banner`, so a substring check failed on the
  page's own prose. Both the suite and `smoke_live.py` now match rendered
  markup (`<div class="dv-banner"`), which a Markdown document can never
  contain — otherwise the check quietly teaches people to stop documenting the
  viewer.

### Fixed — Analytics accuracy

- **AI-search crawlers were not being counted.** The visitor hook was
  registered after `add_llms_routes`, and the package's bot middleware
  short-circuits ClaudeBot / ChatGPT-User / PerplexityBot with its own
  response — so those requests never reached the tracker. The hook is now
  registered first on Flask/Quart (and last on FastAPI, where Starlette runs
  the most recently added middleware outermost).
- **Every visitor looked like one visitor behind a proxy.** The tracker used
  `remote_addr`, which on Render/Cloudflare is the proxy. It now reads
  `CF-Connecting-IP`, `True-Client-IP`, `X-Real-IP` and `X-Forwarded-For`
  first, and takes the country from Cloudflare's `CF-IPCountry` header when
  present — free, instant and accurate.
- **Concurrent workers overwrote each other's hits.** The ledger was read,
  modified and rewritten with no lock; under four workers most hits were lost.
  Writes now take an `flock` and land via an atomic replace.
- **Geolocation no longer blocks page views.** The ip-api.com lookup ran inline
  with a 2s timeout on the first hit from each new IP. It now runs in a bounded
  background thread and is backfilled into the buffered hit before it is
  written, so the country is still recorded. Disable with
  `ANALYTICS_GEO_LOOKUP=0`.
- **The ledger is bounded and no longer rewritten on every request.** Hits are
  buffered (10 hits / 30s) and pruned to `ANALYTICS_RETENTION_DAYS` (45) and
  `ANALYTICS_MAX_VISITS` (20000); the hub holds the durable history.
- The ledger path is now absolute (`TRAFFIC_ANALYTICS_FILE`, else repo root) —
  a relative default wrote a different file depending on the working directory.
- Tablets are no longer counted as mobile (iPads and most Android tablets send
  a mobile token too, and the mobile test ran first).

## [1.0.0] - 2026-06-14

First stable release. The boilerplate moves to **Dash 4.x** with pluggable
backends and **dash-improve-my-llms 2.0**, and retires the experimental TOON
format entirely. This is a significant architectural release — see the
migration notes at the end of this section.

> **Versioning note:** the `0.5.0`–`0.8.0` entries below were the December 2025
> TOON line. That work has been removed (see "Removed" below) and the project
> resumes a single, monotonic version line at `1.0.0`. A short-lived second
> `0.5.0` (the May 2026 dash-improve-my-llms 2.0 preview) has been folded into
> this entry.

### Added — Pluggable backends (Flask / FastAPI / Quart)

- **`lib/backend.py`** — single source of truth for backend selection. Reads
  the `DASH_BACKEND` environment variable (`flask` | `fastapi` | `quart`),
  falls back to `flask`, and exposes `BackendInfo` (label, color, icon,
  async flag) so UI components stay in sync with the running backend.
- **`run.py`** constructs `Dash(backend=resolve_backend(), ...)` and attaches
  `app._backend_info` for layout components.
- **`components/backend_badge.py`** — a navbar/header badge that shows which
  backend the site is currently running on.
- **`lib/asgi_middleware.py`** and **`lib/asgi_routes.py`** — ASGI middleware
  and showcase routes (`/healthz`, `/api/backend`, `/api/pages`) that light up
  on the FastAPI/Quart backends.
- New documentation sections:
  - **Pluggable Backends** (`docs/backends/`) — run the site on any of the
    three backends with one env var.
  - **Backend Deep Dive** (`docs/backend-comparison/`) — architecture,
    strengths/weaknesses, deployment, and best practices for each backend.
  - **FastAPI Showcase** (`docs/fastapi-showcase/`) — OpenAPI docs, a native
    JSON API, ASGI middleware, async demo, endpoint explorer, and a stress
    test, showing what the ASGI backends unlock.

### Added — AI/LLM integration via dash-improve-my-llms 2.0

- **`LLMS_DOC` pattern.** Pages expose a module-level prose string (or call
  `register_page_metadata(path, llms_doc=...)`); the package serves it verbatim
  at `/<page>/llms.txt` under whichever backend is active.
  - `pages/markdown.py` registers the expanded markdown body (with
    `.. source::` directives inlined) for every markdown-driven page.
  - `pages/home.py` exports `LLMS_DOC = content` for the root prose.
- **Multi-backend AI/LLM surfaces.** `add_llms_routes(app)` auto-detects the
  backend and serves `/llms.txt`, `/<page>/llms.txt`, `/sitemap.xml`, and
  `/robots.txt` under Flask, FastAPI, and Quart alike — no `if IS_FLASK:` gate.
- **MCP resource bridge.** Each page's prose registers as a `dash.mcp` resource
  on Dash 4.3+ (a silent no-op on older Dash).

### Changed

- **Upgraded Dash 3.2.0 → 4.2.0** and **Dash Mantine Components 2.4.0 → 2.7.0**
  (Mantine 8.3.6). React 18.2.0.
- **`docs/ai-integration/ai-integration.md`** fully rewritten for the 2.0
  surface (LLMS_DOC, multi-backend, MCP bridge).
- **`requirements.txt`** now pins `dash>=4.1.0`, `dash-mantine-components>=2.7.0`,
  and `dash-improve-my-llms[flask]>=2.0.0`, with commented `[fastapi]`,
  `[quart]`, and `[all]` extras plus `uvicorn` for ASGI deployment.
- **`docs/example/example.md`** "Highlighting Important Elements" section
  rewritten around the `LLMS_DOC` pattern.
- **`components/header.py`**, **`components/appshell.py`**, and
  **`components/navbar.py`** updated for the new backend badge and navigation
  (TOON Format and Handoff entries removed).
- **`lib/directives/llms_copy.py`** / **`assets/llms_copy.js`** updated for the
  2.0 `/<page>/llms.txt` routing.
- `APP_VERSION` and `package.json` bumped to `1.0.0`.

### Removed

- **The entire TOON format system** — `lib/toon_generator.py` (~1100 lines),
  the `docs/toon-format/` page, the TOON Analytics Dashboard
  (`docs/data-visualization/toon_dashboard.py`), and all `/llms.toon`
  routes. `dash-improve-my-llms` 2.0 removed TOON from its public API
  (`TOONConfig`, `toon_encode`, `generate_*_toon` no longer exist).
- **`/page.json` and `/<page>/page.json`** routes — dropped in
  dash-improve-my-llms 2.0; Dash 4.3 MCP exposes layouts as resources natively.
- **`/architecture.txt`** — likewise superseded by MCP.
- **`mark_important()`** and **`mark_component_hidden()`** — now deprecated
  no-ops in 2.0. Write the emphasis directly into a page's `LLMS_DOC` markdown.
- **`LLMS_INTEGRATION.md`** and the `docs/handoff/` doc (the FastAPI port plan
  that became 2.0) — superseded by the in-app AI Integration page.

### Migration notes (from any 0.x)

1. **Backend:** the site defaults to Flask, so no change is required. To run on
   FastAPI or Quart, install the matching extra (`pip install "dash[fastapi]"`)
   and set `DASH_BACKEND=fastapi`.
2. **AI/LLM prose:** give each page module an `LLMS_DOC = """..."""` string at
   module scope (or `register_page_metadata(path, llms_doc=...)` when the prose
   is computed). The startup `UserWarning` from 2.0 names every page still
   missing prose.
3. **dash-improve-my-llms extra:** pick `[flask]`, `[fastapi]`, `[quart]`, or
   `[all]` in `requirements.txt`.
4. **Removed APIs:** replace any `mark_important()` / `mark_component_hidden()`
   calls (now no-ops) with `LLMS_DOC` content, and remove references to TOON,
   `/page.json`, and `/architecture.txt`.

---

## [0.8.0] - 2025-12-14

### Added
- **TOON v3.3 Format Enhancements** - Major comprehension improvements from ~75-80% to ~95%+
  - **New Dataclasses**:
    - `CodeTip` - Short instructional code snippets with context
    - `BestPractice` - Numbered best practices with multi-line code examples
    - `Pattern` - Architectural patterns with implementation code
    - `Resource` - External resource links with full URLs
  - **New Extraction Functions**:
    - `extract_code_tips()` - Finds short code snippets (2-15 lines) with headings
    - `extract_best_practices()` - Extracts numbered practices from "Best Practices" sections
    - `extract_patterns()` - Captures pattern implementations from "Common Patterns" sections
    - `extract_resources()` - Extracts markdown links with full URLs preserved
  - **New TOON Sections**:
    - `tips[N]{context,lang,code}:` - Compact code tips with one-line previews
    - `bestPractices[N]:` - Full multi-line code snippets for each practice
    - `patterns[N]:` - Pattern descriptions with implementation code blocks
    - `resources[N]{name,url}:` - External links without URL truncation

### Changed
- **Updated TOON format version from toon/3.2 to toon/3.3**
- **Enhanced summary line** to include tips, best practices, patterns, and resources counts
- **Improved content deduplication** - Tips exclude Best Practices and Patterns sections to avoid duplicate code

### Fixed
- **Code block detection in section boundaries** - Headings inside code blocks (like `## My Visualization` in markdown examples) were incorrectly detected as section boundaries
  - Added code block range detection using `code_block_ranges` list
  - Added `is_in_code_block()` helper to filter out false headings
  - Applied fix to `extract_code_tips()`, `extract_best_practices()`, and `extract_patterns()`
- **`re.escape()` issue** - `re.escape("Best Practices")` was escaping spaces incorrectly
  - Changed to custom escaping that only escapes regex special chars but preserves spaces

### Technical Details
- Updated `lib/toon_generator.py` (~1100 lines after updates)
- Test results for Data Visualization page:
  - 6 tips (properly deduplicated)
  - 5 best practices (all with full multi-line code)
  - 3 patterns (all with implementation code)
  - 4 resources (with full URLs)
  - TOON size: 11,444 chars

---

## [0.7.0] - 2025-12-13

### Added
- **Custom Documentation-Aware TOON Generator** (`lib/toon_generator.py`)
  - Custom TOON route that processes raw markdown from `NAME_CONTENT_MAP`
  - Achieves **54.7% token reduction** vs llms.txt while preserving all content
  - Full directive awareness (exec, source, kwargs, toc, llms_copy)
  - Features:
    - Section extraction with hierarchical structure (h2-h6)
    - Directive parsing with option extraction
    - Source file embedding with smart code compression
    - Table and list preservation in compact format
    - Exec component detection with callback markers
    - Deduplication of code examples and directives
  - Smart code compression (`compress_code()`) that:
    - Preserves imports, function/class definitions
    - Keeps callback decorators and Input/Output patterns
    - Truncates long files with line count indicator
  - TOON v3.2 format with optimized output:
    - Compact section format: `[level] title`
    - Grouped directives by type
    - Inline table format with pipe separators
    - Key lists extraction for substantial bullet points

### Changed
- **Custom `/<page>/llms.toon` route** in `run.py`
  - Overrides default dash-improve-my-llms TOON for markdown pages
  - Uses raw markdown from NAME_CONTENT_MAP instead of rendered components
  - Processes source directives to embed actual file content

### Fixed
- **TOON content gap issue** - Previous TOON was only capturing 15-20% of documentation content
  - Root cause: dash-improve-my-llms extracts from rendered Dash components, losing directive context
  - Solution: Custom route processes raw markdown with full directive awareness
  - Previous TOON was 185% the size of llms.txt (27,669 chars vs 14,943 chars)
  - New TOON is 45.3% the size of llms.txt (6,965 chars vs 15,369 chars)

### Technical Details
- New module: `lib/toon_generator.py` (698 lines)
  - `generate_documentation_toon()` - Main entry point
  - `build_documentation_toon()` - TOON string builder
  - `extract_sections()` - Hierarchical section parser
  - `extract_directives()` - Directive extractor with options
  - `process_source_directive()` - File content reader
  - `process_exec_directive()` - Component metadata extractor
  - `compress_code()` - Smart code compression
  - `compress_section_content()` - Content summarization
  - `extract_tables()` / `extract_lists()` - Structure extractors

---

## [0.6.0] - 2025-12-13

### Added
- **Enhanced TOON Format v3.1** - Lossless semantic compression with 40-50% token reduction
  - Application context with related pages and multi-page awareness
  - Page purpose explanations with human-readable descriptions
  - Component breakdown with type distribution
  - Human-readable callback descriptions
  - Synthesized page summaries
  - Link categorization (internal vs external)

### Changed
- **Upgraded dash-improve-my-llms from v1.0.0 to v1.1.0**
  - Lossless semantic compression preserves all meaningful content
  - New content extraction: `extract_markdown_content()`, `parse_markdown_content()`
  - Smart compression: `compress_code_example()`, `compress_section_content()`
  - New helper functions: `_generate_page_summary()`, `_format_callback_description()`

### New TOONConfig Options
- `preserve_code_examples=True` - Include code snippets from markdown
- `preserve_headings=True` - Keep section structure
- `preserve_markdown=True` - Extract dcc.Markdown content
- `max_code_lines=30` - Max lines per code example
- `max_sections=20` - Max sections to include
- `max_content_items=100` - Increased from 20

### Documentation
- **Updated AI/LLM Integration Guide** with v1.1.0 TOON enhancements
  - Added design principle: lossless semantic compression
  - Updated token efficiency comparison table
  - Added 6 content gap examples (context, purpose, components, callbacks, summary, navigation)
  - Updated TOONConfig with new v1.1.0 options

### Improved
- Better content preservation in TOON format
- Optimal information density vs token reduction balance
- Enhanced developer experience with richer TOON output

---

## [0.5.0] - 2025-12-13

### Added
- **TOON Format Support** - Token-Oriented Object Notation for 50-60% fewer tokens
  - New `/llms.toon` endpoint for token-optimized LLM documentation
  - New `/architecture.toon` endpoint for token-optimized architecture
  - New `/<page>/llms.toon` per-page TOON format endpoints
  - TOON provides tabular arrays and explicit length markers for LLM validation
  - Ideal for API calls, large apps, and cost-conscious deployments

### Changed
- **Upgraded dash-improve-my-llms from v0.3.0 to v1.0.0**
  - Production-ready release with comprehensive test coverage (88 tests, 98% coverage)
  - New API exports: `TOONConfig`, `toon_encode`, `generate_llms_toon`, `generate_architecture_toon`
  - Zero-change migration: existing code works without modifications

### Documentation
- **Updated AI/LLM Integration Guide** with comprehensive TOON format documentation
  - Added TOON format section with benefits comparison table
  - Added example comparison (markdown vs TOON token usage)
  - Added TOONConfig configuration examples
  - Added programmatic TOON generation examples
  - Updated available routes table with new TOON endpoints
  - Updated key functions reference with new TOON imports

### Improved
- Better AI/LLM documentation organization
- Enhanced developer experience with new format options
- Cost optimization through token-efficient TOON format

---

## [0.4.0] - 2025-11-10

### Added
- **LLM Copy Button Directive** (`.. llms_copy::`)
  - New custom directive that adds a "Copy for llm 📋" button to documentation pages
  - Copies the page's `/llms.txt` URL to clipboard for easy AI assistant sharing
  - Users can paste the URL into ChatGPT, Claude, or other AI assistants for context-aware help
  - Features:
    - Automatic URL construction based on current page path
    - Visual feedback with "✓ Copied! ✓" confirmation
    - Fallback clipboard method for non-HTTPS contexts (HTTP development servers)
    - Works across all modern browsers
    - Tooltip: "Copy llms.txt URL for AI assistants"
  - Implementation:
    - Python directive: `lib/directives/llms_copy.py`
    - JavaScript handler: `assets/llms_copy.js`
    - Uses both modern Clipboard API and legacy `execCommand` fallback
    - Mutation observer for Dash-rendered content detection
  - Documentation updated in Custom Directives guide
  - Added to all 5 example documentation pages

## [0.3.0] - 2025-11-09

### Added - Documentation System
- **Comprehensive Getting Started Guide** (385+ lines)
  - Detailed directive options documentation (`:code: false`, `:defaultExpanded`, `:withExpandedButton`)
  - Interactive examples with best practices
  - File structure examples and patterns
- **Custom Directives Guide** (476 lines)
  - Complete documentation for all 4 directives (toc, exec, source, kwargs)
  - 3 live Python examples (button, counter, form validation)
- **Data Visualization Guide** (465+ lines)
  - 5 chart type examples with full implementations
  - Plotly template integration guide
  - Real-time updates and dashboard patterns
- **Interactive Components Guide** (569 lines)
  - 6 callback pattern examples
  - State management, pattern matching, chained callbacks
  - Loading states demonstration
- **AI/LLM Integration Guide** (577 lines)
  - Complete dash-improve-my-llms documentation
  - SEO optimization strategies
  - Bot management and privacy controls

### Added - Theme System
- **DMC Figure Templates Integration**
  - All Plotly charts now use `dmc.add_figure_templates()`
  - Theme-aware callbacks for 6 chart examples
  - Charts dynamically update with light/dark theme toggle
  - Proper background rendering in both themes
- **Code Block Theming**
  - Theme-aware CSS for markdown code blocks
  - Proper syntax highlighting in light and dark modes
  - Inline code and code block styling
- **Comprehensive Theme Configuration**
  - Professional typography hierarchy (h1-h6)
  - Systematic 4px-based spacing scale
  - 5-level shadow system
  - Consistent border radius system
  - Global component defaults via theme.components
  - Softer black (#1a1b1e) for better contrast

### Added - UI/UX Enhancements
- **Navigation Improvements**
  - Custom page ordering (Getting Started → Custom Directives → AI/LLM → Interactive → Visualization)
  - Better visual hierarchy
  - Organized documentation sections
- **Typography System**
  - Inter font family across application
  - Optimized line heights (md: 1.55 for body text)
  - Proper font sizes (16px base)
  - Font smoothing and text rendering optimization
- **Layout Refinements**
  - Better responsive breakpoints (md for navbar)
  - Improved spacing consistency
  - Enhanced mobile experience
  - Better heading spacing (1.5em top, 0.5em bottom)

### Added - Production Features
- **SEO-Ready HTML Template**
  - Comprehensive meta tags with developer guidance
  - Open Graph and Twitter Card configuration
  - Structured data (Schema.org) for Organization and SoftwareApplication
  - Analytics integration (Google Analytics ready to enable)
  - Favicon configuration with multiple formats
  - Performance optimization (preconnect hints)
  - Search engine verification placeholders
  - Enhanced noscript fallback with styled content
  - 297 lines of documentation and configuration

### Improved
- **15 Working Python Examples**
  - Button interactions, counters, form validation
  - 5 chart types (bar, line, scatter, realtime, dashboard)
  - Callback patterns and state management
  - All examples theme-aware and fully functional
- **Directive System**
  - Fixed kwargs directive to parse component specifications (e.g., `dmc.Button`)
  - Better error handling and fallbacks
  - Support for directive options
- **Code Quality**
  - Fixed JSON serialization error (removed lambda from theme styles)
  - Better import statements
  - Comprehensive inline comments
  - Fixed DMC 2.4.0 compatibility issues

### Changed
- **Better Performance**
  - Optimized theme switching
  - Smooth transitions
  - Better font loading
- **Documentation Organization**
  - Clear learning path
  - Progressive complexity
  - Better code examples

### Fixed
- Import errors in example files (missing dmc, State imports)
- DMC 2.4.0 compatibility (removed unsupported `type` prop from TextInput)
- JSON serialization error in theme configuration
- Heading ID generation with code blocks in markdown
- Theme persistence and switching
- Code block rendering in dark mode

## [0.2.0] - 2025-11-09

### Changed
- **BREAKING**: Migrated from Dash 2.5.0+ to Dash 3.2.0
- **BREAKING**: Migrated from dash-mantine-components 0.14.7 to 2.4.0
- **BREAKING**: Updated all Mantine packages from 7.14.1 to 8.3.6
- Updated Flask from 1.0.4+ to 3.1.2
- Updated Plotly from 5.0.0+ to 6.4.0
- Updated `app.run_server()` to `app.run()` (Dash 3.x standard)

### Removed
- **BREAKING**: Removed deprecated package imports:
  - `dash-html-components` (now part of main `dash` package)
  - `dash-core-components` (now part of main `dash` package)
  - `dash_table` (now part of main `dash` package)

### Fixed
- Replaced deprecated `NotificationProvider` with `NotificationContainer`
- Fixed Mantine version mismatch between package.json and DMC version
- Added node_modules to .gitignore

### Added
- Added package-lock.json for reproducible npm builds
- Comprehensive migration documentation (8 detailed guides)
- Project analysis and assessment documentation
- Persistent theme preference storage using localStorage
- Browser color scheme preference detection on first visit
- Smooth theme transitions without page flash
- AI/LLM & SEO Integration (dash-improve-my-llms v0.3.0)
  - Automatic llms.txt, page.json, architecture.txt generation
  - SEO-optimized sitemap.xml with intelligent priority
  - Bot management (blocks AI training, allows AI search)
  - Structured data for better search indexing
  - Privacy controls for sensitive pages

### Improved
- Better dependency management with cleaner requirements.txt
- Improved code organization with inline comments
- Enhanced theme management system
- Better performance with latest Dash and DMC versions

## [0.1.0] - 2024-11-30

### Added
- Initial release of Dash Documentation Boilerplate
- Markdown-driven documentation system
- Support for light and dark themes
- Responsive design for mobile and desktop
- Docker deployment support
- Interactive code examples with syntax highlighting
- Custom markdown directives:
  - `toc` - Table of contents generation
  - `exec` - Executable Python code blocks
  - `source` - Source code display with syntax highlighting
  - `kwargs` - Component props documentation
- AppShell layout with header, navbar, and responsive drawer
- Search functionality for navigation
- Theme toggle with icon indicators
- Integration with dash-mantine-components (DMC)
- Integration with python-frontmatter for metadata
- Custom CSS styling system
- Docker and docker-compose configuration

### Documentation
- README with getting started guide
- Project structure documentation
- Example documentation pages

---

## Version History Summary

| Version | Date | Dash | DMC | Mantine | Python | Features |
|---------|------|------|-----|---------|--------|----------|
| 1.0.0 | 2026-06-14 | 4.2.0 | 2.7.0 | 8.3.6 | 3.11+ | Pluggable backends (Flask/FastAPI/Quart), dash-improve-my-llms 2.0, TOON removed |
| 0.8.0 | 2025-12-14 | 3.2.0 | 2.4.0 | 8.3.6 | 3.11+ | TOON v3.3, tips/best practices/patterns/resources extraction |
| 0.7.0 | 2025-12-13 | 3.2.0 | 2.4.0 | 8.3.6 | 3.11+ | Custom TOON generator, documentation-aware TOON v3.2 |
| 0.6.0 | 2025-12-13 | 3.2.0 | 2.4.0 | 8.3.6 | 3.11+ | Enhanced TOON v3.1, dash-improve-my-llms v1.1.0 |
| 0.5.0 | 2025-12-13 | 3.2.0 | 2.4.0 | 8.3.6 | 3.11+ | TOON format, dash-improve-my-llms v1.0.0 |
| 0.4.0 | 2025-11-10 | 3.2.0 | 2.4.0 | 8.3.6 | 3.11+ | LLM Copy Button directive |
| 0.3.0 | 2025-11-09 | 3.2.0 | 2.4.0 | 8.3.6 | 3.11+ | Comprehensive docs, theme system, SEO |
| 0.2.0 | 2025-11-09 | 3.2.0 | 2.4.0 | 8.3.6 | 3.11+ | Migration to Dash 3.x, DMC 2.4.0, AI/LLM |
| 0.1.0 | 2024-11-30 | 2.5.0+ | 0.14.7 | 7.14.1 | 3.11+ | Initial release |

---

## Migration Guides

### Migrating to 1.0.0 from any 0.x

This is the major release that moves the boilerplate to Dash 4.x. See the
**Migration notes** under [1.0.0](#100---2026-06-14) for the full checklist.
In short:

1. **Backend:** defaults to Flask — no change required. For FastAPI/Quart,
   `pip install "dash[fastapi]"` (or `[quart]`) and set `DASH_BACKEND=fastapi`.
2. **AI/LLM prose:** add an `LLMS_DOC` string to each page module (or call
   `register_page_metadata(path, llms_doc=...)`); the 2.0 startup warning lists
   pages still missing prose.
3. **dash-improve-my-llms extra:** pick `[flask]` / `[fastapi]` / `[quart]` /
   `[all]` in `requirements.txt`.
4. **Removed APIs:** drop any TOON usage (`TOONConfig`, `toon_encode`,
   `generate_*_toon`), `/page.json`, `/architecture.txt`, and the now-no-op
   `mark_important()` / `mark_component_hidden()` calls — move emphasis into
   `LLMS_DOC` instead.

### Migrating to 0.6.0 from 0.5.0

**Zero changes required!** The upgrade is fully backwards compatible.

Key changes:
1. Update `dash-improve-my-llms` in requirements.txt to `>=1.1.0`
2. TOON output now includes richer, lossless semantic content automatically

Optional new TOONConfig options:
```python
from dash_improve_my_llms import TOONConfig

app._toon_config = TOONConfig(
    # New in v1.1.0:
    preserve_code_examples=True,   # Include code snippets
    preserve_headings=True,        # Keep section structure
    preserve_markdown=True,        # Extract dcc.Markdown content
    max_code_lines=30,             # Max lines per code example
    max_sections=20,               # Max sections to include
    max_content_items=100,         # Increased from 20
)
```

### Migrating to 0.5.0 from 0.4.0

**Zero changes required!** The upgrade is fully backwards compatible.

Key changes:
1. Update `dash-improve-my-llms` in requirements.txt to `>=1.0.0`
2. New TOON endpoints are automatically available:
   - `/llms.toon` - Token-optimized LLM docs
   - `/architecture.toon` - Token-optimized architecture
   - `/<page>/llms.toon` - Per-page TOON format

Optional new features:
```python
# Configure TOON output (optional)
from dash_improve_my_llms import TOONConfig

app._toon_config = TOONConfig(
    indent=2,
    delimiter=",",
    include_metadata=True
)

# Programmatic TOON encoding (optional)
from dash_improve_my_llms import toon_encode
toon_string = toon_encode({"key": "value"})
```

### Migrating to 0.3.0 from 0.2.0

Minor updates, mostly additive. Key changes:
1. Documentation content significantly expanded
2. Chart examples now use DMC figure templates
3. Enhanced SEO features in index.html
4. Better theme integration across all components

### Migrating to 0.2.0 from 0.1.0

Major breaking changes. See migration documentation:

- **Quick Start**: `MIGRATION_README.md`
- **Detailed Guide**: `claude.md`
- **Step-by-Step**: `MIGRATION_CHECKLIST.md`
- **Code Changes**: `CODE_CHANGES_SUMMARY.md`

Key changes to be aware of:
1. Update all imports from `dash_html_components` to `from dash import html`
2. Update all imports from `dash_core_components` to `from dash import dcc`
3. Replace `dmc.NotificationProvider()` with `dmc.NotificationContainer()`
4. Update custom components to use DMC 2.4.0 API
5. Check CSS for any Mantine 8 specific changes

---

## Support

- **Issues**: [GitHub Issues](https://github.com/pip-install-python/Dash-Documentation-Boilerplate/issues)
- **Discussions**: [GitHub Discussions](https://github.com/pip-install-python/Dash-Documentation-Boilerplate/discussions)
- **Dash Community**: [Plotly Community Forum](https://community.plotly.com/)

---

[unreleased]: https://github.com/pip-install-python/Dash-Documentation-Boilerplate/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/pip-install-python/Dash-Documentation-Boilerplate/compare/v0.8.0...v1.0.0
[0.8.0]: https://github.com/pip-install-python/Dash-Documentation-Boilerplate/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/pip-install-python/Dash-Documentation-Boilerplate/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/pip-install-python/Dash-Documentation-Boilerplate/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/pip-install-python/Dash-Documentation-Boilerplate/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/pip-install-python/Dash-Documentation-Boilerplate/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/pip-install-python/Dash-Documentation-Boilerplate/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/pip-install-python/Dash-Documentation-Boilerplate/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/pip-install-python/Dash-Documentation-Boilerplate/releases/tag/v0.1.0
