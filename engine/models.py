from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List
from uuid import uuid4

from .data_contract import SCHEMA_VERSION


@dataclass
class Space:
    name: str
    category: str
    quantity: int = 1
    area: float = 10.0
    min_width: float = 2.4
    min_depth: float = 2.4
    priority: str = "normal"
    notes: str = ""
    id: str = field(default_factory=lambda: str(uuid4()))
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def total_area(self) -> float:
        return max(0, int(self.quantity)) * max(0.0, float(self.area))

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["schema_version"] = SCHEMA_VERSION
        data["area_m2"] = float(self.area)
        data["min_width_m"] = float(self.min_width)
        data["min_depth_m"] = float(self.min_depth)
        data["total_area_m2"] = self.total_area
        return data


@dataclass
class Project:
    name: str = "Untitled Project"
    typology: str = "Residential"
    site_area: float = 1000.0
    floors: int = 1
    location: str = ""
    climate: str = "Tropical"
    target_gfa: float = 0.0
    spaces: List[Space] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))
    schema_version: str = SCHEMA_VERSION

    @property
    def programmed_area(self) -> float:
        return sum(s.total_area for s in self.spaces)

    @property
    def floor_area_target(self) -> float:
        return max(0.0, float(self.target_gfa)) / max(1, int(self.floors)) if self.target_gfa else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "id": self.id,
            "name": self.name,
            "typology": self.typology,
            "site_area": float(self.site_area),
            "site_area_m2": float(self.site_area),
            "floors": int(self.floors),
            "location": self.location,
            "climate": self.climate,
            "target_gfa": float(self.target_gfa),
            "target_gfa_m2": float(self.target_gfa),
            "programmed_area_m2": self.programmed_area,
            "spaces": [s.to_dict() for s in self.spaces],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        spaces = []
        for raw in data.get("spaces", []):
            values = dict(raw)
            for derived in ("schema_version", "area_m2", "min_width_m", "min_depth_m", "total_area_m2"):
                values.pop(derived, None)
            spaces.append(Space(**values))
        return cls(
            name=str(data.get("name", "Untitled Project")),
            typology=str(data.get("typology", "Residential")),
            site_area=float(data.get("site_area_m2", data.get("site_area", 1000.0))),
            floors=max(1, int(data.get("floors", 1))),
            location=str(data.get("location", "")),
            climate=str(data.get("climate", "Tropical")),
            target_gfa=float(data.get("target_gfa_m2", data.get("target_gfa", 0.0))),
            spaces=spaces,
            metadata=dict(data.get("metadata", {})),
            id=str(data.get("id", uuid4())),
            schema_version=str(data.get("schema_version", SCHEMA_VERSION)),
        )
