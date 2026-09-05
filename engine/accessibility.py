from typing import Dict, List
from .models import Project

DEFAULT_DOOR_WIDTH = 0.9
DEFAULT_RAMP_SLOPE = 0.0833
DEFAULT_TURNING_DIAMETER = 1.5

def accessibility_checks(project: Project, door_width: float = DEFAULT_DOOR_WIDTH, ramp_slope: float = DEFAULT_RAMP_SLOPE, turning_diameter: float = DEFAULT_TURNING_DIAMETER) -> List[Dict]:
    return [
        {"Check": "Accessible door clear width", "Value": door_width, "Required": DEFAULT_DOOR_WIDTH, "Status": "OK" if door_width >= DEFAULT_DOOR_WIDTH else "Review"},
        {"Check": "Ramp slope", "Value": ramp_slope, "Required maximum": DEFAULT_RAMP_SLOPE, "Status": "OK" if ramp_slope <= DEFAULT_RAMP_SLOPE else "Review"},
        {"Check": "Wheelchair turning diameter", "Value": turning_diameter, "Required": DEFAULT_TURNING_DIAMETER, "Status": "OK" if turning_diameter >= DEFAULT_TURNING_DIAMETER else "Review"},
    ]

def accessibility_summary(project: Project) -> Dict:
    checks = accessibility_checks(project)
    passed = sum(c["Status"] == "OK" for c in checks)
    return {"passed": passed, "total": len(checks), "score": round(100 * passed / len(checks), 1)}
