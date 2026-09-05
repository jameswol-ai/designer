import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from engine import build_project, score_project
from modules import dashboard, project_brief, site_context, space_program, metric_handbook, space_planner, adjacency, floor_plan, compliance

st.set_page_config(page_title="Designer | Architectural Design Studio", page_icon="🏛️", layout="wide")

TABS = {
    "Dashboard": dashboard,
    "Project Brief": project_brief,
    "Site & Context": site_context,
    "Space Program": space_program,
    "Metric Standards": metric_handbook,
    "Space Planner": space_planner,
    "Floor Plan": floor_plan,
    "Adjacency": adjacency,
    "Compliance": compliance,
}

if "project" not in st.session_state:
    st.session_state.project = build_project("My Architectural Project", "Residential", 1000.0, 1, "Medium")
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Dashboard"

project = st.session_state.project

with st.sidebar:
    st.markdown("# 🏛️ Designer")
    st.caption("Architectural Design Studio")
    st.divider()
    active = st.radio("Design workspace", list(TABS), index=list(TABS).index(st.session_state.active_tab))
    st.session_state.active_tab = active
    st.divider()
    st.subheader("Project Controls")
    scale = st.selectbox("Program scale", ["Small", "Medium", "Large"], index=1)
    if st.button("Generate / Reset Program", type="primary", use_container_width=True):
        st.session_state.project = build_project(project.name, project.typology, project.site_area, project.floors, scale)
        st.session_state.project.location = project.location
        st.session_state.project.climate = project.climate
        st.rerun()
    st.divider()
    st.info("Metric values included in this prototype are illustrative baseline data. Licensed handbook-derived rules can be added to the metric data layer.")

st.title("🏛️ Designer")
st.caption(f"Metric-based architectural planning studio • {project.name}")

scores = score_project(project)
TABS[active].render(project, scores) if active == "Dashboard" else TABS[active].render(project)

st.divider()
with st.expander("Project summary & export"):
    c1, c2, c3 = st.columns(3)
    c1.metric("Programmed area", f"{project.programmed_area:,.1f} m²")
    c2.metric("Overall score", f"{scores['Overall']:.1f}/100")
    c3.metric("Metric compliance", f"{scores['Metric compliance']:.1f}%")
    st.download_button("Export project JSON", data=json.dumps(project.to_dict(), indent=2), file_name="designer_project.json", mime="application/json")
