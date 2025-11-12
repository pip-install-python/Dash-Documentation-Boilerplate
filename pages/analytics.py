"""
Analytics Page - Visitor Analytics Dashboard

This page demonstrates visitor tracking with device and bot detection.
Updates in real-time without requiring page refresh.
"""
import dash_mantine_components as dmc
from dash import Input, Output, callback, html, register_page, dcc
from datetime import datetime, timedelta
import json
from pathlib import Path
from collections import Counter
import dash_ag_grid as dag
import plotly.graph_objects as go

# Register page
register_page(
    __name__,
    path="/analytics/traffic",
    name="Traffic Analytics",
    title="Traffic Analytics | Dash Documentation Boilerplate",
    description="Visitor analytics dashboard with device and bot tracking"
)

# Path to analytics data
ANALYTICS_FILE = Path(__file__).parent.parent / "visitor_analytics.json"


def load_analytics():
    """Load analytics data from JSON file."""
    if ANALYTICS_FILE.exists():
        with open(ANALYTICS_FILE, "r") as f:
            data = json.load(f)

            # Clean up any _reload-hash or internal Dash paths from existing data
            clean_visits = []
            for visit in data.get("visits", []):
                path = visit.get("path", "")
                # Filter out internal Dash paths
                skip_paths = [
                    '.css', '.js', '.png', '.jpg', '.ico', '_dash', '_reload-hash',
                    '/_dash-update-component', '/_dash-layout', '/assets/', '[]'
                ]
                if not any(ext in path for ext in skip_paths):
                    clean_visits.append(visit)

            # Recalculate stats from clean visits
            stats = {
                "desktop": 0,
                "mobile": 0,
                "tablet": 0,
                "bot": 0,
                "total": 0
            }

            for visit in clean_visits:
                device_type = visit.get("device_type", "desktop")
                stats[device_type] = stats.get(device_type, 0) + 1
                stats["total"] += 1

            return {
                "visits": clean_visits,
                "stats": stats
            }

    return {
        "visits": [],
        "stats": {
            "desktop": 0,
            "mobile": 0,
            "tablet": 0,
            "bot": 0,
            "total": 0
        }
    }


def get_bot_visits_by_type(visits):
    """Get bot visits grouped by bot type."""
    bot_visits = [v for v in visits if v["device_type"] == "bot"]
    bot_types = Counter([v.get("bot_type", "unknown") for v in bot_visits])
    return bot_types


def get_visits_by_hour(visits):
    """Get visits grouped by hour for the last 24 hours."""
    now = datetime.now()
    twenty_four_hours_ago = now - timedelta(hours=24)

    # Filter visits from last 24 hours
    recent_visits = []
    for visit in visits:
        try:
            visit_time = datetime.fromisoformat(visit["timestamp"])
            if visit_time >= twenty_four_hours_ago:
                recent_visits.append(visit)
        except:
            continue

    # Group by hour
    hourly_counts = {}
    for i in range(24):
        hour = (now - timedelta(hours=23-i)).strftime("%H:00")
        hourly_counts[hour] = {"desktop": 0, "mobile": 0, "tablet": 0, "bot": 0}

    for visit in recent_visits:
        try:
            visit_time = datetime.fromisoformat(visit["timestamp"])
            hour_key = visit_time.strftime("%H:00")
            device_type = visit["device_type"]
            if hour_key in hourly_counts:
                hourly_counts[hour_key][device_type] += 1
        except:
            continue

    return hourly_counts


def get_top_pages(visits, limit=10):
    """Get most visited pages with device type breakdown."""
    # Filter out internal paths
    filtered_visits = [v for v in visits if v["path"] not in ["/_dash-update-component", "/_dash-layout"]]

    # Count total visits per page to find top pages
    page_counts = Counter([v["path"] for v in filtered_visits])
    top_pages = [page for page, count in page_counts.most_common(limit)]

    # Get device breakdown for each top page
    page_device_breakdown = {}
    for page in top_pages:
        page_device_breakdown[page] = {
            "desktop": 0,
            "mobile": 0,
            "tablet": 0,
            "bot": 0
        }

    # Count visits by device type for each page
    for visit in filtered_visits:
        page = visit["path"]
        if page in page_device_breakdown:
            device = visit["device_type"].lower()
            if device in page_device_breakdown[page]:
                page_device_breakdown[page][device] += 1

    return page_device_breakdown


