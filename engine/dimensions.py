from __future__ import annotations

from typing import Dict, List, Optional

from .layout import generate_layout
from .models import Project
from .structure_grid import candidate_grids

DEFAULT_GRID_SPACING = 6.0
DIMENSION_OFFSET = 0.6


def _round(value: float) -> float:
    return round(float(value), 2)


def room_dimensions(project: Project, floor: Optional[int] = None) -> List[Dict]:
    rows: List[Dict] = []
    for room in generate_layout(project):
        if floor is not None and int(room.get("floor", 1)) != int(floor):
            continue
        rows.append({
            "floor": int(room.get("floor", 1)),
            "space": room["name"],
            "width_m": _round(room["width"]),
            "depth_m": _round(room["depth"]),
            "area_m2": _round(room["area"]),
            "x_m": _round(room["x"]),
            "y_m": _round(room["y"]),
        })
    return rows


def dimension_summary(project: Project, floor: Optional[int] = None) -> Dict:
    rooms = room_dimensions(project, floor)
    return {
        "rooms": len(rooms),
        "total_area_m2": _round(sum(r["area_m2"] for r in rooms)),
        "overall_width_m": _round(max((r["x_m"] + r["width_m"] for r in rooms), default=0)),
        "overall_depth_m": _round(max((r["y_m"] + r["depth_m"] for r in rooms), default=0)),
    }


def grid_axes(project: Project, spacing: Optional[float] = None) -> Dict[str, List[float]]:
    candidates = candidate_grids(project)
    selected = candidates[0] if candidates else {}
    grid_spacing = float(spacing or selected.get("span_m", DEFAULT_GRID_SPACING))
    grid_spacing = max(1.0, grid_spacing)
    summary = dimension_summary(project)
    width = max(summary["overall_width_m"], grid_spacing)
    depth = max(summary["overall_depth_m"], grid_spacing)
    x: List[float] = []
    y: List[float] = []
    value = 0.0
    while value <= width + 0.01:
        x.append(_round(value))
        value += grid_spacing
    value = 0.0
    while value <= depth + 0.01:
        y.append(_round(value))
        value += grid_spacing
    return {"x": x, "y": y, "spacing_m": _round(grid_spacing)}


def grid_schedule(project: Project, spacing: Optional[float] = None) -> List[Dict]:
    axes = grid_axes(project, spacing)
    rows: List[Dict] = []
    for index, value in enumerate(axes["x"]):
        rows.append({"axis": chr(65 + index), "direction": "X", "position_m": value})
    for index, value in enumerate(axes["y"], start=1):
        rows.append({"axis": str(index), "direction": "Y", "position_m": value})
    return rows


def dimension_chains(project: Project, floor: int = 1) -> Dict[str, List[Dict]]:
    rooms = room_dimensions(project, floor)
    if not rooms:
        return {"horizontal": [], "vertical": []}
    horizontal = [{"from": r["x_m"], "to": _round(r["x_m"] + r["width_m"]), "dimension_m": r["width_m"], "space": r["space"]} for r in rooms]
    vertical = [{"from": r["y_m"], "to": _round(r["y_m"] + r["depth_m"]), "dimension_m": r["depth_m"], "space": r["space"]} for r in rooms]
    return {"horizontal": horizontal, "vertical": vertical}
