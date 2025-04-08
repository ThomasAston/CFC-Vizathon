from dash import dcc, html, Input, Output, callback
import json
from pages.player_card import render_player_cards_by_position

# Load pre-fetched structured squad data from your JSON file
with open("DATA/players.json") as f:
    squad_data = json.load(f)

layout = html.Div([
    dcc.Tabs(id="squad-type-tabs", value="MySquads", mobile_breakpoint=0, children=[
        dcc.Tab(label="My Squads", value="MySquads"),
        dcc.Tab(label="Opposition", value="Opposition")
    ]),
    html.Div(id="squad-type-content", style={"padding": "12px"})
])

@callback(
    Output("squad-type-content", "children"),
    Input("squad-type-tabs", "value")
)
def render_squad_type_tab(tab):
    if tab == "MySquads":
        options = list(squad_data["chelsea_squads"].keys())
        return html.Div([
            html.H3("Select a squad...", style={"font-family": "CFC Serif"}),
            dcc.Dropdown(
                id="squad-dropdown",
                options=[{"label": name, "value": name} for name in options],
                value=options[0],
                clearable=False,
                searchable=False,
                style={"width": "250px", "margin-bottom": "25px"}
            ),
            html.Div(id="squad-dropdown-content")
        ])

    elif tab == "Opposition":
        my_squads = list(squad_data["opposition"].keys())
        return html.Div([
            html.H3("Select a squad...", style={"font-family": "CFC Serif"}),
            dcc.Dropdown(
                id="oppo-squad-dropdown",
                options=[{"label": name, "value": name} for name in my_squads],
                value=my_squads[0],
                clearable=False,
                searchable=False,
                style={"width": "350px", "margin-bottom": "20px"}
            ),
            html.H3("Select a competition...", style={"font-family": "CFC Serif"}),
            dcc.Dropdown(
                id="competition-dropdown",
                clearable=False,
                searchable=False,
                style={"width": "350px", "margin-bottom": "20px"}
            ),
            html.H3("Select an opposition...", style={"font-family": "CFC Serif"}),
            dcc.Dropdown(
                id="opposition-dropdown",
                clearable=False,
                searchable=False,
                style={"width": "350px", "margin-bottom": "20px"}
            ),
            html.Div(id="opposition-squad-content")
        ])

@callback(
    Output("competition-dropdown", "options"),
    Output("competition-dropdown", "value"),
    Input("oppo-squad-dropdown", "value")
)
def update_competitions(squad_name):
    competitions = squad_data["opposition"].get(squad_name, {})
    options = [{"label": c, "value": c} for c in competitions]
    return options, options[0]["value"] if options else None

@callback(
    Output("opposition-dropdown", "options"),
    Output("opposition-dropdown", "value"),
    Input("oppo-squad-dropdown", "value"),
    Input("competition-dropdown", "value")
)
def update_opposition_dropdown(squad_name, competition):
    teams = squad_data["opposition"].get(squad_name, {}).get(competition, {})
    options = [{"label": name, "value": name} for name in teams]
    return options, options[0]["value"] if options else None

@callback(
    Output("opposition-squad-content", "children"),
    Input("oppo-squad-dropdown", "value"),
    Input("competition-dropdown", "value"),
    Input("opposition-dropdown", "value")
)
def display_opposition_squad(squad, comp, team):
    players = squad_data["opposition"].get(squad, {}).get(comp, {}).get(team, [])
    return render_player_cards_by_position(players)

@callback(
    Output("squad-dropdown-content", "children"),
    Input("squad-dropdown", "value")
)
def display_selected_squad(squad_name):
    players = squad_data["chelsea_squads"].get(squad_name, [])
    return render_player_cards_by_position(players)
