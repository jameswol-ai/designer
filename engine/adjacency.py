from typing import Dict, List, Tuple
from .models import Project

DEFAULT_ADJACENCIES = {
    "Living Room": ["Kitchen", "Double Bedroom"],
    "Kitchen": ["Living Room"],
    "Classroom": ["Staff Office", "WC"],
    "Open Office": ["Meeting Room", "WC"],
}


def adjacency_matrix(project: Project) -> Tuple[List[str], List[List[int]]]:
    names = [s.name for s in project.spaces]
    matrix = [[0 for _ in names] for _ in names]
    for i, name in enumerate(names):
        for j, other in enumerate(names):
            if other in DEFAULT_ADJACENCIES.get(name, []):
                matrix[i][j] = 1
    return names, matrix


def adjacency_score(project: Project) -> float:
    names, matrix = adjacency_matrix(project)
    required = 0
    satisfied = 0
    positions = {}
    for index, space in enumerate(project.spaces):
        positions.setdefault(space.name, index)
    for i, name in enumerate(names):
        for target in DEFAULT_ADJACENCIES.get(name, []):
            required += 1
            j = positions.get(target)
            if j is not None and matrix[i][j] == 1:
                satisfied += 1
    if required == 0:
        return 100.0
    return satisfied / required * 100.0


def adjacency_summary(project: Project) -> Dict:
    names, matrix = adjacency_matrix(project)
    return {
        "spaces": len(names),
        "required_relationships": sum(sum(row) for row in matrix),
        "score": round(adjacency_score(project), 1),
    }
