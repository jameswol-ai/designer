import json

import pandas as pd
import streamlit as st

from engine.drawings import drawing_sheet, elevation_data, floor_plan_data, section_data
from engine.building_generator import generate_building


def render(project):
    st.subheader("Architectural Drawings")
    st.caption("Conceptual drawing views generated from the canonical building model.")
    layout = st.session_state.get("selected_planning_layout")
    floors = max(1, int(project.floors))
    drawing_type = st.selectbox("Drawing", ["Floor Plan", "Elevation", "Section", "Drawing Sheet"])

    if drawing_type == "Floor Plan":
        floor = st.number_input("Floor", min_value=1, max_value=floors, value=1, step=1)
        data = floor_plan_data(project, int(floor), layout=layout)
        rooms = pd.DataFrame(data["rooms"])
        if not rooms.empty:
            st.dataframe(rooms[[c for c in ["id", "name", "category", "floor", "x", "y", "width", "depth", "area"] if c in rooms.columns]], use_container_width=True, hide_index=True)
        with st.expander("Walls, openings, structure and furniture"):
            st.json({k: data[k] for k in ["walls", "openings", "structure", "furniture"]})
        st.download_button("Export floor plan JSON", json.dumps(data, indent=2), file_name=f"A1{int(floor):02d}_floor_plan.json", mime="application/json")

    elif drawing_type == "Elevation":
        side = st.selectbox("Elevation", ["front", "rear", "left", "right"])
        data = elevation_data(project, side, layout=layout)
        st.metric("Overall height", f"{data['height_m']:.2f} m")
        st.metric("Elevation width", f"{data['width_m']:.2f} m")
        st.dataframe(pd.DataFrame({"Level": range(len(data["levels"])), "Height (m)": data["levels"]}), use_container_width=True, hide_index=True)
        st.download_button("Export elevation JSON", json.dumps(data, indent=2), file_name=f"A2_{side}_elevation.json", mime="application/json")

    elif drawing_type == "Section":
        axis = st.selectbox("Section axis", ["x", "y"])
        data = section_data(project, axis, layout=layout)
        st.metric("Section height", f"{data['height_m']:.2f} m")
        st.metric("Section span", f"{data['width_m']:.2f} m")
        st.dataframe(pd.DataFrame({"Level": range(len(data["floor_levels"])), "Height (m)": data["floor_levels"]}), use_container_width=True, hide_index=True)
        st.download_button("Export section JSON", json.dumps(data, indent=2), file_name=f"A3_section_{axis}.json", mime="application/json")

    else:
        sheet = drawing_sheet(project, floor=1, layout=layout)
        model = generate_building(project, layout=layout)
        st.write(f"**{sheet['sheet_number']} | {sheet['title']}**")
        st.metric("Rooms", len(model.rooms))
        st.metric("Building elements", len(model.elements))
        st.dataframe(pd.DataFrame([model.summary()]), use_container_width=True, hide_index=True)
        st.download_button("Export drawing sheet JSON", json.dumps(sheet, indent=2), file_name=f"{sheet['sheet_number']}.json", mime="application/json")
