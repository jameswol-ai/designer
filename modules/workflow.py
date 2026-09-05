from __future__ import annotations

import streamlit as st


def render(project, active_section: str, active_tab: str, navigation: dict) -> None:
    st.subheader("Design Workflow")
    st.caption("Move through the architectural workflow while keeping the current project model active.")

    stages = list(navigation)
    current_index = stages.index(active_section) if active_section in stages else 0

    cols = st.columns(len(stages))
    for index, stage in enumerate(stages):
        with cols[index]:
            status = "Current" if index == current_index else ("Complete" if index < current_index else "Next")
            st.markdown(f"**{index + 1}. {stage}**")
            st.caption(status)
            if st.button("Open", key=f"workflow_stage_{index}", use_container_width=True, disabled=index == current_index):
                first_tab = next(iter(navigation[stage]))
                st.session_state.active_tab = first_tab
                st.rerun()

    st.divider()
    st.markdown(f"**Current workspace:** {active_tab}")
    st.caption("The active project, program, planning layout and model are shared across workspaces.")

    if project.location:
        st.caption(f"Site: {project.location}")
    if project.climate:
        st.caption(f"Climate: {project.climate}")
