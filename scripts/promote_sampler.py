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

4. TWO CONSECUTIVE BAD READS BEFORE ANY VERDICT (note 149a, modelviewer).
   Mid-swap `/healthz` returns an empty or unparseable body for ONE tick
   with `release` already moved — a container restarting, not an outage. A
   watcher that calls that wrong cries wolf; one that reads it as "the run
   vanished" repeats the rate-limit mistake in a new costume. A single
   unreadable sample is an ordinary member of the bracket here; two in a
   row is reported as a condition in its own right.

5. PRINTS THE PUSH -> PROMOTE GAP beside the bracket (note 128a). The whole
   inference is that a push-watching Render would have swapped EARLIER than
   observed — which only separates the two triggers when the gap is bigger
   than the build+swap time. Under ~3 minutes the two hypotheses predict
   the same wire, and the honest output is "no verdict possible" rather
   than a number that looks like evidence.

The result is STRONG EVIDENCE, never proof: a queued or slow build could in
principle produce the same shape. The canonical discriminator is still the
first push that goes RED on main leaving `release` unmoved and the wire
unchanged.

    python3 scripts/promote_sampler.py --sha <the run's sha>
    python3 scripts/promote_sampler.py --sha <sha> --samples 8 --interval 45
    python3 scripts/promote_sampler.py --sha <sha> \
        --push 2026-09-11T00:50:07Z --promote 2026-09-11T00:51:59Z
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

# Below this, a push-watching Render and a promote-watching Render predict
# the same wire, because the gap is within the build+swap time itself
# (measured on this host: 99 s, 113 s, 103 s from the promote step).
MIN_GAP_FOR_A_VERDICT = 180


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


def parse_stamp(text: str):
    """An ISO-8601 `...Z` stamp, or None. Never raises on bad input."""
    from datetime import datetime, timezone

    try:
        cleaned = (text or "").strip().replace("Z", "+00:00")
        parsed = datetime.fromisoformat(cleaned)
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def consecutive_bad_reads(states: list) -> int:
    """The longest run of consecutive `unreadable` samples (note 149a)."""
    longest = run = 0
    for state in states:
        run = run + 1 if state == UNREADABLE else 0
        longest = max(longest, run)
    return longest


def gap_verdict(push: str, promote: str) -> tuple:
    """(seconds, message) for the push -> promote gap, or (None, message).

    A gap under MIN_GAP_FOR_A_VERDICT means the two hypotheses predict the
    same wire: no verdict is possible from this run however clean the
    bracket is, and saying so is the point.
    """
    first, second = parse_stamp(push), parse_stamp(promote)
    if first is None or second is None:
        return None, ("push -> promote gap: not given (pass --push and "
                      "--promote to get a verdict on which trigger the swap "
                      "followed)")
    seconds = (second - first).total_seconds()
    if seconds < 0:
        return seconds, (f"push -> promote gap: {seconds:.0f}s — the promote "
                         "precedes the push, so one of these stamps is wrong")
    if seconds < MIN_GAP_FOR_A_VERDICT:
        return seconds, (
            f"push -> promote gap: {seconds:.0f}s — NO VERDICT POSSIBLE. "
            f"Under {MIN_GAP_FOR_A_VERDICT}s a push-watching and a "
            "promote-watching Render predict the same wire, because the gap "
            "is inside the build+swap time. The bracket below is real; it "
            "just cannot say which trigger it followed.")
    return seconds, (
        f"push -> promote gap: {seconds:.0f}s — wide enough for a verdict: "
        "had Render reacted to the PUSH, the swap would have landed about "
        f"{seconds:.0f}s earlier than it did.")


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
    parser.add_argument("--push", default="",
                        help="the push's timestamp (ISO-8601, e.g. "
                             "2026-09-11T00:50:07Z)")
    parser.add_argument("--promote", default="",
                        help="the PROMOTE STEP's completed_at — the step, "
                             "never the deploy job's")
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

    print("\n--- gap ---")
    _seconds, message = gap_verdict(args.push, args.promote)
    print(message)

    worst = consecutive_bad_reads(states)
    if worst >= 2:
        print(f"\n--- {worst} CONSECUTIVE BAD READS ---")
        print("Two unreadable samples in a row is not the restart tick — one "
              "empty body mid-swap is a container coming back, this is not. "
              "Check the host before trusting anything below.")

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
