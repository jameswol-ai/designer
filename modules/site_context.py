import streamlit as st


def _index(options, value):
    try:
        return options.index(value)
    except ValueError:
        return 0


def render(project):
    st.subheader("Site & Context")
    st.caption("Capture the site assumptions that influence orientation, access, environmental response and later planning checks.")

    directions = ["North", "South", "East", "West"]
    noise_levels = ["Low", "Medium", "High"]

    c1, c2 = st.columns(2)
    with c1:
        project.location = st.text_input("Project location", value=project.location or "", key="site_location")
        orientation = project.metadata.get("site_orientation", "North")
        project.metadata["site_orientation"] = st.selectbox(
            "Primary site orientation", directions, index=_index(directions, orientation), key="site_orientation"
        )
        project.metadata["site_slope"] = st.number_input(
            "Average site slope (%)", min_value=0.0, max_value=100.0,
            value=float(project.metadata.get("site_slope", 0.0)), step=0.5, key="site_slope"
        )
    with c2:
        climate = project.climate or ""
        project.climate = st.text_input("Climate / environmental context", value=climate, key="site_climate")
        access = project.metadata.get("road_access", "North")
        project.metadata["road_access"] = st.selectbox(
            "Primary road access", directions, index=_index(directions, access), key="road_access"
        )
        noise = project.metadata.get("noise_level", "Medium")
        project.metadata["noise_level"] = st.selectbox(
            "Noise context", noise_levels, index=_index(noise_levels, noise), key="noise_level"
        )

    project.metadata["site_notes"] = st.text_area(
        "Site notes", value=project.metadata.get("site_notes", ""), key="site_notes"
    )

    st.subheader("Site assumptions")
    st.dataframe(
        [
            {"Parameter": "Orientation", "Value": project.metadata["site_orientation"]},
            {"Parameter": "Road access", "Value": project.metadata["road_access"]},
            {"Parameter": "Slope", "Value": f"{project.metadata['site_slope']:.1f}%"},
            {"Parameter": "Noise", "Value": project.metadata["noise_level"]},
            {"Parameter": "Climate", "Value": project.climate or "Not defined"},
            {"Parameter": "Location", "Value": project.location or "Not defined"},
        ],
        use_container_width=True,
        hide_index=True,
    )
