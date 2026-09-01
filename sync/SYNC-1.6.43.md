# SYNC 1.6.43 (template @ 1.6.43)

Three items. The rest of 1.6.43 — the `.. exec::` machine-lane builder,
the `:code: false` guard, the phantom-release parser, the per-call-site
UA pin, the subset-plus-reality-check battery pin, the tier-doc corpus
sweep, the registry-derived nesting control — is NOT here, because it is
already ported and wire-verified on eleven forks during the item-18
round. Those detects passing on arrival is not a vacuous spec; **the
passing detect IS the proof the round landed**, and a fork that reads
`already-present` against its own tree has measured something it should
measure. The corrections themselves live in SYNC-1.6.22-1.6.42's item 18,
which grew 448 lines this round.

What IS here is what no fork has consumed: one lib defect with a live
data consequence on every board in the fleet, two spec-text corrections
from pipdocs' item-12 port, and a kit refresh.

ORDER MATTERS: **item 1 first**, then the rest. It is the only item with
a consequence that is accruing while you read this.

```yaml sync-verbatim
# EMPTY, and that is a statement rather than an omission (sync/README).
# All three items are contract-class. The one file a fan-out might have
# wanted to byte-copy — .claude/CLAUDE.md — is contract by the authoring
# rule that has stood since the F1 pilots: its contract and traps
# sections port verbatim, everything above them adapts. A workflow
# cannot make that distinction, so item 3 stays session-class.
```

---

### 1. The read table drops internal traffic too (1.6.43, note 83a)
class: contract — the same class `lib/analytics_tracker.py` already
  carries as item 12 of SYNC-1.6.22-1.6.42. NOT a reclass: every reason
  item 12 gave for contract-over-verbatim still holds.
files: `lib/analytics_tracker.py` (`record_read`), plus the fork's own
  internal-traffic test.
contract: `record_read` — the `on_document_read` hook the 2.8.0 floor
  added — MUST drop a request carrying `lib.constants.INTERNAL_UA_TOKEN`
  **before it reads any field**, exactly as `track_visit` has since the
  internal-traffic contract existed. The gate is item 12(c)'s clause and
  it is the whole item: **"counted nowhere" includes the READ TABLE.**
  A fork whose internal-traffic contract says traffic carrying the token
  is counted nowhere, and whose `reads` table counts it, does not hold
  that contract — it holds half of it.
  Key on the event's `ua` field. `EVENT_FIELDS` has `ua`, not
  `user_agent`; a drop keyed on the wrong name is silently a no-op, which
  is this item's own failure mode.
detect: in `record_read`, does the token check precede the row build?
  `grep -n "INTERNAL_UA_TOKEN" lib/analytics_tracker.py` returning only
  the `track_visit` occurrence means the hook never learned it. If your
  tracker's read path has another name, look for whatever the package's
  `on_document_read` is registered to in `run.py`.
acceptance: pipdocs' measurement shape, and **print the count beside the
  result** — a bare "no rows" is the negative this round learned not to
  trust. One probe carrying the internal token → zero `reads` rows; one
  probe carrying a real crawler UA → exactly one row, so the pin cannot
  pass by dropping everything. Both directions in the same test.
  ALSO PRINT THE RESOLVED `dash-improve-my-llms` VERSION in that output
  (note 89), so your report says what was actually tested rather than
  what the floor permits — and say it even when it differs from what
  your production image resolves, because that gap is the interesting
  part. Template's acceptance run: **suite at dimll 2.8.0**, 467 passed,
  3 skipped, exit codes captured; **production resolves 2.9.4**.
  `ua` is in `EVENT_FIELDS` at BOTH versions, read from the 2.9.4 wheel
  rather than inferred — which is the check that matters here, since the
  drop keys on `ua` and a field renamed between versions would make this
  fix a silent no-op on production while passing in CI. Do that
  comparison for YOUR resolved pair before reporting green.
notes: found by pipdocs on a private host (69 rows where 67 were real)
  and REPRODUCED on the template before it was accepted — a habit worth
  copying, since the relay was a summary of a summary by the time it
  reached here. The live consequence is why this item is first: the
  network's own probes — the hub's health sweep, every satellite's link
  audit, every post-deploy battery — have been landing in `reads` and are
  currently the busiest "vendor" on every board in the fleet. Historical
  rows keep them; the ops seat is handling the hub-side read window.
  The floor stays `>=2.8.0` for this release. The bump is note 84's and
  arrives with its own knobs.

---

### 2. Two corrections from pipdocs' item-12 port (1.6.43, note 83b/83d)
class: contract — spec text and a fence note, not code. Nothing to copy;
  something to stop believing.
files: your own reading of SYNC-1.6.22-1.6.42 items 12 and 18, and your
  `tests/` if you took the classifier test as cargo.
