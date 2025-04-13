from dash import html, dcc, Input, Output, State, callback, ctx, no_update
from datetime import datetime, timedelta
import matplotlib.colors as mcolors
import plotly.express as px
from utils.data_loader import load_player_data, load_gps_data, compute_gradient_df, compute_acwr
from utils.plot_helpers import base_bar_figure, get_matchday_shapes_annotations, bubble_plot_figure
from utils.components import collapsible_section, date_slider
from utils.constants import *

# Load data & settings
colors = [mcolors.to_hex(c) for c in ['tab:blue', 'tab:orange', 'tab:green']]
player_lookup = load_player_data("DATA/players.json")
gps_df = load_gps_data("DATA/CFC GPS Data.csv")
gradient_df = compute_gradient_df(gps_df, metrics)

training_avg_duration = gps_df[gps_df["is_training_day"]]["day_duration"].mean()
match_avg_duration = gps_df[gps_df["is_match_day"]]["day_duration"].mean()
training_avg_distance = gps_df[gps_df["is_training_day"]]["distance"].mean()
match_avg_distance = gps_df[gps_df["is_match_day"]]["distance"].mean()
training_avg_distance_per_min = gps_df[gps_df["is_training_day"]]["distance_per_min"].mean()
match_avg_distance_per_min = gps_df[gps_df["is_match_day"]]["distance_per_min"].mean()
training_avg_peak_speed = gps_df[gps_df["is_training_day"]]["peak_speed"].mean()
match_avg_peak_speed = gps_df[gps_df["is_match_day"]]["peak_speed"].mean()

valid_distances = gps_df[gps_df["distance"] > 0]
max_date = valid_distances["date"].max()
min_date = max_date - timedelta(weeks=52)

shapes, annotations = get_matchday_shapes_annotations(gps_df)

section_ids = [
    "load_demand_info", 
    "day_duration", "distance", "distance_per_min", "top_speed",
    "high_speed", "accel_decel", "hr_zones", "acwr"
]

# Helper: convert slider timestamps to datetime range
def get_date_range(selected_range):
    start_date = datetime.fromtimestamp(selected_range[0])
    end_date = datetime.fromtimestamp(selected_range[1])
    return start_date, end_date

