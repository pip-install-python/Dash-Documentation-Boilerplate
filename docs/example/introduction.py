from dash import Dash, dcc, html, Input, Output, callback
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px

# Import mark_important to highlight key elements for AI/LLMs
try:
    from dash_improve_my_llms import mark_important
except ImportError:
    # Fallback if package not installed
    def mark_important(component, component_id=None):
        return component

# Register Mantine templates
dmc.add_figure_templates(default="mantine_light")

# Sample data
df1 = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Grapes"],
    "Amount": [4, 1, 2, 2]
})

df2 = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Grapes"],
    "Amount": [2, 4, 5, 1]
})

# Mark the interactive controls as important for LLM understanding
component = html.Div([
    html.H1("Graph Update Example", style={'textAlign': 'center', 'marginBottom': '20px'}),
    mark_important(
        html.Div([
            dcc.Graph(id='example-graph'),
            html.Button('Update Graph', id='update-button', n_clicks=0,
                       style={'marginTop': '10px', 'padding': '10px 20px'})
        ], id='interactive-section'),
        component_id='interactive-section'
    )
])

# Callback to update the graph
@callback(
    Output('example-graph', 'figure'),
    Input('update-button', 'n_clicks'),
    Input("color-scheme-storage", "data"),
)
def update_graph(n_clicks, theme):
    """Update graph based on button clicks and theme"""
    template = "mantine_dark" if theme == "dark" else "mantine_light"

    if n_clicks % 2 == 0:
        fig = px.bar(df1, x="Fruit", y="Amount", title="Fruit Amounts", template=template)
    else:
        fig = px.bar(df2, x="Fruit", y="Amount", title="Updated Fruit Amounts", template=template)
    return fig
