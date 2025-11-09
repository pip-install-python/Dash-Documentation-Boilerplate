from dash import html, callback, Input, Output, State, ALL, MATCH
import dash_mantine_components as dmc
from dash_iconify import DashIconify

component = html.Div([
    dmc.Title("Pattern Matching Callbacks", order=4, mb=10),
    dmc.Text("Click 'Add Item' to dynamically create new inputs with pattern-matching callbacks.", mb=15, c="dimmed", size="sm"),

    dmc.Button(
        "Add Item",
        id="add-item-btn",
        variant="filled",
        color="teal",
        leftSection=DashIconify(icon="mdi:plus"),
        mb=15
    ),

    html.Div(id="items-container"),

    dmc.Paper([
        dmc.Text("Total of all items:", size="sm", c="dimmed", mb=5),
        dmc.Title("0", id="total-sum", order=3, c="teal")
    ], p="md", withBorder=True, radius="md", mt=15)
])


@callback(
    Output("items-container", "children"),
    Input("add-item-btn", "n_clicks"),
    State("items-container", "children"),
    prevent_initial_call=True
)
def add_item(n_clicks, children):
    children = children or []
    new_id = len(children)

    new_item = dmc.Group([
        dmc.NumberInput(
            label=f"Item {new_id + 1}",
            id={"type": "item-input", "index": new_id},
            value=0,
            min=0,
            style={"flex": 1}
        ),
        dmc.ActionIcon(
            DashIconify(icon="mdi:delete"),
            id={"type": "delete-btn", "index": new_id},
            variant="filled",
            color="red",
            size="lg",
            mt=25
        )
    ], mb=10)

    children.append(new_item)
    return children


@callback(
    Output("total-sum", "children"),
    Input({"type": "item-input", "index": ALL}, "value")
)
def calculate_total(values):
    total = sum(v or 0 for v in values)
    return f"Total: {total}"


@callback(
    Output("items-container", "children", allow_duplicate=True),
    Input({"type": "delete-btn", "index": ALL}, "n_clicks"),
    State("items-container", "children"),
    prevent_initial_call=True
)
def delete_item(delete_clicks, children):
    from dash import ctx

    if not ctx.triggered or not any(delete_clicks):
        return children

    # Find which delete button was clicked
    button_id = ctx.triggered_id
    if button_id:
        index_to_remove = button_id["index"]
        children = [child for i, child in enumerate(children) if i != index_to_remove]

    return children
