from dash import Dash, dcc, html, Input, Output
import pages.homepage as homepage
import pages.biography as biography
from DATA.players import (
    senior_squad, u21s_squad, fa_youth_squad, u18s_squad,
    on_loan_squad, staff_squad, opposition_teams
)

app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


# Main router
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == "/":
        return homepage.layout
    elif pathname.startswith("/player/"):
        player_id = pathname.split("/player/")[1]
        return biography.layout(player_id)
    else:
        return html.Div([html.H1("404 - Page not found")])


# Squad tabs (Chelsea internal squads)
@app.callback(
    Output('squad-content', 'children'),
    Input('squad-tabs', 'value')
)
def update_my_squad(tab_value):
    if tab_value == 'Senior':
        return homepage.render_squad_list(senior_squad)
    elif tab_value == 'U21s':
        return homepage.render_squad_list(u21s_squad)
    elif tab_value == 'FAYouth':
        return homepage.render_squad_list(fa_youth_squad)
    elif tab_value == 'U18s':
        return homepage.render_squad_list(u18s_squad)
    elif tab_value == 'OnLoan':
        return homepage.render_squad_list(on_loan_squad)
    elif tab_value == 'Staff':
        return homepage.render_squad_list(staff_squad)
    return html.Div("Invalid squad")


# Opposition dropdown
@app.callback(
    Output('opposition-content', 'children'),
    Input('opposition-dropdown', 'value')
)
def update_opposition_squad(team_name):
    return homepage.render_squad_list(opposition_teams.get(team_name, []))


if __name__ == '__main__':
    app.run(debug=True)
