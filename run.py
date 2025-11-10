import dash
from dash import Dash, _dash_renderer
import json
from flask import jsonify
from components.appshell import create_appshell
import dash_mantine_components as dmc

# AI/LLM Integration & SEO
from dash_improve_my_llms import add_llms_routes, RobotsConfig, register_page_metadata

_dash_renderer._set_react_version("18.2.0")

stylesheets = [
    dmc.styles.ALL
]

scripts = [
    "https://cdnjs.cloudflare.com/ajax/libs/dayjs/1.10.8/dayjs.min.js",
    "https://unpkg.com/hotkeys-js/dist/hotkeys.min.js",
]

app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    use_pages=True,
    external_scripts=scripts,
    external_stylesheets=stylesheets,
    update_title=None,
    prevent_initial_callbacks=True,
    index_string=open('templates/index.html').read()  # Add this line
)

# ============================================================================
# AI/LLM & SEO Configuration
# ============================================================================

# Set base URL for SEO (change to your production URL)
app._base_url = "https://your-app-url.com"  # Update this!

# Configure bot management policies
app._robots_config = RobotsConfig(
    block_ai_training=True,      # Block GPTBot, CCBot, anthropic-ai, etc.
    allow_ai_search=True,         # Allow ChatGPT-User, ClaudeBot, PerplexityBot
    allow_traditional=True,       # Allow Googlebot, Bingbot, etc.
    crawl_delay=10,               # 10 second delay between bot requests
    disallowed_paths=[],          # Add paths to block (e.g., ["/admin", "/api/*"])
)

# Add LLMS routes - enables llms.txt, page.json, architecture.txt, robots.txt, sitemap.xml
add_llms_routes(app)

# Register metadata for home page (improves SEO and AI understanding)
register_page_metadata(
    path="/",
    name="Dash Documentation Boilerplate",
    description="A modern, responsive documentation system for Dash applications built with Dash Mantine Components"
)

# ============================================================================

app.layout = create_appshell(dash.page_registry.values())

server = app.server


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port='8559')