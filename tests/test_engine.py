from engine import build_project, check_project, generate_layout, score_project

def test_program_and_score():
    p = build_project("Test", "Residential", 1000, 1, "Medium")
    assert p.programmed_area > 0
    assert 0 <= score_project(p)["Overall"] <= 100
    assert len(check_project(p)) == len(p.spaces)

def test_layout():
    p = build_project("Test", "Office", 1000, 2, "Medium")
    layout = generate_layout(p)
    assert layout
    assert all(r["width"] > 0 and r["depth"] > 0 for r in layout)
