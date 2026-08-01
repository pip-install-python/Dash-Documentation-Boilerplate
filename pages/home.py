from pathlib import Path

import frontmatter
import dash_mantine_components as dmc
from dash import dcc, register_page

from lib.constants import OG_IMAGE_URL, PAGE_TITLE_PREFIX, SITE_DESCRIPTION

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

# Module-level LLMS_DOC — dash-improve-my-llms 2.0 picks this up automatically
# and serves it verbatim at /llms.txt. No layout walking, no extraction.
LLMS_DOC = content

layout = dmc.Container(
    # Page-unique id: keeps React's keyed reconciliation of page swaps atomic
    # (see the wrapper comment in pages/markdown.py).
    id="m2d-page-home",
    size="lg",
    py="xl",
    children=[
        dcc.Markdown(
            content,
            style={
                "maxWidth": "none",  # Allow Container to control width
            }
        )
    ]
)
