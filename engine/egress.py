from math import ceil
from typing import Dict, List
from .models import Project

DEFAULT_EXIT_CAPACITY = 100
DEFAULT_TRAVEL_LIMIT = 30.0

def egress_summary(project: Project) -> Dict:
    occupants = max(1, ceil(project.programmed_area / 15.0))
    exits = max(1, ceil(occupants / DEFAULT_EXIT_CAPACITY))
    if occupants > 50:
        exits = max(2, exits)
    return {"estimated_occupants": occupants, "indicative_exits": exits, "travel_distance_limit_m": DEFAULT_TRAVEL_LIMIT}

def egress_checks(project: Project) -> List[Dict]:
    s = egress_summary(project)
    return [{"Check": "Estimated occupant load", "Value": s["estimated_occupants"], "Status": "Indicative"},
            {"Check": "Indicative exit count", "Value": s["indicative_exits"], "Status": "Review against applicable fire code"},
            {"Check": "Travel distance", "Limit (m)": s["travel_distance_limit_m"], "Status": "Requires geometric path analysis"}]
