---
name: Data Visualization
description: Interactive charts and graphs with Plotly integration
endpoint: /examples/visualization
package: visualization
icon: mdi:chart-line
---

.. toc::

## Introduction

This page demonstrates how to create **interactive data visualizations** using Plotly with your Dash Documentation Boilerplate. Plotly provides powerful, interactive charts that integrate seamlessly with Dash callbacks.

---

## Basic Chart Example

Let's start with a simple bar chart example:

.. exec::docs.data-visualization.basic_chart
    :code: false
Source code:

.. source::docs/data-visualization/basic_chart.py
    :defaultExpanded: false
    :withExpandedButton: true

---

## Interactive Line Chart

This example shows multiple lines with hover tooltips and a legend:

.. exec::docs.data-visualization.line_chart
    :code: false
Source code:

.. source::docs/data-visualization/line_chart.py

---

## Scatter Plot with Filtering

An interactive scatter plot with dropdown filtering:

.. exec::docs.data-visualization.scatter_plot
    :code: false
Source code:

.. source::docs/data-visualization/scatter_plot.py

---

## Real-Time Data Updates

This example demonstrates how to update charts in real-time using intervals:

.. exec::docs.data-visualization.realtime_chart
    :code: false
Source code:

.. source::docs/data-visualization/realtime_chart.py

---

## Dashboard with Multiple Charts

A comprehensive dashboard combining multiple chart types:

.. exec::docs.data-visualization.dashboard
    :code: false
Source code:

.. source::docs/data-visualization/dashboard.py

---

## Chart Types Reference

### Available Plotly Chart Types

Plotly Express provides many chart types:

#### Basic Charts
- **Bar Charts** - `px.bar()`
- **Line Charts** - `px.line()`
- **Scatter Plots** - `px.scatter()`
- **Pie Charts** - `px.pie()`
- **Histograms** - `px.histogram()`

#### Statistical Charts
- **Box Plots** - `px.box()`
- **Violin Plots** - `px.violin()`
- **Density Heatmaps** - `px.density_heatmap()`

#### Scientific Charts
- **Scatter Matrix** - `px.scatter_matrix()`
- **Parallel Coordinates** - `px.parallel_coordinates()`
- **3D Scatter** - `px.scatter_3d()`

#### Financial Charts
- **Candlestick** - `go.Candlestick()`
- **OHLC** - `go.Ohlc()`
- **Waterfall** - `go.Waterfall()`

---

## Customization Tips

### Theme Integration

Charts automatically inherit the app's color scheme. To ensure consistency:

```python
import plotly.express as px

# Use the primary color from your theme
fig = px.bar(df, x="category", y="value", color_discrete_sequence=["teal"])

# Or use Plotly's built-in templates
fig.update_layout(template="plotly_white")  # or "plotly_dark"
```

### Responsive Charts

Make charts responsive to window size:

```python
fig.update_layout(
    autosize=True,
    margin=dict(l=20, r=20, t=40, b=20),
)

# In your component
dcc.Graph(
    figure=fig,
    config={'responsive': True},
    style={'height': '400px'}
)
```

### Interactive Features

Enable useful interactions:

```python
config = {
    'displayModeBar': True,
    'displaylogo': False,
    'modeBarButtonsToRemove': ['pan2d', 'lasso2d'],
    'toImageButtonOptions': {
        'format': 'png',
        'filename': 'chart',
        'height': 1080,
        'width': 1920,
        'scale': 2
    }
}

dcc.Graph(figure=fig, config=config)
```

---

## Performance Tips

### 1. Limit Data Points

For large datasets, consider:

```python
# Sample data if too large
if len(df) > 10000:
    df = df.sample(10000)
```

### 2. Use Scattergl for Large Scatter Plots

```python
import plotly.graph_objects as go

fig = go.Figure(data=go.Scattergl(
    x=x_data,
    y=y_data,
    mode='markers'
))
```

### 3. Optimize Update Frequency

```python
# Use longer intervals for real-time updates
dcc.Interval(
    interval=2000,  # Update every 2 seconds
    n_intervals=0
)
```

---

## Common Patterns

### Pattern 1: Chart with Controls

```markdown
## My Visualization

Use the controls below to customize the view:

.. exec::docs.viz.controlled_chart
```

```python
component = html.Div([
    dmc.Select(
        label="Metric",
        data=[...],
        id="metric-select"
    ),
    dcc.Graph(id="chart")
])

@callback(Output("chart", "figure"), Input("metric-select", "value"))
def update(metric):
    return create_figure(metric)
```

### Pattern 2: Multi-View Dashboard

```python
component = dmc.SimpleGrid([
    dmc.Card([dcc.Graph(figure=fig1)]),
    dmc.Card([dcc.Graph(figure=fig2)]),
    dmc.Card([dcc.Graph(figure=fig3)]),
    dmc.Card([dcc.Graph(figure=fig4)]),
], cols={"base": 1, "sm": 2})
```

### Pattern 3: Clickable Charts

```python
@callback(
    Output("details", "children"),
    Input("chart", "clickData")
)
def display_click_data(clickData):
    if not clickData:
        return "Click on a data point"
    return f"Selected: {clickData['points'][0]['x']}"
```

---

## Best Practices

### 1. Add Axis Labels

Always label your axes:

```python
fig.update_layout(
    xaxis_title="Time (hours)",
    yaxis_title="Temperature (°C)"
)
```

### 2. Include Titles

Make charts self-explanatory:

```python
fig.update_layout(
    title="Monthly Sales Performance",
    title_x=0.5  # Center the title
)
```

### 3. Use Color Wisely

Choose accessible colors:

```python
# Good - accessible color palette
colors = ['#1f77b4', '#ff7f0e', '#2ca02c']

# Even better - use colorblind-friendly palettes
import plotly.express as px
fig = px.bar(df, color_discrete_sequence=px.colors.qualitative.Safe)
```

### 4. Add Hover Information

Provide context on hover:

```python
fig = px.scatter(
    df, x="x", y="y",
    hover_data=["category", "value", "date"]
)
```

### 5. Handle Empty Data

Always check for empty datasets:

```python
if df.empty:
    return {
        'data': [],
        'layout': {
            'xaxis': {'visible': False},
            'yaxis': {'visible': False},
            'annotations': [{
                'text': 'No data available',
                'showarrow': False,
                'font': {'size': 20}
            }]
        }
    }
```

---

## Resources

- **Plotly Express**: [plotly.com/python/plotly-express/](https://plotly.com/python/plotly-express/)
- **Plotly Graph Objects**: [plotly.com/python/graph-objects/](https://plotly.com/python/graph-objects/)
- **Dash Core Components**: [dash.plotly.com/dash-core-components/graph](https://dash.plotly.com/dash-core-components/graph)
- **Color Scales**: [plotly.com/python/builtin-colorscales/](https://plotly.com/python/builtin-colorscales/)

---

## Next Steps

- **Interactive Components** - Learn advanced callback patterns
- **AI Integration** - Make your visualizations AI-friendly
- **Getting Started** - Create your first documentation page

---

Happy visualizing! 📊
