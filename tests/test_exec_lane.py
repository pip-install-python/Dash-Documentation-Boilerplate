"""`.. exec::` reaches the machine lane — the fourth empty-page mechanism.

Owner's decision 0aa (2026-08-31), road (a) with the dedupe rule, after the
item-18 fan-out found this class live on SIX forks: muicharts, pannellum,
muischeduler, email, flows and llms. The shape is always the same — a
directive that renders Dash components puts its output only in the React
tree, while the machine lane, the prerender and the crawler HTML are built
from the markdown SOURCE where the directive line is stripped. The page
looks perfect in a browser the entire time.

Measured HERE before the fix: `/fastapi-showcase/llms.txt` carried 19,378
bytes of prose about three components whose code appeared nowhere in it.

Two roads answer this class and they now compose rather than collide:
(a) auto-render the exec'd module's SOURCE into the prose, through the same
fence-aware pass `.. source::` uses — one parse, two consumers; and
(b) hand-pair every `.. exec::` with a `.. source::` (modelviewer's road),
which four of this repo's five exec-using docs already took. The dedupe
rule is what makes (a) skip where (b) already applies.

A NOTE ON HOW THIS FILE IS WRITTEN. The round that produced it kept finding
pins that could not go red — a heading asserted instead of rows, a substring
counted instead of an element, a grep matching prose ABOUT the defect. So
every content pin here is mutation-checked, and the fixtures carry the
NEGATIVE cases (fenced, differently-targeted) rather than only the happy one.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent


# --------------------------------------------------------------- unit --


UNPAIRED = """# Page

Some prose.

.. exec::docs.fastapi-showcase.async_demo

More prose.
"""

# `:code: false` is the author saying "this module is plumbing for an
# embed, not documentation" (muischeduler). Rendering it into the machine
# lane publishes what the browser lane deliberately hides — and silently,
# because the browser keeps looking right. This repo shipped that inversion
# on all three of its own unpaired directives before the correction.
HIDDEN = """# Page

.. exec::docs.fastapi-showcase.async_demo
    :code: false

More prose.
"""

PAIRED = """# Page

.. exec::docs.fastapi-showcase.async_demo

Source code:

.. source::docs/fastapi-showcase/async_demo.py
    :defaultExpanded: false
"""

# The third case, and the one that makes the dedupe safe: a `.. source::`
# IS present, but for a different target. Deduping on "any source nearby"
# would swallow exactly the unpaired directive the rule exists to catch.
DIFFERENT_TARGET = """# Page

.. exec::docs.fastapi-showcase.async_demo

.. source::docs/fastapi-showcase/stress_test.py
"""

FENCED = """# Page

Here is how you write one:

```markdown
.. exec::docs.fastapi-showcase.async_demo
```

That was documentation.
"""


def _expand(text: str) -> str:
    """pages.markdown registers a page at import, so it cannot be imported
    until the app exists — every caller here takes the `app_module` fixture
    first."""
    from pages.markdown import _expand_source_directives

    return _expand_source_directives(text)


def _needle() -> str:
    """A real line from the module, read at run time.

    Never a literal: a hardcoded expectation drifts out of the file it
    claims to be about and the pin quietly starts proving nothing.

    Fork-invariant shape (leaflet, 2026-08-31): first top-level `def`, ELSE
    first top-level assignment. A `def `-only search finds nothing on a fork
    whose showcase convention is a module-level `component = dmc.Stack(...)`
    with no functions anywhere, and the pin then fails at collection rather
    than testing anything. Multi-line-string openers are skipped — anchoring
    on a `QUICKSTART = ` triple-quote opener works but is a poor needle.
    """
    src = (REPO / "docs" / "fastapi-showcase" / "async_demo.py").read_text()
    lines = src.split("\n")
    for line in lines:
        if line.startswith("def "):
            return line
    for line in lines:
        if re.match(r"^\w+\s*=", line) and not re.search(r'=\s*("""|\'\'\')', line):
            return line
    pytest.fail("no top-level def or assignment in the module to anchor the pin on")


def test_the_needle_is_really_in_the_module():
    """Non-vacuity for every assertion below."""
    assert _needle().startswith("def ")


def test_an_unpaired_exec_renders_its_module_source(app_module):
    out = _expand(UNPAIRED)
    assert _needle() in out, "the exec'd component's code never reached the prose"
    assert "```python" in out
    assert ".. exec::" not in out, "the raw directive line survived into the prose"


