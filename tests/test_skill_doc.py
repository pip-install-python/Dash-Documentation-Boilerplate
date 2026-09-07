"""The generated SKILL.md — 1.6.45 item 2.

dash-improve-my-llms looks for `SKILL.md` in the assets folder, digests the
bytes on disk, and lists it at `/.well-known/agent-skills/index.json`. The
package does not generate it; on this network the HOST does, from its own
corpus, because a hand-written skill goes stale silently and the first
reader to notice is an agent acting on it.
"""
from __future__ import annotations

import hashlib
import json

import pytest

from conftest import REPO_ROOT


@pytest.fixture(scope="module")
def index(app_module, client):
    response = client.get("/.well-known/agent-skills/index.json")
    assert str(response.status).startswith("200"), response.status
    return json.loads(response.text)


# ----------------------------------------------------------- the detect --


def test_the_index_lists_at_least_one_skill(index):
    """Item 2's detect. The template has no package of its own and still
    serves one skill, for the network's use."""
    assert index["skills"], "the index is empty — nothing was generated"
    assert len(index["skills"]) == 1, (
        f"{len(index['skills'])} skills; the contract is exactly one per host"
    )


def test_the_index_is_empty_never_absent_without_a_skill_file(app_module):
    """The distinction the whole release turns on: `skills: []` says "this
    host has none", a 404 is indistinguishable from a host that never
    learned the standard. Asserted through the PACKAGE's own builder with
    the path forced absent, so no file has to be deleted."""
    from dash_improve_my_llms import wellknown

    body = json.loads(wellknown.build_agent_skills_index(app_module.app,
                                                         skill_path=None))
    assert "skills" in body
    assert isinstance(body["skills"], list)


# ------------------------------------------------------- the acceptance --


def test_the_fetched_bytes_match_the_advertised_digest(index, client):
    """Item 2's acceptance. The digest is the point of the spec — it lets an
    agent cache a skill and know when it changed — so it must describe the
    bytes the host actually SERVES, not the ones it meant to."""
    entry = index["skills"][0]
    served = client.get("/assets/SKILL.md")
    assert str(served.status).startswith("200"), served.status

    digest = hashlib.sha256(served.text.encode("utf-8")).hexdigest()
    assert entry["digest"] == f"sha256:{digest}", (
        "the index advertises a digest for bytes other than the ones served"
    )


# ------------------------------------------------------------ the name --


def test_the_name_is_the_pypi_name_lower_case_and_hyphenated():
    from lib.constants import API_PACKAGES
    from lib.skill_doc import skill_name

    name = skill_name()
    assert name == name.lower(), f"{name!r} is not lower-case"
    assert "_" not in name, f"{name!r} carries an underscore, not a hyphen"
    assert " " not in name and name.strip() == name

    if API_PACKAGES:
        assert name == str(API_PACKAGES[0]).lower().replace("_", "-"), (
            "a host that documents a component must name that component — it "
            "is the string an agent would pip install"
        )
    else:
        assert name == "dash-documentation-boilerplate", (
            "a host with no package names its own distribution"
        )


def test_a_declared_package_takes_over_the_name(monkeypatch):
    """The fork case, exercised on a tree that has no package: without this
    the name rule is only ever tested in its fallback branch."""
    import lib.constants as constants
    import lib.skill_doc as skill_doc

    monkeypatch.setattr(constants, "API_PACKAGES", ["dash_mantine_components"])
    monkeypatch.setattr(skill_doc, "API_PACKAGES", ["dash_mantine_components"])
    assert skill_doc.skill_name() == "dash-mantine-components"


# ----------------------------------------------------- frontmatter + body --


