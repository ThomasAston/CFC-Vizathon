from dash import callback, dcc, html, Input, Output, State
from utils.components import collapsible_section
import plotly.graph_objects as go
from utils.constants import body_markers

def render_injury(player_id):
    return html.Div([
        collapsible_section(
            "Module Guide",
            html.Div([
                html.P("This module will summarise injury risk and current injury status."),
                html.Ul([
                    html.Li("Track injury history and recovery timelines"),
                    html.Li("Integrate physio notes or medical assessments (coming soon)"),
                ]),
                html.P("Use this section to support safe return-to-play and injury prevention decisions."),
            ]),
            section_id="injury_info"
        ),

        html.H3("Injury Status Overview", style={"textAlign": "center", "marginTop": "30px"}),

        html.Div([
            html.Div([
                html.Div("🩹 Last Injury", className="placeholder-label"),
                html.H4("Hamstring – 28 days ago", className="placeholder-value")
            ], className="injury-summary-box"),

            html.Div([
                html.Div("🛌 Recovery Time", className="placeholder-label"),
                html.H4("Fully recovered", className="placeholder-value")
            ], className="injury-summary-box"),

            html.Div([
                html.Div("⚠️ Risk Level", className="placeholder-label"),
                html.H4("Moderate", className="placeholder-value", style={"color": "orange"})
            ], className="injury-summary-box"),
        ], style={
            "display": "flex",
            "justifyContent": "space-around",
            "flexWrap": "wrap",
            "marginTop": "20px",
            "marginBottom": "30px"
        }),

        html.Div([
        html.H4("Player History", style={"textAlign": "center", "marginTop": "40px"}),

        html.Div(
                dcc.Graph(
                    id="injury-body-map",
                    figure={
                        "data": [
                            go.Scatter(
                                x=[0.5, 0.46, 0.533],
                                y=[0.93, 0.53, 0.61],
                                mode="markers",
                                marker=dict(
                                    size=15,
                                    color=[0.9, 0.4, 0.6],
                                    colorscale="Blues",
                                    cmin=0,
                                    cmax=1,
                                    colorbar=dict(
                                        title="Severity",
                                        thickness=12,
                                        len=0.55,
                                        lenmode="fraction",
                                        x=0.7,
                                        y=0.64,
                                        tickvals=[0, 0.5, 1],
                                        ticktext=["Low", "Moderate", "High"],
                                        outlinewidth=0
                                    ),
                                ),
                                hovertemplate=(
                                    "<b>%{customdata[0]}</b><br>" +
                                    "Severity: %{customdata[1]:.0%}<br>" +
                                    "Days Ago: %{customdata[2]}<br>" +
                                    "%{customdata[3]}<extra></extra>"
                                ),
                                customdata=[
                                    ["Head", 0.9, 62, "Concussion"],
                                    ["Right Knee", 0.4, 73, "Mild inflammation"],
                                    ["Left Hamstring", 0.6, 28, "Strain"]
                                ],
                                showlegend=False
                            )
                        ],
                        "layout": go.Layout(
                            autosize=True,
                            images=[dict(
                                source="/assets/body_map.png",
                                xref="x", yref="y",
                                x=0, y=1,
                                sizex=1, sizey=3,
                                xanchor="left", yanchor="top",
                                sizing="contain",
                                layer="below"
                            )],
                            xaxis=dict(visible=False, range=[0, 1], fixedrange=True),
                            yaxis=dict(visible=False, range=[0, 1], scaleanchor="x", fixedrange=True),
                            margin=dict(l=0, r=0, t=20, b=20),
                            dragmode=False,
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)"
                        )
                    },
                        config={"displayModeBar": False},
                style={
                    "height": "500px",
                    "width": "100%",              # Let it fill the container
                    "maxWidth": "500px",          # Constrain width
                    "margin": "0 auto"
                }
            ),
            style={
                "display": "flex",
                "justifyContent": "center",
                "width": "100%",
                "overflow": "hidden",
                "marginTop": "-40px",
                "marginLeft": "-50px",
            }
        )
    ]),

    ])


@callback(
    Output("injury_info-collapse", "is_open"),
    Input("injury_info-toggle", "n_clicks"),
    State("injury_info-collapse", "is_open"),
    prevent_initial_call=True
)
def toggle_injury_info(n, is_open):
    if n:
        return not is_open
    return is_open