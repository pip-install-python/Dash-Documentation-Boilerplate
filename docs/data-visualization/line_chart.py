from dash import dcc, callback, Input, Output
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
import numpy as np

# Register Mantine templates
dmc.add_figure_templates(default="mantine_light")

# Generate sample time series data
dates = pd.date_range('2024-01-01', periods=30, freq='D')
np.random.seed(42)

df = pd.DataFrame({
    'Date': dates,
    'Revenue': np.cumsum(np.random.randn(30) * 10 + 100),
    'Costs': np.cumsum(np.random.randn(30) * 8 + 80),
    'Profit': np.cumsum(np.random.randn(30) * 5 + 20)
})

# Melt the dataframe for plotting multiple lines
df_melted = df.melt(id_vars=['Date'], var_name='Metric', value_name='Amount')

# Create initial figure
fig = px.line(
    df_melted,
    x='Date',
    y='Amount',
    color='Metric',
    title='Financial Metrics Over Time',
    color_discrete_map={
        'Revenue': '#12B886',  # Teal
        'Costs': '#FA5252',    # Red
        'Profit': '#228BE6'    # Blue
    }
)

fig.update_layout(
    xaxis_title='Date',
    yaxis_title='Amount ($)',
    hovermode='x unified',
    height=450,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

component = dcc.Graph(figure=fig, id='figure-line-chart')


@callback(
    Output('figure-line-chart', "figure"),
    Input("color-scheme-storage", "data"),
)
def update_figure_theme(theme):
    """Update chart template based on color scheme"""
    template = "mantine_dark" if theme == "dark" else "mantine_light"

    # Recreate the figure with the correct template
    fig = px.line(
        df_melted,
        x='Date',
        y='Amount',
        color='Metric',
        title='Financial Metrics Over Time',
        color_discrete_map={
            'Revenue': '#12B886',
            'Costs': '#FA5252',
            'Profit': '#228BE6'
        },
        template=template
    )

    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Amount ($)',
        hovermode='x unified',
        height=450,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig
