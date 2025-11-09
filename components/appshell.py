import dash_mantine_components as dmc
from dash import Output, Input, clientside_callback, dcc, page_container, State

from components.header import create_header
from components.navbar import create_navbar, create_navbar_drawer
from lib.constants import PRIMARY_COLOR


def create_appshell(data):
    return dmc.MantineProvider(
        id="m2d-mantine-provider",
        theme={
            "primaryColor": PRIMARY_COLOR,
            "fontFamily": "'Inter', sans-serif",
            "components": {
                "Button": {"defaultProps": {"fw": 400}},
                "Alert": {"styles": {"title": {"fontWeight": 500}}},
                "AvatarGroup": {"styles": {"truncated": {"fontWeight": 500}}},
                "Badge": {"styles": {"root": {"fontWeight": 500}}},
                "Progress": {"styles": {"label": {"fontWeight": 500}}},
                "RingProgress": {"styles": {"label": {"fontWeight": 500}}},
                "CodeHighlightTabs": {"styles": {"file": {"padding": 12}}},
                "Table": {
                    "defaultProps": {
                        "highlightOnHover": True,
                        "withTableBorder": True,
                        "verticalSpacing": "sm",
                        "horizontalSpacing": "md",
                    }
                },
            },
            "colors": {
                "myColor": [
                    "#F2FFB6",
                    "#DCF97E",
                    "#C3E35B",
                    "#AAC944",
                    "#98BC20",
                    "#86AC09",
                    "#78A000",
                    "#668B00",
                    "#547200",
                    "#455D00",
                ]
            },
        },
        children=[
            dcc.Location(id="url", refresh="callback-nav"),
            dcc.Store(id="color-scheme-storage", storage_type="local"),
            dmc.NotificationContainer(),
            dmc.AppShell(
                [
                    create_header(data),
                    create_navbar(data),
                    create_navbar_drawer(data),
                    dmc.AppShellMain(children=page_container),
                ],
                header={"height": 70},
                padding="xl",
                navbar={
                    "width": 300,
                    "breakpoint": "lg",
                    "collapsed": {"mobile": True},
                },
                aside={
                    "width": 300,
                    "breakpoint": "xl",
                    "collapsed": {"desktop": False, "mobile": True},
                },
            ),
        ],
    )


# Initialize theme from localStorage or browser preference on page load
clientside_callback(
    """
    function(pathname) {
        // Check if theme is already stored in localStorage
        const storedTheme = localStorage.getItem('color-scheme-storage');
        if (storedTheme) {
            try {
                const parsed = JSON.parse(storedTheme);
                return parsed;
            } catch (e) {
                // If parsing fails, fall through to default logic
            }
        }

        // Check browser preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }

        // Default to light theme
        return 'light';
    }
    """,
    Output("color-scheme-storage", "data"),
    Input("url", "pathname"),
)

# Apply theme from storage to MantineProvider
clientside_callback(
    """
    function(colorScheme) {
        // Default to light if no theme is set
        return colorScheme || 'light';
    }
    """,
    Output("m2d-mantine-provider", "forceColorScheme"),
    Input("color-scheme-storage", "data")
)

# Toggle theme when button is clicked
clientside_callback(
    """
    function(n_clicks, theme) {
        // Toggle between light and dark
        const newTheme = theme === 'dark' ? 'light' : 'dark';
        return newTheme;
    }
    """,
    Output("color-scheme-storage", "data", allow_duplicate=True),
    Input("color-scheme-toggle", "n_clicks"),
    State("color-scheme-storage", "data"),
    prevent_initial_call=True,
)