"""
Visitor Analytics Tracker
Tracks visitor information including device type, bot detection, and geolocation.

This ledger is the raw material for two things:

1. the app's own record of who read the docs, and
2. the hourly rollup this app POSTs to 2plot.ai (``lib/satellite_reporter``),
   which is what the network ``/traffic`` dashboard charts.

Because the hub compares apps side by side, the fields written here match the
hub's own ledger exactly: ``{timestamp, path, device_type, user_agent,
bot_type?, ip_address?, location?}``. Crawler rows (``device_type == "bot"``)
additionally carry ``{vendor_key, vendor_class, verified, lane}`` since
1.6.34; human rows are unchanged.

Since 1.6.34 the same file holds a SECOND table, ``reads``: one row per
corpus document dash-improve-my-llms served, handed to :meth:`record_read`
through the package's ``on_document_read`` hook (2.8.0). ``visits`` is what
the request hook saw; ``reads`` is what the package says it served (tier,
verdict, bytes, verified vendor). They are joined by ``lib/traffic_rollup``
and never summed into each other.

THERE IS ONE CLASSIFIER — ``dash_improve_my_llms.classify()``. This module
carried its own User-Agent lists for a year; they filed ClaudeBot (Anthropic's
*training* crawler) under "search", still named the retired ``anthropic-ai`` /
``claude-web`` tokens, knew nothing of ``bytespider`` or ``Claude-User``, and
counted every UA-less or library client (``httpx``, ``Go-http-client``) as a
person. Every host in the fleet reported those numbers. The lists are gone:
``is_bot`` / ``detect_bot_type`` keep their names for callers and delegate. A
token the registry lacks is a pushback to the package, never a list here —
``tests/test_analytics_classifier.py`` greps this file for the old tokens.

Accuracy notes (these are the things that quietly wreck the numbers):

- **Network machinery is never a visitor.** Any request whose User-Agent
  carries ``lib.constants.INTERNAL_UA_TOKEN`` is dropped in ``track_visit``
  before device detection — the network's internal-traffic contract
  (https://2plot.ai/docs/satellite-analytics). ``/healthz`` is dropped there
  too. Both are write-time rules on purpose; see the comment in ``track_visit``.
- **No raw IP is stored** (1.6.44 item 16, owner decision 2026-09-01). The
  client address is still RESOLVED from the proxy headers, because it is
  needed to tell one visitor from another and because ``remote_addr`` behind
  Cloudflare/Render is the proxy — every visitor would otherwise collapse
  into one. It is then reduced to ``visitor_key``, a keyed one-way hash of
  (address + User-Agent), and the address itself is dropped. Set
  ``ANALYTICS_KEEP_CLIENT_IP=1`` to keep it — the same switch ``record_read``
  has always honoured.
- **Location comes from the edge, never from a lookup.** Cloudflare's
  ``CF-IPCountry`` answers the country; ``CF-IPCity``, ``CF-Region``,
  ``CF-IPLatitude`` and ``CF-IPLongitude`` answer more when the zone's
  "Add visitor location headers" managed transform is on. Whatever ARRIVES
  is stored; whatever does not is absent. There is no third-party lookup and
  no fallback to one: the ip-api.com path was REMOVED at 1.6.44, not
  defaulted off, because a disabled lookup is one environment variable away
  from being an enabled one.
- **Writes are buffered, locked and pruned.** Multiple gunicorn/uvicorn workers
  share this file; without an ``flock`` around the read-modify-write they
  silently overwrite each other's hits. The buffer keeps a docs site from
  rewriting the whole file on every request, and retention keeps it bounded.
"""
import atexit
import hashlib
import hmac
import json
import os
import secrets
import threading
import time
from pathlib import Path
from datetime import datetime, timedelta

from dash_improve_my_llms import classify
from dash_improve_my_llms._ledger import EVENT_FIELDS

try:  # POSIX only — Windows dev boxes just run without the cross-process lock
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None


