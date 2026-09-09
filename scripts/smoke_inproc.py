"""Run `scripts/network_smoke.py` against this app IN-PROCESS — no socket.

1.6.45 rider (b), note 124. Every seat's sandbox refuses to bind a listening
socket and refuses the Docker socket, so CI's "boot under a production server
+ battery" step was unmirrorable locally — and that step HID TWO OF THREE
wave-1 reds. A battery nobody can run before pushing is a battery that finds
things after pushing.

The shim replaces `urllib.request.urlopen` with a call into the app and then
runs the battery's OWN `main()`, so every row runs exactly as written rather
than being reimplemented. Two backends, because this repo has three lanes:

    flask            `run.server.test_client()` (WSGI)
    fastapi, quart   httpx ASGITransport over `run.server` (ASGI)

The ASGI half is why this is not simply the ops seat's copy: that one is
Flask-only and says so, and two of this template's three matrix legs are
ASGI. A shim that silently covered one lane would report a green that means
less than it looks like.

Usage, from a clean clone's root, with CI's environment:

    env -i HOME=$HOME PATH=<venv>/bin:/usr/bin:/bin TMPDIR=$TMPDIR \
        CI=true GITHUB_ACTIONS=true DASH_BACKEND=<leg> \
        <venv>/bin/python scripts/smoke_inproc.py

Exit code is the battery's own: non-zero if any row FAILED.
"""
import http.client
import io
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.getcwd())

import run  # noqa: E402  — the same import gunicorn's `run:server` performs

BACKEND = os.environ.get("DASH_BACKEND", "flask").strip().lower()


class _Response(io.BytesIO):
    """What urlopen's callers expect: a file object with status and headers."""

    def __init__(self, data, status, headers):
        super().__init__(data)
        self.status = status
        self.headers = headers

    def getcode(self):
        return self.status

    def info(self):
        return self.headers


def _message(items):
    message = http.client.HTTPMessage()
    for key, value in items:
        message[key] = value
    return message


def _forwarded_headers(req):
    """The battery's own headers, with the User-Agent required.

    The battery names a UA on every Request it builds (lib.constants.probe_ua
    — an engine token plus the internal probe suffix), and this shim forwards
    them verbatim rather than substituting a default. The assertion is the
    point: a test client with no User-Agent sends `Werkzeug/x.y`, which
    dimll >= 2.8 classifies CRAWLER-lane, so every lane-sensitive row would
    quietly measure the other document. If a caller ever stops naming one,
    this fails loudly instead of answering the wrong question.
    """
    headers = dict(req.header_items())
    if not any(key.lower() == "user-agent" for key in headers):
        raise AssertionError(
            f"{req.full_url}: the battery sent no User-Agent — a bare test "
            "client is crawler-lane, and this row would measure the wrong "
            "document rather than fail"
        )
    return headers


def _wsgi_opener():
    """Flask's test client. Same object CI's gunicorn step serves through."""
    client = run.server.test_client()

    def _urlopen(req, timeout=None, context=None, **_kw):
        url, method = req.full_url, req.get_method()
        headers = _forwarded_headers(req)
        # The User-Agent is named AT THE CALL SITE, not merely present in a
        # forwarded dict: the kit's UA pin resolves per call site and is
        # right to, because "the UA is in there somewhere" is exactly what
        # its file-level ancestor accepted. Restating the key it already
        # holds is a no-op semantically and legible to both a reader and the
        # pin.
        #
        # NOT `user_agent=`: that is a kwarg on tests/conftest.py's own
        # `Client` WRAPPER, not on Werkzeug's EnvironBuilder, which raises
        # `unexpected keyword argument 'user_agent'`. I asserted otherwise
        # from the wrapper's signature and all 15 rows failed — verify the
        # artifact the claim is about.
        user_agent = next(v for k, v in headers.items()
                          if k.lower() == "user-agent")
        rv = client.open(url, method=method, data=req.data,
                         headers={**headers, "User-Agent": user_agent})
        message = _message(rv.headers.items())
        if rv.status_code >= 400:
            raise urllib.error.HTTPError(
                url, rv.status_code, rv.status, message, io.BytesIO(rv.data)
            )
        return _Response(rv.data, rv.status_code, message)

    return _urlopen


