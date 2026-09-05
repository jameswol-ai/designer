from math import ceil
from typing import Dict, List
from .models import Project

def candidate_grids(project: Project, preferred_span: float = 6.0) -> List[Dict]:
    side = max(1.0, (project.programmed_area / max(project.floors, 1)) ** 0.5)
    x_count = max(1, ceil(side / preferred_span))
    y_count = max(1, ceil(side / preferred_span))
    return [{"Option": "Regular", "X bays": x_count, "Y bays": y_count, "Approx X spacing (m)": round(side / x_count, 2), "Approx Y spacing (m)": round(side / y_count, 2)},
            {"Option": "Compact", "X bays": max(1, x_count - 1), "Y bays": max(1, y_count - 1), "Approx X spacing (m)": round(side / max(1, x_count - 1), 2), "Approx Y spacing (m)": round(side / max(1, y_count - 1), 2)}]

def structural_grid_summary(project: Project) -> Dict:
    grids = candidate_grids(project)
    return {"floor_plate_estimate_m2": round(project.programmed_area / max(project.floors, 1), 1), "preferred_span_m": 6.0, "options": len(grids)}
