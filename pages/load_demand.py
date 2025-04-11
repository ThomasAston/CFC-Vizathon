from dash import html, dcc, Input, Output, callback
from datetime import datetime, timedelta
import matplotlib.colors as mcolors
from dash import ctx
import plotly.express as px
from utils.data_loader import load_player_data, load_gps_data, compute_gradient_df, compute_acwr
from utils.plot_helpers import base_bar_figure, get_matchday_shapes_annotations, bubble_plot
from utils.components import collapsible_section, date_slider
from utils.constants import *

colors = [mcolors.to_hex(c) for c in ['tab:blue', 'tab:orange', 'tab:green']]
player_lookup = load_player_data("DATA/players.json")
gps_df = load_gps_data("DATA/CFC GPS Data.csv")

# Calculate average duration for training and match days
training_avg_duration = gps_df[gps_df["is_training_day"]]["day_duration"].mean()
match_avg_duration = gps_df[gps_df["is_match_day"]]["day_duration"].mean()

# Calculate average distance for training and match days
training_avg_distance = gps_df[gps_df["is_training_day"]]["distance"].mean()
match_avg_distance = gps_df[gps_df["is_match_day"]]["distance"].mean()

# Calculate average distance per minute on matchdays and training days
match_avg_distance_per_min = gps_df[gps_df["is_match_day"]]["distance_per_min"].mean()
training_avg_distance_per_min = gps_df[gps_df["is_training_day"]]["distance_per_min"].mean()

match_avg_peak_speed = gps_df[gps_df["is_match_day"]]["peak_speed"].mean()
training_avg_peak_speed = gps_df[gps_df["is_training_day"]]["peak_speed"].mean()

valid_distances = gps_df[gps_df["distance"] > 0]
max_date = valid_distances["date"].max()
min_date = max_date - timedelta(weeks=52)

# Create shapes and annotations for ALL matchdays
shapes, annotations = get_matchday_shapes_annotations(gps_df)

gradient_df = compute_gradient_df(gps_df, metrics)

def render_load_demand(player_id):
    return date_slider(
        label_id="reporting-period-label",
        slider_id="reporting-slider",
        min_date=min_date,
        max_date=max_date,
        initial_weeks=6,
        output_id="load-demand-output"
    )


