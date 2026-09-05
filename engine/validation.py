from __future__ import annotations

from typing import Any, Dict, List, Optional

from .models import Project
from metric.standards import validate_space


def check_project(project: Project, session_rows: Optional[list] = None) -> List[Dict[str, Any]]:
    """Validate every programmed space against the active Metric rule set."""
    return [validate_space(space, session_rows=session_rows) for space in project.spaces]


def score_project(project: Project, session_rows: Optional[list] = None) -> Dict[str, float]:
    """Return project-level planning scores.

    ``session_rows`` is optional so older callers remain compatible while the
    current application can supply licensed/user-provided Metric data.
    """
    checks = check_project(project, session_rows=session_rows)
    compliant = sum(row.get("status") == "Compliant" for row in checks)
    metric_score = 100.0 * compliant / len(checks) if checks else 0.0
    site_efficiency = min(
        100.0,
        float(project.programmed_area) / max(float(project.site_area), 1.0) * 100.0,
    )
    return {
        "Metric compliance": round(metric_score, 1),
        "Program/site efficiency": round(site_efficiency, 1),
        "Overall": round((metric_score * 0.7) + (site_efficiency * 0.3), 1),
    }
