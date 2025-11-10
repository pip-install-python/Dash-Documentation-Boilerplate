from dash import html, dcc, callback, Input, Output
import dash_mantine_components as dmc
import plotly.graph_objects as go
from collections import deque
import random
from datetime import datetime, timedelta

# Register Mantine templates
dmc.add_figure_templates(default="mantine_light")

# Initialize deque to store recent data points
MAX_DATA_POINTS = 50
time_data = deque(maxlen=MAX_DATA_POINTS)
value_data = deque(maxlen=MAX_DATA_POINTS)

# Initialize with some data
start_time = datetime.now()
for i in range(20):
    time_data.append(start_time + timedelta(seconds=i))
    value_data.append(random.uniform(20, 80))

component = html.Div([
    dmc.Title("Real-Time Data Stream", order=4, mb=10),
    dmc.Alert(
        "This chart updates every 2 seconds with simulated real-time data",
        color="blue",
        mb=15
    ),
    dcc.Graph(id="realtime-graph"),
    dcc.Interval(
        id="interval-component",
        interval=2000,  # Update every 2 seconds
        n_intervals=0
    )
])


@callback(
    Output("realtime-graph", "figure"),
    Input("interval-component", "n_intervals")
)
def update_realtime(n):
    # Add new data point
    time_data.append(datetime.now())

    # Generate new value with some randomness
    if len(value_data) > 0:
        last_value = value_data[-1]
        new_value = last_value + random.uniform(-5, 5)
        # Keep value in reasonable range
        new_value = max(10, min(90, new_value))
    else:
        new_value = 50

    value_data.append(new_value)

    # Create figure
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=list(time_data),
        y=list(value_data),
        mode='lines+markers',
        name='Sensor Reading',
        line=dict(color='#12B886', width=2),
        marker=dict(size=6)
    ))

    fig.update_layout(
        title='Live Sensor Data',
        xaxis_title='Time',
        yaxis_title='Value',
        yaxis_range=[0, 100],
        hovermode='x',
        height=400,
        showlegend=False
    )

    return fig
