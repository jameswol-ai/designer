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
