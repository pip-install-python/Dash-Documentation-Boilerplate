#!/usr/bin/env python3
"""Smoke battery for a 2plot satellite — CI container and production alike.

One script, two seats, the SAME named checks either way, so a failure in CI
and a failure against production read identically:

    CI container   python scripts/network_smoke.py --base-url http://localhost:8550
    Production     python scripts/network_smoke.py --base-url https://boilerplate.2plot.dev

Stdlib-only on purpose: CI runs it from the host against the booted container
with a bare `python3`, before anything is pip-installed.

This is a TEMPLATE FILE. Every satellite forked from this repo copies it
verbatim and changes only the block marked "per-site" below — the expected
H1, the port, the paths that must 404. Everything else is the network
standard; if a check here is wrong, it is wrong on twenty hosts.

What a satellite is to the network is what the battery proves: that it states
its identity, that its agent-facing document surfaces are real, that it runs
the intended dash-improve-my-llms artifact, and that no owner-only surface
leaks. A satellite holds no key material, so unlike the hub's copy of this
script there is no agent-key API to fail closed — the corresponding check
here is that this host's llms.txt points *back* at the hub that does.

Every UA this script sends carries the internal-traffic token (the analytics
point of truth — https://2plot.ai/docs/satellite-analytics, "Internal
traffic"): a battery must never register as a visitor or a "bot" in any
network ledger. Even the deliberately crawler-shaped probe appends the token
— the target still exercises its bot path, but its analytics know the caller
is machinery.

Exit code: 1 if any check fails, else 0.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TIMEOUT = 30
try:
    from lib.constants import PROBE_UA_SUFFIX as _PROBE
except Exception:  # running outside a repo checkout — keep the token intact
    _PROBE = "2plot-internal/probe"
# The default UA names the BROWSER lane first (1.6.40; muischeduler's
# finding on its item-12 port): at dash-improve-my-llms >= 2.8 a UA with
# no browser engine token is classified crawler-lane, so a bare internal
# token made every default-UA check read the prerendered crawler document
# — a manifest-link or og:image check goes red the moment a floor moves,
# in CD's verify job. The internal token stays IN the string, after the
# engine token: INTERNAL_UA_TOKEN is a substring match, so the far side's
# internal-traffic exclusion still holds. CRAWLER_UA is the other lane
# and is deliberately untouched.
BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 " + _PROBE
    + " network-smoke"
)
UA = BROWSER_UA
CRAWLER_UA = "Mozilla/5.0 (compatible; Googlebot/2.1) " + _PROBE

# The network's TEMPLATE host. This file is copied verbatim into every fork,
# so the constant is the same everywhere on purpose: it is what a fork
# compares ITSELF against, not its own identity (that is BASE_URL).
TEMPLATE_BASE_URL = "https://boilerplate.2plot.dev"


def _ssl_context() -> ssl.SSLContext:
    """Verify certificates via certifi when available.

    The same fix smoke_live.py and audit_links.py carry, arriving here late
    (1.6.30, muicharts): CI runs this battery against http://localhost, where
    TLS never comes up, so the omission was invisible for the CI seat — and
    Linux runners have an OS trust store anyway. A Mac running it against a
    production https host got CERTIFICATE_VERIFY_FAILED on every check, 0/12,
    which reads as "the site is down" rather than "this laptop has no CA
    bundle". Verification stays ON either way; certifi only supplies the
    bundle. Both live tools a CD run can certify with now carry it.
    """
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


SSL_CONTEXT = _ssl_context()

# The body dash-improve-my-llms serves when a page has no prose registered.
# Matched in full, deliberately: this app's own <noscript> block legitimately
# says "requires JavaScript", and a substring check on that phrase reports a
# perfectly healthy host as broken. (It did, the first time this ran.)
STUB_MARKER = "This page contains interactive content that requires JavaScript"

# ---------------------------------------------------------------- per-site --
# The three values a fork changes. Everything below this block is the network
# standard and is copied verbatim.

# This app's one identity (lib/constants.SITE_BRAND). tests/test_site_identity
# asserts every local surface carries it; this pins the DEPLOYED artifact to
# it, which is the half no unit test can reach.
SITE_H1 = "# Dash Documentation Boilerplate — the 2plot network's template"

# The container port. Matches the Dockerfile's EXPOSE and CMD.
DEFAULT_BASE_URL = "http://localhost:8550"

# Owner-only surfaces that must 404 their llms.txt to an anonymous reader.
# This template ships no hidden pages, so the list is a canary rather than a
# census: `/admin` is what a fork will add first, and `mark_hidden("/admin")`
# has to keep working. A fork adds its own paths here in the same change that
# marks them hidden.
# Every mark_hidden page's llms.txt must 404. Literals because this tool
# runs standalone against a live host with no app import — and PINNED
# against the registry by tests/test_nav_contract.py, so a page added,
# renamed or deleted moves this tuple in the same change (pannellum's
# carried a page deleted 08-02 and missed /admin/traffic; note 74).
HIDDEN_DOC_PATHS = (
    "/admin/control-board/llms.txt",
    "/admin/traffic/llms.txt",
)

# The hub one level up the chain. A satellite's llms.txt must name it — that
# is what lets an agent walk from any leaf to the network root.
HUB_URL = "https://2plot.dev"

# ---------------------------------------------------------------------------

PASS, FAIL, WARN, SKIP = "pass", "FAIL", "warn", "skip"
_RESULTS: list[tuple[str, str, str]] = []  # (name, verdict, detail)


class SmokeFailure(Exception):
    pass


class SmokeSkip(Exception):
    """A check that cannot apply here — recorded as `skip`, never as `pass`.

    The distinction is the whole point: a check that silently passes when its
    precondition is absent is a check that swept nothing (note 88), and it
    reads identically to one that swept the corpus and found it clean.
    """


class _Headers(dict):
    """Lower-cased response headers that also remember REPEATED names.

    `dict(resp.headers)` and `{k: v for k, v in resp.headers.items()}` both
    keep only the LAST value per name, and dash-improve-my-llms emits several
    `Link` headers (muicharts, 2026-08-26). Every existing caller wants the
    dict, so the dict is what this is; `get_all()` is the repaired accessor.

    Note that a folded value is equally legal — over HTTP/2 the wire read of
    this host returns both discovery relations comma-joined in ONE `link` —
    so `get_all()` is necessary and not sufficient: a caller counting
    relations must parse the values it gets back, not count the list.
    """

    def __init__(self, pairs):
        self._all: dict[str, list[str]] = {}
        for key, value in pairs:
            self._all.setdefault(key.lower(), []).append(value)
        super().__init__({k: v[-1] for k, v in self._all.items()})

    def get_all(self, name: str) -> list:
        return list(self._all.get(name.lower(), []))


def fetch(url: str, ua: str = UA, method: str = "GET",
          body: bytes | None = None, headers: dict | None = None,
          timeout: int = TIMEOUT, retries: int = 3):
    """(status, headers, text) — HTTP errors are results, not exceptions;
    network errors raise AFTER retries.

    Response headers come back lower-cased: gunicorn sends `content-type`,
    proxies often re-case it — callers must not care. (A CI-only failure in
    the network root's battery was exactly that difference.)
    """
    last_exc: Exception | None = None
    for attempt in range(retries):
        if attempt:
            time.sleep(2 * attempt)
        req = urllib.request.Request(url, data=body, method=method)
        req.add_header("User-Agent", ua)
        for k, v in (headers or {}).items():
            req.add_header(k, v)
        try:
            with urllib.request.urlopen(
                req, timeout=timeout, context=SSL_CONTEXT
            ) as r:
                return (r.status, _Headers(r.headers.items()),
                        r.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            return (e.code, _Headers((e.headers or {}).items()),
                    e.read().decode("utf-8", "replace"))
        except Exception as exc:  # timeout, reset, truncated read, …
            last_exc = exc
    raise last_exc


def record(name: str, verdict: str, detail: str = "") -> None:
    _RESULTS.append((name, verdict, detail))
    print(f"[{verdict:>4}] {name}" + (f" — {detail}" if detail else ""), flush=True)
    if verdict == WARN and os.getenv("GITHUB_ACTIONS"):
        print(f"::warning title=network-smoke {name}::{detail}", flush=True)


def check(name: str, fn) -> None:
    try:
        fn()
        record(name, PASS)
    except SmokeSkip as exc:
        record(name, SKIP, str(exc))
    except SmokeFailure as exc:
        record(name, FAIL, str(exc))
    except Exception as exc:  # network/parse error → still a failure
        record(name, FAIL, f"{type(exc).__name__}: {exc}")


def expect(cond: bool, msg: str) -> None:
    if not cond:
        raise SmokeFailure(msg)


def skip(msg: str) -> None:
    """This check does not apply to this host. Never a pass."""
    raise SmokeSkip(msg)


# ------------------------------------------------------------- the battery --

def declared_python_minor():
    """The fleet Python this checkout declares: the Dockerfile's FROM minor.

    None when there is nothing to hold the host against — no Dockerfile
    beside this script (a fork that deploys another way, or the script run
    outside a checkout) — or when the seat itself is off-contract:
    SMOKE_PYTHON_DECLARED=ignore is set by ci.yml's matrix boot step, whose
    gunicorn deliberately runs the LEG's interpreter (3.13/3.12), and
    tests/test_network_smoke.py's in-process seat monkeypatches this to None
    for the same reason. The seats that leave it armed are exactly the ones
    whose interpreter is a deploy artifact: the docker container in CI and
    production in CD. (First run on the 1.6.27 branch proved both edges
    live: the 3.14 row passed this check, the 3.13/3.12 legs failed it.)
    """
    if os.environ.get("SMOKE_PYTHON_DECLARED") == "ignore":
        return None
    dockerfile = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "Dockerfile")
    try:
        with open(dockerfile, encoding="utf-8") as fh:
            for line in fh:
                m = re.match(r"FROM\s+python:(\d+\.\d+)", line)
                if m:
                    return m.group(1)
    except OSError:
        pass
    return None


def satellite_checks(base: str) -> None:
    get = lambda path, **kw: fetch(base + path, **kw)  # noqa: E731

    def healthz_ok():
        status, _, text = get("/healthz")
        expect(status == 200, f"/healthz {status}")
        expect(json.loads(text).get("ok") is True, f"unexpected body {text[:120]!r}")

    def head_healthz_matches_get():
        # HTTP requires HEAD wherever GET is served. Werkzeug derives a HEAD
        # rule from every GET rule; FastAPI's APIRoute does not, so an ASGI
        # lane answers 405 to the method most uptime monitoring probes with —
        # measured on both FastAPI hosts, every route, 2026-08-27.
        #
        # This does NOT weaken "probe with GET, never HEAD". That rule is
        # about how a session READS a site, and it exists precisely because
        # HEAD can answer for reasons that have nothing to do with the
        # document. This check asks the other question — does HEAD work — and
        # it is the one thing that would have caught the defect on the first
        # CD run after either fork switched backends.
        status, _, _ = get("/healthz")
        expect(status == 200, f"GET /healthz {status} — nothing to compare")
        head_status, _, _ = get("/healthz", method="HEAD")
        expect(head_status == status,
               f"HEAD /healthz {head_status} vs GET {status}"
               + (" — the router has no HEAD rule for its GET routes"
                  if head_status == 405 else ""))

    def python_matches_declared():
        # WHICH interpreter serves, versus the one this repo declares. Three
        # Pythons coexisted for months (image 3.11.8, matrix 3.12,
        # render.yaml 3.12.0) because nothing on the wire could contradict
        # any of them — /healthz's `python` field is the observability, and
        # this check is the teeth: the served minor must equal the
        # Dockerfile's FROM minor. A host with no Dockerfile (or a copy of
        # this script running outside a checkout) has no declaration to
        # compare, so field presence alone is the check there.
        status, _, text = get("/healthz")
        expect(status == 200, f"/healthz {status}")
        served = json.loads(text).get("python") or ""
        expect(bool(served), "/healthz carries no `python` field — the "
               "serving interpreter is invisible (pre-1.6.27 build?)")
        declared = declared_python_minor()
        if declared is None:
            return
        served_minor = ".".join(served.split(".")[:2])
        expect(served_minor == declared,
               f"host serves Python {served}, repo declares {declared} — "
               "a stale image, or a platform runtime nobody aligned")

    def llms_txt_identity():
        # The check this whole standard exists for. The H1 is what an agent
        # fetching /llms.txt cold reads as the name of this site, and a
        # pre-2.3.4 artifact publishes `app.title` (or a bare "Dash") there
        # with nothing else looking wrong.
        status, headers, text = get("/llms.txt")
        expect(status == 200, f"/llms.txt {status}")
        ct = headers.get("content-type", "")
        expect(ct.startswith("text/markdown"), f"content-type {ct!r}")
        first = text.splitlines()[0] if text else ""
        expect(first == SITE_H1, f"H1 {first!r} — identity regression?")
        expect("## Pages" in text, "page index section missing")
        expect("## Network" in text, "cross-host directory missing")

    def llms_txt_names_the_hub():
        _status, _, text = get("/llms.txt")
        expect(HUB_URL in text, f"the directory does not name {HUB_URL}")

    def page_llms_nav():
        status, _, text = get("/backends/llms.txt")
        expect(status == 200, f"/backends/llms.txt {status}")
        expect("/llms.txt" in text, "llms_nav header missing — page doc is a dead end")

    def hidden_pages_404():
        for path in HIDDEN_DOC_PATHS:
            status, _, _ = get(path)
            expect(status == 404, f"{path} {status} (owner surface leaked)")

    def robots_artifact_fingerprint():
        # pip metadata is invisible from outside, so the robots.txt crawler
        # split is how a live host is proven to run the intended package:
        # 2.3.2 allowed OAI-SearchBot; 2.3.3 moved ClaudeBot (the training
        # crawler) to Disallow while allowing Claude-User / Claude-SearchBot.
        status, _, text = get("/robots.txt")
        expect(status == 200, f"/robots.txt {status}")
        lines = [ln.strip() for ln in text.splitlines()]

        def rule(agent):
            marker = f"User-agent: {agent}"
            expect(marker in lines, f"{marker} stanza missing")
            return lines[lines.index(marker) + 1]

        for agent, expected, since in (
            ("OAI-SearchBot", "Allow: /", "2.3.2"),
            ("Claude-User", "Allow: /", "2.3.3"),
            ("Claude-SearchBot", "Allow: /", "2.3.3"),
        ):
            got = rule(agent)
            expect(got == expected,
                   f"{agent} -> {got!r}, expected {expected!r}: pre-{since} artifact")
        # Posture, not artifact (1.6.37): no training stanza is emitted at
        # all when the wall is retired; absent or Allow is the allow shape.
        for agent in ("ClaudeBot", "GPTBot"):
            marker = f"User-agent: {agent}"
            walled = marker in lines and lines[lines.index(marker) + 1] == "Disallow: /"
            expect(not walled, f"{agent} still Disallowed: the 1.6.37 posture flip has not landed")
        expect(any(ln.startswith("Sitemap:") for ln in lines), "Sitemap line missing")

    def sitemap_absolute_and_on_this_host():
        status, _, text = get("/sitemap.xml")
        expect(status == 200, f"/sitemap.xml {status}")
        expect("<loc>https://" in text or "<loc>http://" in text,
               "no absolute <loc> URLs")
        for path in HIDDEN_DOC_PATHS:
            leaked = path.rsplit("/llms.txt", 1)[0]
            expect(leaked not in text, f"hidden path {leaked} leaked into sitemap")

    def crawler_gets_prose():
        # The prerender. A crawler that receives the JavaScript stub indexes
        # nothing, and the page looks perfect in a browser the whole time.
        status, _, text = get("/", ua=CRAWLER_UA)
        expect(status == 200, f"/ {status}")
        expect("<title>" in text, "crawler HTML has no <title>")
        expect(STUB_MARKER not in text,
               "the home page served the JavaScript stub to a crawler")
        expect('rel="canonical"' in text, "no canonical tag for a crawler")

    def agents_and_browsers_get_different_types():
        # One URL, two audiences, and a `Vary` that stops a CDN mixing them.
        status, md_headers, md = get("/backends/llms.txt")
        expect(status == 200, f"/backends/llms.txt {status}")
        expect(md_headers.get("content-type", "").startswith("text/markdown"),
               f"agents got {md_headers.get('content-type')!r}")
        expect("<!DOCTYPE html>" not in md, "viewer chrome reached an agent")

        _status, html_headers, html = get(
            "/backends/llms.txt",
            headers={"Accept": "text/html,application/xhtml+xml,*/*;q=0.8"})
        expect("text/html" in html_headers.get("content-type", ""),
               f"browsers got {html_headers.get('content-type')!r}")
        expect("mk-wordmark" in html, "the network wordmark is missing")

        for label, headers in (("markdown", md_headers), ("html", html_headers)):
            expect("accept" in headers.get("vary", "").lower(),
                   f"no Vary: Accept on the {label} variant — a shared cache "
                   "may serve it to everyone")

    # ---------------------------------------------------------------------
    # The four fleet invariants (1.6.44 item 5). Most forks had some of these
    # as local tests; here they run against the DEPLOYED host on every CD, so
    # a defect that only appears on the wire — a router with no HEAD rule, a
    # lane that lost its discovery headers, a directory that drifted from its
    # own module — is caught by the deploy that shipped it.

    def head_get_parity_three_uas():
        """HEAD answers wherever GET does, in every lane.

        `/healthz` alone with one UA is not the test: the prerender
        middleware answers a crawler-UA `HEAD /` before routing, so that one
        path can return 200 on a host whose every other route 405s. Probe a
        path that is NOT `/`, with all three UAs.
        """
        paths = ("/healthz", "/llms.txt", "/robots.txt", "/sitemap.xml", "/")
        agents = (("browser", BROWSER_UA), ("crawler", CRAWLER_UA),
                  ("engine", "curl/8 " + _PROBE))
        mismatches = []
        pairs = 0
        for path in paths:
            for lane, ua in agents:
                get_status, _, _ = get(path, ua=ua)
                head_status, _, _ = get(path, ua=ua, method="HEAD")
                pairs += 1
                if head_status != get_status:
                    mismatches.append(
                        f"{lane} {path}: HEAD {head_status} vs GET {get_status}"
                        + (" (no HEAD rule for this GET route)"
                           if head_status == 405 else ""))
        expect(pairs == len(paths) * len(agents),
               f"compared {pairs} pairs, expected {len(paths) * len(agents)}")
        expect(not mismatches, "; ".join(mismatches))

    def api_llms_rows_present():
        """A host that declares API_PACKAGES serves a non-empty /api index.

        SKIPPED, never passed, where API_PACKAGES is empty — the template's
        own state. A pass here would be a check that swept nothing.
        """
        try:
            from lib.constants import API_PACKAGES
        except Exception:
            skip("no checkout beside this script — API_PACKAGES unreadable")
        if not API_PACKAGES:
            skip("API_PACKAGES is empty on this host — nothing to index")
        status, _, text = get("/api/llms.txt")
        expect(status == 200, f"/api/llms.txt {status} while API_PACKAGES "
                              f"declares {len(API_PACKAGES)} package(s)")
        rows = [ln for ln in text.splitlines() if ln.strip().startswith("- ")]
        expect(len(rows) > 0,
               f"/api/llms.txt lists 0 entries for {list(API_PACKAGES)}")

    def discovery_link_headers_per_lane():
        """Both lanes advertise the same discovery relations.

        Read every `Link` value, not `headers['link']`: repeated headers keep
        only the last through a plain dict, and a folded comma-joined value is
        equally legal — this host serves both relations folded over HTTP/2.
        So parse the relations out of everything that came back.
        """
        wanted = {"alternate", "describedby"}
        for lane, ua in (("browser", BROWSER_UA), ("crawler", CRAWLER_UA)):
            status, headers, _ = get("/", ua=ua)
            expect(status == 200, f"{lane} GET / {status}")
            values = headers.get_all("link")
            rels = set(re.findall(r'rel="?([a-zA-Z-]+)"?', ", ".join(values)))
            expect(wanted <= rels,
                   f"{lane} lane advertises {sorted(rels) or 'no Link header'}"
                   f" — missing {sorted(wanted - rels)}")
            expect(all("/llms.txt" in v for v in values),
                   f"{lane} lane's Link headers do not point at /llms.txt: "
                   f"{values}")

    def ai_bot_posture():
        """The SERVED robots.txt against the one this app GENERATES.

        1.6.44 item 19, from the 2plot.dev proxy canary. An edge can inject,
        rewrite or replace robots.txt in perfectly valid syntax, with no tell
        beyond a comment marker — a grep for `User-agent:` sails straight
        past it. To learn what the APP declares you must generate it in
        process or read the config; to learn what the WORLD is told you fetch
        it; and WHEN THEY DIFFER, THE DIFFERENCE IS THE FINDING. Same family
        as "verify the artifact the claim is about, and say which one".

        SKIPPED where the app cannot be generated beside this script (a copy
        of the battery run against another host) — a comparison with only
        one side is not a comparison.
        """
        status, _, served = get("/robots.txt")
        expect(status == 200, f"/robots.txt {status}")

        try:
            from lib.robots_expected import expected_directives
            generated = expected_directives()
        except Exception as exc:
            skip(f"cannot generate this app's robots.txt here ({type(exc).__name__})")

        if not generated:
            skip("the app generated no directives to compare against")

        def directives(text):
            out = []
            for line in text.splitlines():
                line = line.split("#", 1)[0].strip()
                if line and ":" in line:
                    name, _, value = line.partition(":")
                    out.append((name.strip().lower(), value.strip()))
            return out

        served_directives = directives(served)
        expect(served_directives,
               "the served robots.txt carries no directives at all")

        # BOTH directions. An edge that REMOVES a directive is as much a
        # rewrite as one that adds a stanza — dropping this host's `Allow:`
        # rules for the AI search agents would be invisible to an
        # added-only comparison, and it is the change most likely to be
        # made on your behalf by a "security" default.
        injected = [d for d in served_directives if d not in generated]
        missing = [d for d in generated if d not in served_directives]
        markers = [ln.strip() for ln in served.splitlines()
                   if ln.strip().startswith("#")
                   and ("BEGIN" in ln or "Managed" in ln or "END" in ln)]
        expect(not injected and not missing and not markers,
               "the served robots.txt is not the one this app wrote"
               + (f" — {len(injected)} directive(s) the app did not "
                  f"generate, first: {injected[0]}" if injected else "")
               + (f" — {len(missing)} directive(s) the app wrote that are "
                  f"NOT served, first: {missing[0]}" if missing else "")
               + (f" — edge marker: {markers[0]!r}" if markers else ""))

    def directory_counts_are_derived():
        """The Network section lists exactly the peers the module names.

        Counts come from `lib/network_directory`, never a literal: a hard
        number in a battery is a check that stops testing the moment the
        fleet grows, and passes while doing it.
        """
        try:
            from lib.constants import BASE_URL
            from lib.network_directory import peers_for
        except Exception:
            skip("no checkout beside this script — the directory is unreadable")
        expected = {p["url"].rstrip("/") for p in peers_for(BASE_URL)}
        expect(len(expected) > 0,
               "peers_for() names no peers — nothing to hold the wire to")
        _status, _, text = get("/llms.txt")
        section = text.split("## Network", 1)[-1]
        missing = sorted(u for u in expected if u.rstrip("/") not in section)
        expect(not missing,
               f"{len(missing)} of {len(expected)} peers absent from the "
               f"/llms.txt Network section: {missing[:3]}")

    # ---------------------------------------------------------------------
    # The well-known surfaces (1.6.45 item 3). dimll 2.10 serves three new
    # documents and a Content-Signal line; these are the rows that read them.
    # Every one NAMES WHAT IT DID NOT COVER when it skips, because a skip
    # that says nothing is indistinguishable from a pass that means nothing.

    def wellknown_unknown_404():
        """Tier 0: an unknown /.well-known/* path is a 404 JSON body, never
        the app shell.

        The failure this catches is not a missing route — it is a route that
        answers 200 with HTML, which every catch-all does by default.
        piratesbargain.com serves its catch-all HTML at /llms.txt, so the
        error body naming `/llms.txt` is itself the tell: a host whose 404
        body does not name it is serving somebody else's catch-all.
        """
        status, _, text = get("/.well-known/nope")
        expect(status == 404, f"/.well-known/nope answered {status}, not 404 "
                              "— an unknown well-known path is being served "
                              "by a catch-all")
        stripped = text.lstrip()
        expect(not stripped.lower().startswith("<!doctype"),
               "the 404 body is HTML — this is the app shell, not a well-known "
               "error document")
        try:
            body = json.loads(text)
        except ValueError:
            raise SmokeFailure(f"the 404 body is not JSON: {text[:80]!r}")
        expect(body.get("see") == "/llms.txt",
               f"the 404 body does not point at /llms.txt: {body!r}")

    def api_catalog_links_resolve():
        """Every `href` in the catalog answers 200.

        A catalog entry that 404s is the lie the Tier 0 guard removes: an
        agent reads the catalog, follows a link, and gets nothing. Checking
        the document parses is not enough — it is the LINKS that are the
        claim.
        """
        status, _, text = get("/.well-known/api-catalog")
        expect(status == 200, f"/.well-known/api-catalog {status}")
        try:
            catalog = json.loads(text)
        except ValueError:
            raise SmokeFailure(f"not JSON: {text[:80]!r}")

        links = []
        for entry in catalog.get("linkset") or []:
            for rel, items in entry.items():
                if rel == "anchor" or not isinstance(items, list):
                    continue
                links += [i.get("href") for i in items if isinstance(i, dict)]
        links = [href for href in links if href]
        if not links:
            skip("the catalog declares no links — nothing to resolve "
                 "(the document's own 200 is covered, its links are not)")

        # 200 IS NOT ENOUGH, and my own mutation check is what proved it:
        # a catalog pointing at `/nowhere-at-all` PASSED a status check,
        # because Dash answers 200 for any path and lets the client router
        # decide (note 104 — the soft-404 item 8 fixes). A catalog entry
        # resolving to the app shell is exactly the lie this row exists to
        # catch, so the shell is a failure whatever its status.
        broken = []
        for href in links:
            path = urllib.parse.urlsplit(href).path or href
            if not path.startswith("/"):
                continue                      # off-host; not this host's claim
            code, _, body = get(path, ua=CRAWLER_UA)
            if code != 200:
                broken.append(f"{path} -> {code}")
            elif body.lstrip().lower().startswith("<!doctype"):
                broken.append(f"{path} -> 200 but the app shell (soft 404)")
        expect(not broken,
               f"{len(broken)} of {len(links)} catalog link(s) do not resolve: "
               f"{broken[:3]}")

    def mcp_card_matches_host():
        """The card is this host's, or there is no card.

        This is the package's untested "real registration flips the card"
        path: a host with no MCP bridge must 404, and a host with one must
        name ITSELF — a card naming another app is worse than none, because
        an agent would route to it.
        """
        status, _, text = get("/.well-known/mcp/server-card.json")
        if status == 404:
            skip("no MCP bridge on this host — the 404 is the contract "
                 "(the card's CONTENT is not covered here)")
        expect(status == 200, f"/.well-known/mcp/server-card.json {status}")
        try:
            card = json.loads(text)
        except ValueError:
            raise SmokeFailure(f"not JSON: {text[:80]!r}")

        _status, _, health = get("/healthz")
        app_name = (json.loads(health).get("app") or "").strip()
        expect(bool(app_name), "/healthz names no app — nothing to compare")
        served = ((card.get("serverInfo") or {}).get("name") or "").strip()
        expect(served == app_name,
               f"the MCP card names {served!r} and this host is {app_name!r}")

    def skills_index_and_digest():
        """The index is a LIST — empty is an answer, absent is a mystery —
        and any entry's digest describes the bytes actually served.

        Both halves in one row on purpose: a host with no SKILL.md is the
        empty case and a host with one is the digest case, and a battery
        that only checked the populated case would miss the index
        disappearing altogether.
        """
        status, _, text = get("/.well-known/agent-skills/index.json")
        expect(status == 200, f"agent-skills index {status} — empty is an "
                              "answer, absent is a mystery")
        try:
            index = json.loads(text)
        except ValueError:
            raise SmokeFailure(f"not JSON: {text[:80]!r}")
        skills = index.get("skills")
        expect(isinstance(skills, list),
               f"`skills` is {type(skills).__name__}, not a list")

        if not skills:
            skip("this host publishes no skill — the index's EMPTY shape is "
                 "covered, no digest was checked")

        import hashlib

        for entry in skills:
            href = entry.get("url") or ""
            # Take the PATH, whatever host the index names. The index is
            # built from the app's own BASE_URL, so in-process (and against
            # any host probed by another name) it advertises the public
            # origin while the battery is talking to 127.0.0.1 — comparing
            # against `base` made this row fail on a correct index.
            path = urllib.parse.urlsplit(href).path or href
            expect(path.startswith("/"),
                   f"skill url has no path: {href!r}")
            code, _, body = get(path)
            expect(code == 200, f"{path} -> {code}; the index advertises it")
            digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
            expect(entry.get("digest") == f"sha256:{digest}",
                   f"{path}: the index advertises {entry.get('digest')} and "
                   f"the served bytes hash to sha256:{digest}")

    def page_markdown_negotiation():
        """`Accept: text/markdown` is a second REPRESENTATION of the page.

        Not a second URL: same path, negotiated, with `Vary` naming Accept so
        a shared cache cannot serve one to a client that asked for the other.
        """
        status, headers, markdown = get(
            "/backends", headers={"Accept": "text/markdown"})
        expect(status == 200, f"/backends (markdown) {status}")
        ctype = headers.get("content-type", "")
        expect(ctype.startswith("text/markdown"),
               f"Accept: text/markdown got {ctype!r}")
        expect("accept" in headers.get("vary", "").lower(),
               f"Vary is {headers.get('vary')!r} — a shared cache may serve "
               "this markdown to a browser")

        _s, html_headers, _html = get(
            "/backends", headers={"Accept": "text/html,*/*;q=0.8"})
        expect("text/html" in html_headers.get("content-type", ""),
               "the same URL did not give HTML to an HTML request")

        # CORRECTED AGAINST THE DROP, and corrected twice, which is why the
        # measurement is written down here rather than the conclusion.
        #
        # The drop says the negotiated bytes EQUAL `/<page>/llms.txt`'s. They
        # do not, on dimll 2.10.0. Nor does either contain the other — my
        # first correction assumed a prefix and was also wrong. Measured on
        # this host: the two share a 7,481-character common SUFFIX out of
        # ~7,800, and diverge in a navigational line, the standalone document
        # saying "…listed in the site index above" where the negotiated one
        # says "…every page on this site, as Markdown".
        #
        # So they are the same PAGE with different framing, and the honest
        # invariant is identity of the page rather than of the bytes: same
        # H1, both markdown. That catches the negotiation serving a different
        # page — which is the failure worth catching — and does not pretend
        # to a byte equality the package does not offer.
        _s, _h, standalone = get("/backends/llms.txt")
        heading = markdown.strip().splitlines()[0] if markdown.strip() else ""
        twin_heading = (standalone.strip().splitlines()[0]
                        if standalone.strip() else "")
        expect(heading.startswith("# "),
               f"the negotiated markdown does not start with an H1: "
               f"{heading[:60]!r}")
        expect(heading == twin_heading,
               f"the negotiated representation is a different page: "
               f"{heading!r} vs {twin_heading!r} at /backends/llms.txt")

    def edge_honours_vary():
        """A REAL cache in front of this host serves two representations of
        one URL. Only meaningful through an edge."""
        if not base.startswith("https://"):
            skip("not fetched through an edge (no https) — Vary is asserted "
                 "on the app's own headers by page_markdown_negotiation, and "
                 "the CACHE's behaviour is not covered here")
        _s, md_headers, markdown = get(
            "/backends", headers={"Accept": "text/markdown"})
        _s2, html_headers, html = get(
            "/backends", headers={"Accept": "text/html,*/*;q=0.8"})
        expect(markdown != html,
               "the edge served ONE representation to both Accept headers — "
               "a cache that ignores Vary")
        for label, hdrs in (("markdown", md_headers), ("html", html_headers)):
            expect("accept" in hdrs.get("vary", "").lower(),
                   f"the {label} response lost its Vary through the edge")

    def assets_cached():
        """A static asset carries a real max-age (note 103).

        Every host in the fleet answered `no-cache` on /assets/* until
        1.6.44 item 6g, so the edge stored NOTHING and every page paid for
        its CSS again on every view. The header is the whole check.

        NOT COVERED: that an edge actually stored it. This reads the
        ORIGIN's header — `edge_honours_vary` is the row that speaks to
        cache behaviour, and neither one proves a hit ratio.
        """
        status, headers, _ = get("/assets/main.css")
        expect(status == 200, f"/assets/main.css {status} — nothing to read")
        value = (headers.get("cache-control") or "").lower()
        expect(value, "/assets/main.css carries no cache-control at all")
        match = re.search(r"max-age\s*=\s*(\d+)", value)
        expect(match is not None,
               f"cache-control {value!r} names no max-age — `no-cache` and "
               "`no-store` are the pre-1.6.44 answer the edge cannot store")
        expect(int(match.group(1)) > 0,
               f"max-age={match.group(1)} is zero — stored, then never used")

    def healthz_keys_vs_template():
        """This host's /healthz key set against the TEMPLATE'S LIVE set.

        Read at run time, never a fixed list of seven: a fixed list goes
        stale the release after it is written, and the defect this row
        exists for is a host serving FEWER keys than the template — an ASGI
        response model that silently drops a field it was not told about
        (`llms_version` was missing from this lane for two days in 1.6.44
        for exactly that reason, while every fixed-list check passed).

        ON THE TEMPLATE ITSELF the comparison is a tautology — the host and
        the reference are the same wire, and the row can never fail. The
        drop's wording did not cover that case. So here the reference
        becomes the app's OWN `health_payload()`, computed in process: wire
        keys versus the keys the code produces is precisely the
        response-model drop, and it is the only form of this row that can
        go red on the host the fork copies from.

        NOT COVERED either way: the VALUES. Key presence only. And on a
        FLASK origin the self-comparison is weak by construction — the route
        serialises the payload dict as-is, so the two sets agree unless the
        route filters. Its teeth are on the ASGI lanes, which is where the
        defect was. Mutation-checked 2026-09-11 by putting the 1.6.44 defect
        back (HealthResponse without `llms_version`, extra="ignore"): the row
        goes red naming `llms_version` as dropped between code and wire.
        """
        status, _, text = get("/healthz")
        expect(status == 200, f"/healthz {status} — nothing to compare")
        mine = set(json.loads(text).keys())
        expect(mine, "/healthz returned an object with no keys at all")

        base_host = urllib.parse.urlsplit(base).netloc
        template_host = urllib.parse.urlsplit(TEMPLATE_BASE_URL).netloc
        try:
            from lib.constants import BASE_URL as _SELF
            self_host = urllib.parse.urlsplit(_SELF).netloc
        except Exception:
            self_host = ""
        is_template = template_host in (base_host, self_host)

        if is_template:
            try:
                from lib.health import health_payload
            except Exception:
                skip("this IS the template, and lib/health.py is not "
                     "importable beside this script — the self-comparison "
                     "against the template would be a tautology, so the row "
                     "has no reference at all here")
            backend = json.loads(text).get("backend") or "flask"
            produced = set(health_payload(backend).keys())
            dropped = sorted(produced - mine)
            expect(not dropped,
                   f"the app's health_payload() produces {sorted(produced)} "
                   f"but the wire serves {sorted(mine)} — {dropped} is "
                   "dropped between the code and the response, which is the "
                   "ASGI response-model class this row exists for")
            return

        ref_status, _, ref_text = fetch(TEMPLATE_BASE_URL + "/healthz", ua=UA)
        expect(ref_status == 200,
               f"the template's /healthz answered {ref_status} — no "
               f"reference set, so this host's {len(mine)} keys are unjudged")
        theirs = set(json.loads(ref_text).keys())
        expect(theirs, "the template served a /healthz object with no keys")
        missing = sorted(theirs - mine)
        expect(not missing,
               f"this host is missing {missing} that the template serves "
               f"(template {len(theirs)} keys, here {len(mine)})")

    def crawler_404():
        """An unregistered path is a 404 to a crawler, a shell to a browser.

        1.6.45 item 8. Dash answers 200 for ANY path, so every mistyped link
        and stale URL was a soft 404 that search engines and agents indexed
        as real. Both lanes are asked, because 404ing BOTH would satisfy a
        one-lane check while breaking the site for people.
        """
        missing = "/definitely-not-a-page-on-this-host"
        crawler_status, _, _ = get(missing, ua=CRAWLER_UA)
        expect(crawler_status == 404,
               f"{missing} answered {crawler_status} to a crawler — a soft "
               "404 is indexed as a real page")

        browser_status, _, body = get(missing, ua=BROWSER_UA)
        expect(browser_status == 200,
               f"{missing} answered {browser_status} to a BROWSER — the "
               "browser lane keeps Dash's own 404 page, which is the better "
               "experience; a bare status code here is a regression, not a fix")
        expect(body.lstrip().lower().startswith("<!doctype"),
               "the browser did not get the app shell")

        # And a real page must still be 200 on both, or this row would pass
        # on a host that 404s everything.
        for label, ua in (("crawler", CRAWLER_UA), ("browser", BROWSER_UA)):
            status, _, _ = get("/backends", ua=ua)
            expect(status == 200,
                   f"/backends answered {status} to a {label} — the guard is "
                   "eating registered pages")

    def content_signal_matches_config():
        """Exactly one `Content-Signal:` line, and its values are this host's
        RobotsConfig rather than a copied default."""
        _status, _, robots = get("/robots.txt")
        lines = [ln.strip() for ln in robots.splitlines()
                 if ln.strip().lower().startswith("content-signal:")]
        expect(len(lines) == 1,
               f"{len(lines)} Content-Signal lines; the spec allows one")

        try:
            import run

            config = getattr(run.app, "_robots_config", None)
        except Exception:
            config = None
        if config is None:
            skip(f"no checkout beside this script — the single line "
                 f"{lines[0]!r} is covered, its VALUES are not")

        signal = dict(
            part.strip().split("=", 1)
            for part in lines[0].split(":", 1)[1].split(",")
            if "=" in part
        )
        expected = {
            "search": "yes" if getattr(config, "allow_traditional", True) else "no",
            "ai-input": "yes" if getattr(config, "allow_ai_search", True) else "no",
            "ai-train": "no" if getattr(config, "block_ai_training", False) else "yes",
        }
        wrong = {k: (signal.get(k), v) for k, v in expected.items()
                 if signal.get(k) != v}
        expect(not wrong,
               f"Content-Signal disagrees with this host's RobotsConfig: "
               f"{wrong} (served {lines[0]!r})")

    for name, fn in (
        ("healthz_ok", healthz_ok),
        ("wellknown_unknown_404", wellknown_unknown_404),
        ("api_catalog_links_resolve", api_catalog_links_resolve),
        ("mcp_card_matches_host", mcp_card_matches_host),
        ("skills_index_and_digest", skills_index_and_digest),
        ("page_markdown_negotiation", page_markdown_negotiation),
        ("edge_honours_vary", edge_honours_vary),
        ("assets_cached", assets_cached),
        ("healthz_keys_vs_template", healthz_keys_vs_template),
        ("crawler_404", crawler_404),
        ("content_signal_matches_config", content_signal_matches_config),
        ("head_get_parity_three_uas", head_get_parity_three_uas),
        ("api_llms_rows_present", api_llms_rows_present),
        ("discovery_link_headers_per_lane", discovery_link_headers_per_lane),
        ("directory_counts_are_derived", directory_counts_are_derived),
        ("ai_bot_posture", ai_bot_posture),
        ("head_healthz_matches_get", head_healthz_matches_get),
        ("python_matches_declared", python_matches_declared),
        ("llms_txt_identity", llms_txt_identity),
        ("llms_txt_names_the_hub", llms_txt_names_the_hub),
        ("page_llms_nav", page_llms_nav),
        ("hidden_pages_404", hidden_pages_404),
        ("robots_artifact_fingerprint", robots_artifact_fingerprint),
        ("sitemap_absolute_and_on_this_host", sitemap_absolute_and_on_this_host),
        ("crawler_gets_prose", crawler_gets_prose),
        ("agents_and_browsers_get_different_types",
         agents_and_browsers_get_different_types),
    ):
        check(name, fn)


# ------------------------------------------------------------------- main --

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base-url", default=DEFAULT_BASE_URL,
                    help="the satellite under test (default: the CI container)")
    ap.add_argument("--require", default="", metavar="ROW,ROW",
                    help="rows that MUST pass here: a skip in one of them "
                         "exits non-zero. A skip is a verdict, never a pass "
                         "(note 108) — some rows can only mean anything in "
                         "one seat, and silently skipping there is how a "
                         "battery stays green for a whole release without "
                         "making its comparison.")
    args = ap.parse_args()

    base = args.base_url.rstrip("/")
    required = [name.strip() for name in args.require.split(",") if name.strip()]
    print(f"network-smoke → {base}"
          + (f"  (requiring {len(required)}: {', '.join(required)})"
             if required else "")
          + "\n")
    satellite_checks(base)

    counts = {v: sum(1 for _, verdict, _ in _RESULTS if verdict == v)
              for v in (PASS, FAIL, WARN, SKIP)}
    print(f"\n{counts[PASS]} passed, {counts[FAIL]} failed, "
          f"{counts[WARN]} warnings, {counts[SKIP]} skipped")

    verdicts = {name: verdict for name, verdict, _ in _RESULTS}
    details = {name: detail for name, _, detail in _RESULTS}
    # A required name that matches NO row requires nothing — the typo makes
    # the flag decorative and the run green, which is the failure this whole
    # item is about. It is an error in its own right.
    unknown = [name for name in required if name not in verdicts]
    skipped = [name for name in required if verdicts.get(name) == SKIP]
    for name in unknown:
        print(f"::error::--require names {name!r}, which is not a row in this "
              f"battery — it requires nothing and this run proved nothing "
              f"about it")
    for name in skipped:
        print(f"::error::{name} SKIPPED and is required here — {details[name]}")

    return 1 if (counts[FAIL] or skipped or unknown) else 0


if __name__ == "__main__":
    sys.exit(main())
