from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Sequence
from uuid import uuid5, NAMESPACE_URL

from .furniture import furniture_for
from .layout import generate_layout


@dataclass(frozen=True)
class FurnitureElement:
    id: str
    floor: int
    room: str
    space_id: Optional[str]
    name: str
    x: float
    y: float
    width: float
    depth: float
    height: float = 0.75

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


def furniture_elements(project, floor: Optional[int] = None, layout: Optional[Sequence[Dict]] = None) -> List[FurnitureElement]:
    rooms = list(layout) if layout is not None else generate_layout(project)
    if floor is not None:
        rooms = [r for r in rooms if int(r.get("floor", 1)) == int(floor)]
    elements: List[FurnitureElement] = []

    for room in rooms:
        room_floor = int(room.get("floor", 1))
        items = furniture_for(type("SpaceProxy", (), {"category": room["category"]})())
        if not items:
            continue
        cursor_x, cursor_y = float(room["x"]) + 0.35, float(room["y"]) + 0.35
        for item in items:
            width, depth = float(item["width"]), float(item["depth"])
            if cursor_x + width > float(room["x"]) + float(room["width"]) - 0.2:
                cursor_x = float(room["x"]) + 0.35
                cursor_y += depth + 0.35
            if cursor_y + depth > float(room["y"]) + float(room["depth"]) - 0.2:
                continue
            key = f"{room.get('id', room['name'])}:{item['name']}:{round(cursor_x,3)}:{round(cursor_y,3)}"
            elements.append(FurnitureElement(
                id=str(uuid5(NAMESPACE_URL, key)), floor=room_floor, room=room["name"],
                space_id=room.get("space_id"), name=item["name"], x=round(cursor_x, 3), y=round(cursor_y, 3),
                width=width, depth=depth, height=float(item.get("height", 0.75)),
            ))
            cursor_x += width + 0.35
    return elements