_REPO_ROOT = Path(__file__).resolve().parent.parent

# How many hits to hold in memory before touching disk, and the longest a hit
# may sit in the buffer. Both are tiny; the point is to turn "rewrite the file
# on every request" into "rewrite it a few times a minute".
FLUSH_EVERY = int(os.getenv("ANALYTICS_FLUSH_EVERY", "10"))
FLUSH_INTERVAL_S = float(os.getenv("ANALYTICS_FLUSH_INTERVAL_S", "30"))

# Retention. The hub keeps the durable history (every rollup we POST rides its
# heartbeat store), so this file only needs enough runway to build a rollup and
# show recent local history.
RETENTION_DAYS = int(os.getenv("ANALYTICS_RETENTION_DAYS", "45"))
MAX_VISITS = int(os.getenv("ANALYTICS_MAX_VISITS", "20000"))

# The read event carries the client address; it is dropped from the stored
# row unless the operator opts in. The row is shown to vendors later (the
# ledger plan's reconciliation) and the package's docstring leaves the
# decision to the app — this is the decision.
KEEP_CLIENT_IP = os.getenv("ANALYTICS_KEEP_CLIENT_IP", "0") == "1"

# The keys a crawler row gains from classify(); a human row never carries
# them, so the v3 rollup sees human rows byte-for-byte as before.
_VENDOR_KEYS = ("vendor_key", "vendor_class", "verified", "lane")

_IP_HEADERS = (
    "cf-connecting-ip",     # Cloudflare
    "true-client-ip",       # Cloudflare Enterprise / Akamai
    "x-real-ip",            # nginx
    "x-forwarded-for",      # everything else (first hop = the client)
)

_PRIVATE_PREFIXES = ('10.', '172.', '192.168.', 'fe80:', 'fc00:', 'fd00:')

# Cloudflare's visitor-location headers. `cf-ipcountry` is on by default;
# the rest arrive only where the zone has "Add visitor location headers"
# enabled (the owner's click, per zone). The read is DEFENSIVE — store what
# arrives, never assume a set — so a host with the transform off records
# country only and a host with it on records more, with no code change and
# no lookup in either case.
_GEO_HEADERS = {
    "cf-ipcountry": "country_code",
    "cf-ipcity": "city",
    "cf-region": "region",
    "cf-iplatitude": "latitude",
    "cf-iplongitude": "longitude",
}

# Which of them this host has actually SEEN, logged once per boot and listed
# additively on /healthz's geo block. A set, because the answer is "which
# ones arrive here", not "how many requests carried them".
_geo_headers_seen: set = set()
_geo_headers_logged = False


def analytics_path() -> Path:
    """Resolve the ledger path (env override, else repo root).

    Absolute on purpose: the old relative default wrote a *different* file
    depending on the process working directory, which split the numbers.
    """
    return Path(os.getenv("TRAFFIC_ANALYTICS_FILE")
                or _REPO_ROOT / "visitor_analytics.json")


def _ledger_persistence_warning() -> None:
    """Loud when the ledger would not survive a deploy (1.6.44 item 22).

    Mirrors `lib.page_visibility._persistence_warning` deliberately — same
    shape, same two failure modes, same place in the boot output — because
    the two stores fail for identical reasons and an operator who has learnt
    to look for one should find the other beside it.

    `analytics_path()` falls back SILENTLY to the repository root, which is
    the container filesystem and is replaced wholesale on every deploy.
    `PAGE_VISIBILITY_FILE` has warned about exactly this since the pilot
    host lost its toggles twice; the ledger, which is the more expensive
    thing to lose, said nothing (note 96: muischeduler, email, emojimart).

    Pairs with item 20: this says it once at boot, and `/healthz`'s
    `ledger.persistent` says it continuously to anyone who asks.
    """
    configured = os.environ.get("TRAFFIC_ANALYTICS_FILE")
    if not configured:
        print(
            f"[analytics] WARNING: TRAFFIC_ANALYTICS_FILE unset — ledger at "
            f"{analytics_path()} is on the container filesystem and will not "
            "survive a deploy. Set TRAFFIC_ANALYTICS_FILE=/var/data/"
            "visitor_analytics.json on the service (render.yaml declares the "
            "disk, but only a Blueprint sync or a dashboard add makes it "
            "live).",
            flush=True,
        )
        return
    path = Path(configured)
    if str(path).startswith("/var/"):
        anchor = (Path("/") / path.parts[1] / path.parts[2]
                  if len(path.parts) > 2 else path.parent)
        if not os.path.ismount(str(anchor)):
            print(
                f"[analytics] WARNING: {anchor} is not a mounted disk on this "
                "instance — the ledger will vanish on the next deploy. An app "
                "can mkdir a path under /var and everything works until the "
                "deploy that replaces the filesystem.",
                flush=True,
            )


