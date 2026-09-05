from engine import build_project, generate_building, generate_layout


def test_layout_and_building_share_room_ids():
    project = build_project("Unified", "Residential", 1000, 2, "Medium")
    layout = generate_layout(project)
    model = generate_building(project, layout=layout)
    assert model.rooms
    assert {room["id"] for room in model.rooms} == {room["id"] for room in layout}
    assert all(element.id for element in model.elements)


def test_building_contains_furniture_and_structure():
    project = build_project("Model", "Residential", 1000, 2, "Medium")
    model = generate_building(project)
    kinds = {element.kind for element in model.elements}
    assert "wall" in kinds
    assert "column" in kinds
    assert "stair" in kinds
    assert "furniture" in kinds
