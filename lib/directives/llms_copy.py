import textwrap
import dash_mantine_components as dmc
from dash import html
from dash.development.base_component import Component
from markdown2dash import BaseDirective
from lib.constants import NAME_CONTENT_MAP, APP_VERSION


class LlmsCopy(BaseDirective):
    """
    Directive to add an LLM copy button at the top of documentation pages.

    Usage in markdown:
        .. llms_copy::Page Title

    This creates a button that copies the page content formatted for LLM consumption.
    """
    NAME = "llms_copy"

    def render(self, renderer, title: str, content: str, **options) -> Component:
        """
        Render the LLM copy buttons component.

        Args:
            renderer: The markdown renderer
            title: The page title (unused in URL mode)
            content: The directive content (unused)
            **options: Additional options (unused)

        Returns:
            A Dash component with copy buttons and tooltips
        """
        # Create unique ID for buttons (sanitize title for ID)
        safe_title = title.lower().replace(" ", "-").replace("/", "-")
        llms_button_id = f"llm-copy-button-{safe_title}"
        toon_button_id = f"llms-toon-button-{safe_title}"
        json_button_id = f"page-json-button-{safe_title}"

        # LLM Copy button (llms.txt)
        llms_button = dmc.Tooltip(
            dmc.Button(
                "Copy for llm 📋",
                id=llms_button_id,
                variant="subtle",
                color="gray",
                size="compact-sm",
                className="llms-copy-button",  # Add class for JS to find
            ),
            label="Copy llms.txt URL for AI assistants",
            position="top",
            withArrow=True
        )

        # TOON button (llms.toon - token-optimized)
        toon_button = dmc.Tooltip(
            dmc.Button(
                "llms.toon 🎯",
                id=toon_button_id,
                variant="subtle",
                color="gray",
                size="compact-sm",
                className="llms-toon-button",  # Add class for JS to find
            ),
            label="Copy llms.toon URL (40-50% fewer tokens)",
            position="top",
            withArrow=True
        )

        # Page JSON button
        json_button = dmc.Tooltip(
            dmc.Button(
                "page.json 📄",
                id=json_button_id,
                variant="subtle",
                color="gray",
                size="compact-sm",
                className="page-json-button",  # Add class for JS to find
            ),
            label="View page structure as JSON",
            position="top",
            withArrow=True
        )

        # Group buttons together
        component = dmc.Group(
            [llms_button, toon_button, json_button],
            gap="xs"
        )

        return dmc.Box(component, c="dimmed", my="sm")

