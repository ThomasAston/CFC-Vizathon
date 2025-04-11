from utils.data_loader import load_recovery_data
from utils.plot_helpers import recovery_radar_chart, emboss_color
from utils.constants import colors
from dash import callback, dcc, html, Input, Output


rec_df = load_recovery_data("DATA/CFC Recovery status Data.csv")

def render_recovery(player_id):
    radar_fig = recovery_radar_chart(rec_df)
    score = rec_df["emboss_baseline_score"].iloc[-1]
    score_color = emboss_color(score)
    return html.Div([
        html.H3("Most Recent Scores", style={"textAlign": "center"}),
        html.Div([
            html.H4("Emboss Baseline", style={"marginBottom": "4px", "color": "#444"}),
            html.H2(
                f"{score:.2f}",
                style={
                    "color": score_color,
                    "fontWeight": "bold",
                    "margin": "0",
                    "fontSize": "32px"
                }
            )
        ], style={
            "textAlign": "center",
            "marginBottom": "20px"
        }),

        dcc.Graph(figure=radar_fig, config={"displayModeBar": False})
    ], style={"maxWidth": "600px", "margin": "0 auto"})


@callback(
    Output("recovery-radar-chart", "figure"),
    Input("reporting-slider-recovery", "value")
)
def update_recovery(selected_range):
    return recovery_radar_chart(rec_df)
