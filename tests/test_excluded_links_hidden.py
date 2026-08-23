"""excluded_links must hide from BOTH audiences — the llms-2plot-dev footgun.

Before 1.6.8, a path in ``components/navbar.excluded_links`` disappeared
from the sidebar while staying in sitemap.xml, /llms.txt, the tier corpora,
MCP and the prerender. On the first real fork that mattered:
llms-2plot-dev "hid" the template's tutorial pages and kept publishing
them to every crawler as its own documentation — duplicate content
competing with the site it forked from, invisible from a browser.

The navbar now marks every excluded path hidden through dimll at import
time. This suite pins the parity from both ends: the mechanism (every
excluded path is in dimll's hidden state) and the surfaces (nothing
excluded appears in the sitemap or /llms.txt, while a control page does —
so an empty sitemap can never pass this vacuously).
"""

from __future__ import annotations


def test_every_excluded_path_is_machine_hidden(app):
    from components.navbar import excluded_links
    from dash_improve_my_llms import is_hidden

    not_hidden = [p for p in excluded_links if not is_hidden(p)]
    assert not_hidden == [], (
        f"excluded from the sidebar but NOT from the machine surfaces: "
        f"{not_hidden} — the navbar's mark_hidden wiring is broken or was "
        "removed; these paths would publish to every crawler while looking "
        "hidden from a browser."
    )


def test_excluded_paths_absent_from_sitemap_and_llms(client):
    from components.navbar import excluded_links

    sitemap = client.get("/sitemap.xml").text
    llms = client.get("/llms.txt").text

    leaked = []
    for path in excluded_links:
        if f"{path}</loc>" in sitemap:
            leaked.append(f"{path} in sitemap.xml")
        if f"{path})" in llms or f"{path}/llms.txt" in llms:
            leaked.append(f"{path} in /llms.txt")
    assert leaked == [], f"sidebar-hidden pages published to machines: {leaked}"

    # Positive control: a real page IS listed, so an empty sitemap or a
    # broken llms.txt cannot make the assertions above pass vacuously.
    assert "/getting-started</loc>" in sitemap
    assert "/getting-started" in llms
