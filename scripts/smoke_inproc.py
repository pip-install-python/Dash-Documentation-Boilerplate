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


def _wsgi_opener():
    """Flask's test client. Same object CI's gunicorn step serves through."""
    client = run.server.test_client()

    def _urlopen(req, timeout=None, context=None, **_kw):
        url, method = req.full_url, req.get_method()
        headers = dict(req.header_items())
        rv = client.open(url, method=method, headers=headers, data=req.data)
        message = _message(rv.headers.items())
        if rv.status_code >= 400:
            raise urllib.error.HTTPError(
                url, rv.status_code, rv.status, message, io.BytesIO(rv.data)
            )
        return _Response(rv.data, rv.status_code, message)

    return _urlopen


def _asgi_opener():
    """httpx over the ASGI app — the fastapi and quart legs.

    `follow_redirects=False` on purpose: the battery asks questions ABOUT
    status codes (HEAD/GET parity, the well-known 404 guard), and a client
    that quietly followed a redirect would answer a different question than
    the one each row asks.
    """
    import httpx

    transport = httpx.ASGITransport(app=run.server)
    client = httpx.Client(transport=transport,
                          base_url="http://127.0.0.1:8550",
                          follow_redirects=False)

    def _urlopen(req, timeout=None, context=None, **_kw):
        url, method = req.full_url, req.get_method()
        headers = dict(req.header_items())
        rv = client.request(method, url, headers=headers, content=req.data)
        message = _message(rv.headers.items())
        body = rv.content
        if rv.status_code >= 400:
            raise urllib.error.HTTPError(
                url, rv.status_code, rv.reason_phrase, message, io.BytesIO(body)
            )
        return _Response(body, rv.status_code, message)

    return _urlopen


urllib.request.urlopen = (
    _wsgi_opener() if BACKEND == "flask" else _asgi_opener()
)

print(f"[smoke-inproc] backend={BACKEND} "
      f"({'WSGI test client' if BACKEND == 'flask' else 'httpx ASGITransport'})",
      flush=True)

sys.argv = ["network_smoke.py", "--base-url", "http://127.0.0.1:8550"]
sys.path.insert(0, os.path.join(os.getcwd(), "scripts"))

import network_smoke  # noqa: E402

sys.exit(network_smoke.main())
