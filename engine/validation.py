from typing import Dict, List
from .models import Project
from metric.standards import validate_space

def check_project(project: Project) -> List[Dict]:
    return [validate_space(s) for s in project.spaces]

def score_project(project: Project) -> Dict[str, float]:
    checks = check_project(project)
    compliant = sum(r["status"] == "Compliant" for r in checks)
    metric_score = 100.0 * compliant / len(checks) if checks else 0.0
    site_efficiency = min(100.0, project.programmed_area / max(project.site_area, 1.0) * 100.0)
    return {"Metric compliance": round(metric_score, 1),
            "Program/site efficiency": round(site_efficiency, 1),
            "Overall": round((metric_score * 0.7) + (site_efficiency * 0.3), 1)}
