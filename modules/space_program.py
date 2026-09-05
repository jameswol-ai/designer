import pandas as pd
import streamlit as st

from metric.standards import standard_for

PRIORITIES = ["low", "normal", "high", "critical"]


def render(project):
    st.subheader("Space Program")
    st.caption("Structured program data with live dimensional requirements and compliance status.")
    session_rows = st.session_state.get("metric_handbook_standards", [])

    rows = []
    for index, space in enumerate(project.spaces):
        rule = standard_for(space, session_rows=session_rows)
        rows.append({
            "id": space.id, "space": space.name, "category": space.category, "quantity": space.quantity,
            "area_m2": round(space.area, 2), "total_area_m2": round(space.total_area, 2),
            "required_area_m2": round(rule["min_area"], 2), "width_m": round(space.min_width, 2),
            "required_width_m": round(rule["min_width"], 2), "depth_m": round(space.min_depth, 2),
            "required_depth_m": round(rule["min_depth"], 2), "priority": space.priority,
            "status": "Compliant" if space.area >= rule["min_area"] and space.min_width >= rule["min_width"] and space.min_depth >= rule["min_depth"] else "Review",
            "source": rule.get("source", "Designer baseline"),
        })
    df = pd.DataFrame(rows)
    if df.empty:
        st.info("No spaces are currently in the project program.")
        return

    a, b, c, d = st.columns(4)
    a.metric("Space types", len(df))
    b.metric("Instances", int(df["quantity"].sum()))
    c.metric("Program area", f"{df['total_area_m2'].sum():,.1f} m²")
    d.metric("Items needing review", int((df["status"] != "Compliant").sum()))
    st.dataframe(df.drop(columns=["id"]), use_container_width=True, hide_index=True)

    options = list(range(len(project.spaces)))
    idx = st.selectbox("Space to edit", options, format_func=lambda i: project.spaces[i].name)
    space = project.spaces[idx]
    rule = standard_for(space, session_rows=session_rows)

    c1, c2, c3, c4 = st.columns(4)
    space.quantity = int(c1.number_input("Quantity", 1, 1000, int(space.quantity), key=f"qty_{space.id}"))
    space.area = float(c2.number_input("Area / unit (m²)", 0.1, 100000.0, float(space.area), 0.5, key=f"area_{space.id}"))
    space.min_width = float(c3.number_input("Minimum width (m)", 0.1, 100.0, float(space.min_width), 0.1, key=f"width_{space.id}"))
    space.min_depth = float(c4.number_input("Minimum depth (m)", 0.1, 100.0, float(space.min_depth), 0.1, key=f"depth_{space.id}"))
    space.priority = st.selectbox("Priority", PRIORITIES, index=PRIORITIES.index(space.priority) if space.priority in PRIORITIES else 1, key=f"priority_{space.id}")

    st.write("Active requirement")
    st.dataframe([{
        "required_area_m2": rule["min_area"], "required_width_m": rule["min_width"],
        "required_depth_m": rule["min_depth"], "source": rule.get("source", "Designer baseline"),
        "notes": rule.get("notes", ""),
    }], use_container_width=True, hide_index=True)
