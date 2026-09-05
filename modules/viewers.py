import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from engine.viewers import VIEW_MODES, model_summary
from engine.layout import generate_layout


def _floor_plan(project):
    layout = generate_layout(project)
    fig = go.Figure()
    for r in layout:
        fig.add_shape(type="rect", x0=r["x"], y0=r["y"], x1=r["x"] + r["width"], y1=r["y"] + r["depth"], line=dict(width=2))
        fig.add_annotation(x=r["x"] + r["width"] / 2, y=r["y"] + r["depth"] / 2, text=f"{r['name']}<br>{r['area']:.1f} m²", showarrow=False)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    fig.update_layout(height=620, xaxis_title="m", yaxis_title="m", margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)


def _stacked_model(project):
    s = model_summary(project)
    fig = go.Figure()
    for floor in range(project.floors):
        z = floor * 3.2
        fig.add_trace(go.Mesh3d(x=[0, s["floor_width_m"], s["floor_width_m"], 0], y=[0, 0, s["floor_depth_m"], s["floor_depth_m"]], z=[z, z, z, z], i=[0, 0], j=[1, 2], k=[2, 3], opacity=0.55, name=f"Floor {floor + 1}"))
    fig.update_layout(height=650, scene=dict(xaxis_title="X (m)", yaxis_title="Y (m)", zaxis_title="Z (m)"), margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig, use_container_width=True)


def _elevation(project):
    s = model_summary(project)
    height = project.floors * 3.2
    fig = go.Figure()
    fig.add_shape(type="rect", x0=0, y0=0, x1=s["floor_width_m"], y1=height, line=dict(width=2))
    for floor in range(1, project.floors):
        z = floor * 3.2
        fig.add_shape(type="line", x0=0, y0=z, x1=s["floor_width_m"], y1=z, line=dict(width=1))
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    fig.update_layout(height=550, xaxis_title="Width (m)", yaxis_title="Height (m)")
    st.plotly_chart(fig, use_container_width=True)


def _section(project):
    s = model_summary(project)
    height = project.floors * 3.2
    fig = go.Figure()
    fig.add_shape(type="rect", x0=0, y0=0, x1=s["floor_depth_m"], y1=height, line=dict(width=2))
    for floor in range(1, project.floors):
        z = floor * 3.2
        fig.add_shape(type="line", x0=0, y0=z, x1=s["floor_depth_m"], y1=z, line=dict(width=1))
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    fig.update_layout(height=550, xaxis_title="Depth (m)", yaxis_title="Height (m)")
    st.plotly_chart(fig, use_container_width=True)


def render(project):
    st.subheader("Architectural Viewers")
    view = st.selectbox("View", VIEW_MODES, index=2)
    if view == "Dashboard":
        st.info("Use the Dashboard workspace for project metrics and scoring.")
    elif view == "3D Model":
        st.caption("Conceptual massing viewer. This is not a BIM model.")
        _stacked_model(project)
    elif view == "Floor Plan":
        _floor_plan(project)
    elif view == "Site Plan":
        s = model_summary(project)
        st.metric("Estimated floor plate", f"{s['floor_area_m2']:,.1f} m²")
        st.metric("Site area", f"{project.site_area:,.1f} m²")
        _floor_plan(project)
    elif view == "Elevations":
        _elevation(project)
    elif view == "Sections":
        _section(project)
    else:
        st.info("Analysis viewer is reserved for the compliance and engineering engines.")
