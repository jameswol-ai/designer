import pandas as pd
import streamlit as st

from engine.design_basics import DesignBasicRule, active_rules, design_basics_report

CATEGORIES = ["Human Dimensions", "Space Requirements", "Movement", "Accessibility", "Dimensional Coordination"]


def _import_rules(uploaded):
    if uploaded is None:
        return []
    frame = pd.read_csv(uploaded)
    required = {"key", "category", "label", "value", "unit", "description"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    return [DesignBasicRule(
        key=str(row["key"]), category=str(row["category"]), label=str(row["label"]), value=float(row["value"]),
        unit=str(row["unit"]), description=str(row["description"]), source=str(row.get("source", "Licensed/user-supplied data")),
    ) for row in frame.to_dict(orient="records")]


def _rows_for_category(report, category):
    if category == "Human Dimensions": return report["human_dimensions"]
    if category == "Space Requirements": return report["space_requirements"]
    if category == "Movement": return report["movement"]
    if category == "Accessibility": return [report["accessibility"]]
    return [report["dimensional_coordination"]]


def render(project, category=None):
    st.subheader(category or "Design Basics")
    st.caption("Rule-driven architectural planning checks for human dimensions, space, movement, accessibility and dimensional coordination.")

    design_rows = st.session_state.get("design_basic_rules", [])
    metric_rows = st.session_state.get("metric_handbook_standards", [])
    report = design_basics_report(project, session_rows=metric_rows, design_rows=design_rows)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Movement score", f"{report['movement_score']:.1f}%")
    c2.metric("Spaces", len(report["space_requirements"]))
    c3.metric("Planning grid", f"{report['dimensional_coordination']['planning_grid_m']:.2f} m")
    c4.metric("Turning diameter", f"{report['accessibility']['turning_diameter_m']:.2f} m")

    selected = category or st.selectbox("Design Basics layer", CATEGORIES)
    st.dataframe(pd.DataFrame(_rows_for_category(report, selected)), use_container_width=True, hide_index=True)

    if selected == "Movement":
        st.subheader("Movement checks")
        st.write("Spaces are screened against the active conceptual movement-width rule. Project-specific circulation and code requirements remain authoritative.")
    elif selected == "Accessibility":
        st.subheader("Accessibility baseline")
        st.write("Door, turning and ramp values are planning baselines and must be verified against the governing accessibility requirements for the project jurisdiction.")
    elif selected == "Dimensional Coordination":
        st.subheader("Coordination")
        st.write("The active planning grid and dimension offsets can be used by the layout and drawing engines as coordination parameters.")

    with st.expander("Import licensed Design Basics rules"):
        uploaded = st.file_uploader("CSV rules", type=["csv"], key="design_basics_rules_upload")
        if uploaded is not None:
            try:
                imported = _import_rules(uploaded)
                st.session_state["design_basic_rules"] = [rule.to_dict() for rule in imported]
                st.success(f"Loaded {len(imported)} rules for this session.")
                st.rerun()
            except (ValueError, TypeError) as exc:
                st.error(str(exc))
        if st.button("Clear imported Design Basics rules", key="clear_design_basics_rules"):
            st.session_state.pop("design_basic_rules", None)
            st.rerun()

    with st.expander("Active rule set"):
        st.dataframe(pd.DataFrame([rule.to_dict() for rule in active_rules(design_rows)]), use_container_width=True, hide_index=True)
