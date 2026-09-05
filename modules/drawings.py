import json

import pandas as pd
import streamlit as st

from engine.drawings import drawing_sheet, elevation_data, floor_plan_data, section_data
from engine.drawing_graphics import drawing_graphics
from engine.drawing_renderer import render_graphics
from engine.drawing_sheet import drawing_register
from engine.building_generator import generate_building


def _layer_names(graphics):
    return sorted({item.get("layer", "annotation") for item in graphics.get("graphics", [])})


def render(project):
    st.subheader("Architectural Drawings")
    st.caption("Interactive conceptual drawings generated from the canonical building model.")
    layout = st.session_state.get("selected_planning_layout")
    floors = max(1, int(project.floors))
    drawing_type = st.selectbox("Drawing", ["Floor Plan", "Elevation", "Section", "Drawing Sheet", "Drawing Register"])

    if drawing_type == "Floor Plan":
        floor = st.number_input("Floor", min_value=1, max_value=floors, value=1, step=1)
        graphics = drawing_graphics(project, "floor_plan", int(floor), layout=layout)
        layers = _layer_names(graphics)
        selected = st.multiselect("Layers", layers, default=layers)
        fig = render_graphics(graphics, layers=selected, title=f"Level {int(floor)} Floor Plan")
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True, "displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]})
        data = floor_plan_data(project, int(floor), layout=layout)
        rooms = pd.DataFrame(data["rooms"])
        if not rooms.empty:
            st.dataframe(rooms[[c for c in ["id", "name", "category", "floor", "x", "y", "width", "depth", "area"] if c in rooms.columns]], use_container_width=True, hide_index=True)
        with st.expander("Drawing data"):
            st.json(graphics)
        st.download_button("Export floor plan JSON", json.dumps(data, indent=2), file_name=f"A1{int(floor):02d}_floor_plan.json", mime="application/json")

    elif drawing_type == "Elevation":
        side = st.selectbox("Elevation", ["front", "rear", "left", "right"])
        data = elevation_data(project, side, layout=layout)
        graphics = drawing_graphics(project, "elevation", 1, layout=layout)
        layers = _layer_names(graphics)
        selected = st.multiselect("Layers", layers, default=layers, key="elevation_layers")
        st.plotly_chart(render_graphics(graphics, layers=selected, title=f"{side.title()} Elevation"), use_container_width=True, config={"scrollZoom": True, "displaylogo": False})
        st.metric("Overall height", f"{data['height_m']:.2f} m")
        st.metric("Elevation width", f"{data['width_m']:.2f} m")
        st.dataframe(pd.DataFrame({"Level": range(len(data["levels"])), "Height (m)": data["levels"]}), use_container_width=True, hide_index=True)
        st.download_button("Export elevation JSON", json.dumps(data, indent=2), file_name=f"A2_{side}_elevation.json", mime="application/json")

    elif drawing_type == "Section":
        axis = st.selectbox("Section axis", ["x", "y"])
        data = section_data(project, axis, layout=layout)
        graphics = drawing_graphics(project, "section", 1, layout=layout)
        layers = _layer_names(graphics)
        selected = st.multiselect("Layers", layers, default=layers, key="section_layers")
        st.plotly_chart(render_graphics(graphics, layers=selected, title=f"Section {axis.upper()}"), use_container_width=True, config={"scrollZoom": True, "displaylogo": False})
        st.metric("Section height", f"{data['height_m']:.2f} m")
        st.metric("Section span", f"{data['width_m']:.2f} m")
        st.dataframe(pd.DataFrame({"Level": range(len(data["floor_levels"])), "Height (m)": data["floor_levels"]}), use_container_width=True, hide_index=True)
        st.download_button("Export section JSON", json.dumps(data, indent=2), file_name=f"A3_section_{axis}.json", mime="application/json")

    elif drawing_type == "Drawing Sheet":
        floor = st.number_input("Sheet floor", min_value=1, max_value=floors, value=1, step=1, key="sheet_floor")
        sheet = drawing_sheet(project, floor=int(floor), layout=layout)
        graphics = {"graphics": sheet["graphics"]}
        st.plotly_chart(render_graphics(graphics, title=f"{sheet['drawing_number']} | {sheet['title']}"), use_container_width=True, config={"scrollZoom": True, "displaylogo": False})
        st.write(f"**{sheet['drawing_number']} | {sheet['title']}**")
        st.dataframe(pd.DataFrame([sheet["title_block"]]), use_container_width=True, hide_index=True)
        st.download_button("Export drawing sheet JSON", json.dumps(sheet, indent=2), file_name=f"{sheet['drawing_number']}.json", mime="application/json")

    else:
        register = drawing_register(project, layout=layout)
        st.dataframe(pd.DataFrame(register), use_container_width=True, hide_index=True)
        st.download_button("Export drawing register JSON", json.dumps(register, indent=2), file_name="A000_drawing_register.json", mime="application/json")
        model = generate_building(project, layout=layout)
        st.caption(f"Canonical model: {len(model.rooms)} rooms, {len(model.elements)} building elements.")
