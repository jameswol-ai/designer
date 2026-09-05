from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

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
    kind: str
    floor: int
    name: str
    x: float
    y: float
    width: float
    depth: float
    z: float = 0.0
    height: float = 0.0

    def as_dict(self) -> Dict:
        return self.__dict__.copy()


def _room_walls(room: Dict, exterior: bool = False) -> List[Element]:
    t = EXTERIOR_WALL if exterior else INTERIOR_WALL
    x, y = room["x"], room["y"]
    w, d = room["width"], room["depth"]
    floor = int(room.get("floor", 1))
    z = (floor - 1) * WALL_HEIGHT
    return [
        Element("wall", floor, f"{room['name']} west wall", x, y, t, d, z, WALL_HEIGHT),
        Element("wall", floor, f"{room['name']} east wall", x + w - t, y, t, d, z, WALL_HEIGHT),
        Element("wall", floor, f"{room['name']} south wall", x, y, w, t, z, WALL_HEIGHT),
        Element("wall", floor, f"{room['name']} north wall", x, y + d - t, w, t, z, WALL_HEIGHT),
    ]


def room_elements(project, floor: Optional[int] = None) -> List[Element]:
    rooms = generate_layout(project)
    if floor is not None:
        rooms = [r for r in rooms if int(r.get("floor", 1)) == int(floor)]
    elements: List[Element] = []
    for room in rooms:
        elements.extend(_room_walls(room))
        elements.append(Element("slab", int(room.get("floor", 1)), f"{room['name']} slab", room["x"], room["y"], room["width"], room["depth"], (int(room.get("floor", 1)) - 1) * WALL_HEIGHT, SLAB_THICKNESS))
        elements.append(Element("door", int(room.get("floor", 1)), f"{room['name']} door", room["x"] + room["width"] / 2 - DOOR_WIDTH / 2, room["y"], DOOR_WIDTH, 0.08, (int(room.get("floor", 1)) - 1) * WALL_HEIGHT, 2.1))
        elements.append(Element("window", int(room.get("floor", 1)), f"{room['name']} window", room["x"] + room["width"] * 0.25, room["y"] + room["depth"] - 0.05, max(1.2, room["width"] * 0.35), 0.08, (int(room.get("floor", 1)) - 1) * WALL_HEIGHT + WINDOW_SILL, WINDOW_HEIGHT))
    return elements


def structural_elements(project) -> List[Element]:
    from .structure_grid import candidate_grids

    candidates = candidate_grids(project)
    if not candidates:
        return []
    grid = candidates[0]
    spacing = float(grid.get("span_m", 6.0))
    width = max((r["x"] + r["width"] for r in generate_layout(project)), default=spacing)
    depth = max((r["y"] + r["depth"] for r in generate_layout(project)), default=spacing)
    elements: List[Element] = []
    for floor in range(1, max(1, int(project.floors)) + 1):
        z = (floor - 1) * WALL_HEIGHT
        x = 0.0
        while x <= width + 0.01:
            y = 0.0
            while y <= depth + 0.01:
                elements.append(Element("column", floor, f"Column {floor}-{x:.1f}-{y:.1f}", x, y, 0.30, 0.30, z, WALL_HEIGHT))
                y += spacing
            x += spacing
    return elements


def stair_elements(project) -> List[Element]:
    elements: List[Element] = []
    for floor in range(1, max(1, int(project.floors))):
        z = (floor - 1) * WALL_HEIGHT
        elements.append(Element("stair", floor, f"Stair to level {floor + 1}", 0.0, 0.0, STAIR_WIDTH, 3.6, z, WALL_HEIGHT))
    return elements


def building_elements(project, floor: Optional[int] = None) -> List[Element]:
    elements = room_elements(project, floor)
    if floor is None:
        elements.extend(structural_elements(project))
        elements.extend(stair_elements(project))
    else:
        elements.extend(e for e in structural_elements(project) if e.floor == int(floor))
        elements.extend(e for e in stair_elements(project) if e.floor == int(floor))
    return elements


def element_summary(project) -> Dict[str, int]:
    elements = building_elements(project)
    summary: Dict[str, int] = {}
    for element in elements:
        summary[element.kind] = summary.get(element.kind, 0) + 1
    return summary
