from dash import html, dcc, callback, Input, Output
import pandas as pd
import plotly.express as px
import dash_mantine_components as dmc
import numpy as np

# Generate sample data
np.random.seed(42)
df = pd.DataFrame({
    'Height': np.random.normal(170, 10, 100),
    'Weight': np.random.normal(70, 15, 100),
    'Age': np.random.randint(20, 60, 100),
    'Gender': np.random.choice(['Male', 'Female'], 100)
})

component = html.Div([
    dmc.Title("Height vs Weight Analysis", order=4, mb=10),
    dmc.Select(
        label="Filter by Gender",
        data=[
            {"label": "All", "value": "all"},
            {"label": "Male", "value": "Male"},
            {"label": "Female", "value": "Female"}
        ],
        value="all",
        id="gender-filter",
        mb=15,
        style={"maxWidth": "200px"}
    ),
    dcc.Graph(id="scatter-chart")
])


@callback(
    Output("scatter-chart", "figure"),
    Input("gender-filter", "value")
)
def update_scatter(gender):
    if gender == "all":
        filtered_df = df
    else:
        filtered_df = df[df['Gender'] == gender]

    fig = px.scatter(
        filtered_df,
        x='Height',
        y='Weight',
        color='Gender',
        size='Age',
        title=f'Height vs Weight{" - " + gender if gender != "all" else ""}',
        hover_data=['Age'],
        color_discrete_map={'Male': '#228BE6', 'Female': '#FA5252'}
    )

    fig.update_layout(
        xaxis_title='Height (cm)',
        yaxis_title='Weight (kg)',
        height=450
    )

    return fig
