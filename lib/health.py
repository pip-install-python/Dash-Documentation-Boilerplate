"""
``/healthz`` liveness probe for the Flask and Quart backends.

The 2plot.ai hub sweeps every satellite's ``/healthz`` once an hour and records
up/down + latency — that's the "Satellite health & reach" panel on ``/traffic``
(the traffic rollup this app POSTs supplies the other half). The FastAPI build
declares a typed ``/healthz`` in ``lib/asgi_routes`` so it shows up in Swagger,
but it renders from the SAME ``health_payload`` below — one payload builder on
every backend, so the probe contract doesn't depend on which backend a
deployment happens to run.

Keep it cheap: the hub measures the round trip, so any work done here is
reported back as this app being slow.
"""
from __future__ import annotations

import json
import mmap
import os
import platform
import re
from pathlib import Path

import dash


def _resolved_country(headers=None) -> str:
    """``geo.explain_resolution`` over THIS request's headers, or a reason.

    Reads the request headers directly rather than anything the package
    threads through, so it answers "did the country header reach this app
    at all?" independently of how the enforcement seam is wired.

    Each route passes its own framework's headers explicitly — the first
    version read Flask's request context, which made the FastAPI and Quart
    lanes answer "no request context" forever: pannellum's production
    healthz (FastAPI) was the host that showed it, first wave of the
    ≥2.7.1 floor round. ``normalize_headers`` accepts Flask/Starlette/
    Quart/dict and never raises. The Flask-context fallback stays for
    callers that pass nothing.
    """
    try:
        from dash_improve_my_llms import geo
        from dash_improve_my_llms._headers import normalize_headers
    except Exception:
        return "unavailable (pre-2.7.0 package)"

    try:
        if headers is not None:
            return geo.explain_resolution(normalize_headers(headers))

        from flask import has_request_context, request

        if not has_request_context():
            return "no request context"
        return geo.explain_resolution(normalize_headers(request.headers))
    except Exception:
        return "unavailable"


def _llms_version() -> dict:
    """`{"llms_version": "2.10.0"}`, or `{}` if the package cannot be read.

    Omitted rather than reported as "unknown": a health payload that
    invents a version is worse than one that is silent about it, and the
    boot floor in run.py already refuses to start below the floor — so an
    absent key here means the import broke after boot, which is itself the
    finding.
    """
    try:
        import dash_improve_my_llms as _pkg

        version = getattr(_pkg, "__version__", None)
        return {"llms_version": version} if version else {}
    except Exception:
        return {}


# The two tables the ledger holds. Named rather than discovered so a future
# key cannot be counted as a visit by accident.
_LEDGER_TABLES = ("visits", "reads")

# Above this, the streaming counter is worth its complexity; below it, a
# plain parse is faster than a scan and far easier to be sure of. 2 MB is
# ~7k rows on this tree's row size — comfortably past the point where a
# full parse is noticeable on a 30-second HEALTHCHECK, and far below the
# 135 MB the 45-day window reaches at 10k reads/day.
_FULL_PARSE_CEILING = 2 * 1024 * 1024

# A row opening inside a top-level array, at `json.dump(..., indent=2)`'s
# second level. A literal, deliberately: an alternation that also matched
# table headers ran 17x slower (436 ms against 26 ms) because its first
# branch made the engine attempt a match at every quote in the file.
#
# An empty array ("reads": []) contains no row openings, which yields the
# correct 0 rather than a missing key — the line-based first version lost
# exactly that case.
_ROW_OPENING = re.compile(rb"\n    \{")


def _count_rows_by_parsing(path) -> dict:
    """The obvious way, kept for small files and as the fallback."""
    data = json.loads(path.read_text())
    if not isinstance(data, dict):
        return {}
    return {t: len(data[t]) for t in _LEDGER_TABLES
            if isinstance(data.get(t), list)}


