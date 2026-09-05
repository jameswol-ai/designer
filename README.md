# Designer

**Architectural Design Studio**

Designer is a modular architectural planning application for turning a project brief into a structured, measurable conceptual building model.

## Modern design workflow

```text
Brief
  -> Site & Context
  -> Space Program
  -> Metric Standards
  -> Adjacency
  -> Space Planning
  -> Dimensions
  -> Compliance
  -> Building Model
  -> Floor Plans / Sections / Elevations
  -> Analysis / Reports
```

## Design system

```text
DESIGNER
├── PROJECT
│   ├── Dashboard
│   ├── Project Brief
│   └── Site & Context
├── DESIGN BASICS
│   ├── Human Dimensions
│   ├── Space Requirements
│   ├── Movement
│   ├── Accessibility
│   └── Dimensional Coordination
├── BUILDING TYPES
├── ENVIRONMENT
├── SAFETY
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
    ├── Reports
    └── Metric Standards
```

## Modern data architecture

Designer now uses a versioned project document contract:

```text
schema_version: designer.project.v2
project
  id
  name
  typology
  site_area_m2
  floors
  target_gfa_m2
  spaces[]
    id
    category
    quantity
    area_m2
    min_width_m
    min_depth_m
    priority
    metadata
layout[]
  id
  space_id
  floor
  geometry
    x
    y
    width
    depth
    rotation_deg
metrics
```

The data contract is implemented in `engine/data_contract.py`. It provides normalized geometry records, stable IDs, schema versioning, portable JSON documents and basic document validation. Legacy top-level geometry fields remain available so existing calculation and visualization modules remain compatible.

## Metric standards

The application includes a small set of Designer-owned illustrative baseline standards. The Metric Handbook itself is copyrighted and is not redistributed by this repository.

Licensed project datasets derived from a permitted copy can be imported through the Metric Standards workspace as CSV or JSON. Imported standards override matching Designer baseline keys for the current Streamlit session and are used by program generation and compliance scoring.

Supported fields:

```text
key,category,label,min_area_m2,min_width_m,min_depth_m,notes,source
```

## Engine architecture

```text
Streamlit modules
      |
      v
Versioned project data
      |
      +--> Metric standards
      +--> Program engine
      +--> Adjacency / constraints
      +--> Layout engine
      +--> Compliance engine
      +--> Building geometry
      +--> Visualization
      +--> Reports / export
```

The calculation layer does not depend on Streamlit. UI state is passed into engine functions explicitly.

## Run

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Quality and scope

Designer is a conceptual architectural design and planning tool. Generated layouts, geometry, dimensions and compliance results are preliminary design aids and must be checked against the project brief, applicable legislation, local codes, engineering requirements and professional judgment before construction use.
