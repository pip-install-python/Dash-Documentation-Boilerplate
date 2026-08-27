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

TWO Pythons can live in one ci.yml, and this file pins only one of them
(1.6.28 — filed independently by flows and clerkhook): the SITE lane —
the jobs that install the site's requirements file and boot/serve the
docs app — is held to the image's minor. A PACKAGE matrix (a wheel's
`requires-python` claim, e.g. 3.9–3.13) is the package's business and
out of scope; pinning it to a container base would fail the moment the
image moved.

JOB-SCOPED, not file-scoped (1.6.30, emojimart's shape). Until this
release the paragraph above was true only in the docstring: the greps
below read the whole file, so the first fork with a package matrix
failed on a lane this file explicitly disclaims. The lanes are now
declared by NAME — `SITE_LANE_JOBS` and `PACKAGE_LANE_JOBS` — the pins
read site-lane job bodies only, and a job that declares a Python and
sits in neither set fails `test_every_job_declaring_a_python_is_classified`
loudly. Silence there would be the worse failure: an unclassified job is
a Python nobody is holding to anything.

A fork adapts THREE things and nothing else: the two job-name sets, and
`SITE_PYTHON_FLOOR` (its own supported floor, cross-checked against its
README below).

Session-class for forks, not block cargo: it presumes a Dockerfile and a
render.yaml, which not every fork carries — the sync spec's conditional
item covers adoption.
"""
from __future__ import annotations

import re

from conftest import REPO_ROOT

CI = ".github/workflows/ci.yml"
CD = ".github/workflows/cd.yml"

# The SITE lane: jobs that install this site's requirements and boot/serve
# the docs app. Every python they declare is held to the image's minor.
SITE_LANE_JOBS = {
    CI: frozenset({"lint", "test", "docker", "pip-audit"}),
    CD: frozenset({"test", "deploy", "verify"}),
}

# The PACKAGE lane: jobs testing a wheel's own `requires-python` window.
# EMPTY in the template — it ships no package — and that is a statement,
# not an omission: a fork that publishes a component from this same repo
# names its wheel jobs here, and this file then stops reading them.
PACKAGE_LANE_JOBS = {
    CI: frozenset(),
    CD: frozenset(),
}

# The oldest Python this SITE supports, independent of the fleet minor it
# runs in production. The matrix may keep a leg here even when it is far
# below the fleet Python — emojimart holds 3.10 because python-frontmatter
# needs typing.TypeGuard — and the README is where the promise is made, so
# the two are pinned together below. None = no floor below the fleet minor.
SITE_PYTHON_FLOOR: str | None = "3.12"


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


def _jobs(path) -> dict[str, list[str]]:
    """`jobs:` split into name -> its lines, by indentation.

    Hand-parsed on purpose: this suite installs the SITE's requirements and
    PyYAML is not among them. Only the structure matters here — the top-level
    `jobs:` mapping, and its two-space keys.
    """
    jobs: dict[str, list[str]] = {}
    inside = False
    current: str | None = None
    for ln in _uncommented(path):
        if re.match(r"^jobs:\s*$", ln):
            inside = True
            continue
        if not inside:
            continue
        if ln.strip() and not ln.startswith(" "):
            break  # a later top-level key — `jobs:` is over
        m = re.match(r"^  ([A-Za-z0-9_-]+):\s*$", ln)
        if m:
            current = m.group(1)
            jobs[current] = []
            continue
        if current is not None:
            jobs[current].append(ln)
    assert jobs, f"{path}: no `jobs:` mapping parsed"
    return jobs


def _declared_pythons(lines) -> list[str]:
    """Every LITERAL python minor a job's lines declare.

    `${{ matrix.python }}` is not a literal and not a declaration — the
    matrix rows it reads are.
    """
    found = []
    for ln in lines:
        for pattern in (
            r'^\s*python:\s*\["([\d.]+)"\]',   # matrix main
            r'^\s*- python:\s*"([\d.]+)"',     # an include leg
            r'^\s*python-version:\s*"([\d.]+)"',  # a singleton job's pin
        ):
            m = re.match(pattern, ln)
            if m:
                found.append(m.group(1))
    return found


def _site_lane_lines(path) -> list[str]:
    jobs = _jobs(path)
    known = SITE_LANE_JOBS[path]
    missing = sorted(known - set(jobs))
    assert not missing, (
        f"{path}: SITE_LANE_JOBS names {missing}, which no longer exist — a "
        "renamed job silently drops out of every pin below. Update the set."
    )
    return [ln for name in sorted(known) for ln in jobs[name]]


def test_every_job_declaring_a_python_is_classified():
    """The guard on the guard (1.6.30).

    Scoping the pins to the site lane means an unlisted job is simply not
    read — which is the right behaviour for a package matrix and the wrong
    one for a job somebody forgot to classify. This test is the difference:
    every job that declares a python literal must be in exactly one lane.
    """
    for path in (CI, CD):
        classified = SITE_LANE_JOBS[path] | PACKAGE_LANE_JOBS[path]
        overlap = SITE_LANE_JOBS[path] & PACKAGE_LANE_JOBS[path]
        assert not overlap, (
            f"{path}: {sorted(overlap)} classified as BOTH lanes — a job "
            "serves one Python's purpose or the other"
        )
        for name, lines in _jobs(path).items():
            pythons = _declared_pythons(lines)
            if not pythons:
                continue
            assert name in classified, (
                f"{path} job {name!r} declares Python {sorted(set(pythons))} "
                "and belongs to neither SITE_LANE_JOBS nor "
                "PACKAGE_LANE_JOBS. Classify it: a site-lane job is held to "
                "the image's minor, a package-lane job is the wheel's "
                "business and deliberately unread. An unclassified job is a "
                "Python nobody holds to anything."
            )


def test_the_declared_floor_is_the_one_the_readme_promises():
    """SITE_PYTHON_FLOOR is a promise made in public — hold the two together.

    The floor widens the matrix window below (a leg at the floor is legal
    however far it sits under the fleet minor), so a floor invented here and
    nowhere else would widen it on nothing. Patterns that do not match
    contribute nothing — a fork states its floor in its own words — but at
    least one declaration must exist.
    """
    if SITE_PYTHON_FLOOR is None:
        return
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    found = {
        value
        for pattern in (
            r"Python-(\d+\.\d+)\+-blue",              # the shields badge
            r"\*\*Python (\d+\.\d+)\+\*\*",           # the feature list
            r"(\d+\.\d+) or higher",                  # the requirements prose
            r"\|\s*Python\s*\|\s*(\d+\.\d+)\+\s*\|",  # the compatibility table
        )
        for value in re.findall(pattern, readme)
    }
    assert found, (
        f"SITE_PYTHON_FLOOR is {SITE_PYTHON_FLOOR!r} but README.md states no "
        "floor at all — the promise has to be somewhere a reader can find it"
    )
    assert found == {SITE_PYTHON_FLOOR}, (
        f"README.md promises Python {sorted(found)}, this file's floor is "
        f"{SITE_PYTHON_FLOOR!r} — one of the two is stale"
    )


def test_dockerfile_tag_is_minor_only():
    """The patch pin IS the security bug: `3.11.8-slim` never receives a
    3.11.x fix release. The minor tag tracks them through Docker Hub."""
    tag = _fleet_minor()
    assert re.fullmatch(r"\d+\.\d+-slim", tag), (
        f"Dockerfile FROM tag is {tag!r} — must be a MINOR tag "
        "(python:X.Y-slim), never a patch pin"
    )


def test_render_yaml_agrees_with_the_image():
    """BRANCHES on the service runtime (1.6.28 — filed independently by
    three forks in the batch-2/3 round; the template is the reference
    implementation for BOTH branches, not just its own service type).

    `runtime: python` — the native runtime reads PYTHON_VERSION and
    requires a full X.Y.Z (its encoding, not ours): the value is
    REQUIRED and its MINOR must be the fleet Python. THE PIN COMPARES
    THE MINOR, deliberately (restated 1.6.30 after muicharts): Render
    RESOLVES the patch itself — a service asking for 3.14.7 was served
    3.14.3 — so a patch-level assertion here would fail against a
    platform doing exactly what it documents. The patch needs a human
    bump now and then; the minor drifting is the class this file exists
    for, and `python_matches_declared` on the wire is what holds the
    running interpreter to it.

    `runtime: docker` — NOTHING reads PYTHON_VERSION; the image is the
    interpreter. The key must be ABSENT: a value there reads like the
    platform's setting and can never be true — the item's own defect
    class (a declaration nothing holds to reality) arriving through the
    fix. If the runtime ever changes, this test flips branches by
    itself.

    Anything else fails loudly: extend the branch deliberately, never
    by accident."""
    minor = _fleet_minor().removesuffix("-slim")
    runtime = _render_runtime()
    lines = _uncommented("render.yaml")
    value = None
    for i, ln in enumerate(lines):
        if re.match(r"\s*- key: PYTHON_VERSION$", ln):
            m = re.search(r'value:\s*"([^"]+)"', lines[i + 1])
            value = m and m.group(1)
            break
    if runtime == "docker":
        assert value is None, (
            f"render.yaml declares PYTHON_VERSION {value!r} on a docker "
            "runtime — nothing reads it there; a string that looks like "
            "the platform's setting and can never be true is the drift "
            "class this file exists to kill. Delete the key."
        )
        return
    assert runtime == "python", (
        f"render.yaml runtime is {runtime!r} — this test knows `python` "
        "and `docker`; extend the branch deliberately"
    )
    assert value, "render.yaml declares no PYTHON_VERSION"
    assert re.fullmatch(r"\d+\.\d+\.\d+", value), (
        f"PYTHON_VERSION {value!r} — Render requires full X.Y.Z"
    )
    assert value.startswith(minor + "."), (
        f"render.yaml PYTHON_VERSION {value} vs image python:{minor}-slim — "
        "the native-runtime lane and the image lane disagree"
    )


def _render_runtime() -> str:
    for ln in _uncommented("render.yaml"):
        m = re.match(r"\s*runtime:\s*(\S+)", ln)
        if m:
            return m.group(1)
    raise AssertionError("render.yaml declares no `runtime:`")


def test_ci_matrix_main_and_singleton_jobs_agree_with_the_image():
    """SITE-lane jobs only (see the module docstring). Reads the bodies of
    the jobs named in SITE_LANE_JOBS, never the whole file — a package
    matrix elsewhere in the same ci.yml is out of scope by construction,
    not by hope."""
    minor = _fleet_minor().removesuffix("-slim")
    ci = _site_lane_lines(CI)

    mains = [m.group(1) for ln in ci
             if (m := re.match(r'\s*python:\s*\["([\d.]+)"\]', ln))]
    assert mains == [minor], (
        f"ci.yml site-lane matrix main {mains} vs image python:{minor}-slim"
    )

    # lint and pip-audit run literal python-version pins; the test job's is
    # `${{ matrix.python }}` and is deliberately not a literal.
    literals = [m.group(1) for ln in ci
                if (m := re.match(r'\s*python-version:\s*"([\d.]+)"', ln))]
    assert literals and set(literals) == {minor}, (
        f"ci.yml site-lane singleton jobs pin {literals}, image is "
        f"python:{minor}-slim"
    )

    cd = _site_lane_lines(CD)
    cd_literals = [m.group(1) for ln in cd
                   if (m := re.match(r'\s*python-version:\s*"([\d.]+)"', ln))]
    assert cd_literals and set(cd_literals) == {minor}, (
        f"cd.yml site-lane jobs pin {cd_literals}, image is "
        f"python:{minor}-slim"
    )


def test_matrix_legs_are_within_the_window():
    """The window (corrected 1.6.30): the fleet minor, ONE adjacent minor,
    and the site's declared floor where it is lower.

    The old rule demanded a contiguous three-wide window, which reads as a
    quota and is wrong in both directions. emojimart keeps a 3.10 leg —
    python-frontmatter needs typing.TypeGuard, so 3.10 is genuinely its
    floor, four minors under the fleet Python; muicharts narrowed to
    3.13/3.12 by choice. Both are right: breadth is a CEILING here, never a
    requirement, and the floor is a promise the README makes (pinned above).

    The dash-bottom rows pin their own python and ride a window leg — they
    vary the dash axis, not the python axis, so they need no exemption as
    long as the leg they sit on is inside the window.
    """
    major, y = (int(p) for p in _fleet_minor().removesuffix("-slim").split("."))
    allowed = {f"{major}.{y}", f"{major}.{y - 1}", f"{major}.{y + 1}"}
    if SITE_PYTHON_FLOOR:
        floor_major, floor_y = (int(p) for p in SITE_PYTHON_FLOOR.split("."))
        if (floor_major, floor_y) < (major, y):
            allowed.add(SITE_PYTHON_FLOOR)

    legs = [m.group(1) for ln in _site_lane_lines(CI)
            if (m := re.match(r'\s*- python:\s*"([\d.]+)"', ln))]
    assert legs, "the matrix has no include legs — the window collapsed to one"

    outside = sorted({leg for leg in legs if leg not in allowed})
    assert not outside, (
        f"site-lane matrix legs {outside} are outside the window "
        f"{sorted(allowed)}: the fleet minor {major}.{y}, one adjacent "
        f"minor, and the declared floor ({SITE_PYTHON_FLOOR or 'none'})"
    )

    if SITE_PYTHON_FLOOR:
        below = sorted({
            leg for leg in legs
            if tuple(int(p) for p in leg.split(".")) <
            tuple(int(p) for p in SITE_PYTHON_FLOOR.split("."))
        })
        assert not below, (
            f"site-lane matrix legs {below} run below the declared floor "
            f"{SITE_PYTHON_FLOOR} — either the README promises too much or "
            "the leg tests a Python this site does not support"
        )
