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

Fleet precedents for what belongs here: flexlayout's own-source
`_build_llms_doc` dedup and app-key sourcing; flows' own
`_health_body` payload shape (ports the healthz CONTRACT, not the
template's file); clerkhook's minimal `{ok, app, build}` healthz and
its heartbeat-as-before_request (the single anonymous 200 on a locked
host); muischeduler's no-npm dependabot scope.

## This repo's divergences

*(none — this IS the template. Forks: replace this section with your
list at fork time; the fork-point identity ritual in run.py is the
model for what a well-recorded decision looks like.)*

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

Measured on boilerplate.2plot.dev, 2026-08-27, build 5589318:

```yaml posture
ai_bots: {"/": 403, "/llms.txt": 200, "/healthz": 403}
healthz: full
runtime: python
```
