import json
from functools import partial

import streamlit as st

from engine import build_project, project_document, score_project
from modules import dashboard, project_brief, site_context, space_program, metric_handbook, space_planner, adjacency, floor_plan, compliance, viewers, design_reference, design_basics

st.set_page_config(page_title="Designer | Architectural Design Studio", page_icon="D", layout="wide")


def reference(section, topic):
    return partial(design_reference.render, section=section, topic=topic)


def basics(topic):
    return partial(design_basics.render, category=topic)


NAVIGATION = {
    "Project": {"Dashboard": dashboard, "Project Brief": project_brief, "Site & Context": site_context},
    "Design Basics": {"Human Dimensions": basics("Human Dimensions"), "Space Requirements": basics("Space Requirements"), "Movement": basics("Movement"), "Accessibility": basics("Accessibility"), "Dimensional Coordination": basics("Dimensional Coordination")},
    "Building Types": {name: reference("Building Types", name) for name in ["Housing", "Offices", "Schools", "Universities", "Hospitals", "Hotels", "Retail", "Restaurants", "Libraries", "Industrial", "Sports", "Religious", "Civic", "Transport"]},
    "Environment": {name: reference("Environment", name) for name in ["Daylight", "Lighting", "Ventilation", "Thermal", "Acoustics", "Tropical Design"]},
    "Safety": {name: reference("Safety", name) for name in ["Fire", "Egress", "Accessibility", "Security", "Flood"]},
    "Design Engine": {"Space Program": space_program, "Adjacency": adjacency, "Planning": space_planner, "Dimensions": viewers, "Compliance": compliance, "Building Model": viewers, "Floor Plans": floor_plan, "Sections": viewers, "Elevations": viewers, "Reports": viewers, "Metric Standards": metric_handbook, "Viewers": viewers},
}

FLAT_TABS = [tab for tabs in NAVIGATION.values() for tab in tabs]
metric_rows = st.session_state.get("metric_handbook_standards", [])

if "project" not in st.session_state:
    st.session_state.project = build_project("My Architectural Project", "Residential", 1000.0, 1, "Medium")
if "active_tab" not in st.session_state or st.session_state.active_tab not in FLAT_TABS:
    st.session_state.active_tab = "Dashboard"

active_tab = st.session_state.active_tab
active_section = next(section for section, tabs in NAVIGATION.items() if active_tab in tabs)
project = st.session_state.project

with st.sidebar:
    st.markdown("# Designer")
    st.caption("Architectural Design Studio")
    st.divider()
    sections = list(NAVIGATION)
    selected_section = st.radio("Design Stage", sections, index=sections.index(active_section), label_visibility="collapsed", key="sidebar_design_stage")
    tabs = list(NAVIGATION[selected_section])
    selected_tab = st.radio("Workspace", tabs, index=tabs.index(active_tab) if selected_section == active_section else 0, label_visibility="collapsed", key="sidebar_workspace")
    if selected_tab != st.session_state.active_tab:
        st.session_state.active_tab = selected_tab
        st.rerun()
    st.divider()
    st.subheader("Project Controls")
    scale = st.selectbox("Program scale", ["Small", "Medium", "Large"], index=1)
    if st.button("Generate / Reset Program", type="primary", use_container_width=True):
        st.session_state.project = build_project(project.name, project.typology, project.site_area, project.floors, scale, session_rows=metric_rows)
        st.session_state.project.location = project.location
        st.session_state.project.climate = project.climate
        st.rerun()
    st.divider()
    st.caption(f"Data schema: {project.schema_version}")
    if metric_rows:
        st.success(f"Active licensed Metric dataset: {len(metric_rows)} records")
    else:
        st.caption("Metric values in the prototype are illustrative baseline data.")

st.title("Designer")
st.caption(f"Metric-based architectural planning studio | {project.name}")
try:
    scores = score_project(project, session_rows=metric_rows)
except TypeError as exc:
    if "session_rows" not in str(exc):
        raise
    scores = score_project(project)

current_module = next(NAVIGATION[section][st.session_state.active_tab] for section in NAVIGATION if st.session_state.active_tab in NAVIGATION[section])
if st.session_state.active_tab == "Dashboard":
    current_module.render(project, scores)
elif callable(current_module) and not hasattr(current_module, "render"):
    current_module(project)
else:
    current_module.render(project)

st.divider()
with st.expander("Project data and export"):
    document = project_document(project, layout=st.session_state.get("selected_planning_layout"))
    st.json(document)
    st.download_button("Export versioned project JSON", data=json.dumps(document, indent=2), file_name="designer_project_v2.json", mime="application/json")
