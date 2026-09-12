# SYNC 1.6.46 (template @ 1.6.46, OPEN — not a release yet)

**This spec is OPEN.** Nothing below has been built. It exists so that no
item rides on one session's memory: the fleet's own note 135 says a rider
appended to a drop file is THE RECORD, NOT THE DELIVERY, and until
2026-09-12 half of these lived only in this seat's memory file, which is
worse — not even a record a fork could read.

Written in the format ops adopted for this release (note 187, and the
evidence is three items in 1.6.45 that each cost a separate round trip to
discover): **every block states whether the TEMPLATE can exercise its own
acceptance.** A block that cannot is marked **FORK-ONLY** and names how a
fork proves it. 9(b)'s tautology on the template, T1's `pip install` for a
package that does not exist here, and item 6's editable install were all
discovered separately, by three different forks, because no spec said
which side could test what.

Provenance is on every block. Where a measurement is already taken, it is
quoted with its date and sha so nobody pays for it twice.

The tip this spec is written against: **`4fddb16`** (1.6.46's hotfix
series — `ef38cc8`, `8a8a79f`, `4fddb16` — on the wire, CD conclusion
`success`). dimll pinned `==2.10.0`.

```yaml sync-verbatim
# EMPTY, and for the third release running. Every item here is contract-
# or cargo-class with a fork-owned seam, and the two files a fan-out
# might want to byte-copy are the two it must not: `.claude/CLAUDE.md`
# ports its contract and traps sections and adapts everything above them,
# and `.claude/session-name`'s CONTENT IS THE FORK'S OWN APP KEY.
```

---

### 1. note 128's IncompleteRead backoff

class: contract (`scripts/network_smoke.py`)
template exercises its acceptance: **YES** — reproducible against this
  host's own production wire.
files: `scripts/network_smoke.py`, `tests/test_network_smoke.py`
detect: `fetch` retries the whole REQUEST and never accumulates partial
  reads; `grep -c IncompleteRead scripts/network_smoke.py` = 0.
acceptance: a fixture that truncates a chunked body mid-read is
  recovered, with a control proving the fixture actually truncates (a
  fixture that stopped truncating would make the test decorative).
notes: **THE ONLY ITEM IN THIS SPEC WITH LIVE BLAST RADIUS.** Whole-
  request retries do not survive a truncated chunked read, and this bites
  in CD's verify job where a red is indistinguishable from a real
  regression. Measured twice on this host against production, 2026-09-12:
  `agents_and_browsers_get_different_types` with `IncompleteRead(6406
  bytes read, 1602 more expected)` after its three retries, and
  `head_get_parity_three_uas` with `IncompleteRead(10952 bytes read, 8287
  more expected)` — and the very next run of the same command passed, so
  it is intermittent and will not reproduce on demand. Build it before it
  reds a deploy nobody can explain.

### 2. `/healthz` reports the ledger without an absolute path

class: contract (`lib/health.py`, the healthz key contract)
template exercises its acceptance: **YES**
files: `lib/health.py`, `lib/asgi_routes.py`, `tests/test_healthz_shape.py`
detect: `ledger.path` present in the served payload (production shows
  `/var/data/visitor_analytics.json`).
acceptance: the ledger block reports PERSISTENCE and COUNTS with no
  filesystem path, and the key-set tests move with it.
notes: a small disclosure, and a host-varying shape — it is what made the
  1.6.45 probe-cap defect depend on CHECKOUT DEPTH, because the body's
  length varied with where the repo sat. Gated on the key contract being
  able to absorb the change: `cd.yml`'s build-match wait reads `build`
  from this document, and `healthz_keys_vs_template` compares its key
  set, so both move in the same commit or neither does.

### 3. The 3.14 / pip-26.1 truststore mechanism in `ci_leg.sh`

class: cargo (`scripts/ci_leg.sh`)
template exercises its acceptance: **YES** — python3.14.4 is installed on
  this seat, so this is verifiable here and simply not yet done.
