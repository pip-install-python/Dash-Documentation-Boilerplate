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


def test_the_work_dir_carries_the_repo_identity():
    """A per-UID temp dir is SHARED STATE (pannellum, 2026-09-12).

    `$TMPDIR` is /tmp/claude-<uid> — shared by every seat running as this
    user — so `ci_leg_$BACKEND` put two repos' clones in ONE directory.
    Pannellum measured its own flask clone sitting at ANOTHER fork's commit
    while its other two legs were its own, and the contaminated run
    reported EXACTLY its clean numbers: a wrong green that announces
    nothing. It surfaced only because the battery then tripped on a file
    that WAS in its tree.

    basename alone is not enough — a fork and its template, or two
    checkouts of one fork, still collide — so the key carries a cksum of
    the full path.
    """
    source = (REPO_ROOT / "scripts" / "ci_leg.sh").read_text()
    work = [line for line in source.splitlines()
            if line.startswith("WORK=")]
    assert len(work) == 1, work
    assert "$REPO_KEY" in work[0] or "${REPO_KEY}" in work[0], (
        f"{work[0]} does not carry the repo identity — two seats on one UID "
        "will clone into the same directory and the counts will be somebody "
        "else's"
    )
    assert "REPO_KEY=" in source
    assert "cksum" in source, (
        "the key has no path hash — basename alone collides for a fork and "
        "its template, and for two checkouts of one repo"
    )


def test_the_repo_key_separates_the_three_collision_shapes():
    """The control: the key must differ for a fork vs the template, and for
    two checkouts sharing a basename. A key that were constant would satisfy
    the source pin above and fix nothing."""
    import subprocess

    def key(path: str) -> str:
        out = subprocess.run(
            ["bash", "-c",
             'printf "%s" "$(basename "$1")-$(printf %s "$1" | cksum '
             '| cut -d" " -f1)"', "_", path],
            capture_output=True, text=True, check=True)
        return out.stdout.strip()

    template = key("/repos/dash-documentation-boilerplate")
    fork = key("/repos/dash-pannellum-docs")
    twin = key("/elsewhere/dash-documentation-boilerplate")
    assert template != fork, (template, fork)
    assert template != twin, (
        f"{template} == {twin} — two checkouts sharing a basename collide, "
        "which is the case basename-alone got wrong"
    )


def test_the_interpreter_is_chosen_by_whether_its_venv_can_install():
    """leaflet's rider, 2026-09-12. Preference is the wrong selector.

    3.14.4's ensurepip ships pip 26.1, which validates TLS through the
    macOS truststore and ignores --cert/PIP_CERT, so behind a proxy the
    vendored sdist's isolated build env cannot reach the index and the
    venv build fails — dropping the whole leg to the weaker mask path on
    every seat here. Measured on this box: python3.14 -> "its venv could
    not install the leg"; python3.12 -> venv built, pip 24.0, 781
    collected, 773 passed.
    """
    source = (REPO_ROOT / "scripts" / "ci_leg.sh").read_text()
    assert "PY_CANDIDATES=" in source, (
        "the script still picks ONE interpreter by preference — on a "
        "3.14-default box behind a proxy that is the mask path every time"
    )
    assert "build_venv \"$cand_path\"" in source, (
        "the candidate loop does not test each interpreter by BUILDING "
        "its venv, which is the only thing that distinguishes them"
    )
    # the loop must try more than one, and 3.14 must still be first so a
    # box where its pip works is not downgraded
    candidates = [line for line in source.splitlines()
                  if line.startswith("PY_CANDIDATES=")][0]
    assert candidates.index("3.14") < candidates.index("3.12"), candidates
    assert "python3.12" in candidates and "python3.11" in candidates


def test_the_environment_block_prints_the_pip_version():
    """Which pip installed the leg is the difference between a real venv and
    a fallback, so the report says it rather than leaving it inferable."""
    source = (REPO_ROOT / "scripts" / "ci_leg.sh").read_text()
    assert '-m pip --version' in source
    assert 'echo "   pip ' in source


def test_a_concurrent_run_is_locked_out_rather_than_having_its_clone_deleted():
    """leaflet's second rider. REPO_KEY separates FORKS, not two runs of the
    same fork, and `rm -rf "$CLONE"` is what eats a concurrent run
    mid-suite.

    Verified live: a lock holding a LIVE pid refuses with exit 5; a lock
    holding a dead pid is cleared and the run proceeds (exit 0); the lock
    is released on exit.
    """
    source = (REPO_ROOT / "scripts" / "ci_leg.sh").read_text()
    assert 'LOCK="$WORK/.lock"' in source
    assert "exit 5" in source, (
        "the refusal shares an exit code with another failure — 3 is 'no "
        "verification possible' and 4 is 'masks ineffective', so a reader "
        "cannot tell which refusal happened"
    )
    assert 'kill -0 "$holder"' in source, (
        "the lock does not check whether the holder is alive, so one "
        "crashed run wedges the work dir forever"
    )
    assert "trap 'rm -f \"$LOCK\"' EXIT" in source, "the lock is never released"
    # The lock must be taken BEFORE the destructive clone step — compared
    # on CODE LINES, not on `source.index`. The first version of this
    # assertion used the raw string offsets and failed on a correct script,
    # because the lock's own COMMENT quotes `rm -rf "$CLONE"` while
    # explaining what it protects: the first textual match was the prose,
    # forty lines above the statement. Third instance of that trap in this
    # release, and the second inside a test written to pin a fix.

    def line_of(needle: str) -> int:
        for number, line in enumerate(source.splitlines(), 1):
            if line.lstrip().startswith("#"):
                continue
            if needle in line:
                return number
        raise AssertionError(f"{needle!r} appears only in comments")

    lock_at = line_of('LOCK="$WORK/.lock"')
    clone_at = line_of('rm -rf "$CLONE"')
    assert lock_at < clone_at, (
        f"the lock is taken at line {lock_at}, after the clone is deleted "
        f"at line {clone_at} — the race it exists to prevent has already "
        "happened by then"
    )
