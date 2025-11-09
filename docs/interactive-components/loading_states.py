from dash import html, callback, Input, Output, dcc
import dash_mantine_components as dmc
import time

component = html.Div([
    dmc.Title("Loading States Example", order=4, mb=10),
    dmc.Text(
        "Click the button to trigger a slow operation. Notice the loading indicator while processing.",
        mb=15,
        c="dimmed",
        size="sm"
    ),

    dmc.Button(
        "Process Data",
        id="process-btn",
        variant="filled",
        color="teal",
        mb=15
    ),

    dcc.Loading(
        id="loading-component",
        type="default",
        children=[
            dmc.Paper([
                html.Div(
                    "Click the button to start processing",
                    id="loading-output"
                )
            ], p="md", withBorder=True, radius="md")
        ]
    )
])


@callback(
    Output("loading-output", "children"),
    Input("process-btn", "n_clicks"),
    prevent_initial_call=True
)
def process_data(n_clicks):
    # Simulate a slow operation
    time.sleep(2)

    return html.Div([
        dmc.Alert(
            title="Processing Complete!",
            color="teal",
            children=[
                dmc.Text(f"Successfully processed request #{n_clicks}", mb=5),
                dmc.Text("This simulated a 2-second operation.", size="sm", c="dimmed")
            ]
        )
    ])
