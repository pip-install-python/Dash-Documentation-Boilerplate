"""One fleet Python — image, matrix and render.yaml must agree.

Found by the ops seat reading the tree, not a report (2026-08-25): the
Dockerfile said `python:3.11.8-slim` — a PATCH pin, so the image never
received a 3.11.x security release — while the CI matrix said 3.12 and
render.yaml said 3.12.0. Three declared Pythons, the docker boot/battery
testing an interpreter the matrix never ran, and nothing on the wire able to
contradict any of them. These pins hold every encoding to ONE minor, sourced
from the Dockerfile's FROM tag; /healthz's `python` field plus the
`python_matches_declared` battery check (scripts/network_smoke.py) hold the
serving host to the same one.

What is deliberately NOT here: no comparison of the RUNNING interpreter to
the fleet minor — the suite legitimately runs on the adjacent window legs
(the matrix's 3.13/3.12 rows), where that assertion would be false by
design. Image-vs-declaration is the battery's job, against a host.

Session-class for forks, not block cargo: it presumes a Dockerfile and a
render.yaml, which not every fork carries — the sync spec's conditional
item covers adoption.
"""
from __future__ import annotations

import re

from conftest import REPO_ROOT


def _fleet_minor() -> str:
    """The single source: the Dockerfile's FROM tag."""
    for line in (REPO_ROOT / "Dockerfile").read_text(encoding="utf-8").splitlines():
        m = re.match(r"FROM\s+python:(\S+)", line)
        if m:
            return m.group(1)
    raise AssertionError("Dockerfile has no `FROM python:` line")


def _uncommented(path) -> list[str]:
    return [
        ln for ln in (REPO_ROOT / path).read_text(encoding="utf-8").splitlines()
        if not ln.lstrip().startswith("#")
    ]


def test_dockerfile_tag_is_minor_only():
    """The patch pin IS the security bug: `3.11.8-slim` never receives a
    3.11.x fix release. The minor tag tracks them through Docker Hub."""
    tag = _fleet_minor()
    assert re.fullmatch(r"\d+\.\d+-slim", tag), (
        f"Dockerfile FROM tag is {tag!r} — must be a MINOR tag "
        "(python:X.Y-slim), never a patch pin"
    )


def test_render_yaml_agrees_with_the_image():
    """Render's PYTHON_VERSION takes a full X.Y.Z (its encoding, not ours) —
    the MINOR must be the fleet Python. The patch there needs a human bump
    now and then; the minor drifting is the class this file exists for."""
    minor = _fleet_minor().removesuffix("-slim")
    lines = _uncommented("render.yaml")
    value = None
    for i, ln in enumerate(lines):
        if re.match(r"\s*- key: PYTHON_VERSION$", ln):
            m = re.search(r'value:\s*"([^"]+)"', lines[i + 1])
            value = m and m.group(1)
            break
    assert value, "render.yaml declares no PYTHON_VERSION"
    assert re.fullmatch(r"\d+\.\d+\.\d+", value), (
        f"PYTHON_VERSION {value!r} — Render requires full X.Y.Z"
    )
    assert value.startswith(minor + "."), (
        f"render.yaml PYTHON_VERSION {value} vs image python:{minor}-slim — "
        "the native-runtime lane and the image lane disagree"
    )


def test_ci_matrix_main_and_singleton_jobs_agree_with_the_image():
    minor = _fleet_minor().removesuffix("-slim")
    ci = _uncommented(".github/workflows/ci.yml")

    mains = [m.group(1) for ln in ci
             if (m := re.match(r'\s*python:\s*\["([\d.]+)"\]', ln))]
    assert mains == [minor], (
        f"ci.yml matrix main {mains} vs image python:{minor}-slim"
    )

    # lint and pip-audit run literal python-version pins; the test job's is
    # `${{ matrix.python }}` and is deliberately not a literal.
    literals = [m.group(1) for ln in ci
                if (m := re.match(r'\s*python-version:\s*"([\d.]+)"', ln))]
    assert literals and set(literals) == {minor}, (
        f"ci.yml singleton jobs pin {literals}, image is python:{minor}-slim"
    )

    cd = _uncommented(".github/workflows/cd.yml")
    cd_literals = [m.group(1) for ln in cd
                   if (m := re.match(r'\s*python-version:\s*"([\d.]+)"', ln))]
    assert cd_literals and set(cd_literals) == {minor}, (
        f"cd.yml verify job pins {cd_literals}, image is python:{minor}-slim"
    )


def test_matrix_legs_are_the_adjacent_minors():
    """The compat window stays three wide: the two include legs on the
    default backend are X.Y-1 and X.Y-2 (or X.Y+1 once it exists). The
    dash-bottom rows pin their own python and are exempt — they vary the
    dash axis, not the python axis."""
    major, y = (int(p) for p in _fleet_minor().removesuffix("-slim").split("."))
    allowed = {f"{major}.{y}", f"{major}.{y - 1}", f"{major}.{y - 2}",
               f"{major}.{y + 1}"}
    ci = _uncommented(".github/workflows/ci.yml")
    legs = [m.group(1) for ln in ci
            if (m := re.match(r'\s*- python:\s*"([\d.]+)"', ln))]
    assert legs, "the matrix has no include legs — the window collapsed to one"
    outside = [leg for leg in legs if leg not in allowed]
    assert not outside, (
        f"matrix legs {outside} fall outside the three-wide window around "
        f"{major}.{y}"
    )
