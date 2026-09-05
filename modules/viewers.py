import plotly.graph_objects as go
import streamlit as st

from engine.viewers import VIEW_MODES
from engine.furniture import furniture_schedule
from engine.structure_grid import candidate_grids
from engine.dimensions import grid_axes, grid_schedule, dimension_summary, room_dimensions
from engine.vertical import stair_schedule
from engine.environment import environmental_checks
from engine.egress import egress_summary
from engine.site import parking_plan
from engine.building_generator import generate_building
from engine.planning_constraints import constraint_report

FLOOR_HEIGHT = 3.2


def _safe_floor_count(project):
    try:
        floors = int(project.floors)
    except (TypeError, ValueError):
        floors = 1
    return max(1, floors)


def _active_layout(project):
    layout = st.session_state.get("selected_planning_layout")
    return layout if isinstance(layout, list) and layout else None


def _floor_plan(project, floor=1, labels=True, grid=True, dimensions=True, structural_grid=True, layout=None):
    building = generate_building(project, layout=layout)
    rooms = [r for r in building.rooms if int(r.get("floor", 1)) == int(floor)]
    fig = go.Figure()
    for r in rooms:
        x0, y0 = float(r["x"]), float(r["y"])
        x1, y1 = x0 + float(r["width"]), y0 + float(r["depth"])
        fig.add_shape(type="rect", x0=x0, y0=y0, x1=x1, y1=y1, line=dict(width=2))
        if labels:
            area = float(r.get("area_m2", r.get("area", 0.0)))
            fig.add_annotation(x=(x0+x1)/2, y=(y0+y1)/2, text=f"{r['name']}<br>{area:.1f} m²", showarrow=False)
        if dimensions:
            fig.add_annotation(x=(x0+x1)/2, y=y0-0.18, text=f"{float(r['width']):.2f} m", showarrow=False, font=dict(size=10))
            fig.add_annotation(x=x1+0.18, y=(y0+y1)/2, text=f"{float(r['depth']):.2f} m", showarrow=False, font=dict(size=10), textangle=-90)

    if grid:
        max_x = max((float(r["x"]) + float(r["width"]) for r in rooms), default=20)
        max_y = max((float(r["y"]) + float(r["depth"]) for r in rooms), default=20)
        step = 5
        for v in range(0, int(max(max_x, max_y)) + step, step):
            fig.add_vline(x=v, line_width=1, opacity=0.2)
            fig.add_hline(y=v, line_width=1, opacity=0.2)

    if structural_grid:
        axes = grid_axes(project)
        for index, x in enumerate(axes.get("x", [])):
            fig.add_vline(x=x, line_width=1, opacity=0.35)
            if index < 26:
                fig.add_annotation(x=x, y=0, text=chr(65 + index), showarrow=False, yshift=-22)
        for index, y in enumerate(axes.get("y", []), start=1):
            fig.add_hline(y=y, line_width=1, opacity=0.35)
            fig.add_annotation(x=0, y=y, text=str(index), showarrow=False, xshift=-18)

    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    fig.update_layout(height=650, xaxis_title="m", yaxis_title="m", margin=dict(l=40,r=40,t=20,b=40))
    return fig, rooms


def _element_trace(element):
    x, y, z = element.x, element.y, element.z
    w, d, h = element.width, element.depth, element.height
    if element.kind in {"wall", "column", "slab", "floor_slab", "roof_slab", "furniture"}:
        x0, x1, y0, y1, z0, z1 = x, x+w, y, y+d, z, z+h
        vx = [x0,x1,x1,x0,x0,x1,x1,x0]; vy = [y0,y0,y1,y1,y0,y0,y1,y1]; vz = [z0,z0,z0,z0,z1,z1,z1,z1]
        i = [0,0,0,4,4,4,0,1,2,3]; j = [1,2,4,5,6,7,1,5,6,7]; k = [2,3,5,6,7,4,5,6,7,4]
        return go.Mesh3d(x=vx, y=vy, z=vz, i=i, j=j, k=k, opacity=0.75, name=element.name, hovertemplate=f"{element.name}<extra></extra>")
    if element.kind == "stair":
        steps = 10
        step_depth = d / steps
        return [go.Mesh3d(x=[x,x+w,x+w,x,x,x+w,x+w,x], y=[y+n*step_depth,y+n*step_depth,y+(n+1)*step_depth,y+(n+1)*step_depth,y+n*step_depth,y+n*step_depth,y+(n+1)*step_depth,y+(n+1)*step_depth], z=[z+n*h/steps]*4+[z+(n+1)*h/steps]*4, i=[0,0,0,4,4,4,0,1,2,3], j=[1,2,4,5,6,7,1,5,6,7], k=[2,3,5,6,7,4,5,6,7,4], opacity=0.8, name=element.name, showlegend=n == 0, hovertemplate=f"{element.name}<extra></extra>") for n in range(steps)]
    return go.Scatter3d(x=[x, x+w], y=[y, y+d], z=[z, z+h], mode="lines", name=element.name)