def layout():
    return dmc.Container([
        # Interval for auto-refresh every 5 seconds
        dcc.Interval(
            id='analytics-interval',
            interval=5*1000,  # in milliseconds
            n_intervals=0
        ),

        # Store for analytics data (load initial data)
        dcc.Store(id='analytics-data-store', data=load_analytics()),

        # Header Section
        dmc.Group([
            create_stat_card(
                label="Total Visits",
                icon="📊",
                color="violet",
                card_id="total-stat"
            ),
            dmc.Stack([
                dmc.Group([
                    dmc.Stack([
                        dmc.Title("Traffic Analytics", order=2, className="m2d-heading"),
                        dmc.Text(
                            "Visitor Devices Being Used & Bot Tracking",
                            size="lg",
                            c="dimmed",
                            className="m2d-paragraph"
                        ),
                    ], gap=4),
                ], justify="space-between", align="flex-start"),
            ]),

            # Info Alert
            dmc.Alert(
                children=[
                    dmc.Text([
                        "Real-time visitor analytics tracking device types, bot visits, and page views. ",
                        "Updates automatically every 5 seconds."
                    ], size="sm"),
                ],
                title="📊 Analytics Dashboard",
                color="blue",
                variant="light",
                radius="md",
            ),
        ], gap="xl", mb="xl"),

        # Stats Cards Section
        # dmc.SimpleGrid(
        #     cols={"base": 1, "xs": 2, "sm": 3, "md": 5},
        #     spacing="lg",
        #     mb="xl",
        #     children=[
        #         create_stat_card(
        #             label="Total Visits",
        #             icon="📊",
        #             color="violet",
        #             card_id="total-stat"
        #         ),
        #         create_stat_card(
        #             label="Desktop",
        #             icon="🖥️",
        #             color="gray",
        #             card_id="desktop-stat"
        #         ),
        #         create_stat_card(
        #             label="Mobile",
        #             icon="📱",
        #             color="gray",
        #             card_id="mobile-stat"
        #         ),
        #         create_stat_card(
        #             label="Tablet",
        #             icon="📲",
        #             color="gray",
        #             card_id="tablet-stat"
        #         ),
        #         create_stat_card(
        #             label="Bots",
        #             icon="🤖",
        #             color="gray",
        #             card_id="bot-stat"
        #         ),
        #     ]
        # ),

        # Charts
        dmc.Stack([
            # Device Distribution and Bot Types
            dmc.SimpleGrid(
                cols={"base": 1, "md": 2},
                spacing="lg",
                mb="lg",
                children=[
                    dmc.Paper([
                        dmc.Stack([
                            dmc.Stack([
                                dmc.Title("Device Distribution", order=3),
                                dmc.Text("Breakdown by device type", size="sm", c="dimmed"),
                            ], gap=4),
                            html.Div(id="device-chart-container"),
                        ], gap="md"),
                    ], p="lg", radius="md", withBorder=True, shadow="sm"),
                    dmc.Paper([
                        dmc.Stack([
                            dmc.Stack([
                                dmc.Title("Bot Types", order=3),
                                dmc.Text("AI Training, Search, and Traditional bots", size="sm", c="dimmed"),
                            ], gap=4),
                            html.Div(id="bot-types-chart-container"),
                        ], gap="md"),
                    ], p="lg", radius="md", withBorder=True, shadow="sm"),
                ]
            ),

            # Hourly visits
            dmc.Paper([
                dmc.Stack([
                    dmc.Stack([
                        dmc.Title("Visits by Hour", order=3),
                        dmc.Text("Activity over the last 24 hours", size="sm", c="dimmed"),
                    ], gap=4),
                    html.Div(id="hourly-chart-container"),
                ], gap="md"),
            ], p="lg", radius="md", withBorder=True, shadow="sm"),

            # Top pages
            dmc.Paper([
                dmc.Stack([
                    dmc.Stack([
                        dmc.Title("Most Visited Pages", order=3),
                        dmc.Text("Top 10 pages by visit count", size="sm", c="dimmed"),
                    ], gap=4),
                    html.Div(id="top-pages-chart-container"),
                ], gap="md"),
            ], p="lg", radius="md", withBorder=True, shadow="sm"),

            # Bot visits table
            dmc.Paper([
                dmc.Title("Recent Bot Visits", order=3, mb="md"),
                html.Div(id="bot-visits-table-container"),
            ], p="lg", radius="md", withBorder=True),

            # Visitor Location Map
            dmc.Paper([
                dmc.Stack([
                    dmc.Stack([
                        dmc.Title("Visitor Locations", order=3),
                        dmc.Text("Geographic distribution of visitors", size="sm", c="dimmed"),
                    ], gap=4),
                    html.Div(id="location-map-container"),
                ], gap="md"),
            ], p="lg", radius="md", withBorder=True, shadow="sm"),
        ], gap="lg"),

    ], size="xl", py="xl")


