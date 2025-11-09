import importlib
import inspect
from markdown2dash.src.directives.kwargs import Kwargs as KwargsBase

def convert_docstring_to_dict(docstring):
    """Convert numpy style parameter docstring to a list of dicts with keys name, type, description"""

    lines: list[str] = docstring.split("----------\n")[-1].split("\n")

    params = []
    new_param = None
    for line in lines:
        if not line.startswith("    "):
            if new_param is not None:
                params.append(new_param)
            name, type = line.split(": ", 1)
            new_param = {"name": name, "type": type, "description": ""}
        else:
            new_param["description"] += " " + line.strip()
    params.append(new_param)

    return params

class Kwargs(KwargsBase):

    def hook(self, md, state):
        sections = []

        for tok in state.tokens:
            if tok["type"] == self.block_name:
                sections.append(tok)

        for section in sections:
            attrs = section["attrs"]

            # Parse the component specification (e.g., "dmc.Button" or "html.Div")
            component_spec = attrs["title"]

            # Common package name mappings
            package_map = {
                "dmc": "dash_mantine_components",
                "html": "dash.html",
                "dcc": "dash.dcc",
                "dash": "dash"
            }

            # Try to parse package.Component format
            if "." in component_spec:
                package_abbr, component_name = component_spec.rsplit(".", 1)
                package = package_map.get(package_abbr, package_abbr)
            else:
                # If no package specified, use default or library attribute
                package = attrs.pop("library", "dash_mantine_components")
                component_name = component_spec

            try:
                imported = importlib.import_module(package)
                component = getattr(imported, component_name)
                docstring = inspect.getdoc(component)

                if docstring and "----------" in docstring:
                    docstring = docstring.split("----------\n")[-1]
                    attrs["kwargs"] = convert_docstring_to_dict(docstring)
                else:
                    # If no proper docstring, use component's __init__ signature
                    attrs["kwargs"] = []
            except (ModuleNotFoundError, AttributeError, Exception) as e:
                # If import fails, just skip kwargs generation
                attrs["kwargs"] = []