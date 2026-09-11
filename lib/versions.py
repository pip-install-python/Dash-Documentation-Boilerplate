"""Version claims are derived from the installed packages, never written.

Prose that states a package version writes ``{{VERSION:<distribution>}}``
— the name exactly as it appears on PyPI and in ``pip install`` — and the
markdown loaders substitute the version of whatever is actually installed.
The served documents are the network's point of truth, and a hardcoded
number is a lie waiting for the next release: "Powered by 2.3.4" shipped
on /llms.txt for months while 2.5.1 was serving the site.

The general form exists so every satellite forked from this template can
make the same claim about the package IT documents ("dash-mui-charts
{{VERSION:dash-mui-charts}}") without touching loader code — bump the
package, redeploy, and the browser page, the copy button, /llms.txt and
every /<page>/llms.txt publish the new number together.

Fenced code blocks and inline code spans are left verbatim: a code example
*showing* the placeholder syntax (docs/network-standard does) must render
the syntax, not the substituted number.

A placeholder naming a distribution that is not installed raises at load
time. Both loaders run at import, so a typo fails the boot (and therefore
CI) instead of leaking ``{{VERSION:...}}`` into served prose — the same
loud-over-silent choice the identity tests make.

ONE EXCEPTION, and it is the host's OWN package (note 133, excalidraw
17c9dd2). A component fork documents a package that is imported from the
TREE, never installed: CI installs requirements.txt and the image does
`COPY . .`, neither of which runs `pip install .`. So `{{VERSION:dash-
excalidraw}}` on the fork that IS dash-excalidraw raised LookupError
during app construction and took the whole site down — every test red,
the boot step red — while the fork's own venv, which happened to have the
distribution installed, was green. Dash component packages carry
`__version__` statically (from package-info.json), so when the named
distribution is one this host DOCUMENTS (`API_PACKAGES`) and no
distribution is installed, the version is read from the imported module
instead. Every other name keeps the LookupError: the fallback must not
turn a typo into a silent pass.
"""
from __future__ import annotations

import re
from importlib.metadata import PackageNotFoundError, version

_PLACEHOLDER = re.compile(r"\{\{VERSION:([A-Za-z0-9._-]+)\}\}")

# The first placeholder, from before the general form existed (the 2026-08-14
# truth sweep). Satellites forked in that window may still write it.
_LEGACY = "{{DIMLL_VERSION}}"
_LEGACY_DIST = "dash-improve-my-llms"

_FENCE = re.compile(r"^\s*(```|~~~)")
# Inline code spans, shortest match — `code`. CommonMark lets a span cross a
# soft line break, so newlines are allowed inside. Split with a capture group
# so the spans survive into the output untouched.
_CODE_SPAN = re.compile(r"(`[^`]+`)")


def _own_package_modules() -> list:
    """The module names this host documents, read at CALL time.

    A fork edits `API_PACKAGES`; reading it here rather than binding it at
    import keeps the fallback keyed on the host's real declaration.
    """
    try:
        from lib.constants import API_PACKAGES

        return [str(name) for name in API_PACKAGES if name]
    except Exception:
        return []


def version_from_tree(dist: str) -> str | None:
    """`dist`'s version read from the IMPORTED module, or None.

    Only for a distribution this host documents — see the module docstring.
    `dash-excalidraw` the distribution is `dash_excalidraw` the module.
    """
    wanted = dist.replace("-", "_")
    if wanted not in _own_package_modules():
        return None
    try:
        import importlib

        return getattr(importlib.import_module(wanted), "__version__", None)
    except Exception:
        return None


def version_of(dist: str) -> str | None:
    """The installed version, else the tree's for this host's own package.

    The ONE resolver: the markdown substituter below, the header's version
    badge and the landing page's install line all read it, so they cannot
    disagree about what this host runs.
    """
    try:
        return version(dist)
    except PackageNotFoundError:
        return version_from_tree(dist)


def _substitute_prose(text: str, source: str) -> str:
    def replace(match: re.Match) -> str:
        dist = match.group(1)
        resolved = version_of(dist)
        if resolved:
            return resolved
        if dist.replace("-", "_") in _own_package_modules():
            raise LookupError(
                f"{source} claims a version for {dist!r}, which this host "
                "documents, but the distribution is not installed AND the "
                "module carries no __version__ — a Dash component package "
                "should carry one from package-info.json."
            ) from None
        raise LookupError(
            f"{source} claims a version for {dist!r}, but that "
            "distribution is not installed — the claim cannot be true. "
            "Fix the {{VERSION:...}} name or install the package."
        ) from None

    out = []
    for part in _CODE_SPAN.split(text):
        if part.startswith("`"):
            out.append(part)
            continue
        part = part.replace(_LEGACY, f"{{{{VERSION:{_LEGACY_DIST}}}}}")
        out.append(_PLACEHOLDER.sub(replace, part))
    return "".join(out)


def substitute_versions(content: str, *, source: str = "<markdown>") -> str:
    """Replace every version placeholder in ``content`` (outside code) with
    the installed distribution's version. ``source`` names the file in the
    error message."""
    out = []
    prose: list[str] = []
    in_fence = False

    def flush():
        if prose:
            out.append(_substitute_prose("".join(prose), source))
            prose.clear()

    for line in content.splitlines(keepends=True):
        if _FENCE.match(line):
            flush()
            in_fence = not in_fence
            out.append(line)
        elif in_fence:
            out.append(line)
        else:
            prose.append(line)
    flush()
    return "".join(out)