def _lower_headers(headers) -> dict:
    """Normalise any header mapping (Flask, Starlette, dict) to lowercase."""
    if not headers:
        return {}
    try:
        return {str(k).lower(): v for k, v in headers.items()}
    except Exception:
        return {}


def client_ip(headers=None, fallback=None):
    """The real client address, reading proxy headers before ``remote_addr``."""
    lc = _lower_headers(headers)
    for name in _IP_HEADERS:
        raw = lc.get(name)
        if not raw:
            continue
        # X-Forwarded-For is "client, proxy1, proxy2" — the client is first.
        ip = str(raw).split(",")[0].strip()
        if ip:
            return ip
    return fallback


def header_country(headers=None):
    """ISO country code from Cloudflare's ``CF-IPCountry``, if present.

    ``XX`` (unknown) and ``T1`` (Tor) are not countries — treated as absent.
    """
    cc = (_lower_headers(headers).get("cf-ipcountry") or "").strip().upper()
    return cc if cc and cc not in ("XX", "T1") else None


def header_geo(headers=None) -> dict:
    """Everything the EDGE told us about where this request came from.

    Defensive by construction (1.6.44 item 16): each header is read
    independently and a missing one is simply absent from the result. A host
    whose zone has the visitor-location transform off records country only; a
    host with it on records city, region and coordinates too. Neither branch
    reaches the network, and there is no configuration that makes it.
    """
    global _geo_headers_logged

    lc = _lower_headers(headers)
    out: dict = {}
    for header, field in _GEO_HEADERS.items():
        raw = lc.get(header)
        if raw is None:
            continue
        value = str(raw).strip()
        if not value:
            continue
        _geo_headers_seen.add(header)
        if field == "country_code":
            value = value.upper()
            if value in ("XX", "T1"):    # unknown, Tor — not countries
                continue
            out["country"] = value
        out[field] = value

    if out and not _geo_headers_logged:
        _geo_headers_logged = True
        print(f"[analytics] visitor-location headers seen: "
              f"{', '.join(sorted(_geo_headers_seen))}", flush=True)
    return out


def geo_headers_seen() -> list:
    """The visitor-location headers this process has received, sorted.

    Read by ``/healthz``'s geo block so the answer to "is the transform on
    for this zone?" is visible without reading logs.
    """
    return sorted(_geo_headers_seen)


def _visitor_salt() -> bytes:
    """The key for ``visitor_key``'s one-way hash.

    ``ANALYTICS_VISITOR_SALT`` when set. Otherwise a random salt generated
    once and kept beside the ledger — which means it survives restarts
    exactly where the ledger does. On an ephemeral container filesystem it
    rotates on every deploy, and that is a property rather than a bug: the
    hashes stop being linkable across deploys, and the host that wanted
    them linkable was told to mount a disk (item 22).
    """
    env = os.getenv("ANALYTICS_VISITOR_SALT")
    if env:
        return env.encode()
    path = analytics_path().parent / ".visitor_salt"
    try:
        if path.exists():
            return path.read_bytes()
        salt = secrets.token_bytes(32)
        path.write_bytes(salt)
        return salt
    except Exception:
        # Unwritable directory: fall back to a process-lifetime salt rather
        # than to no salt. An unsalted hash of an IP is an IP.
        global _fallback_salt
        if _fallback_salt is None:
            _fallback_salt = secrets.token_bytes(32)
        return _fallback_salt


