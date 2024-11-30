import dash_mantine_components as dmc
from dash import Output, Input, clientside_callback, html, get_asset_url
from dash_iconify import DashIconify


def create_link(icon, href):
    return dmc.Anchor(
        dmc.ActionIcon(
            DashIconify(icon=icon, width=25), variant="transparent", size="lg", color="blue"
        ),
        href=href,
        target="_blank",
        visibleFrom="xs",
    )


def create_search(data):
    return dmc.Select(
        id="select-component",
        placeholder="Search",
        mt=-2,
        searchable=True,
        clearable=True,
        w=250,
        nothingFoundMessage="Nothing Found!",
        rightSectionWidth=60,
        leftSection=DashIconify(icon="mingcute:search-3-line"),
        data=[
            {"label": component["name"], "value": component["path"]}
            for component in data
            if component["name"] not in ["Home", "Not found 404"]
        ],
        visibleFrom="sm",
        comboboxProps={"zIndex": 2000},
    )


def create_header(data):
    return dmc.AppShellHeader(
        px=25,
        children=[
            dmc.Stack(
                justify="center",
                h=70,
                children=dmc.Grid(
                    justify="space-between",
                    children=[
                        dmc.GridCol(
                            dmc.Group(
                                [
                                    dmc.ActionIcon(
                                        DashIconify(
                                            icon="radix-icons:hamburger-menu",
                                            width=25,
                                        ),
                                        id="drawer-hamburger-button",
                                        variant="transparent",
                                        size="lg",
                                        hiddenFrom="lg",
                                        style={'color': '#0094ce'}
                                    ),
                                    dmc.Anchor(
                                         [html.Img(src=get_asset_url('dash_documentation_boilerplate.png'), style={'height':'40px', 'width':'40px', 'margin-right':'8px'}), "Boilerplate"], size="xl", href="/", underline=False,
                                    style={'color': '#0094ce', 'display': 'flex', 'align-items': 'center'}
                                    ),
                                ],
                                gap="md",
                            ),
                            span="content",
                        ),
                        dmc.GridCol(
                            span="auto",
                            children=dmc.Group(
                                justify="flex-end",
                                h=31,
                                gap="md",
                                children=[
                                    create_search(data),
                                    create_link(
                                        "radix-icons:github-logo",
                                        "https://github.com/pip-install-python/Dash-Documentation-Boilerplate",

                                    ),
                                    dmc.ActionIcon(
                                        [
                                            DashIconify(
                                                icon="radix-icons:sun",
                                                width=25,
                                                id="light-theme-icon",
                                            ),
                                            DashIconify(
                                                icon="radix-icons:moon",
                                                width=25,
                                                id="dark-theme-icon",
                                            ),
                                        ],
                                        variant="transparent",
                                        color="yellow",
                                        id="color-scheme-toggle",
                                        size="lg",

                                    ),
                                ],
                            ),
                        ),
                    ],
                ),
            )
        ],
    )


clientside_callback(
    """
    function(value) {
        if (value) {
            return value
        }
    }
    """,
    Output("url", "href"),
    Input("select-component", "value"),
)

clientside_callback(
    """function(n_clicks) { return true }""",
    Output("components-navbar-drawer", "opened"),
    Input("drawer-hamburger-button", "n_clicks"),
    prevent_initial_call=True,
)
