from typing import List, Optional

from .models import Project, Space
from metric.database import standards_as_rules

TEMPLATES = {
    "Residential": [
        ("Living Room", "living_room", 1), ("Kitchen", "kitchen", 1),
        ("Double Bedroom", "bedroom_double", 2), ("WC", "toilet", 2)
    ],
    "Office": [("Open Office", "office", 1), ("Meeting Room", "office", 1), ("WC", "toilet", 2)],
    "Education": [("Classroom", "classroom", 4), ("Staff Office", "office", 1), ("WC", "toilet", 4)],
}


def generate_program(typology: str, scale: str = "Medium", session_rows: Optional[list] = None) -> List[Space]:
    factor = {"Small": 0.85, "Medium": 1.0, "Large": 1.2}.get(scale, 1.0)
    rules = standards_as_rules(session_rows)
    result = []
    for name, category, qty in TEMPLATES.get(typology, TEMPLATES["Residential"]):
        rule = rules.get(category, {"min_area": 0.0, "min_width": 0.0, "min_depth": 0.0})
        result.append(
            Space(
                name=name,
                category=category,
                quantity=qty,
                area=round(float(rule["min_area"]) * factor, 1),
                min_width=float(rule["min_width"]),
                min_depth=float(rule["min_depth"]),
            )
        )
    return result


def build_project(
    name: str,
    typology: str,
    site_area: float,
    floors: int,
    scale: str,
    session_rows: Optional[list] = None,
) -> Project:
    return Project(
        name=name,
        typology=typology,
        site_area=site_area,
        floors=floors,
        spaces=generate_program(typology, scale, session_rows=session_rows),
    )
