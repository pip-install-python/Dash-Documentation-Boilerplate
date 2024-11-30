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
            package = attrs.pop("library", "dash_pydantic_form")
            component_name = attrs["title"]
            imported = importlib.import_module(package)
            component = getattr(imported, component_name)
            docstring = inspect.getdoc(component).split("----------\n")[-1]
            attrs["kwargs"] = convert_docstring_to_dict(docstring)