def _count_rows_by_streaming(path) -> dict:
    """Count each table's rows WITHOUT building them (1.6.45 item 7).

    The block used to `json.loads` the whole ledger on every probe — 12.8 ms
    at 5.76 MB, and ~0.3 s at the ~135 MB a 45-day window reaches once
    `reads` stopped being capped by count (1.6.44 item 21), against a
    HEALTHCHECK that runs every 30 seconds. The fix is to count, not to
    shorten the window: the window is a retention decision, and this was a
    performance problem wearing its clothes.

    The tracker writes with `json.dump(..., indent=2)`, so every row inside a
    top-level array begins on its own line at exactly four spaces. Locating
    each table and counting that marker with `str.count` does the work in C
    — no per-line Python loop (the first version iterated lines and was
    barely faster than parsing) and no object allocation.

    Returns {} when the shape is not the one it knows, and the caller falls
    back to a real parse. A counter that GUESSED on an unfamiliar file would
    be worse than the parse it replaced: these numbers are read by people
    deciding whether a disk is filling.
    """
    # MEMORY-MAPPED, and the five attempts are recorded because four of
    # them were slower than they looked. Measured on the acceptance fixture
    # (39.2 MB, 200,000 rows), best of three, budget 50 ms:
    #
    #   read_text + str.count             66 ms  the UTF-8 decode dominates
    #   read_bytes + bytes.count          40 ms  the 39 MB copy dominates
    #   mmap, find each table, count      51 ms  `find` for the LATER table
    #                                            rescans everything before it
    #                                            (22 ms of the 51)
    #   mmap, ONE combined alternation   436 ms  catastrophically worse: the
    #                                            `"([a-z_]+)": \[` branch makes
    #                                            the engine attempt a match at
    #                                            every quote in the file
    #   mmap, bounded find then rfind     this   ~28 ms
    #
    # The component timings are what made the last one obvious: `find` for
    # the later table cost 22 ms while all the row counting cost 23 ms. A key
    # near the START is cheap to `find`; a key near the END is cheap to
    # `rfind`. So look in the first megabyte, and fall back to a backward
    # search — correct wherever the key actually is, fast at both ends.
    _HEAD = 1 << 20
    counts = {}
    with open(path, "rb") as handle:
        with mmap.mmap(handle.fileno(), 0, access=mmap.ACCESS_READ) as mapped:
            starts = {}
            for table in _LEDGER_TABLES:
                key = b'"' + table.encode() + b'": ['
                index = mapped.find(key, 0, _HEAD)
                if index < 0:
                    index = mapped.rfind(key)
                if index >= 0:
                    starts[table] = index
            # An absent table is ABSENT, not zero — that is what tells the
            # caller this file is a shape we do not know, so it can fall back
            # to a real parse instead of reporting confident nonsense.
            if not starts:
                return {}

            ordered = sorted(starts.items(), key=lambda kv: kv[1])
            for position, (table, begin) in enumerate(ordered):
                end_at = (ordered[position + 1][1]
                          if position + 1 < len(ordered) else len(mapped))
                counts[table] = sum(1 for _ in _ROW_OPENING.finditer(
                    mapped, begin, end_at))
    return counts


def _count_rows(path) -> dict:
    """Row counts for the ledger's tables, streamed on a large file.

    Correctness first: a small file is parsed, and a large one is streamed
    and falls back to a parse if the scan does not recognise the shape.
    """
    try:
        size = path.stat().st_size
    except OSError:
        return {}
    if size <= _FULL_PARSE_CEILING:
        return _count_rows_by_parsing(path)
    counts = _count_rows_by_streaming(path)
    return counts if counts else _count_rows_by_parsing(path)


