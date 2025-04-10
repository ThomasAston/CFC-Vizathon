from dash import html, dcc, Input, Output, callback
import json
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.colors as mcolors
from dash import ctx
import dash_bootstrap_components as dbc

colors = [mcolors.to_hex(c) for c in ['tab:blue', 'tab:orange', 'tab:green']]

# Load data
with open("DATA/players.json") as f:
    data = json.load(f)

# Flatten players by ID for lookup
player_lookup = {}
for group in ["chelsea_squads", "opposition"]:
    for squad in data[group]:
        squads = data[group][squad] if group == "chelsea_squads" else [
            p for comp in data[group][squad].values() for team in comp.values() for p in team
        ]
        for p in squads:
            player_lookup[str(p["id"])] = p

# Load GPS data
gps_df = pd.read_csv("DATA/CFC GPS Data.csv", encoding="latin-1")
gps_df["date"] = pd.to_datetime(gps_df["date"], format="%d/%m/%Y")

# Create columns for training days and match days
gps_df["is_training_day"] = (gps_df["day_duration"] > 0) & (gps_df["md_plus_code"] != 0)
gps_df["is_match_day"] = (gps_df["day_duration"] > 0) & (gps_df["md_plus_code"] == 0)

# Calculate average distance for training and match days
training_avg_distance = gps_df[gps_df["is_training_day"]]["distance"].mean()
match_avg_distance = gps_df[gps_df["is_match_day"]]["distance"].mean()

# Calculate distance per minute
gps_df["distance_per_min"] = gps_df["distance"] / gps_df["day_duration"]

# Calculate average distance per minute on matchdays and training days
match_avg_distance_per_min = gps_df[gps_df["is_match_day"]]["distance_per_min"].mean()
training_avg_distance_per_min = gps_df[gps_df["is_training_day"]]["distance_per_min"].mean()

match_avg_peak_speed = gps_df[gps_df["is_match_day"]]["peak_speed"].mean()
training_avg_peak_speed = gps_df[gps_df["is_training_day"]]["peak_speed"].mean()

# Calculate time spent in heart rate zones in seconds
def hms_to_seconds(hms):
    try:
        h, m, s = map(int, hms.split(":"))
        return h * 3600 + m * 60 + s
    except:
        return 0

for i in range(1, 6):
    col = f"hr_zone_{i}_hms"
    gps_df[f"hr_zone_{i}_sec"] = gps_df[col].fillna("00:00:00").apply(hms_to_seconds)

# ACWR calculation
def compute_acwr(df, metric):
    df = df.sort_values("date")
    acwr = []
    for i in range(len(df)):
        acute = df.iloc[max(0, i - 6):i + 1][metric].mean()
        chronic = df.iloc[max(0, i - 27):i + 1][metric].mean()
        acwr.append(acute / chronic if chronic else 0)
    df = df.copy()
    df["acwr"] = acwr
    return df

# gps_acwr = compute_acwr(gps_df)

valid_distances = gps_df[gps_df["distance"] > 0]
max_date = valid_distances["date"].max()
min_date = max_date - timedelta(weeks=52)

# Convert to timestamps
min_ts = int(min_date.timestamp())
max_ts = int(max_date.timestamp())
six_weeks_ago_ts = int((max_date - timedelta(weeks=6)).timestamp())

# Generate date marks every month
mark_dates = pd.date_range(start=min_date, end=max_date, freq="2MS")  # 2MS for every two months
marks = {
    int(d.timestamp()): d.strftime("%b %Y")
    for d in mark_dates
}

zone_colors = ["rgba(173, 216, 230, 0.6)",  # LightBlue (Zone 1)
                "rgba(135, 206, 250, 0.6)",  # SkyBlue
                "rgba(100, 149, 237, 0.6)",  # CornflowerBlue
                "rgba(65, 105, 225, 0.6)",   # RoyalBlue
                "rgba(0, 0, 139, 0.6)"      # DarkBlue (Zone 5)
                ]


def collapsible_section(title, content, section_id):
    return html.Div([
        dbc.Button(
            title,
            id=f"{section_id}-toggle",
            className="mb-2",
            color="white",
            style={"width": f"{min(len(title), 100)}%", "textAlign": "left"}
        ),
        dbc.Collapse(
            content,
            id=f"{section_id}-collapse",
            is_open=False
        )
    ])


