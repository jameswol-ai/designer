from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

from .architectural_model import Element, WALL_HEIGHT
from .layout import generate_layout
from .models import Project

WALL_THICKNESS = 0.10
DOOR_WIDTH = 0.90
DOOR_DEPTH = 0.08
DOOR_HEIGHT = 2.10
WINDOW_WIDTH = 1.20
WINDOW_DEPTH = 0.08
WINDOW_HEIGHT = 1.20
WINDOW_SILL = 0.90


@dataclass(frozen=True)
class BuildingModel:
    floors: int
    floor_height: float
    rooms: List[Dict]
    elements: List[Element]

    @property
    def width(self) -> float:
        return max((r["x"] + r["width"] for r in self.rooms), default=0.0)

    @property
    def depth(self) -> float:
        return max((r["y"] + r["depth"] for r in self.rooms), default=0.0)

    @property
    def gross_floor_area(self) -> float:
        return sum(float(r.get("area", 0.0)) for r in self.rooms)

    def summary(self) -> Dict:
        counts: Dict[str, int] = {}
        for element in self.elements:
            counts[element.kind] = counts.get(element.kind, 0) + 1
        return {
            "floors": self.floors,
            "floor_height_m": self.floor_height,
            "width_m": round(self.width, 2),
            "depth_m": round(self.depth, 2),
            "gross_floor_area_m2": round(self.gross_floor_area, 2),
            "rooms": len(self.rooms),
            "elements": counts,
        }


def _normalise_layout(project: Project, columns: int, layout: Optional[Sequence[Dict]]) -> List[Dict]:
    source = list(layout) if layout is not None else generate_layout(project, columns=columns)
    return [dict(room) for room in source]


def _floor_envelope(rooms: List[Dict]) -> tuple[float, float]:
    return (
        max((float(r["x"]) + float(r["width"]) for r in rooms), default=0.0),
        max((float(r["y"]) + float(r["depth"]) for r in rooms), default=0.0),
    )


def _floor_slab(floor: int, width: float, depth: float) -> Element:
    z = (floor - 1) * WALL_HEIGHT
    return Element("floor_slab", floor, f"Level {floor} slab", 0.0, 0.0, width, depth, z, 0.20)


def _roof_slab(floor: int, width: float, depth: float) -> Element:
    z = floor * WALL_HEIGHT
    return Element("roof_slab", floor, "Roof slab", 0.0, 0.0, width, depth, z, 0.20)


def _wall_elements(room: Dict, floor: int, z: float) -> List[Element]:
    x, y = float(room["x"]), float(room["y"])
    w, d = float(room["width"]), float(room["depth"])
    return [
        Element("wall", floor, f"{room['name']} west wall", x, y, WALL_THICKNESS, d, z, WALL_HEIGHT),
        Element("wall", floor, f"{room['name']} east wall", x + w - WALL_THICKNESS, y, WALL_THICKNESS, d, z, WALL_HEIGHT),
        Element("wall", floor, f"{room['name']} south wall", x, y, w, WALL_THICKNESS, z, WALL_HEIGHT),
        Element("wall", floor, f"{room['name']} north wall", x, y + d - WALL_THICKNESS, w, WALL_THICKNESS, z, WALL_HEIGHT),
    ]


def _opening_elements(room: Dict, floor: int, z: float) -> List[Element]:
    x, y = float(room["x"]), float(room["y"])
    w, d = float(room["width"]), float(room["depth"])
    door_x = x + max(0.0, (w - DOOR_WIDTH) / 2.0)
    window_width = min(max(WINDOW_WIDTH, w * 0.35), max(WINDOW_WIDTH, w - 0.30))
    window_x = x + max(0.0, (w - window_width) / 2.0)
    return [
        Element("door", floor, f"{room['name']} entrance", door_x, y, DOOR_WIDTH, DOOR_DEPTH, z, DOOR_HEIGHT),
        Element("window", floor, f"{room['name']} window", window_x, y + d - WINDOW_DEPTH, window_width, WINDOW_DEPTH, z + WINDOW_SILL, WINDOW_HEIGHT),
    ]


def generate_building(
    project: Project,
    columns: int = 2,
    layout: Optional[Sequence[Dict]] = None,
) -> BuildingModel:
    """Generate a conceptual multi-floor building from a program or supplied spatial layout.

    The optional layout lets a selected planning alternative flow directly into the
    building model and keeps the generator deterministic.
    """
    floors = max(1, int(project.floors))
    columns = max(1, int(columns))
    rooms = _normalise_layout(project, columns, layout)
    elements: List[Element] = []

    for floor in range(1, floors + 1):
        floor_rooms = [r for r in rooms if int(r.get("floor", 1)) == floor]
        width, depth = _floor_envelope(floor_rooms)
        if width <= 0.0 or depth <= 0.0:
            continue

        elements.append(_floor_slab(floor, width, depth))
        if floor == floors:
            elements.append(_roof_slab(floor, width, depth))

        z = (floor - 1) * WALL_HEIGHT
        for room in floor_rooms:
            elements.extend(_wall_elements(room, floor, z))
            elements.extend(_opening_elements(room, floor, z))

    return BuildingModel(floors=floors, floor_height=WALL_HEIGHT, rooms=rooms, elements=elements)


def building_summary(project: Project, columns: int = 2) -> Dict:
    return generate_building(project, columns=columns).summary()
