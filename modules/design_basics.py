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
    return [
        DesignBasicRule(
            key=str(row["key"]), category=str(row["category"]), label=str(row["label"]),
            value=float(row["value"]), unit=str(row["unit"]),
            description=str(row["description"]), source=str(row.get("source", "Licensed/user-supplied data")),
        )
        for row in frame.to_dict(orient="records")
    ]


def render(project):
    st.subheader("Design Basics")
    st.caption("Rule-driven architectural planning checks for human dimensions, space, movement, accessibility and dimensional coordination.")

    report = design_basics_report(project)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Movement score", f"{report['movement_score']:.1f}%")
    c2.metric("Spaces", len(report["space_requirements"]))
    c3.metric("Planning grid", f"{report['dimensional_coordination']['planning_grid_m']:.2f} m")
    c4.metric("Turning diameter", f"{report['accessibility']['turning_diameter_m']:.2f} m")

    category = st.selectbox("Design Basics layer", CATEGORIES)
    if category == "Human Dimensions":
        rows = report["human_dimensions"]
    elif category == "Space Requirements":
        rows = report["space_requirements"]
    elif category == "Movement":
        rows = report["movement"]
    elif category == "Accessibility":
        rows = [report["accessibility"]]
    else:
        rows = [report["dimensional_coordination"]]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with st.expander("Import licensed Design Basics rules"):
        uploaded = st.file_uploader("CSV rules", type=["csv"], key="design_basics_rules_upload")
        if uploaded is not None:
            try:
                imported = _import_rules(uploaded)
                st.session_state["design_basic_rules"] = [rule.to_dict() for rule in imported]
                st.success(f"Loaded {len(imported)} rules for this session.")
            except (ValueError, TypeError) as exc:
                st.error(str(exc))
        if st.button("Clear imported Design Basics rules"):
            st.session_state.pop("design_basic_rules", None)
            st.rerun()

    st.subheader("Active rule set")
    st.dataframe(pd.DataFrame([rule.to_dict() for rule in active_rules()]), use_container_width=True, hide_index=True)
