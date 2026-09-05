"""The ledger's boot guard — 1.6.44 item 22.

`analytics_path()` falls back SILENTLY to the repository root, which is the
container filesystem and is replaced wholesale on every deploy.
`PAGE_VISIBILITY_FILE` has warned about exactly this since the pilot host
lost its board toggles twice; the ledger — the more expensive thing to lose
— said nothing (note 96: muischeduler, email, emojimart).

DEVIATION FROM THE ITEM'S ACCEPTANCE, stated rather than quietly taken. The
item asks for the line to be asserted "via caplog". This warning is a
`print`, not a `logger.warning`, for two reasons: it fires at IMPORT time,
where caplog's handler is not yet attached and a re-import in-process is
unreliable; and it deliberately mirrors
`lib.page_visibility._persistence_warning`, which is also a print, so the
two land beside each other in one deploy log for an operator who has learnt
to look for one of them. Tested by running a real fresh interpreter in both
env states, which is a stronger check than caplog would have been — it
exercises the actual boot path rather than a re-entry into a loaded module.
"""
from __future__ import annotations

import subprocess
import sys

from conftest import REPO_ROOT

IMPORT_TRACKER = "import sys; sys.path.insert(0, '.'); import lib.analytics_tracker"


def _boot(env_value):
    """Import the tracker in a fresh interpreter; return combined output."""
    import os

    env = dict(os.environ)
    env.pop("TRAFFIC_ANALYTICS_FILE", None)
    if env_value is not None:
        env["TRAFFIC_ANALYTICS_FILE"] = str(env_value)
    result = subprocess.run([sys.executable, "-c", IMPORT_TRACKER],
                            cwd=REPO_ROOT, env=env,
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    return result.stdout + result.stderr


def test_an_unset_path_warns_at_boot():
    output = _boot(None)
    assert "[analytics] WARNING" in output
    assert "TRAFFIC_ANALYTICS_FILE unset" in output
    assert "will not survive a deploy" in output
    assert "visitor_analytics.json" in output, (
        "the warning must name the path it is warning about — an operator "
        "needs to know which file is about to be lost"
    )


def test_a_configured_path_is_silent(tmp_path):
    """The other direction, so the guard cannot pass as a constant."""
    output = _boot(tmp_path / "visitor_analytics.json")
    assert "[analytics] WARNING" not in output, output


def test_the_warning_mirrors_its_sibling():
    """Same shape, same prefix style, same advice — one habit covers both."""
    tracker = (REPO_ROOT / "lib" / "analytics_tracker.py").read_text()
    visibility = (REPO_ROOT / "lib" / "page_visibility.py").read_text()

    assert "[analytics] WARNING" in tracker
    assert "[visibility] WARNING" in visibility
    for phrase in ("Blueprint sync", "not a mounted disk"):
        assert phrase in tracker and phrase in visibility, (
            f"{phrase!r} is in one guard and not the other"
        )


def test_a_var_path_that_is_not_a_mount_also_warns():
    """The second failure shape: an app can `mkdir /var/data` on the
    container filesystem and everything works until the next deploy."""
    output = _boot("/var/definitely-not-a-mount/visitor_analytics.json")
    assert "[analytics] WARNING" in output
    assert "not a mounted disk" in output


def test_the_guard_pairs_with_the_healthz_block():
    """Item 22 says it once at boot; item 20 says it continuously.

    They must AGREE, which is a different assertion from either of their
    values — and the reason this test says so rather than pinning `False`:
    the suite points TRAFFIC_ANALYTICS_FILE at a tmpdir, so `persistent` is
    correctly True here while it is False for a bare `python run.py`. A test
    that pinned the value would have been pinning the fixture.
    """
    from pathlib import Path

    from lib.analytics_tracker import analytics_path
    from lib.health import _ledger_block

    block = _ledger_block()
    resolved = Path(analytics_path()).resolve()
    inside_tree = str(resolved).startswith(str(REPO_ROOT.resolve()) + "/")

    assert block["persistent"] is (not inside_tree), (
        f"healthz says persistent={block['persistent']} for {resolved}, which "
        f"is {'inside' if inside_tree else 'outside'} the tree — the boot "
        "guard and the health block are reading different things"
    )
    assert block["path"] == str(resolved)