def create_stat_card(label, icon, color="violet", card_id=None):
    """Create a stat card with dynamic value."""
    return dmc.Paper([
        dmc.Stack([
            dmc.Group([
                dmc.Text(icon, size="xl"),
                dmc.Title(
                    "0",
                    order=2,
                    c=f"{color}.6" if color != "gray" else None,
                    id=f"{card_id}-value"
                ),
            ], gap="xs", justify="center"),
            dmc.Text(label, size="sm", c="dimmed", ta="center"),
        ], gap="xs", align="center"),
    ], p="lg", radius="md", withBorder=True, shadow="sm", id=card_id)


def create_bot_visits_table(bot_visits):
    """Create a table showing recent bot visits using AG Grid."""
    if not bot_visits:
        return dmc.Text("No bot visits yet. Bots will be tracked automatically.", c="dimmed", fs="italic")

    # Prepare data for AG Grid
    row_data = []
    for visit in bot_visits:
        timestamp = visit.get('timestamp', 'Unknown')
        try:
            dt = datetime.fromisoformat(timestamp)
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            time_str = timestamp

        bot_type = visit.get('bot_type', 'unknown')

        # Capitalize bot type for display
        bot_type_display = bot_type.capitalize()

        user_agent = visit.get('user_agent', 'Unknown')

        row_data.append({
            'timestamp': time_str,
            'bot_type': bot_type_display,
            'bot_type_raw': bot_type,  # Keep raw for styling
            'page': visit.get('path', '/'),
            'user_agent': user_agent
        })

    # Define column definitions with styling
    column_defs = [
        {
            'field': 'timestamp',
            'headerName': 'Timestamp',
            'width': 200,
            'sortable': True,
            'filter': True,
            'cellClass': 'timestamp-cell'
        },
        {
            'field': 'bot_type',
            'headerName': 'Bot Type',
            'width': 130,
            'sortable': True,
            'filter': True,
            'cellClass': 'bot-type-cell',
            'cellClassRules': {
                'bot-training': 'data.bot_type_raw === "training"',
                'bot-search': 'data.bot_type_raw === "search"',
                'bot-traditional': 'data.bot_type_raw === "traditional"',
                'bot-unknown': 'data.bot_type_raw === "unknown"'
            }
        },
        {
            'field': 'page',
            'headerName': 'Page',
            'width': 250,
            'sortable': True,
            'filter': True,
            'cellClass': 'page-cell'
        },
        {
            'field': 'user_agent',
            'headerName': 'User Agent',
            'flex': 1,
            'sortable': True,
            'filter': True,
            'cellClass': 'user-agent-cell',
            'wrapText': True,
            'autoHeight': True
        }
    ]

    # Create AG Grid
    return dag.AgGrid(
        id='bot-visits-grid',
        rowData=row_data,
        columnDefs=column_defs,
        defaultColDef={
            'resizable': True,
            'sortable': True,
            'filter': True,
        },
        dashGridOptions={
            'pagination': True,
            'paginationPageSize': 20,
            'domLayout': 'autoHeight',
            'animateRows': True,
        },
        style={'height': 'auto'},
        className='ag-theme-alpine'
    )


# Callback to load analytics data periodically
@callback(
    Output('analytics-data-store', 'data'),
    Input('analytics-interval', 'n_intervals')
)
def update_analytics_data(n):
    """Load fresh analytics data."""
    return load_analytics()


# Callbacks to update stat cards
@callback(
    Output('total-stat-value', 'children'),
    Input('analytics-data-store', 'data')
)
def update_total_stat(data):
    if not data:
        return "0"
    return f"{data['stats']['total']:,}"


@callback(
    Output('desktop-stat-value', 'children'),
    Input('analytics-data-store', 'data')
)
def update_desktop_stat(data):
    if not data:
        return "0"
    return f"{data['stats']['desktop']:,}"


@callback(
    Output('mobile-stat-value', 'children'),
    Input('analytics-data-store', 'data')
)
def update_mobile_stat(data):
    if not data:
        return "0"
    return f"{data['stats']['mobile']:,}"


