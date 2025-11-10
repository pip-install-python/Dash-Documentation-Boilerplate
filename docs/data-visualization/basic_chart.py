from dash import dcc
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

# Create bar chart with Mantine template
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

component = dcc.Graph(figure=fig, config={'displayModeBar': False})
