from dash import html, callback, Input, Output, State
import dash_mantine_components as dmc

component = html.Div([
    dmc.Title("State Management Example", order=4, mb=10),
    dmc.Text(
        "Type your name and click submit. Notice the callback only fires when you click submit, not on every keystroke.",
        mb=10,
        c="dimmed",
        size="sm"
    ),

    dmc.Stack([
        dmc.TextInput(
            label="Enter Your Name",
            placeholder="John Doe",
            id="name-input-state"
        ),
        dmc.Button(
            "Submit",
            id="submit-btn-state",
            variant="filled",
            color="teal"
        ),
        dmc.Paper([
            html.Div(
                "Click submit to see your name",
                id="greeting-output"
            )
        ], p="md", withBorder=True, radius="md")
    ], gap="sm")
])


@callback(
    Output("greeting-output", "children"),
    Input("submit-btn-state", "n_clicks"),
    State("name-input-state", "value"),
    prevent_initial_call=True
)
def display_greeting(n_clicks, name):
    if not name:
        return "Please enter your name above!"

    return html.Div([
        dmc.Text(f"Hello, {name}! 👋", size="lg", fw=500, c="teal"),
        dmc.Text(f"You've submitted this form {n_clicks} time(s).", size="sm", c="dimmed", mt=5)
    ])
