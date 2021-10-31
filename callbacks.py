# -*- coding: utf-8 -*-
# """
# Created on Tue May 18 16:16:47 2021

# @author: Ahmad ALMAKSOUR
# """

import dash
import dash_core_components as dcc
from datetime import datetime,timedelta
import dash_table
from dash.dependencies import Input, Output, State
from flask_caching import Cache
from app import app
import pandas as pd
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from cassandra.query import dict_factory
import time
import io
from flask import request,current_app
from csv import DictWriter
from layouts import layout
# %% Setup 
TIMEOUT = 60
def pandas_factory(colnames, rows):
    return pd.DataFrame(rows, columns=colnames)    

################### Memory cache #################
cache = Cache(
    app.server, config={"CACHE_TYPE": "filesystem", "CACHE_DIR": "cache-directory"} )
app.config.suppress_callback_exceptions = True
    
# %% callback to establish the connection with cassandra database
@app.callback(Output('page-content', 'children'),
              Output("hide_div", "children"),
              Output('hidden','style'),
              Output('db_login','style'),
              Output('loading','children'),
              Output("alert_connection", "children"),
              Output("alert_connection", "is_open"),    
              Input("db_login", "n_clicks"),
              Input("alert_connection", "children"),
              State('db-url', 'value'),
              State('name', 'value'),
              State('password', 'value'),
              State("alert_connection", "is_open"),
              State('page-content', 'children'),
              prevent_initial_call=True)
def connection(n_clicks,children_alert,url,name,mot_pass,is_open,page_content):
    is_open = False
    children_alert = []
    if ',' in url:
            db_url= url.split(',')
    else :    
            db_url = [url]
    username = name
    layout1=layout            
    display= {'display': 'none'}
    password = mot_pass
    auth_provider = PlainTextAuthProvider(username=username, password=password)
    try :    
        cluster = Cluster(db_url, auth_provider=auth_provider,connect_timeout=2)
        session2 = cluster.connect()
        session2.default_fetch_size = None
        current_app.cass_session=session2  # storage the seesion in current_app to use it an any callback
        current_app.cass_cluster=cluster 
    except Exception as e :
            children_alert = ["informations incorrect !"]
            is_open = True
            layout1=page_content
    print(is_open)
    #print(db_url)
    if is_open == True : 
        print("incorrect")
        return layout1,"",{'display': 'block'},{'display': 'block'},"",children_alert,is_open
    else : 
       print("correct")
       return layout1,"",{'display': 'none'},{'display': 'none'},"",children_alert,is_open
        
# %% kesapces dropdown 
# callback to get the keyspaces and define the access rights for each user
@app.callback(Output("keyspace", "options"), Input("hide_div", "children"),prevent_initial_call=True)
def keyspaces_name(option):
    option=[]
    cluster=current_app.cass_cluster 
    session_n = current_app.cass_session #session2  
    username = request.authorization["username"]
    if username == "admin":
        keyspaces = [key for key in cluster.metadata.keyspaces if "system" not in key]
    else:
        keyspaces = [
            key
            for key in cluster.metadata.keyspaces
            if "system" not in key and "reaper" not in key
        ]
    if keyspaces:
        for keyspace in keyspaces:
            option.append({"label": keyspace, "value": keyspace})
    
    return option

