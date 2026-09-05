from math import ceil
from typing import Dict, List
from .models import Project

DEFAULT_RISER = 0.17
DEFAULT_TREAD = 0.28
DEFAULT_STAIR_WIDTH = 1.2

def stair_schedule(project: Project, riser: float = DEFAULT_RISER, tread: float = DEFAULT_TREAD, width: float = DEFAULT_STAIR_WIDTH) -> List[Dict]:
    floor_to_floor = 3.2
    risers = max(1, ceil(floor_to_floor / riser))
    actual_riser = floor_to_floor / risers
    return [{"Element": "Main stair", "Floor-to-floor (m)": floor_to_floor, "Risers": risers, "Riser (m)": round(actual_riser, 3), "Tread (m)": tread, "Width (m)": width, "Status": "OK" if width >= 1.2 and tread >= 0.28 else "Review"}]

def vertical_summary(project: Project) -> Dict:
    return {"floors": project.floors, "stairs_required": max(1, project.floors - 1), "lift_required": project.floors > 1}
