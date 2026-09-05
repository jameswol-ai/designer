from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

from .architectural_model import Element, WALL_HEIGHT, building_elements, structural_elements, stair_elements
from .data_contract import SCHEMA_VERSION
from .layout import generate_layout
from .models import Project
from .furniture_model import furniture_elements


@dataclass(frozen=True)
class BuildingModel:
    schema_version: str
    floors: int
    floor_height: float
    rooms: List[Dict]
    elements: List[Element]

    @property
    def width(self) -> float:
        return max((float(r["x"]) + float(r["width"]) for r in self.rooms), default=0.0)

    @property
    def depth(self) -> float:
        return max((float(r["y"]) + float(r["depth"]) for r in self.rooms), default=0.0)

    @property
    def gross_floor_area(self) -> float:
        return sum(float(r.get("area_m2", r.get("area", 0.0))) for r in self.rooms)

    def to_dict(self) -> Dict:
        return {
            "schema_version": self.schema_version,
            "floors": self.floors,
            "floor_height_m": self.floor_height,
            "envelope": {"width_m": self.width, "depth_m": self.depth},
            "gross_floor_area_m2": self.gross_floor_area,
            "rooms": self.rooms,
            "elements": [element.as_dict() for element in self.elements],
        }

    def summary(self) -> Dict:
        counts: Dict[str, int] = {}
        for element in self.elements:
            counts[element.kind] = counts.get(element.kind, 0) + 1
        return {"schema_version": self.schema_version, "floors": self.floors, "floor_height_m": self.floor_height, "width_m": round(self.width, 2), "depth_m": round(self.depth, 2), "gross_floor_area_m2": round(self.gross_floor_area, 2), "rooms": len(self.rooms), "elements": counts}


def generate_building(project: Project, columns: int = 2, layout: Optional[Sequence[Dict]] = None) -> BuildingModel:
    """Generate one coherent building model from one authoritative spatial layout."""
    rooms = [dict(room) for room in (layout if layout is not None else generate_layout(project, columns=columns))]
    elements = building_elements(project, layout=rooms)
    elements.extend(structural_elements(project, layout=rooms))
    elements.extend(stair_elements(project))
    elements.extend(Element(item.id, "furniture", item.floor, item.name, item.x, item.y, item.width, item.depth, height=item.height, space_id=item.space_id, metadata={"room": item.room}) for item in furniture_elements(project, layout=rooms))
    return BuildingModel(SCHEMA_VERSION, max(1, int(project.floors)), WALL_HEIGHT, rooms, elements)


def building_summary(project: Project, columns: int = 2, layout: Optional[Sequence[Dict]] = None) -> Dict:
    return generate_building(project, columns=columns, layout=layout).summary()
