from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

from .building_generator import generate_building
from .drawing_graphics import floor_plan_graphics


@dataclass
class TitleBlock:
    project: str
    drawing_number: str
    title: str
    scale: str = "NTS"
    status: str = "CONCEPT"
    revision: str = "P01"
    drawn_by: str = "Designer"
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "project": self.project,
            "drawing_number": self.drawing_number,
            "title": self.title,
            "scale": self.scale,
            "status": self.status,
            "revision": self.revision,
            "drawn_by": self.drawn_by,
            "notes": self.notes,
        }


def make_sheet(project, drawing_number: str = "A101", title: str = "Ground Floor Plan", floor: int = 1, layout: Optional[Sequence[Dict]] = None, scale: str = "1:100") -> Dict:
    model = generate_building(project, layout=layout)
    graphics = floor_plan_graphics(project, floor=floor, layout=layout)
    title_block = TitleBlock(
        project=project.name,
        drawing_number=drawing_number,
        title=title,
        scale=scale,
        notes=[
            "Conceptual architectural drawing generated from the canonical Designer model.",
            "Dimensions and compliance criteria require professional verification before construction use.",
        ],
    )
    return {
        "schema_version": "designer.drawing_sheet.v1",
        "sheet_size": "A1",
        "drawing_number": drawing_number,
        "title": title,
        "project_id": project.id,
        "floor": floor,
        "model_summary": model.summary(),
        "graphics": graphics["graphics"],
        "title_block": title_block.to_dict(),
    }


def drawing_register(project, layout: Optional[Sequence[Dict]] = None) -> List[Dict]:
    floors = max(1, int(project.floors))
    register = [{"drawing_number": "A001", "title": "Drawing Index", "discipline": "Architecture", "status": "CONCEPT"}]
    for floor in range(1, floors + 1):
        register.append({"drawing_number": f"A{100 + floor:03d}", "title": f"Level {floor} Floor Plan", "discipline": "Architecture", "status": "CONCEPT"})
    register.extend([
        {"drawing_number": "A201", "title": "Building Elevations", "discipline": "Architecture", "status": "CONCEPT"},
        {"drawing_number": "A301", "title": "Building Sections", "discipline": "Architecture", "status": "CONCEPT"},
    ])
    return register
