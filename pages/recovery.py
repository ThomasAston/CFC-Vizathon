from utils.data_loader import load_recovery_data, compute_gradient_df, load_gps_data
from utils.plot_helpers import recovery_radar_chart, emboss_color, base_bar_figure, get_matchday_shapes_annotations
from utils.components import date_slider, collapsible_section
import dash_bootstrap_components as dbc
from datetime import datetime
from dash import callback, dcc, html, Input, Output


rec_df = load_recovery_data("DATA/CFC Recovery status Data.csv")
max_date = rec_df["date"].max()
min_date = rec_df["date"].min()
metrics = [col for col in rec_df.columns if col != "date"]
gradient_df = compute_gradient_df(rec_df, metrics)

gps_df = load_gps_data("DATA/CFC GPS Data.csv")
shapes, annotations = get_matchday_shapes_annotations(gps_df)

def render_recovery(player_id):

    radar_fig = recovery_radar_chart(rec_df)
    score = rec_df["emboss_baseline_score"].iloc[-1]
    score_color = emboss_color(score)

    # Inside render_recovery:
    composite_options = [
        {"label": metric.replace("_baseline_composite", "").replace("_", " ").title(), "value": metric}
        for metric in metrics if metric.endswith("_baseline_composite")
    ]

    completeness_options = [
        {"label": metric.replace("_completeness", "").replace("_", " ").title(), "value": metric}
        for metric in metrics if metric.endswith("_completeness")
    ]

    composite_section = collapsible_section("Composite Score Trends", html.Div([
        html.Div([
            dcc.Dropdown(
                id="composite-metric-dropdown",
                options=composite_options,
                value="sleep_baseline_composite",
                clearable=False,
                searchable=False,
                style={"width": "250px", "margin": "0 auto 20px auto"}
            )
        ], style={"textAlign": "center"}),

        dcc.Graph(id="composite-trend-graph", config={"displayModeBar": False})
    ]), "composite_trend")

    completeness_section = collapsible_section("Completeness Score Trends", html.Div([
        html.Div([
            dcc.Dropdown(
                id="completeness-metric-dropdown",
                options=completeness_options,
                value="sleep_baseline_completeness",
                clearable=False,
                searchable=False,
                style={"width": "300px", "margin": "0 auto 20px auto"}
            )
        ], style={"textAlign": "center"}),

        dcc.Graph(id="completeness-trend-graph", config={"displayModeBar": False})
    ]), "completeness_trend")

    overall_section = collapsible_section("Overall Recovery Score", html.Div([
        dcc.Graph(id="overall-recovery-graph", config={"displayModeBar": False})
    ]), "overall_recovery")

    return html.Div([
        collapsible_section(
        "Module Guide",
        html.Div([
            html.P("This module summarises player recovery using composite scores derived from subjective and/or objective data sources."),
            html.Ul([
                html.Li("Composite scores represent a weighted summary of recovery-related indicators (e.g. sleep, soreness, fatigue)."),
                html.Li("Use the date slider to explore how recovery status has changed over time."),
                html.Li("Toggle between different composite metrics to analyse trends or red flags."),
            ]),
            html.P("Use this to support decisions around rest, rehabilitation, and load management."),
        ]),
        section_id="recovery_info"
        ),

        html.H3("Most Recent Scores", style={"textAlign": "center"}),

        html.Div([
            html.H4("Overall Score", style={"marginBottom": "4px", "color": "#444"}),
            html.H2(
                f"{score:.2f}",
                style={
                    "color": score_color,
                    "fontWeight": "bold",
                    "margin": "0",
                    "fontSize": "32px"
                }
            )
        ], style={"textAlign": "center", "marginBottom": "20px"}),

        dcc.Graph(figure=radar_fig, config={"displayModeBar": False}),

        date_slider(
            label_id="reporting-period-recovery",
            slider_id="reporting-slider-recovery",
            min_date=min_date,
            max_date=max_date,
            initial_weeks=12,
            output_id="recovery-status-output",
        ),
        
        composite_section,
        completeness_section,
        overall_section

    ], style={"margin": "0 auto"})

    
