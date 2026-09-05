import pandas as pd
import streamlit as st
from engine.adjacency import adjacency_matrix


def render(project):
    st.subheader("Adjacency Planning")
    names, matrix = adjacency_matrix(project)
    st.dataframe(pd.DataFrame(matrix, index=names, columns=names), use_container_width=True)
    st.caption("1 = preferred adjacency in the current baseline rules; 0 = no preferred relationship recorded.")
