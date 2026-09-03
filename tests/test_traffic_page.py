"""/admin/traffic — the host's own ledger, behind the control board's gate."""

from __future__ import annotations

import importlib
import json
from datetime import date, datetime

import pytest

from conftest import CRAWLER_UA

from dash_improve_my_llms._ledger import EVENT_FIELDS

TODAY = date(2026, 8, 29)
YESTERDAY = date(2026, 8, 28)


def _page():
    import pages.traffic as traffic
    return importlib.reload(traffic)


def _read(day, vendor_key, verified, path="/llms.txt", tier="index", nbytes=500,
          verdict="served", status=200):
    ev = {k: None for k in EVENT_FIELDS}
    ev.update(ts=datetime(day.year, day.month, day.day, 12).timestamp(),
              path=path, method="GET", tier=tier, lane="crawler",
              bot_type="training", vendor_key=vendor_key, verified=verified,
              verdict=verdict, status=status, bytes=nbytes, ua="ua", kind="read")
    ev.pop("client_ip")
    return ev


@pytest.fixture
def fixture_ledger(tmp_path, monkeypatch):
    """3 vendors × 2 days, with distinct counts so a cell cannot pass by luck."""
    reads = (
        [_read(TODAY, "gptbot", "unverified")] * 5
        + [_read(YESTERDAY, "gptbot", "unverified")] * 2
        + [_read(TODAY, "claudebot", "n/a", path="/backends/llms.txt", tier="page")] * 3
        + [_read(YESTERDAY, "claudebot", "n/a")] * 1
        + [_read(TODAY, "googlebot", "verified", path="/sitemap.xml", tier="sitemap")] * 7
        + [_read(YESTERDAY, "googlebot", "verified")] * 4
    )
    p = tmp_path / "visitor_analytics.json"
    p.write_text(json.dumps({"visits": [], "reads": reads}))
    monkeypatch.setenv("TRAFFIC_ANALYTICS_FILE", str(p))
    return p


def test_the_page_is_hidden_from_every_machine_surface(app_module, client):
    from dash_improve_my_llms import is_hidden

    assert is_hidden("/admin/traffic")
    assert "/admin/traffic</loc>" not in client.get("/sitemap.xml").text
    assert "/admin/traffic" not in client.get("/llms.txt").text
    # and a crawler asking for it gets the package's 404, like the board
    assert client.get("/admin/traffic", user_agent=CRAWLER_UA).status == \
        client.get("/admin/control-board", user_agent=CRAWLER_UA).status


def test_anonymous_is_denied_exactly_like_the_control_board(app_module, monkeypatch):
    import pages.control_board as board
    traffic = _page()
    monkeypatch.delenv("ALLOW_UNGATED_ADMIN", raising=False)
    ours, theirs = str(traffic.layout()), str(board.layout())
    assert "traffic-day" not in ours
    assert "404" in ours and "not currently published" in ours
    assert ours == theirs, "the two admin pages must fail closed identically"


def test_the_tables_render_the_fixture_numbers(app_module, monkeypatch, fixture_ledger):
    traffic = _page()
    monkeypatch.setenv("ALLOW_UNGATED_ADMIN", "1")
    from lib.traffic_rollup import load_reads

    reads = load_reads()
    days = traffic._window(TODAY)
    rows, cells, nbytes = traffic.vendor_by_day(reads, days)
    assert rows == [("googlebot", "verified"), ("gptbot", "unverified"),
                    ("claudebot", "n/a")]
    assert cells[(("googlebot", "verified"), TODAY)] == 7
    assert cells[(("googlebot", "verified"), YESTERDAY)] == 4
    assert cells[(("gptbot", "unverified"), TODAY)] == 5
    assert cells[(("gptbot", "unverified"), YESTERDAY)] == 2
    assert cells[(("claudebot", "n/a"), TODAY)] == 3
    assert cells[(("claudebot", "n/a"), YESTERDAY)] == 1
    assert nbytes[("googlebot", "verified")] == 11 * 500

    rendered = str(traffic._build_page(TODAY, reads))
    for cell in ("googlebot · verified", "gptbot · unverified", "claudebot · n/a",
                 "'7'", "'5'", "'3'", "'4'", "'2'", "'1'"):
        assert cell in rendered, cell
    # vendor → tier for TODAY
    day = str(traffic.day_view(TODAY, reads))
    assert "traffic-vendor-tier" in day
    assert "/backends/llms.txt" in day and "/sitemap.xml" in day
    # the verified legend, so the owner reads n/a as a vendor property
    assert "Anthropic does not" in rendered
    assert "traffic-day" in rendered


