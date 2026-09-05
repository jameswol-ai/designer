import plotly.graph_objects as go
import streamlit as st

from engine.viewers import VIEW_MODES, model_summary
from engine.layout import generate_layout
from engine.furniture import furniture_schedule
from engine.furniture_model import furniture_elements
from engine.structure_grid import candidate_grids
from engine.dimensions import grid_axes, grid_schedule, dimension_chains, dimension_summary
from engine.vertical import stair_schedule
from engine.environment import environmental_checks
from engine.egress import egress_summary
from engine.site import parking_plan
from engine.architectural_model import building_elements, element_summary

FLOOR_HEIGHT = 3.2


def _floor_plan(project, floor=1, labels=True, grid=True, dimensions=True, structural_grid=True):
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

    if structural_grid:
        axes = grid_axes(project)
        for index, x in enumerate(axes["x"]):
            fig.add_vline(x=x, line_width=1, opacity=0.35)
            fig.add_annotation(x=x, y=0, text=chr(65 + index), showarrow=False, yshift=-22)
        for index, y in enumerate(axes["y"], start=1):
            fig.add_hline(y=y, line_width=1, opacity=0.35)
            fig.add_annotation(x=0, y=y, text=str(index), showarrow=False, xshift=-18)

    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    fig.update_layout(height=650, xaxis_title="m", yaxis_title="m", margin=dict(l=40,r=40,t=20,b=40))
    return fig, rooms


def _box_vertices(width, depth, z0, z1):
    return (
        [0, width, width, 0, 0, width, width, 0],
        [0, 0, depth, depth, 0, 0, depth, depth],
        [z0, z0, z0, z0, z1, z1, z1, z1],
    )


def _element_trace(element):
    x, y, z = element.x, element.y, element.z
    w, d, h = element.width, element.depth, element.height
    if element.kind in {"wall", "column", "slab"}:
        x0, x1 = x, x + w
        y0, y1 = y, y + d
        z0, z1 = z, z + h
        vx = [x0,x1,x1,x0,x0,x1,x1,x0]
        vy = [y0,y0,y1,y1,y0,y0,y1,y1]
        vz = [z0,z0,z0,z0,z1,z1,z1,z1]
        i = [0,0,0,4,4,4,0,1,2,3]
        j = [1,2,4,5,6,7,1,5,6,7]
        k = [2,3,5,6,7,4,5,6,7,4]
        return go.Mesh3d(x=vx, y=vy, z=vz, i=i, j=j, k=k, opacity=0.75, name=element.name, hovertemplate=f"{element.name}<extra></extra>")
    if element.kind == "stair":
        steps = 10
        traces = []
        step_depth = d / steps if steps else d
        for n in range(steps):
            traces.append(go.Mesh3d(
                x=[x,x+w,x+w,x,x,x+w,x+w,x],
                y=[y+n*step_depth,y+n*step_depth,y+(n+1)*step_depth,y+(n+1)*step_depth,y+n*step_depth,y+n*step_depth,y+(n+1)*step_depth,y+(n+1)*step_depth],
                z=[z+n*h/steps]*4+[z+(n+1)*h/steps]*4,
                i=[0,0,0,4,4,4,0,1,2,3], j=[1,2,4,5,6,7,1,5,6,7], k=[2,3,5,6,7,4,5,6,7,4],
                opacity=0.8, name=element.name, showlegend=n == 0,
                hovertemplate=f"{element.name}<extra></extra>",
            ))
        return traces
    return go.Scatter3d(x=[x, x+w], y=[y, y+d], z=[z, z+h], mode="lines", name=element.name)


def _furniture_trace(item, floor_height=FLOOR_HEIGHT):
    z0 = (item.floor - 1) * floor_height
    x, y, w, d, h = item.x, item.y, item.width, item.depth, item.height
    vx = [x,x+w,x+w,x,x,x+w,x+w,x]
    vy = [y,y,y+d,y+d,y,y,y+d,y+d]
    vz = [z0,z0,z0,z0,z0+h,z0+h,z0+h,z0+h]
    i = [0,0,0,4,4,4,0,1,2,3]
    j = [1,2,4,5,6,7,1,5,6,7]
    k = [2,3,5,6,7,4,5,6,7,4]
    return go.Mesh3d(x=vx, y=vy, z=vz, i=i, j=j, k=k, opacity=0.9, name=item.name, hovertemplate=f"{item.name}<br>{item.room}<br>{item.width:.2f} x {item.depth:.2f} m<extra></extra>", showlegend=False)