def _architectural_model(project, selected_floor=None, show_walls=True, show_slabs=True, show_openings=True, show_structure=True, show_stairs=True, show_furniture=True, layout=None):
    building = generate_building(project, layout=layout)
    fig = go.Figure()
    elements = building.elements if selected_floor is None else [e for e in building.elements if e.floor == int(selected_floor)]
    enabled = {"wall": show_walls, "column": show_structure, "slab": show_slabs, "floor_slab": show_slabs, "roof_slab": show_slabs, "door": show_openings, "window": show_openings, "stair": show_stairs, "furniture": show_furniture}
    for element in elements:
        if not enabled.get(element.kind, True):
            continue
        traces = _element_trace(element)
        for trace in traces if isinstance(traces, list) else [traces]:
            fig.add_trace(trace)
    fig.update_layout(height=720, scene=dict(xaxis_title="X (m)", yaxis_title="Y (m)", zaxis_title="Z (m)", aspectmode="data"), margin=dict(l=0,r=0,t=20,b=0), legend=dict(orientation="h"))
    return fig, building


def _building_elevation(project, layout=None, depth=False):
    building = generate_building(project, layout=layout)
    span = building.depth if depth else building.width
    height = building.floors * building.floor_height
    fig = go.Figure()
    fig.add_shape(type="rect", x0=0, y0=0, x1=span, y1=height, line=dict(width=2))
    for floor in range(1, building.floors):
        fig.add_shape(type="line", x0=0, y0=floor*building.floor_height, x1=span, y1=floor*building.floor_height, line=dict(width=1))
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    fig.update_layout(height=550, xaxis_title="m", yaxis_title="Height (m)")
    return fig


def render(project):
    st.subheader("Architectural Viewers")
    st.caption("All conceptual views consume the same canonical building model generated from the active spatial layout.")
    view = st.selectbox("View", VIEW_MODES, index=min(2, len(VIEW_MODES)-1))
    floors = _safe_floor_count(project)
    layout = _active_layout(project)
    if layout:
        st.caption(f"Active planning alternative: {st.session_state.get('selected_planning_alternative') or 'Selected layout'}")

    if view == "Dashboard":
        st.info("Use the Dashboard workspace for project metrics and scoring.")
    elif view == "3D Model":
        options = ["All floors"] + list(range(1, floors + 1))
        floor = st.selectbox("Building level", options)
        selected_floor = None if floor == "All floors" else int(floor)
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        flags = [c1.checkbox("Walls", True), c2.checkbox("Slabs", True), c3.checkbox("Doors and windows", True), c4.checkbox("Structure", True), c5.checkbox("Stairs", True), c6.checkbox("Furniture", True)]
        fig, building = _architectural_model(project, selected_floor, *flags, layout)
        st.plotly_chart(fig, use_container_width=True)
        st.subheader("Generated building")
        st.dataframe([building.summary()], use_container_width=True, hide_index=True)
        st.subheader("Planning diagnostics")
        st.json(constraint_report(project, building.rooms))
    elif view == "Floor Plan":
        floor = st.slider("Floor", min_value=1, max_value=floors, value=1, step=1, key="viewer_floor")
        c1, c2, c3, c4 = st.columns(4)
        fig, rooms = _floor_plan(project, floor, c1.checkbox("Room labels", True), c2.checkbox("Reference grid", True), c3.checkbox("Dimensions", True), c4.checkbox("Structural grid", True), layout)
        st.plotly_chart(fig, use_container_width=True)
        st.subheader("Dimension schedule")
        st.dataframe([dimension_summary(project, floor)], use_container_width=True, hide_index=True)
        st.dataframe(room_dimensions(project, floor), use_container_width=True, hide_index=True)
        st.subheader("Structural grid schedule")
        st.dataframe(grid_schedule(project), use_container_width=True, hide_index=True)
        if rooms:
            names = [f"{r['name']} | {float(r.get('area_m2', r.get('area', 0.0))):.1f} m²" for r in rooms]
            selected = st.selectbox("Select room", names)
            st.dataframe([rooms[names.index(selected)]], use_container_width=True, hide_index=True)
        else:
            st.info("No spaces are assigned to this floor.")
    elif view == "Site Plan":
        fig, _ = _floor_plan(project, 1, True, True, True, True, layout)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe([parking_plan(project)], use_container_width=True, hide_index=True)
    elif view == "Elevations":
        st.plotly_chart(_building_elevation(project, layout), use_container_width=True)
    elif view == "Sections":
        st.plotly_chart(_building_elevation(project, layout, True), use_container_width=True)
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
