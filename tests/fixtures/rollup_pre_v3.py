"""A v4-WITHOUT-v3 rollup — clerkhook's shape, as a fixture (1.6.36).

The oldest fork's lib/traffic_rollup.py has `load_visits`, `load_reads`,
`vendor_rows`, `daily_rollup(app, day, visits=None, reads=None)` — and NO
`load_agent_hits`, NO `agent_visits` kwarg, NO `bot_visitors` key. The
1.6.34 cargo test reached for all three and would have gone red on
arrival. tests/test_rollup_v4_is_v3_agnostic.py runs the cargo test
against THIS module so that regression is caught in the template.

Deliberately not imported by runtime code. v4 pieces are the template's
own (imported, so the fixture cannot drift from the shape it certifies).
"""
from __future__ import annotations

from datetime import date, datetime

from lib.analytics_tracker import analytics_path
from lib.traffic_rollup import _SKIP, load_reads, vendor_rows, visitor_key  # noqa: F401

__all__ = ["load_visits", "load_reads", "vendor_rows", "daily_rollup"]


def load_visits(path=None):
    import json

    try:
        with open(path or analytics_path()) as f:
            raw = json.load(f).get("visits", [])
    except Exception:
        return []
    out = []
    for v in raw:
        p = v.get("path") or ""
        if not p.startswith("/") or any(s in p for s in _SKIP):
            continue
        try:
            dt = datetime.fromisoformat(v["timestamp"])
        except Exception:
            continue
        v = dict(v)
        v["dt"] = dt.replace(tzinfo=None)
        v["vkey"] = visitor_key(v)
        out.append(v)
    out.sort(key=lambda v: v["dt"])
    return out


def daily_rollup(app: str, day: date | None = None, visits=None,
                 reads=None) -> dict | None:
    """v2 + v4 only. No agent join, no bot_visitors."""
    day = day or datetime.now().date()
    visits = load_visits() if visits is None else visits
    reads = load_reads() if reads is None else reads
    hits = [v for v in visits if v["dt"].date() == day]
    day_reads = [r for r in reads if r["dt"].date() == day]
    if not hits and not day_reads:
        return None
    humans = [v for v in hits if v.get("device_type") != "bot"]
    pages: dict[str, int] = {}
    for v in humans:
        pages[v["path"]] = pages.get(v["path"], 0) + 1
    payload = {
        "app": app,
        "date": day.strftime("%Y-%m-%d"),
        "human_hits": len(humans),
        "bot_hits": len(hits) - len(humans),
        "visitors": len({v["vkey"] for v in humans}),
        "sessions": 0,
        "pages": [{"path": p, "hits": n} for p, n in sorted(pages.items(), key=lambda kv: -kv[1])[:20]],
        "countries": {},
    }
    if day_reads:
        vendors = vendor_rows(day_reads)
        payload["vendors"] = vendors
        payload["reads"] = sum(v["hits"] for v in vendors)
    return payload
