from dash import html, dcc
from DATA.players import (
    senior_squad, u21s_squad, fa_youth_squad, u18s_squad,
    on_loan_squad, staff_squad, opposition_teams
)

def render_squad_list(squad):
    return html.Div([
        html.Ul([
            html.Li(
                html.A([
                    html.Img(src="assets/img/team/team-1/team-tbd.png", style={
                        'height': '50px',
                        'width': '50px',
                        'border-radius': '50%',
                        'margin-right': '10px'
                    }),
                    html.Span(f"{player['name']} ({player['position']})")
                ], href=f"/player/{player['id']}", style={
                    'display': 'flex',
                    'align-items': 'center',
                    'padding': '10px',
                    'text-decoration': 'none',
                    'color': 'black',
                    'border-bottom': '1px solid #eee'
                })
            ) for player in squad
        ])
    ])

layout = html.Div([
    html.H1("Player Interface"),

    html.H2("My Squads"),
    dcc.Tabs(id='squad-tabs', value='Senior', children=[
        dcc.Tab(label='Senior', value='Senior'),
        dcc.Tab(label='U21s', value='U21s'),
        dcc.Tab(label='FA Youth Cup', value='FAYouth'),
        dcc.Tab(label='U18s', value='U18s'),
        dcc.Tab(label='On Loan', value='OnLoan'),
        dcc.Tab(label='Staff', value='Staff'),
    ]),
    html.Div(id='squad-content'),

    html.H2("Opposition Squads"),
    dcc.Dropdown(
        id='opposition-dropdown',
        options=[{'label': team, 'value': team} for team in opposition_teams.keys()],
        value=list(opposition_teams.keys())[0]
    ),
    html.Div(id='opposition-content')
])