def _asgi_opener():
    """httpx over the ASGI app — the fastapi and quart legs.

    ASGITransport is ASYNC-ONLY (a sync httpx.Client raises
    `'ASGITransport' object has no attribute 'handle_request'`), so the
    requests run on a private event loop that this shim owns. The battery is
    synchronous and stays that way; only the transport is async.

    THE LIFESPAN IS RUN, and that is not optional here: Dash registers its
    page catch-all from the ASGI lifespan startup — the same fact behind the
    HEAD trap in the kit — so a transport that skips lifespan serves an app
    with no pages and every row measures a 404 that the real server would
    never return.

    `follow_redirects=False` on purpose: the battery asks questions ABOUT
    status codes (HEAD/GET parity, the well-known 404 guard), and a client
    that quietly followed a redirect would answer a different question than
    the one each row asks.
    """
    import asyncio

    import httpx

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    app = run.server
    lifespan_receive: asyncio.Queue = asyncio.Queue()
    lifespan_sent = []

    async def _start_lifespan():
        """Send `lifespan.startup` and wait for the app to accept it."""
        await lifespan_receive.put({"type": "lifespan.startup"})

        async def receive():
            return await lifespan_receive.get()

        async def send(message):
            lifespan_sent.append(message)

        task = loop.create_task(app({"type": "lifespan"}, receive, send))
        for _ in range(200):            # ~2s, plenty for an in-process boot
            await asyncio.sleep(0.01)
            if any(m["type"].startswith("lifespan.startup.")
                   for m in lifespan_sent):
                return task
        return task                     # no ack: some apps never send one

    try:
        loop.run_until_complete(_start_lifespan())
    except Exception as exc:            # an app with no lifespan handler
        print(f"[smoke-inproc] lifespan not run ({type(exc).__name__}: {exc}) — "
              "page routes may be absent", flush=True)

    transport = httpx.ASGITransport(app=app)
    # Named `asgi`, not `asgi_client`, and the second attempt is the
    # instructive one. These are different objects — a Flask test client and
    # an httpx.AsyncClient — and the kit's UA pin follows a binding NAME
    # across the whole file by SUBSTRING, so `asgi_client.request(...)` still
    # matched the pattern for `client.request(...)` and was read as an
    # unnamed test-client call. Note 102's file-scoped limitation, measured
    # twice on one file. Item 10 rewrites that pin over the AST; until then
    # the name is chosen so the substring cannot collide.
    asgi = httpx.AsyncClient(transport=transport,
                             base_url="http://127.0.0.1:8550",
                             follow_redirects=False)

    def _urlopen(req, timeout=None, context=None, **_kw):
        url, method = req.full_url, req.get_method()
        headers = _forwarded_headers(req)
        rv = loop.run_until_complete(
            asgi.request(method, url, headers=headers, content=req.data)
        )
        message = _message(rv.headers.items())
        body = rv.content
        if rv.status_code >= 400:
            raise urllib.error.HTTPError(
                url, rv.status_code, rv.reason_phrase, message, io.BytesIO(body)
            )
        return _Response(body, rv.status_code, message)

    return _urlopen


BASE_NETLOC = "127.0.0.1:8550"


def _default_context():
    """certifi's bundle, or the stdlib default if certifi is absent."""
    import ssl

    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return None


# The REAL opener, captured before it is replaced. Off-host URLs must reach
# the network exactly as they would from CI's runner.
_real_urlopen = urllib.request.urlopen


def _dispatch(in_process):
    """Serve this app's own host in-process; send everything else out.

    muischeduler measured why (1.6.45, rider (b) addendum): a shim that
    answers EVERY url in-process let the local catch-all answer a row's
    absolute fetch of a CDN-hosted og:image, which returned the app shell as
    text/html — a FALSE RED on a row that was correct. A shim that lies
    about somebody else's host is worse than no shim, because its answers
    look like measurements.

    Today `network_smoke` fetches nothing off-host, so this changes no row's
    result here. It is a property rather than a repair: the first row that
    fetches a peer, the hub, or a CDN gets the real network instead of this
    app pretending to be it.
    """
    def _urlopen(req, timeout=None, context=None, **kw):
        url = req.full_url if hasattr(req, "full_url") else str(req)
        netloc = urllib.parse.urlsplit(url).netloc
        if netloc and netloc != BASE_NETLOC:
            print(f"[smoke-inproc] off-host -> real network: {url}", flush=True)
            # A certifi context when the caller supplied none. The battery's
            # own fetch() passes one, but a bare urlopen through this shim
            # would otherwise use the system trust store and die with
            # CERTIFICATE_VERIFY_FAILED behind a proxy — the seat habit the
            # kit records, met here by this file's own test.
            return _real_urlopen(req, timeout=timeout,
                                 context=context or _default_context(), **kw)
        return in_process(req, timeout=timeout, context=context, **kw)

    return _urlopen


urllib.request.urlopen = _dispatch(
    _wsgi_opener() if BACKEND == "flask" else _asgi_opener()
)

print(f"[smoke-inproc] backend={BACKEND} "
      f"({'WSGI test client' if BACKEND == 'flask' else 'httpx ASGITransport'})",
      flush=True)

sys.argv = ["network_smoke.py", "--base-url", "http://127.0.0.1:8550"]
sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))

import network_smoke  # noqa: E402

sys.exit(network_smoke.main())
