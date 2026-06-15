"""
In-browser concurrency stress test.

Fires N parallel GETs at /healthz from the user's browser using Promise.all,
times each one, and reports wall-clock + percentile stats. ASGI backends
(FastAPI, Quart) handle these concurrently on a single worker; the Flask
default sync worker serializes them, which shows up as p99 latency that
grows roughly linearly with N.

Pure clientside — no extra Python deps, no server callback churn during the
test, no separate process needed.
"""
from dash import html, Input, Output, State, clientside_callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from lib.backend import get_backend_info


_info = get_backend_info()


component = html.Div([
    dmc.Title("Concurrency stress test", order=4, mb="xs"),
    dmc.Text(
        "Fires N concurrent GET /healthz requests directly from your browser. "
        "On the FastAPI backend, wall-clock stays flat (~one request's worth) as N grows. "
        "On Flask with default sync workers, wall-clock grows roughly linearly.",
        size="sm",
        c="dimmed",
        mb="md",
    ),
    dmc.Alert(
        f"Active backend: {_info.label} — "
        + ("expect flat wall-clock as concurrency rises." if _info.is_async
           else "expect wall-clock to climb with concurrency."),
        icon=DashIconify(icon="mdi:speedometer"),
        color=_info.color,
        variant="light",
        mb="md",
    ),

    dmc.Group(
        [
            dmc.NumberInput(
                id="fas-stress-n",
                label="Concurrent requests (N)",
                value=20,
                min=1,
                max=200,
                step=5,
                w=200,
            ),
            dmc.Select(
                id="fas-stress-path",
                label="Endpoint",
                value="/healthz",
                data=[
                    {"label": "/healthz", "value": "/healthz"},
                    {"label": "/api/backend", "value": "/api/backend"},
                    {"label": "/api/pages", "value": "/api/pages"},
                ],
                w=200,
            ),
            dmc.Button(
                "Run",
                id="fas-stress-go",
                leftSection=DashIconify(icon="mdi:play-circle-outline", width=16),
                color="teal",
                mt="lg",
            ),
        ],
        gap="md",
        align="flex-end",
        mb="md",
    ),

    dmc.SimpleGrid(
        [
            dmc.Paper([
                dmc.Text("Wall-clock", size="xs", c="dimmed", tt="uppercase", fw=700),
                dmc.Text("—", id="fas-stress-wall", size="xl", fw=700),
            ], p="sm", withBorder=True, radius="md"),
            dmc.Paper([
                dmc.Text("p50", size="xs", c="dimmed", tt="uppercase", fw=700),
                dmc.Text("—", id="fas-stress-p50", size="xl", fw=700),
            ], p="sm", withBorder=True, radius="md"),
            dmc.Paper([
                dmc.Text("p95", size="xs", c="dimmed", tt="uppercase", fw=700),
                dmc.Text("—", id="fas-stress-p95", size="xl", fw=700),
            ], p="sm", withBorder=True, radius="md"),
            dmc.Paper([
                dmc.Text("p99", size="xs", c="dimmed", tt="uppercase", fw=700),
                dmc.Text("—", id="fas-stress-p99", size="xl", fw=700),
            ], p="sm", withBorder=True, radius="md"),
            dmc.Paper([
                dmc.Text("Throughput", size="xs", c="dimmed", tt="uppercase", fw=700),
                dmc.Text("—", id="fas-stress-rps", size="xl", fw=700),
            ], p="sm", withBorder=True, radius="md"),
            dmc.Paper([
                dmc.Text("Errors", size="xs", c="dimmed", tt="uppercase", fw=700),
                dmc.Text("—", id="fas-stress-errors", size="xl", fw=700),
            ], p="sm", withBorder=True, radius="md"),
        ],
        cols={"base": 2, "sm": 3, "md": 6},
        mb="md",
    ),

    dmc.Paper(
        [
            dmc.Text("Per-request latency histogram", size="xs", c="dimmed", fw=600, mb="xs"),
            html.Pre(
                "Run the stress test to see results.",
                id="fas-stress-hist",
                style={
                    "fontFamily": "ui-monospace, SFMono-Regular, Menlo, monospace",
                    "fontSize": "0.75rem",
                    "lineHeight": 1.4,
                    "margin": 0,
                    "whiteSpace": "pre",
                    "overflow": "auto",
                },
            ),
        ],
        p="md",
        withBorder=True,
        radius="md",
    ),
])


clientside_callback(
    r"""
    async function(n_clicks, n, path) {
        if (!n_clicks) {
            return Array(7).fill(window.dash_clientside.no_update);
        }
        const N = Math.max(1, Math.min(200, n || 20));
        const t0 = performance.now();
        const results = await Promise.all(
            Array.from({length: N}, async () => {
                const s = performance.now();
                try {
                    const r = await fetch(path);
                    await r.text();
                    return {ms: performance.now() - s, ok: r.ok};
                } catch (e) {
                    return {ms: performance.now() - s, ok: false};
                }
            })
        );
        const wall = performance.now() - t0;
        const latencies = results.map(r => r.ms).sort((a, b) => a - b);
        const errors = results.filter(r => !r.ok).length;
        const pct = (p) => latencies[Math.min(latencies.length - 1, Math.floor(p * latencies.length))];
        const fmt = (ms) => ms < 10 ? ms.toFixed(2) + ' ms' : ms.toFixed(0) + ' ms';
        const rps = (N / (wall / 1000)).toFixed(0) + ' rps';

        // Tiny ASCII histogram: 12 buckets across the observed range
        const lo = latencies[0], hi = latencies[latencies.length - 1];
        const span = Math.max(0.1, hi - lo);
        const buckets = 12;
        const counts = new Array(buckets).fill(0);
        for (const ms of latencies) {
            const idx = Math.min(buckets - 1, Math.floor((ms - lo) / span * buckets));
            counts[idx]++;
        }
        const maxCount = Math.max(...counts);
        const bar = (c) => '█'.repeat(Math.round((c / maxCount) * 30));
        const lines = counts.map((c, i) => {
            const a = (lo + (span * i / buckets)).toFixed(1).padStart(7);
            const b = (lo + (span * (i + 1) / buckets)).toFixed(1).padStart(7);
            return `${a}–${b} ms  ${bar(c).padEnd(30)} ${c}`;
        });

        return [
            fmt(wall),
            fmt(pct(0.50)),
            fmt(pct(0.95)),
            fmt(pct(0.99)),
            rps,
            String(errors),
            lines.join('\n'),
        ];
    }
    """,
    [
        Output("fas-stress-wall", "children"),
        Output("fas-stress-p50", "children"),
        Output("fas-stress-p95", "children"),
        Output("fas-stress-p99", "children"),
        Output("fas-stress-rps", "children"),
        Output("fas-stress-errors", "children"),
        Output("fas-stress-hist", "children"),
    ],
    Input("fas-stress-go", "n_clicks"),
    State("fas-stress-n", "value"),
    State("fas-stress-path", "value"),
    prevent_initial_call=True,
)