def _ledger_block() -> dict:
    """`{"path", "persistent", "visits", "reads"}` — the ledger, from outside.

    1.6.44 item 20 (note 93; excalidraw's shape and name). Three facts that
    were previously invisible on the wire:

    `persistent` is MEASURED, never declared. It is true iff the resolved
    path lies OUTSIDE the repository root — i.e. on a mounted disk such as
    `/var/data/...`. A path under the app tree is the container filesystem
    and reads false EVEN WHERE A BLUEPRINT DECLARES A DISK: leaflet ran for
    weeks with a declared disk and no disk, and nothing on the wire could
    contradict the declaration. A boolean that reports the deployment's
    intention is worth nothing; this one reports the filesystem.

    `visits` and `reads` are the two tables' current row counts, read from
    the same file the tracker writes. A missing file is `0` and `0` — never
    an error, and /healthz stays 200: this block is a diagnostic, and a
    diagnostic that can take the health probe down with it is a liability.

    Row CONTENTS never appear here. Counts, a boolean and a path.
    """
    block = {"path": None, "persistent": False, "visits": 0, "reads": 0}
    try:
        from lib.analytics_tracker import analytics_path

        path = Path(analytics_path()).resolve()
        block["path"] = str(path)
        repo_root = Path(__file__).resolve().parent.parent
        try:
            path.relative_to(repo_root)
            block["persistent"] = False      # inside the tree: container fs
        except ValueError:
            block["persistent"] = True       # outside it: a mounted disk

        if path.exists():
            counts = _count_rows(path)
            block["visits"] = counts.get("visits", 0)
            block["reads"] = counts.get("reads", 0)
    except Exception:
        # Never let a diagnostic break the health probe. An unreadable or
        # half-written ledger reports zeros, and the `path` that is already
        # in the block is what a reader needs to go and look.
        pass
    return block


def _geo_headers_seen() -> list:
    """The visitor-location headers the tracker has seen this process.

    Read through the tracker rather than re-read here: one module decides
    what counts as a location header, and a health probe that kept its own
    list would drift from the one doing the recording.
    """
    try:
        from lib.analytics_tracker import geo_headers_seen

        return geo_headers_seen()
    except Exception:
        return []


