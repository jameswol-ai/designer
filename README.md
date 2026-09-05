# Designer

**Architectural Design Studio**

Designer is a modular architectural planning application built around metric-based space programming, dimensional rules, adjacency analysis, preliminary floor-plan generation, compliance checks, design scoring, conceptual building geometry, and interactive architectural views.

## Design system

```text
DESIGNER
├── DESIGN BASICS
│   ├── Human Dimensions
│   ├── Space Requirements
│   ├── Movement
│   ├── Accessibility
│   └── Dimensional Coordination
├── BUILDING TYPES
│   ├── Housing
│   ├── Offices
│   ├── Schools
│   ├── Universities
│   ├── Hospitals
│   ├── Hotels
│   ├── Retail
│   ├── Restaurants
│   ├── Libraries
│   ├── Industrial
│   ├── Sports
│   ├── Religious
│   ├── Civic
│   └── Transport
├── ENVIRONMENT
│   ├── Daylight
│   ├── Lighting
│   ├── Ventilation
│   ├── Thermal
│   ├── Acoustics
│   └── Tropical Design
├── SAFETY
│   ├── Fire
│   ├── Egress
│   ├── Accessibility
│   ├── Security
│   └── Flood
└── DESIGN ENGINE
    ├── Space Program
    ├── Adjacency
    ├── Planning
    ├── Dimensions
    ├── Compliance
    ├── Building Model
    ├── Floor Plans
    ├── Sections
    ├── Elevations
    └── Reports
```

## Metric standards

The application includes a small set of Designer-owned illustrative baseline standards. The Metric Handbook itself is copyrighted and is not redistributed by this repository.

Licensed project datasets derived from a permitted copy can be imported through the Metric Handbook workspace as CSV or JSON. Imported standards override the matching Designer baseline keys for the current Streamlit session and are used by program generation and compliance scoring.

Supported fields:

```text
key,category,label,min_area_m2,min_width_m,min_depth_m,notes,source
```

The active standards layer is implemented in `metric/database.py` and `metric/standards.py`.

## Run

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Architecture

```text
streamlit_app.py
├── engine/       # design calculations, planning and geometry
├── metric/       # standards database and Metric integration boundary
├── modules/      # Streamlit workspaces
├── data/         # app-owned taxonomy and project data
└── tests/        # engine tests
```

## Scope

Designer is a conceptual architectural design and planning tool. Generated layouts, geometry, dimensions and compliance results are preliminary design aids and must be checked against the project brief, applicable legislation, local codes, engineering requirements and professional judgment before construction use.
