"""
Analytics Page - Visitor Analytics Dashboard

This page demonstrates visitor tracking with device and bot detection.
"""
import dash_mantine_components as dmc
from dash import Input, Output, callback, html, register_page
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
    analytics = load_analytics()
    visits = analytics["visits"]
    stats = analytics["stats"]

    # Prepare data for charts
    device_data = [
        {"name": "Desktop", "value": stats['desktop'], "color": "violet.6"},
        {"name": "Mobile", "value": stats['mobile'], "color": "blue.6"},
        {"name": "Tablet", "value": stats['tablet'], "color": "green.6"},
        {"name": "Bots", "value": stats['bot'], "color": "yellow.6"},
    ]
    # Filter out zero values
    device_data = [d for d in device_data if d["value"] > 0]

    # Bot types data
    bot_types = get_bot_visits_by_type(visits)
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

    # Hourly visits data
    hourly_counts = get_visits_by_hour(visits)
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

    # Top pages data
    top_pages = get_top_pages(visits)
    top_pages_data = [
        {"page": page, "visits": count}
        for page, count in top_pages
    ]

    # Get recent bot visits with details
    recent_bot_visits = [v for v in visits if v["device_type"] == "bot"][-20:]
    recent_bot_visits.reverse()

    return dmc.Container([
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
                        "Data updates automatically on each visit."
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
                    value=stats['total'],
                    label="Total Visits",
                    icon="📊",
                    color="violet",
                    card_id="total-stat"
                ),
                create_stat_card(
                    value=stats['desktop'],
                    label="Desktop",
                    icon="🖥️",
                    color="gray",
                    card_id="desktop-stat"
                ),
                create_stat_card(
                    value=stats['mobile'],
                    label="Mobile",
                    icon="📱",
                    color="gray",
                    card_id="mobile-stat"
                ),
                create_stat_card(
                    value=stats['tablet'],
                    label="Tablet",
                    icon="📲",
                    color="gray",
                    card_id="tablet-stat"
                ),
                create_stat_card(
                    value=stats['bot'],
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
                    create_chart_card(
                        title="Device Distribution",
                        description="Breakdown by device type",
                        chart=dmc.PieChart(
                            id="device-chart",
                            data=device_data if device_data else [{"name": "No visits yet", "value": 1, "color": "gray.3"}],
                            size=200,
                            withLabelsLine=True,
                            labelsPosition="outside",
                            labelsType="percent",
                            withLabels=True,
                            tooltipDataSource="segment",
                            h=350,
                        ) if device_data else dmc.Center(
                            dmc.Text("No visit data yet", c="dimmed", fs="italic"),
                            h=350
                        )
                    ),
                    create_chart_card(
                        title="Bot Types",
                        description="AI Training, Search, and Traditional bots",
                        chart=dmc.BarChart(
                            id="bot-types-chart",
                            data=bot_data if bot_data else [],
                            dataKey="type",
                            series=[{"name": "visits", "color": "blue.6"}],
                            h=350,
                            withLegend=False,
                            yAxisLabel="Visits",
                            xAxisLabel="Bot Type",
                        ) if bot_data else dmc.Center(
                            dmc.Text("No bot visits yet", c="dimmed", fs="italic"),
                            h=350
                        )
                    ),
                ]
            ),

            # Hourly visits
            create_chart_card(
                title="Visits by Hour",
                description="Activity over the last 24 hours",
                chart=dmc.AreaChart(
                    id="hourly-chart",
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
                ) if hourly_data and any(sum(h.values()) for h in hourly_counts.values()) else dmc.Center(
                    dmc.Text("No visit data available", c="dimmed", fs="italic"),
                    h=350
                )
            ),

            # Top pages
            create_chart_card(
                title="Most Visited Pages",
                description="Top 10 pages by visit count",
                chart=dmc.BarChart(
                    id="top-pages-chart",
                    data=top_pages_data if top_pages_data else [],
                    dataKey="page",
                    series=[{"name": "visits", "color": "violet.6"}],
                    h=350,
                    orientation="horizontal",
                    withLegend=False,
                    yAxisLabel="Page",
                    xAxisLabel="Visits",
                ) if top_pages_data else dmc.Center(
                    dmc.Text("No page visits yet", c="dimmed", fs="italic"),
                    h=350
                )
            ),

            # Bot visits table
            dmc.Paper([
                dmc.Title("Recent Bot Visits", order=3, mb="md"),
                create_bot_visits_table(recent_bot_visits) if recent_bot_visits else dmc.Text(
                    "No bot visits yet. Bots will be tracked automatically.",
                    c="dimmed",
                    fs="italic"
                ),
            ], p="lg", radius="md", withBorder=True),
        ], gap="lg"),

    ], size="xl", py="xl")


def create_stat_card(value, label, icon, color="violet", card_id=None):
    """Create a stat card."""
    return dmc.Paper([
        dmc.Stack([
            dmc.Group([
                dmc.Text(icon, size="xl"),
                dmc.Title(
                    f"{value:,}",
                    order=2,
                    c=f"{color}.6" if color != "gray" else None
                ),
            ], gap="xs", justify="center"),
            dmc.Text(label, size="sm", c="dimmed", ta="center"),
        ], gap="xs", align="center"),
    ], p="lg", radius="md", withBorder=True, shadow="sm", id=card_id)


def create_chart_card(title, description, chart):
    """Create a chart card."""
    return dmc.Paper([
        dmc.Stack([
            dmc.Stack([
                dmc.Title(title, order=3),
                dmc.Text(description, size="sm", c="dimmed"),
            ], gap=4),
            chart,
        ], gap="md"),
    ], p="lg", radius="md", withBorder=True, shadow="sm")


def create_bot_visits_table(bot_visits):
    """Create a table showing recent bot visits."""
    if not bot_visits:
        return dmc.Text("No bot visits recorded yet.", c="dimmed", fs="italic")

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