_fallback_salt = None


def visitor_key(ip_address, user_agent) -> str:
    """A keyed one-way hash identifying a visitor without storing them.

    HMAC, not a bare digest: the IPv4 space is small enough to enumerate, so
    an unkeyed hash of an address is a reversible encoding of the address.
    Truncated to 16 hex characters — enough to separate visitors in a day's
    ledger, not enough to be a durable identifier.
    """
    material = f"{ip_address or '?'}|{user_agent or '?'}".encode()
    return hmac.new(_visitor_salt(), material, hashlib.sha256).hexdigest()[:16]


# The ip-api.com lookup lived here from the first version until 1.6.44 and
# is REMOVED, not defaulted off (item 16, owner: "I'm not a fan … I don't
# think we are gaining much"). It sent a visitor's IP address to a third
# party on a background thread, cached the answer, and backfilled the row at
# flush; `ANALYTICS_GEO_LOOKUP=0` turned it off and one environment variable
# turned it back on. Location now comes from the edge headers this app
# already receives, or it is absent — see `header_geo`.
#
# Removed with it: `_geo_cache`, `_geo_inflight`, `_geo_lock`, `geo_for`,
# `_geolocate`, `AnalyticsTracker.get_geolocation`, the `_geo_pending`
# marker and the flush-time backfill that resolved it. The `requests`
# import went too — this module no longer makes an outbound request of any
# kind, which is the property worth keeping, and the one a reviewer can
# check in one grep.


