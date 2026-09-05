from __future__ import annotations

from typing import Dict, Iterable, Optional, Sequence

import plotly.graph_objects as go

from .drawing_graphics import drawing_graphics


def _xy(points):
    return [p[0] for p in points], [p[1] for p in points]


def _add_line(fig, item, visible=True):
    x, y = _xy(item["points"])
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name=item.get("layer", "line"), legendgroup=item.get("layer", "line"), visible=visible, hoverinfo="skip", line={"width": 2}))


def _add_dimension(fig, item, visible=True):
    ext = item.get("extension", [])
    if len(ext) == 4:
        fig.add_trace(go.Scatter(x=[p[0] for p in ext[:2]], y=[p[1] for p in ext[:2]], mode="lines", name="dimensions", legendgroup="dimensions", visible=visible, hoverinfo="skip", line={"width": 1}))
        fig.add_trace(go.Scatter(x=[p[0] for p in ext[2:]], y=[p[1] for p in ext[2:]], mode="lines", name="dimensions", legendgroup="dimensions", visible=visible, hoverinfo="skip", line={"width": 1}))
    x, y = _xy(item.get("points", []))
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines+markers", name="dimensions", legendgroup="dimensions", visible=visible, hovertemplate=item.get("label", "") + "<extra></extra>", line={"width": 1}, marker={"size": 4}))
    if x and y:
        fig.add_annotation(x=sum(x) / len(x), y=sum(y) / len(y), text=item.get("label", ""), showarrow=False, font={"size": 10}, visible=visible)


def _add_text(fig, item, visible=True):
    fig.add_trace(go.Scatter(x=[item["x"]], y=[item["y"]], mode="text", text=[item["text"]], name=item.get("layer", "annotation"), legendgroup=item.get("layer", "annotation"), visible=visible, hoverinfo="skip", textfont={"size": max(8, int(float(item.get("size", 0.14)) * 55))}))


def _add_arc(fig, item, visible=True):
    import math
    angles = [math.radians(item.get("start_deg", 0) + (item.get("end_deg", 90) - item.get("start_deg", 0)) * i / 24) for i in range(25)]
    cx, cy = item.get("center", [0, 0])
    r = float(item.get("radius", 1))
    fig.add_trace(go.Scatter(x=[cx + r * math.cos(a) for a in angles], y=[cy + r * math.sin(a) for a in angles], mode="lines", name=item.get("layer", "arc"), legendgroup=item.get("layer", "arc"), visible=visible, hoverinfo="skip", line={"width": 1}))


def render_graphics(graphics: Dict, layers: Optional[Iterable[str]] = None, title: str = "Architectural Drawing") -> go.Figure:
    allowed = set(layers) if layers is not None else None
    fig = go.Figure()
    for item in graphics.get("graphics", []):
        layer = item.get("layer", "annotation")
        visible = allowed is None or layer in allowed
        if item.get("type") == "line":
            _add_line(fig, item, visible)
        elif item.get("type") == "dimension":
            _add_dimension(fig, item, visible)
        elif item.get("type") == "text":
            _add_text(fig, item, visible)
        elif item.get("type") == "arc":
            _add_arc(fig, item, visible)
    fig.update_layout(title=title, template="simple_white", showlegend=True, hovermode="closest", margin={"l": 20, "r": 20, "t": 50, "b": 20}, xaxis={"title": "m", "scaleanchor": "y", "scaleratio": 1, "showgrid": False, "zeroline": False}, yaxis={"title": "m", "showgrid": False, "zeroline": False})
    fig.update_layout(dragmode="pan")
    return fig


def render_drawing(project, drawing_type: str = "floor_plan", floor: int = 1, layout: Optional[Sequence[Dict]] = None, layers: Optional[Iterable[str]] = None) -> go.Figure:
    data = drawing_graphics(project, drawing_type=drawing_type, floor=floor, layout=layout)
    return render_graphics(data, layers=layers, title=drawing_type.replace("_", " ").title())
