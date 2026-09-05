from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List, Optional


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


def _coerce_rules(rows: Optional[Iterable[Any]]) -> List[DesignBasicRule]:
    result: List[DesignBasicRule] = []
    for row in rows or []:
        if isinstance(row, DesignBasicRule):
            result.append(row)
        elif isinstance(row, dict):
            try:
                result.append(DesignBasicRule(
                    key=str(row["key"]), category=str(row["category"]), label=str(row["label"]),
                    value=float(row["value"]), unit=str(row["unit"]),
                    description=str(row["description"]), source=str(row.get("source", "User-supplied data")),
                ))
            except (KeyError, TypeError, ValueError):
                continue
    return result


def active_rules(design_rows: Optional[Iterable[Any]] = None) -> List[DesignBasicRule]:
    """Return the baseline rules overlaid by explicitly supplied Design Basics rules."""
    overrides = {rule.key: rule for rule in _coerce_rules(design_rows)}
    known = {rule.key for rule in BASELINE_RULES}
    return [overrides.get(rule.key, rule) for rule in BASELINE_RULES] + [
        rule for key, rule in overrides.items() if key not in known
    ]


def rule_for(key: str, default: Optional[float] = None, *, design_rows: Optional[Iterable[Any]] = None) -> Optional[DesignBasicRule]:
    wanted = str(key).strip().lower()
    for rule in active_rules(design_rows):
        if rule.key.lower() == wanted:
            return rule
    if default is None:
        return None
    return DesignBasicRule(key, "Custom", key.replace("_", " ").title(), default, "m", "Fallback planning rule.")


def human_dimensions(*, design_rows: Optional[Iterable[Any]] = None) -> List[Dict[str, Any]]:
    return [rule.to_dict() for rule in active_rules(design_rows) if rule.category == "Human Dimensions"]


def space_requirements(project: Any) -> List[Dict[str, Any]]:
    rows = []
    for space in getattr(project, "spaces", []):
        quantity = max(int(getattr(space, "quantity", 1)), 1)
        rows.append({"space": space.name, "category": space.category, "area_m2": round(float(space.area), 2), "min_width_m": round(float(space.min_width), 2), "min_depth_m": round(float(space.min_depth), 2), "area_per_person_m2": round(float(space.area) / quantity, 2)})
    return rows


def movement_checks(project: Any, *, design_rows: Optional[Iterable[Any]] = None) -> List[Dict[str, Any]]:
    corridor_rule = rule_for("corridor_width", 1.20, design_rows=design_rows)
    corridor = corridor_rule.value if corridor_rule else 1.20
    return [{"space": space.name, "required_clear_width_m": corridor, "provided_min_width_m": float(space.min_width), "status": "Compliant" if float(space.min_width) >= corridor else "Review"} for space in getattr(project, "spaces", [])]


def accessibility_checks(project: Any = None, *, design_rows: Optional[Iterable[Any]] = None) -> Dict[str, Any]:
    door = rule_for("accessible_door_width", 0.90, design_rows=design_rows)
    turning = rule_for("accessible_turning_diameter", 1.50, design_rows=design_rows)
    ramp = rule_for("ramp_max_slope", 0.0833, design_rows=design_rows)
    return {"door_width_m": door.value if door else 0.90, "turning_diameter_m": turning.value if turning else 1.50, "max_ramp_slope_ratio": ramp.value if ramp else 0.0833, "note": "Conceptual baseline. Verify against the governing accessibility standard."}


def dimensional_coordination(project: Any = None, *, design_rows: Optional[Iterable[Any]] = None) -> Dict[str, Any]:
    grid = rule_for("planning_grid", 6.0, design_rows=design_rows)
    offset = rule_for("dimension_offset", 0.6, design_rows=design_rows)
    return {"planning_grid_m": grid.value if grid else 6.0, "dimension_offset_m": offset.value if offset else 0.6, "site_area_m2": float(getattr(project, "site_area", 0.0)) if project is not None else 0.0, "floors": max(1, int(getattr(project, "floors", 1))) if project is not None else 1}


def design_basics_report(project: Any, *, session_rows: Optional[Iterable[Any]] = None, design_rows: Optional[Iterable[Any]] = None) -> Dict[str, Any]:
    movement = movement_checks(project, design_rows=design_rows)
    compliant = sum(row["status"] == "Compliant" for row in movement)
    return {"human_dimensions": human_dimensions(design_rows=design_rows), "space_requirements": space_requirements(project), "movement": movement, "accessibility": accessibility_checks(project, design_rows=design_rows), "dimensional_coordination": dimensional_coordination(project, design_rows=design_rows), "movement_score": round(100.0 * compliant / len(movement), 1) if movement else 100.0, "metric_records": len(list(session_rows or []))}
