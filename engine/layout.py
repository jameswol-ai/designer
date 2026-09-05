from math import ceil, sqrt
from typing import List, Dict
from .models import Project

def generate_layout(project: Project, columns: int = 2) -> List[Dict]:
    spaces = [s for s in project.spaces for _ in range(s.quantity)]
    columns = max(1, columns)
    x = y = 0.0
    row_height = 0.0
    out = []
    gap = 0.35
    max_width = sqrt(max(project.site_area, 100.0)) * 0.75
    for i, s in enumerate(spaces):
        width = max(s.min_width, sqrt(s.area * s.min_width / max(s.min_depth, 0.1)))
        depth = max(s.min_depth, s.area / max(width, 0.1))
        if i and i % columns == 0:
            x = 0.0
            y += row_height + gap
            row_height = 0.0
        if x + width > max_width and x > 0:
            x = 0.0
            y += row_height + gap
            row_height = 0.0
        out.append({"name": s.name, "x": round(x, 2), "y": round(y, 2),
                    "width": round(width, 2), "depth": round(depth, 2), "area": s.area})
        x += width + gap
        row_height = max(row_height, depth)
    return out