class AnalyticsTracker:
    """Track visitor analytics to JSON file."""

    def __init__(self, data_file=None):
        self._data_file = Path(data_file) if data_file else None
        self._buffer = []
        self._reads_buffer = []
        self._buffer_lock = threading.Lock()
        self._last_flush = time.time()
        atexit.register(self.flush)

    @property
    def data_file(self) -> Path:
        return self._data_file or analytics_path()

    def _ensure_file_exists(self):
        """Create analytics file if it doesn't exist."""
        if not self.data_file.exists():
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            self.data_file.write_text(json.dumps({
                "visits": [],
                "reads": [],
                "stats": {
                    "desktop": 0,
                    "mobile": 0,
                    "tablet": 0,
                    "bot": 0,
                    "total": 0
                }
            }, indent=2))

    def detect_device_type(self, user_agent, classification=None):
        """Detect device type from user agent string.

        ``classification`` is an already-computed ``classify()`` result so a
        caller that needs the vendor keys too classifies exactly once.
        """
        # Bots first — including the EMPTY User-Agent, which the package puts
        # on the crawler lane (no browser sends none) and this method used to
        # file as a desktop human.
        c = classification if classification is not None else _classify(user_agent)
        if c["lane"] == "crawler":
            return "bot"

        user_agent = (user_agent or "").lower()

        # Check for tablet before mobile — iPads and most Android tablets also
        # carry a mobile token, so the mobile test would swallow them.
        if any(tablet in user_agent for tablet in ['ipad', 'tablet', 'kindle', 'silk']):
            return "tablet"

        if any(mobile in user_agent for mobile in ['mobile', 'android', 'iphone', 'ipod', 'blackberry', 'windows phone']):
            return "mobile"

        return "desktop"

    def is_bot(self, user_agent, client_ip=None):
        """Is this request on the crawler lane? Delegates to the package.

        Kept by name for callers and forks' tests; the body is the one
        classifier. Note the contract change from the list this replaced:
        an absent UA is a bot now, not a desktop visitor.
        """
        return _classify(user_agent, client_ip)["lane"] == "crawler"

    def detect_bot_type(self, user_agent, client_ip=None):
        """``training`` / ``search`` / ``traditional`` / ``unknown``, per the
        package's vendor registry — the same buckets robots.txt is rendered
        from, so what the site SAYS about a vendor and what it COUNTS agree."""
        return _classify(user_agent, client_ip)["bot_type"] or "unknown"

    def track_visit(self, path, user_agent, ip_address=None, headers=None):
        """Track a visitor.

        ``headers`` is optional but strongly recommended — it's what makes the
        client IP and country correct behind a proxy. See ``client_ip``.
        """
        # --- The network's internal-traffic contract, applied at WRITE time --
        #
        # https://2plot.ai/docs/satellite-analytics, "Internal traffic": a
        # request carrying INTERNAL_UA_TOKEN is 2plot machinery talking to
        # itself and is counted nowhere. This has to happen HERE, before
        # `detect_device_type`, and not in lib/traffic_rollup's read-time
        # filter, for two reasons:
        #
        #   1. classification would run first, and the health sweep and smoke
        #      batteries look like bots — they would land in `bot_hits` and be
        #      reported to the hub as crawler interest in these docs;
        #   2. the ledger is what a person reads on a local analytics view. A
        #      row that exists but is filtered on the way out is still a row
        #      somebody has to know to discount.
        #
        # The token is matched case-insensitively so a caller may capitalise
        # its suffix however it likes.
        from lib.constants import INTERNAL_UA_TOKEN

        if INTERNAL_UA_TOKEN in (user_agent or "").lower():
            return

        # Skip internal Dash paths and static assets. `/healthz` and `/health`
        # are here too: the hub sweeps /healthz hourly and Render's own probe
        # hits it far more often than that, so storing it turns the ledger into
        # a record of monitoring. lib/traffic_rollup also drops it at read time
        # — that stays, for ledgers written before this rule existed.
        skip_paths = [
            '.css', '.js', '.png', '.jpg', '.ico', '.svg', '.woff', '.woff2', '.ttf', '.eot',
            '_dash', '_reload-hash', 'favicon', '/_dash-update-component',
            '/_dash-layout', '/_dash-dependencies', '/_dash-component-suites',
            '/assets/', '/healthz', '/health', '[]'  # Also skip malformed paths
        ]
        if any(skip in path for skip in skip_paths):
            return

        # Only track valid paths that start with /
        if not path or not path.startswith('/') or path.startswith('//'):
            return

        # Resolve the REAL address first: `verified` is computed against the
        # client, and behind Cloudflare/Render `ip_address` is the proxy.
        ip_address = client_ip(headers, ip_address)

        # Classify exactly once per request — lane, bucket and vendor come
        # from the same call, so a row can never disagree with itself.
        c = _classify(user_agent, ip_address)
        device_type = self.detect_device_type(user_agent, classification=c)

        visit_data = {
            "timestamp": datetime.now().isoformat(),
            "path": path,
            "device_type": device_type,
            "user_agent": user_agent or "Unknown",
        }

        # Crawler rows carry the vendor identity; human rows are unchanged
        # byte-for-byte (the v3 rollup's tests pin that shape).
        if device_type == "bot":
            visit_data["bot_type"] = c["bot_type"] or "unknown"
            for key in _VENDOR_KEYS:
                visit_data[key] = c.get(key)

        # The address is resolved (above) so one visitor can be told from
        # another, then REDUCED. `visitor_key` is what the ledger keeps; the
        # address itself is kept only where the operator opted in.
        visit_data["visitor_key"] = visitor_key(ip_address, user_agent)
        if ip_address and KEEP_CLIENT_IP:
            visit_data["ip_address"] = ip_address

        # Location from the edge, or not at all. No lookup, no pending
        # marker, no backfill — whatever the headers carried is what the row
        # gets, and a host whose zone sends only the country records only the
        # country.
        location = header_geo(headers)
        if location:
            visit_data["location"] = location

        self._enqueue(self._buffer, visit_data)

    def record_read(self, event):
        """Keep one read event from dash-improve-my-llms' ``on_document_read``.

        Registered once in ``run.py``. The package hands over every key in
        ``_ledger.EVENT_FIELDS`` for each corpus document it served — tier,
        lane, vendor, verified, policy, verdict, status, bytes — and does no
        I/O of its own. This is where the row is kept: the ``reads`` table of
        the same ledger, same buffer discipline, same lock, same retention.

        Called synchronously on the request path by the package, which also
        catches anything raised here (fail-open, warned once). Keep it cheap:
        it appends; the flush does the disk work.

        ``client_ip`` is dropped unless ``ANALYTICS_KEEP_CLIENT_IP=1``.
        """
        if not isinstance(event, dict):
            return
        # DROP FIRST, before anything else is read (pipdocs, 2026-08-31 —
        # measured on this tree: 69 rows where 67 were real). `track_visit`
        # has dropped INTERNAL_UA_TOKEN since the internal-traffic contract
        # and this hook never learned to, so the network's own probes — the
        # hub's health sweep, every satellite's link audit — landed in the
        # `reads` table and became the busiest "vendor" on every board in
        # the fleet. "Counted nowhere" has to include the read table, or the
        # contract is only half kept.
        from lib.constants import INTERNAL_UA_TOKEN

        if INTERNAL_UA_TOKEN in (event.get("ua") or "").lower():
            return
        row = {k: event.get(k) for k in EVENT_FIELDS}
        if not KEEP_CLIENT_IP:
            row.pop("client_ip", None)
        row["kind"] = "read"
        self._enqueue(self._reads_buffer, row)

    def _enqueue(self, buffer, row):
        with self._buffer_lock:
            buffer.append(row)
            pending = len(self._buffer) + len(self._reads_buffer)
            due = (pending >= FLUSH_EVERY
                   or (time.time() - self._last_flush) >= FLUSH_INTERVAL_S)
        if due:
            self.flush()

    # ------------------------------------------------------------------ disk --

    def flush(self):
        """Write buffered hits to disk under a cross-process lock.

        Safe to call at any time (the satellite reporter calls it before
        building a rollup so the numbers include the current minute).
        """
        with self._buffer_lock:
            pending, self._buffer = self._buffer, []
            reads, self._reads_buffer = self._reads_buffer, []
            self._last_flush = time.time()
        if not pending and not reads:
            return
        try:
            self._write(pending, reads)
        except Exception:
            # Never lose the app over analytics; put the hits back so the next
            # flush can retry them.
            with self._buffer_lock:
                self._buffer = pending + self._buffer
                self._reads_buffer = reads + self._reads_buffer

    def _write(self, pending, reads=()):
        self._ensure_file_exists()
        path = self.data_file
        lock_path = path.with_suffix(path.suffix + ".lock")
        lock_fh = open(lock_path, "a+") if fcntl else None
        try:
            if lock_fh:
                fcntl.flock(lock_fh, fcntl.LOCK_EX)
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                if not isinstance(data, dict):
                    raise ValueError("ledger is not an object")
            except Exception:
                data = {"visits": [], "reads": [],
                        "stats": {"desktop": 0, "mobile": 0,
                                  "tablet": 0, "bot": 0, "total": 0}}

            visits = data.setdefault("visits", [])
            # A ledger written before 1.6.34 has no `reads`; absence is empty.
            read_rows = data.setdefault("reads", [])
            stats = data.setdefault("stats", {})
            # Internal markers stay on the buffered copy (for a retry) and
            # never reach the ledger.
            visits.extend(dict(v) for v in pending)
            for v in pending:
                dt = v["device_type"]
                stats[dt] = stats.get(dt, 0) + 1
                stats["total"] = stats.get("total", 0) + 1

            data["visits"] = _prune(visits)
            read_rows.extend(reads)
            # cap=False: reads keep every row inside the retention window
            # (item 21). The count cap is the visits table's rule.
            data["reads"] = _prune(read_rows, stamp=_read_stamp, cap=False)

            # Atomic replace: a crash mid-write can't leave a truncated ledger.
            tmp = path.with_suffix(path.suffix + ".tmp")
            with open(tmp, 'w') as f:
                json.dump(data, f, indent=2)
            os.replace(tmp, path)
        finally:
            if lock_fh:
                try:
                    fcntl.flock(lock_fh, fcntl.LOCK_UN)
                finally:
                    lock_fh.close()