@callback(
    Output('tablet-stat-value', 'children'),
    Input('analytics-data-store', 'data')
)
def update_tablet_stat(data):
    if not data:
        return "0"
    return f"{data['stats']['tablet']:,}"


@callback(
    Output('bot-stat-value', 'children'),
    Input('analytics-data-store', 'data')
)
def update_bot_stat(data):
    if not data:
        return "0"
    return f"{data['stats']['bot']:,}"


# Callback to update device chart
@callback(
    Output('device-chart-container', 'children'),
    Input('analytics-data-store', 'data')
)
def update_device_chart(data):
    if not data:
        return dmc.Center(dmc.Text("Loading...", c="dimmed", fs="italic"), h=350)

    stats = data['stats']
    device_data = [
        {"name": "Desktop", "value": stats['desktop'], "color": "violet.6"},
        {"name": "Mobile", "value": stats['mobile'], "color": "blue.6"},
        {"name": "Tablet", "value": stats['tablet'], "color": "green.6"},
        {"name": "Bots", "value": stats['bot'], "color": "yellow.6"},
    ]
    # Filter out zero values
    device_data = [d for d in device_data if d["value"] > 0]

    if not device_data:
        return dmc.Center(dmc.Text("No visit data yet", c="dimmed", fs="italic"), h=350)

    return dmc.PieChart(
        data=device_data,
        size=200,
        withLabelsLine=True,
        labelsPosition="outside",
        labelsType="percent",
        withLabels=True,
        tooltipDataSource="segment",
        h=350,
    )


# Callback to update bot types chart
@callback(
    Output('bot-types-chart-container', 'children'),
    Input('analytics-data-store', 'data')
)
def update_bot_types_chart(data):
    if not data:
        return dmc.Center(dmc.Text("Loading...", c="dimmed", fs="italic"), h=350)

    bot_types = get_bot_visits_by_type(data['visits'])
    bot_color_map = {
        'training': 'red.6',
        'search': 'blue.6',
        'traditional': 'green.6',
        'unknown': 'gray.6'
    }
    bot_data = [
        {"type": key.capitalize(), "visits": value, "color": bot_color_map.get(key, 'gray.6')}
        for key, value in bot_types.items()
    ]

    if not bot_data:
        return dmc.Center(dmc.Text("No bot visits yet", c="dimmed", fs="italic"), h=350)

    return dmc.BarChart(
        data=bot_data,
        dataKey="type",
        series=[{"name": "visits", "color": "blue.6"}],
        h=350,
        withLegend=False,
        yAxisLabel="Visits",
        xAxisLabel="Bot Type",
    )


# Callback to update hourly chart
@callback(
    Output('hourly-chart-container', 'children'),
    Input('analytics-data-store', 'data')
)
def update_hourly_chart(data):
    if not data:
        return dmc.Center(dmc.Text("Loading...", c="dimmed", fs="italic"), h=350)

    hourly_counts = get_visits_by_hour(data['visits'])
    hourly_data = [
        {
            "hour": hour,
            "Desktop": counts["desktop"],
            "Mobile": counts["mobile"],
            "Tablet": counts["tablet"],
            "Bots": counts["bot"]
        }
        for hour, counts in hourly_counts.items()
    ]

    if not hourly_data or not any(sum(h.values()) for h in hourly_counts.values()):
        return dmc.Center(dmc.Text("No visit data available", c="dimmed", fs="italic"), h=350)

    return dmc.AreaChart(
        data=hourly_data,
        dataKey="hour",
        series=[
            {"name": "Desktop", "color": "violet.6"},
            {"name": "Mobile", "color": "blue.6"},
            {"name": "Tablet", "color": "green.6"},
            {"name": "Bots", "color": "yellow.6"},
        ],
        h=350,
        curveType="natural",
        withLegend=True,
        legendProps={"verticalAlign": "top", "height": 50},
        yAxisLabel="Visits",
        xAxisLabel="Hour",
        type="stacked",
    )


