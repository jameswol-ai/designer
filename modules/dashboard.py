import streamlit as st
import pandas as pd


def render(project, scores):
    st.subheader("Design Dashboard")
    a, b, c, d = st.columns(4)
    a.metric("Programmed area", f"{project.programmed_area:,.1f} m²")
    b.metric("Site area", f"{project.site_area:,.1f} m²")
    c.metric("Floors", project.floors)
    d.metric("Spaces", sum(s.quantity for s in project.spaces))

    left, right = st.columns([1, 2])
    with left:
        st.metric("Overall score", f"{scores['Overall']:.1f}/100")
        st.progress(min(100, max(0, int(scores['Overall']))))
        st.metric("Metric compliance", f"{scores['Metric compliance']:.1f}%")
        st.metric("Program/site efficiency", f"{scores['Program/site efficiency']:.1f}%")
    with right:
        rows = [{"Space": s.name, "Category": s.category, "Qty": s.quantity, "Total area (m²)": s.total_area} for s in project.spaces]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
