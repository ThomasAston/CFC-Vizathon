import plotly.express as px
import plotly.graph_objects as go

def get_matchday_shapes_annotations(df):
    matchday_df = df[df["is_match_day"] == True]

    shapes = [{
        "type": "line",
        "x0": row["date"],
        "x1": row["date"],
        "y0": 0,
        "y1": 1,
        "xref": "x",
        "yref": "paper",
        "line": {"color": "gray", "width": 1}
    } for _, row in matchday_df.iterrows()]

    annotations = [{
        "x": row["date"],
        "y": 1.1,
        "xref": "x",
        "yref": "paper",
        "text": row["opposition_code"],
        "showarrow": False,
        "font": {"color": "gray", "size": 10}
    } for _, row in matchday_df.iterrows()]

    return shapes, annotations

def add_average_lines(fig, match_avg, training_avg, suffix=""):
    fig.add_scatter(
        x=[None], y=[None], mode="lines", name="Match Avg",
        line=dict(color="#d16002", dash="dash", width=1), showlegend=True
    )
    fig.add_scatter(
        x=[None], y=[None], mode="lines", name="Training Avg",
        line=dict(color="#ec9706", dash="dash", width=1), showlegend=True
    )

    fig.add_shape(
        type="line", xref="paper", yref="y",
        x0=0, x1=1, y0=match_avg, y1=match_avg,
        line=dict(color="#d16002", width=1, dash="dash")
    )
    fig.add_shape(
        type="line", xref="paper", yref="y",
        x0=0, x1=1, y0=training_avg, y1=training_avg,
        line=dict(color="#ec9706", width=1, dash="dash")
    )
    return fig

def base_bar_figure(
    df,
    metric,
    x_range,
    match_avg,
    training_avg,
    hover_suffix="",
    yaxis_range=None,
    shapes=None,
    annotations=None
):
    filtered = df[df["metric"] == metric]

    fig = px.bar(
        filtered,
        x="date",
        y="height",
        base="base",
        color="color_val",
        color_continuous_scale="Blues",
        height=300,
        custom_data=["total"]
    )

    fig.update_traces(
        marker_line_width=0,
        hovertemplate=f"%{{customdata[0]:.0f}}{hover_suffix}<extra></extra>"
    )

    # Dummy traces for legend
    fig.add_scatter(
        x=[None], y=[None], mode="lines", name="Match Avg",
        line=dict(color="#d16002", dash="dash", width=1), showlegend=True
    )
    fig.add_scatter(
        x=[None], y=[None], mode="lines", name="Training Avg",
        line=dict(color="#ec9706", dash="dash", width=1), showlegend=True
    )

    avg_lines = [
        {
            "type": "line", "xref": "paper", "yref": "y",
            "x0": 0, "x1": 1,
            "y0": match_avg, "y1": match_avg,
            "line": {"color": "#d16002", "width": 1, "dash": "dash"}
        },
        {
            "type": "line", "xref": "paper", "yref": "y",
            "x0": 0, "x1": 1,
            "y0": training_avg, "y1": training_avg,
            "line": {"color": "#ec9706", "width": 1, "dash": "dash"}
        }
    ]

    fig.update_layout(
        xaxis=dict(title=None, range=x_range, fixedrange=False),
        yaxis=dict(title=None, fixedrange=True, range=yaxis_range),
        plot_bgcolor="#fff",
        paper_bgcolor="#fff",
        margin=dict(l=40, r=10, t=30, b=40),
        showlegend=True,
        dragmode="pan",
        hovermode="x unified",
        bargap=0,
        
        legend=dict(x=0, y=1, xanchor="left", yanchor="top", font=dict(size=12)),
        shapes=[*(shapes or []), *avg_lines],
        annotations=annotations or []
    )

    fig.update_coloraxes(showscale=False)
    return fig