@callback(
    Output("load-demand-output", "children"),
    Input("reporting-slider", "value")
)
def update_load_demand(selected_range):
    start_date = datetime.fromtimestamp(selected_range[0])
    end_date = datetime.fromtimestamp(selected_range[1])
    x_range = [start_date, end_date]

    zone_totals = {zone: gps_df[zone].sum() for zone in zone_cols}
    total_time = sum(zone_totals.values())

    zone_percentages = {
        zone.replace("_sec", "").replace("hr_zone_", "Zone "): (val / total_time * 100 if total_time else 0)
        for zone, val in zone_totals.items()
    }

    # Matchdays and training days (within selected range)
    recent = gps_df[gps_df["date"].between(start_date, end_date) & gps_df["day_duration"] > 0]
    
    # Filter gradient data for the selected date range
    range_gradient_df = gradient_df[
        (gradient_df["date"] >= start_date) & (gradient_df["date"] <= end_date)
    ]

    total_distance = int(recent["distance"].sum())
    matchdays_in_range = recent[(recent["md_plus_code"] == 0)]
    trainingdays_in_range = recent[(recent["md_plus_code"] != 0) & (recent["day_duration"] > 0)]

    return html.Div([
        html.Div([
            html.Div([
                html.H5("Report Days", style={"marginBottom": "4px", "fontSize": "10px", "color": "#555"}),
                html.H3(str((end_date - start_date).days + 1), style={"margin": "5px"})
            ], style={"flex": "1"}),

            html.Div([
                html.H5("Match Days", style={"marginBottom": "4px", "fontSize": "10px", "color": "#555"}),
                html.H3(str(len(matchdays_in_range)), style={"margin": "5px"})
            ], style={"flex": "1"}),

            html.Div([
                html.H5("Training Days", style={"marginBottom": "4px", "fontSize": "10px", "color": "#555"}),
                html.H3(str(len(trainingdays_in_range)), style={"margin": "5px"})
            ], style={"flex": "1"}),

            html.Div([
                html.H5("Total Distance", style={"marginBottom": "4px", "fontSize": "10px", "color": "#555"}),
                html.H3(f"{total_distance:,} m", style={"margin": "5px"})
            ], style={"flex": "1"}),
        ], style={
            "display": "flex",
            "whiteSpace": "nowrap",
            "margin": "10px auto 20px auto",
            "maxWidth": "90%",
            "marginTop": "50px",
            "flexWrap": "wrap"
        }),

        bubble_plot(recent),

        collapsible_section("Duration", dcc.Graph(
            figure=base_bar_figure(
                range_gradient_df,
                "day_duration",
                x_range,
                match_avg_duration,
                training_avg_duration,
                hover_suffix=" min",
                shapes=shapes,
                annotations=annotations,
            ), config={"displayModeBar": False}
        ), "day_duration"),

        collapsible_section("Distance", dcc.Graph(
            figure=base_bar_figure(
                range_gradient_df,
                "distance",
                x_range,
                match_avg_distance,
                training_avg_distance,
                hover_suffix=" m",
                shapes=shapes,
                annotations=annotations,
            ), config={"displayModeBar": False}
        ), "distance"),

        collapsible_section("Distance/Min", dcc.Graph(
            figure=base_bar_figure(
                range_gradient_df,
                "distance_per_min",
                x_range,
                match_avg_distance_per_min,
                training_avg_distance_per_min,
                hover_suffix=" m/min",
                shapes=shapes,
                annotations=annotations,
            ), config={"displayModeBar": False}
        ), "distance_per_min"),

        collapsible_section("Top Speed", dcc.Graph(
            figure=base_bar_figure(
                range_gradient_df,
                "peak_speed",
                x_range,
                match_avg_peak_speed,
                training_avg_peak_speed,
                hover_suffix=" km/h",
                shapes=shapes,
                annotations=annotations,
            ), config={"displayModeBar": False}
        ), "top_speed"),

        collapsible_section("Distance at High-Speed",
        html.Div([
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
        
        collapsible_section("Accel/Decel Efforts",
        html.Div([
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

        collapsible_section(
            "Heart Rate Zone Duration",
            html.Div([
                # Horizontally aligned zone percentage summaries
                html.Div([
                    html.Div([
                        html.H5(zone, style={"margin": "0", "fontSize": "10px", "color": "#555"}),
                        html.P(f"{percentage:.1f}%", style={"margin": "0", "fontWeight": "bold"})
                    ], style={"textAlign": "center", "minWidth": "60px"})  # Optional: fix width for spacing
                    for zone, percentage in zone_percentages.items()
                ], style={
                    "display": "flex",
                    "flexDirection": "row",
                    "justifyContent": "space-between",
                    "marginBottom": "10px"
                }),

                # HR zone duration graph
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
                            "legend": {
                                "x": 0,
                                "y": 1,
                                "xanchor": "left",
                                "yanchor": "top",
                                "font": {"size": 12}
                            },
                            "shapes": shapes,
                            "annotations": annotations,
                            "dragmode": False
                        }
                    },
                    config={"displayModeBar": False, "scrollZoom": False, "staticPlot": False}
                )
            ]),
            "hr_zones"
        ),

        collapsible_section(
            "Acute:Chronic Workload Ratio",
            html.Div(
                [
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
                ] + [
                    dcc.Graph(
                        id="acwr-graph",
                        config={"displayModeBar": False, "scrollZoom": False, "staticPlot": False}
                    )
                ]
            ),
            "acwr"
        )
    ])

@callback(
    Output("high-speed-graph", "figure"),
    Input("speed-threshold-dropdown", "value"),
    Input("reporting-slider", "value")
)
def update_high_speed_plot(speed_column, selected_range):
    start_date = datetime.fromtimestamp(selected_range[0])
    end_date = datetime.fromtimestamp(selected_range[1])
    x_range = [start_date, end_date]
    range_gradient_df = gradient_df[
        (gradient_df["date"] >= start_date) & (gradient_df["date"] <= end_date)
    ]
    # Averages
    match_avg = gps_df[gps_df["is_match_day"]][speed_column].mean()
    training_avg = gps_df[gps_df["is_training_day"]][speed_column].mean()

    fig=base_bar_figure(
                range_gradient_df,
                speed_column,
                x_range,
                match_avg,
                training_avg,
                hover_suffix=" m",
                shapes=shapes,
                annotations=annotations,
            )

    return fig

@callback(
    Output("high-accel-graph", "figure"),
    Input("accel-threshold-dropdown", "value"),
    Input("reporting-slider", "value")
)

def update_high_accel_plot(accel_column, selected_range):
    start_date = datetime.fromtimestamp(selected_range[0])
    end_date = datetime.fromtimestamp(selected_range[1])
    x_range = [start_date, end_date]
    range_gradient_df = gradient_df[
        (gradient_df["date"] >= start_date) & (gradient_df["date"] <= end_date)
    ]
    # Averages
    match_avg = gps_df[gps_df["is_match_day"]][accel_column].mean()
    training_avg = gps_df[gps_df["is_training_day"]][accel_column].mean()

    fig=base_bar_figure(
                range_gradient_df,
                accel_column,
                x_range,
                match_avg,
                training_avg,
                hover_suffix=" efforts",
                shapes=shapes,
                annotations=annotations,
            )

    return fig

@callback(
    Output("acwr-graph", "figure"),
    Input("acwr-metric-dropdown", "value"),
    Input("reporting-slider", "value")
)
def update_acwr_plot(metric, selected_range):
    start_date = datetime.fromtimestamp(selected_range[0])
    end_date = datetime.fromtimestamp(selected_range[1])
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
        "dragmode": False
        }
    }

from dash import ctx, Output, Input, State, callback

section_ids = [
    "day_duration", "distance", "distance_per_min", "top_speed", "high_speed",
    "accel_decel", "hr_zones", "acwr"
]

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


@callback(
    Output("reporting-period-label", "children"),
    Input("reporting-slider", "value")
)
def update_reporting_load(value):
    start = datetime.fromtimestamp(value[0]).strftime("%d/%m/%Y")
    end = datetime.fromtimestamp(value[1]).strftime("%d/%m/%Y")
    return f"Select Report Period: {start} – {end}"