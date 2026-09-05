import json
from functools import partial

import streamlit as st

from engine import build_project, project_document, score_project
from modules import (
    adjacency,
    compliance,
    dashboard,
    design_basics,
    design_reference,
    drawings,
    floor_plan,
    metric_handbook,
    project_brief,
    site_context,
    space_planner,
    space_program,
    viewers,
)

st.set_page_config(page_title="Designer | Architectural Design Studio", page_icon="D", layout="wide", initial_sidebar_state="expanded")

st.markdown(
    """
    <style>
    .designer-brand { font-size: 2.1rem; font-weight: 750; letter-spacing: -0.04em; margin-bottom: 0; }
    .designer-subtitle { color: #666; margin-top: -0.35rem; margin-bottom: 1rem; }
    .stage-card { border: 1px solid rgba(49,51,63,.15); border-radius: 12px; padding: .85rem 1rem; background: rgba(250,250,250,.55); }
    .stage-card strong { display:block; font-size: .92rem; }
    .stage-card span { color:#777; font-size:.78rem; }
    div[data-testid="stMetric"] { border: 1px solid rgba(49,51,63,.12); border-radius: 10px; padding: .65rem .8rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def reference(section, topic):
    return partial(design_reference.render, section=section, topic=topic)


def basics(topic):
    return partial(design_basics.render, category=topic)


NAVIGATION = {
    "Project": {"Dashboard": dashboard, "Project Brief": project_brief, "Site & Context": site_context},
    "Design Basics": {
        "Human Dimensions": basics("Human Dimensions"),
        "Space Requirements": basics("Space Requirements"),
        "Movement": basics("Movement"),
        "Accessibility": basics("Accessibility"),
        "Dimensional Coordination": basics("Dimensional Coordination"),
    },
    "Building Types": {name: reference("Building Types", name) for name in ["Housing", "Offices", "Schools", "Universities", "Hospitals", "Hotels", "Retail", "Restaurants", "Libraries", "Industrial", "Sports", "Religious", "Civic", "Transport"]},
    "Environment": {name: reference("Environment", name) for name in ["Daylight", "Lighting", "Ventilation", "Thermal", "Acoustics", "Tropical Design"]},
    "Safety": {name: reference("Safety", name) for name in ["Fire", "Egress", "Accessibility", "Security", "Flood"]},
    "Design Engine": {
        "Space Program": space_program,
        "Adjacency": adjacency,
        "Planning": space_planner,
        "Dimensions": viewers,
        "Compliance": compliance,
        "Building Model": viewers,
        "Floor Plans": drawings,
        "Sections": drawings,
        "Elevations": drawings,
        "Reports": viewers,
        "Metric Standards": metric_handbook,
        "Viewers": viewers,
    },
}

STAGES = ["Project", "Design Basics", "Building Types", "Environment", "Safety", "Design Engine"]
FLAT_TABS = [tab for tabs in NAVIGATION.values() for tab in tabs]
metric_rows = st.session_state.get("metric_handbook_standards", [])

if "project" not in st.session_state:
    st.session_state.project = build_project("My Architectural Project", "Residential", 1000.0, 1, "Medium", session_rows=metric_rows)
if "active_tab" not in st.session_state or st.session_state.active_tab not in FLAT_TABS:
    st.session_state.active_tab = "Dashboard"
if "program_scale" not in st.session_state:
    st.session_state.program_scale = "Medium"

active_tab = st.session_state.active_tab
active_section = next(section for section, tabs in NAVIGATION.items() if active_tab in tabs)
project = st.session_state.project

with st.sidebar:
    st.markdown("# Designer")
    st.caption("Architectural Design Studio")
    st.divider()

    sections = list(NAVIGATION)
    selected_section = st.radio(
        "Design Stage",
        sections,
        index=sections.index(active_section),
        label_visibility="collapsed",
        key="sidebar_design_stage",
    )
    tabs = list(NAVIGATION[selected_section])
    selected_tab = st.radio(
        "Workspace",
        tabs,
        index=tabs.index(active_tab) if selected_section == active_section else 0,
        label_visibility="collapsed",
        key="sidebar_workspace",
    )
    if selected_tab != st.session_state.active_tab:
        st.session_state.active_tab = selected_tab
        st.rerun()

    st.divider()
    st.subheader("Project Controls")
    scale = st.selectbox("Program scale", ["Small", "Medium", "Large"], key="program_scale")
    if st.button("Generate / Reset Program", type="primary", use_container_width=True):
        old = st.session_state.project
        st.session_state.project = build_project(old.name, old.typology, old.site_area, old.floors, scale, session_rows=metric_rows)
        st.session_state.project.location = old.location
        st.session_state.project.climate = old.climate
        st.session_state.pop("selected_planning_layout", None)
        st.session_state.pop("selected_planning_alternative", None)
        st.session_state.pop("selected_planning_columns", None)
        st.rerun()

    st.divider()
    st.subheader("Project Status")
    st.caption(f"{project.name}")
    st.caption(f"{project.typology} | {project.floors} floor(s) | {project.site_area:,.0f} m² site")
    if metric_rows:
        st.success(f"Metric dataset: {len(metric_rows)} records")
    else:
        st.info("Using illustrative baseline Metric values")
    st.caption(f"Schema: {project.schema_version}")

# Header
st.markdown('<div class="designer-brand">Designer</div>', unsafe_allow_html=True)
st.markdown('<div class="designer-subtitle">Parametric architectural planning studio</div>', unsafe_allow_html=True)

try:
    scores = score_project(project, session_rows=metric_rows)
except TypeError as exc:
    if "session_rows" not in str(exc):
        raise
    scores = score_project(project)

# Compact project cockpit. These values stay visible while navigating the workspaces.
metric_cols = st.columns(4)
metric_cols[0].metric("Overall", f"{scores.get('Overall', 0):.1f}%")
metric_cols[1].metric("Metric compliance", f"{scores.get('Metric compliance', 0):.1f}%")
metric_cols[2].metric("Programmed area", f"{project.programmed_area:,.1f} m²")
metric_cols[3].metric("Floors", str(project.floors))

completed = STAGES.index(active_section)
progress = completed / max(len(STAGES) - 1, 1)
st.progress(progress, text=f"Design workflow: {active_section} | {completed + 1} of {len(STAGES)}")

# Quick project context row.
context_cols = st.columns(3)
context_cols[0].markdown(f'<div class="stage-card"><strong>Project</strong><span>{project.name}</span></div>', unsafe_allow_html=True)
context_cols[1].markdown(f'<div class="stage-card"><strong>Site</strong><span>{project.location or "Location not defined"}</span></div>', unsafe_allow_html=True)
context_cols[2].markdown(f'<div class="stage-card"><strong>Climate</strong><span>{project.climate or "Climate not defined"}</span></div>', unsafe_allow_html=True)

st.divider()

current_module = next(
    NAVIGATION[section][st.session_state.active_tab]
    for section in NAVIGATION
    if st.session_state.active_tab in NAVIGATION[section]
)

if st.session_state.active_tab == "Dashboard":
    current_module.render(project, scores)
elif callable(current_module) and not hasattr(current_module, "render"):
    current_module(project)
else:
    current_module.render(project)

st.divider()
with st.expander("Project data and export"):
    document = project_document(project, layout=st.session_state.get("selected_planning_layout"))
    export_cols = st.columns([2, 1])
    with export_cols[0]:
        st.caption("Versioned project document")
        st.json(document)
    with export_cols[1]:
        st.download_button(
            "Export project JSON",
            data=json.dumps(document, indent=2),
            file_name="designer_project_v2.json",
            mime="application/json",
            use_container_width=True,
        )
        st.caption("The export contains the current project state and selected planning layout.")
