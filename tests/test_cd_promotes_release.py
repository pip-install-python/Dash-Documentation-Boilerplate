"""CD promotes main → release on a green matrix; nothing else writes release.

The road since 1.6.35 (owner decision A, 2026-08-29): Render auto-deploys
the `release` branch and ONLY cd.yml's `deploy` job writes it, as a
fast-forward push of the run's own sha after the CI matrix is green. The
measurement behind it: 14:12Z that day, de0bcff pushed to main; Render,
watching main, built it within the minute; its CD run went red at 14:13Z
with the deploy job skipped; /healthz served the red build for ~6 minutes.
CI cannot stop a deploy while the platform watches the branch CI is still
judging.

These pins hold the STRUCTURE — the part a fork can drift silently:
`deploy` still needs `test`; the promote step exists and is not a force
push; the write grant is on that one job, not the workflow; the hook
step is gone; render.yaml watches `release`.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
CD = REPO / ".github" / "workflows" / "cd.yml"
RENDER = REPO / "render.yaml"


def _cd() -> dict:
    return yaml.safe_load(CD.read_text())


def _deploy() -> dict:
    return _cd()["jobs"]["deploy"]


def _promote_step() -> dict:
    steps = [s for s in _deploy()["steps"] if s.get("name") == "Promote to release"]
    assert len(steps) == 1, "cd.yml deploy job must have exactly one 'Promote to release' step"
    return steps[0]


def test_release_is_only_written_after_a_green_matrix():
    """needs: [test] is the whole gate — a red matrix never reaches the push."""
    assert "test" in _deploy()["needs"]
    assert _cd()["jobs"]["test"]["uses"].endswith("ci.yml")


def test_the_promote_step_is_a_fast_forward_push_of_this_sha():
    # Commands only — the step's comments explain why NOT to force.
    run = "\n".join(
        line for line in _promote_step()["run"].splitlines()
        if not line.lstrip().startswith("#")
    )
    assert re.search(r"git push origin\s+\"?HEAD:refs/heads/release\"?", run), run
    assert "--force" not in run and " -f " not in run and "+HEAD" not in run, (
        "a non-fast-forward push must FAIL the job — someone wrote release "
        "by hand — never be forced over"
    )


def test_a_verify_only_dispatch_does_not_promote():
    cond = _promote_step().get("if", "")
    assert "inputs.target_url == ''" in cond and "github.event_name == 'push'" in cond, cond


def test_the_write_grant_is_on_the_deploy_job_only():
    assert _deploy()["permissions"] == {"contents": "write"}
    assert _cd()["permissions"] == {"contents": "read"}, (
        "the workflow-level grant stays read; only the promote job writes"
    )
    for name, job in _cd()["jobs"].items():
        if name != "deploy":
            assert job.get("permissions", {}).get("contents") != "write", name


def test_the_deploy_hook_is_gone():
    """Sync item 13's detect, from the inside: the secret's name must not
    appear anywhere in the file, comments included."""
    assert "RENDER_DEPLOY_HOOK" + "_URL" not in CD.read_text()
    assert not any("hook" in (s.get("id") or "") for s in _deploy()["steps"])


def test_render_watches_release():
    doc = yaml.safe_load(RENDER.read_text())
    web = [s for s in doc["services"] if s.get("type") == "web"]
    assert web and all(s.get("branch") == "release" for s in web), (
        "render.yaml must deploy `release` — main is where CI judges, "
        "release is what it certified"
    )
    # autoDeploy stays unset (Render default: on) — it IS the mechanism.
    assert all("autoDeploy" not in s or s["autoDeploy"] is True for s in web)


def test_the_posture_fence_declares_the_road():
    text = (REPO / "DIVERGENCES.md").read_text()
    fence = re.search(r"^```yaml posture[ \t]*\n(.*?)^```", text, re.M | re.S).group(1)
    assert re.search(r"^deploy:\s*release-branch\s*$", fence, re.M), fence
