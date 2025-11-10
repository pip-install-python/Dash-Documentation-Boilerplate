from dash import dcc, callback, Input, Output
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px

# Register Mantine templates
dmc.add_figure_templates(default="mantine_light")

# Sample data
df = pd.DataFrame({
    "Category": ["Product A", "Product B", "Product C", "Product D", "Product E"],
    "Sales": [120, 95, 180, 140, 165]
})

# Create initial figure
fig = px.bar(
    df,
    x="Category",
    y="Sales",
    title="Product Sales Comparison",
    color="Sales",
    color_continuous_scale="teal"
)

fig.update_layout(
    xaxis_title="Product Category",
    yaxis_title="Sales (Units)",
    showlegend=False,
    height=400
)

component = dcc.Graph(figure=fig, id='figure-basic-chart', config={'displayModeBar': False})


@callback(
    Output('figure-basic-chart', "figure"),
    Input("color-scheme-storage", "data"),
)
def update_figure_theme(theme):
    """Update chart template based on color scheme"""
    template = "mantine_dark" if theme == "dark" else "mantine_light"

    # Recreate the figure with the correct template
    fig = px.bar(
        df,
        x="Category",
        y="Sales",
        title="Product Sales Comparison",
        color="Sales",
        color_continuous_scale="teal",
        template=template
    )

    fig.update_layout(
        xaxis_title="Product Category",
        yaxis_title="Sales (Units)",
        showlegend=False,
        height=400
    )

    return fig
