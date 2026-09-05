import json
from functools import partial

import streamlit as st

from engine import build_project, score_project
from modules import (
    dashboard,
    project_brief,
    site_context,
    space_program,
    metric_handbook,
    space_planner,
    adjacency,
    floor_plan,
    compliance,
    viewers,
    design_reference,
    design_basics,
)

st.set_page_config(page_title="Designer | Architectural Design Studio", page_icon="D", layout="wide")


def reference(section, topic):
    return partial(design_reference.render, section=section, topic=topic)


def basics(topic):
    return partial(design_basics.render, category=topic)


NAVIGATION = {
    "Design Basics": {
        "Human Dimensions": basics("Human Dimensions"),
        "Space Requirements": basics("Space Requirements"),
        "Movement": basics("Movement"),
        "Accessibility": basics("Accessibility"),
        "Dimensional Coordination": basics("Dimensional Coordination"),
    },
    "Building Types": {
        "Housing": reference("Building Types", "Housing"),
        "Offices": reference("Building Types", "Offices"),
        "Schools": reference("Building Types", "Schools"),
        "Universities": reference("Building Types", "Universities"),
        "Hospitals": reference("Building Types", "Hospitals"),
        "Hotels": reference("Building Types", "Hotels"),
        "Retail": reference("Building Types", "Retail"),
        "Restaurants": reference("Building Types", "Restaurants"),
        "Libraries": reference("Building Types", "Libraries"),
        "Industrial": reference("Building Types", "Industrial"),
        "Sports": reference("Building Types", "Sports"),
        "Religious": reference("Building Types", "Religious"),
        "Civic": reference("Building Types", "Civic"),
        "Transport": reference("Building Types", "Transport"),
    },
    "Environment": {
        "Daylight": reference("Environment", "Daylight"),
        "Lighting": reference("Environment", "Lighting"),
        "Ventilation": reference("Environment", "Ventilation"),
        "Thermal": reference("Environment", "Thermal"),
        "Acoustics": reference("Environment", "Acoustics"),
        "Tropical Design": reference("Environment", "Tropical Design"),
    },
    "Safety": {
        "Fire": reference("Safety", "Fire"),
        "Egress": reference("Safety", "Egress"),
        "Accessibility": reference("Safety", "Accessibility"),
        "Security": reference("Safety", "Security"),
        "Flood": reference("Safety", "Flood"),
    },
    "Design Engine": {
        "Space Program": space_program,
        "Adjacency": adjacency,
        "Planning": space_planner,
        "Dimensions": viewers,
        "Compliance": compliance,
        "Building Model": viewers,
        "Floor Plans": floor_plan,
        "Sections": viewers,
        "Elevations": viewers,
        "Reports": viewers,
        "Metric Standards": metric_handbook,
        "Viewers": viewers,
    },
    "Project": {
        "Dashboard": dashboard,
        "Project Brief": project_brief,
        "Site & Context": site_context,
    },
}

FLAT_TABS = [tab for tabs in NAVIGATION.values() for tab in tabs]
active_metric_rows = st.session_state.get("metric_handbook_standards", [])

if "project" not in st.session_state:
    # Keep first-run project creation compatible with older deployed planner builds.
    # No imported Metric dataset can exist on the first pass unless a project already exists.
    st.session_state.project = build_project(
        "My Architectural Project", "Residential", 1000.0, 1, "Medium"
    )

if "active_tab" not in st.session_state or st.session_state.active_tab not in FLAT_TABS:
    st.session_state.active_tab = "Dashboard"

active_tab = st.session_state.active_tab
active_section = next(section for section, tabs in NAVIGATION.items() if active_tab in tabs)
project = st.session_state.project

with st.sidebar:
    st.markdown("# Designer")
    st.caption("Architectural Design Studio")
    st.divider()
    st.markdown("**Design Stage**")
    section_names = list(NAVIGATION)
    section_index = section_names.index(active_section)
    selected_section = st.radio("Design Stage", section_names, index=section_index, label_visibility="collapsed", key="sidebar_design_stage")
    st.markdown("**Workspace**")
    section_tabs = list(NAVIGATION[selected_section])
    tab_index = section_tabs.index(active_tab) if active_section == selected_section else 0
    selected_tab = st.radio("Workspace", section_tabs, index=tab_index, label_visibility="collapsed", key="sidebar_workspace")
    if selected_tab != st.session_state.active_tab:
        st.session_state.active_tab = selected_tab
        st.rerun()
    st.divider()
    st.subheader("Project Controls")
    scale = st.selectbox("Program scale", ["Small", "Medium", "Large"], index=1)
    if st.button("Generate / Reset Program", type="primary", use_container_width=True):
        st.session_state.project = build_project(project.name, project.typology, project.site_area, project.floors, scale, session_rows=st.session_state.get("metric_handbook_standards", []))
        st.session_state.project.location = project.location
        st.session_state.project.climate = project.climate
        st.rerun()
    st.divider()
    if active_metric_rows:
        st.success(f"Active licensed Metric dataset: {len(active_metric_rows)} records")
    else:
        st.caption("Metric values included in this prototype are illustrative baseline data. Licensed handbook-derived rules can be added to the metric data layer.")

st.title("Designer")
st.caption(f"Metric-based architectural planning studio | {project.name}")
scores = score_project(project, session_rows=st.session_state.get("metric_handbook_standards", []))
current_module = next(NAVIGATION[section][st.session_state.active_tab] for section in NAVIGATION if st.session_state.active_tab in NAVIGATION[section])

if st.session_state.active_tab == "Dashboard":
    current_module.render(project, scores)
elif callable(current_module) and not hasattr(current_module, "render"):
    current_module(project)
else:
    current_module.render(project)

st.divider()
with st.expander("Project summary and export"):
    c1, c2, c3 = st.columns(3)
    c1.metric("Programmed area", f"{project.programmed_area:,.1f} m²")
    c2.metric("Overall score", f"{scores['Overall']:.1f}/100")
    c3.metric("Metric compliance", f"{scores['Metric compliance']:.1f}%")
    st.download_button("Export project JSON", data=json.dumps(project.to_dict(), indent=2), file_name="designer_project.json", mime="application/json")