contract:
  (a) THE LANE HAZARD IS A CLASS, NOT A FILENAME. It was written as
    "item 12's proxy-scheme hazard applies to every such test, not only
    test_proxy_scheme.py", which still reads as `not-applicable` on a
    fork that has no such file — and the hazard has nothing to do with
    proxies. State it as: **any test that requests a browser surface
    without naming a UA.** On pipdocs it bit `test_social_card.py` and
    `test_page_structure.py`, neither of which sounds like a lane test.
  (b) THE `user_agent=` KWARG IS NOT PORTABLE. `client.get(path,
    user_agent=…)` works on the template only because conftest's
    `Client` wrapper folds it into `headers` before werkzeug sees it. A
    fork whose `client` is a raw werkzeug test client gets an
    `EnvironBuilder` rejection on current pins from the identical line.
    Copy the WRAPPER, or fold the kwarg into headers yourself, before
    copying any call site that uses it.
  (c) `tests/test_analytics_classifier.py` HAS THREE FORK-OWNED SEAMS,
    not zero. Its fence note said the file imports only names every fork
    has had — true of the imports, false of the interface: the row-key
    SET, `flush()`, and the geo switch are all things a fork shapes.
    The README's two questions ("who stubs this?", "what does it call
    into?") were asked and answered too shallowly. Asking them is not
    the same as answering them about every seam the file TOUCHES.
detect: `grep -rn "test_client()" tests/ scripts/` and, for each hit,
  ask whether that request names a UA — not whether the FILE mentions
  one. If you took `tests/test_analytics_classifier.py` as cargo, diff
  its row-key set, `flush()` call and geo handling against your tracker.
acceptance: no test in your tree requests a browser surface without
  naming a UA (the per-call-site pin from item 18 already enforces this
  if you ported it — say which of the two you are relying on); and your
  classifier test, if present, passes against YOUR tracker's seams
  rather than the template's.
notes: (c) is the mirror question (1.6.30) applied one level deeper, and
  it is the second time this round a cargo judgement was right about
  imports and wrong about the interface — `scripts/smoke_live.py` was the
  first, in 1.6.29. When you next put a file in the block, answer the two
  questions about every seam it touches, not every name it imports.

---

### 3. Kit refresh — three traps (1.6.43)
class: contract. `.claude/CLAUDE.md`'s contract and traps sections port
  VERBATIM; everything above them adapts to your fork's own guide. That
  rule is why this is not cargo and why no fan-out can do it for you.
files: `.claude/CLAUDE.md`, traps section.
contract: three traps, all earned in the item-18 round:
  (a) WHICH BRANCH RENDER BUILDS CAN BE MEASURED ON A GREEN PUSH, BY
    TIMING (leaflet). `main == release == wire` at every step of a
    promote tells you nothing. Sample `/healthz` every ~45 s from the
    push and time the swap against the **promote**, not the push.
    leaflet measured build+swap at 2m03s from its promote; had Render
    reacted to the push, that same interval would have put the build live
    ~1m52s before it appeared. STRONG EVIDENCE, NOT PROOF — the
    canonical discriminator is still the first push that goes RED on
    main, with `release` unmoved and the wire unchanged. Four hosts
    correctly declined to call their `deploy:` fence row proven on a
    green push; that refusal is the standard.
  (b) VERIFY THE ARTIFACT THE CLAIM IS ABOUT, AND SAY WHICH ONE. It runs
    both ways. A props table absent from the crawler document is a defect
    of the SITE, not of the harness — pannellum moved that assertion to
    the lane that passed and the pin held for a fortnight over a corpus
    serving zero props. WHEN A LANE DISAGREES, THAT IS THE FINDING. And
    the inverse, which is worse because it sends someone hunting a bug
    that does not exist: `curl https://…/ | grep -c skip-link` returns
    **0** on a host where the skip link ships and works (excalidraw),
    because it is a Dash component in `app.layout`.
  (c) ASSERT THE CORPUS IS NON-EMPTY BEFORE TRUSTING ANY NEGATIVE, and
    print the count beside the result (note 88). A sweep that found
    nothing and a sweep that swept nothing produce the same green.
    MEASURED ON THE TEMPLATE, 2026-09-01: this repo's `.flake8` excludes
    `docs/*/`, so `flake8 docs/` exits **0** with a file in `docs/`
    containing `def broken(:` — the linter is not passing the file, it is
    not reading it. `py_compile` sees it immediately. Same family as the
    two above and as this seat's own `pytest … | tail -2 && git commit`,
    where the pipe's exit status was `tail`'s and a red suite committed
    anyway.
detect: `grep -c "measured on a GREEN push" .claude/CLAUDE.md` = 0, or
  `grep -c "ASSERT THE CORPUS IS NON-EMPTY" .claude/CLAUDE.md` = 0.
acceptance: the three traps present in your traps section, adapted only
  where your host's shape differs; `tests/test_claude_kit.py` green.
notes: if your fork's `.claude/CLAUDE.md` is its own guide with kit
  content merged in (the batch-1 precedent — excalidraw, email), this is
  a MERGE into your traps section, never an install-over.

---

## Reporting

Per-item disposition (applied / ported-as-contract / already-present /
not-applicable-because / open, each with evidence), the resolved
`dash-improve-my-llms` version printed beside your acceptance output,
your suite before→after, CD run id + conclusion FROM THE RUN, refs, and
`/healthz build` read twice. Corrections to THIS SPEC where it mismatched
your tree — eleven forks corrected the last one and it was better for it.
