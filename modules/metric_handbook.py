import pandas as pd
import streamlit as st
from metric.standards import STANDARDS


def render(project=None):
    st.subheader("Metric Standards")
    st.caption("Illustrative baseline rules only. Use licensed handbook-derived data for professional project decisions.")
    df = pd.DataFrame(STANDARDS).T.reset_index(names="Category")
    st.dataframe(df, use_container_width=True, hide_index=True)
