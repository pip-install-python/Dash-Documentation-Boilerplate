# Dash Documentation Boilerplate

## Project Overview

This project is a modern documentation boilerplate for Dash applications,
providing a markdown-driven documentation system with interactive examples,
comprehensive theming, and AI/LLM integration. It is the template that the
`*.2plot.dev` component documentation sites are forked from.

Versions, dependencies and history are deliberately not restated here — they go
stale. Read `requirements.txt` for the stack and `CHANGELOG.md` for what
changed and when.

---

## Custom Directives

| Directive | Syntax | Purpose |
|-----------|--------|---------|
| `toc` | `.. toc::` | Generate table of contents |
| `exec` | `.. exec::module.path` | Render Python component |
| `source` | `.. source::file/path.py` | Display source code |
| `kwargs` | `.. kwargs::ComponentName` | Show component props |

Options are documented in `docs/directives/directives.md`.

---

## Configuration

### Customization Points

| File | Purpose |
|------|---------|
| `lib/constants.py` | App-wide constants (colors, titles) |
| `assets/main.css` | Custom CSS styles |
| `templates/index.html` | HTML template (analytics, meta tags, SEO) |
| `components/appshell.py` | Theme configuration, MantineProvider settings |
| `components/navbar.py` | Navigation ordering and organization (incl. the full-height mobile drawer — the network-standard mobile nav) |
| `pages/control_board.py` | `/admin/control-board` — live per-page tier + llms.txt toggles (owner/admin-gated, fails closed) |
| `lib/page_visibility.py` | The board's override store (persists to `PAGE_VISIBILITY_FILE`; overrides beat frontmatter in `lib/access.py`) |
| `lib/auth_demos.py` | Live-demo teasers rendered inside the sign-in gate cards |

---

## Development Notes

### Adding New Documentation Pages
1. Create folder in `docs/` (e.g., `docs/my-component/`)
2. Create markdown file with frontmatter:
```markdown
---
name: My Component
description: Description of my component
endpoint: /components/my-component
icon: mdi:code-tags
---

.. toc::

## Overview
...
```
3. Add Python examples as needed
4. Reference with `.. exec::docs.my-component.example`
5. Page will auto-register and appear in navigation

### Creating Theme-Aware Charts
1. Import `dmc.add_figure_templates()`
2. Register templates at module level
3. Create callback with `Input("color-scheme-storage", "data")`
4. Use ternary to select template: `"mantine_dark" if theme == "dark" else "mantine_light"`
5. Recreate figure with template parameter

---

## Resources