def render_load_demand(player_id):
    return html.Div([
        collapsible_section(
            "Module Guide",
            html.Div([
                html.P("This module summarises the external physical load experienced by players during training and matches. Metrics include:"),
                html.Ul([
                    html.Li("Session duration (how long each session lasted)"),
                    html.Li("Distance covered and intensity (distance per min), which can be thought of as the average speed of the session"),
                    html.Li("Top speed and high-speed efforts, which are the maximum speed and distance covered at high speeds in a session"),
                    html.Li("Acceleration/deceleration efforts, which are the number of times a player accelerates or decelerates above a certain threshold"),
                    html.Li("Heart rate zones, which indicate the amount of time spent in different heart rate zones during a session"),
                    html.Li("Acute:Chronic Workload Ratio (ACWR), which is a measure of training load that compares the acute load (recent training) to the chronic load (long-term training)."),
                ]),
                html.P("Use the reporting period slider to explore changes over time."),
            ]),
            section_id="load_demand_info"
        ),
        date_slider(
            label_id="reporting-period-label",
            slider_id="reporting-slider",
            min_date=min_date,
            max_date=max_date,
            initial_weeks=6,
            output_id="load-demand-output"
        ),
        html.Div(id="summary-box", style={"width": "100%", "marginTop": "50px", "textAlign": "center"}),
        html.Div([
            html.H4("Load Profile Overview", style={"textAlign": "center", "marginBottom": "10px"}),
            html.P(
                "Training and match day load profiles. Bubble size represents total high-speed running distance for a session.",
                style={"textAlign": "left"}
            ),
            dcc.Graph(id="bubble-plot", config={"displayModeBar": False})
        ], style={"maxWidth": "90%", "margin": "0 auto", "marginBottom": "30px", "marginTop": "50px"}),
        collapsible_section("Duration", html.Div(id="day_duration-content"), "day_duration"),
        collapsible_section("Distance", html.Div(id="distance-content"), "distance"),
        collapsible_section("Average Speed", html.Div(id="distance_per_min-content"), "distance_per_min"),
        collapsible_section("Top Speed", html.Div(id="top_speed-content"), "top_speed"),
        # For dropdown-based sections, include the dropdown and graph in the static layout so that they are not re-created when toggling.
        collapsible_section("Distance at High-Speed", html.Div([
            dcc.Dropdown(
                id="speed-threshold-dropdown",
                options=[
                    {"label": ">21 km/h", "value": "distance_over_21"},
                    {"label": ">24 km/h", "value": "distance_over_24"},
                    {"label": ">27 km/h", "value": "distance_over_27"},
                ],
                value="distance_over_21",
                clearable=False,
                searchable=False,
                style={"width": "200px", "marginBottom": "10px", "margin": "0 auto"}
            ),
            dcc.Graph(id="high-speed-graph", config={"displayModeBar": False})
        ]), "high_speed"),
        collapsible_section("Accel/Decel Efforts", html.Div([
            dcc.Dropdown(
                id="accel-threshold-dropdown",
                options=[
                    {"label": ">2.5 m/s²", "value": "accel_decel_over_2_5"},
                    {"label": ">3.5 m/s²", "value": "accel_decel_over_3_5"},
                    {"label": ">4.5 m/s²", "value": "accel_decel_over_4_5"},
                ],
                value="accel_decel_over_2_5",
                clearable=False,
                searchable=False,
                style={"width": "200px", "marginBottom": "10px", "margin": "0 auto"}
            ),
            dcc.Graph(id="high-accel-graph", config={"displayModeBar": False})
        ]), "accel_decel"),
        collapsible_section("Heart Rate Zone Duration", html.Div(id="hr_zones-content"), "hr_zones"),
        collapsible_section("Acute:Chronic Workload Ratio", html.Div([
            dcc.Dropdown(
                id="acwr-metric-dropdown",
                options=[
                    {"label": "Total Distance", "value": "distance"},
                    {"label": "Distance/Min", "value": "distance_per_min"},
                    {"label": "Accels/Decels >3.5 m/s²", "value": "accel_decel_over_3_5"},
                    {"label": "Distance >21 km/h", "value": "distance_over_21"},
                ],
                value="distance",
                clearable=False,
                searchable=False,
                style={"width": "300px", "marginBottom": "10px", "margin": "0 auto"}
            ),
            dcc.Graph(id="acwr-graph", config={"displayModeBar": False})
        ]), "acwr")
    ])

# Update reporting period label
@callback(
    Output("reporting-period-label", "children"),
    Input("reporting-slider", "value")
)
def update_reporting_load(value):
    start, end = get_date_range(value)
    return f"Select Report Period: {start.strftime('%d/%m/%Y')} – {end.strftime('%d/%m/%Y')}"

# Toggle collapsible sections (same as before)
@callback(
    [Output(f"{section_id}-collapse", "is_open") for section_id in section_ids],
    [Input(f"{section_id}-toggle", "n_clicks") for section_id in section_ids],
    [State(f"{section_id}-collapse", "is_open") for section_id in section_ids],
    prevent_initial_call=True
)
def toggle_collapsible(*args):
    n = len(section_ids)
    clicks = args[:n]
    states = args[n:]
    triggered = ctx.triggered_id
    return [
        not state if triggered == f"{section_id}-toggle" else state
        for section_id, state in zip(section_ids, states)
    ]

# Generic callback for bar chart metrics (sections without built-in dropdowns)
def render_bar_chart(metric, selected_range, match_avg, training_avg, hover_suffix):
    start_date, end_date = get_date_range(selected_range)
    x_range = [start_date, end_date]
    range_df = gradient_df[(gradient_df["date"] >= start_date) & (gradient_df["date"] <= end_date)]
    return dcc.Graph(
        figure=base_bar_figure(
            range_df, metric, x_range, match_avg, training_avg,
            hover_suffix=hover_suffix, shapes=shapes, annotations=annotations
        ),
        config={"displayModeBar": False}
    )

@callback(
    Output("day_duration-content", "children"),
    Input("day_duration-collapse", "is_open"),
    Input("reporting-slider", "value")
)
def render_day_duration(is_open, selected_range):
    if not is_open:
        return no_update
    return render_bar_chart("day_duration", selected_range, match_avg_duration, training_avg_duration, " min")

