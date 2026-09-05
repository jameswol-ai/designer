from engine import build_project, generate_layout
from engine.drawing_graphics import drawing_graphics
from engine.drawing_renderer import render_graphics
from engine.drawing_sheet import drawing_register, make_sheet


def test_floor_plan_graphics_contains_core_layers():
    project = build_project("Drawing Test", "Residential", 1000, 2, "Medium")
    layout = generate_layout(project)
    data = drawing_graphics(project, "floor_plan", 1, layout=layout)
    assert data["schema_version"] == "designer.graphics.v1"
    assert data["graphics"]
    layers = {item["layer"] for item in data["graphics"] if "layer" in item}
    assert "walls" in layers
    assert "room_tags" in layers
    assert "dimensions" in layers


def test_renderer_builds_interactive_figure():
    project = build_project("Renderer Test", "Residential", 1000, 1, "Medium")
    graphics = drawing_graphics(project, "floor_plan")
    figure = render_graphics(graphics)
    assert len(figure.data) > 0
    assert figure.layout.xaxis.scaleanchor == "y"


def test_drawing_sheet_and_register_are_versioned():
    project = build_project("Sheet Test", "Residential", 1000, 2, "Medium")
    sheet = make_sheet(project)
    assert sheet["schema_version"] == "designer.drawing_sheet.v1"
    assert sheet["drawing_number"] == "A101"
    register = drawing_register(project)
    assert register[0]["drawing_number"] == "A001"
    assert any(row["drawing_number"] == "A201" for row in register)
