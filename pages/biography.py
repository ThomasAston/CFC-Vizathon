from dash import html, dcc, Input, Output, State, callback
import json
import plotly.graph_objects as go
from pages import load_demand, physical_development, recovery, injury_history, external_factors
import matplotlib.colors as mcolors
import pandas as pd

# Load priority areas
priority_df = pd.read_csv("DATA/CFC Individual Priority Areas.csv")

# Set plot colors
colors = [mcolors.to_hex(c) for c in ['tab:blue', 'tab:orange', 'tab:green']]

# Load data
with open("DATA/players.json") as f:
    data = json.load(f)

# Flatten players by ID for quick lookup
player_lookup = {}
for group in ["chelsea_squads", "opposition"]:
    if group == "chelsea_squads":
        for squad in data[group]:
            for p in data[group][squad]:
                player_lookup[str(p["id"])] = p
    else:
        for squad in data[group]:
            for comp in data[group][squad]:
                for team in data[group][squad][comp]:
                    for p in data[group][squad][comp][team]:
                        player_lookup[str(p["id"])] = p

def render(player_id):
    player = player_lookup.get(str(player_id))
    if not player:
        return html.H2("Player not found")

    position = player.get("position")
    comparison_options = [
        {"label": f"{p['name']} ({p['position']})", "value": str(p["id"])}
        for p in player_lookup.values()
        if p.get("position") == position and str(p["id"]) != str(player_id)
    ]

    return html.Div([
        dcc.Link("\u2190 Back to Squads", href="/", style={"margin-bottom": "10px", "display": "inline-block"}),

        html.Div([
            # Left: Player profile info
            html.Div([
                html.Img(src=player["photo"], style={
                    "height": "100px",
                    "width": "100px",
                    "border-radius": "50%",
                    "object-fit": "cover",
                    "margin-right": "15px"
                }),
                html.Div([
                    html.H2(player["name"], style={"margin-bottom": "5px", "fontFamily": "CFC Serif"}),
                    html.P(f"Position: {player.get('position', '-')}", style={"margin": "2px 0"}),
                    html.P(f"Age: {player.get('age', '-')}", style={"margin": "2px 0"}),
                    html.P(f"Height: {player.get('height', '-')}", style={"margin": "2px 0"}),
                    html.P(f"Weight: {player.get('weight', '-')}", style={"margin": "2px 0"}),
                    html.P(f"Nationality: {player.get('nationality', '-')}", style={"margin": "2px 0"}),
                ])
            ], style={
                "minWidth": "250px",
                "flex": "1 1 300px",
                "display": "flex",
                # "maxWidth": "300px",
                "alignItems": "center",
                "justifyContent": "center",
                # "textAlign": "center",       # Center text
            }),

            # Middle: Radar + dropdown
            html.Div([
                html.Div([
                    dcc.Graph(id="radar-compare", style={"height": "220px", "width": "350px"}, config={"displayModeBar": False}),
                    dcc.Dropdown(
                        id="comparison-dropdown",
                        options=comparison_options,
                        placeholder="Compare stats this season...",
                        style={
                            "width": "300px",
                            "marginTop": "0px",
                            "fontSize": "12px",
                            "height": "30px",
                            "lineHeight": "30px"
                        },
                    )
                ], style={
                    "display": "flex",
                    "flexDirection": "column",
                    "alignItems": "center"
                })
            ], style={
                "flex": "1 1 350px",
                # "marginLeft": "20px",
                "marginTop": "-20px",
                "justifyContent": "center",
                "display": "flex"
            }),

            # Right: Individual priority areas
            html.Div([
                html.Div([
                    html.H2("Priority Areas", style={"margin-bottom": "5px", "fontFamily": "CFC Serif"}),
                    html.Div([
                        html.P([
                            html.Span(f"{row['Category']} – {row['Area']}: ", style={"fontWeight": "bold"}),
                            f" {row['Target']}"
                        ], style={"margin": "10px 0"}) for _, row in priority_df.iterrows()
                    ])
                ])
            ], style={
                "flex": "1 1 300px",
                "marginLeft": "20px",
                "marginRight": "20px",
                "display": "flex",
                "flexDirection": "column",
                "alignItems": "center",     # center the whole section in its flex container
                "textAlign": "left",        # but left-align the text inside
            })
        ], style={
            "display": "flex",
            "flexWrap": "wrap",
            "alignItems": "flex-start",
            "gap": "20px",
            "justifyContent": "center",
            "marginBottom": "20px",
        }),

        dcc.Tabs(id="player-tabs", value="LoadDemand", mobile_breakpoint=0, children=[
            dcc.Tab(label="Load Demand", value="LoadDemand"),
            dcc.Tab(label="Injury History", value="Injury"),
            dcc.Tab(label="Physical Development", value="Physical"),
            dcc.Tab(label="Recovery", value="Recovery"),
            dcc.Tab(label="External Factors", value="External"),
        ]),

        html.Div(id="player-tab-content", style={"padding": "10px"}),

        dcc.Store(id="main-player-id", data=str(player_id))
    ])


