from .models import Project, Space
from .data_contract import SCHEMA_VERSION, project_document, normalize_layout, validate_document
from .planner import generate_program, build_project
from .adjacency import adjacency_matrix, adjacency_score, adjacency_summary
from .layout import generate_layout
from .space_planning import generate_alternatives, best_alternative, planning_summary
from .planning_constraints import (
    classify_zone,
    required_adjacencies,
    adjacency_proximity_score,
    overlap_penalty,
    zoning_score,
    grid_alignment_score,
    constraint_report,
)
from .building_generator import BuildingModel, generate_building, building_summary
from .validation import check_project, score_project

__all__ = [
    "Project", "Space", "SCHEMA_VERSION", "project_document", "normalize_layout", "validate_document",
    "generate_program", "build_project", "adjacency_matrix", "adjacency_score", "adjacency_summary",
    "generate_layout", "generate_alternatives", "best_alternative", "planning_summary",
    "classify_zone", "required_adjacencies", "adjacency_proximity_score", "overlap_penalty",
    "zoning_score", "grid_alignment_score", "constraint_report", "BuildingModel", "generate_building",
    "building_summary", "check_project", "score_project",
]
