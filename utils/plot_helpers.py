import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash import html, dcc
from utils.constants import colors
import matplotlib.colors as mcolors

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
        "y": 1,
        "xref": "x",
        "yref": "paper",
        "text": row["opposition_code"],
        "showarrow": False,
        "textangle": -90,
        "font": {"color": "gray", "size": 10},
        "yanchor": "bottom"
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

import plotly.graph_objects as go

def base_bar_figure(
    df,
    metric,
    x_range,
    match_avg=None,
    training_avg=None,
    hover_suffix="",
    y_range=[None, None],
    shapes=None,
    annotations=None
):
    filtered = df[df["metric"] == metric]
    
    positive_df = filtered[filtered["total"] >= 0]
    negative_df = filtered[filtered["total"] < 0]

    fig = go.Figure()

    # Positive bars in Blues
    if not positive_df.empty:
        fig.add_trace(go.Bar(
            x=positive_df["date"],
            y=positive_df["height"],
            base=positive_df["base"],
            marker=dict(
            color=positive_df["color_val"],
            colorscale="Blues",
            line=dict(width=0)
            ),
            customdata=positive_df["total"],
            hovertemplate=f"%{{customdata:.2f}}{hover_suffix}<extra></extra>",
            name="Positive",
            showlegend=False
        ))

    # Negative bars in Oranges
    if not negative_df.empty:
        fig.add_trace(go.Bar(
            x=negative_df["date"],
            y=negative_df["height"],
            base=negative_df["base"],
            marker=dict(
                color=negative_df["color_val"],
                colorscale="Oranges",
                line=dict(width=0)
            ),
            customdata=negative_df["total"],
            hovertemplate=f"%{{customdata:.2f}}{hover_suffix}<extra></extra>",
            name="Negative",
            showlegend=False
        ))

    # Add dummy traces for average legends
    if match_avg is not None:
        fig.add_scatter(
            x=[None], y=[None], mode="lines", name="Match Avg",
            line=dict(color="#d16002", dash="dash", width=1), showlegend=True
        )
    if training_avg is not None:
        fig.add_scatter(
            x=[None], y=[None], mode="lines", name="Training Avg",
            line=dict(color="#ec9706", dash="dash", width=1), showlegend=True
        )

    # Add average lines
    avg_lines = []
    if match_avg is not None:
        avg_lines.append({
            "type": "line", "xref": "paper", "yref": "y",
            "x0": 0, "x1": 1,
            "y0": match_avg, "y1": match_avg,
            "line": {"color": "#d16002", "width": 1, "dash": "dash"}
        })
    if training_avg is not None:
        avg_lines.append({
            "type": "line", "xref": "paper", "yref": "y",
            "x0": 0, "x1": 1,
            "y0": training_avg, "y1": training_avg,
            "line": {"color": "#ec9706", "width": 1, "dash": "dash"}
        })

    fig.update_layout(
        xaxis=dict(title=None, range=x_range, fixedrange=True, showline=True, linecolor='gray'),
        yaxis=dict(title=None, fixedrange=True, range=y_range),
        plot_bgcolor="#fff",
        paper_bgcolor="#fff",
        margin=dict(l=40, r=10, t=30, b=40),
        showlegend=True,
        hovermode="x unified",
        bargap=0,
        legend=dict(x=0, y=1, xanchor="left", yanchor="top", font=dict(size=12)),
        shapes=[*(shapes or []), *avg_lines],
        autosize=True,
        height=250,
        annotations=annotations or []
    )

    return fig


def bubble_plot_figure(data):
    return px.scatter(
        data[data["day_duration"] > 0],
        x="distance",
        y="distance_per_min",
        size="distance_over_21",
        color=data["is_match_day"].map({True: "Match", False: "Training"}),
        size_max=30,
        height=400,
        color_discrete_map={"Match": "#d16002", "Training": "#1f77b4"},
        custom_data=["date", "distance", "distance_per_min", "distance_over_21", "session_type"]
    ).update_traces(
        hovertemplate=(
            "<b>%{customdata[0]|%d %b %Y}</b><br><br>"
            "Total Distance: %{customdata[1]:,.0f} m<br>"
            "Average Speed: %{customdata[2]:.1f} m/min<br>"
            "High-Speed Distance: %{customdata[3]:,.0f} m<br>"
            "Session Type: %{customdata[4]}<extra></extra>"
        )
    ).update_layout(
        margin={"l": 40, "r": 10, "t": 30, "b": 40},
        plot_bgcolor="#fff",
        paper_bgcolor="#fff",
        xaxis=dict(title="Total Distance (m)", showline=True, linecolor="gray"),
        yaxis=dict(title="Average Speed (m/min)", showline=True),
        legend_title="Session Type",
        legend=dict(
            x=1, 
            y=1, 
            xanchor="right", 
            yanchor="top", 
            font=dict(size=12),
            bgcolor="rgba(255,255,255,0.5)"  # Add opacity to legend background
        ),
        dragmode=False
    )

