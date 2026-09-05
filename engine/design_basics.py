from __future__ import annotations

from dataclasses import dataclass, asdict
from math import ceil
from typing import Any, Dict, Iterable, List


@dataclass(frozen=True)
class DesignBasicRule:
    key: str
    category: str
    label: str
    value: float
    unit: str
    description: str
    source: str = "Designer baseline"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


BASELINE_RULES: List[DesignBasicRule] = [
    DesignBasicRule("human_footprint_width", "Human Dimensions", "Typical standing person width", 0.60, "m", "Indicative planning allowance for a standing adult."),
    DesignBasicRule("human_footprint_depth", "Human Dimensions", "Typical standing person depth", 0.45, "m", "Indicative planning allowance for a standing adult."),
    DesignBasicRule("movement_clearance", "Movement", "Basic clear movement width", 0.90, "m", "Indicative single-person clear movement allowance."),
    DesignBasicRule("corridor_width", "Movement", "Primary corridor width", 1.20, "m", "Indicative conceptual corridor width."),
    DesignBasicRule("accessible_door_width", "Accessibility", "Accessible clear door width", 0.90, "m", "Indicative baseline; verify against applicable regulations."),
    DesignBasicRule("accessible_turning_diameter", "Accessibility", "Wheelchair turning diameter", 1.50, "m", "Indicative planning allowance; verify against applicable regulations."),
    DesignBasicRule("ramp_max_slope", "Accessibility", "Conceptual maximum ramp slope", 0.0833, "ratio", "Indicative 1:12 planning basis; verify local requirements."),
    DesignBasicRule("planning_grid", "Dimensional Coordination", "Preferred planning grid", 6.00, "m", "Conceptual structural/planning coordination module."),
    DesignBasicRule("dimension_offset", "Dimensional Coordination", "Dimension line offset", 0.60, "m", "Graphic dimensioning allowance."),
]


def _session_rules() -> List[DesignBasicRule]:
    try:
        rows = __import__("streamlit").session_state.get("design_basic_rules", [])
    except Exception:
        rows = []
    result: List[DesignBasicRule] = []
    for row in rows:
        if isinstance(row, DesignBasicRule):
            result.append(row)
        elif isinstance(row, dict):
            try:
                result.append(DesignBasicRule(**row))
            except TypeError:
                continue
    return result


def active_rules() -> List[DesignBasicRule]:
    overrides = {rule.key: rule for rule in _session_rules()}
    return [overrides.get(rule.key, rule) for rule in BASELINE_RULES] + [
        rule for key, rule in overrides.items() if key not in {item.key for item in BASELINE_RULES}
    ]


def rule_for(key: str, default: float | None = None) -> DesignBasicRule | None:
    for rule in active_rules():
        if rule.key == key:
            return rule
    if default is None:
        return None
    return DesignBasicRule(key, "Custom", key.replace("_", " ").title(), default, "m", "Fallback rule.")


def human_dimensions() -> List[Dict[str, Any]]:
    return [rule.to_dict() for rule in active_rules() if rule.category == "Human Dimensions"]


def space_requirements(project: Any) -> List[Dict[str, Any]]:
    rows = []
    for space in getattr(project, "spaces", []):
        rows.append({
            "space": space.name,
            "category": space.category,
            "area_m2": round(float(space.area), 2),
            "min_width_m": round(float(space.min_width), 2),
            "min_depth_m": round(float(space.min_depth), 2),
            "area_per_person_m2": round(float(space.area) / max(int(space.quantity), 1), 2),
        })
    return rows


def movement_checks(project: Any) -> List[Dict[str, Any]]:
    corridor = rule_for("corridor_width", 1.20).value
    rows = []
    for space in getattr(project, "spaces", []):
        width = float(space.min_width)
        rows.append({"space": space.name, "required_clear_width_m": corridor, "provided_min_width_m": width, "status": "Compliant" if width >= corridor else "Review"})
    return rows


def accessibility_checks(project: Any) -> Dict[str, Any]:
    door = rule_for("accessible_door_width", 0.90).value
    turning = rule_for("accessible_turning_diameter", 1.50).value
    ramp = rule_for("ramp_max_slope", 0.0833).value
    return {"door_width_m": door, "turning_diameter_m": turning, "max_ramp_slope_ratio": ramp, "note": "Conceptual baseline. Verify against the governing accessibility standard."}


def dimensional_coordination(project: Any) -> Dict[str, Any]:
    grid = rule_for("planning_grid", 6.0).value
    return {"planning_grid_m": grid, "dimension_offset_m": rule_for("dimension_offset", 0.6).value, "site_area_m2": float(getattr(project, "site_area", 0.0)), "floors": max(1, int(getattr(project, "floors", 1)))}


def design_basics_report(project: Any) -> Dict[str, Any]:
    movement = movement_checks(project)
    compliant = sum(row["status"] == "Compliant" for row in movement)
    return {"human_dimensions": human_dimensions(), "space_requirements": space_requirements(project), "movement": movement, "accessibility": accessibility_checks(project), "dimensional_coordination": dimensional_coordination(project), "movement_score": round(100.0 * compliant / len(movement), 1) if movement else 100.0}
