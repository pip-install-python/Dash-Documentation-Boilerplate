"""The docs/ sweep — 1.6.44 item 7.

`.flake8` excludes `docs/*/`, so a lint over the repository says nothing
about the Python a documentation site actually renders. `py_compile` reads
those files; CI runs it as a named step. This module holds the step to its
name and the corpus to being non-empty.
"""
from __future__ import annotations

import py_compile
import subprocess
import sys

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


def test_flake8_alone_would_not_have_caught_it(tmp_path):
    """The reason the step exists, measured rather than asserted.

    A syntactically broken file inside docs/ is invisible to flake8 (the
    exclude) and loud to py_compile. If .flake8 ever stops excluding docs/,
    this test goes red and the sweep can be reconsidered.
    """
    probe = REPO_ROOT / "docs" / "_flake8_probe_tmp.py"
    probe.write_text("def broken(:\n    pass\n")
    try:
        lint = subprocess.run([sys.executable, "-m", "flake8", "docs/"],
                              cwd=REPO_ROOT, capture_output=True, text=True)
        compiled = subprocess.run([sys.executable, "-m", "py_compile", str(probe)],
                                  cwd=REPO_ROOT, capture_output=True, text=True)
    finally:
        probe.unlink(missing_ok=True)
        for cached in (REPO_ROOT / "docs").glob("__pycache__/_flake8_probe_tmp*"):
            cached.unlink(missing_ok=True)

    assert lint.returncode == 0 and lint.stdout.strip() == "", (
        "flake8 now reads docs/ — the exclude changed, revisit the sweep"
    )
    assert compiled.returncode != 0 and "SyntaxError" in compiled.stderr


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