def _visit_stamp(v):
    return v.get("timestamp") or ""


def _read_stamp(r):
    """Read rows carry the package's epoch ``ts``; compare on the same ISO
    axis the visit rows use so one retention rule covers both tables."""
    ts = r.get("ts")
    try:
        return datetime.fromtimestamp(float(ts)).isoformat()
    except (TypeError, ValueError, OverflowError, OSError):
        return ""


def _prune(rows, stamp=_visit_stamp, cap=True):
    """Drop rows older than the retention window; cap the total only if asked.

    THE COUNT CAP IS FOR `visits` ONLY (1.6.44 item 21; note 94, measured on
    llms, muicharts and pannellum). It applied to BOTH tables, and on a
    corpus served to every crawler in the world the READ table fills fastest
    — so the oldest read rows went first and the ledger ate its own history
    while its retention window said the rows should still be there. A cap
    that silently deletes inside the window is not a cap, it is a different
    retention policy nobody wrote down.

    `reads` prune by DATE only. If the read table grows beyond what a host
    can hold, the answer is a shorter retention window — a number an
    operator sets and can see — not a silent truncation.
    """
    if RETENTION_DAYS > 0:
        cutoff = (datetime.now() - timedelta(days=RETENTION_DAYS)).isoformat()
        rows = [v for v in rows if stamp(v) >= cutoff]
    if cap and MAX_VISITS > 0 and len(rows) > MAX_VISITS:
        rows = rows[-MAX_VISITS:]
    return rows


