from engine import build_project, drawing_graphics, graphics_to_svg


def test_drawing_graphics_has_multiple_layers():
    project = build_project("Drawing", "Residential", 1000, 1, "Medium")
    data = drawing_graphics(project, "floor_plan", 1)
    layers = {item.get("layer") for item in data["graphics"]}
    assert "walls" in layers
    assert "room_tags" in layers
    assert "dimensions" in layers


def test_svg_is_deterministic_for_same_graphics():
    project = build_project("Drawing", "Residential", 1000, 1, "Medium")
    data = drawing_graphics(project, "floor_plan", 1)
    assert graphics_to_svg(data) == graphics_to_svg(data)
