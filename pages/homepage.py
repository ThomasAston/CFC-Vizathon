from dash import html, dcc
import pages.highlights as highlights
import pages.squads as squads
from dash import Input, Output, callback

layout = html.Div([
    # Tabs outside the padded content
    dcc.Tabs(id="main-tabs", value="Squads", mobile_breakpoint=0, children=[
        dcc.Tab(label="Highlights", value="Highlights"),
        dcc.Tab(label="Squads", value="Squads"),
    ]),
    # Wrap only the dynamic content in padding
    html.Div(id="main-tab-content", className="page-content")
])

@callback(
    Output("main-tab-content", "children"),
    Input("main-tabs", "value")
)
def render_main_tab(tab):
    if tab == "Highlights":
        return highlights.layout
    elif tab == "Squads":
        return squads.layout
