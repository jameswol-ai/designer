import json

import pandas as pd
import streamlit as st

from metric.catalog import BOOK_METADATA, MetricStandard, catalog_rows

REQUIRED = {"key", "category", "label"}
NUMERIC = ("min_area_m2", "min_width_m", "min_depth_m")


def _parse_uploaded(uploaded):
    if uploaded is None:
        return []
    raw = uploaded.getvalue().decode("utf-8")
    if uploaded.name.lower().endswith(".json"):
        payload = json.loads(raw)
        payload = payload.get("standards", []) if isinstance(payload, dict) else payload
        if not isinstance(payload, list):
            raise ValueError("JSON must contain a standards array.")
        records = payload
    else:
        records = pd.read_csv(uploaded).to_dict(orient="records")

    result = []
    for item in records:
        missing = REQUIRED - set(item)
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(sorted(missing))}")
        values = {key: item.get(key, 0.0) for key in NUMERIC}
        result.append(MetricStandard(
            key=str(item["key"]).strip(), category=str(item["category"]).strip(),
            label=str(item["label"]).strip(), min_area_m2=float(values["min_area_m2"] or 0),
            min_width_m=float(values["min_width_m"] or 0), min_depth_m=float(values["min_depth_m"] or 0),
            notes=str(item.get("notes", "")), source=str(item.get("source", "User-supplied licensed data")),
        ))
    return result


def render(project=None):
    st.subheader("Metric Standards")
    st.caption("Versioned standards data layer for architectural programming. Only app-owned illustrative baseline values are bundled.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Reference", BOOK_METADATA["title"])
    c2.metric("Publisher", BOOK_METADATA["publisher"])
    c3.metric("Bundled book content", "No")
    st.info("Import standards from a licensed project dataset. Designer stores only the structured records supplied for the current session.")

    uploaded = st.file_uploader("Import licensed standards", type=["csv", "json"], key="metric_standards_upload")
    if uploaded is not None:
        try:
            imported = _parse_uploaded(uploaded)
            st.session_state["metric_handbook_standards"] = [item.to_dict() for item in imported]
            st.success(f"Imported {len(imported)} standards.")
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            st.error(f"Import failed: {exc}")

    session_rows = st.session_state.get("metric_handbook_standards", [])
    if session_rows:
        df = pd.DataFrame(session_rows)
        st.subheader("Active project standards")
        search = st.text_input("Filter standards", key="metric_filter")
        if search:
            mask = df.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
            df = df[mask]
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("Export active standards JSON", json.dumps({"schema_version": "designer.metric.v1", "standards": session_rows}, indent=2), "designer_metric_standards.json", "application/json")
        if st.button("Clear active standards", key="clear_metric_standards"):
            st.session_state.pop("metric_handbook_standards", None)
            st.rerun()
    else:
        st.subheader("Designer baseline standards")
        st.dataframe(pd.DataFrame(catalog_rows()), use_container_width=True, hide_index=True)

    with st.expander("Import schema"):
        st.code("key,category,label,min_area_m2,min_width_m,min_depth_m,notes,source", language="text")
