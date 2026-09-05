import plotly.graph_objects as go
import streamlit as st
from engine.layout import generate_layout


def render(project):
    st.subheader("Space Planner")
    columns = st.slider("Layout columns", 1, 6, 2)
    layout = generate_layout(project, columns=columns)
    fig = go.Figure()
    for r in layout:
        fig.add_shape(type="rect", x0=r["x"], y0=r["y"], x1=r["x"] + r["width"], y1=r["y"] + r["depth"], line=dict(width=2))
        fig.add_annotation(x=r["x"] + r["width"] / 2, y=r["y"] + r["depth"] / 2, text=f"{r['name']}<br>{r['area']:.1f} m²", showarrow=False)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    fig.update_layout(height=650, xaxis_title="m", yaxis_title="m", margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)
