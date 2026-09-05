import plotly.graph_objects as go
import streamlit as st

from engine.layout import generate_layout
from engine.space_planning import generate_alternatives, planning_summary


def _draw_layout(layout):
    fig = go.Figure()
    for r in layout:
        fig.add_shape(type="rect", x0=r["x"], y0=r["y"], x1=r["x"] + r["width"], y1=r["y"] + r["depth"], line=dict(width=2))
        fig.add_annotation(x=r["x"] + r["width"] / 2, y=r["y"] + r["depth"] / 2, text=f"{r['name']}<br>{r['area']:.1f} m²", showarrow=False)
    fig.update_yaxes(scaleanchor="x", scaleratio=1)
    fig.update_layout(height=650, xaxis_title="m", yaxis_title="m", margin=dict(l=20, r=20, t=20, b=20))
    return fig


def render(project):
    st.subheader("Space Planner")
    st.caption("Generate and compare conceptual planning alternatives using layout, adjacency, furniture and compliance signals.")

    max_columns = st.slider("Maximum planning columns", 1, 6, 4)
    summary = planning_summary(project, max_columns=max_columns)
    c1, c2, c3 = st.columns(3)
    c1.metric("Alternatives", summary["alternatives"])
    c2.metric("Recommended", summary["recommended"] or "None")
    c3.metric("Planning score", f"{summary['score']:.1f}")

    alternatives = generate_alternatives(project, max_columns=max_columns)
    if not alternatives:
        st.info("Add spaces to the project program before generating alternatives.")
        return

    rows = [a.as_dict() for a in alternatives]
    st.subheader("Alternative comparison")
    st.dataframe(rows, use_container_width=True, hide_index=True)

    labels = [a.name for a in alternatives]
    selected = st.selectbox("Alternative", labels, index=0)
    alternative = alternatives[labels.index(selected)]
    st.subheader(f"{alternative.name} plan")
    st.plotly_chart(_draw_layout(alternative.layout), use_container_width=True)

    st.subheader("Planning criteria")
    criteria = {
        "Compactness": alternative.compactness,
        "Circulation": alternative.circulation,
        "Furniture fit": alternative.furniture,
        "Adjacency": alternative.adjacency,
        "Compliance": alternative.compliance,
    }
    st.bar_chart(criteria)

    with st.expander("Manual layout control"):
        columns = st.slider("Layout columns", 1, 6, alternative.columns, key="manual_layout_columns")
        st.plotly_chart(_draw_layout(generate_layout(project, columns=columns)), use_container_width=True)