def render_load_demand(player_id):
    return html.Div([
        html.Div([
            html.Label(id="reporting-period-label", style={
                "fontWeight": "bold",
                "fontSize": "24px",  # Increased font size
                "marginBottom": "20px",
                "display": "block"
            }),
            dcc.RangeSlider(
                id="reporting-slider",
                min=int(min_date.timestamp()),
                max=int(max_date.timestamp()),
                step=7 * 24 * 60 * 60,  # 1 week in seconds
                value=[
                    int((max_date - timedelta(weeks=6)).timestamp()),
                    int(max_date.timestamp())
                ],
                marks={
                    int(d.timestamp()): d.strftime('%b %Y')
                    for d in pd.date_range(min_date, max_date, freq='2MS')
                },
            )
        ], style={"marginBottom": "30px", "maxWidth": "600px"}),

        html.Div(id="load-demand-output")
    ])


@callback(
    Output("reporting-period-label", "children"),
    Input("reporting-slider", "value")
)
def update_reporting_label(value):
    start = datetime.fromtimestamp(value[0]).strftime("%d/%m/%Y")
    end = datetime.fromtimestamp(value[1]).strftime("%d/%m/%Y")
    return f"Select Report Period: {start} – {end}"

@callback(
    Output("load-demand-output", "children"),
    Input("reporting-slider", "value")
)
def update_load_demand(selected_range):
    start_date = datetime.fromtimestamp(selected_range[0])
    end_date = datetime.fromtimestamp(selected_range[1])
    x_range = [start_date, end_date]
    # print("Selected range:", start_date.date(), "to", end_date.date())

    filtered_df = gps_df[(gps_df["date"] >= start_date) & (gps_df["date"] <= end_date)]

    # Compute total time in HR zones
    zone_cols = [
        "hr_zone_1_sec", "hr_zone_2_sec", "hr_zone_3_sec", "hr_zone_4_sec", "hr_zone_5_sec"
    ]
    zone_totals = {zone: filtered_df[zone].sum() for zone in zone_cols}
    total_time = sum(zone_totals.values())

    zone_percentages = {
        zone.replace("_sec", "").replace("hr_zone_", "Zone "): (val / total_time * 100 if total_time else 0)
        for zone, val in zone_totals.items()
    }

    recent = gps_df[gps_df["date"].between(start_date, end_date)]
    total_distance = int(recent["distance"].sum())
    matchdays = recent[(recent["md_plus_code"] == 0) & (recent["day_duration"] > 0)]
    trainingdays = recent[(recent["md_plus_code"] != 0) & (recent["day_duration"] > 0)]

    # Matchday lines + labels
    shapes = [{
        "type": "line",
        "x0": row["date"],
        "x1": row["date"],
        "y0": 0,
        "y1": 1,
        "xref": "x",
        "yref": "paper",
        "line": {"color": "gray", "width": 1}
    } for _, row in matchdays.iterrows()]
    annotations = [{
        "x": row["date"],
        "y": 1.1,
        "xref": "x",
        "yref": "paper",
        "text": row["opposition_code"],
        "showarrow": False,
        "font": {"color": "gray", "size": 10}
    } for _, row in matchdays.iterrows()]

    return html.Div([
        html.Div([
            html.Div([
                html.H5("Report Days", style={"marginBottom": "4px", "fontSize": "14px", "color": "#555"}),
                html.H3(str((end_date - start_date).days + 1), style={"margin": "0"})
            ], style={"flex": "1"}),

            html.Div([
                html.H5("Match Days", style={"marginBottom": "4px", "fontSize": "14px", "color": "#555"}),
                html.H3(str(len(matchdays)), style={"margin": "0"})
            ], style={"flex": "1"}),

            html.Div([
                html.H5("Training Days", style={"marginBottom": "4px", "fontSize": "14px", "color": "#555"}),
                html.H3(str(len(trainingdays)), style={"margin": "0"})
            ], style={"flex": "1"}),

            html.Div([
                html.H5("Total Distance", style={"marginBottom": "4px", "fontSize": "14px", "color": "#555"}),
                html.H3(f"{total_distance:,} m", style={"margin": "0"})
            ], style={"flex": "1"}),

        ], style={
            "display": "flex",
            "gap": "40px",
            "marginBottom": "20px",
            "flexWrap": "wrap"  # Added to allow wrapping on narrow screens
        }),

        # html.H4("Distance", style={"marginBottom": "10px", "fontFamily": "CFC Serif"}),
        collapsible_section("Distance", dcc.Graph(
            figure={
                "data": [
                    {
                        "x": gps_df["date"],
                        "y": gps_df["distance"],
                        "name": "(m)",
                        "type": "scatter",
                        "mode": "lines+markers",
                        "line": {"color": colors[0]},
                        "marker": {"size": 6},
                        "connectgaps": True,
                        "showlegend": False
                    },
                    {
                        "x": [x_range[0], x_range[1]],
                        "y": [match_avg_distance] * 2,
                        "type": "scatter",
                        "mode": "lines",
                        "line": {"color": colors[1], "dash": "dash", "width": 1},
                        "name": "Match Avg"
                    },
                    {
                        "x": [x_range[0], x_range[1]],
                        "y": [training_avg_distance] * 2,
                        "type": "scatter",
                        "mode": "lines",
                        "line": {"color": colors[2], "dash": "dash", "width": 1},
                        "name": "Training Avg"
                    }
                ],
                "layout": {
                    "xaxis": {"title": "Date", "range": x_range},
                    "yaxis": {"title": "Distance (m)", "fixedrange": True},
                    "margin": {"l": 40, "r": 10, "t": 30, "b": 40},
                    "height": 300,
                    "plot_bgcolor": "#fff",
                    "paper_bgcolor": "#fff",
                    "showlegend": True,
                    "legend": {
                        "x": 0,
                        "y": 1,
                        "xanchor": "left",
                        "yanchor": "top",
                        "font": {"size": 12}
                    },
                    "shapes": shapes,
                    "annotations": annotations,
                    "dragmode": "pan",
                }
            },
            config={"displayModeBar": False, "scrollZoom": False, "staticPlot": False}
        ), "distance"),

        collapsible_section("Distance/Minute", dcc.Graph(
            figure={
                "data": [
                    {
                        "x": gps_df["date"],
                        "y": gps_df["distance_per_min"],
                        "type": "scatter",
                        "mode": "lines+markers",
                        "line": {"color": colors[0]},
                        "marker": {"size": 6},
                        "name": "(m/min)",
                        "showlegend": False,
                        "connectgaps": True
                    },
                    {
                        "x": [x_range[0], x_range[1]],
                        "y": [match_avg_distance_per_min] * 2,
                        "type": "scatter",
                        "mode": "lines",
                        "line": {"color": colors[1], "dash": "dash", "width": 1},
                        "name": "Match Avg"
                    },
                    {
                        "x": [x_range[0], x_range[1]],
                        "y": [training_avg_distance_per_min] * 2,
                        "type": "scatter",
                        "mode": "lines",
                        "line": {"color": colors[2], "dash": "dash", "width": 1},
                        "name": "Training Avg"
                    }
                ],
                "layout": {
                    "xaxis": {"title": "Date", "range": x_range},
                    "yaxis": {"title": "m/min", "fixedrange": True},
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
                    "dragmode": "pan"
                }
            },
            config={"displayModeBar": False, "scrollZoom": False, "staticPlot": False}
        ), "distance_per_min"),


        collapsible_section("Top Speed", dcc.Graph(
            figure={
                "data": [
                    {
                        "x": gps_df[gps_df["day_duration"] > 0]["date"],
                        "y": gps_df[gps_df["day_duration"] > 0]["peak_speed"],
                        "type": "scatter",
                        "mode": "lines+markers",
                        "line": {"color": colors[0]},
                        "marker": {"size": 6},
                        "name": "km/h",
                        "showlegend": False,
                        "connectgaps": True
                    },
                    {
                        "x": [x_range[0], x_range[1]],
                        "y": [match_avg_peak_speed] * 2,
                        "type": "scatter",
                        "mode": "lines",
                        "line": {"color": colors[1], "dash": "dash", "width": 1},
                        "name": "Match Avg"
                    },
                    {
                        "x": [x_range[0], x_range[1]],
                        "y": [training_avg_peak_speed] * 2,
                        "type": "scatter",
                        "mode": "lines",
                        "line": {"color": colors[2], "dash": "dash", "width": 1},
                        "name": "Training Avg"
                    }
                ],
                "layout": {
                    "xaxis": {"title": "Date", "range": x_range},
                    "yaxis": {"title": "m/min", "fixedrange": True},
                    "margin": {"l": 40, "r": 10, "t": 30, "b": 40},
                    "height": 300,
                    "plot_bgcolor": "#fff",
                    "paper_bgcolor": "#fff",
                    "legend": {
                        "x": 0,
                        "y": 0.1,
                        "xanchor": "left",
                        "yanchor": "bottom",
                        "font": {"size": 12}
                    },
                    "shapes": shapes,
                    "annotations": annotations,
                    "dragmode": "pan"
                }
            },
            config={"displayModeBar": False, "scrollZoom": False, "staticPlot": False}
        ), "top_speed"),

        collapsible_section("Distance at High-Speed",
        html.Div([
            html.H4("Distance at High-Speed", style={"marginBottom": "6px", "fontFamily": "CFC Serif"}),
            dcc.Dropdown(
                id="speed-threshold-dropdown",
                options=[
                    {"label": ">21 km/h", "value": "distance_over_21"},
                    {"label": ">24 km/h", "value": "distance_over_24"},
                    {"label": ">27 km/h", "value": "distance_over_27"},
                ],
                value="distance_over_21",
                clearable=False,
                style={"width": "200px", "marginBottom": "10px"}
            ),
            dcc.Graph(id="high-speed-graph", config={"displayModeBar": False})
        ], style={"marginTop": "30px"}), "high_speed"),
        
        collapsible_section("Accel/Decel Efforts",
        html.Div([
            dcc.Dropdown(
                id="accel-threshold-dropdown",
                options=[
                    {"label": ">2.5 m/s^2", "value": "accel_decel_over_2_5"},
                    {"label": ">3.5 m/s^2", "value": "accel_decel_over_3_5"},
                    {"label": ">4.5 m/s^2", "value": "accel_decel_over_4_5"},
                ],
                value="accel_decel_over_2_5",
                clearable=False,
                style={"width": "200px", "marginBottom": "10px"}
            ),
            dcc.Graph(id="high-accel-graph", config={"displayModeBar": False})
        ], style={"marginTop": "30px"}), "accel_decel"),

        collapsible_section(
            "Heart Rate Zone Duration",
            html.Div([
                html.Div([
                    html.H5(zone, style={"margin": "0", "fontSize": "10px", "color": "#555"}),
                    html.P(f"{percentage:.1f}%", style={"margin": "0", "fontWeight": "bold"})
                ], style={"flex": "1"}) for zone, percentage in zone_percentages.items()
            ] + [
                dcc.Graph(
                    figure={
                        "data": [
                            {
                                "x": filtered_df["date"],
                                "y": filtered_df[f"hr_zone_{i}_sec"],
                                "stackgroup": "one",
                                "name": f"Zone {i}",
                                "line": {"width": 0.5, "color": zone_colors[i - 1]},
                                "fillcolor": zone_colors[i - 1]
                            } for i in range(1, 5)
                        ],
                        "layout": {
                            "xaxis": {"title": "Date", "range": x_range},
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
                            "dragmode": "pan"
                        }
                    },
                    config={"displayModeBar": False, "scrollZoom": False, "staticPlot": False}
                )
            ], style={"display": "flex", "flexDirection": "column", "gap": "10px"}),
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
                        style={"width": "300px", "marginBottom": "10px"}
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

    # Filter for date range
    filtered_df = gps_df[(gps_df["date"] >= start_date) & (gps_df["date"] <= end_date) & (gps_df["day_duration"] > 0)]

    # Calculate averages for match/training days
    match_avg = gps_df[gps_df["is_match_day"]][speed_column].mean()
    training_avg = gps_df[gps_df["is_training_day"]][speed_column].mean()

    # Matchday vertical lines and labels
    matchdays = filtered_df[filtered_df["is_match_day"]]
    shapes = [{
        "type": "line",
        "x0": row["date"],
        "x1": row["date"],
        "y0": 0,
        "y1": 1,
        "xref": "x",
        "yref": "paper",
        "line": {"color": "gray", "width": 1}
    } for _, row in matchdays.iterrows()]
    annotations = [{
        "x": row["date"],
        "y": 1.1,
        "xref": "x",
        "yref": "paper",
        "text": row["opposition_code"],
        "showarrow": False,
        "font": {"color": "gray", "size": 10}
    } for _, row in matchdays.iterrows()]

    return {
        "data": [
            {
                "x": filtered_df["date"],
                "y": filtered_df[speed_column],
                "name": "(m)",
                "type": "scatter",
                "mode": "lines+markers",
                "line": {"color": colors[0]},
                "marker": {"size": 6},
                "connectgaps": True,
                "showlegend": False
            },
            {
                "x": [start_date, end_date],
                "y": [match_avg] * 2,
                "type": "scatter",
                "mode": "lines",
                "line": {"color": colors[1], "dash": "dash", "width": 1},
                "name": "Match Avg"
            },
            {
                "x": [start_date, end_date],
                "y": [training_avg] * 2,
                "type": "scatter",
                "mode": "lines",
                "line": {"color": colors[2], "dash": "dash", "width": 1},
                "name": "Training Avg"
            }
        ],
        "layout": {
            "xaxis": {"title": "Date", "range": x_range},
            "yaxis": {"title": "Distance (m)", "fixedrange": True},
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
            "dragmode": "pan"
        }
    }

@callback(
    Output("high-accel-graph", "figure"),
    Input("accel-threshold-dropdown", "value"),
    Input("reporting-slider", "value")
)
def update_high_accel_plot(accel_column, selected_range):
    start_date = datetime.fromtimestamp(selected_range[0])
    end_date = datetime.fromtimestamp(selected_range[1])
    x_range = [start_date, end_date]

    # Filter for date range
    filtered_df = gps_df[(gps_df["date"] >= start_date) & (gps_df["date"] <= end_date) & (gps_df["day_duration"] > 0)]

    # Calculate averages for match/training days
    match_avg = gps_df[gps_df["is_match_day"]][accel_column].mean()
    training_avg = gps_df[gps_df["is_training_day"]][accel_column].mean()

    # Matchday vertical lines and labels
    matchdays = filtered_df[filtered_df["is_match_day"]]
    shapes = [{
        "type": "line",
        "x0": row["date"],
        "x1": row["date"],
        "y0": 0,
        "y1": 1,
        "xref": "x",
        "yref": "paper",
        "line": {"color": "gray", "width": 1}
    } for _, row in matchdays.iterrows()]
    annotations = [{
        "x": row["date"],
        "y": 1.1,
        "xref": "x",
        "yref": "paper",
        "text": row["opposition_code"],
        "showarrow": False,
        "font": {"color": "gray", "size": 10}
    } for _, row in matchdays.iterrows()]

    return {
        "data": [
            {
                "x": filtered_df["date"],
                "y": filtered_df[accel_column],
                "name": "num. efforts",
                "type": "scatter",
                "mode": "lines+markers",
                "line": {"color": colors[0]},
                "marker": {"size": 6},
                "connectgaps": True,
                "showlegend": False
            },
            {
                "x": [start_date, end_date],
                "y": [match_avg] * 2,
                "type": "scatter",
                "mode": "lines",
                "line": {"color": colors[1], "dash": "dash", "width": 1},
                "name": "Match Avg"
            },
            {
                "x": [start_date, end_date],
                "y": [training_avg] * 2,
                "type": "scatter",
                "mode": "lines",
                "line": {"color": colors[2], "dash": "dash", "width": 1},
                "name": "Training Avg"
            }
        ],
        "layout": {
            "xaxis": {"title": "Date", "range": x_range},
            "yaxis": {"title": "Distance (m)", "fixedrange": True},
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
            "dragmode": "pan"
        }
    }

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
    filtered_acwr = acwr_df[(acwr_df["date"] >= start_date) & (acwr_df["date"] <= end_date)]

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
        "xaxis": {"title": "Date", "range": x_range},
        "yaxis": {"title": "ACWR", "range": [0, None], "fixedrange": True},
        "margin": {"l": 40, "r": 10, "t": 30, "b": 40},
        "height": 300,
        "plot_bgcolor": "#fff",
        "paper_bgcolor": "#fff",
        "showlegend": False,
        "dragmode": "pan"
        }
    }

from dash import ctx, Output, Input, State, callback

section_ids = [
    "distance", "distance_per_min", "top_speed", "high_speed",
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