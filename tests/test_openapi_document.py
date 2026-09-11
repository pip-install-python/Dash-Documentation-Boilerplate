"""Every FastAPI handler's annotations resolve, and the document renders.

Note 143, muischeduler's /openapi.json 500. `lib/clerk_webhook.py` carried
`from __future__ import annotations`, so its handler's `request: Request`
became the STRING "Request", which FastAPI resolves from MODULE globals —
and `Request` was imported inside the registering function, so pydantic met
an unresolved ForwardRef and ONE undescribable route of 21 poisoned the
WHOLE document.

Why it hid: /docs and /redoc answered 200 because they are shells that fetch
the document in the browser, so every status sweep saw green. The identity
knobs that document was meant to title had never once been visible.

THE CHECK IS RUNTIME RESOLUTION, NOT A SOURCE SCAN, and note 143 paid for
that lesson: the seat's AST checker reported the hub EXPOSED because it
counted an import inside a module-level `try:` block as a local import. An
import inside a module-level try IS module-level. `typing.get_type_hints`
asks the only question that matters — can this handler's annotations be
resolved — and cannot be fooled by where the import is written.
"""
from __future__ import annotations

import typing

import pytest

from conftest import backend as _resolve_backend


def _walk_routes(routes, depth=0):
    """Every leaf route, through FastAPI's nested routers.

    `_IncludedRouter` exposes no `.routes`; the real router is on
    `.original_router`. A flat walk finds three anonymous containers and
    none of the routes inside them.
    """
    for route in routes:
        inner = getattr(route, "original_router", None)
        children = (getattr(inner, "routes", None) if inner is not None
                    else getattr(route, "routes", None))
        if children and depth < 6:
            yield from _walk_routes(children, depth + 1)
        else:
            yield route


@pytest.fixture
def asgi_app(app_module):
    backend = _resolve_backend()
    if backend != "fastapi":
        pytest.skip(
            f"this leg runs backend={backend!r}, which serves no OpenAPI "
            "document at all — the handler sweep and the document render are "
            "UNCOVERED here and are asserted on the fastapi leg"
        )
    pytest.importorskip("starlette")
    return app_module.app.server


def _handlers(server):
    from starlette.testclient import TestClient

    with TestClient(server):          # lifespan: Dash's routes register here
        return [(str(getattr(r, "path", "?")), r.endpoint)
                for r in _walk_routes(server.routes)
                if getattr(r, "endpoint", None) is not None]


def test_every_handlers_annotations_resolve(asgi_app):
    """The class, not the one file: any handler whose hints cannot resolve
    is a route that would poison the whole document."""
    handlers = _handlers(asgi_app)
    assert len(handlers) >= 10, (
        f"only {len(handlers)} handler(s) found — the walk is not reaching "
        "the routers, and a clean sweep of almost nothing is not a result"
    )
    broken = []
    for path, endpoint in handlers:
        try:
            typing.get_type_hints(endpoint)
        except Exception as exc:
            broken.append(f"{path}: {type(exc).__name__}: {exc}")
    assert broken == [], (
        f"{len(broken)} of {len(handlers)} handlers have annotations that do "
        f"not resolve — each one poisons /openapi.json entirely: {broken}"
    )


def test_the_openapi_document_actually_renders(asgi_app):
    """The definitive check. /docs and /redoc answering 200 proves nothing —
    they are shells that fetch this in the browser."""
    document = asgi_app.openapi()
    assert document and document.get("paths"), document
    assert len(document["paths"]) >= 5, document["paths"].keys()


def test_the_sweep_catches_an_unresolvable_annotation(asgi_app):
    """Positive control. Without it, a green above could mean the sweep
    resolves nothing at all.

    Reproduces note 143 exactly: PEP 563 semantics (a STRING annotation)
    naming a type that is not in the handler's module globals — which is
    what `from __future__ import annotations` plus a locally imported
    `Request` produces.
    """
    def handler(request: "RequestNotInGlobals"):   # noqa: F821
        return None

    with pytest.raises(Exception):
        typing.get_type_hints(handler)

    # and the sweep's own predicate, on the same function
    broken = []
    try:
        typing.get_type_hints(handler)
    except Exception as exc:
        broken.append(f"/planted: {type(exc).__name__}: {exc}")
    assert broken, "the sweep's predicate does not flag the planted handler"


def test_agent_key_still_refuses_pep_563(app_module):
    """Source pin. `lib/agent_key.py` documents that it deliberately omits
    `from __future__ import annotations` — there the consequence was a silent
    422 on every call rather than a 500 on the document. A later tidy-up that
    adds the line to every module would reintroduce it."""
    import ast
    import pathlib

    path = (pathlib.Path(__file__).resolve().parent.parent
            / "lib" / "agent_key.py")
    source = path.read_text()

    # PARSE, do not grep. The first version of this assertion used
    # `"from __future__ import annotations" not in source` and went RED on a
    # correct file: that module's DOCSTRING contains the sentence "No ``from
    # __future__ import annotations`` here, deliberately", so the grep
    # matched the prose describing the absence. It is the kit's own trap —
    # a file-scoped grep matching a comment ABOUT the defect it hunts — and
    # it fired on the very test written to guard against that family.
    futures = [node for node in ast.parse(source).body
               if isinstance(node, ast.ImportFrom) and node.module == "__future__"]
    imported = sorted(alias.name for node in futures for alias in node.names)
    assert "annotations" not in imported, (
        f"lib/agent_key.py now really imports {imported} from __future__ — "
        "its own docstring explains why it must not: the handler's "
        "`request: Request` becomes a string FastAPI cannot resolve, and the "
        "parameter silently becomes a required query field"
    )
    assert "PEP 563" in source, (
        "the comment explaining the omission is gone — the next person to "
        "tidy imports has nothing to read"
    )
