import pandas as pd
import streamlit as st
from engine.validation import check_project, score_project


def render(project):
    st.subheader("Design Compliance")
    scores = score_project(project)
    a, b = st.columns(2)
    a.metric("Metric compliance", f"{scores['Metric compliance']:.1f}%")
    b.metric("Overall design score", f"{scores['Overall']:.1f}/100")
    df = pd.DataFrame(check_project(project))
    st.dataframe(df, use_container_width=True, hide_index=True)
