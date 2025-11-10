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
    """Get most visited pages."""
    page_counts = Counter([v["path"] for v in visits if v["path"] not in ["/_dash-update-component", "/_dash-layout"]])
    return page_counts.most_common(limit)


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
        dmc.Stack([
            dmc.Group([
                dmc.Stack([
                    dmc.Title("Traffic Analytics", order=2, className="m2d-heading"),
                    dmc.Text(
                        "Visitor Analytics & Bot Tracking",
                        size="lg",
                        c="dimmed",
                        className="m2d-paragraph"
                    ),
                ], gap=4),
            ], justify="space-between", align="flex-start"),

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
        dmc.SimpleGrid(
            cols={"base": 1, "xs": 2, "sm": 3, "md": 5},
            spacing="lg",
            mb="xl",
            children=[
                create_stat_card(
                    label="Total Visits",
                    icon="📊",
                    color="violet",
                    card_id="total-stat"
                ),
                create_stat_card(
                    label="Desktop",
                    icon="🖥️",
                    color="gray",
                    card_id="desktop-stat"
                ),
                create_stat_card(
                    label="Mobile",
                    icon="📱",
                    color="gray",
                    card_id="mobile-stat"
                ),
                create_stat_card(
                    label="Tablet",
                    icon="📲",
                    color="gray",
                    card_id="tablet-stat"
                ),
                create_stat_card(
                    label="Bots",
                    icon="🤖",
                    color="gray",
                    card_id="bot-stat"
                ),
            ]
        ),

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
    """Create a table showing recent bot visits."""
    if not bot_visits:
        return dmc.Text("No bot visits yet. Bots will be tracked automatically.", c="dimmed", fs="italic")

    rows = []
    for visit in bot_visits:
        timestamp = visit.get('timestamp', 'Unknown')
        try:
            dt = datetime.fromisoformat(timestamp)
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            time_str = timestamp

        bot_type = visit.get('bot_type', 'unknown')

        # Color code by bot type
        if bot_type == 'training':
            badge = dmc.Badge("Training", color="red", size="sm", variant="filled")
        elif bot_type == 'search':
            badge = dmc.Badge("Search", color="blue", size="sm", variant="filled")
        elif bot_type == 'traditional':
            badge = dmc.Badge("Traditional", color="green", size="sm", variant="filled")
        else:
            badge = dmc.Badge("Unknown", color="gray", size="sm", variant="outline")

        user_agent = visit.get('user_agent', 'Unknown')
        truncated_ua = user_agent[:80] + "..." if len(user_agent) > 80 else user_agent

        rows.append(
            dmc.TableTr([
                dmc.TableTd(dmc.Text(time_str, size="sm", ff="monospace")),
                dmc.TableTd(badge),
                dmc.TableTd(dmc.Code(visit.get('path', '/'), style={"fontSize": "12px"})),
                dmc.TableTd(dmc.Text(truncated_ua, size="xs", c="dimmed", style={"maxWidth": "400px"})),
            ])
        )

    return dmc.Table([
        dmc.TableThead(
            dmc.TableTr([
                dmc.TableTh("Timestamp"),
                dmc.TableTh("Bot Type"),
                dmc.TableTh("Page"),
                dmc.TableTh("User Agent"),
            ])
        ),
        dmc.TableTbody(rows),
    ], striped=True, highlightOnHover=True, withTableBorder=True, withColumnBorders=True)


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

    top_pages = get_top_pages(data['visits'])
    top_pages_data = [
        {"page": page, "visits": count}
        for page, count in top_pages
    ]

    if not top_pages_data:
        return dmc.Center(dmc.Text("No page visits yet", c="dimmed", fs="italic"), h=350)

    return dmc.BarChart(
        data=top_pages_data,
        dataKey="page",
        series=[{"name": "visits", "color": "violet.6"}],
        h=350,
        orientation="horizontal",
        withLegend=False,
        yAxisLabel="Page",
        xAxisLabel="Visits",
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