def health_payload(backend: str, headers=None) -> dict:
    payload = {
        "ok": True,
        "backend": backend,
        "dash_version": dash.__version__,
        # The RESOLVED dash-improve-my-llms version (1.6.44 item 1's rider;
        # excalidraw's name and shape, adopted verbatim so the fleet never
        # carries two spellings of the same key). Additive: item 10's seven
        # keys stay and a RENAME is still the failure.
        #
        # It exists because the CI-vs-production gap was otherwise
        # SELF-REPORTED — no public surface on any host printed what the
        # package actually resolved to. excalidraw's first wire reading
        # proved the gap is real rather than theoretical: `llms_version`
        # 2.9.4 while its own suite ran 2.8.0, on a host with no floor bump,
        # because a `>=` floor cannot pull a new wheel through a cached
        # Docker layer. A field whose whole job is to be readable from
        # outside cannot be omitted on failure quietly, so it is omitted
        # only when the import itself fails — see below.
        **_llms_version(),
        # WHICH interpreter is actually serving. Before this field the repo
        # declared three different Pythons (Dockerfile 3.11.8, matrix 3.12,
        # render.yaml 3.12.0) and nothing on the wire could contradict any
        # of them — the drift was invisible to the battery by construction
        # (ops-seat finding, 2026-08-25). scripts/network_smoke.py asserts
        # this minor against the Dockerfile's FROM tag, so image and
        # declaration can no longer part ways silently.
        "python": platform.python_version(),
        # Where this host's ledger actually lives, whether it survives a
        # deploy, and how much is in it (1.6.44 item 20). Additive: item
        # 10's seven keys stay and a RENAME is still the failure.
        "ledger": _ledger_block(),
    }
    # Which commit the RUNNING instance was built from. This is what lets CD
    # verify the artifact it shipped rather than whichever build happens to
    # be serving: a Render service with a disk restarts with a blip instead
    # of overlapping instances, so a bare 200 proves nothing about WHICH
    # build answered (the muicharts finding, 2026-08-21 — its battery had
    # been verifying the previous release on every run, invisibly, until a
    # new surface made the race lose). Optional on purpose: omitted where
    # the platform variable does not exist, so the fleet's probe contract
    # is unchanged.
    build = os.environ.get("RENDER_GIT_COMMIT")
    if build:
        payload["build"] = build

    # WHICH satellite answered. `build` says which commit, this says which
    # app — and on a fleet where every host shares this template and a
    # hostname can be repointed between services (llms.2plot.dev was,
    # 2026-08-23), "is this the site I think it is?" is a different question
    # from "is this the build I shipped?". Cheap, and the hub's sweep gets
    # it for free.
    payload["app"] = os.environ.get("SATELLITE_APP_KEY") or "unknown"

    # The geo guardrail's LIVE state (dash-improve-my-llms >= 2.7.0). Added
    # after llms-2plot-dev's production verification could not answer "is
    # the denylist actually in force?" from outside: the control board and
    # the public policy showcase both showed countries denied while every
    # request was served 200, and the only surfaces that could settle it
    # (the boot log, the operator panel) need credentials a verification
    # pass does not have.
    #
    # Counts and flags only — never the denylist's country codes: a health
    # endpoint is not where anyone should learn policy. `resolved` reveals
    # only the caller's own country back to them, which Cloudflare's
    # /cdn-cgi/trace already does — and it is THE per-host check
    # docs/GEO.md calls mandatory before trusting a denylist. It also
    # localises a failure: geo can be configured with a full denylist and
    # still never match if the country header is not reaching the app —
    # "configured: true, denied: 7, resolved: unknown" says that in one
    # line.
    try:
        from dash_improve_my_llms import geo
    except ImportError:
        # Pre-2.7 package: the key is OMITTED, not error-flagged — a host on
        # an older floor is not broken, it just predates the diagnostic. The
        # fleet's >=2.7.1 floor round lights this up with no further change.
        pass
    else:
        try:
            payload["geo"] = {
                "configured": bool(geo.is_configured()),
                "denied": len(
                    geo.effective_policy().get("deny_countries") or []
                ),
                "resolved": _resolved_country(headers),
                # WHICH visitor-location headers this process has actually
                # received (1.6.44 item 16). Additive and list-shaped on
                # purpose: the Cloudflare "Add visitor location headers"
                # transform is an owner click PER ZONE, so the only honest
                # answer to "is it on for this host?" is the set of headers
                # that have turned up — and it grows as they do, rather than
                # being declared once and going stale. Empty on a host that
                # has served no request carrying one yet.
                "headers_seen": _geo_headers_seen(),
            }
        except Exception:  # never let a diagnostic break the health probe
            payload["geo"] = {"configured": False, "denied": 0,
                              "headers_seen": _geo_headers_seen(),
                              "error": True}

    return payload


def register_health_route(app, backend: str) -> None:
    """Mount ``/healthz`` on Flask/Quart. No-op on FastAPI (already typed)."""
    if backend == "fastapi":
        return

    server = app.server

    # Built PER REQUEST, not once at registration. It used to be a snapshot
    # closed over by the route — harmless while every field was static
    # (ok/backend/dash_version/build never change for a running process),
    # and silently wrong the moment one is not: on llms-2plot-dev the route
    # is registered ~150 lines before configure_geo runs, so a snapshot
    # reported the guardrail as unconfigured on a host where it is
    # configured — the diagnostic lying in exactly the situation it exists
    # for (found 2026-08-23, fixed fork-side first).
    if backend == "quart":
        from quart import jsonify, request

        @server.get("/healthz")
        async def _healthz():  # pragma: no cover — quart runtime
            return jsonify(health_payload(backend, headers=request.headers))
    else:
        from flask import jsonify, request

        @server.get("/healthz")
        def _healthz():
            return jsonify(health_payload(backend, headers=request.headers))

    print(f"[boilerplate] /healthz registered ({backend}) — "
          "the 2plot.ai hourly health sweep probes this path.")
