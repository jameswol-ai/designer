from typing import Dict, List
from .models import Project

DEFAULT_DOOR_WIDTH = 0.9
DEFAULT_WINDOW_TO_FLOOR_RATIO = 0.10

def opening_schedule(project: Project) -> List[Dict]:
    rows = []
    for space in project.spaces:
        rows.append({"Space": space.name, "Door width (m)": DEFAULT_DOOR_WIDTH, "Indicative window area (m²)": round(space.area * DEFAULT_WINDOW_TO_FLOOR_RATIO, 2), "Qty": space.quantity})
    return rows

def opening_summary(project: Project) -> Dict:
    total_window = sum(s.area * DEFAULT_WINDOW_TO_FLOOR_RATIO * s.quantity for s in project.spaces)
    return {"door_width_m": DEFAULT_DOOR_WIDTH, "window_area_m2": round(total_window, 1), "window_ratio": DEFAULT_WINDOW_TO_FLOOR_RATIO}
