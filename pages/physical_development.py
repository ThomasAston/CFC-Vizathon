from dash import callback, dcc, html, Input, Output, State, ctx
from datetime import datetime
from utils.data_loader import load_physical_data, compute_physical_gradient_df
from utils.plot_helpers import base_bar_figure, create_physical_heatmap
from utils.components import date_slider, collapsible_section

phys_df = load_physical_data("DATA/CFC Physical Capability Data_.csv")
gradient_df = compute_physical_gradient_df(phys_df)
max_date = phys_df["testDate"].max()
min_date = phys_df["testDate"].min()

section_ids = ["iso_trends", "dyn_trends"]

def render_physical_development(player_id):
    return html.Div([
        date_slider(
            label_id="reporting-period-physical",
            slider_id="reporting-slider-physical",
            min_date=min_date,
            max_date=max_date,
            initial_weeks=52,
            output_id="physical-demand-output"
        ),
        html.Div(id="physical-demand-output", style={"width": "100%", "marginTop": "40px"}),

        collapsible_section("Isometric Expression Trends", html.Div(id="iso_trends-content"), "iso_trends"),
        collapsible_section("Dynamic Expression Trends", html.Div(id="dyn_trends-content"), "dyn_trends")
    ])


@callback(
    Output("reporting-period-physical", "children"),
    Input("reporting-slider-physical", "value")
)
def update_reporting_label(value):
    start = datetime.fromtimestamp(value[0]).strftime("%d/%m/%Y")
    end = datetime.fromtimestamp(value[1]).strftime("%d/%m/%Y")
    return f"Select Report Period: {start} – {end}"


@callback(
    Output("physical-demand-output", "children"),
    Input("reporting-slider-physical", "value")
)
def update_physical_summary(selected_range):
    start_date, end_date = map(datetime.fromtimestamp, selected_range)
    df_filtered = phys_df[
        (phys_df["testDate"] >= start_date) &
        (phys_df["testDate"] <= end_date) &
        (phys_df["benchmarkPct"].notna())
    ]

    return html.Div([
        html.H3("Average Benchmark % Over Reporting Period", style={
            "textAlign": "center", "marginBottom": "20px", "marginTop": "50px"
        }),
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
    ])


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
    Output("iso_trends-content", "children"),
    Input("iso_trends-collapse", "is_open"),
    Input("reporting-slider-physical", "value")
)
def render_iso_trends(is_open, selected_range):
    if not is_open:
        return None
    return html.Div([
        html.Div([
            dcc.Dropdown(
                id="iso-movement-dropdown",
                options=[{"label": m.title(), "value": m}
                         for m in phys_df[phys_df["expression"] == "isometric"]["movement"].unique()],
                value="agility",
                clearable=False,
                searchable=False,
                style={"minWidth": "200px", "flex": "1"}
            ),
            dcc.Dropdown(
                id="iso-quality-dropdown",
                options=[],
                value="acceleration",
                clearable=False,
                searchable=False,
                style={"minWidth": "200px", "flex": "1"}
            )
        ], style={
            "display": "flex", "flexWrap": "wrap", "gap": "10px",
            "justifyContent": "center", "marginBottom": "10px"
        }),
        dcc.Graph(id="iso-trend-graph", config={"displayModeBar": False})
    ])


@callback(
    Output("dyn_trends-content", "children"),
    Input("dyn_trends-collapse", "is_open"),
    Input("reporting-slider-physical", "value")
)
def render_dyn_trends(is_open, selected_range):
    if not is_open:
        return None
    return html.Div([
        html.Div([
            dcc.Dropdown(
                id="dyn-movement-dropdown",
                options=[{"label": m.title(), "value": m}
                         for m in phys_df[phys_df["expression"] == "dynamic"]["movement"].unique()],
                value="agility",
                clearable=False,
                searchable=False,
                style={"minWidth": "200px", "flex": "1"}
            ),
            dcc.Dropdown(
                id="dyn-quality-dropdown",
                options=[],
                value="acceleration",
                clearable=False,
                searchable=False,
                style={"minWidth": "200px", "flex": "1"}
            )
        ], style={
            "display": "flex", "flexWrap": "wrap", "gap": "10px",
            "justifyContent": "center", "marginBottom": "10px"
        }),
        dcc.Graph(id="dyn-trend-graph", config={"displayModeBar": False})
    ])

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
    unique_qualities = filtered["quality"].dropna().unique()
    options = [{"label": q.title(), "value": q} for q in unique_qualities]
    default_value = "acceleration" if "acceleration" in unique_qualities else (
        unique_qualities[0] if len(unique_qualities) > 0 else None
    )
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
    unique_qualities = filtered["quality"].dropna().unique()
    options = [{"label": q.title(), "value": q} for q in unique_qualities]
    default_value = "acceleration" if "acceleration" in unique_qualities else (
        unique_qualities[0] if len(unique_qualities) > 0 else None
    )
    return options, default_value

@callback(
    Output("iso-trend-graph", "figure"),
    Input("iso-movement-dropdown", "value"),
    Input("iso-quality-dropdown", "value"),
    Input("reporting-slider-physical", "value")
)
def update_iso_trend_plot(movement, quality, selected_range):
    start, end = map(datetime.fromtimestamp, selected_range)
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
def update_dyn_trend_plot(movement, quality, selected_range):
    start, end = map(datetime.fromtimestamp, selected_range)
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
