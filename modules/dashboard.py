from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from engine.building_generator import generate_building
from engine.data_contract import project_document
from engine.planning_constraints import classify_zone
from engine.space_planning import generate_alternatives, planning_summary


def _program_rows(project):
    return [
        {
            "Space": s.name,
            "Category": s.category,
            "Zone": classify_zone({"category": s.category}),
            "Qty": int(s.quantity),
            "Area / unit (m²)": round(float(s.area), 2),
            "Total area (m²)": round(float(s.total_area), 2),
            "Priority": s.priority,
        }
        for s in project.spaces
    ]


def _score_rows(scores):
    return pd.DataFrame([
        {"Indicator": "Overall design score", "Score": float(scores.get("Overall", 0.0))},
        {"Indicator": "Metric compliance", "Score": float(scores.get("Metric compliance", 0.0))},
        {"Indicator": "Program/site efficiency", "Score": float(scores.get("Program/site efficiency", 0.0))},
    ])


def render(project, scores):
    st.subheader("Design Dashboard")
    st.caption("Project command center for program, planning, model, compliance and documentation status.")

    planning = planning_summary(project)
    layout = st.session_state.get("selected_planning_layout")
    model = generate_building(project, layout=layout)
    total_instances = sum(max(0, int(s.quantity)) for s in project.spaces)
    floor_area = project.programmed_area / max(1, int(project.floors))
    site_coverage = min(100.0, project.programmed_area / max(float(project.site_area), 1.0) * 100.0)
    target_gfa = float(project.target_gfa or 0.0)
    target_gap = target_gfa - float(project.programmed_area) if target_gfa else 0.0
    target_status = "On target" if target_gfa and abs(target_gap) < max(1.0, target_gfa * 0.05) else ("Below target" if target_gfa and target_gap > 0 else ("Above target" if target_gfa else "Not set"))

    st.markdown("### Project overview")
    a, b, c, d, e, f = st.columns(6)
    a.metric("Program area", f"{project.programmed_area:,.1f} m²")
    b.metric("Floor plate", f"{floor_area:,.1f} m²")
    c.metric("Floors", int(project.floors))
    d.metric("Space instances", total_instances)
    e.metric("Model elements", len(model.elements))
    f.metric("Site utilization", f"{site_coverage:.1f}%")

    st.markdown("### Design health")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Overall", f"{scores.get('Overall', 0):.1f}/100")
    c2.metric("Metric compliance", f"{scores.get('Metric compliance', 0):.1f}%")
    c3.metric("Planning score", f"{planning.get('score', 0):.1f}/100")
    c4.metric("Layout overlaps", planning.get("overlaps", 0))
    st.progress(min(100, max(0, int(scores.get("Overall", 0)))), text="Overall design health")

    if scores.get("Overall", 0) >= 85:
        st.success("Design baseline is performing strongly. Continue with detailed coordination and professional verification.")
    elif scores.get("Overall", 0) >= 65:
        st.info("Design baseline is progressing. Review the lower-scoring checks before documentation.")
    else:
        st.warning("Design baseline needs attention. Resolve program, dimensional or site-efficiency issues before advancing.")

    left, right = st.columns([1.05, 1])
    with left:
        st.markdown("### Score profile")
        score_df = _score_rows(scores)
        fig = go.Figure(go.Bar(x=score_df["Score"], y=score_df["Indicator"], orientation="h", text=[f"{v:.1f}" for v in score_df["Score"]], textposition="auto"))
        fig.update_xaxes(range=[0, 100], title="Score")
        fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="")
        st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
    with right:
        st.markdown("### Program distribution")
        categories = {}
        for space in project.spaces:
            categories[space.category] = categories.get(space.category, 0.0) + float(space.total_area)
        if categories:
            fig = go.Figure(go.Pie(labels=list(categories.keys()), values=list(categories.values()), hole=0.45))
            fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10), showlegend=True)
            st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})
        else:
            st.info("Add spaces to populate program analytics.")

    st.markdown("### Planning intelligence")
    p1, p2, p3 = st.columns(3)
    p1.metric("Recommended option", planning.get("recommended") or "None")
    p2.metric("Alternatives", planning.get("alternatives", 0))
    p3.metric("Selected layout", st.session_state.get("selected_planning_alternative", "Not selected"))
    alternatives = generate_alternatives(project)
    if alternatives:
        comparison = pd.DataFrame([a.as_dict() for a in alternatives])
        columns = [c for c in ["name", "score", "compactness", "circulation", "furniture", "adjacency", "zoning", "grid_alignment", "compliance", "overlaps"] if c in comparison.columns]
        st.dataframe(comparison[columns], use_container_width=True, hide_index=True)

    st.markdown("### Project targets")
    target_cols = st.columns(4)
    target_cols[0].metric("Target GFA", f"{target_gfa:,.1f} m²" if target_gfa else "Not set")
    target_cols[1].metric("Target gap", f"{target_gap:+,.1f} m²" if target_gfa else "Not set")
    target_cols[2].metric("Target status", target_status)
    target_cols[3].metric("Gross model area", f"{model.gross_floor_area:,.1f} m²")

    st.markdown("### Program schedule")
    rows = _program_rows(project)
    if rows:
        program_df = pd.DataFrame(rows)
        st.dataframe(program_df, use_container_width=True, hide_index=True)
        category_summary = program_df.groupby("Category", as_index=False)["Total area (m²)"].sum().sort_values("Total area (m²)", ascending=False)
        category_summary = category_summary.rename(columns={"Total area (m²)": "Area (m²)"})
        with st.expander("Area summary by category"):
            st.dataframe(category_summary, use_container_width=True, hide_index=True)
    else:
        st.info("No programmed spaces are available.")

    st.markdown("### Model status")
    model_kinds = {}
    for element in model.elements:
        model_kinds[element.kind] = model_kinds.get(element.kind, 0) + 1
    m1, m2 = st.columns([1, 1])
    with m1:
        st.dataframe(
            pd.DataFrame([{"Element type": k, "Count": v} for k, v in sorted(model_kinds.items())]),
            use_container_width=True,
            hide_index=True,
        )
    with m2:
        if layout:
            st.success("A selected planning layout is driving the canonical building model.")
            st.caption(f"Layout rooms: {len(layout)} | Model rooms: {len(model.rooms)}")
        else:
            st.info("No manually selected planning layout. The model is using the generated baseline layout.")

    st.markdown("### Project information")
    info = [
        {"Parameter": "Project", "Value": project.name},
        {"Parameter": "Typology", "Value": project.typology},
        {"Parameter": "Location", "Value": project.location or "Not defined"},
        {"Parameter": "Climate", "Value": project.climate or "Not defined"},
        {"Parameter": "Site area", "Value": f"{project.site_area:,.1f} m²"},
        {"Parameter": "Schema", "Value": project.schema_version},
    ]
    st.dataframe(pd.DataFrame(info), use_container_width=True, hide_index=True)

    with st.expander("Versioned project data document"):
        st.json(project_document(project, layout=layout))
