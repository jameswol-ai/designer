import plotly.graph_objects as go
import streamlit as st
from engine.layout import generate_layout


def render(project):
    st.subheader("Preliminary Floor Plan")
    floor = st.number_input("Floor", 1, max(1, int(project.floors)), 1)
    columns = st.slider("Plan columns", 1, 6, 2, key="floor_columns")
    layout = generate_layout(project, columns=columns)
    fig = go.Figure()
    for r in layout:
        fig.add_shape(type="rect", x0=r["x"], y0=r["y"], x1=r["x"] + r["width"], y1=r["y"] + r["depth"], line=dict(width=2))
        fig.add_annotation(x=r["x"] + r["width"] / 2, y=r["y"] + r["depth"] / 2, text=r["name"], showarrow=False)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    fig.update_layout(height=700, title=f"Floor {floor}", xaxis_title="m", yaxis_title="m", margin=dict(l=20, r=20, t=45, b=20))
    st.plotly_chart(fig, use_container_width=True)
