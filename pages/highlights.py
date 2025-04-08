from dash import html
import json

# Load fixtures from JSON
with open("DATA/fixtures.json") as f:
    fixtures = json.load(f)

# Create fixture cards
fixture_cards = [
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
        "maxWidth": "600px"
    }) for fix in fixtures
]

# Full highlights layout
layout = html.Div([
    html.H2([
        html.Span("\uea48", className="icon"),
        "Upcoming Fixtures"
    ], className="section-heading"),

    html.Div(fixture_cards),

    html.H2([html.Span("\uebce", className="icon"), "Load Demand"], className="section-heading"),
    html.H2([html.Span("\uebec", className="icon"), "Injury History"], className="section-heading"),
    html.H2([html.Span("\uea9e", className="icon"), "Physical Development"], className="section-heading"),
    html.H2([html.Span("\uead8", className="icon"), "Recovery"], className="section-heading"),
    html.H2([html.Span("\ueb1d", className="icon"), "External Factors"], className="section-heading"),

], style={"padding": "12px"})
