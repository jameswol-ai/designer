import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from engine.data_contract import project_document
from engine.space_planning import planning_summary


def render(project, scores):
    st.subheader("Design Dashboard")
    st.caption("Live project intelligence across program, planning, compliance and building data.")

    total_instances = sum(max(1, int(s.quantity)) for s in project.spaces)
    floor_area = project.programmed_area / max(1, int(project.floors))
    target_gap = max(0.0, float(project.target_gfa) - project.programmed_area) if project.target_gfa else 0.0
    planning = planning_summary(project)

    a, b, c, d, e = st.columns(5)
    a.metric("Program area", f"{project.programmed_area:,.1f} m²")
    b.metric("Floor plate", f"{floor_area:,.1f} m²")
    c.metric("Floors", project.floors)
    d.metric("Space instances", total_instances)
    e.metric("Target gap", f"{target_gap:,.1f} m²")

    left, right = st.columns([1, 1])
    with left:
        st.metric("Overall score", f"{scores['Overall']:.1f}/100")
        st.progress(min(100, max(0, int(scores["Overall"]))))
        st.metric("Metric compliance", f"{scores['Metric compliance']:.1f}%")
        st.metric("Program/site efficiency", f"{scores['Program/site efficiency']:.1f}%")
        st.metric("Best planning option", planning.get("recommended") or "None")
    with right:
        categories = {}
        for space in project.spaces:
            categories[space.category] = categories.get(space.category, 0.0) + space.total_area
        if categories:
            fig = go.Figure(go.Bar(x=list(categories.values()), y=list(categories.keys()), orientation="h"))
            fig.update_layout(height=330, xaxis_title="Area (m²)", yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Add spaces to populate program analytics.")

    rows = [
        {"id": s.id, "Space": s.name, "Category": s.category, "Qty": s.quantity,
         "Area / unit (m²)": round(s.area, 2), "Total area (m²)": round(s.total_area, 2),
         "Priority": s.priority}
        for s in project.spaces
    ]
    st.subheader("Program data")
    st.dataframe(pd.DataFrame(rows).drop(columns=["id"], errors="ignore"), use_container_width=True, hide_index=True)

    with st.expander("Modern project data document"):
        st.json(project_document(project))
