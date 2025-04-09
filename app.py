from dash import Dash, dcc, html, Input, Output
import pages.homepage as homepage
import pages.biography as biography
import pages.highlights as highlights
import pages.squads as squads

app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    if pathname == "/" or pathname == "/home":
        return homepage.layout
    elif pathname.startswith("/player/"):
        player_id = pathname.split("/player/")[1]
        return biography.render(player_id)
    else:
        return html.Div([html.H1("404 - Page not found")])

import os

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8050)),
        debug=False
    )