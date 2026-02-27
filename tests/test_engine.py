from pathlib import Path

from app.interpretation_engine.engine import InterpretationEngine
from app.models import Category, LabResult, PatientProfile, Sex
from app.ocr.service import OCRService
from app.reference_database.repository import ReferenceRepository


def test_microcytic_anemia_pattern():
    repo = ReferenceRepository("data/references.json")
    engine = InterpretationEngine(repo)
    profile = PatientProfile(age=30, sex=Sex.F, category=Category.ADULT)

    results = [
        LabResult(parameter="Hb", value=9.8, unit="g/dL"),
        LabResult(parameter="VCM", value=72, unit="fL"),
    ]

    report = engine.analyze(profile, results)

    assert any("anemia microcítica" in f.title.lower() for f in report.findings)
    assert any(c.parameter == "Hemoglobina" and c.level.value.startswith("bajo") for c in report.classified)


def test_ckd_pattern_detection():
    repo = ReferenceRepository("data/references.json")
    engine = InterpretationEngine(repo)
    profile = PatientProfile(
        age=66,
        sex=Sex.M,
        category=Category.ADULT,
        has_ckd=True,
        ckd_stage=4,
    )

    results = [
        LabResult(parameter="Creat", value=4.2, unit="mg/dL"),
        LabResult(parameter="eGFR", value=12, unit="mL/min/1.73m2"),
    ]

    report = engine.analyze(profile, results)

    assert any("renal" in f.title.lower() for f in report.findings)
    assert report.alerts


def test_unmapped_parameter_is_reported():
    repo = ReferenceRepository("data/references.json")
    engine = InterpretationEngine(repo)
    profile = PatientProfile(age=50, sex=Sex.M, category=Category.ADULT)

    report = engine.analyze(
        profile,
        [LabResult(parameter="ParametroDesconocido", value=10, unit="mg/dL")],
    )

    assert "ParametroDesconocido" in report.unmapped_parameters


def test_ocr_extract_txt_entrypoint(tmp_path: Path):
    repo = ReferenceRepository("data/references.json")
    ocr = OCRService(repo)
    src = tmp_path / "ocr.txt"
    src.write_text("Hb: 11 g/dL", encoding="utf-8")

    results = ocr.extract(str(src))

    assert len(results) == 1
    assert results[0].parameter == "Hemoglobina"
