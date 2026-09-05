# Designer

**Architectural Design Studio**

Designer is a modular architectural planning application built around metric-based space programming, dimensional rules, adjacency analysis, preliminary floor-plan generation, compliance checks, and design scoring.

## V1
- Project brief and building typologies
- Metric standards data layer
- Space-program generator
- Adjacency matrix
- Preliminary rectangular floor-plan generation
- Area schedules and efficiency metrics
- Metric compliance checks
- Interactive Plotly diagrams
- JSON export

> **Metric Handbook note:** the application provides a standards-data architecture and illustrative baseline values. It does not reproduce the copyrighted Metric Handbook. Load licensed/user-provided handbook data into `metric/data/` when available.

## Run

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Architecture

```text
streamlit_app.py
├── engine/       # design calculations and geometry
├── metric/       # standards database and typologies
├── modules/      # Streamlit views
├── data/         # user/project data
└── tests/        # engine tests
```
