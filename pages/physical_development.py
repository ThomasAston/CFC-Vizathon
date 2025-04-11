from utils.data_loader import load_physical_data, compute_physical_gradient_df
from utils.components import date_slider, collapsible_section
from utils.plot_helpers import create_physical_heatmap, base_bar_figure
from dash import callback, dcc, html, Input, Output, State
from datetime import datetime, timedelta
import plotly.express as px
import pandas as pd

phys_df = load_physical_data("DATA/CFC Physical Capability Data_.csv")
max_date = phys_df["testDate"].max()
min_date = phys_df["testDate"].min()

metric = "benchmarkPct"
gradient_df = compute_physical_gradient_df(phys_df)

def render_physical_development(player_id):
    
    return date_slider(
        label_id="reporting-period-physical",
        slider_id="reporting-slider-physical",
        min_date=min_date,
        max_date=max_date,
        initial_weeks=52,
        output_id="physical-demand-output"
    )

@callback(
    Output("reporting-period-physical", "children"),
    Input("reporting-slider-physical", "value")
)
def update_reporting_physical(value):
    start = datetime.fromtimestamp(value[0]).strftime("%d/%m/%Y")
    end = datetime.fromtimestamp(value[1]).strftime("%d/%m/%Y")
    return f"Select Report Period: {start} – {end}"


@callback(
    Output("physical-demand-output", "children"),
    Input("reporting-slider-physical", "value")
)
def update_physical_demand(selected_range):
    start_date = datetime.fromtimestamp(selected_range[0])
    end_date = datetime.fromtimestamp(selected_range[1])

    df_filtered = phys_df[
        (phys_df["testDate"] >= start_date) &
        (phys_df["testDate"] <= end_date) &
        (phys_df["benchmarkPct"].notna())
    ]

    # Filter gradient data for the selected date range
    range_gradient_df = gradient_df[
        (gradient_df["date"] >= start_date) & (gradient_df["date"] <= end_date)
    ]

    return html.Div([
        html.H3("Average Benchmark % Over Reporting Period", style={"textAlign": "center", "marginBottom": "20px", "marginTop": "50px"}),

        html.Div([
            create_physical_heatmap(df_filtered, "isometric", "Isometric Expression"),
            create_physical_heatmap(df_filtered, "dynamic", "Dynamic Expression"),
        ], style={
            "display": "flex",
            "flexDirection": "row",
            "flexWrap": "wrap",
            "justifyContent": "center",
            "gap": "20px"
        }),

        collapsible_section("Isometric Expression Trends", html.Div([
            html.Div([
                    dcc.Dropdown(
                        id="iso-movement-dropdown",
                        options=[{"label": m.title(), "value": m} for m in phys_df[phys_df["expression"] == "isometric"]["movement"].unique()],
                        value="agility",
                        searchable=False,
                        clearable=False,
                        style={"minWidth": "200px", "flex": "1"}
                    ),
                    dcc.Dropdown(
                        id="iso-quality-dropdown",
                        options=[],
                        value="acceleration",
                        searchable=False,
                        clearable=False,
                        style={"minWidth": "200px", "flex": "1"}
                    )
                ], style={
                    "display": "flex",
                    "flexWrap": "wrap",
                    "gap": "10px",
                    "justifyContent": "center",
                    "marginBottom": "10px"
                }),

            dcc.Graph(id="iso-trend-graph", config={"displayModeBar": False})
        ]), "iso_trends"),

        collapsible_section("Dynamic Expression Trends", html.Div([
            html.Div([
                    dcc.Dropdown(
                        id="dyn-movement-dropdown",
                        options=[{"label": m.title(), "value": m} for m in phys_df[phys_df["expression"] == "dynamic"]["movement"].unique()],
                        value="agility",
                        searchable=False,
                        clearable=False,
                        style={"minWidth": "200px", "flex": "1"}
                    ),
                    dcc.Dropdown(
                        id="dyn-quality-dropdown",
                        options=[],
                        value="acceleration",
                        searchable=False,
                        clearable=False,
                        style={"minWidth": "200px", "flex": "1"}
                    )
                ], style={
                    "display": "flex",
                    "flexWrap": "wrap",
                    "gap": "10px",
                    "justifyContent": "center",
                    "marginBottom": "10px"
                }),

            dcc.Graph(id="dyn-trend-graph", config={"displayModeBar": False})
        ]), "dyn_trends")
    ])