def bubble_plot(data, title="Load Profile Overview"):
    return html.Div([
        html.H4(title, style={"textAlign": "center", "marginBottom": "10px"}),
        html.P(
            "Training and match day load profiles. "
            "Bubble size represents total high-speed running distance for a session.",
            style={"textAlign": "left"}
        ),
        dcc.Graph(id="bubble-plot", figure=bubble_plot_figure(data), config={"displayModeBar": False})
    ], style={"maxWidth": "90%", "margin": "0 auto", "marginBottom": "30px"})



def create_physical_heatmap(df_filtered, expression_type, title):
    """
    Creates a dcc.Graph component showing a heatmap for the specified expression type (isometric/dynamic)
    from the physical development data.

    Args:
        df_filtered (pd.DataFrame): Filtered DataFrame with benchmarkPct values
        expression_type (str): "isometric" or "dynamic"
        title (str): Title to display above the heatmap

    Returns:
        html.Div: A Dash component containing the heatmap plot
    """
    df_expr = df_filtered[df_filtered["expression"] == expression_type]
    pivot = df_expr.pivot_table(
        index="quality",
        columns="movement",
        values="benchmarkPct",
        aggfunc="mean"
    ).sort_index()

    pivot.index = pivot.index.str.capitalize()
    pivot.columns = pivot.columns.str.capitalize()

    fig = px.imshow(
        pivot,
        text_auto=".2f",
        color_continuous_scale="Blues",
        aspect="auto"
    ).update_layout(
        margin={"l": 40, "r": 10, "t": 0, "b": 20},
        xaxis_title=None,
        yaxis_title=None,
        coloraxis_showscale=False,
        dragmode=False,
        plot_bgcolor="#fff",
        paper_bgcolor="#fff"
    )

    return html.Div([
        html.H4(title, style={"textAlign": "center"}),
        dcc.Graph(
            figure=fig,
            config={"displayModeBar": False},
            style={
                "height": 400,
                "width": "100%",
                "maxWidth": "90%",
                "margin": "0 auto"
            }
        )
    ], style={
        "width": "100%",
        "maxWidth": "600px",
        "margin": "0 auto",
        "marginBottom": "20px"
    })

def recovery_radar_chart(pivoted_df):
    # Filter to only composite metric columns (excluding total score)
    composite_cols = [col for col in pivoted_df.columns 
                      if col.endswith("_baseline_composite") and col != "emboss_baseline_score"]

    # Drop rows where all composites are missing
    df_clean = pivoted_df[composite_cols].dropna(how="all")
    if df_clean.empty:
        return go.Figure().update_layout(title="No recovery data available.")

    # Get the most recent score for each metric
    latest_scores = df_clean.apply(lambda col: col.dropna().iloc[-1] if not col.dropna().empty else None)

    radar_df = pd.DataFrame({
        "category": [col.replace("_baseline_composite", "").replace("_", " ").title() for col in latest_scores.index],
        "score": latest_scores.values
    }).dropna()

    if radar_df.empty:
        return go.Figure().update_layout(title="No valid composite scores to display.")
    
    fig = go.Figure()
    # Add a circle at r=0 with color colors[1] and dashed line style
    fig.add_trace(go.Scatterpolar(
        r=[0] * len(radar_df["category"]) + [0],
        theta=list(radar_df["category"]) + [radar_df["category"].iloc[0]],
        fill='toself',
        line=dict(color=colors[1]),
        name="Normative Score"
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=list(radar_df["score"]) + [radar_df["score"].iloc[0]],
        theta=list(radar_df["category"]) + [radar_df["category"].iloc[0]],
        fill='toself',
        line=dict(color=colors[0]),
        name="Composite Score"
    ))

    fig.update_layout(
        polar=dict(
            bgcolor='rgba(0,0,0,0)',  # transparent background
            radialaxis=dict(
                visible=True,
                showline=False,
                showgrid=True,
                gridcolor='#ccc',
                gridwidth=0.5,
                tickvals=[],
                range=[-1, 1]
            ),
            angularaxis=dict(
                tickfont=dict(size=10),
                gridcolor='#ccc',
                gridwidth=0.5
            )
        ),
        showlegend=True,
        legend=dict(
            orientation="h",      # horizontal layout
            x=0.5,                # centered horizontally
            y=-0.0,               # place below the chart area
            xanchor="center",
            yanchor="top",
            font=dict(size=10),
            bgcolor="rgba(255,255,255,0.8)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",  # transparent background
        plot_bgcolor="rgba(0,0,0,0)",  # transparent background
        dragmode="pan",
    )

    return fig


def emboss_color(score, vmin=-1, vmax=1):
    """
    Map score from [vmin, vmax] to a color on a red → yellow → green scale.
    """
    cmap = mcolors.LinearSegmentedColormap.from_list("emboss", ["#d62728", "#ffbf00", "#2ca02c"])  # red → yellow → green
    norm_score = (score - vmin) / (vmax - vmin)
    norm_score = max(0, min(1, norm_score))  # clamp between 0 and 1
    return mcolors.to_hex(cmap(norm_score))