def test_the_gate_opens_locally_with_the_dev_override(app_module, monkeypatch, fixture_ledger):
    traffic = _page()
    monkeypatch.setenv("ALLOW_UNGATED_ADMIN", "1")
    assert "traffic-day" in str(traffic.layout())


# ------------------------------------------- 1.6.44 item 3: the verdict column --


def _hidden_admin_path(app_module) -> str:
    """A real mark_hidden path from the registry, not a literal.

    A hardcoded `/admin/traffic` would keep passing on a fork that renamed
    or moved its admin pages, which is the drift note 74 exists for.
    """
    import dash

    admin = sorted(
        p["path"] for p in dash.page_registry.values()
        if p["path"].startswith("/admin/")
    )
    assert admin, "no admin pages registered — this pin would be vacuous"
    return f"{admin[0]}/llms.txt"


def test_a_denied_read_is_labelled_and_not_counted_among_serves(app_module):
    """Item 3's acceptance: the board LABELS enforcement, never hides it.

    A mark_hidden path fetched by a crawler is REFUSED, and that refusal is
    the only visible evidence the delisting works. So it must appear as its
    own row carrying its verdict, and it must not be added to serves — a
    board that folds them reports enforcement as traffic.
    """
    traffic = _page()
    hidden = _hidden_admin_path(app_module)

    reads_day = (
        [_read(TODAY, "gptbot", "unverified", path="/llms.txt")] * 4
        + [_read(TODAY, "gptbot", "unverified", path=hidden,
                 verdict="denied", status=404)] * 2
    )

    served, not_served = traffic.serve_counts(reads_day)
    assert (served, not_served) == (4, 2), (served, not_served)

    rows = traffic.top_paths(reads_day)
    cells = {(path, verdict): hits for _, _, paths in rows for path, verdict, hits in paths}
    assert cells[(hidden, "denied")] == 2, cells
    assert cells[("/llms.txt", "served")] == 4, cells
    # The same path under two verdicts stays TWO rows, which is the whole
    # point of grouping on (path, verdict) rather than on path.
    both = (
        [_read(TODAY, "gptbot", "unverified", path=hidden)]
        + [_read(TODAY, "gptbot", "unverified", path=hidden, verdict="denied")]
    )
    split = {(p, v) for _, _, paths in traffic.top_paths(both) for p, v, _ in paths}
    assert split == {(hidden, "served"), (hidden, "denied")}, split


def test_the_verdict_reaches_the_rendered_table_as_a_word(app_module):
    """Labelled, not colour-coded. Colour alone puts the meaning in a
    channel a screen reader and a colour-blind reader do not get."""
    traffic = _page()
    hidden = _hidden_admin_path(app_module)
    rendered = str(traffic.top_paths_block(
        [_read(TODAY, "gptbot", "unverified", path=hidden, verdict="denied")]
    ))
    assert "denied" in rendered, "the verdict never reached the table"
    assert "verdict" in rendered, "the column header is missing"


def test_the_rollup_vendors_shape_is_unchanged_by_item_3(app_module):
    """Item 3 changes the BOARD, not the payload — the hub side is its own
    drop, so `vendors[]` keys must not move here."""
    from lib.traffic_rollup import vendor_rows

    rows = vendor_rows([_read(TODAY, "gptbot", "unverified", verdict="denied")])
    assert rows, "vendor_rows returned nothing to check"
    assert "verdict" not in rows[0], (
        "item 3 leaked a verdict key into the rollup's vendor rows; the hub "
        "contract is a separate drop"
    )
