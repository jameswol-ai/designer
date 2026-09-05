import pandas as pd
import streamlit as st

from engine.validation import check_project, score_project


def render(project):
    st.subheader("Design Compliance")
    st.caption("Transparent rule checks against the active Designer baseline and any licensed project standards.")
    session_rows = st.session_state.get("metric_handbook_standards", [])
    scores = score_project(project, session_rows=session_rows)
    checks = check_project(project, session_rows=session_rows)
    a, b, c = st.columns(3)
    a.metric("Metric compliance", f"{scores['Metric compliance']:.1f}%")
    b.metric("Overall design score", f"{scores['Overall']:.1f}/100")
    c.metric("Spaces checked", len(checks))

    df = pd.DataFrame(checks)
    if not df.empty:
        display = df.rename(columns={
            "name": "Space", "category": "Category", "area": "Area (m²)",
            "required_area": "Required area (m²)", "required_width": "Required width (m)",
            "required_depth": "Required depth (m)", "status": "Status", "source": "Source",
        })
        st.dataframe(display, use_container_width=True, hide_index=True)
        review = display[display["Status"] != "Compliant"]
        if not review.empty:
            st.warning(f"{len(review)} programmed space(s) require design review.")
        else:
            st.success("All programmed spaces pass the active dimensional baseline.")
    else:
        st.info("No programmed spaces are available for compliance checking.")
