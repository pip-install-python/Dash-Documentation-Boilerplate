import os

import dash_mantine_components as dmc
from dash.development.base_component import Component
from dash_iconify import DashIconify
from markdown2dash import SourceCode


class SC(SourceCode):
    NAME = "source"

    def render(self, renderer, title: str, content: str, **options) -> Component:
        defaultExpanded = options.pop("defaultExpanded", "false")
        withExpandedButton = options.pop("withExpandedButton", "true")

        mapping = {
            "py": {"language": "python", "icon": DashIconify(icon="devicon:python")},
            "css": {"language": "css", "icon": DashIconify(icon="devicon:css3")},
        }
        files = title.split(", ")
        code = []
        for file in files:
            extension = file.split(".")[-1]
            # `with`, not `open(...).read()`: this runs per directive render,
            # so the leaked descriptors accumulate for as long as the process
            # lives and are only reclaimed when GC gets to them. That is also
            # why the ResourceWarning it raised was intermittent.
            with open(file, "r") as handle:
                source = handle.read()
            code.append(
                {
                    "fileName": os.path.basename(file),
                    "code": source,
                    "language": mapping[extension]["language"],
                    "icon": mapping[extension]["icon"],
                }
            )
        return dmc.CodeHighlightTabs(
            code=code,
            defaultExpanded=defaultExpanded == "true",
            withExpandButton=withExpandedButton == "true",
            # The copy button is icon-only; without these it has no
            # accessible name (the audit's "copy button without text").
            copyLabel="Copy code",
            copiedLabel="Copied",
        )
