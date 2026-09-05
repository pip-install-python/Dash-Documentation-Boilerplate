"""`scripts/ci_leg.sh` — 1.6.45 item 6, note 107.

The script exists because 1.6.44 went red three times on one distinction:
"three lanes green" on a single interpreter proves the lanes' CODE PATHS and
says nothing about what each CI leg INSTALLS. Every one of those failures was
green on a machine that happened to carry all three backends, plus Pillow,
plus flake8.

These tests hold the script to the properties that make it worth running.
They do NOT run it — a full leg takes ~15 s and the suite would then contain
three copies of itself.
"""
from __future__ import annotations

import os
import stat
import subprocess

from conftest import REPO_ROOT

SCRIPT = REPO_ROOT / "scripts" / "ci_leg.sh"
SOURCE = SCRIPT.read_text()


def test_the_script_exists_and_is_executable():
    """Item 6's detect."""
    assert SCRIPT.is_file()
    assert os.stat(SCRIPT).st_mode & stat.S_IXUSR, "not executable"


def test_it_refuses_an_unknown_backend():
    result = subprocess.run(["bash", str(SCRIPT), "sqlalchemy"],
                            capture_output=True, text=True, cwd=REPO_ROOT)
    assert result.returncode == 2
    assert "usage:" in result.stderr


def test_it_installs_what_ci_installs_in_ci_s_order():
    """The venv path must be ci.yml's block, not an approximation of it."""
    ci = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text()
    for fragment in ("-r requirements.txt",
                     "--no-deps markdown2dash==0.1.2",
                     "pytest"):
        assert fragment in SOURCE, f"the script does not install {fragment!r}"
        assert fragment in ci, f"ci.yml no longer installs {fragment!r} — the "
    assert 'dash[$BACKEND]' in SOURCE and "httpx" in SOURCE
    assert 'dash-improve-my-llms[$BACKEND]' in SOURCE


def test_it_does_not_add_a_second_q():
    """pytest.ini carries -q; a second one suppresses the summary line, so the
    run reports no counts at all (note 99 — which cost three runs of mine
    before it was noticed)."""
    assert "-m pytest tests" in SOURCE
    assert "pytest tests -q" not in SOURCE
    assert "-qq" not in SOURCE


def test_it_warns_against_upgrading_pip_in_a_sandbox():
    """pip >= 26 validates against the system trust store and rejects a
    proxy's certificate — every index fetch dies. The venv's stock pip works,
    and the next person should not rediscover that."""
    assert "upgrade pip" in SOURCE
    assert "trust store" in SOURCE or "certificate" in SOURCE


def test_the_fallback_announces_itself_as_weaker():
    """A fallback that looked like the real thing would be the same species
    of lie the script exists to prevent."""
    assert "FALLING BACK TO RESOLVED MASKS" in SOURCE
    assert "weaker than a venv run" in SOURCE


def test_the_masks_are_resolved_not_assumed():
    """Assuming is how the first attempt masked pydantic and httpx — both of
    which CI's flask leg HAS (dash requires pydantic, dash-clerk-auth requires
    httpx) — and manufactured a failure that did not exist."""
    assert "--dry-run" in SOURCE and "--report" in SOURCE
    assert "sys.modules[_m] = None" in SOURCE, (
        "a raising stub still satisfies find_spec; assigning None to "
        "sys.modules is what makes both the import AND find_spec fail"
    )


def test_the_fallback_proves_the_masks_bite_before_reporting_green():
    """A mask that silently fails to apply produces a green run that swept
    nothing — note 88, in the tool built to prevent note 88's cousin."""
    assert "control: the masks bite" in SOURCE
    assert "refusing to report a green" in SOURCE


def test_it_names_the_absences_it_is_testing_for():
    for pkg in ("fastapi", "starlette", "quart", "pillow", "flake8"):
        assert pkg in SOURCE.lower(), f"{pkg} is not among the tracked absences"
