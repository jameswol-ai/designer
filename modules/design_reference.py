from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st


REFERENCE_PATH = Path(__file__).resolve().parents[1] / "data" / "design_reference.json"


def _taxonomy():
    return json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))


def render(project=None, section=None, topic=None):
    taxonomy = _taxonomy()
    section = section or "Design Basics"
    topics = taxonomy.get(section, [])

    st.subheader(section)
    st.caption("Structured architectural design workspace. Reference content is a taxonomy and rule framework, not a reproduction of copyrighted publications.")

    selected = topic or st.selectbox("Topic", topics, key=f"reference_topic_{section}")
    st.markdown(f"### {selected}")

    if section == "Design Basics":
        rows = [
            {"Topic": "Human Dimensions", "Engine role": "People, furniture and ergonomic clearances"},
            {"Topic": "Space Requirements", "Engine role": "Minimum area and dimensional validation"},
            {"Topic": "Movement", "Engine role": "Circulation paths, corridors and movement zones"},
            {"Topic": "Accessibility", "Engine role": "Accessible routes, doors, ramps and turning space"},
            {"Topic": "Dimensional Coordination", "Engine role": "Grid, room and dimensional coordination"},
        ]
    elif section == "Building Types":
        rows = [{"Building type": item, "Planning engine": "Typology template + active metric standards"} for item in topics]
    elif section == "Environment":
        rows = [{"Topic": item, "Engine role": "Environmental design checks and future simulation hook"} for item in topics]
    elif section == "Safety":
        rows = [{"Topic": item, "Engine role": "Safety validation and compliance workflow"} for item in topics]
    else:
        rows = [{"Design Engine": item, "Status": "Integrated" if item in {"Space Program", "Adjacency", "Planning", "Dimensions", "Compliance", "Building Model", "Floor Plans", "Sections", "Elevations", "Reports"} else "Planned"} for item in topics]

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    if project is not None:
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("Project", project.name)
        c2.metric("Typology", project.typology)
        c3.metric("Floors", max(1, int(project.floors)))

    with st.expander("Implementation notes"):
        st.write("Use licensed project datasets for handbook-derived numeric values. Designer keeps source metadata with imported standards so validation results can be traced to the active dataset.")
