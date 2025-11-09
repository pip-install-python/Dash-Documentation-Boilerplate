from dash import html, dcc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_mantine_components as dmc
import numpy as np

# Generate comprehensive sample data
np.random.seed(42)
dates = pd.date_range('2024-01-01', periods=90, freq='D')

df_sales = pd.DataFrame({
    'Date': dates,
    'Sales': np.cumsum(np.random.randn(90) * 50 + 1000),
    'Target': np.linspace(90000, 120000, 90)
})

df_products = pd.DataFrame({
    'Product': ['Electronics', 'Clothing', 'Food', 'Books', 'Other'],
    'Revenue': [45000, 32000, 28000, 15000, 12000]
})

df_regions = pd.DataFrame({
    'Region': ['North', 'South', 'East', 'West'],
    'Q1': [23000, 19000, 31000, 21000],
    'Q2': [25000, 21000, 29000, 24000],
    'Q3': [27000, 23000, 32000, 26000],
    'Q4': [29000, 25000, 35000, 28000]
})

# Create charts
# 1. Sales Trend Line Chart
fig_sales = px.line(
    df_sales,
    x='Date',
    y=['Sales', 'Target'],
    title='Sales Performance vs Target',
    color_discrete_map={'Sales': '#12B886', 'Target': '#FA5252'}
)
fig_sales.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20), showlegend=True)

# 2. Product Revenue Pie Chart
fig_products = px.pie(
    df_products,
    values='Revenue',
    names='Product',
    title='Revenue by Product Category',
    color_discrete_sequence=px.colors.qualitative.Set2
)
fig_products.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))

# 3. Regional Performance Bar Chart
df_regions_melted = df_regions.melt(
    id_vars=['Region'],
    var_name='Quarter',
    value_name='Revenue'
)
fig_regions = px.bar(
    df_regions_melted,
    x='Region',
    y='Revenue',
    color='Quarter',
    title='Quarterly Revenue by Region',
    barmode='group'
)
fig_regions.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))

# 4. KPI Cards Data
total_revenue = df_products['Revenue'].sum()
avg_daily_sales = df_sales['Sales'].tail(30).mean()
target_achievement = (df_sales['Sales'].iloc[-1] / df_sales['Target'].iloc[-1]) * 100

component = html.Div([
    dmc.Title("Executive Dashboard", order=3, mb=20),

    # KPI Cards Row
    dmc.SimpleGrid([
        dmc.Card([
            dmc.Group([
                dmc.ThemeIcon(
                    dmc.Text("$", size="xl", fw=700),
                    size="xl",
                    radius="md",
                    color="teal",
                    variant="light"
                ),
                html.Div([
                    dmc.Text("Total Revenue", size="sm", c="dimmed"),
                    dmc.Title(f"${total_revenue:,.0f}", order=4, c="teal")
                ])
            ]),
        ], withBorder=True, p="md", radius="md"),

        dmc.Card([
            dmc.Group([
                dmc.ThemeIcon(
                    dmc.Text("📊", size="xl"),
                    size="xl",
                    radius="md",
                    color="blue",
                    variant="light"
                ),
                html.Div([
                    dmc.Text("Avg Daily Sales", size="sm", c="dimmed"),
                    dmc.Title(f"${avg_daily_sales:,.0f}", order=4, c="blue")
                ])
            ]),
        ], withBorder=True, p="md", radius="md"),

        dmc.Card([
            dmc.Group([
                dmc.ThemeIcon(
                    dmc.Text("🎯", size="xl"),
                    size="xl",
                    radius="md",
                    color="green" if target_achievement >= 100 else "orange",
                    variant="light"
                ),
                html.Div([
                    dmc.Text("Target Achievement", size="sm", c="dimmed"),
                    dmc.Title(
                        f"{target_achievement:.1f}%",
                        order=4,
                        c="green" if target_achievement >= 100 else "orange"
                    )
                ])
            ]),
        ], withBorder=True, p="md", radius="md"),
    ], cols={"base": 1, "sm": 3}, mb=20),

    # Charts Grid
    dmc.SimpleGrid([
        dmc.Card([
            dcc.Graph(figure=fig_sales, config={'displayModeBar': False})
        ], withBorder=True, p="md", radius="md"),

        dmc.Card([
            dcc.Graph(figure=fig_products, config={'displayModeBar': False})
        ], withBorder=True, p="md", radius="md"),
    ], cols={"base": 1, "sm": 2}, mb=15),

    dmc.Card([
        dcc.Graph(figure=fig_regions, config={'displayModeBar': False})
    ], withBorder=True, p="md", radius="md")
])