@callback(
    Output("distance-content", "children"),
    Input("distance-collapse", "is_open"),
    Input("reporting-slider", "value")
)
def render_distance(is_open, selected_range):
    if not is_open:
        return no_update
    return render_bar_chart("distance", selected_range, match_avg_distance, training_avg_distance, " m")

@callback(
    Output("distance_per_min-content", "children"),
    Input("distance_per_min-collapse", "is_open"),
    Input("reporting-slider", "value")
)
def render_distance_per_min(is_open, selected_range):
    if not is_open:
        return no_update
    return render_bar_chart("distance_per_min", selected_range, match_avg_distance_per_min, training_avg_distance_per_min, " m/min")

@callback(
    Output("top_speed-content", "children"),
    Input("top_speed-collapse", "is_open"),
    Input("reporting-slider", "value")
)
def render_top_speed(is_open, selected_range):
    if not is_open:
        return no_update
    return render_bar_chart("peak_speed", selected_range, match_avg_peak_speed, training_avg_peak_speed, " km/h")

@callback(
    Output("hr_zones-content", "children"),
    Input("hr_zones-collapse", "is_open"),
    Input("reporting-slider", "value")
)
def render_hr_zones(is_open, selected_range):
    if not is_open:
        return no_update

    start_date, end_date = get_date_range(selected_range)
    x_range = [start_date, end_date]
    recent = gps_df[(gps_df["date"] >= start_date) & (gps_df["date"] <= end_date)]
    zone_totals = {zone: recent[zone].sum() for zone in zone_cols}
    total_time = sum(zone_totals.values())
    zone_percentages = {
        zone.replace("_sec", "").replace("hr_zone_", "Zone "): (val / total_time * 100 if total_time else 0)
        for zone, val in zone_totals.items()
    }

    return html.Div([
        html.Div([
            html.Div([
                html.H5(zone, style={"margin": "0", "fontSize": "10px", "color": "#555"}),
                html.P(f"{perc:.1f}%", style={"margin": "0", "fontWeight": "bold"})
            ], style={"textAlign": "center", "minWidth": "60px"})
            for zone, perc in zone_percentages.items()
        ], style={"display": "flex", "flexDirection": "row", "justifyContent": "space-around", "marginBottom": "10px"}),
        dcc.Graph(
            figure={
                "data": [
                    {
                        "x": gps_df["date"],
                        "y": gps_df[f"hr_zone_{i}_sec"],
                        "stackgroup": "one",
                        "name": f"Zone {i}",
                        "line": {"width": 0.5, "color": zone_colors[i - 1]},
                        "fillcolor": zone_colors[i - 1]
                    } for i in range(1, 6)
                ],
                "layout": {
                    "xaxis": {"title": "Date", "range": x_range, "fixedrange": True},
                    "yaxis": {"title": "Time in Zone (sec)", "fixedrange": True},
                    "margin": {"l": 40, "r": 10, "t": 30, "b": 40},
                    "height": 300,
                    "plot_bgcolor": "#fff",
                    "paper_bgcolor": "#fff",
                    "legend": {"x": 0, "y": 1, "xanchor": "left", "yanchor": "top", "font": {"size": 12}},
                    "shapes": shapes,
                    "annotations": annotations,
                    "dragmode": False
                }
            },
            config={"displayModeBar": False}
        )
    ])

@callback(
    Output("bubble-plot", "figure"),
    Input("reporting-slider", "value")
)
def update_bubble_plot(selected_range):
    start_date, end_date = get_date_range(selected_range)
    filtered_df = gps_df[
        (gps_df["date"] >= start_date) & 
        (gps_df["date"] <= end_date) & 
        (gps_df["day_duration"] > 0)
    ]
    return bubble_plot_figure(filtered_df)