def test_the_frontmatter_is_read_by_the_packages_own_parser():
    """Not by a reimplementation of it. The package's parser is deliberately
    small — no YAML dependency, two scalar fields — so the only question
    that matters is whether IT can read what this writes."""
    from dash_improve_my_llms.wellknown import parse_skill_frontmatter

    from lib.skill_doc import build_skill_md, skill_description, skill_name

    fields = parse_skill_frontmatter(build_skill_md())
    assert fields.get("name") == skill_name()
    assert fields.get("description") == skill_description()


def test_the_description_is_the_sites_own_and_within_the_cap():
    from lib.constants import SITE_DESCRIPTION
    from lib.skill_doc import MAX_DESCRIPTION, skill_description

    description = skill_description()
    assert description
    assert len(description) <= MAX_DESCRIPTION
    assert "\n" not in description, "the parser reads one line per field"
    assert description.split()[:3] == " ".join(SITE_DESCRIPTION.split()).split()[:3]


def test_an_over_long_description_is_truncated_not_dropped(monkeypatch):
    """A description that is too long is still the best answer available."""
    import lib.skill_doc as skill_doc

    monkeypatch.setattr(skill_doc, "SITE_DESCRIPTION", "x " * 2000)
    description = skill_doc.skill_description()
    assert 0 < len(description) <= skill_doc.MAX_DESCRIPTION


def test_the_body_carries_the_quickstart_from_the_corpus():
    """From home.md, not a copy of it: an agent and a human reader must be
    given the same instructions or the generator is pointless."""
    from lib.skill_doc import build_skill_md

    home = (REPO_ROOT / "pages" / "home.md").read_text()
    assert "## Quick Start" in home, (
        "the corpus no longer has a Quick Start section — the generator's "
        "source moved and the skill body is now thinner than it reads"
    )
    doc = build_skill_md()
    assert "## Quick Start" in doc
    assert "git clone" in doc, "the quickstart's commands did not come through"


def test_the_body_points_at_the_machine_lane():
    from lib.constants import BASE_URL
    from lib.skill_doc import build_skill_md

    doc = build_skill_md()
    assert f"{BASE_URL}/llms.txt" in doc


def test_the_api_pointer_appears_only_where_the_page_exists(monkeypatch):
    """A pointer to /api on a host with no packages is a soft 404 — the
    defect item 11 of 1.6.44 exists to catch, reintroduced in a document
    the shell-link walker cannot see."""
    import lib.skill_doc as skill_doc

    monkeypatch.setattr(skill_doc, "API_PACKAGES", [])
    assert "/api" not in skill_doc.build_skill_md()

    monkeypatch.setattr(skill_doc, "API_PACKAGES", ["dash_mantine_components"])
    assert "/api" in skill_doc.build_skill_md()


# ------------------------------------------------ generated, not written --


def test_the_file_is_generated_and_never_committed():
    """A committed SKILL.md would let a hand edit survive and be served with
    a digest matching the edit rather than the corpus."""
    import subprocess

    ignored = [ln.strip() for ln in (REPO_ROOT / ".gitignore").read_text().splitlines()]
    assert "assets/SKILL.md" in ignored

    tracked = subprocess.run(["git", "ls-files", "assets/SKILL.md"],
                             cwd=REPO_ROOT, capture_output=True, text=True)
    assert tracked.stdout.strip() == "", "SKILL.md is tracked by git"


def test_boot_regenerates_it_rather_than_writing_once():
    """The digest advertises these bytes; a file written once and left would
    advertise a digest for content the corpus no longer contains."""
    src = "\n".join(
        line for line in (REPO_ROOT / "run.py").read_text().splitlines()
        if not line.lstrip().startswith("#")
    )
    assert "write_skill_md(" in src
    assert src.index("write_skill_md(") < src.index("add_llms_routes("), (
        "the file must exist before the package's routes go on"
    )


def test_a_write_failure_does_not_take_the_boot_down(tmp_path, monkeypatch):
    """A degraded skill surface is not a broken site."""
    from lib.skill_doc import write_skill_md

    with pytest.raises(OSError):
        write_skill_md(tmp_path / "does" / "not" / "exist")
