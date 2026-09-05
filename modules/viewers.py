import plotly.graph_objects as go
import streamlit as st

from engine.viewers import VIEW_MODES, model_summary
from engine.layout import generate_layout
from engine.furniture import furniture_schedule
from engine.structure_grid import candidate_grids
from engine.vertical import stair_schedule
from engine.environment import environmental_checks
from engine.egress import egress_summary
from engine.site import parking_plan


def _floor_plan(project, floor=1, labels=True, grid=True, dimensions=True):
    rooms = [r for r in generate_layout(project) if r.get("floor", 1) == floor]
    fig = go.Figure()
    for r in rooms:
        x0, y0 = r["x"], r["y"]
        x1, y1 = x0 + r["width"], y0 + r["depth"]
        fig.add_shape(type="rect", x0=x0, y0=y0, x1=x1, y1=y1, line=dict(width=2))
        if labels:
            fig.add_annotation(x=(x0+x1)/2, y=(y0+y1)/2, text=f"{r['name']}<br>{r['area']:.1f} m²", showarrow=False)
        if dimensions:
            fig.add_annotation(x=(x0+x1)/2, y=y0-0.18, text=f"{r['width']:.2f} m", showarrow=False, font=dict(size=10))
            fig.add_annotation(x=x1+0.18, y=(y0+y1)/2, text=f"{r['depth']:.2f} m", showarrow=False, font=dict(size=10), textangle=-90)
    if grid:
        max_x = max((r["x"] + r["width"] for r in rooms), default=20)
        max_y = max((r["y"] + r["depth"] for r in rooms), default=20)
        for v in range(0, int(max(max_x, max_y)) + 5, 5):
            fig.add_vline(x=v, line_width=1, opacity=0.2)
            fig.add_hline(y=v, line_width=1, opacity=0.2)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    fig.update_layout(height=650, xaxis_title="m", yaxis_title="m", margin=dict(l=20,r=20,t=20,b=20))
    return fig, rooms


def _stacked_model(project):
    s = model_summary(project)
    width, depth = s["floor_width_m"], s["floor_depth_m"]
    floor_height = 3.2
    fig = go.Figure()
    for floor in range(project.floors):
        z0, z1 = floor * floor_height, (floor + 1) * floor_height
        x = [0,width,width,0,0,width,width,0]
        y = [0,0,depth,depth,0,0,depth,depth]
        z = [z0,z0,z0,z0,z1,z1,z1,z1]
        i=[0,0,0,4,4,4,0,1,2,3]
        j=[1,2,4,5,6,7,1,5,6,7]
        k=[2,3,5,6,7,4,5,6,7,4]
        fig.add_trace(go.Mesh3d(x=x,y=y,z=z,i=i,j=j,k=k,opacity=0.35,name=f"Floor {floor+1}"))
    fig.update_layout(height=680,scene=dict(xaxis_title="X (m)",yaxis_title="Y (m)",zaxis_title="Z (m)"),margin=dict(l=0,r=0,t=20,b=0))
    return fig


def _elevation(project, title, depth=False):
    s = model_summary(project)
    span = s["floor_depth_m"] if depth else s["floor_width_m"]
    height = project.floors * 3.2
    fig = go.Figure()
    fig.add_shape(type="rect",x0=0,y0=0,x1=span,y1=height,line=dict(width=2))
    for floor in range(1,project.floors):
        fig.add_shape(type="line",x0=0,y0=floor*3.2,x1=span,y1=floor*3.2,line=dict(width=1))
    fig.add_annotation(x=span/2,y=height+0.5,text=title,showarrow=False)
    fig.update_yaxes(scaleanchor="x",scaleratio=1)
    fig.update_layout(height=550,xaxis_title="m",yaxis_title="Height (m)")
    return fig


def render(project):
    st.subheader("Architectural Viewers")
    st.caption("Interactive conceptual visualization of the current architectural model.")
    view = st.selectbox("View", VIEW_MODES, index=min(2, len(VIEW_MODES)-1))
    if view == "Dashboard":
        st.info("Use the Dashboard workspace for project metrics and scoring.")
    elif view == "3D Model":
        st.plotly_chart(_stacked_model(project), use_container_width=True)
    elif view == "Floor Plan":
        floor = st.slider("Floor", 1, max(1, project.floors), 1)
        c1, c2, c3 = st.columns(3)
        labels = c1.checkbox("Room labels", True)
        grid = c2.checkbox("Grid overlay", True)
        dimensions = c3.checkbox("Dimensions", True)
        fig, rooms = _floor_plan(project, floor, labels, grid, dimensions)
        st.plotly_chart(fig, use_container_width=True)
        st.subheader("Room inspection")
        if rooms:
            names = [f"{r['name']} | {r['area']:.1f} m²" for r in rooms]
            selected = st.selectbox("Select room", names)
            room = rooms[names.index(selected)]
            st.dataframe([room], use_container_width=True, hide_index=True)
        else:
            st.info("No spaces are assigned to this floor.")
    elif view == "Site Plan":
        fig, _ = _floor_plan(project, 1, True, True, True)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe([parking_plan(project)], use_container_width=True, hide_index=True)
    elif view == "Elevations":
        st.plotly_chart(_elevation(project, "Elevation"), use_container_width=True)
    elif view == "Sections":
        st.plotly_chart(_elevation(project, "Section", True), use_container_width=True)
    else:
        st.write("Furniture and equipment")
        st.dataframe(furniture_schedule(project), use_container_width=True, hide_index=True)
        st.write("Structural grid candidates")
        st.dataframe(candidate_grids(project), use_container_width=True, hide_index=True)
        st.write("Vertical circulation")
        st.dataframe(stair_schedule(project), use_container_width=True, hide_index=True)
        st.write("Environmental analysis")
        st.dataframe(environmental_checks(project), use_container_width=True, hide_index=True)
        st.write("Egress summary")
        st.json(egress_summary(project))
