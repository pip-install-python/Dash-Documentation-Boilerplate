"""The v4 cargo test must pass against the OLDEST fork's rollup (1.6.36).

At 1.6.34 tests/test_traffic_rollup_v4.py imported `load_agent_hits` and
asserted `bot_visitors` — v3 seams that clerkhook (v4 without v3) lacks —
and a live fan-out would have landed it red on arrival. This runs the
cargo file, unmodified, against tests/fixtures/rollup_pre_v3.py in a
subprocess with ROLLUP_V4_MODULE set. Green here means the cargo is
safe on every fork's rollup shape the fleet has; red means someone
reached for v3 again.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def test_the_v4_cargo_test_passes_on_a_pre_v3_rollup():
    env = {**os.environ, "ROLLUP_V4_MODULE": "tests.fixtures.rollup_pre_v3"}
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
         "tests/test_traffic_rollup_v4.py"],
        cwd=REPO, env=env, capture_output=True, text=True, timeout=300,
    )
    assert proc.returncode == 0, (
        "the v4 cargo test reaches for a v3 seam — it would go red on the "
        "oldest fork (clerkhook):\n" + proc.stdout[-3000:] + proc.stderr[-1500:]
    )
    # pytest.ini's quiet mode prints dots and a percentage, no summary line.
    assert "[100%]" in proc.stdout and "failed" not in proc.stdout, proc.stdout[-500:]


def test_the_fixture_really_lacks_v3():
    from tests.fixtures import rollup_pre_v3 as fx
    import inspect

    assert not hasattr(fx, "load_agent_hits")
    assert "agent_visits" not in inspect.signature(fx.daily_rollup).parameters
