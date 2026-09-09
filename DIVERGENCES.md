# Divergences from the template

Every DELIBERATE difference between this repo and
dash-documentation-boilerplate, with its reason. This file is the
boundary between design and drift:

- Template syncs read this file FIRST and must not "restore" anything
  recorded here.
- A difference not recorded here is treated as drift and will be
  synced away.
- Record the divergence in the SAME commit that creates it — one
  line: what differs, why, and what the template would otherwise do.
- An empty list is a statement too: it means this repo intends to
  match the template exactly.
- Two kinds of entry live here, and the second is the one forks keep
  losing (1.6.44 item 9). A DIVERGENCE says "this repo differs, on
  purpose". A RECORDED CONVENTION says "this repo MATCHES, and the
  match is a decision" — most often something deliberately REMOVED or
  deliberately not added. Nothing in a diff distinguishes the second
  from an accident, so a sync restores it and nobody notices; the
  entry is what makes the absence legible. Both are read by the
  fan-out machinery and by sync authors, which is why they belong in
  this file rather than in a test docstring — neither reads those.

Fleet precedents for what belongs here: flexlayout's own-source
`_build_llms_doc` dedup and app-key sourcing; flows' own
`_health_body` payload shape (ports the healthz CONTRACT, not the
template's file); clerkhook's minimal `{ok, app, build}` healthz and
its heartbeat-as-before_request (the single anonymous 200 on a locked
host); muischeduler's no-npm dependabot scope.

## This repo's divergences

Forks: replace this section with your own list at fork time; the
fork-point identity ritual in run.py is the model for what a
well-recorded decision looks like.

- **`Bash(git push*)` is NOT in `.claude/settings.json`'s deny list**,
  where 1.6.45 item 13 specifies it for the template. Owner decision,
  2026-09-07, asked and answered before the file was written.

  The item's reasoning is sound — a bad template push fans out to
  twelve forks on the next round, so it makes the template's push a
  human action. The owner's working practice is the other way round:
  the session stages and verifies a stack, the owner reads the report
  and says "push it", and the session pushes. A `deny` rule blocks the
  tool outright rather than prompting, so keeping it would have
  silently broken that loop — the owner would have said "push it" and
  received a refusal.

  What still holds without the deny: this repository is the TEMPLATE,
  so item 12's push clause does NOT apply here and "ops approved —
  push" is not sufficient (see `.claude/CLAUDE.md` clause 7). The
  owner's own word in the owner's own terminal is still required for
  every push of this tree. The deny would have been a second lock on a
  door the contract already locks; its absence changes who can turn
  the key, not whether there is one.

  A fork consuming item 13 should keep the deny unless its owner says
  otherwise — the fork case is the one the item was written for.

## Recorded conventions (not divergences)

Guard entries. Every line here documents something this repo MATCHES
or deliberately does NOT carry — an absence a sync would otherwise
read as drift and helpfully undo. Adding one costs a sentence; the
alternative costs a fortnight of a defect walking back in.

- **`HeadAsGetMiddleware` is GONE and must not come back** (1.6.44
  item 2). It converted HEAD to GET ABOVE the router, so every HEAD
  looked correct whatever the router did — it MASKED the package's
  own fix rather than conflicting with it, and would have masked a
  regression in it just as well. Retirement is gated on the PACKAGE's
  behaviour, not on the date and not on whatever the pin says today:
  from 2.9.4 the package walks the router itself, so the shim is
  unnecessary at 2.9.4 and at every version after it (the pin is
  2.10.0 since 1.6.45 item 1). A fork whose floor is BELOW 2.9.4
  still needs the shim. `lib/asgi_middleware.py` keeps the full
  reasoning where the code used to be.
- **There is no User-Agent list in this app, and there must not be**
  (1.6.34). `dash_improve_my_llms.classify()` is the one classifier.
  The tracker carried a local list for a year; it filed ClaudeBot as
  *search*, still named the retired `anthropic-ai` / `claude-web`
  tokens, and counted every UA-less client as a human — on every host
  in the fleet. `tests/test_analytics_classifier.py` greps the module
  for the old tokens and goes red if one returns. A missing token is a
  pushback to the package seat, never a table here. The same rule now
  covers `vendor_class` (item 8): prefer the package's value, derive
  from the package's REGISTRY when absent, never from a local map.
- **This host claims NO `/.well-known/*` route of its own** (1.6.45 item 5),
  and a fork that does must record it here.

  The mechanism makes the absence worth writing down. `add_llms_routes()`
  collects the paths already in the URL map and SKIPS any well-known route
  it finds there (`_wk_claimed` in the package's adapters), so a host that
  registers `/.well-known/<anything>` BEFORE that call silently takes the
  path over — the package does not serve its version and does not complain.
  That is the right behaviour (a host must be able to own its own
  namespace), and it means the difference between "the package serves this"
  and "we do" is invisible in a diff and invisible on the wire.

  Measured on this tree: zero self-registered well-known routes, so the
  package serves all three of `agent-skills/index.json`, `api-catalog` and
  `mcp/server-card.json`. `tests/test_skill_doc.py` holds that, with a
  positive control — a synthetic claimed route must be detected, so the
  check cannot pass by looking at nothing.

  A fork with its own status page, its own catalog, or a hand-rolled MCP
  card records it here in the same commit that registers it. Otherwise the
  next sync reads the package's absence as drift and "restores" a route the
  fork deliberately owns.

- **The duplicate `operationId`s in `/openapi.json` are NOT worked around
  here** (1.6.45, found while building item 3). On every FastAPI host,
  `/healthz`, `/api/backend` and `/api/pages` emit the SAME operationId for
  their GET and their HEAD — 16 operations, 13 distinct on this tree — so
  the document fails OpenAPI 3.x, which requires operationId to be unique
  document-wide. Wire-confirmed by the ops seat the same day:
  pannellum.2plot.dev serves 15 operations with 12 distinct and the same
  three duplicated; muischeduler.2plot.dev's `/openapi.json` returns 500.

  The cause is the package's and the fix belongs there (dimll 2.11 register
  item D1): dash-improve-my-llms adds HEAD to every route declaring GET —
  which is the correct fix, the one that retired HeadAsGetMiddleware — while
  FastAPI generates one operationId per ROUTE and reuses it for every
  method. There is no clean app-side repair: FastAPI's
  `generate_unique_id_function` receives the route, not the method, so it
  cannot tell the GET from the HEAD it is naming.

  A local workaround would mean either dropping HEAD from the schema (hiding
  a route this network deliberately serves) or renaming operations the
  package will rename again — both of which would make the fork's document
  disagree with the package's intent and would have to be unpicked when D1
  lands. Recorded so a sync does not read the absence of a workaround as an
  oversight, and so the next reader knows the invalid document is known
  rather than unnoticed.

- **Content images carry width/height and NOT `loading`/`decoding`**
  (1.6.44 item 6f). Neither attribute is a prop of dash 4.4.1's
  `html.Img` and Dash RAISES on an unknown one — adding them takes the
  whole site down at import, not at render.
  `tests/test_a11y_block.py` pins the reason and goes red the day Dash
  learns them.
- **Two of item 6's a11y sub-items are recorded rather than fixed**,
  a form the item's own wording allows ("identified and fixed **or
  recorded**"):
- **(d) the mobile console error** seen on leaflet, llms and
  pannellum — NOT REPRODUCED on this host. Measured 2026-09-04 in the
  owner's Chrome against the deployed build c9a5458: page load
  produced 16 console messages, all of them `LOG` (Clerk theme and
  session lines, the text-animation and sun-rotation scripts), and
  ZERO errors or warnings. Nothing to fix here; a fork that DOES see
  it should not read this line as clearance for its own tree.
- **(e) shipped CSS/JS are not minified**, deliberately. The wire
  serves them `content-encoding: gzip` (measured the same day on
  `/assets/main.css` and `/assets/llms_copy.js`), the whole of
  `assets/` is ~29 KB of text before compression, and this repo is a
  TEMPLATE — the stylesheet a fork opens on day one should be the one
  a human wrote. A build step would trade that for a saving the
  transfer encoding has already taken. Revisit if `assets/` grows past
  a few hundred KB.

## Byte-owned paths

Paths this fork owns byte-for-byte. The F3b fan-out never overwrites
a path listed here; everything else in the spec's `sync-verbatim`
block is the template's to update mechanically. Prose above explains
divergences; this block is the machine answer.

Repo-relative paths, one per line, `#` comments, no `..`; exactly one
block. An EMPTY block means "the template owns every sync-verbatim
path here" — present so the absence is a statement. When the block
exists it is authoritative; a fork without it gets the conservative
mention heuristic (over-flags, never restores).

```yaml byte-owned
```

## Posture

What this host ANSWERS, as measured — never as intended. The hub's F4
battery seeded these per-host postures from its own table, which is a
copy of a measurement somebody took once; this block homes them in the
repo that can keep them true, and the hub reads it instead.

Three keys, all optional. An EMPTY block means "the template defaults" —
present, so the absence is a statement. `tests/test_claude_kit.py`
validates the shape (and holds `runtime:` against render.yaml, where the
repo declares one); nothing validates the numbers but a probe, so
re-measure when you change what this host serves:

    ai_bots   the status an AI-crawler UA receives per path, measured
              with a real vendor UA (ClaudeBot, GPTBot — NOT a UA-less
              curl, which is classified separately). A blocked vendor
              gets 403 on the browser document while the agent surfaces
              stay open — that asymmetry is the posture, and it is
              invisible from a browser.
    healthz   `full` (the fleet payload: app, backend, build, geo,
              python, …) or `minimal` (a deliberately reduced body — see
              clerkhook's recorded divergence; the battery's
              python_matches_declared skips with notice there).
    runtime   `docker` or `python` — the Render service runtime, which
              decides whether PYTHON_VERSION is required or forbidden
              (sync spec item 5).
    deploy    `release-branch` — Render deploys `release`, which only
              CD writes after a green matrix (1.6.35, sync item 13);
              `build` on /healthz is HEAD of `release`, and `main`
              ahead of it is an uncertified push pending. ABSENT reads
              as `main`: Render watches main and a push deploys before
              CI has judged it. MEASURED BY RED PUSH 2026-08-31 on this
              host: 417731e went red in CI (run 33342828114), `release`
              held, and the ops seat's 41 wire samples over ten minutes
              all served the prior green build (425baea) on a host whose
              push-to-wire window is 90–135 s — the red build never
              served. The mechanism is proven where it was built.
    unknown_ai `allow` | `meter` | `block` — this host's
              `default_unknown_ai` (RobotsConfig), what an unrecognised
              or ABSENT User-Agent receives on the corpus (1.6.36; dimll
              2.9.0 widened "block" to cover those). Absent reads as
              `allow`, the package default.

Measured on boilerplate.2plot.dev, 2026-08-30T00:09Z, build 700a170 — Round 3.4
(the posture flip, 1.6.37) LANDED, with the ClaudeBot UA
(`Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible;
ClaudeBot/1.0; +claudebot@anthropic.com)`) and the GPTBot UA
(`…compatible; GPTBot/1.2; +https://openai.com/gptbot`), identical for
both: `/` 200 (the 18,779-byte crawler document), `/llms.txt` 200,
`/healthz` 200; robots.txt carries no Disallow for either. History,
kept because it corrects a framing: the reading before this release
(2026-08-29T23:49Z, build ecc66f8) was 403/200/403 on the wire AND
in-process, and the drop had framed that as two walls — the app's
and a Cloudflare edge rule on `/`. The EDGE WALL WAS NEVER OBSERVED on
this host: every 403 was the app's `block_ai_training`, and the flip
alone produced 200/200/200 with no Cloudflare edit (ops seat, 00:08Z;
this session, 2026-08-30T00:09Z). The owner is checking whether any zone rule
exists at all; until a host measures otherwise, the app-level wire
measurement is the whole posture.

```yaml posture
# 2026-08-30T00:09Z, build 700a170, ClaudeBot and GPTBot identical — see above
ai_bots: {"/": 200, "/llms.txt": 200, "/healthz": 200}
healthz: full
runtime: python
deploy: release-branch
unknown_ai: allow
```
