"""The footer — identical on every host (1.6.38).

© {this year} Pip Install Python LLC · GitHub PROFILE · Discord · YouTube.
The repository link is the top bar's icon, the single Changelog link is
the sidebar's (owner, 2026-08-30). Every icon carries an accessible name;
the year is computed.

The Terms and Privacy links arrived at 1.6.44 (item 15) and LEFT AGAIN at
1.6.45 — owner's design word, 2026-09-07, from checking the satellites on a
phone: "I noticed the terms and privacy links were placed in the footer.
I'd like to move those links to the sidebar and not the footer — it makes
the footer a bit too crowded." At mobile width the row
"© 2026 … · Terms · Privacy" collided with the GitHub/Discord/YouTube
icons. The pages did not move: item 15 already registers them in the
sidebar's `Legal` group (last in CATEGORY_ORDER, and so visible in the
mobile drawer), which makes the footer anchors a DUPLICATE of a
navigation entry that already exists — the footer was carrying them
twice over.

So the footer is the copyright line and the icons, and nothing else. The
older rule it replaced still stands underneath: no link here to a page
that is not registered. pipdocs advertised /terms and /privacy from every
page in the fleet while neither existed, and nothing caught it because
Dash answers 200 for any path — the shell renders and the client router
finds nothing. `tests/test_shell_links_resolve.py` (1.6.44 item 11) holds
every internal link in this shell against `dash.page_registry`, so that
ordering rule is enforced rather than remembered.
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
                    dmc.Text(f"© {datetime.now().year} {PUBLISHER}",
                             size="sm", c="dimmed"),
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
