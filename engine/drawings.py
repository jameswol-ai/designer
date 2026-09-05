from __future__ import annotations

from typing import Dict, List, Optional, Sequence

from .architectural_model import Element, WALL_HEIGHT
from .building_generator import BuildingModel, generate_building
from .dimensions import grid_axes


def _rooms(model: BuildingModel, floor: int) -> List[Dict]:
    return [r for r in model.rooms if int(r.get("floor", 1)) == int(floor)]


def floor_plan_data(project, floor: int = 1, layout: Optional[Sequence[Dict]] = None) -> Dict:
    model = generate_building(project, layout=layout)
    rooms = _rooms(model, floor)
    return {
        "drawing_type": "floor_plan",
        "floor": int(floor),
        "rooms": rooms,
        "walls": [e.as_dict() for e in model.elements if e.kind == "wall" and e.floor == floor],
        "openings": [e.as_dict() for e in model.elements if e.kind in {"door", "window"} and e.floor == floor],
        "furniture": [e.as_dict() for e in model.elements if e.kind == "furniture" and e.floor == floor],
        "structure": [e.as_dict() for e in model.elements if e.kind == "column" and e.floor == floor],
        "grid": grid_axes(project),
    }


def elevation_data(project, side: str = "front", layout: Optional[Sequence[Dict]] = None) -> Dict:
    model = generate_building(project, layout=layout)
    width = model.depth if side in {"left", "right"} else model.width
    height = model.floors * model.floor_height
    return {
        "drawing_type": "elevation",
        "side": side,
        "width_m": round(width, 3),
        "height_m": round(height, 3),
        "levels": [round(i * model.floor_height, 3) for i in range(model.floors + 1)],
        "openings": [e.as_dict() for e in model.elements if e.kind in {"door", "window"}],
    }


def section_data(project, axis: str = "x", layout: Optional[Sequence[Dict]] = None) -> Dict:
    model = generate_building(project, layout=layout)
    return {
        "drawing_type": "section",
        "axis": axis,
        "width_m": round(model.width if axis == "x" else model.depth, 3),
        "height_m": round(model.floors * model.floor_height, 3),
        "floor_levels": [round(i * model.floor_height, 3) for i in range(model.floors + 1)],
        "stairs": [e.as_dict() for e in model.elements if e.kind == "stair"],
        "slabs": [e.as_dict() for e in model.elements if e.kind == "slab"],
    }


def drawing_sheet(project, sheet_number: str = "A101", title: str = "Floor Plan", floor: int = 1, layout: Optional[Sequence[Dict]] = None) -> Dict:
    return {
        "schema_version": "designer.drawing.v1",
        "sheet_number": sheet_number,
        "title": title,
        "project": project.name,
        "scale": "Conceptual",
        "floor_plan": floor_plan_data(project, floor=floor, layout=layout),
        "notes": ["Conceptual drawing generated from the canonical Designer building model.", "Verify all dimensions, structure, fire safety and accessibility requirements against applicable codes before construction use."],
    }
