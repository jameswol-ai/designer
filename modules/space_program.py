import pandas as pd
import streamlit as st


def render(project):
    st.subheader("Space Program")
    rows = []
    for i, s in enumerate(project.spaces):
        rows.append({"id": i, "Space": s.name, "Category": s.category, "Quantity": s.quantity, "Area / unit (m²)": s.area, "Total (m²)": s.total_area, "Priority": s.priority})
    df = pd.DataFrame(rows)
    st.dataframe(df.drop(columns=["id"]), use_container_width=True, hide_index=True)

    if not df.empty:
        idx = st.selectbox("Space to edit", range(len(df)), format_func=lambda i: df.iloc[i]["Space"])
        space = project.spaces[idx]
        c1, c2, c3 = st.columns(3)
        space.quantity = int(c1.number_input("Quantity", 1, 1000, int(space.quantity), key=f"qty_{idx}"))
        space.area = float(c2.number_input("Area / unit (m²)", 0.1, 100000.0, float(space.area), 0.5, key=f"area_{idx}"))
        space.priority = c3.selectbox("Priority", ["low", "normal", "high", "critical"], index=["low", "normal", "high", "critical"].index(space.priority) if space.priority in ["low", "normal", "high", "critical"] else 1, key=f"priority_{idx}")
