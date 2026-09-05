import streamlit as st


def render(project):
    st.subheader("Site & Context")
    c1, c2 = st.columns(2)
    with c1:
        project.metadata["site_orientation"] = st.selectbox("Primary site orientation", ["North", "South", "East", "West"])
        project.metadata["site_slope"] = st.number_input("Average site slope (%)", 0.0, 100.0, float(project.metadata.get("site_slope", 0.0)), 0.5)
    with c2:
        project.metadata["road_access"] = st.selectbox("Primary access", ["North", "South", "East", "West"])
        project.metadata["noise_level"] = st.selectbox("Noise context", ["Low", "Medium", "High"])
    project.metadata["site_notes"] = st.text_area("Site notes", project.metadata.get("site_notes", ""))
