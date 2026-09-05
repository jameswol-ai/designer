import plotly.graph_objects as go
import streamlit as st

from engine.layout import generate_layout
from engine.planning_constraints import classify_zone, constraint_report
from engine.space_planning import generate_alternatives, planning_summary


def _draw_layout(layout):
    fig = go.Figure()
    for r in layout:
        fig.add_shape(
            type="rect",
            x0=r["x"],
            y0=r["y"],
            x1=r["x"] + r["width"],
            y1=r["y"] + r["depth"],
            line=dict(width=2),
        )
        fig.add_annotation(
            x=r["x"] + r["width"] / 2,
            y=r["y"] + r["depth"] / 2,
            text=f"{r['name']}<br>{r['area']:.1f} m²",
            showarrow=False,
        )
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    fig.update_layout(height=650, xaxis_title="m", yaxis_title="m", margin=dict(l=20, r=20, t=20, b=20))
    return fig


def _zone_rows(layout):
    return [
        {"floor": item["floor"], "space": item["name"], "category": item["category"], "zone": classify_zone(item)}
        for item in layout
    ]


def render(project):
    st.subheader("Space Planner")
    st.caption("Generate, compare and select conceptual planning alternatives before building generation.")

    max_columns = st.slider("Maximum planning columns", 1, 6, 4)
    summary = planning_summary(project, max_columns=max_columns)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Alternatives", summary["alternatives"])
    c2.metric("Recommended", summary["recommended"] or "None")
    c3.metric("Planning score", f"{summary['score']:.1f}")
    c4.metric("Overlaps", summary["overlaps"])

    alternatives = generate_alternatives(project, max_columns=max_columns)
    if not alternatives:
        st.info("Add spaces to the project program before generating alternatives.")
        return

    rows = [a.as_dict() for a in alternatives]
    st.subheader("Alternative comparison")
    st.dataframe(rows, use_container_width=True, hide_index=True)

    labels = [a.name for a in alternatives]
    default_index = 0
    if summary.get("recommended") in labels:
        default_index = labels.index(summary["recommended"])
    selected = st.selectbox("Alternative", labels, index=default_index, key="selected_planning_alternative")
    alternative = alternatives[labels.index(selected)]

    st.session_state["selected_planning_layout"] = alternative.layout
    st.session_state["selected_planning_alternative"] = alternative.name
    st.session_state["selected_planning_columns"] = alternative.columns

    report = constraint_report(project, alternative.layout)

    st.subheader(f"{alternative.name} plan")
    st.plotly_chart(_draw_layout(alternative.layout), use_container_width=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Adjacency proximity", f"{report['adjacency_proximity']:.1f}")
    c2.metric("Zoning coherence", f"{report['zoning']:.1f}")
    c3.metric("Grid alignment", f"{report['grid_alignment']:.1f}")
    c4.metric("Overlaps", report["overlaps"])

    st.subheader("Planning criteria")
    criteria = {
        "Compactness": alternative.compactness,
        "Circulation": alternative.circulation,
        "Furniture fit": alternative.furniture,
        "Adjacency": alternative.adjacency,
        "Zoning": alternative.zoning,
        "Grid alignment": alternative.grid_alignment,
        "Compliance": alternative.compliance,
    }
    st.bar_chart(criteria)

    st.subheader("Program zoning")
    st.dataframe(_zone_rows(alternative.layout), use_container_width=True, hide_index=True)

    st.success("Selected alternative is now the active conceptual layout for the building model and Viewer.")

    with st.expander("Constraint diagnostics"):
        st.json(report)

    with st.expander("Manual layout control"):
        columns = st.slider("Layout columns", 1, 6, alternative.columns, key="manual_layout_columns")
        manual_layout = generate_layout(project, columns=columns)
        st.plotly_chart(_draw_layout(manual_layout), use_container_width=True)
        st.json(constraint_report(project, manual_layout))
