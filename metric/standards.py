from typing import Any, Dict

from engine.models import Space

from .database import standard_by_key

STANDARDS: Dict[str, Dict[str, Any]] = {
    "bedroom_single": {"label": "Single bedroom", "min_area": 9.0, "min_width": 2.4, "min_depth": 3.0},
    "bedroom_double": {"label": "Double bedroom", "min_area": 11.0, "min_width": 2.7, "min_depth": 3.0},
    "living_room": {"label": "Living room", "min_area": 14.0, "min_width": 3.0, "min_depth": 3.5},
    "kitchen": {"label": "Kitchen", "min_area": 7.0, "min_width": 2.1, "min_depth": 3.0},
    "office": {"label": "Office", "min_area": 10.0, "min_width": 2.7, "min_depth": 3.0},
    "classroom": {"label": "Classroom", "min_area": 50.0, "min_width": 6.0, "min_depth": 7.5},
    "toilet": {"label": "WC", "min_area": 2.0, "min_width": 1.2, "min_depth": 1.5},
    "corridor": {"label": "Corridor", "min_area": 0.0, "min_width": 1.2, "min_depth": 1.2},
}


def standard_for(space: Space, session_rows=None) -> Dict[str, Any]:
    key = space.category.lower().replace(" ", "_")
    active = standard_by_key(key, session_rows)
    if active is not None:
        return {
            "label": active.label,
            "min_area": active.min_area_m2,
            "min_width": active.min_width_m,
            "min_depth": active.min_depth_m,
            "notes": active.notes,
            "source": active.source,
        }
    return STANDARDS.get(
        key,
        {"label": space.name, "min_area": 0.0, "min_width": 0.0, "min_depth": 0.0},
    )


def validate_space(space: Space, session_rows=None) -> Dict[str, Any]:
    rule = standard_for(space, session_rows=session_rows)
    area_ok = space.area >= rule["min_area"]
    width_ok = space.min_width >= rule["min_width"]
    depth_ok = space.min_depth >= rule["min_depth"]
    return {
        "name": space.name,
        "category": space.category,
        "area": space.area,
        "required_area": rule["min_area"],
        "required_width": rule["min_width"],
        "required_depth": rule["min_depth"],
        "area_ok": area_ok,
        "width_ok": width_ok,
        "depth_ok": depth_ok,
        "source": rule.get("source", "Designer baseline"),
        "status": "Compliant" if area_ok and width_ok and depth_ok else "Review",
    }
