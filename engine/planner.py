from typing import List
from .models import Project, Space
from metric.standards import STANDARDS

TEMPLATES = {
    "Residential": [
        ("Living Room", "living_room", 1), ("Kitchen", "kitchen", 1),
        ("Double Bedroom", "bedroom_double", 2), ("WC", "toilet", 2)
    ],
    "Office": [("Open Office", "office", 1), ("Meeting Room", "office", 1), ("WC", "toilet", 2)],
    "Education": [("Classroom", "classroom", 4), ("Staff Office", "office", 1), ("WC", "toilet", 4)],
}

def generate_program(typology: str, scale: str = "Medium") -> List[Space]:
    factor = {"Small": 0.85, "Medium": 1.0, "Large": 1.2}.get(scale, 1.0)
    result = []
    for name, category, qty in TEMPLATES.get(typology, TEMPLATES["Residential"]):
        rule = STANDARDS[category]
        result.append(Space(name=name, category=category, quantity=qty,
                            area=round(rule["min_area"] * factor, 1),
                            min_width=rule["min_width"], min_depth=rule["min_depth"]))
    return result

def build_project(name: str, typology: str, site_area: float, floors: int, scale: str) -> Project:
    return Project(name=name, typology=typology, site_area=site_area, floors=floors,
                    spaces=generate_program(typology, scale))