def _architectural_model(project, selected_floor=None, show_walls=True, show_slabs=True, show_openings=True, show_structure=True, show_stairs=True, show_furniture=True):
    fig = go.Figure()
    elements = building_elements(project, selected_floor)
    enabled = {"wall": show_walls, "slab": show_slabs, "door": show_openings, "window": show_openings, "column": show_structure, "stair": show_stairs}
    for element in elements:
        if not enabled.get(element.kind, True):
            continue
        traces = _element_trace(element)
        if isinstance(traces, list):
            for trace in traces:
                fig.add_trace(trace)
        else:
            fig.add_trace(traces)
    if show_furniture:
        for item in furniture_elements(project, selected_floor):
            fig.add_trace(_furniture_trace(item))
    fig.update_layout(height=720, scene=dict(xaxis_title="X (m)", yaxis_title="Y (m)", zaxis_title="Z (m)", aspectmode="data"), margin=dict(l=0,r=0,t=20,b=0), legend=dict(orientation="h"))
    return fig


def _dimension_overlay(project, floor):
    chains = dimension_chains(project, floor)
    fig = go.Figure()
    for item in chains["horizontal"]:
        y = -0.6
        fig.add_trace(go.Scatter(x=[item["from"], item["to"]], y=[y, y], mode="lines+text", text=["", f"{item['dimension_m']:.2f} m"], textposition="top center", showlegend=False))
    for item in chains["vertical"]:
        x = max(0.0, dimension_summary(project, floor)["overall_width_m"] + 0.6)
        fig.add_trace(go.Scatter(x=[x, x], y=[item["from"], item["to"]], mode="lines+text", text=["", f"{item['dimension_m']:.2f} m"], textposition="middle right", showlegend=False))
    return fig


def _elevation(project, title, depth=False):
    s = model_summary(project)
    span = s["floor_depth_m"] if depth else s["floor_width_m"]
    height = project.floors * FLOOR_HEIGHT
    fig = go.Figure()
    fig.add_shape(type="rect", x0=0, y0=0, x1=span, y1=height, line=dict(width=2))
    for floor in range(1, project.floors):
        fig.add_shape(type="line", x0=0, y0=floor*FLOOR_HEIGHT, x1=span, y1=floor*FLOOR_HEIGHT, line=dict(width=1))
    fig.add_annotation(x=span/2, y=height+0.5, text=title, showarrow=False)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    fig.update_layout(height=550, xaxis_title="m", yaxis_title="Height (m)")
    return fig


def render(project):
    st.subheader("Architectural Viewers")
    st.caption("Interactive conceptual visualization of the current architectural model.")
    view = st.selectbox("View", VIEW_MODES, index=min(2, len(VIEW_MODES)-1))
    if view == "Dashboard":
        st.info("Use the Dashboard workspace for project metrics and scoring.")
    elif view == "3D Model":
        floor_options = ["All floors"] + list(range(1, max(1, int(project.floors)) + 1))
        floor = st.selectbox("Building level", floor_options)
        selected_floor = None if floor == "All floors" else int(floor)
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        show_walls = c1.checkbox("Walls", True)
        show_slabs = c2.checkbox("Slabs", True)
        show_openings = c3.checkbox("Doors and windows", True)
        show_structure = c4.checkbox("Structure", True)
        show_stairs = c5.checkbox("Stairs", True)
        show_furniture = c6.checkbox("Furniture", True)
        st.plotly_chart(_architectural_model(project, selected_floor, show_walls, show_slabs, show_openings, show_structure, show_stairs, show_furniture), use_container_width=True)
        st.subheader("Model elements")
        st.dataframe([element_summary(project)], use_container_width=True, hide_index=True)
    elif view == "Floor Plan":
        floor = st.slider("Floor", 1, max(1, project.floors), 1)
        c1, c2, c3, c4 = st.columns(4)
        labels = c1.checkbox("Room labels", True)
        grid = c2.checkbox("Reference grid", True)
        dimensions = c3.checkbox("Dimensions", True)
        structural_grid = c4.checkbox("Structural grid", True)
        fig, rooms = _floor_plan(project, floor, labels, grid, dimensions, structural_grid)
        st.plotly_chart(fig, use_container_width=True)
        st.subheader("Dimension schedule")
        st.dataframe(dimension_summary(project, floor), use_container_width=True, hide_index=True)
        st.dataframe(room_dimensions(project, floor), use_container_width=True, hide_index=True)
        st.subheader("Structural grid schedule")
        st.dataframe(grid_schedule(project), use_container_width=True, hide_index=True)
        st.subheader("Room inspection")
        if rooms:
            names = [f"{r['name']} | {r['area']:.1f} m²" for r in rooms]
            selected = st.selectbox("Select room", names)
            room = rooms[names.index(selected)]
            st.dataframe([room], use_container_width=True, hide_index=True)
        else:
            st.info("No spaces are assigned to this floor.")
    elif view == "Site Plan":
        fig, _ = _floor_plan(project, 1, True, True, True, True)
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
