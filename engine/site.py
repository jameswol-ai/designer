from math import sqrt
from typing import Dict, List
from .models import Project

DEFAULT_PARKING_AREA = 30.0

def parking_plan(project: Project, parking_ratio: float = 1 / 50) -> Dict:
    spaces = max(0, round(project.programmed_area * parking_ratio))
    parking_area = spaces * DEFAULT_PARKING_AREA
    site_coverage = project.programmed_area / max(project.site_area, 1.0)
    return {"parking_spaces": spaces, "parking_area_m2": round(parking_area, 1), "site_coverage": round(site_coverage, 3), "remaining_site_area_m2": round(max(0, project.site_area - project.programmed_area - parking_area), 1)}

def site_checks(project: Project) -> List[Dict]:
    p = parking_plan(project)
    return [{"Check": "Indicative site coverage", "Value": p["site_coverage"], "Guideline maximum": 0.60, "Status": "OK" if p["site_coverage"] <= 0.60 else "Review"},
            {"Check": "Parking provision", "Value": p["parking_spaces"], "Required basis": "1 space / 50 m² programmed area", "Status": "Indicative"}]