# Callback to update top pages chart
@callback(
    Output('top-pages-chart-container', 'children'),
    Input('analytics-data-store', 'data')
)
def update_top_pages_chart(data):
    if not data:
        return dmc.Center(dmc.Text("Loading...", c="dimmed", fs="italic"), h=350)

    page_device_breakdown = get_top_pages(data['visits'])

    # Transform data for stacked bar chart
    top_pages_data = []
    for page, devices in page_device_breakdown.items():
        top_pages_data.append({
            "page": page,
            "Desktop": devices["desktop"],
            "Mobile": devices["mobile"],
            "Tablet": devices["tablet"],
            "Bots": devices["bot"]
        })

    if not top_pages_data:
        return dmc.Center(dmc.Text("No page visits yet", c="dimmed", fs="italic"), h=350)

    return dmc.BarChart(
        data=top_pages_data,
        dataKey="page",
        series=[
            {"name": "Desktop", "color": "violet.6"},
            {"name": "Mobile", "color": "blue.6"},
            {"name": "Tablet", "color": "green.6"},
            {"name": "Bots", "color": "yellow.6"},
        ],
        h=400,
        orientation="horizontal",
        withLegend=True,
        withBarValueLabel=True,
        legendProps={"verticalAlign": "top", "height": 50},
        yAxisLabel="Page",
        xAxisLabel="Visits by Device Type",
        # type="stacked",
        barProps={"isAnimationActive": True},
    )


# Callback to update bot visits table
@callback(
    Output('bot-visits-table-container', 'children'),
    Input('analytics-data-store', 'data')
)
def update_bot_visits_table(data):
    if not data:
        return dmc.Text("Loading...", c="dimmed", fs="italic")

    visits = data['visits']
    recent_bot_visits = [v for v in visits if v["device_type"] == "bot"][-20:]
    recent_bot_visits.reverse()

    return create_bot_visits_table(recent_bot_visits)


def get_location_data(visits):
    """Aggregate visitor location data for bubble map."""
    location_counts = {}

    for visit in visits:
        # Check if visit has location data
        if 'location' not in visit:
            continue

        location = visit['location']
        lat = location.get('latitude')
        lon = location.get('longitude')
        city = location.get('city', 'Unknown')
        country = location.get('country', 'Unknown')

        if lat is None or lon is None:
            continue

        # Create a unique key for each location
        location_key = f"{lat},{lon}"

        if location_key not in location_counts:
            location_counts[location_key] = {
                'latitude': lat,
                'longitude': lon,
                'city': city,
                'country': country,
                'count': 0,
                'device_breakdown': {'desktop': 0, 'mobile': 0, 'tablet': 0, 'bot': 0}
            }

        location_counts[location_key]['count'] += 1
        device_type = visit.get('device_type', 'desktop')
        location_counts[location_key]['device_breakdown'][device_type] += 1

    return list(location_counts.values())


# Callback to update location map
@callback(
    Output('location-map-container', 'children'),
    Input('analytics-data-store', 'data')
)
def update_location_map(data):
    if not data:
        return dmc.Center(dmc.Text("Loading...", c="dimmed", fs="italic"), h=400)

    location_data = get_location_data(data['visits'])

    if not location_data:
        return dmc.Center(
            dmc.Stack([
                dmc.Text("🌍", size="60px", ta="center"),
                dmc.Text("No location data yet", size="lg", fw=500, ta="center"),
                dmc.Text(
                    "Visitor locations will appear here as they visit your site",
                    c="dimmed",
                    size="sm",
                    ta="center"
                )
            ], align="center", gap="xs"),
            h=400
        )

    # Prepare data for bubble map
    lats = [loc['latitude'] for loc in location_data]
    lons = [loc['longitude'] for loc in location_data]
    counts = [loc['count'] for loc in location_data]

    # Create hover text with device breakdown
    hover_texts = []
    for loc in location_data:
        breakdown = loc['device_breakdown']
        text = (
            f"<b>{loc['city']}, {loc['country']}</b><br>"
            f"Total Visits: {loc['count']}<br>"
            f"🖥️ Desktop: {breakdown['desktop']}<br>"
            f"📱 Mobile: {breakdown['mobile']}<br>"
            f"📲 Tablet: {breakdown['tablet']}<br>"
            f"🤖 Bots: {breakdown['bot']}"
        )
        hover_texts.append(text)

    # Create the bubble map
    fig = go.Figure(data=go.Scattergeo(
        lon=lons,
        lat=lats,
        text=hover_texts,
        mode='markers',
        marker=dict(
            size=[count * 3 + 10 for count in counts],  # Scale bubble size
            color=counts,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(
                title="Visits",
                thickness=15,
                len=0.7
            ),
            line=dict(width=0.5, color='rgba(255, 255, 255, 0.8)'),
            sizemode='diameter'
        ),
        hovertemplate='%{text}<extra></extra>'
    ))

    # Update layout
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='natural earth',
            bgcolor='rgba(0,0,0,0)'
        ),
        height=500,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )

    return dcc.Graph(figure=fig, config={'displayModeBar': False})
