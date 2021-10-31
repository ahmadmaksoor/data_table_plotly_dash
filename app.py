import dash
import dash_bootstrap_components as dbc
import dash
import dash_auth


external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css", dbc.themes.GRID]


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server


################ Authentification ############
VALID_USERNAME_PASSWORD_PAIRS = {"admin": "admin", "user": "password"}

auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)


