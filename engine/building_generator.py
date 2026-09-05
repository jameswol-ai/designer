from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .architectural_model import Element, WALL_HEIGHT
from .layout import generate_layout
from .models import Project


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


def _floor_rooms(project: Project, floor: int, columns: int) -> List[Dict]:
    return [r for r in generate_layout(project, columns=columns) if int(r.get("floor", 1)) == floor]


def _floor_envelope(rooms: List[Dict]) -> tuple[float, float]:
    return (
        max((r["x"] + r["width"] for r in rooms), default=0.0),
        max((r["y"] + r["depth"] for r in rooms), default=0.0),
    )


def _floor_slab(floor: int, width: float, depth: float) -> Element:
    z = (floor - 1) * WALL_HEIGHT
    return Element("floor_slab", floor, f"Level {floor} slab", 0.0, 0.0, width, depth, z, 0.20)


def _roof_slab(floor: int, width: float, depth: float) -> Element:
    z = floor * WALL_HEIGHT
    return Element("roof_slab", floor, "Roof slab", 0.0, 0.0, width, depth, z, 0.20)


def generate_building(project: Project, columns: int = 2) -> BuildingModel:
    """Generate a conceptual multi-floor building model from the current project program."""
    floors = max(1, int(project.floors))
    columns = max(1, int(columns))
    rooms = generate_layout(project, columns=columns)
    elements: List[Element] = []

    for floor in range(1, floors + 1):
        floor_rooms = _floor_rooms(project, floor, columns)
        width, depth = _floor_envelope(floor_rooms)
        if width <= 0.0 or depth <= 0.0:
            continue
        elements.append(_floor_slab(floor, width, depth))
        if floor == floors:
            elements.append(_roof_slab(floor, width, depth))

        z = (floor - 1) * WALL_HEIGHT
        for room in floor_rooms:
            x, y = room["x"], room["y"]
            w, d = room["width"], room["depth"]
            elements.extend([
                Element("wall", floor, f"{room['name']} west wall", x, y, 0.10, d, z, WALL_HEIGHT),
                Element("wall", floor, f"{room['name']} east wall", x + w - 0.10, y, 0.10, d, z, WALL_HEIGHT),
                Element("wall", floor, f"{room['name']} south wall", x, y, w, 0.10, z, WALL_HEIGHT),
                Element("wall", floor, f"{room['name']} north wall", x, y + d - 0.10, w, 0.10, z, WALL_HEIGHT),
                Element("door", floor, f"{room['name']} entrance", x + w / 2.0 - 0.45, y, 0.90, 0.08, z, 2.10),
                Element("window", floor, f"{room['name']} window", x + w * 0.25, y + d - 0.05, max(1.20, w * 0.35), 0.08, z + 0.90, 1.20),
            ])

    return BuildingModel(floors=floors, floor_height=WALL_HEIGHT, rooms=rooms, elements=elements)


def building_summary(project: Project, columns: int = 2) -> Dict:
    return generate_building(project, columns=columns).summary()
