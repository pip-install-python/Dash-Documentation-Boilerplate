"""
Live API browser for the FastAPI surface.

Hits /healthz, /api/backend, /api/pages from the browser via fetch() and
renders the JSON. Works on any backend (the routes also exist on Flask via
the Flask-side llms.txt etc), but only FastAPI auto-populates /docs.
"""
from dash import html, Input, Output, State, ALL, clientside_callback
import dash_mantine_components as dmc
from dash_iconify import DashIconify


def _endpoint_button(label: str, path: str, color: str) -> dmc.Button:
    return dmc.Button(
        label,
        id={"type": "fas-explorer-btn", "path": path},
        leftSection=DashIconify(icon="mdi:arrow-right-circle-outline", width=16),
        variant="light",
        color=color,
        size="sm",
    )


component = html.Div([
    dmc.Title("Live OpenAPI surface explorer", order=4, mb="xs"),
    dmc.Text(
        "Click any endpoint to GET it from the browser and render the response. "
        "On the FastAPI backend these routes are declared with typed Pydantic models, "
        "so they also appear automatically at /docs and /redoc.",
        size="sm",
        c="dimmed",
        mb="md",
    ),
    dmc.Group(
        [
            _endpoint_button("GET /healthz", "/healthz", "teal"),
            _endpoint_button("GET /api/backend", "/api/backend", "cyan"),
            _endpoint_button("GET /api/pages", "/api/pages", "violet"),
            dmc.Anchor(
                dmc.Button(
                    "Open Swagger UI",
                    leftSection=DashIconify(icon="logos:swagger", width=16),
                    variant="outline",
                    color="gray",
                    size="sm",
                ),
                href="/docs",
                target="_blank",
                underline=False,
            ),
        ],
        gap="sm",
        mb="md",
    ),
    dmc.Paper(
        [
            dmc.Group(
                [
                    DashIconify(icon="mdi:code-json", width=16),
                    dmc.Text("Response", size="sm", fw=600),
                    dmc.Badge(
                        "—",
                        id="fas-explorer-status",
                        color="gray",
                        variant="light",
                        size="sm",
                    ),
                    dmc.Text("", id="fas-explorer-timing", size="xs", c="dimmed"),
                ],
                gap="sm",
                mb="xs",
            ),
            html.Pre(
                "Click an endpoint to see its JSON response here.",
                id="fas-explorer-output",
                style={
                    "fontFamily": "ui-monospace, SFMono-Regular, Menlo, monospace",
                    "fontSize": "0.8rem",
                    "lineHeight": 1.5,
                    "margin": 0,
                    "whiteSpace": "pre-wrap",
                    "wordBreak": "break-word",
                    "maxHeight": "320px",
                    "overflow": "auto",
                },
            ),
        ],
        p="md",
        withBorder=True,
        radius="md",
    ),
])


# Clientside fetch — keeps the demo backend-agnostic and avoids round-tripping
# through Dash's own callback transport just to hit a sibling HTTP route.
clientside_callback(
    """
    async function(n_clicks_list, ids) {
        const ctx = window.dash_clientside.callback_context;
        if (!ctx.triggered.length || ctx.triggered[0].value == null) {
            return window.dash_clientside.no_update;
        }
        const triggered = JSON.parse(ctx.triggered[0].prop_id.split('.')[0]);
        const path = triggered.path;
        const t0 = performance.now();
        let status, body;
        try {
            const r = await fetch(path, {headers: {'Accept': 'application/json'}});
            status = r.status;
            const text = await r.text();
            try {
                body = JSON.stringify(JSON.parse(text), null, 2);
            } catch (e) {
                body = text;
            }
        } catch (e) {
            return [`Network error: ${e.message}`, 'ERROR', 'red', ''];
        }
        const ms = (performance.now() - t0).toFixed(1);
        const color = status === 200 ? 'teal' : (status < 400 ? 'cyan' : 'red');
        return [body, String(status), color, `GET ${path} • ${ms} ms`];
    }
    """,
    [
        Output("fas-explorer-output", "children"),
        Output("fas-explorer-status", "children"),
        Output("fas-explorer-status", "color"),
        Output("fas-explorer-timing", "children"),
    ],
    Input({"type": "fas-explorer-btn", "path": ALL}, "n_clicks"),
    State({"type": "fas-explorer-btn", "path": ALL}, "id"),
    prevent_initial_call=True,
)
