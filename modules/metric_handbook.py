import json

import pandas as pd
import streamlit as st

from metric.catalog import BOOK_METADATA, MetricStandard, catalog_rows


def _parse_uploaded(uploaded):
    if uploaded is None:
        return []
    raw = uploaded.getvalue().decode("utf-8")
    if uploaded.name.lower().endswith(".json"):
        payload = json.loads(raw)
        if isinstance(payload, dict):
            payload = payload.get("standards", [])
        return [MetricStandard(**item) for item in payload]

    frame = pd.read_csv(uploaded)
    rows = []
    for item in frame.to_dict(orient="records"):
        rows.append(
            MetricStandard(
                key=str(item["key"]),
                category=str(item.get("category", item["key"])),
                label=str(item.get("label", item["key"])),
                min_area_m2=float(item.get("min_area_m2", 0.0)),
                min_width_m=float(item.get("min_width_m", 0.0)),
                min_depth_m=float(item.get("min_depth_m", 0.0)),
                notes=str(item.get("notes", "")),
                source=str(item.get("source", "User-supplied licensed data")),
            )
        )
    return rows


def render(project=None):
    st.subheader("Metric Handbook")
    st.caption("Architectural planning reference interface. The application bundles only its own illustrative baseline data and can import licensed project standards.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Reference", BOOK_METADATA["title"])
    c2.metric("Publisher", BOOK_METADATA["publisher"])
    c3.metric("Bundled book content", "No")

    st.info("The full Metric Handbook is copyrighted. Designer does not redistribute the book. Upload a licensed CSV or JSON dataset derived from your permitted copy to use handbook-specific values in a project.")

    uploaded = st.file_uploader("Import licensed Metric Handbook-derived standards", type=["csv", "json"])
    imported = _parse_uploaded(uploaded) if uploaded is not None else []

    if imported:
        st.session_state["metric_handbook_standards"] = [item.to_dict() for item in imported]
        st.success(f"Imported {len(imported)} licensed standards for this session.")

    session_rows = st.session_state.get("metric_handbook_standards")
    if session_rows:
        st.subheader("Active licensed project dataset")
        st.dataframe(pd.DataFrame(session_rows), use_container_width=True, hide_index=True)
        st.download_button(
            "Export active standards JSON",
            data=json.dumps({"standards": session_rows}, indent=2),
            file_name="designer_metric_standards.json",
            mime="application/json",
        )
    else:
        st.subheader("Designer baseline standards")
        st.dataframe(pd.DataFrame(catalog_rows()), use_container_width=True, hide_index=True)

    with st.expander("Expected import schema"):
        st.code(
            "key,category,label,min_area_m2,min_width_m,min_depth_m,notes,source\n"
            "example_space,Residential,Example space,12,3,4,Project licensed reference,Licensed Metric Handbook dataset",
            language="text",
        )
