from dash import html, callback, Input, Output, State, ALL
import dash_mantine_components as dmc
from dash_iconify import DashIconify

# Form validation example
component = html.Div([
    dmc.Title("User Registration Form", order=4, mb=10),
    dmc.Stack([
        dmc.TextInput(
            label="Full Name",
            placeholder="Enter your full name",
            id="form-name",
            required=True,
            leftSection=DashIconify(icon="mdi:account")
        ),
        dmc.TextInput(
            label="Email",
            placeholder="your.email@example.com",
            id="form-email",
            required=True,
            leftSection=DashIconify(icon="mdi:email")
        ),
        dmc.PasswordInput(
            label="Password",
            placeholder="Enter password",
            id="form-password",
            required=True,
            leftSection=DashIconify(icon="mdi:lock")
        ),
        dmc.Select(
            label="Country",
            placeholder="Select your country",
            id="form-country",
            data=[
                {"label": "United States", "value": "us"},
                {"label": "United Kingdom", "value": "uk"},
                {"label": "Canada", "value": "ca"},
                {"label": "Australia", "value": "au"},
                {"label": "Germany", "value": "de"},
            ],
            leftSection=DashIconify(icon="mdi:earth")
        ),
        dmc.Checkbox(
            label="I agree to the terms and conditions",
            id="form-terms",
        ),
        dmc.Group([
            dmc.Button(
                "Submit",
                id="form-submit-btn",
                variant="filled",
                color="teal",
                fullWidth=True
            ),
        ]),
        dmc.Paper(
            id="form-output",
            p="md",
            withBorder=True,
            radius="md",
            style={"display": "none"}
        )
    ], gap="sm")
])


@callback(
    Output("form-output", "children"),
    Output("form-output", "style"),
    Input("form-submit-btn", "n_clicks"),
    State("form-name", "value"),
    State("form-email", "value"),
    State("form-password", "value"),
    State("form-country", "value"),
    State("form-terms", "checked"),
    prevent_initial_call=True
)
def validate_form(n_clicks, name, email, password, country, terms):
    errors = []

    if not name or len(name.strip()) < 2:
        errors.append("Name must be at least 2 characters")

    if not email or "@" not in email:
        errors.append("Please enter a valid email")

    if not password or len(password) < 6:
        errors.append("Password must be at least 6 characters")

    if not country:
        errors.append("Please select a country")

    if not terms:
        errors.append("You must agree to the terms and conditions")

    if errors:
        return [
            dmc.Alert(
                title="Validation Errors",
                color="red",
                children=[
                    html.Ul([html.Li(error) for error in errors])
                ]
            )
        ], {"display": "block"}

    return [
        dmc.Alert(
            title="Success!",
            color="teal",
            children=f"Welcome, {name}! Your account has been created."
        )
    ], {"display": "block"}