def test_a_code_false_directive_withholds_the_source_but_says_so(app_module):
    """The author's signal is honoured, and the gap is VISIBLE.

    Skipping silently would leave the same shape as the defect: a machine
    document with nothing where a component is. Broken, hidden and absent
    must not look alike.
    """
    out = _expand(HIDDEN)
    assert _needle() not in out, "`:code: false` source was published to the machine lane"
    assert "source withheld" in out and "async_demo.py" in out, (
        "the withheld component left no trace at all"
    )
    # Line-exact, not a substring: the marker itself quotes `:code: false`,
    # so a substring assertion matches the pin's own output. That is the
    # third time in this round a check matched prose ABOUT the thing it was
    # asked to find — the UA grep flagged its own comment, and before that a
    # naive count read fenced documentation as defects.
    assert not any(ln.strip() == ":code: false" for ln in out.split("\n")), (
        "the directive's option line was left behind as prose"
    )


def test_a_paired_exec_renders_once_not_twice(app_module):
    """The dedupe rule. (a) must not double what (b) already provides."""
    out = _expand(PAIRED)
    assert out.count("# File: docs/fastapi-showcase/async_demo.py") == 1, (
        "the hand-paired page shows its source twice"
    )
    assert _needle() in out
    assert ".. exec::" not in out


def test_a_source_for_a_different_target_does_not_dedupe(app_module):
    """The case that keeps the dedupe honest."""
    out = _expand(DIFFERENT_TARGET)
    assert out.count("# File: docs/fastapi-showcase/async_demo.py") == 1, (
        "an unrelated `.. source::` suppressed the auto-render"
    )
    assert out.count("# File: docs/fastapi-showcase/stress_test.py") == 1


def test_a_fenced_exec_stays_documentation(app_module):
    """Fence-awareness, carried over WITH the fix shape (clerkhook).

    A directive inside a ``` block teaches the syntax. Expanding it there
    injects a fence inside an open fence, closes it early, and the rest of
    the page serves as broken structure — the 2026-08-23 defect, one
    directive along.
    """
    out = _expand(FENCED)
    assert ".. exec::docs.fastapi-showcase.async_demo" in out, "documentation was expanded"
    assert _needle() not in out


def test_a_missing_exec_target_says_so_instead_of_vanishing(app_module):
    """Broken and empty must not look alike — silence is what let this
    class survive on six forks."""
    out = _expand(".. exec::docs.nope.missing_module\n")
    assert "<!-- Error" in out and "missing_module" in out


# --------------------------------------------------- the live registry --


def test_every_exec_in_this_repos_docs_reaches_the_machine_lane(client, app_module):
    """The pages themselves, not a fixture.

    Content, never a heading: the heading was present on the wire the whole
    time /fastapi-showcase served zero lines of the three components it
    describes.
    """
    import re

    checked = 0
    for md in sorted((REPO / "docs").rglob("*.md")):
        fence = None
        for line in md.read_text().split("\n"):
            head = line.lstrip()[:3]
            if fence is None and head in ("```", "~~~"):
                fence = head
                continue
            if fence is not None and head == fence:
                fence = None
                continue
            if fence is not None:
                continue
            m = re.match(r"^\.\. exec::(.+?)$", line)
            if not m:
                continue
            target = REPO / (m.group(1).strip().replace(".", "/") + ".py")
            body = md.read_text()
            # `.strip("\"'")` — a fork whose frontmatter QUOTES its values
            # (`endpoint: "/attribution"`) otherwise builds
            # `/"/attribution"/llms.txt`, gets "llms.txt not available", and
            # sees every page reported as a mechanism-4 leak: a wall of false
            # failures on a pin that is otherwise right (leaflet, 2026-08-31).
            endpoint = re.search(r"^endpoint:\s*(\S+)", body, re.M).group(1).strip("\"'")
            url = f"{endpoint.rstrip('/')}/llms.txt"
            doc = client.get(url).text
            anchors = [
                ln for ln in target.read_text().split("\n")
                if ln.startswith("def ") or ln.startswith("component = ")
            ]
            assert anchors, f"{target} has no anchor line to check"
            # Either the code reached the lane, or the author withheld it with
            # `:code: false` and the document SAYS SO. What is not acceptable
            # is silence, which is the defect this whole file exists for.
            withheld = "source withheld" in doc and target.name in doc
            assert anchors[0] in doc or withheld, (
                f"{url} carries neither {target.name}'s code nor a withheld "
                f"marker for it — mechanism 4"
            )
            checked += 1
    assert checked >= 3, f"only {checked} exec directives walked; the sweep found nothing"


def test_the_exec_pin_goes_red_when_the_expansion_is_disabled(app_module, monkeypatch):
    """THE MUTATION CHECK. A lane pin that cannot fail certifies whatever is
    there — which is how every fork in this round shipped the defect under a
    green suite."""
    import pages.markdown as md

    monkeypatch.setattr(md, "_EXEC_DIRECTIVE", __import__("re").compile(r"^(?!x)x$"))
    out = md._expand_source_directives(UNPAIRED)
    assert _needle() not in out, (
        "disabling the expansion changed nothing — the pin above is vacuous"
    )
