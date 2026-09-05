from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Sequence

from .data_contract import SCHEMA_VERSION
from .layout import generate_layout

WALL_HEIGHT = 3.2
EXTERIOR_WALL = 0.20
INTERIOR_WALL = 0.10
SLAB_THICKNESS = 0.20
DOOR_WIDTH = 0.90
WINDOW_HEIGHT = 1.20
WINDOW_SILL = 0.90
STAIR_WIDTH = 1.20


@dataclass(frozen=True)
class Element:
    id: str
    kind: str
    floor: int
    name: str
    x: float
    y: float
    width: float
    depth: float
    z: float = 0.0
    height: float = 0.0
    space_id: Optional[str] = None
    metadata: Dict[str, Any] = None

    def as_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["schema_version"] = SCHEMA_VERSION
        data["metadata"] = data["metadata"] or {}
        return data


def _element_id(kind: str, floor: int, key: str) -> str:
    safe = "".join(c if c.isalnum() else "-" for c in key.lower()).strip("-")
    return f"{kind}-{floor:02d}-{safe}"


def _room_walls(room: Dict, exterior: bool = False) -> List[Element]:
    t = EXTERIOR_WALL if exterior else INTERIOR_WALL
    x, y, w, d = map(float, (room["x"], room["y"], room["width"], room["depth"]))
    floor = int(room.get("floor", 1)); z = (floor - 1) * WALL_HEIGHT
    sid = room.get("space_id")
    return [
        Element(_element_id("wall", floor, f"{room['name']}-west"), "wall", floor, f"{room['name']} west wall", x, y, t, d, z, WALL_HEIGHT, sid),
        Element(_element_id("wall", floor, f"{room['name']}-east"), "wall", floor, f"{room['name']} east wall", x + w - t, y, t, d, z, WALL_HEIGHT, sid),
        Element(_element_id("wall", floor, f"{room['name']}-south"), "wall", floor, f"{room['name']} south wall", x, y, w, t, z, WALL_HEIGHT, sid),
        Element(_element_id("wall", floor, f"{room['name']}-north"), "wall", floor, f"{room['name']} north wall", x, y + d - t, w, t, z, WALL_HEIGHT, sid),
    ]


def building_elements(project, floor: Optional[int] = None, layout: Optional[Sequence[Dict]] = None) -> List[Element]:
    rooms = list(layout) if layout is not None else generate_layout(project)
    if floor is not None:
        rooms = [r for r in rooms if int(r.get("floor", 1)) == int(floor)]
    elements: List[Element] = []
    for room in rooms:
        rf = int(room.get("floor", 1)); z = (rf - 1) * WALL_HEIGHT; sid = room.get("space_id")
        elements.extend(_room_walls(room))
        elements.append(Element(_element_id("slab", rf, room["name"]), "slab", rf, f"{room['name']} slab", room["x"], room["y"], room["width"], room["depth"], z, SLAB_THICKNESS, sid))
        elements.append(Element(_element_id("door", rf, room["name"]), "door", rf, f"{room['name']} door", room["x"] + room["width"] / 2 - DOOR_WIDTH / 2, room["y"], DOOR_WIDTH, 0.08, z, 2.1, sid))
        elements.append(Element(_element_id("window", rf, room["name"]), "window", rf, f"{room['name']} window", room["x"] + room["width"] * 0.25, room["y"] + room["depth"] - 0.05, max(1.2, room["width"] * 0.35), 0.08, z + WINDOW_SILL, WINDOW_HEIGHT, sid))
    return elements


def structural_elements(project, layout: Optional[Sequence[Dict]] = None) -> List[Element]:
    from .structure_grid import candidate_grids
    rooms = list(layout) if layout is not None else generate_layout(project)
    candidates = candidate_grids(project)
    if not candidates:
        return []
    spacing = float(candidates[0].get("span_m", 6.0))
    width = max((float(r["x"]) + float(r["width"]) for r in rooms), default=spacing)
    depth = max((float(r["y"]) + float(r["depth"]) for r in rooms), default=spacing)
    elements: List[Element] = []
    for floor in range(1, max(1, int(project.floors)) + 1):
        z = (floor - 1) * WALL_HEIGHT; x = 0.0
        while x <= width + 0.01:
            y = 0.0
            while y <= depth + 0.01:
                elements.append(Element(_element_id("column", floor, f"{x:.2f}-{y:.2f}"), "column", floor, f"Column {floor}-{x:.1f}-{y:.1f}", x, y, 0.30, 0.30, z, WALL_HEIGHT, metadata={"grid_spacing_m": spacing}))
                y += spacing
            x += spacing
    return elements


def stair_elements(project) -> List[Element]:
    return [Element(_element_id("stair", floor, f"to-{floor + 1}"), "stair", floor, f"Stair to level {floor + 1}", 0.0, 0.0, STAIR_WIDTH, 3.6, (floor - 1) * WALL_HEIGHT, WALL_HEIGHT, metadata={"width_m": STAIR_WIDTH}) for floor in range(1, max(1, int(project.floors)))]
