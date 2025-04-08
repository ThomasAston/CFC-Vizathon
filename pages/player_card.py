from dash import html, dcc

def render_player_cards_by_position(players):
    layout = []
    positions = ["Goalkeeper", "Defender", "Midfielder", "Attacker"]
    
    for pos in positions:
        pos_players = [p for p in players if p["position"] == pos]
        if pos_players:
            layout.append(html.H4(pos, style={"marginTop": "40px"}))
            layout.extend([
                dcc.Link(
                    href=f"/player/{p['id']}",
                    children=html.Div([
                        html.Img(src=p['photo'], style={
                            'height': '60px',
                            'width': '60px',
                            'border-radius': '50%',
                            'margin-right': '10px'
                        }),
                        html.Span(p["name"], style={'font-weight': 'bold'})
                    ], style={
                        "display": "flex",
                        "alignItems": "center",
                        "gap": "10px",
                        "marginBottom": "6px"
                    }),
                    style={"textDecoration": "none", "color": "inherit"}
                )
                for p in pos_players
            ])
    
    return html.Div(layout)
