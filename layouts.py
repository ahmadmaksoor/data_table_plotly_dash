import dash_core_components as dcc
from datetime import datetime,timedelta
import dash_html_components as html
import dash_bootstrap_components as dbc


tab_style_div1 = {
    "textAlign": "left",
    "padding": "70px 0px",
    "position": "absolute",
    "height": "0%",
    "width": "0%",
}


tab_style_div2 = {"margin-right": "100px", "padding": "22px 0px"}


style_bouton = {"marginTop": 20, "marginBottom": 15}


layout = html.Div(
    [
        dbc.Alert(
            children=[],
            id="alert",
            is_open=False,
            style={"marginTop": 20, "marginBottom": 15, "color": "red"},
        ),
        dcc.Dropdown(id="keyspace", options=[], style={"margin-right": "80%"}),
        html.Div(
            id="tabs-content",
            style=tab_style_div1,
            children=[
                dcc.Tabs(id="tabs_id", vertical=True, children=[], value="tab-1")
            ],
        ),
        dcc.Download(id="download-dataframe-csv"),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            "Max number of rows: ",
                            dcc.Input(
                                id="number_limit_id",
                                value=5000,
                                type="number",
                                debounce=True,
                                placeholder="Number of rows",
                            ),
                        ],
                        style={"marginTop": 20, "marginBottom": 15},
                    ),
                    width="auto",
                ),
                dbc.Col(
                    html.Div(
                        [
                            dcc.Dropdown(
                                id="drop_down",
                                options=[{"label": "All", "value": "All"}],
                                value="All",
                                multi=True,
                            ),
                        ],
                        id="test",
                        style={
                            "marginTop": 20,
                            "marginBottom": 15,
                        },
                    ),
                    width="auto",
                ),
                dbc.Col(
                    html.Div(
                        [
                            dcc.DatePickerRange(
                                id="my-date-picker-range",
                                display_format="D/M/YYYY",
                                persistence=True,
                                clearable=True,
                                min_date_allowed=datetime(2018, 7, 1),
                                max_date_allowed=datetime.today()+timedelta(days=8),
                                initial_visible_month=datetime.today(),
                                end_date=datetime(2022, 8, 25),
                            )
                        ],
                        style={"marginTop": 20, "marginBottom": 15},
                    ),
                    width="auto",
                ),
                dbc.Col(
                    dbc.Button("Export data to csv", id="btn_csv", style=style_bouton),
                    width="auto",
                ),
                dbc.Col(
                    dcc.Loading(
                        id="loading-1",
                        type="circle",
                        children=html.Div(
                            id="loading-output",
                            style={"marginTop": 20, "marginBottom": 15},
                        ),
                    ),
                    width="auto",
                    style={"marginTop": 20, "marginBottom": 15},
                ),
                dbc.Col(
                    dcc.Loading(
                        id="loading-2",
                        type="circle",
                        children=html.Div(
                            id="loading-output-tables",
                            style={"marginTop": 20, "marginBottom": 15},
                        ),
                    ),
                    width="auto",
                    style={"marginTop": 20, "marginBottom": 15},
                ),
                dbc.Col(
                    html.Div(
                        id="load",
                        style={
                            "color": "green",
                            "background-color": "#caf0cf",
                            "border-color": "#caf0cf",
                            "border-radius": "5px",
                            "-webkit-animation": "cssAnimation 0s ease-in 5s forwards",
                        },
                    ),
                    width="auto",
                    style={"marginTop": 25, "marginBottom": 15},
                ),
                
            ],
            style={"flex-wrap": "nowrap"},
        ),
        html.Div(id="hide_div"),
        dcc.Store(id='memory'),
        dcc.Interval(
            id='interval-component',
            interval=4*10000000, # in milliseconds (11 hours)
            n_intervals=0
        )
    ]
)
