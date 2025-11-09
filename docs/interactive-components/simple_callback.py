from dash import html, callback, Input, Output
import dash_mantine_components as dmc

component = html.Div([
    dmc.Title("Simple Callback Example", order=4, mb=10),
    dmc.Button(
        "Click Me!",
        id="simple-button",
        variant="filled",
        color="teal",
        mb=15
    ),
    dmc.Paper([
        html.Div(
            "Button not clicked yet",
            id="simple-output"
        )
    ], p="md", withBorder=True, radius="md")
])


@callback(
    Output("simple-output", "children"),
    Input("simple-button", "n_clicks"),
    prevent_initial_call=False
)
def update_output(n_clicks):
    if n_clicks is None:
        return "Button not clicked yet"
    return f"Button has been clicked {n_clicks} times!"
