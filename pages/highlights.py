from dash import html, dcc
import json
from utils.data_loader import load_fixtures, load_gps_data, load_physical_data, load_recovery_data
from utils.components import create_fixture_cards
from utils.plot_helpers import bubble_plot, create_physical_heatmap, emboss_color, recovery_radar_chart
import dash_daq as daq

fixtures = load_fixtures("DATA/fixtures.json")
fixture_cards = create_fixture_cards(fixtures)

current_season = "2023/2024"  # Replace with the appropriate season
gps_df = load_gps_data("DATA/CFC GPS Data.csv")
gps_df = gps_df[(gps_df["season"] == current_season) & (gps_df["day_duration"] > 0)]

phys_df = load_physical_data("DATA/CFC Physical Capability Data_.csv")

rec_df = load_recovery_data("DATA/CFC Recovery status Data.csv")
radar_fig = recovery_radar_chart(rec_df)
score = rec_df["emboss_baseline_score"].iloc[-1]
score_color = emboss_color(score)

# Full highlights layout
layout = html.Div([
    html.Div(
        html.Img(src="/assets/logo.png", className="responsive-logo"),
        style={"textAlign": "center", "marginBottom": "0px"}
    ),

    html.H2([
        html.Span("\uea48", className="icon"),
        "Upcoming Fixtures"
    ], className="section-heading"),

    html.Div(fixture_cards),

    html.H2([html.Span("\uebce", className="icon"), "Load Demand"], className="section-heading", style={"marginTop": "50px"}),
    bubble_plot(gps_df),

    html.H2([html.Span("\uebec", className="icon"), "Injuries"], className="section-heading", style={"marginTop": "50px"}),
    html.Div([
        html.H3("Current Injuries", style={"textAlign": "center"}),
        html.Ul([
            html.Li("Player 1: Hamstring strain"),
            html.Li("Player 2: Ankle sprain"),
            html.Li("Player 3: Knee injury"),
        ], style={"listStyleType": "none", "padding": 0, "textAlign": "center"})
    ], style={"marginBottom": "50px"}),

    html.H2([html.Span("\uea9e", className="icon"), "Physical Development"], className="section-heading", style={"marginTop": "50px"}),
    create_physical_heatmap(phys_df, "isometric", "Isometric Expression"),

    html.H2([html.Span("\uead8", className="icon"), "Recovery"], className="section-heading", style={"marginTop": "50px"}),
    html.Div([
        html.H3("Squad Averages", style={"textAlign": "center"}),
            html.Div([
            html.H4("Overall Score", style={"marginBottom": "4px", "color": "#444"}),
            daq.Gauge(
            showCurrentValue=False,
            units="%",
            value=score * 100,
            max=100,
            min=-100,
            color={"gradient":True,"ranges":{"red":[-100,20],"yellow":[20,60],"green":[60,100]}},
        )
        ], style={"textAlign": "center", "marginBottom": "-100px"}),

        dcc.Graph(figure=radar_fig, config={"displayModeBar": False})
    ], style={"maxWidth": "600px", "margin": "0 auto"}),

], style={"padding": "12px"})
