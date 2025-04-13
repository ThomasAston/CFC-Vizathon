from dash import callback, dcc, html, Input, Output, State
from utils.components import collapsible_section

def render_external_factors(player_id):
    return html.Div([
        collapsible_section(
            "Module Guide",
            html.Div([
                html.P("This module will summarise external factors that may influence a player's performance. These include both individual and team-context variables."),
                html.Ul([
                    html.Li("Environmental conditions (e.g., weather, travel fatigue)"),
                    html.Li("Team dynamics and cohesion"),
                    html.Li("Player motivation and mindset"),
                    html.Li("Academic or personal stressors (if relevant)"),
                ]),
                html.P("These indicators can support context-aware interpretation of physical and recovery data."),
            ]),
            section_id="external_factors_info"
        ),

        html.H3("External Factors Overview", style={"textAlign": "center", "marginTop": "30px"}),

        html.Div([
            # 🌦️ Environment block
            html.Div([
                html.Div("🌦️ Environment", className="placeholder-label"),
                html.Div([
                    html.Div([
                        html.Span("Weather: ", style={"fontWeight": "bold"}),
                        html.Span("Hot & Humid")
                    ]),
                    html.Div([
                        html.Span("Travel: ", style={"fontWeight": "bold"}),
                        html.Span("Long-haul (4hr drive)")
                    ]),
                    html.Div([
                        html.Span("Surface: ", style={"fontWeight": "bold"}),
                        html.Span("Dry artificial turf")
                    ]),
                    html.Div([
                        html.Span("Kickoff: ", style={"fontWeight": "bold"}),
                        html.Span("Late evening")
                    ])
                ], style={"fontSize": "14px", "lineHeight": "1.6", "color": "#333"})
            ], className="external-box", style={"flex": "1 1 280px", "minWidth": "220px", "margin": "10px"}),

            # 🤝 Cohesion
            html.Div([
                html.Div("🤝 Team Cohesion", className="placeholder-label"),
                html.H4("High", className="placeholder-value", style={"color": "#2a9d8f"})
            ], className="external-box", style={"flex": "1 1 180px", "margin": "10px"}),

            # 🎯 Motivation
            html.Div([
                html.Div("🎯 Motivation", className="placeholder-label"),
                html.H4("Moderate", className="placeholder-value", style={"color": "#e9c46a"})
            ], className="external-box", style={"flex": "1 1 180px", "margin": "10px"}),

            # 🧠 Mental Load
            html.Div([
                html.Div("🧠 Mental Load", className="placeholder-label"),
                html.H4("Elevated", className="placeholder-value", style={"color": "#e76f51"})
            ], className="external-box", style={"flex": "1 1 180px", "margin": "10px"}),
        ], style={
            "display": "flex",
            "flexWrap": "wrap",
            "justifyContent": "center",
            "gap": "20px",
            "marginTop": "20px",
            "marginBottom": "30px"
        }),

    ])

@callback(
    Output("external_factors_info-collapse", "is_open"),
    Input("external_factors_info-toggle", "n_clicks"),
    State("external_factors_info-collapse", "is_open"),
    prevent_initial_call=True
)
def toggle_external_factors_info(n, is_open):
    if n:
        return not is_open
    return is_open