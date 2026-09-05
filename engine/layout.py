from __future__ import annotations

from math import ceil, sqrt
from typing import Dict, List, Tuple

from .models import Project, Space

GAP = 0.35
GRID_STEP = 0.5

REQUIRED_ADJACENCIES = {
    "Living Room": ("Kitchen",),
    "Kitchen": ("Living Room",),
    "Classroom": ("WC", "Staff Office"),
    "Open Office": ("Meeting Room", "WC"),
    "Reception": ("Waiting",),
    "Waiting": ("Reception",),
}

ZONE_KEYWORDS = {
    "public": ("living", "lobby", "reception", "waiting", "dining", "retail", "showroom", "meeting", "classroom"),
    "private": ("bedroom", "office", "study", "consult", "treatment", "staff"),
    "service": ("kitchen", "store", "storage", "utility", "laundry", "plant", "server", "wc", "toilet", "sanitary"),
    "circulation": ("corridor", "stair", "ramp", "lift", "elevator", "foyer"),
}


def _space_instances(project: Project) -> List[Tuple[Space, int]]:
    instances: List[Tuple[Space, int]] = []
    for space in project.spaces:
        for index in range(max(1, int(space.quantity))):
            instances.append((space, index + 1))
    return instances


def _zone(space: Space) -> str:
    text = f"{space.name} {space.category}".lower()
    for zone, keywords in ZONE_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return zone
    return "public"


def _required_targets(name: str, names: set[str]) -> List[str]:
    return [target for target in REQUIRED_ADJACENCIES.get(name, ()) if target in names]


def _dimensions(space: Space) -> Tuple[float, float]:
    area = max(float(space.area), 0.1)
    min_width = max(float(space.min_width), 0.1)
    min_depth = max(float(space.min_depth), 0.1)
    width = max(min_width, sqrt(area * min_width / min_depth))
    depth = max(min_depth, area / width)
    return round(width, 2), round(depth, 2)


def _overlap(a: Dict, b: Dict) -> bool:
    if a["floor"] != b["floor"]:
        return False
    return not (
        a["x"] + a["width"] <= b["x"]
        or b["x"] + b["width"] <= a["x"]
        or a["y"] + a["depth"] <= b["y"]
        or b["y"] + b["depth"] <= a["y"]
    )


def _touch_distance(candidate: Dict, target: Dict) -> float:
    cx = candidate["x"] + candidate["width"] / 2
    cy = candidate["y"] + candidate["depth"] / 2
    tx = target["x"] + target["width"] / 2
    ty = target["y"] + target["depth"] / 2
    return abs(cx - tx) + abs(cy - ty)


def _candidate_positions(room: Dict, placed: List[Dict], max_width: float) -> List[Tuple[float, float]]:
    positions = {(0.0, 0.0)}
    for other in placed:
        if other["floor"] != room["floor"]:
            continue
        positions.update({
            (other["x"] + other["width"] + GAP, other["y"]),
            (max(0.0, other["x"] - room["width"] - GAP), other["y"]),
            (other["x"], other["y"] + other["depth"] + GAP),
            (other["x"], max(0.0, other["y"] - room["depth"] - GAP)),
        })

    max_depth = max(
        [max_width, sqrt(max(room.get("area", 100.0), 100.0)) * 1.75]
        + [p["y"] + p["depth"] + room["depth"] + GAP for p in placed if p["floor"] == room["floor"]]
    )

    # Add a regular scan grid as a fallback so awkward room dimensions still find a position.
    x = 0.0
    while x <= max(0.0, max_width - room["width"]) + 0.01:
        positions.add((round(x, 2), 0.0))
        x += GRID_STEP
    y = 0.0
    while y <= max_depth + 0.01:
        positions.add((0.0, round(y, 2)))
        y += GRID_STEP

    return sorted(positions, key=lambda p: (p[1], p[0]))


