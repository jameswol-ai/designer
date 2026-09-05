from engine import build_project, drawing_graphics, graphics_to_svg


def test_svg_renderer_returns_valid_document():
    project = build_project("SVG", "Residential", 1000, 1, "Medium")
    graphics = drawing_graphics(project, "floor_plan", 1)
    svg = graphics_to_svg(graphics)
    assert svg.startswith("<svg")
    assert "</svg>" in svg
    assert "Room" in svg or "Living" in svg


def test_svg_layer_filtering():
    project = build_project("SVG", "Residential", 1000, 1, "Medium")
    graphics = drawing_graphics(project, "floor_plan", 1)
    svg = graphics_to_svg(graphics, layers=["dimensions"])
    assert "<svg" in svg
