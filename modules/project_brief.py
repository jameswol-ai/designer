import streamlit as st


def render(project):
    st.subheader("Project Brief")
    st.write("Define the architectural intent, typology, site and environmental assumptions.")
    c1, c2 = st.columns(2)
    with c1:
        project.name = st.text_input("Project name", project.name)
        project.typology = st.selectbox("Building typology", ["Residential", "Office", "Education"], index=["Residential", "Office", "Education"].index(project.typology) if project.typology in ["Residential", "Office", "Education"] else 0)
        project.location = st.text_input("Location", project.location)
    with c2:
        project.site_area = st.number_input("Site area (m²)", min_value=100.0, value=float(project.site_area), step=50.0)
        project.floors = st.number_input("Number of floors", min_value=1, max_value=100, value=int(project.floors), step=1)
        project.climate = st.selectbox("Climate", ["Tropical", "Arid", "Temperate", "Hot-humid"], index=["Tropical", "Arid", "Temperate", "Hot-humid"].index(project.climate) if project.climate in ["Tropical", "Arid", "Temperate", "Hot-humid"] else 0)
