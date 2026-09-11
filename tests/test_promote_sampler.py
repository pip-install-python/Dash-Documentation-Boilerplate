"""The promote sampler reports what it observed, and refuses what it did not.

1.6.45 rider, note 149. Two additions to the script, both about the
difference between a measurement and a number that looks like one:

  (a) two consecutive bad reads before anything is called wrong — one
      unparseable /healthz mid-swap is a container restarting, and this
      host's own pairs put exactly one unreadable sample inside the bracket
      twice out of two;
  (b) the push -> promote gap printed beside the bracket, because the whole
      inference is that a push-watching Render would have swapped EARLIER
      than observed — which separates the two hypotheses only when the gap
      exceeds the build+swap time.
"""
from __future__ import annotations

import importlib.util

import pytest

from conftest import REPO_ROOT

_SPEC = importlib.util.spec_from_file_location(
    "promote_sampler", REPO_ROOT / "scripts" / "promote_sampler.py")
sampler = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(sampler)


# ------------------------------------------- (a) consecutive bad reads --


def test_one_unreadable_sample_is_not_a_verdict():
    """The restart tick. This host put exactly one unreadable sample inside
    the bracket on both measured pairs — a rule that fired on one would cry
    wolf on every promote."""
    states = [sampler.OLD, sampler.UNREADABLE, sampler.NEW]
    assert sampler.consecutive_bad_reads(states) == 1


def test_two_in_a_row_is():
    states = [sampler.OLD, sampler.UNREADABLE, sampler.UNREADABLE,
              sampler.NEW]
    assert sampler.consecutive_bad_reads(states) == 2


def test_bad_reads_must_be_CONSECUTIVE():
    """Two unreadable samples with a good one between them are two restarts,
    not an outage — counting them together would reintroduce the wolf."""
    states = [sampler.OLD, sampler.UNREADABLE, sampler.OLD,
              sampler.UNREADABLE, sampler.NEW]
    assert sampler.consecutive_bad_reads(states) == 1


def test_leaflets_shape_two_consecutive_unreadable_is_reported():
    """leaflet's run had two consecutive unreadable samples between its last
    old and first new — the shape the rule is meant to name."""
    states = [sampler.OLD, sampler.UNREADABLE, sampler.UNREADABLE,
              sampler.NEW]
    assert sampler.consecutive_bad_reads(states) >= 2


# ------------------------------------------------- (b) the gap verdict --


def test_this_hosts_own_first_pair_is_too_narrow_for_a_gap_verdict():
    """The template's own pair, run 33576940156 / ac20ed1: push 00:50:07Z,
    promote step 00:51:59Z — 112 s, UNDER the floor.

    Applying note 149's own rule retroactively, neither of this host's
    recorded pairs can separate the two triggers on the GAP alone. That is
    the honest reading, not a bug in the floor: the traps' inference rests
    on where the bracket sits (push + 99 s build+swap = 00:51:46Z, and the
    wire was still old at 00:52:03Z), which holds with ~17 s of margin.
    Thin enough that the rider's ~3 min floor is exactly right to demand
    more before anyone calls it a verdict.
    """
    seconds, message = sampler.gap_verdict("2026-09-02T00:50:07Z",
                                           "2026-09-02T00:51:59Z")
    assert seconds == 112
    assert "NO VERDICT POSSIBLE" in message


def test_the_second_pair_is_also_too_narrow():
    """run 33595792466 / 4e17525: 05:42:53Z -> 05:45:08Z = 135 s. Still under
    the floor — which is the finding, not a bug in the floor: this host's
    build+swap is 99-113 s, so neither of its own pairs can separate the two
    triggers on gap alone, and the inference in the traps rests on the
    bracket's position rather than on the gap."""
    seconds, message = sampler.gap_verdict("2026-09-02T05:42:53Z",
                                           "2026-09-02T05:45:08Z")
    assert seconds == 135
    assert "NO VERDICT POSSIBLE" in message


def test_a_gap_over_the_floor_reads_as_a_verdict():
    seconds, message = sampler.gap_verdict("2026-09-02T00:50:00Z",
                                           "2026-09-02T00:56:00Z")
    assert seconds == 360
    assert "NO VERDICT POSSIBLE" not in message
    assert "wide enough for a verdict" in message


def test_missing_stamps_say_so_rather_than_inventing_a_gap():
    seconds, message = sampler.gap_verdict("", "")
    assert seconds is None
    assert "not given" in message


def test_a_promote_before_the_push_is_named_as_bad_input():
    """Silently reporting a negative gap as "narrow" would hide a swapped
    pair of arguments, which is the easiest mistake to make here."""
    seconds, message = sampler.gap_verdict("2026-09-02T00:51:59Z",
                                           "2026-09-02T00:50:07Z")
    assert seconds < 0
    assert "precedes the push" in message


def test_an_unparseable_stamp_does_not_raise():
    """The sampler runs beside a live promote; it must never die on input."""
    assert sampler.gap_verdict("not-a-time", "2026-09-02T00:50:07Z")[0] is None
    assert sampler.parse_stamp("") is None
    assert sampler.parse_stamp("2026-09-02T00:50:07Z") is not None


@pytest.mark.parametrize("gap,verdict", [(179, False), (180, True),
                                         (181, True)])
def test_the_floor_is_where_it_says_it_is(gap, verdict):
    """The boundary, pinned: a floor nobody tested is a floor that drifts."""
    from datetime import datetime, timedelta, timezone

    start = datetime(2026, 9, 2, tzinfo=timezone.utc)
    seconds, message = sampler.gap_verdict(
        start.isoformat().replace("+00:00", "Z"),
        (start + timedelta(seconds=gap)).isoformat().replace("+00:00", "Z"))
    assert seconds == gap
    assert ("NO VERDICT POSSIBLE" not in message) is verdict