- [Dash Documentation](https://dash.plotly.com/)
- [Dash Mantine Components](https://www.dash-mantine-components.com/)
- [Mantine](https://mantine.dev/)
- [dash-improve-my-llms](https://pypi.org/project/dash-improve-my-llms/)
- [Project Repository](https://github.com/pip-install-python/Dash-Documentation-Boilerplate)
- [dmc-docs Inspiration](https://github.com/snehilvj/dmc-docs)
- [Plotly Community Forum](https://community.plotly.com/)

---

## Network role & the behavioral contract

This repo is a member of the 2plot network — either the template
itself (dash-documentation-boilerplate) or a fork of it serving one
component's documentation. **Identity derives from the repo, never
from this file**: the app key comes from `SATELLITE_APP_KEY` and
run.py's fork point, the host from `lib/constants.py`'s `BASE_URL`,
the deliberate differences from the template from `DIVERGENCES.md`
at the repo root. If those disagree with anything written here,
they win.

### The contract — every session, every prompt

1. **Check the prompt against this tree before executing.** Prompts
   are written from the template's perspective and your fork may
   legitimately differ — floors, backends, payload shapes, page
   sets. A prompt step that doesn't fit this repo is a finding to
   return, not an instruction to force.
2. **Corrections are your job, not scope creep.** If a prompt's
   reference list doesn't match its steps, if its assumed state is
   wrong, or if executing it as written would produce a
   green-but-vacuous result, say so and propose the corrected
   version before running it.
3. **Verify your own deploy on the wire before reporting.** A push
   is not a result. Run `/wire-verify` (or its manual equivalent)
   against production and paste what came back. If your sandbox
   cannot reach your own domain, say exactly that — an unverified
   claim marked as unverified is honest; the same claim unmarked is
   not.
4. **Report observed versus expected, with evidence.** Paste the
   JSON, the status code, the test count. "Should work" and summary
   claims without artifacts are not reports.
5. **Divergence is legitimate when written down.** Before syncing
   template changes, read `DIVERGENCES.md`; never let a sync
   "restore" a recorded deliberate difference. When you deliberately
   diverge, record it there in the same commit — an unrecorded
   divergence is indistinguishable from drift and will be treated
   as drift.
6. **Never touch**: environment variable VALUES, hosting dashboards,
   secrets, other repos' trees, or anything the prompt didn't put in
   scope. Enumerate what you cannot do (closing PRs, dashboard
   steps) for the owner instead of claiming it done.

### Verification traps (fleet-learned, keep them)

- A `>=` floor can never pull a new release through a Docker cache
  hit — the requirements line changing IS the cache bust, and floors
  live in several encodings (requirements, run.py's boot floor,
  tests, CI): grep the number, move every one.
- `/healthz` build == HEAD **of `release`** is the deploy proof on a
  release-branch host — see the fuller trap below, and read that one
  before acting on this line. Written unqualified here until
  2026-09-01, when clerkhook found the two lines contradicting each
  other 116 lines apart: a reader who met this one first was sent to
  the wrong ref, and `main` ahead of `release` reads as drift instead
  of what it is (an uncertified push pending). A missing geo block on
  dimll ≥2.7 means the cache trap fired (unless DIVERGENCES.md says
  this host's healthz is deliberately minimal).
  The general form, since this file is long enough to contain its own
  contradictions: when a trap is later corrected, AMEND THE ORIGINAL —
  a correction that only appends leaves the wrong answer in the place a
  reader looks first.
- Always GET, never HEAD — and the mechanism, measured 2026-08-27
  after two rounds of wrong diagnoses: on the ASGI backends HEAD is
  answered by NOTHING AT ALL. Werkzeug derives a HEAD rule from
  every GET rule; FastAPI's `APIRoute` does not, so a route declared
  `@router.get(...)` returns 405, and every ASGI host in the network
  was 405ing HEAD on every route — `/healthz`, `/robots.txt`,
  `/sitemap.xml` included. Get the LAYER right (corrected 1.6.33,
  after this text and two seats' drops all said "Starlette", and
  three probes went looking in the wrong package):
  `starlette.routing.Route` DOES add HEAD wherever GET is present —
  `self.methods.add("HEAD")`, the same courtesy Werkzeug does — and
  FastAPI's `APIRoute` is the one that takes `methods` literally.
  A HEAD probe therefore tells you about
  the router's method table and never about the document. GET is
  never wrong, which is the whole reason to have one rule.
  Do NOT "verify" the trap on one host and conclude HEAD is fine:
  excalidraw measured twice and was right about its own Flask host
  and wrong about the fleet. Do not verify it on `HEAD /` either —
  a crawler-UA `HEAD /` is answered by the prerender middleware
  before routing, so it returns 200 on a host that 405s everything
  else, and that one case is how this repo's 1.6.31 in-process
  probe cleared the app code. Earlier text here said the ASGI hosts
  DROP the `Link` headers on HEAD: a 405 carries no `Link`, so the
  observation was true and the diagnosis was not. Fixed in the
  template at 1.6.32 (a HEAD→GET ASGI middleware, because the
  package's own adapter declares its routes GET-only); the fleet's
  two ASGI forks consume it as spec item 11, and the hub plus four
  second-ring hosts had the same defect — if you serve a non-Flask
  backend, assume you have it until you have probed a route that is
  NOT `/`. The middleware stayed after dimll 2.7.2 fixed the
  package's own routes, because `/` is Dash's page catch-all and every
  Dash route is an `APIRoute` too — and it is RETIRED at 1.6.44, on the
  pin to dimll 2.9.4, where the package walks the router itself and adds
  HEAD wherever GET is allowed, Dash's lifespan-registered catch-all
  included. Amended here rather than appended below, because the version
  is the whole content of the claim and a reader who met "the middleware
  stays" first would keep a shim that now MASKS the fix it was standing
  in for: converting HEAD to GET above the router made every HEAD look
  correct whatever the router did, so it would have hidden a regression
  in the package's pass exactly as well as it hid the original defect.
  Measured before removing (5 paths x 3 UAs, FastAPI lane, in-process):
  15 of 15 HEAD/GET status pairs matched WITHOUT it, `/` to a browser UA
  included — the one case the old text said would 405. The disable was
  proved non-vacuous first by asserting the middleware stack contained
  the class in one run and not the other. If your floor is below 2.9.4,
  the shim is still load-bearing: this retirement is gated on the pin,
  not on the date.
- Any throwaway Python probe a session writes against a production
  host needs the certifi SSL context AND a retry guard. Fixing the
  shipped tools does not cover the next ad-hoc script: the template
  seat hit `CERTIFICATE_VERIFY_FAILED` in a hand-written CD watcher
  one hour after shipping that exact fix inside both live tools,
  and the ops seat hit it plus an `IncompleteRead` on a chunked
  response in the same session. It is a seat habit, not a repo
  contract, which is what this file is for.
- Run-watchers keyed on a commit sha can match Dependabot's runs on
  the same sha — key on the workflow path (cd.yml) instead.
- The browser lane and the machine lane are different documents;
  a fix proven on one is unproven on the other.
- SUPERSESSION: cd.yml's build-match wait cannot tell "not deployed
  yet" from "already replaced" — both look like a live build that
  is not the sha it wants. A bot-merged PR (any GITHUB_TOKEN merge)
  is one road in: it lands with ZERO workflow runs on the merge sha
  (anti-recursion) yet still reaches production, because the deploy
  hook builds branch HEAD — so an in-flight CD run ships the merge
  while its own wait holds out for the superseded release sha
  (observed live on 4a1d430, 2026-08-25). It is NOT the only road,
  and taking the bot actor off main does not close the class: two
  human pushes inside one deploy window, or hook dispatch lag,
  produce exactly the same state. Since 1.6.25 the wait fails FAST
  when the live build is a DESCENDANT of the wanted sha (compare
  API) instead of going red at timeout — that is the diagnosis, and
  it works whoever merged. The policy — actions PRs: human merge
  when green, never a bot actor on main — removes the most common
  road, not the trap.
- Anonymous api.github.com is 60 requests/hour. With no `gh` and no
  token, read a run ONCE after CI's own jobs report complete — a
  blind 20 s poll loop spends the whole budget reading rate-limit
  bodies as "not done yet" (modelviewer, 2026-08-26).
- A GitHub API JSON body WITHOUT the field you asked for
  (`workflow_runs` absent, not empty) is a rate-limit error body,
  never an empty result — check the field exists before trusting
  the answer.
- `git fetch` before any audit: the fan-out pushes to these repos
  now, and a checkout current yesterday is 2–3 merges behind
  origin/main today (three pilot sessions, same day, 2026-08-26).
- A failed STEP is not a failed RUN. A job with
  `continue-on-error: true` (pip-audit here) reports its step red
  and the RUN still concludes `success`; the reverse also bites —
  a green-looking job list under a run whose conclusion is
  `failure`. Read the run's `conclusion`, then the annotations;
  never infer either one from the other.
- Never round-trip JSON through zsh `echo` — it interprets the
  `\n` inside a multi-line commit message and hands the parser
  real control characters (a broken API read on the template, then
  the same hour on the ops seat). Pipe curl straight into
  `python3`, or use `printf '%s'`.
- Repeated HTTP headers survive only if you keep them: both
  `dict(resp.headers)` and `{k: v for k, v in resp.headers.items()}`
  keep the LAST value per name, and dimll emits several `Link`
  headers (muicharts, 2026-08-26). Iterate the items, or ask for
  `resp.headers.get_all(name)`; in curl, `-D -` and read the raw
  block.
- Name the crawler UA when you probe the machine lane. Which
  document a host serves is decided by the package's UA
  classification, not by the absence of a UA: on the template
  today, curl's default `curl/8.x` receives the SAME crawler
  document as Googlebot (18,779 bytes, byte-identical) while a
  Chrome UA gets the 148 KB app shell. One host (muicharts) reported
  a UA-less probe classified the other way; treat that as
  UNCONFIRMED — muischeduler filed the same observation and then
  RETRACTED it (its report had the two documents swapped), leaving
  one unreproduced sighting, and a trap carrying an unreproducible
  fact spends somebody's afternoon. The advice does not depend on
  it: either lane can be the one you did not mean to test, so send
  `-A "<a real crawler UA>"` and confirm from the body which
  document came back.
- There is ONE classifier: `dash_improve_my_llms.classify()`. Never
  add a User-Agent list to this app — the tracker had one for a year
  (`lib/analytics_tracker.py`, until 1.6.34), it filed ClaudeBot as
  *search* (it is Anthropic's training crawler; the package's registry
  and this repo's own `run.py` comment both said so six lines from
  where the list ignored them), it still named the retired
  `anthropic-ai` / `claude-web` tokens, and it counted every UA-less or
  library client as a human. Every host in the fleet reported those
  numbers. A token the registry lacks is a pushback to the package
  seat, not a list here; `tests/test_analytics_classifier.py` greps the
  module for the old tokens and goes red if one comes back.
- `build == HEAD` on `/healthz` means HEAD of **`release`**, not main
  (1.6.35). Render deploys `release`; only cd.yml's `deploy` job writes
  it, fast-forward, after the CI matrix is green. `main` ahead of
  `release` is an uncertified push pending — its CD run is red or still
  running — never "drift" and never a reason to deploy by hand or to
  write `release` yourself (a non-fast-forward push fails the next run
  on purpose). Compare the wire against `git rev-parse origin/release`;
  the one measurement behind this: 2026-08-29 14:12Z, de0bcff pushed
  to main, built by Render inside the minute, red in CD at 14:13Z,
  served for ~6 minutes. A host whose DIVERGENCES.md posture fence has
  no `deploy:` key still watches main — there the trap is the old one.
- Headless browsers are CRAWLER-lane from dash-improve-my-llms 2.9.0
  (measured on the wheel, 2026-08-29: `HeadlessChrome/…` and a
  Playwright UA classify `lane: crawler, bot_type: monitor,
  vendor_key: headless`; 2.8.0 said browser). A host that screenshots
  ITSELF for social cards — Playwright, Puppeteer, a headless Chrome
  in a job — now receives the crawler document, not the app shell,
  unless the screenshot service sends its own non-headless UA. If a
  card went blank or textual after a floor bump, look here before
  the template. Same class as the two lane traps above: name the UA,
  confirm from the body which document answered.
- Which branch Render actually builds can be measured on a GREEN push,
  by TIMING, without waiting for a red one (leaflet, 2026-08-31 — the
  method, not just its answer). `main == release == wire` at every step
  of a promote tells you nothing: both refs hold the same sha, so the
  wire cannot separate them, and four promotes across three hosts said
  nothing at all. Sample `/healthz` every ~45 s from the moment of the
  push and note when the swap lands relative to the PROMOTE, not the
  push. leaflet measured build+swap at 2m03s from the promote; had
  Render reacted to the push instead, the same 2m03s would have put the
  build live ~1m52s earlier than it appeared, and the wire was still
  serving the old sha well past that point. That is STRONG EVIDENCE
  that Render is building `release` — not proof, since a queued or slow
  build could in principle produce the same shape. The canonical
  discriminator is unchanged and still owed: the first push that goes
  RED on main must leave `release` unmoved and the wire unchanged.
  Worth taking on every SECOND promote — it costs one background
  sampler and converts "asserted" into "strongly evidenced".
  SAMPLE THE WIRE AND THE RUN STATE IN THE SAME LOOP — eight samples at
  45 s, one timeline (pannellum's 15917bc promote, seat-verified; four
  hosts now have a pair measured this way). Two separate reconstructions
  invite exactly the arithmetic error the measurement exists to avoid:
  flexlayout's retroactive read off CD step timestamps was coarser and
  it said so. pannellum's live pair: push 21:55:44Z · promote 21:58:20Z ·
  wire still OLD at 21:58:47Z · wire NEW at 21:59:33Z — 73 s after the
  promote, 183 s after the push. The old-then-new bracket around the
  promote is the whole evidence; a single "new" sample proves nothing
  because it cannot say what it followed.
  TIME AGAINST THE PROMOTE STEP'S `completed_at`, NEVER THE DEPLOY
  JOB'S (emojimart 166e33a, seat-verified). The job CONTAINS the
  build-match wait, so it completes after the swap by construction and
  the arithmetic reads "swap before promote" every single time —
  emojimart measured a 9 s impossible ordering before catching it. A
  measurement that cannot produce a sane answer is worse than none,
  because the number looks like data.
  AND THE SAMPLER MUST RETRY: three attempts per sample, and record
  "unreadable" as a state DISTINCT from "old" (emojimart). The container
  restart lands exactly where the bracket needs its sample, so an
  un-retried loop is systematically blind at the only moment that
  matters — and collapsing unreadable into old invents a bracket that
  was never observed. leaflet's run shows the shape: two consecutive
  unreadable samples sit between its last old and first new.
  THE TEMPLATE'S OWN PAIR, run 33576940156 / ac20ed1, 2026-09-02, and it
  reproduces BOTH corrections rather than merely following them:
    00:50:07Z  run created (push)
    00:51:59Z  STEP 'Promote to release' completed_at
    00:52:03Z  wire still old (2b1edd5)
    00:52:53Z  wire UNREADABLE   <- the restart, inside the bracket
    00:53:38Z  wire NEW (ac20ed1)
    00:53:51Z  JOB 'deploy to render' completed_at
  promote STEP -> swap = **99 s** (sane; pannellum 73 s, leaflet ~123 s).
  deploy JOB -> swap = **-13 s** — the impossible ordering, reproduced on
  the first host to try the method, which is why the step/job distinction
  is in this trap and not a footnote. The UNREADABLE sample fell exactly
  between last-old and first-new: folding it into "old" would have
  reported a 45 s bracket nobody observed.
  A SECOND PAIR ON THE SAME HOST, run 33595792466 / 4e17525, 2026-09-02,
  and it CORRECTS the sentence above: 05:42:53Z created · 05:45:08Z
  promote STEP · 05:45:26Z old · 05:46:16Z UNREADABLE · 05:47:01Z NEW ·
  05:47:01Z deploy JOB. promote STEP -> swap = **113 s** (so 99 s was the
  host, not that push's weather — stable to ~14 s across two runs) and
  push -> swap = 248 s. But deploy JOB -> swap = **0 s**, not negative.
  The earlier wording — "reads swap before promote every time" — is MINE
  and it overstates: the job completes when the build-match wait SEES the
  swap, so it tracks the swap and never the promote, landing at or after
  it. Useless for timing either way, which is the point; predicting the
  SIGN was a claim two runs did not support. And the UNREADABLE sample
  landed inside the bracket twice out of two, which makes the retry a
  property of the restart rather than one host's luck.
  The inference at its real strength: had Render reacted to the PUSH at
  00:50:07Z, the same 99 s build+swap would have served the new build by
  ~00:51:46Z, and the wire was still old at 00:52:03Z — so it reacted to
  the PROMOTE. Fifth host with a measured pair; still not proof, and the
  red push on main remains the discriminator.
- Verify the artifact the claim is about, and say which one you
  measured. Three hosts got this wrong in one round while holding the
  rule: a skip link checked in the received HTML lives in the RENDERED
  DOM (muicharts, twice inside an hour, having written the rule
  itself); a props table absent from the crawler document is a defect
  of the site, not of the harness — pannellum moved that assertion onto
  the rendered layout and the pin passed for a fortnight over a corpus
  serving zero props. WHEN A LANE DISAGREES, THAT IS THE FINDING; never
  relocate the assertion to the lane that passes. And an owner-gated
  section needs BOTH cookie states to be a measurement at all
  (modelviewer: `credentials: 'include'` → 2,962 B with admin hrefs,
  `'omit'` → 108 B with none — hidden, not merely styled away).
  The error runs BOTH ways and the second one is worse, because it
  sends someone hunting a bug that does not exist: `curl https://…/ |
  grep -c skip-link` returns **0** on a host where the skip link is
  shipped and working (excalidraw, 2026-08-31) — it is a Dash
  component in `app.layout`, so React renders it and the served HTML
  never contains it. A fork "verifying the skip link on the wire" with
  curl reports a missing feature that is present. Anything built by
  the layout rather than written into the template is invisible to the
  two artifacts curl can reach; assert it through the layout or a real
  browser, and say which you used.
- Assert the corpus is NON-EMPTY before trusting any negative, and print
  the count beside the result (note 88). A sweep that found nothing and a
  sweep that swept nothing produce the same green, and only one of them
  is evidence. Measured here 2026-09-01: this repo's `.flake8` excludes
  `docs/*/`, so `flake8 docs/` exits 0 with a file in `docs/` containing
  `def broken(:` — the linter is not passing that file, it is not reading
  it; `py_compile` sees it at once. Same family, same day: a naive
  substring count read fenced documentation as defects (this seat), a
  file-scoped grep matched prose ABOUT the defect it was hunting
  (muicharts, clerkhook), a `git show … && diff` printed "(empty = same)"
  on a comparison that never ran (llms), and `pytest … | tail -2 && git
  commit` committed over a red suite because a pipeline's exit status is
  the LAST command's (this seat, one hour after writing the note above).
  Capture the exit code; count what you swept; say both.
- And the same family one turn later, MEASURED TWICE — this seat and
  clerkhook hit it independently within the hour, so it is a property of
  the technique and not one seat's slip: extracting a package constant with
  `re.search(r"EVENT_FIELDS = \((.*?)\)", src, re.S)` truncated at a `)`
  inside a COMMENT in the middle of the tuple, printed eight of sixteen
  fields, and reported `'ua' present: False` — confidently, with a
  number beside it. Caught only because eight looked too few. When you
  parse a language construct out of source with a regex, check the count
  against something independent (the file, `python -c "from … import X;
  print(len(X))"`, the CHANGELOG) before you believe a negative.
- A shell's CWD can shadow an installed package, and it produces the most
  convincing wrong answer of the family: measuring `EVENT_FIELDS` across
  two dimll versions, this seat ran the comparison with the cwd inside an
  unpacked 2.9.4 wheel, so `import dash_improve_my_llms` resolved from
  the CURRENT DIRECTORY rather than site-packages — and two readings of
  ONE wheel were reported as two versions agreeing, in a CHANGELOG and a
  shipped spec (2026-09-01, corrected the same day). The load-bearing
  half was true and the supporting detail was invented. When comparing
  versions, `print(mod.__file__)` and assert it is the path you meant, or
  set PYTHONPATH explicitly and import in a fresh process per version;
  and print the unpacked file count before the read (note 88 applied to
  the check itself, leaflet). Note also that parsing the constant out of
  source is not the safe alternative: the regex form truncated on a `)`
  inside a comment (measured twice — this seat and clerkhook), and an AST
  form written to replace it agreed with the wrong answer until the
  import settled it. IMPORT THE THING.
- NAME THE CHECK THAT ACTUALLY RAN, not the one you meant to run (1.6.44
  item 7). `.flake8` excludes `docs/*/`, so for a year "flake8 is clean"
  was reported as covering the exec'd examples a documentation site
  RENDERS, and it never read one of them: a file in `docs/` containing
  `def broken(:` leaves `flake8 docs/` at exit 0 with zero output —
  measured again here 2026-09-04, alongside `py_compile` exiting 1 with
  the SyntaxError on the same file. The general form of the reporting
  rule: a report says which invocation produced the number, over how
  many files, and with what exit code, because "lint passed" is a claim
  about a command and everyone reads it as a claim about the code. CI
  runs the sweep as its own step (`py_compile sweep of docs/`) and fails
  when the corpus is EMPTY, since a sweep of nothing is the same green
  as a sweep of something clean.
- PRINT THE RESOLVED VERSION BESIDE THE RESULT, and say which tool
  produced it (1.6.44 item 10, note 89). An acceptance is a claim about
  a tree at a version: "suite green" is not a result, "471 passed, 3
  skipped, exit 0, dimll 2.9.4 imported from .venv/…/site-packages" is.
  Resolve it by IMPORTING and printing `mod.__file__` — never by
  reading requirements.txt, which states the intent, and never by
  parsing source, which truncates (see the regex and cwd-shadowing
  traps above). The gap this closes is real and was measured on
  excalidraw 2026-09-01: `llms_version` 2.9.4 on the wire while its
  suite ran 2.8.0, so its CI and its production disagreed about which
  package's behaviour was being accepted, and every green tick meant
  the older one.
  The same rule names the tools whose LOCAL invocation is not CI's:
  `actionlint` without shellcheck on PATH skips every `run:` block's
  shell analysis, so "actionlint clean" locally is a weaker statement
  than the CI job's; a local absence of the binary is weaker still,
  and both must be reported as what they are. The general form: when
  the check you ran differs from the check CI runs, the report says
  so in the same sentence as the result.
- A CD LANE THAT CALLS ci.yml MUST NOT ALSO LET ci.yml RUN ITSELF on a
  push to main (1.6.44 item 12, clerkhook 44c0c27). Both runs resolve to
  the concurrency group `ci-${{ github.ref }}` with
  `cancel-in-progress: true`, so one is killed at random; when the
  standalone run wins, CD's `test` job is CANCELLED, `deploy` skips,
  `release` never moves — and `main` ahead of `release` then reads as an
  ordinary pending push instead of as the accident it is. Detect:
  `ci.yml` declares `push: branches: [main]` AND `cd.yml` has
  `uses: ./.github/workflows/ci.yml`. Acceptance: a `workflow_call`
  creates NO run of its own, so the next push to main adds ZERO rows to
  the CI workflow list and the matrix appears exactly once, as `ci / *`
  jobs INSIDE the CD run. The template has the correct shape
  (pull_request + workflow_dispatch + workflow_call) and the pin is in
  `tests/test_cd_promotes_release.py` so it cannot drift back.
  Sub-trap, met while writing that pin: PyYAML parses an unquoted `on:`
  key as the BOOLEAN `True`, so `workflow["on"]` raises KeyError on
  every workflow file in this repo. A test that reads triggers must try
  both keys — one that catches the KeyError and moves on asserts
  nothing at all.
