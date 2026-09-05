from typing import Dict, List
from .models import Project

DEFAULT_CORRIDOR_WIDTH = 1.2
ACCESSIBLE_TURNING_DIAMETER = 1.5

def circulation_summary(project: Project, corridor_width: float = DEFAULT_CORRIDOR_WIDTH) -> Dict:
    programmed = project.programmed_area
    estimated_circulation = programmed * 0.15
    return {"corridor_width_m": corridor_width, "estimated_circulation_area_m2": round(estimated_circulation, 1), "circulation_ratio": 0.15, "width_status": "OK" if corridor_width >= DEFAULT_CORRIDOR_WIDTH else "Review"}

def circulation_checks(project: Project, corridor_width: float = DEFAULT_CORRIDOR_WIDTH) -> List[Dict]:
    summary = circulation_summary(project, corridor_width)
    return [{"Check": "Minimum corridor width", "Value": corridor_width, "Required": DEFAULT_CORRIDOR_WIDTH, "Status": summary["width_status"]},
            {"Check": "Estimated circulation allowance", "Value": summary["estimated_circulation_area_m2"], "Required": round(project.programmed_area * 0.10, 1), "Status": "OK"}]
