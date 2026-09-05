from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from .catalog import MetricStandard, bundled_standards


def _coerce(item: Any) -> MetricStandard:
    if isinstance(item, MetricStandard):
        return item
    return MetricStandard(
        key=str(item.get("key", "")),
        category=str(item.get("category", item.get("key", ""))),
        label=str(item.get("label", item.get("key", ""))),
        min_area_m2=float(item.get("min_area_m2", item.get("min_area", 0.0))),
        min_width_m=float(item.get("min_width_m", item.get("min_width", 0.0))),
        min_depth_m=float(item.get("min_depth_m", item.get("min_depth", 0.0))),
        notes=str(item.get("notes", "")),
        source=str(item.get("source", "User-supplied licensed data")),
    )


def active_standards(session_rows: Optional[Iterable[Any]] = None) -> List[MetricStandard]:
    """Return session-supplied standards overlaid on the app-owned baseline."""
    baseline = {item.key: item for item in bundled_standards()}
    for raw in session_rows or []:
        item = _coerce(raw)
        if item.key:
            baseline[item.key] = item
    return list(baseline.values())


def standard_by_key(key: str, session_rows: Optional[Iterable[Any]] = None) -> Optional[MetricStandard]:
    wanted = str(key).strip().lower().replace(" ", "_")
    return next((item for item in active_standards(session_rows) if item.key.lower() == wanted), None)


def standards_as_rules(session_rows: Optional[Iterable[Any]] = None) -> Dict[str, Dict[str, Any]]:
    return {
        item.key: {
            "label": item.label,
            "min_area": item.min_area_m2,
            "min_width": item.min_width_m,
            "min_depth": item.min_depth_m,
            "notes": item.notes,
            "source": item.source,
        }
        for item in active_standards(session_rows)
    }
