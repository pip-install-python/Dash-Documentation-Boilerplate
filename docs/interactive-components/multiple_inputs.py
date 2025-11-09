from dash import html, callback, Input, Output
import dash_mantine_components as dmc

component = html.Div([
    dmc.Title("Multiple Inputs Example", order=4, mb=10),
    dmc.Text("Enter two numbers to see their sum:", mb=10),

    dmc.Stack([
        dmc.NumberInput(
            label="First Number",
            id="num1-input",
            value=0,
            min=0,
            max=100
        ),
        dmc.NumberInput(
            label="Second Number",
            id="num2-input",
            value=0,
            min=0,
            max=100
        ),
        dmc.Paper([
            dmc.Text("Result:", size="sm", c="dimmed", mb=5),
            dmc.Title(
                "0",
                id="sum-output",
                order=3,
                c="teal"
            )
        ], p="md", withBorder=True, radius="md")
    ], gap="sm")
])


@callback(
    Output("sum-output", "children"),
    Input("num1-input", "value"),
    Input("num2-input", "value")
)
def calculate_sum(num1, num2):
    num1 = num1 or 0
    num2 = num2 or 0
    total = num1 + num2
    return f"{num1} + {num2} = {total}"
