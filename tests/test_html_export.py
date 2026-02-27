from app.export.report_html import render_html
from app.interpretation_engine.engine import InterpretationEngine
from app.models import Category, LabResult, PatientProfile, Sex
from app.reference_database.repository import ReferenceRepository


def test_render_html_contains_table_and_sections():
    repo = ReferenceRepository("data/references.json")
    engine = InterpretationEngine(repo)
    profile = PatientProfile(age=30, sex=Sex.F, category=Category.ADULT)
    report = engine.analyze(profile, [LabResult(parameter="Hb", value=9.8, unit="g/dL")])

    html = render_html(report)

    assert "<table>" in html
    assert "Informe académico de laboratorio" in html
    assert "Parámetros no reconocidos" in html
