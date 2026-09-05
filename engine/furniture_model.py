from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .furniture import furniture_for
from .layout import generate_layout


@dataclass(frozen=True)
class FurnitureElement:
    floor: int
    room: str
    name: str
    x: float
    y: float
    width: float
    depth: float
    height: float = 0.75


def furniture_elements(project, floor: Optional[int] = None) -> List[FurnitureElement]:
    elements: List[FurnitureElement] = []
    rooms = generate_layout(project)
    if floor is not None:
        rooms = [r for r in rooms if int(r.get("floor", 1)) == int(floor)]

    for room in rooms:
        room_floor = int(room.get("floor", 1))
        items = furniture_for(type("SpaceProxy", (), {
            "category": room["category"],
        })())
        if not items:
            continue

        cursor_x = room["x"] + 0.35
        cursor_y = room["y"] + 0.35
        for item in items:
            width = float(item["width"])
            depth = float(item["depth"])
            if cursor_x + width > room["x"] + room["width"] - 0.2:
                cursor_x = room["x"] + 0.35
                cursor_y += depth + 0.35
            if cursor_y + depth > room["y"] + room["depth"] - 0.2:
                continue
            elements.append(FurnitureElement(
                floor=room_floor,
                room=room["name"],
                name=item["name"],
                x=round(cursor_x, 3),
                y=round(cursor_y, 3),
                width=width,
                depth=depth,
                height=0.75,
            ))
            cursor_x += width + 0.35
    return elements
