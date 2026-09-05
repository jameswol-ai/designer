from typing import Dict, List
from .models import Project

DEFAULT_DAYLIGHT_RATIO = 0.10
DEFAULT_VENTILATION_RATIO = 0.05

def environmental_checks(project: Project) -> List[Dict]:
    rows = []
    for space in project.spaces:
        daylight = space.area * DEFAULT_DAYLIGHT_RATIO
        ventilation = space.area * DEFAULT_VENTILATION_RATIO
        rows.append({"Space": space.name, "Area (m²)": space.area, "Indicative daylight opening (m²)": round(daylight, 2), "Indicative ventilation opening (m²)": round(ventilation, 2), "Status": "Review against applicable code"})
    return rows

def environmental_summary(project: Project) -> Dict:
    return {"daylight_ratio": DEFAULT_DAYLIGHT_RATIO, "ventilation_ratio": DEFAULT_VENTILATION_RATIO, "spaces_assessed": len(project.spaces)}
