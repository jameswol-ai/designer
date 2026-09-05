import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from engine import build_project, generate_layout, adjacency_matrix, check_project, score_project
from metric.standards import STANDARDS

st.set_page_config(page_title="Designer | Architectural Design Studio", page_icon="🏛️", layout="wide")

if "project" not in st.session_state:
    st.session_state.project = build_project("My Architectural Project", "Residential", 1000.0, 1, "Medium")

st.title("🏛️ Designer")
st.caption("Metric-based architectural planning studio")

with st.sidebar:
    st.header("Project")
    name = st.text_input("Project name", st.session_state.project.name)
    typology = st.selectbox("Building typology", ["Residential", "Office", "Education"])
    site_area = st.number_input("Site area (m²)", 100.0, 1_000_000.0, float(st.session_state.project.site_area), 50.0)
    floors = st.number_input("Floors", 1, 100, int(st.session_state.project.floors))
    location = st.text_input("Location", st.session_state.project.location)
    climate = st.selectbox("Climate", ["Tropical", "Arid", "Temperate", "Hot-humid"])
    scale = st.selectbox("Program scale", ["Small", "Medium", "Large"])
    if st.button("Generate / Reset Program", type="primary", use_container_width=True):
        st.session_state.project = build_project(name, typology, site_area, floors, scale)
        st.session_state.project.location = location
        st.session_state.project.climate = climate
        st.rerun()
    st.divider()
    st.info("Standards are illustrative baseline data. Add licensed handbook-derived rules to the metric data layer for professional use.")

project = st.session_state.project
project.name, project.typology, project.site_area, project.floors = name, typology, site_area, floors
project.location, project.climate = location, climate

m1, m2, m3, m4 = st.columns(4)
m1.metric("Programmed area", f"{project.programmed_area:,.1f} m²")
m2.metric("Site area", f"{project.site_area:,.1f} m²")
m3.metric("Floors", project.floors)
m4.metric("Spaces", sum(s.quantity for s in project.spaces))

scores = score_project(project)
left, right = st.columns([1, 2])
with left:
    st.subheader("Design score")
    st.metric("Overall", f"{scores['Overall']:.1f}/100")
    st.progress(int(scores["Overall"]))
    st.metric("Metric compliance", f"{scores['Metric compliance']:.1f}%")
    st.metric("Program/site efficiency", f"{scores['Program/site efficiency']:.1f}%")
with right:
    st.subheader("Area distribution")
    df = pd.DataFrame([{"Space": s.name, "Category": s.category, "Qty": s.quantity, "Area / unit (m²)": s.area, "Total (m²)": s.total_area} for s in project.spaces])
    st.dataframe(df, use_container_width=True, hide_index=True)
    fig = go.Figure(go.Bar(x=df["Space"], y=df["Total (m²)"], text=df["Total (m²)"], textposition="auto"))
    fig.update_layout(height=300, margin=dict(l=10, r=10, t=20, b=10), yaxis_title="m²")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Preliminary floor plan")
layout = generate_layout(project)
fig = go.Figure()
for r in layout:
    fig.add_shape(type="rect", x0=r["x"], y0=r["y"], x1=r["x"]+r["width"], y1=r["y"]+r["depth"], line=dict(width=2))
    fig.add_annotation(x=r["x"]+r["width"]/2, y=r["y"]+r["depth"]/2, text=f"{r['name']}<br>{r['area']:.1f} m²", showarrow=False)
fig.update_yaxes(scaleanchor="x", scaleratio=1)
fig.update_layout(height=650, xaxis_title="m", yaxis_title="m", margin=dict(l=20,r=20,t=20,b=20))
st.plotly_chart(fig, use_container_width=True)

st.subheader("Metric compliance")
checks = pd.DataFrame(check_project(project))
st.dataframe(checks, use_container_width=True, hide_index=True)

with st.expander("Adjacency matrix"):
    names, matrix = adjacency_matrix(project)
    st.dataframe(pd.DataFrame(matrix, index=names, columns=names), use_container_width=True)

with st.expander("Standards database"):
    standards_df = pd.DataFrame(STANDARDS).T.reset_index(names="Category")
    st.dataframe(standards_df, use_container_width=True, hide_index=True)

st.download_button("Export project JSON", data=pd.Series(project.to_dict()).to_json(indent=2), file_name="designer_project.json", mime="application/json")
