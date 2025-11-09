from dash import dcc
import pandas as pd
import plotly.express as px

# Sample data
df = pd.DataFrame({
    "Category": ["Product A", "Product B", "Product C", "Product D", "Product E"],
    "Sales": [120, 95, 180, 140, 165]
})

# Create bar chart
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
