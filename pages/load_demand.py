from dash import html, dcc, Input, Output, State, callback
import json
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

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

# Load sample GPS data (same for all players for now)
gps_df = pd.read_csv("DATA/CFC GPS Data.csv", encoding="latin-1")
gps_df["date"] = pd.to_datetime(gps_df["date"], format="%d/%m/%Y")

# Keep only the last 6 weeks of data
six_weeks_ago = gps_df["date"].max() - timedelta(weeks=6)
gps_recent = gps_df[gps_df["date"] >= six_weeks_ago]

# Calculate ACWR
def compute_acwr(df):
    df = df.sort_values("date")
    acwr_values = []

    for i in range(len(df)):
        acute_start = df.iloc[max(0, i-6):i+1]  # 7-day window
        chronic_start = df.iloc[max(0, i-27):i+1]  # 28-day window

        acute = acute_start["distance"].mean()
        chronic = chronic_start["distance"].mean()

        acwr = acute / chronic if chronic != 0 else 0
        acwr_values.append(acwr)

    df = df.copy()
    df["acwr"] = acwr_values
    return df  # Return recent data with ACWR

gps_acwr = compute_acwr(gps_df)

def render_load_demand(player_id):
    # Define x-axis limits for last 6 weeks
    last_date = gps_df["date"].max()
    first_date = gps_df["date"].min()
    six_weeks_ago = last_date - timedelta(weeks=6)
    x_range = [six_weeks_ago, last_date]
    # x_range = [first_date, last_date]

    return html.Div([
        html.H4("Distance Covered (Last 6 Weeks)", style={"marginBottom": "10px"}),
        dcc.Graph(
            figure={
                "data": [
                    {
                        "x": gps_df["date"],
                        "y": gps_df["distance"],
                        "type": "scatter",
                        "mode": "lines+markers",
                        "line": {"color": "#007ACC"},
                        "marker": {"size": 6},
                        "name": "Distance",
                        "connectgaps": True
                    }
                ],
                "layout": {
                    "xaxis": {
                        "title": "Date",
                        "range": x_range  # 👈 restrict visible data
                    },
                    "yaxis": {"title": "Distance (m)"},
                    "margin": {"l": 40, "r": 10, "t": 30, "b": 40},
                    "plot_bgcolor": "#fff",
                    "paper_bgcolor": "#fff",
                }
            },
            config={"displayModeBar": False}
        ),

        html.H4("Acute:Chronic Workload Ratio (ACWR)", style={"marginTop": "30px", "marginBottom": "10px"}),
        dcc.Graph(
            figure={
                "data": [
                    {
                        "x": gps_acwr["date"],
                        "y": gps_acwr["acwr"],
                        "type": "scatter",
                        "mode": "lines+markers",
                        "line": {"color": "#FF800E"},
                        "marker": {"size": 6},
                        "name": "ACWR"
                    },
                    {
                        "x": gps_acwr["date"],
                        "y": [1.5] * len(gps_acwr),
                        "type": "scatter",
                        "mode": "lines",
                        "line": {"dash": "dash", "color": "#e74c3c"},
                        "showlegend": False
                    },
                    {
                        "x": gps_acwr["date"],
                        "y": [0.8] * len(gps_acwr),
                        "type": "scatter",
                        "mode": "lines",
                        "line": {"dash": "dash", "color": "#3498db"},
                        "showlegend": False
                    }
                ],
                "layout": {
                    "xaxis": {
                        "title": "Date",
                        "range": x_range  # 👈 match range for consistency
                    },
                    "yaxis": {"title": "ACWR"},
                    "margin": {"l": 40, "r": 10, "t": 30, "b": 40},
                    "plot_bgcolor": "#fff",
                    "paper_bgcolor": "#fff",
                    "showlegend": False,
                    "annotations": [
                        {
                            "x": gps_acwr["date"].iloc[-5],
                            "y": 1.5,
                            "xref": "x",
                            "yref": "y",
                            "text": "Overtraining Threshold",
                            "showarrow": False,
                            "yanchor": "bottom",
                            "font": {"color": "#e74c3c", "size": 12}
                        },
                        {
                            "x": gps_acwr["date"].iloc[-5],
                            "y": 0.8,
                            "xref": "x",
                            "yref": "y",
                            "text": "Undertraining Threshold",
                            "showarrow": False,
                            "yanchor": "bottom",
                            "font": {"color": "#3498db", "size": 12}
                        }
                    ]
                }
            },
            config={"displayModeBar": False}
        )

    ], style={"paddingTop": "10px"})

