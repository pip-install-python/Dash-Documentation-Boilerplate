from pathlib import Path

import frontmatter
import dash_mantine_components as dmc
from dash import register_page
from markdown2dash import Admonition, Divider, Image, create_parser

from lib.directives.headings import patch_renderer

from lib.constants import OG_IMAGE_URL, PAGE_TITLE_PREFIX, SITE_DESCRIPTION
from lib.versions import substitute_versions

register_page(
    __name__,
    "/",
    title=PAGE_TITLE_PREFIX + "Home",
    # Dash emits `description`, `og:description` and `twitter:description` for
    # every page from this argument, and emits them EMPTY when it is missing —
    # which is what the home page, the most-linked page on the site, was doing.
    description=SITE_DESCRIPTION,
    # The most-shared page on the site. See lib.constants.OG_IMAGE_URL for why
    # this is explicit rather than inferred from assets/.
    image_url=OG_IMAGE_URL,
)

directory = "docs"

# read the home page markdown
md_file = Path("pages") / "home.md"

post = frontmatter.loads(md_file.read_text())
metadata, content = post.metadata, post.content

# Same {{VERSION:<distribution>}} substitution pages/markdown.py applies to
# the docs: home.md says "Powered by dash-improve-my-llms <version>" on the
# most-read surface in the network (/llms.txt), so the number must come from
# the installed package, never from prose — "Powered by 2.3.4" shipped for
# months while a newer package was actually serving the site.
content = substitute_versions(content, source=str(md_file))

# Module-level LLMS_DOC — dash-improve-my-llms picks this up automatically
# and serves it as the opening prose of /llms.txt. No layout walking, no
# extraction.
LLMS_DOC = content

layout = dmc.Container(
    # Page-unique id: keeps React's keyed reconciliation of page swaps atomic
    # (see the wrapper comment in pages/markdown.py).
    id="m2d-page-home",
    size="lg",
    py="xl",
    # markdown2dash, not dcc.Markdown (the fleet's no-`dcc` rule, 1.6.38):
    # the same renderer the docs pages use, so home and docs share one
    # typography and one set of DMC components.
    #
    # parse(content) returns a LIST. If you compose a hero around it, SPLAT
    # or CONCATENATE (`[hero, *parsed]` / `[hero] + parsed`) — a list nested
    # inside a children list renders the page EMPTY with a green suite
    # (React #31; modelviewer, 2026-08-30; tests/test_layout_nesting.py).
    children=(patch_renderer(), create_parser([Admonition(), Divider(), Image()])(content))[1],
)
