"""No page imports a component library inside its layout.

Note 141, owner-reported on the hub from the dev server 2026-09-09.
`pages/home.py::_network_map()` did `import dash_flows` INSIDE the layout
builder. On a fresh process the page-routing callback rendered that layout,
dash_flows registered its components mid-callback, Dash's guard raised
`ImportedInsideCallbackError` and refused the response — `_pages_content`
came back empty and the page was BLANK. The second request found the library
already imported and worked, which is why it survived as long as the map did:
it only ever fails on the first render after a restart, and a restart is
exactly what a deploy is.

Measured across the fleet before the rider was written: no fork lazily
imports a component library in a page today. So this is a REGRESSION test,
and the shape it guards is one nobody would catch by eye — the failure needs
a cold process, and every warm one passes.

A FRESH INTERPRETER is the whole method. Inside pytest the libraries are
already imported by the time any test runs, so the registry cannot grow and
the check would pass on a tree that has the defect.
"""
from __future__ import annotations

import json
import subprocess
import sys

import pytest

from conftest import REPO_ROOT

_RENDER = """
import json, sys, os
sys.path.insert(0, os.getcwd())
import importlib
importlib.import_module("run")
import dash
from dash.development.base_component import ComponentRegistry

{plant}

before = set(ComponentRegistry.registry)
rendered, failed = 0, []
for entry in list(dash.page_registry.values()):
    layout = entry.get("layout")
    try:
        if callable(layout):
            layout()
        rendered += 1
    except Exception as exc:          # a layout that cannot render is its
        failed.append(f"{{entry.get('module')}}: {{type(exc).__name__}}")
after = set(ComponentRegistry.registry)
print("@@RESULT@@" + json.dumps({{
    "grew": sorted(after - before), "rendered": rendered, "failed": failed,
    "before": sorted(before),
}}))
"""

_PLANT = """
def _lazy_layout():
    import {library}          # THE DEFECT: a component library, inside a layout
    return "planted"

dash.register_page("pages.planted_lazy", path="/planted-lazy",
                   name="Planted Lazy", layout=_lazy_layout)
"""


def _run(plant: str = "") -> dict:
    proc = subprocess.run(
        [sys.executable, "-c", _RENDER.format(plant=plant)],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=300,
    )
    marker = [line for line in proc.stdout.splitlines()
              if line.startswith("@@RESULT@@")]
    assert marker, (
        f"the probe interpreter produced no result — exit {proc.returncode}\n"
        f"stderr tail: {proc.stderr[-1500:]}"
    )
    return json.loads(marker[0][len("@@RESULT@@"):])


@pytest.fixture(scope="module")
def baseline() -> dict:
    return _run()


def test_rendering_every_layout_registers_no_new_component_library(baseline):
    """The regression. A library that registers DURING a render is one that
    would have raised ImportedInsideCallbackError on the real first request.
    """
    assert baseline["grew"] == [], (
        f"{baseline['grew']} registered while rendering layouts — a component "
        "library is imported inside a layout function, and the first render "
        "after every restart will be blank"
    )


def test_the_probe_actually_rendered_something(baseline):
    """Note 88. A probe that rendered nothing cannot observe growth, and its
    empty delta is indistinguishable from a clean tree."""
    assert baseline["rendered"] >= 5, baseline
    assert baseline["failed"] == [], (
        f"layouts that could not render: {baseline['failed']} — they were "
        "not covered by the assertion above"
    )
    assert "dash_mantine_components" in baseline["before"], baseline["before"]


def test_a_layout_that_lazily_imports_a_library_fails_it():
    """The rider's positive control: without it, a green above could mean the
    harness cannot see growth at all.

    Uses a REAL component library that this app does not import, so the
    control exercises the same machinery as the defect rather than a mock.
    """
    import importlib.util

    candidates = ("dash_ag_grid", "dash_bootstrap_components",
                  "dash_clerk_auth", "dash_table")
    library = next((name for name in candidates
                    if importlib.util.find_spec(name) is not None), None)
    if library is None:
        pytest.skip(
            "no component library is installed that this app does not "
            "already import, so the control cannot plant the defect — the "
            "regression test above is UNVERIFIED on this leg (candidates: "
            f"{', '.join(candidates)})"
        )

    planted = _run(plant=_PLANT.format(library=library))
    assert library in planted["grew"], (
        f"planting a lazy `import {library}` did not grow the registry — the "
        "probe cannot see the defect it exists to catch"
    )