def _vendor_class_from_registry(vendor_key):
    """The package's own registry answer for ``vendor_key``, or None.

    Not a second opinion and not a local table — ``get_vendor()`` reads the
    same registry ``classify()`` does. It exists only for the version window
    where the event carries a vendor and no class.
    """
    if not vendor_key:
        return None
    try:
        from dash_improve_my_llms.vendors import get_vendor

        vendor = get_vendor(vendor_key)
        return getattr(vendor, "cls", None) if vendor else None
    except Exception:
        return None


def _classify(user_agent, client_ip=None):
    """The one classifier, made total: never raises, always has ``lane``.

    PREFER, THEN DERIVE (1.6.44 item 8). dash-improve-my-llms 2.9.x puts
    ``vendor_class`` on the classification itself. A fork that computes the
    class unconditionally OVERWRITES the package's answer with its own, and
    the two disagree the moment the registry learns a vendor the fork's table
    does not have — which is the whole reason there is one classifier. So the
    package's value is taken whenever it is present, and the registry is
    consulted only where it is absent (a floor below 2.9, or a vendor the
    classifier matched without a class). Never a hand-written map.
    """
    try:
        c = classify(user_agent or "", client_ip)
    except Exception:
        c = {}
    vendor_key = c.get("vendor_key")
    vendor_class = c.get("vendor_class")
    if vendor_class is None:
        vendor_class = _vendor_class_from_registry(vendor_key)
    return {
        "lane": c.get("lane") or "browser",
        "bot_type": c.get("bot_type"),
        "vendor_key": vendor_key,
        "vendor_class": vendor_class,
        "verified": c.get("verified") or "n/a",
    }


_ledger_persistence_warning()

# Global tracker instance
tracker = AnalyticsTracker()
