from typing import Dict, List
from .models import Project, Space

FURNITURE: Dict[str, List[Dict]] = {
    "living_room": [{"name": "Sofa", "width": 2.1, "depth": 0.9}, {"name": "Coffee table", "width": 1.2, "depth": 0.6}],
    "bedroom_double": [{"name": "Double bed", "width": 1.6, "depth": 2.0}, {"name": "Wardrobe", "width": 1.8, "depth": 0.6}],
    "kitchen": [{"name": "Kitchen counter", "width": 2.4, "depth": 0.6}],
    "office": [{"name": "Workstation", "width": 1.5, "depth": 0.75}, {"name": "Meeting table", "width": 1.8, "depth": 0.9}],
    "classroom": [{"name": "Student desk", "width": 0.6, "depth": 0.45}],
    "toilet": [{"name": "WC fixture", "width": 0.7, "depth": 0.7}],
}

def furniture_for(space: Space) -> List[Dict]:
    return FURNITURE.get(space.category, [])

def furniture_schedule(project: Project) -> List[Dict]:
    rows = []
    for space in project.spaces:
        for item in furniture_for(space):
            rows.append({"Space": space.name, "Item": item["name"], "Width (m)": item["width"], "Depth (m)": item["depth"], "Qty": space.quantity})
    return rows

def furniture_check(space: Space) -> Dict:
    items = furniture_for(space)
    footprint = sum(i["width"] * i["depth"] for i in items)
    usable_ratio = footprint / max(space.area, 0.1)
    return {"space": space.name, "furniture_items": len(items), "estimated_footprint_m2": round(footprint, 2), "footprint_ratio": round(usable_ratio, 3), "status": "Review" if usable_ratio > 0.65 else "OK"}
