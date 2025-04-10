import dash_bootstrap_components as dbc
from dash import html, dcc
import pandas as pd
from datetime import timedelta

def collapsible_section(title, content, section_id):
    return html.Div([
        dbc.Button(
            title,
            id=f"{section_id}-toggle",
            className="mb-2",
            color="white",
            style={"width": "90%", "textAlign": "center", "letterSpacing": "1px"}  # Reduced letter spacing
        ),
        dbc.Collapse(
            html.Div(
                content,
                style={"maxWidth": "90%", "margin": "0 auto"}  # ⬅️ limit width and center
            ),
            id=f"{section_id}-collapse",
            is_open=False
        )
    ], style={"marginBottom": "20px"})

def date_slider(
    label_id,
    slider_id,
    min_date,
    max_date,
    initial_weeks=6,
    output_id="load-demand-output"
):
    return html.Div([
        html.Div([
            html.H2(id=label_id, style={
                "fontWeight": "light",
                "fontSize": "18px",
                "marginBottom": "20px",
                "display": "block",
                "textAlign": "center"
            }),
            dcc.RangeSlider(
                id=slider_id,
                min=int(min_date.timestamp()),
                max=int(max_date.timestamp()),
                step=7 * 24 * 60 * 60,  # weekly steps
                value=[
                    int((max_date - timedelta(weeks=initial_weeks)).timestamp()),
                    int(max_date.timestamp())
                ],
                marks={
                    int(d.timestamp()): d.strftime('%b %Y')
                    for d in pd.date_range(min_date, max_date, freq="2MS")
                },
            )
        ], style={
            "marginBottom": "30px",
            "maxWidth": "90%",
            "margin": "0 auto"
        }),

        html.Div(style={"height": "20px"}),

        html.Div(id=output_id, style={"textAlign": "center"})
    ], style={"textAlign": "center", "marginBottom": "30px"})
