from dash import html, callback, Input, Output, State
import dash_mantine_components as dmc
from dash_iconify import DashIconify

# Interactive counter example with callbacks
component = html.Div([
    dmc.Title("Interactive Counter", order=4, mb=10),
    dmc.Group([
        dmc.Button(
            "Increment",
            id="increment-btn",
            variant="filled",
            color="teal",
            leftSection=DashIconify(icon="mdi:plus-circle")
        ),
        dmc.Button(
            "Decrement",
            id="decrement-btn",
            variant="filled",
            color="red",
            leftSection=DashIconify(icon="mdi:minus-circle")
        ),
        dmc.Button(
            "Reset",
            id="reset-btn",
            variant="light",
            color="gray"
        ),
    ], gap="sm", mb=15),
    dmc.Paper([
        dmc.Text("Current Count:", size="sm", c="dimmed"),
        dmc.Title(
            "0",
            id="counter-display",
            order=2,
            c="teal"
        )
    ], p="md", withBorder=True, radius="md")
])


@callback(
    Output("counter-display", "children"),
    Input("increment-btn", "n_clicks"),
    Input("decrement-btn", "n_clicks"),
    Input("reset-btn", "n_clicks"),
    State("counter-display", "children"),
    prevent_initial_call=True
)
def update_counter(inc_clicks, dec_clicks, reset_clicks, current):
    from dash import ctx

    current_value = int(current) if current else 0

    button_id = ctx.triggered_id

    if button_id == "increment-btn":
        return str(current_value + 1)
    elif button_id == "decrement-btn":
        return str(current_value - 1)
    elif button_id == "reset-btn":
        return "0"

    return current