files: `scripts/ci_leg.sh`, `tests/test_ci_leg_script.py`
detect: the candidate loop drops to the next interpreter whenever 3.14's
  own pip cannot reach the index, rather than making 3.14 work.
acceptance: a 3.14 leg builds its venv BEHIND THE PROXY — venv created
  `--without-pip`, packages installed with an older pip via
  `pip --python <venv>/bin/python install …` — and the leg prints the pip
  that did the installing.
notes: 3.14.4's ensurepip ships pip 26.1, which validates TLS through the
  macOS truststore and IGNORES `--cert`/`PIP_CERT` (`OSStatus -26276`),
  so the vendored dash-clerk-auth sdist's isolated build env cannot reach
  the index. "Do not upgrade pip, the stock pip works" is no longer
  sufficient advice — the stock pip IS the broken one on 3.14.
  Also: **certifi is the wrong bundle for pip** (the proxy's CA lives in
  the system store; certifi carries Mozilla's roots) and the RIGHT one
  for the app's runtime fetches. The script should resolve each for its
  own job rather than setting one and hoping.
  The 1.6.45 candidate loop (leaflet) already degrades correctly — it
  takes a real venv on 3.12 instead of the mask path — so this item makes
  3.14 WORK rather than fixing a break. Observed on this seat both ways
  within one hour: one run built all three legs on 3.14/pip 26.1, the
  next fell back to 3.12/pip 24.0.

### 4. `promote_sampler.py` reads the run state it claims to read

class: cargo (`scripts/promote_sampler.py`) — and it is this seat's own
  defect, filed against itself
template exercises its acceptance: **YES** — on the next promote.
files: `scripts/promote_sampler.py`, `tests/test_promote_sampler.py`,
  `.claude/CLAUDE.md` (the trap line moves with it — OWNER'S WORD)
detect: the docstring claims it samples "the wire and the CD run state on
  ONE timeline" while the loop reads only the wire; and the gap verdict
  requires `--push` AND `--promote`.
acceptance: the sampler reads the promote STEP's `completed_at` itself
  after the bracket closes, and prints the gap verdict without the
  operator supplying a timestamp that cannot be known in advance.
notes: THE FEATURE IS DECORATIVE IN LIVE USE AS SHIPPED. The verdict
  needs both flags, but the promote step's time is unknowable until after
  the run while the trap requires the sampler to be started BEFORE the
  promote — so the pair can never both be supplied. Measured 2026-09-12:
  started with `--push 16:20:08Z`, it printed "push -> promote gap: not
  given". I then computed 168 s BY HAND, which is exactly the second
  reconstruction that trap exists to prevent. Every 1.6.45/1.6.46 promote
  needed a separate `ls-remote` watcher for the same reason.

---

### 5. The row-test runner refuses a fixture nothing fetched

class: cargo (`tests/test_network_smoke.py`)
template exercises its acceptance: **YES**
files: `tests/test_network_smoke.py`
detect: a mutation fixture can supply a path the row under test never
  requests, and the test passes.
acceptance: the runner asserts every path a fixture supplies was actually
  FETCHED by the row; a fixture aimed at a row that fails earlier and
  never reaches that path must RED.
notes: muicharts (177ea1f), and it caught a decorative fixture on their
  tree within a minute. This is the GENERALISATION of this seat's own
  finding at `86d2d23`: deriving the probe page from the sitemap broke
  two of my mutation transforms, which had keyed on the literal
  `/backends` — so they intercepted nothing and **passed a mutation that
  never happened**, green rather than red. I fixed the two; muicharts
  built the guard that makes the class impossible. Theirs is the better
  fix and it came from the fork.

### 6. Mutation fixtures key on the battery's own constants

class: cargo (`tests/test_network_smoke.py`, `scripts/network_smoke.py`)
template exercises its acceptance: **YES**
files: `scripts/network_smoke.py`, `tests/test_network_smoke.py`
detect: a fixture names a path or a document as a literal where the
  battery exposes a constant.
acceptance: fixtures read `NEGOTIATION_PATH` / `NEGOTIATION_DOC` (or
  their successors) from the module; changing the constant moves the
  fixtures with it and no test needs editing.
notes: muicharts. The root cause under item 5 rather than the symptom —
  item 5 detects a dead fixture, this one stops it being written. Both,
  not either: the guard catches what a future literal would break, the
  constants stop the literal being introduced.

### 7. The probed page is a REAL registered page

class: contract (`scripts/network_smoke.py`)
template exercises its acceptance: **YES**
files: `scripts/network_smoke.py`, `tests/test_network_smoke.py`
detect: `require_probe_page()` can return a path that answers 404, and
  the rows report a negotiation failure rather than a bad probe.
acceptance: the derived page is asserted to be registered and 200 before
  any row negotiates against it; a sitemap naming a dead path SKIPS with
  that reason rather than failing the negotiation rows.
notes: muicharts. The failure mode the 1.6.45 sitemap derivation can
  still reach: the sitemap is generated from the registry, so a stale or
  proxied sitemap could name a path the app no longer serves, and every
  derived row would then fail for a reason that has nothing to do with
  content negotiation. Same family as "verify the artifact the claim is
  about".

### 8. Item 2's digest comparison, and item 5a's licence equality

class: contract (spec TEXT for two 1.6.45 blocks; the code is already
  right in this tree)
template exercises its acceptance: **YES**
files: `sync/SYNC-1.6.45.md` (the two blocks), `tests/test_skill_doc.py`,
  `tests/test_legal_pages.py`
detect: the spec text tells a fork to compare a bare `sha256` hex, or to
  look for a licence name with a substring.
acceptance: item 2's text says the index field is **`digest`** and
  carries the **`sha256:` prefix** — compared WITH the prefix, because
  `removeprefix` would also accept a bare hex that an index is not
  specified to publish. Item 5a's text says the served licence is the
  single `Licensed under the …` line, compared by EQUALITY, because a
  substring passes a document naming two licences.
notes: muicharts. Both are 1.6.45 corrections that landed in the CODE and
  were only half-written into the TEXT — and a fork builds from the text.
  Pannellum read the old digest line literally and got `MATCH: False` on
  a correct host; pannellum's own `"MIT" in TERMS_DOC` passed while it
  served "the MIT licence" against a LICENSE saying "MIT License".

### 9. Item 6 gains its fork-shape notes

class: contract (spec text for 1.6.45 item 6)
template exercises its acceptance: **NO — FORK-ONLY (a)**
files: `sync/SYNC-1.6.45.md` (item 6's block), `scripts/ci_leg.sh`
detect: (a) a fork that IS a component library runs the leg without
  installing its own package; (b) `ci_leg.sh` re-states a `>=` floor for
  the package item 1 pinned.
acceptance: **(a) FORK-ONLY** — a fork whose docs import its own package
  through `.. exec::` installs it editable (`pip install -e .`) into the
  leg venv, and proves it by the leg COLLECTING a non-zero count; the
  template cannot exercise this because it documents no package
  (`API_PACKAGES == []`, nothing to install). Without it the clone
  collects nothing and the leg greens over an app that never built.
  **(b)** the leg prints the RESOLVED dimll version and its path, so the
  omission is checkable either way.
notes: muischeduler. On (b), **measured on the template 2026-09-12 and it
  does NOT re-float here**: with 2.10.0 installed, `pip install --dry-run
  --report "dash-improve-my-llms[fastapi]>=2.3.4"` changes nothing
  (requirement already satisfied), and on the mask path the appended
  floor resolves TOGETHER with requirements.txt's `==2.10.0`, which wins.
  Here the line is load-bearing ONLY for adding the ASGI extra, which
  requirements.txt leaves commented out per-backend. So (b) is a FORK
  SHAPE — say so in the block, or the next reader treats a working line
  as a bug. It bites exactly where muischeduler is: requirements pinning
  both extras on one line, making the script's line redundant AND a floor
  restatement.

### 10. `licence_name()` belongs where the licence is served

class: contract (`lib/skill_doc.py`, `pages/legal.py`)
template exercises its acceptance: **YES**
files: `lib/skill_doc.py`, `pages/legal.py`, `tests/test_legal_pages.py`
detect: `licence_name()` is defined in a module whose own documents state
  no licence.
acceptance: the function lives where the licence is served, and item 5a's
  text says which served surface is DERIVED and which is a literal
  PINNED BY A TEST.
notes: **Measured at `86d2d23`, 2026-09-12 — do not re-measure.**
  `licence_name()` is defined in `lib/skill_doc.py` and NEVER called
  there; its callers are `pages/legal.py` and the tests. Surfaces
  carrying "MIT License": `/terms` YES, `/terms/llms.txt` YES,
  `/llms.txt` YES, `/.well-known/agent-skills/index.json` **NO**,
  `/assets/SKILL.md` **NO**, `build_skill_md()` **NO**. So the module
  that reads LICENSE produces the only documents that do not mention it.
  `/llms.txt`'s single occurrence is `pages/home.md:262`, a HAND-TYPED
  literal — held honest by a test asserting `licence_name()` appears
  there, so it reds if LICENSE drifts, but still a restatement inside an
  item whose claim is "derived rather than restated". `/terms/llms.txt`
  is the derived one.
  **A fork with no `home.md` fails that `/llms.txt` assertion on a
  correct tree** (muischeduler, DIVERGENCES 4), so the block is
  fork-shape-aware.
  LEFT AS A SEPARATE DECISION, not taken here: whether `SKILL.md` and the
  skills index SHOULD carry the licence at all.

### 11. The quickstart accepts `###`, and `/backends` hides in tests

class: cargo (`lib/skill_doc.py`) + contract (item 3's block)
template exercises its acceptance: **YES**
files: `lib/skill_doc.py`, `tests/test_skill_doc.py`,
  `tests/test_access.py`, `sync/SYNC-1.6.45.md` (item 3's block)
detect: `^##\s+` in the quickstart extractor; a borrowed page literal in
  any TEST.
acceptance: `#{2,4}` accepts `###` and `####` (measured at `86d2d23`:
  `^##\s+` matches `## Quick Start` and NOT `### Quick Start` or
  `#### Quick Start`), with the 1.6.45 non-empty assertion kept — it
  already makes a `###` fork go RED rather than ship a quickstart-less
  SKILL.md silently. And item 3's block says the borrowed page hides in
  TESTS too, keyed on the conftest sample page.
notes: **The SIXTH borrowed `/backends` is `tests/test_access.py:32
  PUBLIC_PAGE`** (used at 184, 231, 236, 321) — invisible for months
  because Dash's soft 404 served the shell for an unregistered page;
  1.6.45 item 8's real 404 is what makes it fail at all. **Items 3 and 8
  are COUPLED: port them together**, or the in-process battery test reds
  main if 3 lands alone.
  The trap sentence this produced, now in the fleet record: **"each of us
  swept where we had been looking."** This seat's count of five was short
  by one because it swept the battery rows and never the tests;
  muicharts' was short by two for the mirror reason.
  `assets/SKILL.md` is gitignored (`.gitignore:208`) and untracked, so a
  fork cannot inspect a committed copy and must generate it.

---

## Held for the owner's word — NOT to be written by any session

Two `.claude/CLAUDE.md` kit lines are queued and **require the owner's
own word, typed in his terminal**. A peer's recommendation is not that
word and cannot become one; CLAUDE.md is named in its own list of things
needing it. They are listed here as a RECORD, not as work anyone may do:

1. **A per-UID temp dir is shared state** — every work path under it
   carries the repo's identity. (1.6.45's `REPO_KEY` fix; pannellum's
   contaminated clone reported another fork's commit with EXACTLY the
   clean numbers.)
2. **Capturing an exit code is useless if nothing consults it** — the
   commit must DEPEND on the check: `lint && git add … && git commit`,
   never `lint ; git add … && git commit`. (muicharts; the separator, not
   the pipeline, and the transcript reads identically either way.)

Item 4 above also moves a trap line, so it carries the same gate.
