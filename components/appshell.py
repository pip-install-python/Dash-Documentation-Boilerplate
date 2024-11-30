import dash_mantine_components as dmc
from dash import Output, Input, clientside_callback, dcc, page_container, State

from components.header import create_header
from components.navbar import create_navbar, create_navbar_drawer
from lib.constants import PRIMARY_COLOR


def create_appshell(data):
    return dmc.MantineProvider(
        id="m2d-mantine-provider",
        forceColorScheme="light",
        theme={
            "primaryColor": PRIMARY_COLOR,
            "fontFamily": "'Inter', sans-serif",
            "components": {
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
            "colors":{
                "dark": [
                    "#f4f4f5",
                    "#e4e4e7",
                    "#d4d4d8",
                    "#a1a1aa",
                    "#71717a",
                    "#52525b",
                    "#3f3f46",
                    "#27272a",
                    "#18181b",
                    "#09090b",
                ],
            }
        },
        children=[
            dcc.Store(id="theme-store", storage_type="local", data="light"),
            dcc.Location(id="url", refresh="callback-nav"),
            dmc.NotificationProvider(zIndex=2000),
            dmc.AppShell(
                [
                    create_header(data),
                    create_navbar(data),
                    create_navbar_drawer(data),
                    dmc.AppShellMain(children=page_container),
                ],
                header={"height": 70},
                padding="xl",
                zIndex=1400,
                navbar={
                    "width": 300,
                    "breakpoint": "lg",
                    "collapsed": {"mobile": True},
                },
                aside={
                    "margin-top":'10px',
                    "width": 300,
                    "breakpoint": "xl",
                    "collapsed": {"desktop": False, "mobile": True},
                },
            ),
        ],
    )


clientside_callback(
    """
    function(data) {
        return data
    }
    """,
    Output("m2d-mantine-provider", "forceColorScheme"),
    Input("theme-store", "data"),
)

clientside_callback(
    """
    function(data) {
        const box = document.getElementById("ethical-ads-box");
        if (data === "dark") {
            box.classList.add("dark");
        } else {
            box.classList.remove("dark");
        }
        return dash_clientside.no_update
    }
    """,
    Output("ethical-ads-box", "className"),
    Input("theme-store", "data"),
)

clientside_callback(
    """
    function(n_clicks, data) {
        return data === "dark" ? "light" : "dark";
    }
    """,
    Output("theme-store", "data"),
    Input("color-scheme-toggle", "n_clicks"),
    State("theme-store", "data"),
    prevent_initial_call=True,
)