def _best_position(room: Dict, placed: List[Dict], targets: List[str], max_width: float) -> Tuple[float, float]:
    candidates = _candidate_positions(room, placed, max_width)
    target_rooms = [p for p in placed if p["name"] in targets and p["floor"] == room["floor"]]

    best = None
    best_score = float("inf")
    for x, y in candidates:
        if x + room["width"] > max_width + 0.01:
            continue
        candidate = dict(room, x=x, y=y)
        if any(_overlap(candidate, other) for other in placed):
            continue

        score = y * 0.08 + x * 0.02
        if target_rooms:
            score += min(_touch_distance(candidate, target) for target in target_rooms) * 2.5
        elif placed:
            score += min(_touch_distance(candidate, other) for other in placed if other["floor"] == room["floor"]) * 0.15

        if _zone(room.get("space", room),) if False else False:
            pass
        if best is None or score < best_score:
            best = (x, y)
            best_score = score

    if best is not None:
        return best

    # Deterministic last-resort placement below the current floor envelope.
    floor_rooms = [p for p in placed if p["floor"] == room["floor"]]
    depth = max((p["y"] + p["depth"] for p in floor_rooms), default=0.0)
    return 0.0, round(depth + GAP, 2)


def _assign_floors(instances: List[Tuple[Space, int]], floors: int) -> Dict[int, List[Tuple[Space, int]]]:
    assignments = {floor: [] for floor in range(1, floors + 1)}
    names = {space.name for space, _ in instances}

    # Keep required adjacency pairs together whenever possible.
    groups: List[List[Tuple[Space, int]]] = []
    used = set()
    for index, (space, instance) in enumerate(instances):
        if index in used:
            continue
        group = [(space, instance)]
        used.add(index)
        targets = set(_required_targets(space.name, names))
        if targets:
            for j, (other, other_instance) in enumerate(instances):
                if j in used:
                    continue
                if other.name in targets:
                    group.append((other, other_instance))
                    used.add(j)
        groups.append(group)

    loads = {floor: 0.0 for floor in assignments}
    for group in groups:
        floor = min(loads, key=lambda f: (loads[f], f))
        assignments[floor].extend(group)
        loads[floor] += sum(max(0.1, float(space.area)) for space, _ in group)
    return assignments


def generate_layout(project: Project, columns: int = 2) -> List[Dict]:
    """Generate deterministic, non-overlapping conceptual room geometry.

    The legacy ``columns`` argument remains supported as a planning-density
    control. Placement now uses adjacency-aware candidate positions and floor
    load balancing rather than a simple row layout.
    """
    instances = _space_instances(project)
    if not instances:
        return []

    floors = max(1, int(project.floors))
    columns = max(1, int(columns))
    site_area = max(float(project.site_area), 100.0)
    max_width = max(6.0, sqrt(site_area) * 0.75)
    # More columns allow a wider initial envelope while preserving the argument's effect.
    max_width = max(max_width, columns * 3.0)

    assignments = _assign_floors(instances, floors)
    output: List[Dict] = []

    for floor in range(1, floors + 1):
        floor_instances = assignments.get(floor, [])
        names = {space.name for space, _ in floor_instances}
        # High-priority and adjacency-rich spaces are placed first.
        ordered = sorted(
            floor_instances,
            key=lambda item: (
                -len(_required_targets(item[0].name, names)),
                0 if str(item[0].priority).lower() in {"high", "critical"} else 1,
                -float(item[0].area),
                item[0].name,
                item[1],
            ),
        )

        floor_rooms: List[Dict] = []
        for space, instance in ordered:
            width, depth = _dimensions(space)
            room = {
                "name": space.name if instance == 1 else f"{space.name} {instance}",
                "category": space.category,
                "floor": floor,
                "x": 0.0,
                "y": 0.0,
                "width": width,
                "depth": depth,
                "area": round(float(space.area), 2),
                "zone": _zone(space),
            }
            targets = _required_targets(space.name, names)
            x, y = _best_position(room, floor_rooms, targets, max_width)
            room["x"] = round(x, 2)
            room["y"] = round(y, 2)
            floor_rooms.append(room)
            output.append(room)

    return output
