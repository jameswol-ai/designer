import json
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
)

st.set_page_config(page_title="Designer | Architectural Design Studio", page_icon="D", layout="wide")

NAVIGATION = {
    "Project": {
        "Dashboard": dashboard,
        "Project Brief": project_brief,
        "Site & Context": site_context,
    },
    "Planning": {
        "Space Program": space_program,
        "Metric Standards": metric_handbook,
        "Space Planner": space_planner,
        "Adjacency": adjacency,
    },
    "Design & Views": {
        "Viewers": viewers,
        "Floor Plan": floor_plan,
    },
    "Review": {
        "Compliance": compliance,
    },
}

WORKSPACES = {
    workspace: list(items.keys()) for workspace, items in NAVIGATION.items()
}
FLAT_TABS = [tab for tabs in NAVIGATION.values() for tab in tabs]

if "project" not in st.session_state:
    st.session_state.project = build_project(
        "My Architectural Project", "Residential", 1000.0, 1, "Medium"
    )

if "active_tab" not in st.session_state or st.session_state.active_tab not in FLAT_TABS:
    st.session_state.active_tab = "Dashboard"

active_tab = st.session_state.active_tab
active_section = next(
    section for section, tabs in NAVIGATION.items() if active_tab in tabs
)

project = st.session_state.project

with st.sidebar:
    st.markdown("# Designer")
    st.caption("Architectural Design Studio")
    st.divider()

    section_names = list(NAVIGATION)
    section_index = section_names.index(active_section)
    selected_section = st.selectbox(
        "Design stage",
        section_names,
        index=section_index,
        key="navigation_section",
    )

    section_tabs = list(NAVIGATION[selected_section])
    tab_index = section_tabs.index(active_tab) if active_section == selected_section else 0
    selected_tab = st.selectbox(
        "Workspace",
        section_tabs,
        index=tab_index,
        key="navigation_workspace",
    )

    if selected_tab != st.session_state.active_tab:
        st.session_state.active_tab = selected_tab
        st.rerun()

    st.divider()
    st.subheader("Project Controls")
    scale = st.selectbox("Program scale", ["Small", "Medium", "Large"], index=1)

    if st.button("Generate / Reset Program", type="primary", use_container_width=True):
        st.session_state.project = build_project(
            project.name,
            project.typology,
            project.site_area,
            project.floors,
            scale,
        )
        st.session_state.project.location = project.location
        st.session_state.project.climate = project.climate
        st.rerun()

    st.divider()
    st.info(
        "Metric values included in this prototype are illustrative baseline data. "
        "Licensed handbook-derived rules can be added to the metric data layer."
    )

st.title("Designer")
st.caption(f"Metric-based architectural planning studio | {project.name}")

scores = score_project(project)
current_module = next(
    NAVIGATION[section][st.session_state.active_tab]
    for section in NAVIGATION
    if st.session_state.active_tab in NAVIGATION[section]
)

if st.session_state.active_tab == "Dashboard":
    current_module.render(project, scores)
else:
    current_module.render(project)

st.divider()
with st.expander("Project summary and export"):
    c1, c2, c3 = st.columns(3)
    c1.metric("Programmed area", f"{project.programmed_area:,.1f} m²")
    c2.metric("Overall score", f"{scores['Overall']:.1f}/100")
    c3.metric("Metric compliance", f"{scores['Metric compliance']:.1f}%")
    st.download_button(
        "Export project JSON",
        data=json.dumps(project.to_dict(), indent=2),
        file_name="designer_project.json",
        mime="application/json",
    )