@callback(
    Output("reporting-period-recovery", "children"),
    Input("reporting-slider-recovery", "value")
)
def update_reporting_recovery(value):
    start = datetime.fromtimestamp(value[0]).strftime("%d/%m/%Y")
    end = datetime.fromtimestamp(value[1]).strftime("%d/%m/%Y")
    return f"Select Report Period: {start} – {end}"

@callback(
    Output("recovery-radar-chart", "figure"),
    Input("reporting-slider-recovery", "value")
)
def update_recovery(selected_range):
    return recovery_radar_chart(rec_df)


@callback(
    Output("composite-trend-graph", "figure"),
    Input("composite-metric-dropdown", "value"),
    Input("reporting-slider-recovery", "value")
)
def update_composite_trend(metric, selected_range):
    start = datetime.fromtimestamp(selected_range[0])
    end = datetime.fromtimestamp(selected_range[1])
    filtered_df = gradient_df[
        (gradient_df["date"] >= start) & (gradient_df["date"] <= end) & (gradient_df["metric"] == metric)
    ]

    return base_bar_figure(
        df=filtered_df,
        metric=metric,
        x_range=[start, end],
        match_avg=None,
        training_avg=None,
        hover_suffix=" %",
        shapes=shapes,
        annotations=annotations
    )

from dash import ctx, State

@callback(
    Output("composite_trend-collapse", "is_open"),
    Input("composite_trend-toggle", "n_clicks"),
    State("composite_trend-collapse", "is_open"),
    prevent_initial_call=True
)
def toggle_composite_section(n, is_open):
    if n:
        return not is_open
    return is_open



@callback(
    Output("completeness-trend-graph", "figure"),
    Input("completeness-metric-dropdown", "value"),
    Input("reporting-slider-recovery", "value")
)
def update_completeness_trend(metric, selected_range):
    start = datetime.fromtimestamp(selected_range[0])
    end = datetime.fromtimestamp(selected_range[1])
    filtered_df = gradient_df[
        (gradient_df["date"] >= start) & (gradient_df["date"] <= end) & (gradient_df["metric"] == metric)
    ]

    return base_bar_figure(
        df=filtered_df,
        metric=metric,
        x_range=[start, end],
        match_avg=None,
        training_avg=None,
        hover_suffix=" %",
        shapes=shapes,
        annotations=annotations
    )

from dash import ctx, State

@callback(
    Output("completeness_trend-collapse", "is_open"),
    Input("completeness_trend-toggle", "n_clicks"),
    State("completeness_trend-collapse", "is_open"),
    prevent_initial_call=True
)
def toggle_completeness_section(n, is_open):
    if n:
        return not is_open
    return is_open

@callback(
    Output("overall-recovery-graph", "figure"),
    Input("reporting-slider-recovery", "value")
)
def update_overall_score(selected_range):
    start = datetime.fromtimestamp(selected_range[0])
    end = datetime.fromtimestamp(selected_range[1])

    filtered_df = gradient_df[
        (gradient_df["date"] >= start) & 
        (gradient_df["date"] <= end) & 
        (gradient_df["metric"] == "emboss_baseline_score")
    ]

    return base_bar_figure(
        df=filtered_df,
        metric="emboss_baseline_score",
        x_range=[start, end],
        hover_suffix=" %",
        y_range=[None, None],
        shapes=shapes,
        annotations=annotations
    )

@callback(
    Output("overall_recovery-collapse", "is_open"),
    Input("overall_recovery-toggle", "n_clicks"),
    State("overall_recovery-collapse", "is_open"),
    prevent_initial_call=True
)
def toggle_overall_section(n, is_open):
    if n:
        return not is_open
    return is_open

@callback(
    Output("recovery_info-collapse", "is_open"),
    Input("recovery_info-toggle", "n_clicks"),
    State("recovery_info-collapse", "is_open"),
    prevent_initial_call=True
)
def toggle_recovery_info(n, is_open):
    if n:
        return not is_open
    return is_open