# %% callback to display tabs, tables with the data
#and display the data filtered by date (date picker range)
@app.callback(
    [
     Output("tabs_id", "children"),
     Output("alert", "children"),
     Output("alert", "is_open"),
     Output("number_limit_id", "value"),
     Output("loading-output-tables", "children"),
     Output("load", "children"),
    ],
    Input("tabs_id", "value"),
    Input("keyspace", "value"),
    Input("number_limit_id", "value"),
    dash.dependencies.Input("my-date-picker-range", "start_date"),
    dash.dependencies.Input("my-date-picker-range", "end_date"),
    Input("drop_down", "value"),
    Input("alert", "children"),
    Input("load", "value"),
    State("tabs_id", "children"),
    State("alert", "is_open"),
    prevent_initial_call=True,
)
@cache.memoize(timeout=TIMEOUT) # stores the results of this call back after it is called and re-uses the result
def update_content(tab,keyspace,limits,start_date,end_date,drop_down,children_alert,loaded,children,is_open,):
    df1 = []
    df = []
    session2=current_app.cass_session
    cluster=current_app.cass_cluster
    tables = [key for key in cluster.metadata.keyspaces[keyspace].tables]
    session = session2
    session.set_keyspace(keyspace)
    if limits > 500000:
        limits = 500000
        children_alert = ["Maximum number  of rows is 500000"]
        is_open = True #display an alert to the user

    else:
        children_alert = []
        is_open = False

    if tab in tables:
        cols= [key for key in cluster.metadata.keyspaces[keyspace].tables[tab].columns]
        lowercase= [key.lower() for key in cluster.metadata.keyspaces[keyspace].tables[tab].columns]
        if "All" in drop_down: #select all columns
        
            if start_date is None: # si on ne filtre pas par date 
                query1 = ('''SELECT * FROM "''' + tab + """" LIMIT """ + str(limits) + """ """)
                
            else:
                if 'date' in lowercase:     
                    query1 = ( '''SELECT * FROM "'''+ tab + '''" where "'''+cols[lowercase.index('date')]+'''" > %s and "'''+
                              cols[lowercase.index('date')]+'''" < %s LIMIT '''+str(limits)+''' ALLOW FILTERING''')

        else: #select some columns

            if start_date is None:
                query1 = ( """SELECT """ + ",".join([f'"{str(i)}"' for i in drop_down]) + ''' FROM "''' + tab
                          + """" LIMIT """+ str(limits) + """ """)

            else:
                
                if 'date' in lowercase:     
                    date_col=cols[lowercase.index('date')]
                    query1 = ( '''SELECT'''+ ",".join([f'"{str(i)}"' for i in drop_down])+ '''FROM "'''+ tab + '''" where "'''
                              +date_col+'''" > %s and "'''
                              +date_col+'''" < %s LIMIT '''+str(limits)+''' ALLOW FILTERING''')
                                        
        try:
            session.row_factory = dict_factory
            rslt1 = session.execute(query1, timeout=None) if start_date is None else session.execute(query1, (start_date, end_date), timeout=None)
            df1 = rslt1._current_rows

        except Exception as e:
            if "Unauthorized" in str(type(e)) or "Undefined column" in str(e):
                children_alert = ["Unauthorized access !"]
                is_open = True
        if df1:
             df = df1

        col = [key for key in cluster.metadata.keyspaces[keyspace].tables[tab].columns if is_open == False]
    children = []
    for ele in tables:

        if ele != tab:
            children.append(dcc.Tab(label=ele, value=ele))
        else:
            if df == []: #if the table is empty
                children.append(
                    dcc.Tab(
                        label=ele,
                        value=ele,
                        children=[
                            dash_table.DataTable(
                                id="dash-table",
                                columns=[{"id": i, "name": i} for i in col],
                                data=df,
                                style_header={
                                    "backgroundColor": "lavender",
                                    "fontWeight": "bold",
                                },
                                style_table={
                                    "height": "80vh",
                                    "width": "100%",
                                    "padding": "0px 22px",
                                    "overflow": "auto",
                                },
                            )
                        ],
                    )
                )

            else:
                children.append(
                    dcc.Tab(
                        label=ele,
                        value=ele,
                        children=[
                            dash_table.DataTable(
                                id="dash-table",
                                columns=[
                                    {"id": i, "name": i} for i in list(df[0].keys())
                                ],
                                data=df,
                                filter_action="native",
                                style_cell={
                                    "whiteSpace": "normal",
                                    "textAlign": "center",
                                    "minWidth": "200px",
                                    "maxWidth": "200px",
                                    "width": "200px",
                                },
                                style_header={
                                    "backgroundColor": "lavender",
                                    "fontWeight": "bold",
                                },
                                style_table={
                                    "height": "79vh",
                                    "width": "100%",
                                    "padding": "0px 22px",
                                    "overflow": "auto",
                                },
                                style_data_conditional=[
                                    {
                                        "if": {"row_index": "odd"},
                                        "backgroundColor": "rgb(248, 248, 248)",
                                    }
                                ],
                                sort_action="native",
                            )
                        ],
                    )
                )

    del session
    
    if len(children_alert) >= 1:
        is_open = True


    ctx = dash.callback_context
    c = ctx.triggered[0]["prop_id"].split(".")[0] #to know which input is triggered
    if c != "keyspace": #to avoid Rows loaded from being displayed when choosing the keyspaces before choosing the tables
        loaded = str(len(df)) + " Rows loaded" #number of lines loaded
            
    return (children, children_alert, is_open, limits, "", loaded)


# %% callback to export the data in csv format
@app.callback(
    Output("download-dataframe-csv", "data"),
    Output("loading-output", "children"),
    Input("btn_csv", "n_clicks"),
    State("tabs_id", "value"),
    State("keyspace", "value"),
    State("dash-table", "data"),
    prevent_initial_call=True,
)
def download_data(n_clicks, tab, keyspace, data):
    now=datetime.now()
    download_buffer = io.StringIO()
    writer = DictWriter(download_buffer, (list(data[0].keys()))) ## columns
    writer.writeheader()
    writer.writerows(data)
    content = download_buffer.getvalue()
    download_buffer.close()
    return (
        dict(
            content=content,
            filename= now.strftime('%Y-%m-%d_%H:%M') + "_" + keyspace + "_" + tab + ".csv",
        ),
        "",
    )

# %% callback to select columns
@app.callback(
    Output("drop_down", "options"),
    Input("tabs_id", "value"),
    Input("keyspace", "value"),
    Input("drop_down", "options"),
    Input("tabs_id", "children"),
    State("dash-table", "data"),
    State("alert", "is_open"),
    prevent_initial_call=True,
)
def dropdown_data(tab, keyspace, option, children, data, is_open):
    option = []
    #session2=current_app.cass_session
    cluster=current_app.cass_cluster
    columns = [key for key in cluster.metadata.keyspaces[keyspace].tables[tab].columns]
    if columns:
        option.append({"label": "All", "value": "All"})
        for column in columns:
            option.append({"label": column, "value": column})
    return option


@app.callback(
    Output("drop_down", "value"),
    Input("tabs_id", "value"),
    Input("drop_down", "value"),
    prevent_initial_call=True,
)
def update_dropdown(tab, dropdown):

    ctx = dash.callback_context
    c = ctx.triggered[0]["prop_id"].split(".")[0]
    if c == "tabs_id":
        return ["All"]

    elif c == "drop_down":
        if "All" in dropdown and len(dropdown) > 1:
            if "All" == dropdown[-1]:
                return ["All"]
            dropdown.remove("All")
            return dropdown

        return dropdown
    else:
        raise "error"

# %% callback to update today's date
@app.callback(
        Output("my-date-picker-range","max_date_allowed"),
        Input("interval-component", "n_intervals"),
        prevent_initial_call=True,
        )
def update_date(n):
    return datetime.today()+timedelta(days=8)