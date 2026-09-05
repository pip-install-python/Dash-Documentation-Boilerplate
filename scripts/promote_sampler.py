#!/usr/bin/env python3
"""Sample the wire and the CD run state on ONE timeline, across a promote.

The concrete form of trap 3(a) (1.6.44 item 17; pannellum 15917bc,
modelviewer 540926a, emojimart 166e33a, clerkhook f1481f5). It answers one
question — does Render react to the PUSH or to the PROMOTE? — and it answers
it on a green push, without waiting for a red one.

Three things this does that a hand-written watcher gets wrong:

1. ONE LOOP, ONE TIMELINE. The wire and the run state are sampled in the
   same iteration. Two separate reconstructions invite exactly the
   arithmetic error the measurement exists to avoid.

2. TIMES AGAINST THE PROMOTE STEP'S `completed_at`, never the deploy JOB's.
   The job CONTAINS the build-match wait, so it completes when the wait SEES
   the swap: it tracks the swap and never the promote, and landed at -13 s
   and 0 s on this host's two measured pairs. Useless for timing either way.

3. RETRIES EACH SAMPLE THREE TIMES and records `unreadable` as a state
   DISTINCT from `old`. The container restart lands exactly where the
   bracket needs its sample — twice out of two on this host — so an
   un-retried loop is systematically blind at the only moment that matters,
   and collapsing unreadable into old invents a bracket nobody observed.

The result is STRONG EVIDENCE, never proof: a queued or slow build could in
principle produce the same shape. The canonical discriminator is still the
first push that goes RED on main leaving `release` unmoved and the wire
unchanged.

    python3 scripts/promote_sampler.py --sha <the run's sha>
    python3 scripts/promote_sampler.py --sha <sha> --samples 8 --interval 45
"""
from __future__ import annotations

import argparse
import json
import ssl
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

DEFAULT_URL = "https://boilerplate.2plot.dev/healthz"
SAMPLES = 8
INTERVAL = 45
ATTEMPTS = 3

# Every ad-hoc probe against a production host needs this: the seat hit
# CERTIFICATE_VERIFY_FAILED in a hand-written CD watcher one hour after
# shipping the same fix inside both live tools.
try:
    import certifi

    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except Exception:  # pragma: no cover — certifi absent
    SSL_CONTEXT = ssl.create_default_context()

try:
    from lib.constants import PROBE_UA_SUFFIX as _PROBE
except Exception:  # pragma: no cover — running outside a checkout
    _PROBE = "2plot-internal/probe"
PROBE_UA = f"curl/8 {_PROBE} promote-sampler"

OLD, NEW, UNREADABLE = "old", "NEW", "unreadable"


def now() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M:%SZ")


def read_build(url: str) -> str | None:
    """The `build` field, or None when the host could not be read.

    None is a STATE, not an error: it is the container restart, and it is
    the sample the bracket depends on.
    """
    for attempt in range(ATTEMPTS):
        if attempt:
            time.sleep(2)
        try:
            request = urllib.request.Request(url)
            request.add_header("User-Agent", PROBE_UA)
            with urllib.request.urlopen(request, timeout=15,
                                        context=SSL_CONTEXT) as response:
                return json.loads(response.read().decode()).get("build") or None
        except (urllib.error.URLError, OSError, ValueError):
            continue
    return None


def classify(build: str | None, wanted: str) -> str:
    if build is None:
        return UNREADABLE
    return NEW if build.startswith(wanted[:12]) else OLD


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sha", required=True, help="the sha being promoted")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--samples", type=int, default=SAMPLES)
    parser.add_argument("--interval", type=int, default=INTERVAL)
    args = parser.parse_args(argv[1:])

    print(f"sampling {args.url} for {args.sha[:12]} — "
          f"{args.samples} samples at {args.interval}s\n")
    timeline = []
    for i in range(args.samples):
        if i:
            time.sleep(args.interval)
        build = read_build(args.url)
        state = classify(build, args.sha)
        stamp = now()
        timeline.append((stamp, state, build))
        print(f"{stamp}  {state:10}  {(build or '-')[:12]}", flush=True)

    states = [s for _, s, _ in timeline]
    print("\n--- bracket ---")
    if NEW not in states:
        print("no NEW sample: the swap did not land inside the window")
        return 1
    first_new = states.index(NEW)
    if OLD not in states[:first_new]:
        print("no OLD sample before the first NEW — this run cannot say what "
              "the swap followed, which is the whole evidence. Start the "
              "sampler BEFORE the promote.")
        return 1
    last_old = max(i for i, s in enumerate(states[:first_new]) if s == OLD)
    print(f"last OLD   {timeline[last_old][0]}")
    for stamp, state, _ in timeline[last_old + 1:first_new]:
        print(f"  {state}  {stamp}   <- inside the bracket")
    print(f"first NEW  {timeline[first_new][0]}")
    print("\nTime this against the PROMOTE STEP's completed_at — the step, "
          "not the deploy job.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
