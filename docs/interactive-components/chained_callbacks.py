from dash import html, callback, Input, Output, dcc
import dash_mantine_components as dmc

# Sample data structure
data = {
    "USA": {
        "California": ["Los Angeles", "San Francisco", "San Diego"],
        "Texas": ["Houston", "Dallas", "Austin"],
        "Florida": ["Miami", "Orlando", "Tampa"]
    },
    "Canada": {
        "Ontario": ["Toronto", "Ottawa", "Hamilton"],
        "Quebec": ["Montreal", "Quebec City", "Laval"],
        "British Columbia": ["Vancouver", "Victoria", "Kelowna"]
    },
    "Mexico": {
        "Jalisco": ["Guadalajara", "Puerto Vallarta", "Zapopan"],
        "Nuevo León": ["Monterrey", "San Pedro", "Santa Catarina"]
    }
}

component = html.Div([
    dmc.Title("Chained Callbacks Example", order=4, mb=10),
    dmc.Text(
        "Select a country to populate states, then select a state to populate cities. Each selection triggers the next dropdown.",
        mb=15,
        c="dimmed",
        size="sm"
    ),

    dmc.Stack([
        dmc.Select(
            label="Country",
            placeholder="Select a country",
            id="country-dropdown",
            data=[{"label": country, "value": country} for country in data.keys()]
        ),
        dmc.Select(
            label="State/Province",
            placeholder="Select a country first",
            id="state-dropdown",
            data=[],
            disabled=True
        ),
        dmc.Select(
            label="City",
            placeholder="Select a state first",
            id="city-dropdown",
            data=[],
            disabled=True
        ),
        dmc.Paper([
            dmc.Text("Your Selection:", size="sm", c="dimmed", mb=5),
            html.Div(
                "Make selections above to see your full location",
                id="selection-output"
            )
        ], p="md", withBorder=True, radius="md")
    ], gap="sm")
])


@callback(
    Output("state-dropdown", "data"),
    Output("state-dropdown", "disabled"),
    Output("state-dropdown", "value"),
    Input("country-dropdown", "value")
)
def update_states(country):
    if not country:
        return [], True, None

    states = list(data[country].keys())
    state_options = [{"label": state, "value": state} for state in states]

    return state_options, False, None


@callback(
    Output("city-dropdown", "data"),
    Output("city-dropdown", "disabled"),
    Output("city-dropdown", "value"),
    Input("state-dropdown", "value"),
    State("country-dropdown", "value")
)
def update_cities(state, country):
    if not state or not country:
        return [], True, None

    cities = data[country][state]
    city_options = [{"label": city, "value": city} for city in cities]

    return city_options, False, None


@callback(
    Output("selection-output", "children"),
    Input("city-dropdown", "value"),
    State("state-dropdown", "value"),
    State("country-dropdown", "value")
)
def display_selection(city, state, country):
    if not all([country, state, city]):
        return "Make selections above to see your full location"

    return html.Div([
        dmc.Text("📍 Your Location:", fw=500, mb=5),
        dmc.Text(f"{city}, {state}, {country}", size="lg", c="teal")
    ])
