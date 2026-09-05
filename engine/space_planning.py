from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .adjacency import adjacency_score
from .furniture import furniture_check
from .layout import generate_layout
from .validation import check_project


@dataclass(frozen=True)
class PlanningAlternative:
    name: str
    columns: int
    score: float
    compactness: float
    circulation: float
    furniture: float
    adjacency: float
    compliance: float
    overlap_count: int
    layout: List[Dict]

    def as_dict(self) -> Dict:
        return {
            "alternative": self.name,
            "columns": self.columns,
            "score": round(self.score, 1),
            "compactness": round(self.compactness, 1),
            "circulation": round(self.circulation, 1),
            "furniture": round(self.furniture, 1),
            "adjacency": round(self.adjacency, 1),
            "compliance": round(self.compliance, 1),
            "overlaps": self.overlap_count,
        }


def _overlaps(a: Dict, b: Dict) -> bool:
    if a["floor"] != b["floor"]:
        return False
    return not (
        a["x"] + a["width"] <= b["x"] or
        b["x"] + b["width"] <= a["x"] or
        a["y"] + a["depth"] <= b["y"] or
        b["y"] + b["depth"] <= a["y"]
    )


def overlap_count(layout: List[Dict]) -> int:
    return sum(
        _overlaps(layout[i], layout[j])
        for i in range(len(layout))
        for j in range(i + 1, len(layout))
    )


def _compactness(layout: List[Dict]) -> float:
    if not layout:
        return 0.0
    used = sum(float(r["area"]) for r in layout)
    width = max((r["x"] + r["width"] for r in layout), default=1.0)
    depth = max((r["y"] + r["depth"] for r in layout), default=1.0)
    envelope = max(width * depth, 1.0)
    return max(0.0, min(100.0, used / envelope * 100.0))


def _furniture_score(project) -> float:
    checks = [
        furniture_check(space)
        for space in project.spaces
        for _ in range(max(1, space.quantity))
    ]
    if not checks:
        return 100.0
    return sum(
        100.0 if c.get("status") == "Adequate" else 50.0
        for c in checks
    ) / len(checks)


def _compliance_score(project) -> float:
    checks = check_project(project)
    if not checks:
        return 100.0
    passed = 0
    total = 0
    for item in checks:
        if not isinstance(item, dict):
            continue
        total += 1
        status = str(item.get("status", "")).lower()
        if status in {"compliant", "pass", "passed", "ok", "adequate"}:
            passed += 1
    return 100.0 if total == 0 else passed / total * 100.0


def _adjacency_score(project) -> float:
    try:
        value = float(adjacency_score(project))
        return max(0.0, min(100.0, value))
    except (TypeError, ValueError, AttributeError):
        return 100.0


def generate_alternatives(project, max_columns: int = 4) -> List[PlanningAlternative]:
    furniture = _furniture_score(project)
    compliance = _compliance_score(project)
    adjacency = _adjacency_score(project)
    alternatives: List[PlanningAlternative] = []

    for columns in range(1, max(1, int(max_columns)) + 1):
        layout = generate_layout(project, columns=columns)
        overlaps = overlap_count(layout)
        compactness = _compactness(layout)
        circulation = max(0.0, 100.0 - min(100.0, overlaps * 12.0))
        score = (
            compactness * 0.25 +
            circulation * 0.20 +
            furniture * 0.15 +
            adjacency * 0.20 +
            compliance * 0.20
        )
        alternatives.append(PlanningAlternative(
            name=f"Option {chr(64 + columns)}",
            columns=columns,
            score=score,
            compactness=compactness,
            circulation=circulation,
            furniture=furniture,
            adjacency=adjacency,
            compliance=compliance,
            overlap_count=overlaps,
            layout=layout,
        ))

    return sorted(alternatives, key=lambda item: item.score, reverse=True)


def best_alternative(project, max_columns: int = 4) -> Optional[PlanningAlternative]:
    alternatives = generate_alternatives(project, max_columns)
    return alternatives[0] if alternatives else None


def planning_summary(project, max_columns: int = 4) -> Dict:
    alternatives = generate_alternatives(project, max_columns)
    best = alternatives[0] if alternatives else None
    return {
        "alternatives": len(alternatives),
        "recommended": best.name if best else None,
        "score": round(best.score, 1) if best else 0.0,
        "columns": best.columns if best else 0,
    }
