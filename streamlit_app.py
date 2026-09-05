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
    metric_handbook,
    project_brief,
    site_context,
    space_planner,
    space_program,
    viewers,
    workflow,
)

st.set_page_config(page_title="Designer | Architectural Design Studio", page_icon="D", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.designer-brand{font-size:2.15rem;font-weight:760;letter-spacing:-.045em;margin-bottom:0}
.designer-subtitle{color:#6b6b6b;margin-top:-.25rem;margin-bottom:1rem}
.status-card{border:1px solid rgba(49,51,63,.14);border-radius:12px;padding:.8rem 1rem;background:rgba(250,250,250,.55);min-height:72px}
.status-card .label{font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;color:#777}
.status-card .value{font-size:1rem;font-weight:650;margin-top:.15rem}
div[data-testid="stMetric"]{border:1px solid rgba(49,51,63,.12);border-radius:10px;padding:.6rem .8rem}
div[data-testid="stSidebar"] .stButton button{border-radius:8px}
</style>
""", unsafe_allow_html=True)


def reference(section, topic):
    return partial(design_reference.render, section=section, topic=topic)


def basics(topic):
    return partial(design_basics.render, category=topic)

BUILDING_TYPES=["Housing","Offices","Schools","Universities","Hospitals","Hotels","Retail","Restaurants","Libraries","Industrial","Sports","Religious","Civic","Transport"]
ENVIRONMENT=["Daylight","Lighting","Ventilation","Thermal","Acoustics","Tropical Design"]
SAFETY=["Fire","Egress","Accessibility","Security","Flood"]

NAVIGATION={
    "Project":{"Dashboard":dashboard,"Workflow":workflow,"Project Brief":project_brief,"Site & Context":site_context},
    "Design Basics":{name:basics(name) for name in ["Human Dimensions","Space Requirements","Movement","Accessibility","Dimensional Coordination"]},
    "Building Types":{name:reference("Building Types",name) for name in BUILDING_TYPES},
    "Environment":{name:reference("Environment",name) for name in ENVIRONMENT},
    "Safety":{name:reference("Safety",name) for name in SAFETY},
    "Design Engine":{
        "Space Program":space_program,"Adjacency":adjacency,"Planning":space_planner,"Dimensions":viewers,
        "Compliance":compliance,"Building Model":viewers,"Floor Plans":drawings,"Sections":drawings,
        "Elevations":drawings,"Reports":viewers,"Metric Standards":metric_handbook,"Viewers":viewers,
    },
}
STAGES=list(NAVIGATION)
FLAT_TABS=[tab for tabs in NAVIGATION.values() for tab in tabs]
metric_rows=st.session_state.get("metric_handbook_standards",[])

if "project" not in st.session_state:
    st.session_state.project=build_project("My Architectural Project","Residential",1000.0,1,"Medium",session_rows=metric_rows)
if "active_tab" not in st.session_state or st.session_state.active_tab not in FLAT_TABS:
    st.session_state.active_tab="Dashboard"
if "program_scale" not in st.session_state:
    st.session_state.program_scale="Medium"

project=st.session_state.project
active_tab=st.session_state.active_tab
active_section=next(section for section,tabs in NAVIGATION.items() if active_tab in tabs)
try:
    scores=score_project(project,session_rows=metric_rows)
except TypeError as exc:
    if "session_rows" not in str(exc): raise
    scores=score_project(project)

with st.sidebar:
    st.markdown("# Designer")
    st.caption("Architectural Design Studio")
    st.divider()
    st.subheader("Design Stage")
    selected_section=st.selectbox("Stage",STAGES,index=STAGES.index(active_section),label_visibility="collapsed")
    if selected_section!=active_section:
        st.session_state.active_tab=next(iter(NAVIGATION[selected_section]))
        st.rerun()
    tabs=list(NAVIGATION[active_section])
    selected_tab=st.selectbox("Workspace",tabs,index=tabs.index(active_tab),label_visibility="collapsed")
    if selected_tab!=active_tab:
        st.session_state.active_tab=selected_tab
        st.rerun()
    st.divider()
    st.subheader("Project Controls")
    scale=st.selectbox("Program scale",["Small","Medium","Large"],key="program_scale")
    if st.button("Generate / Reset Program",type="primary",use_container_width=True):
        old=st.session_state.project
        st.session_state.project=build_project(old.name,old.typology,old.site_area,old.floors,scale,session_rows=metric_rows)
        st.session_state.project.location=old.location
        st.session_state.project.climate=old.climate
        st.session_state.project.metadata.update(old.metadata)
        for key in ["selected_planning_layout","selected_planning_alternative","selected_planning_columns"]:
            st.session_state.pop(key,None)
        st.rerun()
    if st.button("Open Dashboard",use_container_width=True):
        st.session_state.active_tab="Dashboard"
        st.rerun()
    st.divider()
    st.subheader("Project Status")
    st.caption(project.name)
    st.caption(f"{project.typology} | {project.floors} floor(s) | {project.site_area:,.0f} m² site")
    if metric_rows: st.success(f"Metric dataset: {len(metric_rows)} records")
    else: st.info("Illustrative baseline Metric values")
    st.caption(f"Schema: {project.schema_version}")

st.markdown('<div class="designer-brand">Designer</div>',unsafe_allow_html=True)
st.markdown('<div class="designer-subtitle">Parametric architectural planning studio</div>',unsafe_allow_html=True)
metric_cols=st.columns(5)
metric_cols[0].metric("Overall",f"{scores.get('Overall',0):.1f}%")
metric_cols[1].metric("Metric compliance",f"{scores.get('Metric compliance',0):.1f}%")
metric_cols[2].metric("Programmed area",f"{project.programmed_area:,.1f} m²")
metric_cols[3].metric("Site",f"{project.site_area:,.0f} m²")
metric_cols[4].metric("Floors",str(project.floors))
stage_position=STAGES.index(active_section)+1
st.progress(stage_position/len(STAGES),text=f"Design workflow: {active_section} | Stage {stage_position} of {len(STAGES)}")
context_cols=st.columns(4)
for col,(label,value) in zip(context_cols,[("Project",project.name),("Location",project.location or "Not defined"),("Climate",project.climate or "Not defined"),("Workspace",active_tab)]):
    col.markdown(f'<div class="status-card"><div class="label">{label}</div><div class="value">{value}</div></div>',unsafe_allow_html=True)
st.divider()

if active_tab=="Dashboard":
    dashboard.render(project,scores)
elif active_tab=="Workflow":
    workflow.render(project,active_section,active_tab,NAVIGATION)
else:
    current_module=NAVIGATION[active_section][active_tab]
    try:
        if callable(current_module) and not hasattr(current_module,"render"):
            current_module(project)
        else:
            current_module.render(project)
    except Exception as exc:
        st.error(f"Unable to render the {active_tab} workspace.")
        with st.expander("Technical details"): st.exception(exc)

st.divider()
with st.expander("Project data and export"):
    document=project_document(project,layout=st.session_state.get("selected_planning_layout"))
    c1,c2=st.columns([2,1])
    with c1:
        st.caption("Versioned project document")
        st.json(document)
    with c2:
        st.download_button("Export project JSON",data=json.dumps(document,indent=2),file_name="designer_project_v2.json",mime="application/json",use_container_width=True)
        st.caption("Current project state and selected planning layout.")

st.caption("Designer | Conceptual architectural planning environment | Verify professional requirements before construction use.")
