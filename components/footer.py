"""The footer — identical on every host (1.6.38).

© {this year} Pip Install Python LLC · GitHub PROFILE · Discord · YouTube.
The repository link is the top bar's icon, the single Changelog link is
the sidebar's (owner, 2026-08-30). Every icon carries an accessible name;
the year is computed.

The Terms and Privacy links arrived at 1.6.44 (item 15), when the pages
did. The old docstring said "no Terms/Privacy links until those pages
exist" and it was load-bearing: pipdocs advertised both from every page in
the fleet while neither was registered, and nothing caught it because Dash
answers 200 for any path — the shell renders and the client router finds
nothing. `tests/test_shell_links_resolve.py` (item 11) now holds every
internal link in this shell against `dash.page_registry`, so the ordering
rule is enforced rather than remembered.
"""
from datetime import datetime

import dash_mantine_components as dmc
from dash_iconify import DashIconify

from lib.constants import DISCORD_URL, GITHUB_PROFILE_URL, PUBLISHER, YOUTUBE_SUBSCRIBE_URL

FOOTER_HEIGHT = 56


def _icon_link(icon, href, label):
    return dmc.Anchor(
        dmc.ActionIcon(
            DashIconify(icon=icon, width=20),
            size="lg",
            variant="subtle",
            color="gray",
            **{"aria-label": label},
        ),
        href=href,
        target="_blank",
        **{"aria-label": label},
    )


def create_footer():
    return dmc.AppShellFooter(
        dmc.Container(
            dmc.Group(
                [
                    dmc.Group(
                        [
                            dmc.Text(f"© {datetime.now().year} {PUBLISHER}",
                                     size="sm", c="dimmed"),
                            dmc.Anchor("Terms", href="/terms", size="sm",
                                       c="dimmed"),
                            dmc.Anchor("Privacy", href="/privacy", size="sm",
                                       c="dimmed"),
                        ],
                        gap="md",
                        wrap="nowrap",
                    ),
                    dmc.Group(
                        [
                            _icon_link("radix-icons:github-logo", GITHUB_PROFILE_URL, "Pip Install Python on GitHub"),
                            _icon_link("ic:baseline-discord", DISCORD_URL, "Join the 2plot Discord"),
                            _icon_link("mdi:youtube", YOUTUBE_SUBSCRIBE_URL, "Subscribe on YouTube"),
                        ],
                        gap="sm",
                    ),
                ],
                justify="space-between",
                wrap="nowrap",
            ),
            fluid=True,
            px="md",
            h="100%",
            style={"display": "flex", "alignItems": "center"},
        ),
        h=FOOTER_HEIGHT,
        withBorder=True,
    )
