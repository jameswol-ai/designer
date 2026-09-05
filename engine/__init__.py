from .models import Project, Space
from .data_contract import SCHEMA_VERSION, project_document, normalize_layout, validate_document
from .planner import generate_program, build_project
from .adjacency import adjacency_matrix, adjacency_score, adjacency_summary
from .layout import generate_layout
from .space_planning import generate_alternatives, best_alternative, planning_summary
from .planning_constraints import classify_zone, required_adjacencies, adjacency_proximity_score, overlap_penalty, zoning_score, grid_alignment_score, constraint_report
from .building_generator import BuildingModel, generate_building, building_summary
from .validation import check_project, score_project

# Drawing exports are kept optional at package level so importing the core
# engine does not require the Streamlit drawing UI or introduce circular imports.
try:
    from .drawing_graphics import drawing_graphics, floor_plan_graphics
    from .drawing_renderer import render_graphics, render_drawing
    from .drawing_sheet import TitleBlock, make_sheet, drawing_register
    from .drawings import drawing_sheet, floor_plan_data, elevation_data, section_data
except ImportError:
    drawing_graphics = None
    floor_plan_graphics = None
    render_graphics = None
    render_drawing = None
    TitleBlock = None
    make_sheet = None
    drawing_register = None
    drawing_sheet = None
    floor_plan_data = None
    elevation_data = None
    section_data = None

__all__ = [
    "Project", "Space", "SCHEMA_VERSION", "project_document", "normalize_layout", "validate_document",
    "generate_program", "build_project", "adjacency_matrix", "adjacency_score", "adjacency_summary",
    "generate_layout", "generate_alternatives", "best_alternative", "planning_summary", "classify_zone",
    "required_adjacencies", "adjacency_proximity_score", "overlap_penalty", "zoning_score", "grid_alignment_score",
    "constraint_report", "BuildingModel", "generate_building", "building_summary", "check_project", "score_project",
    "drawing_graphics", "floor_plan_graphics", "render_graphics", "render_drawing", "TitleBlock", "make_sheet",
    "drawing_register", "drawing_sheet", "floor_plan_data", "elevation_data", "section_data",
]
