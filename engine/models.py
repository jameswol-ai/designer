from dataclasses import dataclass, field
from typing import Dict, List, Any

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

    @property
    def total_area(self) -> float:
        return self.quantity * self.area

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

    @property
    def programmed_area(self) -> float:
        return sum(s.total_area for s in self.spaces)

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "typology": self.typology, "site_area": self.site_area,
                "floors": self.floors, "location": self.location, "climate": self.climate,
                "target_gfa": self.target_gfa,
                "spaces": [s.__dict__ for s in self.spaces], "metadata": self.metadata}
