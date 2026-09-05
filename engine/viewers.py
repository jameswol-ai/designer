from typing import Dict, List
from .models import Project
from .layout import generate_layout

VIEW_MODES = ["Dashboard", "3D Model", "Floor Plan", "Site Plan", "Elevations", "Sections", "Analysis"]

def view_registry() -> List[Dict[str, str]]:
    return [{"name": name, "description": description} for name, description in [
        ("Dashboard", "Project metrics, compliance and design summary"),
        ("3D Model", "Conceptual massing and floor-stack viewer"),
        ("Floor Plan", "Interactive room and space layout viewer"),
        ("Site Plan", "Building footprint, parking and site context"),
        ("Elevations", "Conceptual building elevations"),
        ("Sections", "Conceptual vertical section through the building"),
        ("Analysis", "Metric, accessibility, environmental and egress results"),
    ]]

def model_summary(project: Project) -> Dict:
    layout = generate_layout(project)
    width = max((r["x"] + r["width"] for r in layout), default=0.0)
    depth = max((r["y"] + r["depth"] for r in layout), default=0.0)
    return {"floor_width_m": round(width, 2), "floor_depth_m": round(depth, 2), "floors": project.floors, "floor_area_m2": round(project.programmed_area / max(project.floors, 1), 1)}
