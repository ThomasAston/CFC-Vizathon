import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, callback
import pandas as pd
from datetime import datetime, timedelta

def collapsible_section(title, content, section_id):
    return html.Div([
        html.Div(
            dbc.Button(
                title,
                id=f"{section_id}-toggle",
                className="mb-2",
                color="white",
                style={"width": "90%", "letterSpacing": "1px"}
            ),
            style={"textAlign": "center", "margin": "0 auto", "width": "100%"}
        ),
        dbc.Collapse(
            html.Div(
                content,
                style={"maxWidth": "90%", "margin": "0 auto"}
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
                marks = {
                    int(d.timestamp()): {
                        "label": d.strftime('%b %Y'),
                        "style": {
                            "transform": "translateX(-20px) translateY(12px) rotate(-90deg)",
                            "transformOrigin": "center",
                            "display": "inline-block",
                            "whiteSpace": "nowrap",
                            "fontSize": "12px",
                            "color": "#555"
                        }
                    }
                    for d in pd.date_range(min_date, max_date, freq="2MS")
                }
            )
        ], style={
            "marginBottom": "30px",
            "maxWidth": "90%",
            "margin": "0 auto"
        }),

        html.Div(style={"height": "20px"}),

        html.Div(id=output_id, style={"textAlign": "center"})
    ], style={"textAlign": "center", "marginBottom": "30px"})


def create_fixture_cards(fixtures):
    return html.Div([
        html.Div([
            # Date and Time
            html.Div([
                html.Div(f"{fix['date'][8:10]}-{fix['date'][5:7]}-{fix['date'][0:4]}", style={
                    "fontWeight": "bold",
                    "fontSize": "clamp(12px, 2vw, 18px)"
                }),
                html.Div(fix["time"], style={
                    "fontSize": "clamp(10px, 1.5vw, 16px)",
                    "color": "#555"
                })
            ], style={
                "minWidth": "75px",
                "textAlign": "left",
                "marginRight": "10px",
            }),

            # Team logo and name
            html.Div([
                html.Img(src=fix["team_logo"], style={
                    "height": "32px",
                    "width": "auto",
                    "marginRight": "10px"
                }),
                html.Div(f"{fix['opponent']} ({fix['venue']})", style={
                    "fontWeight": "bold",
                    "fontSize": "clamp(10px, 2vw, 18px)",
                    "whiteSpace": "nowrap",
                    "overflow": "hidden",
                    "textOverflow": "ellipsis"
                })
            ], style={
                "display": "flex",
                "alignItems": "center",
                "minWidth": "150px",
                "justifyContent": "flex-center",
                "marginLeft": "auto"
            }),

            # Competition logo only (center aligned)
            html.Div([
                html.Img(src=fix["logo"], style={
                    "height": "22px",
                    "width": "auto"
                })
            ], style={
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "flex-center",
                "marginLeft": "auto"
            }),

        ], style={
            "display": "flex",
            "alignItems": "center",
            "padding": "12px 16px",
            "border": "1px solid #ccc",
            "borderRadius": "8px",
            "fontFamily": "CFC Serif",
            "marginBottom": "12px",
            "flexWrap": "nowrap",
            "width": "100%",  # Force cards to have the same width
            "maxWidth": "600px",  # Ensure cards do not exceed max width
            "minWidth": "300px"   # Ensure cards do not go below min width
        }) for fix in fixtures
    ], style={
        "display": "flex",
        "flexDirection": "column",
        "alignItems": "center",
        "justifyContent": "center",
        "margin": "0 auto",
        "width": "100%",  # Ensure the container respects the card width constraints
        "maxWidth": "600px",
        "minWidth": "300px"
    })
