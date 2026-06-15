"""
Sync vs async callback comparison.

Both callbacks do "3 × 500ms of I/O." The sync one runs them sequentially via
time.sleep, so it's always ~1500ms. The async one uses asyncio.gather, so it
fans out to ~500ms on any backend that runs the asyncio loop (FastAPI, Quart,
and Flask via Dash's async-fallback threadpool).

The dramatic difference shows up under load: on FastAPI a single async worker
can handle this concurrently for many users. On Flask each request still ties
up a thread for the duration.
"""
import asyncio
import time

from dash import html, callback, Input, Output
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from lib.backend import get_backend_info


SLEEP_S = 0.5
N_OPS = 3


def _result_card(card_id: str, color: str, kind: str) -> dmc.Paper:
    return dmc.Paper(
        [
            dmc.Group(
                [
                    DashIconify(icon="mdi:timer-outline", width=18),
                    dmc.Text(kind, fw=600, size="sm"),
                    dmc.Badge("idle", id=f"{card_id}-badge", color="gray", variant="light", size="sm"),
                ],
                gap="sm",
                mb="xs",
            ),
            dmc.Text("—", id=f"{card_id}-time", size="xl", fw=700, c=color),
            dmc.Text("Press the button above to run", id=f"{card_id}-detail", size="xs", c="dimmed"),
        ],
        p="md",
        withBorder=True,
        radius="md",
    )


_info = get_backend_info()
_async_native = _info.is_async

component = html.Div([
    dmc.Title("Sync vs async callback timing", order=4, mb="xs"),
    dmc.Text(
        [
            f"Each button runs {N_OPS} simulated I/O operations of {int(SLEEP_S*1000)} ms each. "
            "Sync runs them sequentially; async fans them out with asyncio.gather.",
        ],
        size="sm",
        c="dimmed",
        mb="xs",
    ),
    dmc.Alert(
        f"Active backend: {_info.label}"
        + (" (native async)" if _async_native else " (async callbacks run via threadpool)"),
        icon=DashIconify(icon="mdi:information-outline"),
        color=_info.color,
        variant="light",
        mb="md",
    ),
    dmc.Group(
        [
            dmc.Button(
                "Run sync callback",
                id="fas-async-sync-btn",
                leftSection=DashIconify(icon="mdi:play-circle-outline", width=16),
                color="gray",
                variant="light",
            ),
            dmc.Button(
                "Run async callback",
                id="fas-async-async-btn",
                leftSection=DashIconify(icon="mdi:rocket-launch-outline", width=16),
                color="teal",
            ),
        ],
        gap="sm",
        mb="md",
    ),
    dmc.SimpleGrid(
        [
            _result_card("fas-async-sync", "gray", "Sync (time.sleep ×3)"),
            _result_card("fas-async-async", "teal", "Async (asyncio.gather ×3)"),
        ],
        cols=2,
    ),
])


@callback(
    Output("fas-async-sync-time", "children"),
    Output("fas-async-sync-detail", "children"),
    Output("fas-async-sync-badge", "children"),
    Output("fas-async-sync-badge", "color"),
    Input("fas-async-sync-btn", "n_clicks"),
    prevent_initial_call=True,
)
def run_sync(_n):
    t0 = time.perf_counter()
    for _ in range(N_OPS):
        time.sleep(SLEEP_S)
    elapsed = (time.perf_counter() - t0) * 1000
    return (
        f"{elapsed:.0f} ms",
        f"Sequential — {N_OPS} × {int(SLEEP_S*1000)} ms blocking",
        "done",
        "gray",
    )


@callback(
    Output("fas-async-async-time", "children"),
    Output("fas-async-async-detail", "children"),
    Output("fas-async-async-badge", "children"),
    Output("fas-async-async-badge", "color"),
    Input("fas-async-async-btn", "n_clicks"),
    prevent_initial_call=True,
)
async def run_async(_n):
    t0 = time.perf_counter()
    await asyncio.gather(*[asyncio.sleep(SLEEP_S) for _ in range(N_OPS)])
    elapsed = (time.perf_counter() - t0) * 1000
    backend_note = "native async" if _async_native else "threadpool fallback"
    return (
        f"{elapsed:.0f} ms",
        f"Concurrent via asyncio.gather — {backend_note}",
        "done",
        "teal",
    )
