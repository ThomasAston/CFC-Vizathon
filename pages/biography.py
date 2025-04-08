# from dash import html
# from DATA.players import chelsea_squad

# def layout(player_id):
#     player = next((p for p in chelsea_squad if p["id"] == player_id), None)
#     if not player:
#         return html.Div([html.H2("Player not found")])
    
#     return html.Div([
#         html.H1(player["name"]),
#         html.Img(src="/assets/img/team/team-1/team-tbd.png", style={
#             'height': '200px',
#             'border-radius': '50%',
#             'margin': '20px 0'
#         }),
#         html.P(f"Position: {player['position']}"),
#         html.P(f"Squad Number: {player['number']}"),
#         html.A("← Back to squad", href="/")
#     ])
