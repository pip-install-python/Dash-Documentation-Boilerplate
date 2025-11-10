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
        Render the LLM copy button component.

        Args:
            renderer: The markdown renderer
            title: The page title (unused in URL mode)
            content: The directive content (unused)
            **options: Additional options (unused)

        Returns:
            A Dash component with copy button and tooltip
        """
        # Create unique ID for this button (sanitize title for ID)
        safe_title = title.lower().replace(" ", "-").replace("/", "-")
        button_id = f"llm-copy-button-{safe_title}"

        component = dmc.Tooltip(
            dmc.Button(
                "Copy for llm 📋",
                id=button_id,
                variant="subtle",
                color="gray",
                size="compact-sm",
                className="llms-copy-button",  # Add class for JS to find
            ),
            label="Copy llms.txt URL for AI assistants",
            position="right",
            withArrow=True
        )

        return dmc.Box(component, c="dimmed", my="sm")

