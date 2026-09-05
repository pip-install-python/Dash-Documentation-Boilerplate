"""The docs/ sweep — 1.6.44 item 7.

`.flake8` excludes `docs/*/`, so a lint over the repository says nothing
about the Python a documentation site actually renders. `py_compile` reads
those files; CI runs it as a named step. This module holds the step to its
name and the corpus to being non-empty.
"""
from __future__ import annotations

import importlib.util
import py_compile
import subprocess
import sys

import pytest

from conftest import REPO_ROOT

CI = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text()
DOCS_PY = sorted(REPO_ROOT.glob("docs/**/*.py"))


def test_the_sweep_step_exists_by_name():
    """Item 7's detect. The step name is what a reader of a red run sees."""
    assert "name: py_compile sweep of docs/" in CI
    assert "python3 -m py_compile" in CI


def test_the_sweep_refuses_an_empty_corpus():
    """Note 88, in the workflow itself: a sweep of nothing is not a pass."""
    step = CI.split("name: py_compile sweep of docs/", 1)[1].split("- name:", 1)[0]
    assert 'if [ "$count" -eq 0 ]' in step
    assert "::error::" in step, "an empty corpus must fail the run, not warn"


def test_the_docs_corpus_is_not_empty():
    assert len(DOCS_PY) >= 1, "nothing under docs/ to sweep"


def test_every_docs_module_compiles():
    """The check flake8 cannot make, made here too so a local run catches it
    before CI does."""
    broken = []
    for path in DOCS_PY:
        try:
            py_compile.compile(str(path), cfile=str(path) + "c", doraise=True)
        except py_compile.PyCompileError as exc:
            broken.append(f"{path.relative_to(REPO_ROOT)}: {exc.msg.splitlines()[0]}")
        finally:
            (path.parent / (path.name + "c")).unlink(missing_ok=True)
    assert broken == [], broken
    assert len(DOCS_PY) >= 1


def test_the_lint_config_excludes_docs():
    """The reason the sweep exists, checked WITHOUT running the linter.

    This is the tool-free half, and it is the half CI can actually run: the
    test job installs pytest and the app's requirements, NOT flake8 — flake8
    lives in the lint job. The first version of this module shelled out to
    `python -m flake8` and went red on every matrix leg for that reason
    (CD run 33941955814, all seven test legs, lint itself green).

    Item 10's rule, met from the other side: name the tools whose invocation
    is not the one your check will have. A test that needs a tool the job
    does not install is not testing the code, it is testing the job.
    """
    config = (REPO_ROOT / ".flake8").read_text()
    exclude = config.split("exclude", 1)[1].split("per-file-ignores", 1)[0]
    assert "docs/*/" in exclude, (
        "flake8 no longer excludes docs/ — the sweep's premise changed, so "
        "read it again before trusting either check"
    )


def test_py_compile_catches_a_broken_docs_file(tmp_path):
    """The other half, and it needs nothing but the interpreter.

    A syntactically broken file inside docs/ is loud to py_compile. Whether
    flake8 is blind to it is asserted above from the config; measured
    directly by the test below wherever flake8 is actually installed.
    """
    probe = REPO_ROOT / "docs" / "_pycompile_probe_tmp.py"
    probe.write_text("def broken(:\n    pass\n")
    try:
        compiled = subprocess.run([sys.executable, "-m", "py_compile", str(probe)],
                                  cwd=REPO_ROOT, capture_output=True, text=True)
    finally:
        probe.unlink(missing_ok=True)
        for cached in (REPO_ROOT / "docs").glob("__pycache__/_pycompile_probe_tmp*"):
            cached.unlink(missing_ok=True)

    assert compiled.returncode != 0 and "SyntaxError" in compiled.stderr


def test_flake8_alone_would_not_have_caught_it():
    """The live measurement, wherever flake8 exists.

    SKIPPED — never passed — where it does not. A skip says "not measured
    here"; a pass would say "measured and fine", which is note 88's defect
    and would be especially rich in the module about checks that cannot
    fail.
    """
    if importlib.util.find_spec("flake8") is None:
        pytest.skip("flake8 is not installed in this environment (CI runs it "
                    "in the lint job, not the test job) — the config-level "
                    "assertion above covers the same fact here")

    probe = REPO_ROOT / "docs" / "_flake8_probe_tmp2.py"
    probe.write_text("def broken(:\n    pass\n")
    try:
        lint = subprocess.run([sys.executable, "-m", "flake8", "docs/"],
                              cwd=REPO_ROOT, capture_output=True, text=True)
    finally:
        probe.unlink(missing_ok=True)
        for cached in (REPO_ROOT / "docs").glob("__pycache__/_flake8_probe_tmp2*"):
            cached.unlink(missing_ok=True)

    # The skip decision is made from the RESULT as well as from find_spec:
    # an importable-but-unrunnable flake8 (a broken install, or a stub on
    # PYTHONPATH — which is how CI's condition was reproduced locally) must
    # skip too. A tool that could not run has measured nothing, and the one
    # thing this test must never do is report that as "flake8 was blind".
    if "ModuleNotFoundError" in lint.stderr or "ImportError" in lint.stderr:
        pytest.skip(f"flake8 could not run here: {lint.stderr.strip().splitlines()[-1]}")

    assert lint.returncode == 0 and lint.stdout.strip() == "", (
        "flake8 now reads docs/ — the exclude changed, revisit the sweep"
    )


def test_no_page_module_emits_a_second_h1():
    """Item 7's rider: a page emitting its own `Title(order=1)` under
    markdown.py's order=2 renders a double heading.

    Asserted structurally rather than by grep, because a page that is NOT
    rendered through markdown.py (the changelog and API pages build their own
    layout) is entitled to its own order=1. The invariant is one h1 per page,
    which tests/test_pages.py holds on the rendered document; here we hold the
    markdown lane's own wrapper to order=2 so the two cannot both claim it.
    """
    markdown = (REPO_ROOT / "pages" / "markdown.py").read_text()
    assert "dmc.Title(metadata.name, order=2" in markdown, (
        "the markdown wrapper's heading level moved — every docs page's "
        "heading structure moved with it"
    )
    for page in ("changelog.py", "api.py"):
        # Comments stripped first (item 13, and the second time this module
        # has needed it): the raw source of both pages CONTAINS the string
        # "markdown.py" in comments explaining how they differ from it, so a
        # file-scoped grep reports the defect it is describing.
        src = "\n".join(
            line for line in (REPO_ROOT / "pages" / page).read_text().splitlines()
            if not line.lstrip().startswith("#")
        )
        if "order=1" in src:
            imports_markdown = any(
                line.startswith(("import ", "from "))
                and "pages.markdown" in line.replace("/", ".")
                for line in src.splitlines()
            )
            assert not imports_markdown, (
                f"pages/{page} emits order=1 AND renders through markdown.py"
            )
