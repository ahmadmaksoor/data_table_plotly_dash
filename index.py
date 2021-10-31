import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash
from app import app
import callbacks

db_url = "10.64.265.11"
username = "user"
password = "pass"

app.layout = html.Div(
    [
        html.Div(id="page-content"),
        html.Div(id="hide_div"),
        dbc.Alert(
            children=[],
            id="alert_connection",
            dismissable=True,
            is_open=False,
            style={"marginTop": 20, "marginBottom": 15, "color": "red"},
        ),
        html.Div(
            [
                "database url: ",
                dcc.Input(
                    id="db-url",
                    type="text",
                    debounce=True,
                    style={"marginTop": 20, "marginBottom": 15, "margin-right": "50px"},
                ),
                "username: ",
                dcc.Input(
                    id="name",
                    type="text",
                    debounce=True,
                    style={"marginTop": 20, "marginBottom": 15, "margin-right": "50px"},
                ),
                "password : ",
                dcc.Input(
                    id="password",
                    type="password",
                    debounce=True,
                    style={"marginTop": 20, "marginBottom": 15, "margin-right": "50px"},
                ),
            ],
            id="hidden",
        ),
        dcc.Loading(
            id="loading-2",
            type="circle",
            children=html.Div(
                id="loading",
            ),
            style={"margin-right": "50%", "marginTop": "1.5%"},
        ),
        html.Button(
            "Connection to cassandra database",
            id="db_login",
            n_clicks=0,
        ),
    ]
)

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8079, threaded=True)
