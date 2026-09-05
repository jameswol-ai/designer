from engine.data_contract import SCHEMA_VERSION, normalize_layout, project_document, validate_document
from engine.models import Project, Space


def test_project_uses_versioned_schema_and_stable_ids():
    project = Project(spaces=[Space("Living", "living_room")])
    payload = project.to_dict()
    assert payload["schema_version"] == SCHEMA_VERSION
    assert payload["id"]
    assert payload["spaces"][0]["id"]
    assert payload["programmed_area_m2"] > 0


def test_project_round_trip():
    original = Project(name="Round Trip", site_area=1200, floors=2, spaces=[Space("Room", "office", area=12)])
    restored = Project.from_dict(original.to_dict())
    assert restored.name == original.name
    assert restored.site_area == original.site_area
    assert restored.spaces[0].name == "Room"
    assert restored.spaces[0].id == original.spaces[0].id


def test_layout_records_have_structured_geometry():
    layout = normalize_layout([{"id": "r1", "name": "Room", "floor": 1, "x": 1, "y": 2, "width": 3, "depth": 4}])
    assert layout[0]["schema_version"] == SCHEMA_VERSION
    assert layout[0]["geometry"]["width"] == 3
    assert layout[0]["area_m2"] == 12


def test_document_validation():
    project = Project(spaces=[Space("Room", "office")])
    document = project_document(project)
    assert validate_document(document) == []
