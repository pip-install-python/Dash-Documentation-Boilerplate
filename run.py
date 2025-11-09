import dash
from dash import Dash, _dash_renderer
import json
from flask import jsonify
from components.appshell import create_appshell
import dash_mantine_components as dmc

_dash_renderer._set_react_version("18.2.0")

stylesheets = [
    dmc.styles.ALL
]

scripts = [
    "https://cdnjs.cloudflare.com/ajax/libs/dayjs/1.10.8/dayjs.min.js",
    "https://unpkg.com/hotkeys-js/dist/hotkeys.min.js",
]


app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    use_pages=True,
    external_scripts=scripts,
    external_stylesheets=stylesheets,
    update_title=None,
    prevent_initial_callbacks=True,
    index_string=open('templates/index.html').read()  # Add this line
)


app.layout = create_appshell(dash.page_registry.values())

server = app.server


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port='8552')