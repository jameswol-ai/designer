from __future__ import annotations

from math import hypot
from typing import Dict, Iterable, List, Tuple

from .dimensions import grid_axes
from .models import Project, Space

ZONE_KEYWORDS = {
    "public": ("living", "lobby", "reception", "waiting", "dining", "retail", "showroom", "meeting", "classroom"),
    "private": ("bedroom", "office", "study", "consult", "treatment", "staff"),
    "service": ("kitchen", "store", "storage", "utility", "laundry", "plant", "server", "wc", "toilet", "sanitary"),
    "circulation": ("corridor", "lobby", "stair", "ramp", "lift", "elevator", "foyer"),
}

REQUIRED_ADJACENCIES = {
    "Living Room": ("Kitchen",),
    "Kitchen": ("Living Room",),
    "Classroom": ("WC", "Staff Office"),
    "Open Office": ("Meeting Room", "WC"),
    "Reception": ("Waiting",),
    "Waiting": ("Reception",),
}

SEPARATION_PAIRS = {
    frozenset(("bedroom", "service")),
    frozenset(("living", "service")),
}


def classify_zone(space: Space | Dict) -> str:
    name = str(space.name if hasattr(space, "name") else space.get("name", "")).lower()
    category = str(space.category if hasattr(space, "category") else space.get("category", "")).lower()
    text = f"{name} {category}"
    for zone, keywords in ZONE_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return zone
    return "public"


def required_adjacencies(project: Project) -> List[Tuple[str, str]]:
    names = {s.name for s in project.spaces}
    pairs: List[Tuple[str, str]] = []
    for source, targets in REQUIRED_ADJACENCIES.items():
        if source not in names:
            continue
        for target in targets:
            if target in names:
                pairs.append((source, target))
    return pairs


def _rect_distance(a: Dict, b: Dict) -> float:
    ax = a["x"] + a["width"] / 2.0
    ay = a["y"] + a["depth"] / 2.0
    bx = b["x"] + b["width"] / 2.0
    by = b["y"] + b["depth"] / 2.0
    return hypot(ax - bx, ay - by)


def adjacency_proximity_score(project: Project, layout: List[Dict]) -> float:
    by_name = {item["name"]: item for item in layout}
    pairs = required_adjacencies(project)
    if not pairs:
        return 100.0
    scores: List[float] = []
    for source, target in pairs:
        a = by_name.get(source)
        b = by_name.get(target)
        if not a or not b:
            scores.append(0.0)
            continue
        if a["floor"] != b["floor"]:
            scores.append(20.0)
            continue
        distance = _rect_distance(a, b)
        scores.append(max(0.0, min(100.0, 100.0 - distance * 10.0)))
    return sum(scores) / len(scores)


def overlap_penalty(layout: List[Dict]) -> int:
    penalty = 0
    for i, a in enumerate(layout):
        for b in layout[i + 1 :]:
            if a["floor"] != b["floor"]:
                continue
            if not (
                a["x"] + a["width"] <= b["x"]
                or b["x"] + b["width"] <= a["x"]
                or a["y"] + a["depth"] <= b["y"]
                or b["y"] + b["depth"] <= a["y"]
            ):
                penalty += 1
    return penalty


def zoning_score(layout: List[Dict]) -> float:
    if not layout:
        return 100.0
    score = 100.0
    for i, a in enumerate(layout):
        za = classify_zone(a)
        for b in layout[i + 1 :]:
            if a["floor"] != b["floor"]:
                continue
            zb = classify_zone(b)
            if frozenset((za, zb)) in SEPARATION_PAIRS:
                distance = _rect_distance(a, b)
                if distance < 4.0:
                    score -= (4.0 - distance) * 4.0
    return max(0.0, min(100.0, score))


def grid_alignment_score(project: Project, layout: List[Dict], spacing: float | None = None) -> float:
    if not layout:
        return 100.0
    axes = grid_axes(project, spacing)
    x_axes = axes["x"]
    y_axes = axes["y"]
    if not x_axes or not y_axes:
        return 100.0

    def nearest(value: float, values: Iterable[float]) -> float:
        return min(abs(value - candidate) for candidate in values)

    errors: List[float] = []
    for room in layout:
        errors.extend((nearest(room["x"], x_axes), nearest(room["y"], y_axes)))
    average_error = sum(errors) / len(errors) if errors else 0.0
    return max(0.0, min(100.0, 100.0 - average_error * 25.0))


def constraint_report(project: Project, layout: List[Dict]) -> Dict:
    overlaps = overlap_penalty(layout)
    return {
        "overlaps": overlaps,
        "adjacency_proximity": round(adjacency_proximity_score(project, layout), 1),
        "zoning": round(zoning_score(layout), 1),
        "grid_alignment": round(grid_alignment_score(project, layout), 1),
        "zones": {
            "public": sum(classify_zone(r) == "public" for r in layout),
            "private": sum(classify_zone(r) == "private" for r in layout),
            "service": sum(classify_zone(r) == "service" for r in layout),
            "circulation": sum(classify_zone(r) == "circulation" for r in layout),
        },
    }
