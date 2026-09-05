from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable, List


@dataclass(frozen=True)
class MetricStandard:
    key: str
    category: str
    label: str
    min_area_m2: float = 0.0
    min_width_m: float = 0.0
    min_depth_m: float = 0.0
    notes: str = ""
    source: str = "Illustrative baseline"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Only metadata and app-owned baseline rules are bundled here.
# Licensed handbook-derived values should be imported into the project's
# external standards data layer rather than redistributed with the app.
BOOK_METADATA: Dict[str, Any] = {
    "title": "Metric Handbook: Planning and Design Data",
    "edition": "User-supplied / licensed edition",
    "publisher": "Routledge",
    "role": "Reference source for architectural planning and design data",
    "bundled_content": False,
}


def bundled_standards() -> List[MetricStandard]:
    from .standards import STANDARDS

    result: List[MetricStandard] = []
    for key, rule in STANDARDS.items():
        result.append(
            MetricStandard(
                key=key,
                category=key,
                label=str(rule.get("label", key)),
                min_area_m2=float(rule.get("min_area", 0.0)),
                min_width_m=float(rule.get("min_width", 0.0)),
                min_depth_m=float(rule.get("min_depth", 0.0)),
                notes="Bundled illustrative baseline rule.",
                source="Designer baseline",
            )
        )
    return result


def catalog_rows(standards: Iterable[MetricStandard] | None = None) -> List[Dict[str, Any]]:
    source = bundled_standards() if standards is None else list(standards)
    return [item.to_dict() for item in source]
