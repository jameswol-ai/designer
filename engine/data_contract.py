from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List, Mapping

SCHEMA_VERSION = "designer.project.v2"


@dataclass(frozen=True)
class Quantity:
    value: float
    unit: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Geometry2D:
    x: float
    y: float
    width: float
    depth: float
    rotation_deg: float = 0.0

    @property
    def area(self) -> float:
        return max(0.0, self.width) * max(0.0, self.depth)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def layout_record(room: Mapping[str, Any]) -> Dict[str, Any]:
    """Normalize a room record while retaining legacy top-level fields."""
    geometry = Geometry2D(
        x=float(room.get("x", 0.0)), y=float(room.get("y", 0.0)),
        width=float(room.get("width", 0.0)), depth=float(room.get("depth", 0.0)),
        rotation_deg=float(room.get("rotation_deg", 0.0)),
    )
    record = dict(room)
    record["geometry"] = geometry.to_dict()
    record["area_m2"] = round(float(room.get("area", geometry.area)), 3)
    record["floor"] = int(room.get("floor", 1))
    record["schema_version"] = SCHEMA_VERSION
    return record


def normalize_layout(layout: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    return [layout_record(room) for room in layout]


def project_document(project: Any, *, layout: Iterable[Mapping[str, Any]] | None = None) -> Dict[str, Any]:
    """Return a versioned, portable project document suitable for JSON/API use."""
    document = {
        "schema_version": SCHEMA_VERSION,
        "project": project.to_dict(),
        "metrics": {
            "site_area_m2": float(getattr(project, "site_area", 0.0)),
            "programmed_area_m2": float(getattr(project, "programmed_area", 0.0)),
            "floors": int(getattr(project, "floors", 1)),
        },
    }
    if layout is not None:
        document["layout"] = normalize_layout(layout)
    return document


def validate_document(document: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []
    if document.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"Unsupported schema_version: {document.get('schema_version')!r}")
    project = document.get("project")
    if not isinstance(project, Mapping):
        errors.append("project must be an object")
        return errors
    for field in ("name", "typology", "site_area", "floors", "spaces"):
        if field not in project:
            errors.append(f"project.{field} is required")
    if "site_area" in project and float(project["site_area"]) <= 0:
        errors.append("project.site_area must be greater than zero")
    if "floors" in project and int(project["floors"]) < 1:
        errors.append("project.floors must be at least one")
    if "spaces" in project and not isinstance(project["spaces"], list):
        errors.append("project.spaces must be an array")
    return errors
