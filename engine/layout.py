from math import sqrt
from typing import Dict, List

from .models import Project


def generate_layout(project: Project, columns: int = 2) -> List[Dict]:
    """Generate deterministic conceptual room geometry distributed by floor."""
    spaces = [s for s in project.spaces for _ in range(max(1, s.quantity))]
    floors = max(1, int(project.floors))
    columns = max(1, int(columns))
    gap = 0.35
    max_width = sqrt(max(project.site_area, 100.0)) * 0.75
    out: List[Dict] = []

    for floor in range(1, floors + 1):
        floor_spaces = spaces[floor - 1 :: floors]
        x = y = row_height = 0.0
        for i, space in enumerate(floor_spaces):
            width = max(float(space.min_width), sqrt(float(space.area) * float(space.min_width) / max(float(space.min_depth), 0.1)))
            depth = max(float(space.min_depth), float(space.area) / max(width, 0.1))
            if i and i % columns == 0:
                x = 0.0
                y += row_height + gap
                row_height = 0.0
            if x + width > max_width and x > 0:
                x = 0.0
                y += row_height + gap
                row_height = 0.0
            out.append({"name": space.name, "category": space.category, "floor": floor,
                        "x": round(x, 2), "y": round(y, 2), "width": round(width, 2),
                        "depth": round(depth, 2), "area": round(float(space.area), 2)})
            x += width + gap
            row_height = max(row_height, depth)
    return out