@callback(
    Output("player-tab-content", "children"),
    Input("player-tabs", "value"),
    State("main-player-id", "data")
)
def render_tab(tab, player_id):
    if tab == "LoadDemand":
        return load_demand.render_load_demand(player_id)
    elif tab == "Injury":
        return injury_history.render_injury(player_id)
    elif tab == "Physical":
        return physical_development.render_physical_development(player_id)
    elif tab == "Recovery":
        return recovery.render_recovery(player_id)
    elif tab == "External":
        return external_factors.render_external_factors(player_id)

@callback(
    Output("radar-compare", "figure"),
    Input("comparison-dropdown", "value"),
    State("main-player-id", "data")
)
def update_radar(compare_id, base_id):
    base_player = player_lookup.get(str(base_id))
    compare_player = player_lookup.get(str(compare_id)) if compare_id else None

    def compute_per_90(p):
        radar = p.get("radar", {})
        mins = p.get("minutes", 1) or 1
        return {
            k: (v / mins * 90 if k not in ["Pass Accuracy", "Av. Rating"] else v)
            for k, v in radar.items()
        }

    def normalize(data, max_values):
        return [round(data[k] / max_values.get(k, 1), 2) for k in data]

    base_data = compute_per_90(base_player)
    comp_data = compute_per_90(compare_player) if compare_player else None

    # Get max values for position
    position = base_player.get("position")
    radar_keys = base_data.keys()
    max_vals = {k: 0 for k in radar_keys}
    for p in player_lookup.values():
        if p.get("position") != position:
            continue
        pdata = compute_per_90(p)
        for k in radar_keys:
            max_vals[k] = max(max_vals[k], pdata.get(k, 0))

    base_r = normalize(base_data, max_vals)
    theta = list(radar_keys)

    # 👇 Append the first value to close the shape
    base_r.append(base_r[0])
    theta.append(theta[0])

    traces = [
        go.Scatterpolar(
            r=base_r,
            theta=theta,
            fill="toself",
            name=base_player["name"],
            line=dict(color=colors[0])
        )
    ]

    if comp_data:
        comp_r = normalize(comp_data, max_vals)
        comp_r.append(comp_r[0])

        traces.append(go.Scatterpolar(
            r=comp_r,
            theta=theta,
            fill="toself",
            name=compare_player["name"],
            line=dict(color=colors[1])
        ))

    return go.Figure(
            data=traces,
            layout=go.Layout(
                polar=dict(
                    bgcolor='white',
                    radialaxis=dict(
                        visible=True,
                        showline=False,
                        showgrid=True,
                        gridcolor='#ccc',
                        gridwidth=0.5,
                        tickvals=[]
                    ),
                    angularaxis=dict(
                        tickfont=dict(size=10),
                        gridcolor='#ccc',
                        gridwidth=0.5
                    )
                ),
                showlegend=True,
                margin=dict(t=40, b=40, l=40, r=40)
            )
        )