@callback(
    Output("iso-trend-graph", "figure"),
    Input("iso-movement-dropdown", "value"),
    Input("iso-quality-dropdown", "value"),
    Input("reporting-slider-physical", "value")
)
def update_iso_trend(movement, quality, selected_range):
    start = datetime.fromtimestamp(selected_range[0])
    end = datetime.fromtimestamp(selected_range[1])

    # Construct metric string
    metric_name = f"isometric_{movement}_{quality}".lower().replace(" ", "_")

    filtered_df = gradient_df[
        (gradient_df["metric"] == metric_name) &
        (gradient_df["date"] >= start) &
        (gradient_df["date"] <= end)
    ]

    return base_bar_figure(
        df=filtered_df,
        metric=metric_name,
        x_range=[start, end],
        y_range=[0, None],
        match_avg=None,
        training_avg=None,
        hover_suffix=" %",
        shapes=[],
        annotations=[]
    )


@callback(
    Output("dyn-trend-graph", "figure"),
    Input("dyn-movement-dropdown", "value"),
    Input("dyn-quality-dropdown", "value"),
    Input("reporting-slider-physical", "value")
)
def update_dyn_trend(movement, quality, selected_range):
    start = datetime.fromtimestamp(selected_range[0])
    end = datetime.fromtimestamp(selected_range[1])

    # Construct metric string
    metric_name = f"dynamic_{movement}_{quality}".lower().replace(" ", "_")

    filtered_df = gradient_df[
        (gradient_df["metric"] == metric_name) &
        (gradient_df["date"] >= start) &
        (gradient_df["date"] <= end)
    ]

    return base_bar_figure(
        df=filtered_df,
        metric=metric_name,
        x_range=[start, end],
        y_range=[0, None],
        match_avg=None,
        training_avg=None,
        hover_suffix=" %",
        shapes=[],
        annotations=[]
    )



@callback(
    Output("iso_trends-collapse", "is_open"),
    Input("iso_trends-toggle", "n_clicks"),
    State("iso_trends-collapse", "is_open"),
    prevent_initial_call=True
)
def toggle_iso_section(n, is_open):
    if n:
        return not is_open
    return is_open

@callback(
    Output("dyn_trends-collapse", "is_open"),
    Input("dyn_trends-toggle", "n_clicks"),
    State("dyn_trends-collapse", "is_open"),
    prevent_initial_call=True
)
def toggle_dyn_section(n, is_open):
    if n:
        return not is_open
    return is_open

@callback(
    Output("iso-quality-dropdown", "options"),
    Output("iso-quality-dropdown", "value"),
    Input("iso-movement-dropdown", "value")
)
def update_iso_quality_options(selected_movement):
    filtered = phys_df[
        (phys_df["expression"] == "isometric") &
        (phys_df["movement"] == selected_movement)
    ]
    unique_qualities = filtered["quality"].unique()
    options = [{"label": q.title(), "value": q} for q in unique_qualities]

    # Use "acceleration" if it's in the options, otherwise pick the first one
    default_value = "acceleration" if "acceleration" in unique_qualities else (unique_qualities[0] if len(unique_qualities) > 0 else None)

    return options, default_value

@callback(
    Output("dyn-quality-dropdown", "options"),
    Output("dyn-quality-dropdown", "value"),
    Input("dyn-movement-dropdown", "value")
)
def update_dyn_quality_options(selected_movement):
    filtered = phys_df[
        (phys_df["expression"] == "dynamic") &
        (phys_df["movement"] == selected_movement)
    ]
    unique_qualities = filtered["quality"].unique()
    options = [{"label": q.title(), "value": q} for q in unique_qualities]

    default_value = "acceleration" if "acceleration" in unique_qualities else (unique_qualities[0] if len(unique_qualities) > 0 else None)

    return options, default_value