@callback(
    Output("summary-box", "children"),
    Input("reporting-slider", "value")
)
def update_summary_box(selected_range):
    start_date, end_date = get_date_range(selected_range)
    recent = gps_df[
        (gps_df["date"] >= start_date) &
        (gps_df["date"] <= end_date) &
        (gps_df["day_duration"] > 0)
    ]
    total_distance = int(recent["distance"].sum())
    matchdays = len(recent[recent["md_plus_code"] == 0])
    trainingdays = len(recent[recent["md_plus_code"] != 0])
    return html.Div([
        html.Div([
            html.Div([
                html.H5("Report Days", style={"marginBottom": "4px", "fontSize": "10px", "color": "#555"}),
                html.H3(str((end_date - start_date).days + 1), style={"margin": "5px"})
            ], style={"flex": "1"}),
            html.Div([
                html.H5("Match Days", style={"marginBottom": "4px", "fontSize": "10px", "color": "#555"}),
                html.H3(str(matchdays), style={"margin": "5px"})
            ], style={"flex": "1"}),
            html.Div([
                html.H5("Training Days", style={"marginBottom": "4px", "fontSize": "10px", "color": "#555"}),
                html.H3(str(trainingdays), style={"margin": "5px"})
            ], style={"flex": "1"}),
            html.Div([
                html.H5("Total Distance", style={"marginBottom": "4px", "fontSize": "10px", "color": "#555"}),
                html.H3(f"{total_distance:,} m", style={"margin": "5px"})
            ], style={"flex": "1"})
        ], style={
            "display": "flex",
            "whiteSpace": "nowrap",
            "flexWrap": "wrap",
            "justifyContent": "space-between",
            "margin": "0 auto"
        })
    ], style={"width": "100%"})

# Callback to update the high-speed graph based on dropdown and slider inputs
@callback(
    Output("high-speed-graph", "figure"),
    Input("speed-threshold-dropdown", "value"),
    Input("reporting-slider", "value")
)
def update_high_speed_plot(speed_column, selected_range):
    start_date, end_date = get_date_range(selected_range)
    x_range = [start_date, end_date]
    range_df = gradient_df[(gradient_df["date"] >= start_date) & (gradient_df["date"] <= end_date)]
    match_avg = gps_df[gps_df["is_match_day"]][speed_column].mean()
    training_avg = gps_df[gps_df["is_training_day"]][speed_column].mean()
    return base_bar_figure(
        range_df, speed_column, x_range, match_avg, training_avg,
        hover_suffix=" m", shapes=shapes, annotations=annotations
    )

# Callback to update the acceleration graph based on dropdown and slider inputs
@callback(
    Output("high-accel-graph", "figure"),
    Input("accel-threshold-dropdown", "value"),
    Input("reporting-slider", "value")
)
def update_high_accel_plot(accel_column, selected_range):
    start_date, end_date = get_date_range(selected_range)
    x_range = [start_date, end_date]
    range_df = gradient_df[(gradient_df["date"] >= start_date) & (gradient_df["date"] <= end_date)]
    match_avg = gps_df[gps_df["is_match_day"]][accel_column].mean()
    training_avg = gps_df[gps_df["is_training_day"]][accel_column].mean()
    return base_bar_figure(
        range_df, accel_column, x_range, match_avg, training_avg,
        hover_suffix=" efforts", shapes=shapes, annotations=annotations
    )

# Callback to update the ACWR graph based on dropdown and slider inputs
@callback(
    Output("acwr-graph", "figure"),
    Input("acwr-metric-dropdown", "value"),
    Input("reporting-slider", "value")
)
def update_acwr_plot(metric, selected_range):
    if metric is None:
        return {}
    start_date, end_date = get_date_range(selected_range)
    x_range = [start_date, end_date]
    acwr_df = compute_acwr(gps_df, metric)
    return {
        "data": [
            {
                "x": acwr_df["date"],
                "y": acwr_df["acwr"],
                "type": "scatter",
                "mode": "lines+markers",
                "line": {"color": colors[0]},
                "marker": {"size": 6},
                "name": "ACWR"
            },
            {
                "x": acwr_df["date"].tolist() + acwr_df["date"].tolist()[::-1],
                "y": [0.8] * len(acwr_df) + [1.5] * len(acwr_df[::-1]),
                "type": "scatter",
                "fill": "toself",
                "fillcolor": "rgba(0, 255, 0, 0.1)",
                "line": {"color": "rgba(0,0,0,0)"},
                "hoverinfo": "skip",
                "showlegend": False
            }
        ],
        "layout": {
            "xaxis": {"title": "Date", "range": x_range, "fixedrange": True},
            "yaxis": {"title": "ACWR", "range": [0, None], "fixedrange": True},
            "margin": {"l": 40, "r": 10, "t": 30, "b": 40},
            "height": 300,
            "plot_bgcolor": "#fff",
            "paper_bgcolor": "#fff",
            "showlegend": False,
            "dragmode": False,
            "shapes": shapes,
            "annotations": annotations
        }
    }
