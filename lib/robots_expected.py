"""What robots.txt this app GENERATES — the app's own side of item 19.

The battery compares this against what the world is served. Keeping it in
`lib/` rather than inline in the script is the point: the script may run
against a host whose checkout it does not have, and in that case the
comparison must SKIP rather than invent one side of itself.

Generated from the same `RobotsConfig` the app registers, through the same
package function that serves it — not from a second opinion about what the
config ought to produce. A reimplementation here would compare the edge
against this file's beliefs instead of against the app.
"""
from __future__ import annotations


def generated_text() -> str:
    """The robots.txt body this app produces, in process.

    Called with the app's own `_robots_config` and this host's own base URL,
    through the package's `generate_robots_txt` — the same function that
    answers the route. Anything else would be comparing the edge against a
    guess about the app rather than against the app.
    """
    import run  # noqa: F401 — importing wires the config onto the app

    from dash_improve_my_llms.robots_generator import generate_robots_txt

    from lib.constants import BASE_URL

    config = getattr(run.app, "_robots_config", None)
    if config is None:
        raise RuntimeError("this app registers no RobotsConfig")
    return generate_robots_txt(
        config,
        sitemap_url=f"{BASE_URL}/sitemap.xml",
        base_url=BASE_URL,
    )


def expected_directives() -> list:
    """`[(name, value), ...]` lower-cased, comments stripped.

    The comparison unit is a DIRECTIVE, not a line: whitespace and comment
    differences between the app's output and the edge's copy are not
    findings, and an injected `Disallow: /` is.
    """
    out = []
    for line in generated_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if line and ":" in line:
            name, _, value = line.partition(":")
            out.append((name.strip().lower(), value.strip()))
    return out
