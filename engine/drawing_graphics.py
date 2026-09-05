from __future__ import annotations

from math import cos, radians, sin
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .building_generator import BuildingModel, generate_building
from .drawings import floor_plan_data

Point = Tuple[float, float]


def _line(points: Sequence[Point], layer: str, **extra) -> Dict:
    return {"type": "line", "layer": layer, "points": [[round(x, 3), round(y, 3)] for x, y in points], **extra}


def _text(x: float, y: float, value: str, layer: str = "annotation", size: float = 0.18) -> Dict:
    return {"type": "text", "layer": layer, "x": round(x, 3), "y": round(y, 3), "text": str(value), "size": size}


def _rect(x: float, y: float, width: float, depth: float, layer: str) -> Dict:
    return _line([(x, y), (x + width, y), (x + width, y + depth), (x, y + depth), (x, y)], layer)


def _dimension(x1: float, y1: float, x2: float, y2: float, offset: float, label: str) -> Dict:
    dx, dy = x2 - x1, y2 - y1
    length = (dx * dx + dy * dy) ** 0.5
    if length == 0:
        return {}
    nx, ny = -dy / length, dx / length
    a = (x1 + nx * offset, y1 + ny * offset)
    b = (x2 + nx * offset, y2 + ny * offset)
    return {
        "type": "dimension",
        "layer": "dimensions",
        "points": [[round(a[0], 3), round(a[1], 3)], [round(b[0], 3), round(b[1], 3)]],
        "label": label,
        "extension": [[round(x1, 3), round(y1, 3)], [round(a[0], 3), round(a[1], 3)], [round(x2, 3), round(y2, 3)], [round(b[0], 3), round(b[1], 3)]],
    }


def _grid_bubble(x: float, y: float, label: str) -> List[Dict]:
    return [_line([(x, y), (x, y + 0.35)], "grid"), _text(x, y + 0.52, label, "grid", 0.16)]


def _opening_symbol(element: Dict) -> List[Dict]:
    x, y, w, d = float(element.get("x", 0)), float(element.get("y", 0)), float(element.get("width", 0)), float(element.get("depth", 0))
    kind = element.get("kind", "")
    if kind == "window":
        return [_line([(x, y), (x + w, y)], "openings"), _line([(x, y + d), (x + w, y + d)], "openings")]
    if kind == "door":
        radius = max(w, 0.9)
        return [_line([(x, y), (x + w, y)], "doors"), {"type": "arc", "layer": "doors", "center": [x, y], "radius": radius, "start_deg": 0, "end_deg": 90}]
    return []


def _section_marker(x: float, y: float, label: str) -> List[Dict]:
    return [_line([(x - 0.35, y), (x + 0.35, y)], "markers"), _text(x, y + 0.18, label, "markers", 0.18)]


def floor_plan_graphics(project, floor: int = 1, layout: Optional[Sequence[Dict]] = None) -> Dict:
    data = floor_plan_data(project, floor=floor, layout=layout)
    graphics: List[Dict] = []
    for room in data["rooms"]:
        x, y, w, d = float(room.get("x", 0)), float(room.get("y", 0)), float(room.get("width", 0)), float(room.get("depth", 0))
        graphics.append(_rect(x, y, w, d, "walls"))
        graphics.append(_text(x + w / 2, y + d / 2, room.get("name", "Room"), "room_tags", 0.16))
        graphics.append(_text(x + w / 2, y + d / 2 - 0.25, f"{float(room.get('area', w * d)):.1f} m²", "room_tags", 0.12))
        graphics.append(_dimension(x, y, x + w, y, -0.55, f"{w:.2f} m"))
    for opening in data["openings"]:
        graphics.extend(_opening_symbol(opening))
    for column in data["structure"]:
        x, y = float(column.get("x", 0)), float(column.get("y", 0))
        r = 0.12
        graphics.append(_line([(x-r, y-r), (x+r, y+r)], "structure"))
        graphics.append(_line([(x-r, y+r), (x+r, y-r)], "structure"))
    for i, x in enumerate(data.get("grid", {}).get("x", []), 1) if isinstance(data.get("grid"), dict) else []:
        graphics.extend(_grid_bubble(float(x), -0.8, str(i)))
    graphics.extend(_section_marker(0, max([float(r.get("y", 0)) + float(r.get("depth", 0)) for r in data["rooms"]] or [0]) + 0.8, "A"))
    return {"schema_version": "designer.graphics.v1", "drawing_type": "floor_plan", "floor": floor, "graphics": graphics}


def drawing_graphics(project, drawing_type: str = "floor_plan", floor: int = 1, layout: Optional[Sequence[Dict]] = None) -> Dict:
    if drawing_type == "floor_plan":
        return floor_plan_graphics(project, floor=floor, layout=layout)
    model = generate_building(project, layout=layout)
    height = model.floors * model.floor_height
    span = model.width if drawing_type == "section" else model.width
    graphics = [_line([(0, 0), (span, 0)], "ground"), _line([(0, height), (span, height)], "envelope")]
    for level in range(model.floors + 1):
        z = level * model.floor_height
        graphics.append(_line([(0, z), (span, z)], "levels"))
        graphics.append(_text(0, z + 0.08, f"Level {level}  {z:.2f} m", "levels", 0.14))
    return {"schema_version": "designer.graphics.v1", "drawing_type": drawing_type, "graphics": graphics}
